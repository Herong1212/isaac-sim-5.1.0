__all__ = ["load_index", "is_locking_enabled", "serialize_index", "save_index"]

from zipfile import ZipFile, ZIP_LZMA, ZIP_DEFLATED
import time
import os
import tempfile
import asyncio
import threading
import shutil
from typing import Dict
from functools import lru_cache
from enum import Enum
import concurrent.futures

import carb
import carb.dictionary
import omni.client

from ..utils.common import _error, _info, info_exec_time, _get_setting
from ..utils.omni_client_utils import (
    omni_client_copy,
    omni_client_copy_async,
    omni_client_stat,
    omni_client_stat_async,
    omni_client_reduce_retries,
)
from ..registry_globals import RegistryGlobals


READ_VERSION = 1
WRITE_VERSION = 1
META_KEY = "#meta"

DEFAULT_META = {"read_version": READ_VERSION, "write_version": WRITE_VERSION, "locking_enabled": False}

SUPPORTED_INDEX_FILES = ["index.zip", "index.json", "index.toml"]
NEW_INDEX_FILE = "index.json"


@info_exec_time()
def _zip_file(path, zipped_path):
    with ZipFile(zipped_path, "w", compression=ZIP_LZMA) as zipf:
        zipf.write(path, arcname=os.path.basename(path))


def _unzip(path, target):
    with ZipFile(path, "r") as zipObj:
        zipObj.extractall(path=target)


def _load_meta(index_dict):
    d = carb.dictionary.get_dictionary()
    meta_d = d.get_item(index_dict, META_KEY)
    if meta_d:
        meta_d = meta_d.get_dict()
        return meta_d
    return DEFAULT_META


def _write_meta(index_dict, prev_meta: Dict):
    d = carb.dictionary.get_dictionary()

    # use prev meta with all the data
    meta = prev_meta

    # update versions since we writing index
    meta["read_version"] = READ_VERSION
    meta["write_version"] = WRITE_VERSION

    d.set(index_dict, META_KEY, meta)


def load_index(index_path):
    path, ext = os.path.splitext(index_path)
    index_dict = None
    if ext == ".zip":
        _unzip(index_path, os.path.dirname(index_path))
        _info(f"unzipped index: {index_path}")
        unzipped_path = path + ".json"
        return load_index(unzipped_path)
    elif ext == ".json":
        index_dict = carb.dictionary.get_json_serializer().create_dictionary_from_file(index_path)
    elif ext == ".toml":
        index_dict = carb.dictionary.get_toml_serializer().create_dictionary_from_file(index_path)
    else:
        _error(f"Unsupported index format: {index_path}")

    if index_dict:
        meta = _load_meta(index_dict)
        _info("index meta: {}".format(meta))
        read_version = meta.get("read_version", 0)
        if read_version > READ_VERSION:
            _error(f"Index read version: {read_version} is newer than client: {READ_VERSION}. Can't load this index.")
            return None

    return index_dict


@info_exec_time()
def _prune_index(index_dict):
    # prune
    d = carb.dictionary.get_dictionary()
    keys = index_dict.get_keys()
    for k in keys:
        for p in [
            "native",
            "python",
            "state",
            "test",
            "settings",
            "configPath",
            "path",
            "package/changelog",
            "package/readme",
            "package/description",
            "package/detailedDescription",
        ]:
            item = d.get_item(index_dict, f"{k}/{p}")
            if item != None:
                d.destroy_item(item)


def is_locking_enabled(index_dict) -> bool:
    meta = _load_meta(index_dict)
    return meta.get("locking_enabled", False)


@info_exec_time()
def serialize_index(index_dict, index_local):
    carb.dictionary.get_json_serializer().save_file_from_dictionary(index_dict, index_local, 0)


@info_exec_time()
def save_index(index_dict, tmp_dir, ext):
    meta = _load_meta(index_dict)
    write_version = meta.get("write_version", 0)
    if write_version > WRITE_VERSION:
        _error(f"Index read version: {write_version} is newer than client: {WRITE_VERSION}. Can't save this index.")
        return None

    _write_meta(index_dict, meta)

    _prune_index(index_dict)

    index_local = f"{tmp_dir}/index.json"
    serialize_index(index_dict, index_local)

    if not os.path.exists(index_local):
        _error("index serialization failed")
        return None

    if ext == ".json":
        return index_local
    elif ext == ".zip":
        index_zip = os.path.splitext(index_local)[0] + ".zip"
        _zip_file(index_local, index_zip)
        return index_zip
    else:
        _error(f"unsupported index format: {ext}")
        return


@lru_cache()
def get_default_index_format():
    default_format = _get_setting("/exts/omni.kit.registry.nucleus/defaultIndexFormat", SUPPORTED_INDEX_FILES[0])
    if default_format not in SUPPORTED_INDEX_FILES:
        _error(f"Default format: {default_format} is not supported. Choose out of: {SUPPORTED_INDEX_FILES}.")
        default_format = SUPPORTED_INDEX_FILES[0]
    return default_format


def try_restore_index(index_remote, index_backup):
    """We failed somewhere during publish process where index was already changed. We have a backup file, try to restore"""
    ATTEMPTS = 5
    deleted = False
    for i in range(ATTEMPTS):
        _info(f"attempting to restore index: deleting '{index_remote}'. Attempt: #{i}...")

        result = omni.client.delete(index_remote)
        if result == omni.client.Result.OK:
            _info("successfully deleted index")
            deleted = True
        else:
            _info("failed deleted index. Retrying...")
            continue

    # If no backup that means it is the first time we create index, just deleting is enough
    if index_backup is None:
        if deleted:
            _info("successfully restored index (there was no backup).")
        else:
            _error(f"Delete index manually: '{index_remote}'")
        return

    for i in range(ATTEMPTS):
        _info(f"attempting to restore index from '{index_backup}' -> '{index_remote}'. Attempt: #{i}...")

        result = omni_client_copy(index_backup, index_remote, "restoring from backup")
        if result == omni.client.Result.OK:
            _info("successfully restored index")
            return
        else:
            _info("failed to restore index. Retrying...")
            continue

    _error(f"Index was corrupted, restore it from backup manually. Backup: {index_backup}. Index: '{index_remote}'")


class IndexDownloadState(Enum):
    INPROGRESS = 0
    SUCCESS = 1
    FAILURE = 2


class IndexDownloadTask:
    def __init__(self, index_url, registry_globals: RegistryGlobals, optional, is_async: bool = True):
        self._globals = registry_globals
        try:
            self._tmp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        except:
            # Support python versions < 3.10
            self._tmp_dir = tempfile.TemporaryDirectory()
        self.state = IndexDownloadState.INPROGRESS
        self.index_is_new = False

        self.index_local = None  # that will be full path local tmp copy of index (can be different ext if new)
        self.index_remote = None  # that will be full url to index path if any
        self.index_dict = None

        self._optional = optional

        self.cache_was_used = False

        self._index_url = index_url
        self._start_time = time.monotonic()

        if is_async:
            self._task = asyncio.ensure_future(self._run_async())
        else:
            self._run()

    def cleanup(self):
        self._tmp_dir.cleanup()
        try:
            self._task.cancel()
        except:
            pass

    def _handle_result(self, result):
        if result == omni.client.Result.ERROR_NOT_FOUND:
            _info("index file was not found, index is empty, creating empty index.")
            self.index_remote = f"{self._index_url}/{get_default_index_format()}"
            self.index_local = f"{self._tmp_dir.name}/{NEW_INDEX_FILE}"
            with open(self.index_local, "a") as f:
                f.write("{}")
            self.index_is_new = True
            return IndexDownloadState.SUCCESS
        elif result != omni.client.Result.OK:
            report_fn = _info if self._optional else _error
            report_fn(f"syncing index failed. URL: '{self._index_url}'. Result: {result}")
            return IndexDownloadState.FAILURE
        else:
            # Additional level of protection when file size is 0 (there was a bug in connection lib)
            if os.stat(self.index_local).st_size == 0:
                _error(f"syncing index failed. File size is 0: {self.index_local}")
                return IndexDownloadState.FAILURE
            else:
                _info("index download took: {}".format(time.monotonic() - self._start_time))
                return IndexDownloadState.SUCCESS

    def _load_index_dict(self, download_result):
        state = self._handle_result(download_result)
        if state == IndexDownloadState.SUCCESS:
            if os.path.exists(self.index_local):
                start_time = time.monotonic()
                self.index_dict = load_index(self.index_local)
                _info("dictionary load took: {}".format(time.monotonic() - start_time))
                exts_cache = self._globals.get_exts_cache()
                if exts_cache and not self.cache_was_used and not self.index_is_new:
                    exts_cache.cache_file(self.index_local, self.index_remote)
        self.state = state

    async def _load_index_dict_async(self, download_result):
        load_done = concurrent.futures.Future()

        def load():
            try:
                self._load_index_dict(download_result)
            finally:
                try:
                    load_done.set_result(True)
                except concurrent.futures.InvalidStateError:
                    # This can happen if task was cancelled (on shutdown)
                    pass

        t = threading.Thread(target=load)
        t.start()
        await asyncio.wrap_future(load_done)

    def _yield_supported_index_files(self):
        for index_file in SUPPORTED_INDEX_FILES:
            self.index_remote = f"{self._index_url}/{index_file}"
            self.index_local = f"{self._tmp_dir.name}/{index_file}"
            yield index_file

    def _try_load_from_cache(self):
        # Failure: try cached index (offline mode)
        for _ in self._yield_supported_index_files():
            index_local_path = self._globals.get_exts_cache().get_file_cache_path(self.index_remote)
            if index_local_path:
                change_time = time.ctime(os.path.getmtime(index_local_path))
                carb.log_info(
                    f"OFFLINE MODE: syncing index failed. Using cached index from: {change_time} (path: {index_local_path})"
                )
                shutil.copy(index_local_path, self.index_local)
                self.cache_was_used = True
                return True
        return False

    async def _run_async(self):
        with omni_client_reduce_retries():
            result = omni.client.Result.ERROR_NOT_FOUND
            for _ in self._yield_supported_index_files():
                result, _ = await omni_client_stat_async(self.index_remote)
                if result == omni.client.Result.OK:
                    result = await omni_client_copy_async(self.index_remote, self.index_local, "syncing index (async)")
                    await self._load_index_dict_async(result)
                    return
            if self._try_load_from_cache():
                await self._load_index_dict_async(omni.client.Result.OK)
                return
            self._load_index_dict(result)

    def _run(self):
        with omni_client_reduce_retries():
            result = omni.client.Result.ERROR_NOT_FOUND
            for _ in self._yield_supported_index_files():
                result, _ = omni_client_stat(self.index_remote)
                if result == omni.client.Result.OK:
                    result = omni_client_copy(self.index_remote, self.index_local, "syncing index (sync)")
                    self._load_index_dict(result)
                    return
            if self._try_load_from_cache():
                self._load_index_dict(omni.client.Result.OK)
                return
            self._load_index_dict(result)
