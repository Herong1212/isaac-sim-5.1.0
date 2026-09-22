# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
import datetime
import traceback
import threading
import json
import time
import gzip
import dataclasses
from typing import Tuple
from enum import Enum
from dataclasses import dataclass
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

import carb
import carb.dictionary

import omni.client


from .package_file import PackageFile
from .summaries_file import SummariesFile, SUMMARIES_FILE_KEYS
from .registry_file import RegistryFile, REGISTRY_FILENAME_REMOTE
from ..utils.common import sha1_file, info_exec_time, get_ext_name_tag_version, new_dict_with_filter
from ..utils.omni_client_utils import (
    omni_client_lock_with_retry,
    omni_client_reduce_retries,
    omni_client_write_file,
    omni_client_lock_with_retry,
    omni_client_stat,
    omni_client_read_file,
)
from ..utils.threadsafe_open import ThreadsafeOpen


class IndexSyncError(Exception):
    pass

class IndexConnectionError(Exception):
    pass

def read_remote_zip_to_json(url: str) -> Tuple[dict, omni.client.Result]:
    """Reads a remote zip file and returns the json content and if file did not exist"""
    result, content = omni_client_read_file(url)
    if result == omni.client.Result.OK:
        return json.loads(gzip.decompress(memoryview(content))), result

    return None, result


def replace_ext_with_gz(path):
    return os.path.splitext(path)[0] + ".gz"


class IndexSyncState(Enum):
    INPROGRESS = 0
    SUCCESS = 1
    FAILURE = 2


@dataclass
class IndexChange:
    ext_id: str
    ext_data: dict
    add: bool


class IndexSync:
    def __init__(self, local_path, remote_path, globals, optional=False):
        self._globals = globals

        self._local_path = local_path
        self._remote_path = remote_path
        self._package_files = {}

        self.registry_file_remote = f"{self._remote_path}/{REGISTRY_FILENAME_REMOTE}"

        self._changed_files = set()
        self._changes: list[IndexChange] = []

        self._summaries_file = None

        self._optional = optional

        self.index_is_new = False

        self._fetch()

    def cleanup(self):
        self.wait()
        if self._summaries_file is not None:
            self._summaries_file.destroy(self._globals)
            self._summaries_file = None

    @contextmanager
    def lock(self):
        lock_file = f"{self._local_path}/registry.lock"
        carb.log_info(f"trying to take index_sync lock on: {lock_file}")
        with ThreadsafeOpen(lock_file, "w") as f:
            yield f

    def _fetch(self):
        self.state = IndexSyncState.INPROGRESS

        def _task():
            try:
                with self.lock(), omni_client_reduce_retries():
                    self._task_uncaught()
            except Exception as e:
                exc_type = type(e)
                if exc_type is IndexConnectionError and self._optional:
                    carb.log_info(f"Optional index sync failed for url: '{self._remote_path}'. Exception: {str(e)}")
                else:
                    if exc_type is IndexConnectionError or exc_type is IndexSyncError:
                        msg = str(e)
                    else:
                        msg = traceback.format_exc()
                    carb.log_error(f"Syncing registry index failed for url: '{self._remote_path}'. Exception: {msg}")
                self.state = IndexSyncState.FAILURE
                return
            self.state = IndexSyncState.SUCCESS

        self._thread = threading.Thread(target=_task)
        self._thread.start()

    def _task_uncaught(self):
        # read local index
        self._registry_file = RegistryFile(self._local_path)

        # read remote index registry.zip
        skip_file_download = False
        registry_data_remote, read_result = read_remote_zip_to_json(self.registry_file_remote)
        self.index_is_new = (read_result == omni.client.Result.ERROR_NOT_FOUND)
        is_connection_error = (read_result == omni.client.Result.ERROR_CONNECTION)
        if registry_data_remote == None:
            registry_data_remote = {}

            if not self.index_is_new:
                if is_connection_error:
                    raise IndexConnectionError(f"Failed to connect to the registry: '{self._remote_path}'")
                else:
                    raise IndexSyncError(f"Failed to read main registry file: '{self.registry_file_remote}'")

            # we have local copy of the index, while remote says it's empty. No need to stomp on it. It may indeed
            # be empty or it might be some issue, let's keep a local copy.
            if self._registry_file.files:
                skip_file_download = True

        if not skip_file_download:
            # compare files and run tasks
            files_to_download = []
            for filepath, filehash in registry_data_remote.get("files", {}).items():
                if filepath not in self._registry_file.files or self._registry_file.files[filepath] != filehash:
                    files_to_download.append(filepath)

            if files_to_download:
                print(f"syncing registry: '{self._remote_path}' Downloading {len(files_to_download)} files...")
                with ThreadPoolExecutor() as executor:
                    executor.map(self._download_file, files_to_download)

            # update local registry.json to remember downloaded files
            self._registry_file.set_data(registry_data_remote)
            self._registry_file.save()

        # load summaries
        self._summaries_file = SummariesFile(self._local_path)

    def _download_file(self, filepath: str):
        remote_path = replace_ext_with_gz(f"{self._remote_path}/{filepath}")
        local_path = f"{self._local_path}/{filepath}"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        carb.log_info(f"Downloading file: {remote_path} to {local_path}")

        result, content = omni_client_read_file(remote_path)
        if result != omni.client.Result.OK:
            carb.log_error(f"Failed to download file: {remote_path}. Result: {result}")
            return

        with open(local_path, "wb") as f:
            f.write(gzip.decompress(memoryview(content)))

    def wait(self):
        self._thread.join()

    def get_package_dict(self, package_id) -> dict:
        return self.get_or_create_package_file(package_id).get_package_dict(package_id)

    def get_summaries_dict(self) -> carb.dictionary.Item:
        return self._summaries_file.carb_dict if self._summaries_file else None

    def get_or_create_package_file(self, package_id: str) -> PackageFile:
        package_name, _, _ = get_ext_name_tag_version(package_id)
        path = f"{self._local_path}/packages/{package_name}.json"
        package_file = self._package_files.get(path)
        if not package_file:
            package_file = PackageFile(path)
            self._package_files[path] = package_file
        return package_file

    def apply_change(self, ext_id, ext_dict: dict, add: bool):
        # Data preparation
        if ext_dict:
            ext_dict = new_dict_with_filter(ext_dict, SUMMARIES_FILE_KEYS)

        # Package file
        package_file: PackageFile = self.get_or_create_package_file(ext_id)
        if package_file.apply_change(ext_id, ext_dict, add):
            self._changed_files.add(package_file)

        # Summaries
        if self._summaries_file.apply_change(ext_id, ext_dict, add, package_file):
            self._changed_files.add(self._summaries_file)

        # keep history of changes
        self._changes.append(IndexChange(ext_id, ext_dict, add))

    def _finalize_changes(self):
        if not self._changed_files:
            return

        carb.log_info(f"Rehashing {len(self._changed_files)} files...")

        # Save all the changes and rehash files
        for file in self._changed_files:
            file.save()
            relpath = os.path.relpath(file.path, self._local_path).replace("\\", "/")
            hash = sha1_file(file.path)
            self._registry_file.files[relpath] = hash

        self._registry_file.save()
        self._changed_files.add(self._registry_file)

    @info_exec_time()
    def push_changes(self) -> bool:
        # finalize changes
        self._finalize_changes()

        # relpaths
        changed_paths = [
            os.path.relpath(file.path, self._local_path).replace("\\", "/") for file in self._changed_files
        ]

        # TODO: add locking?
        locking_enabled = False

        with omni_client_lock_with_retry(self.registry_file_remote, locking_enabled) as result:
            if result not in {
                omni.client.Result.OK,
                omni.client.Result.ERROR_NOT_SUPPORTED,
                omni.client.Result.ERROR_NOT_FOUND,
            }:
                carb.log_error(f"Failed to take a lock on {self.registry_file_remote}. Result: '{result}'")
                return False

            # wrap, and fix that non async call
            result, _ = omni_client_stat(self.registry_file_remote)
            if result != omni.client.Result.OK and result != omni.client.Result.ERROR_NOT_FOUND:
                carb.log_error(f"Failed check if {self.registry_file_remote} exists. Result: '{result}'")
                return False

            if result == omni.client.Result.OK:
                # Check once more if we are about to delete index while thinking that we are creating new index. That could
                # happen if when syncing index it was missing for some reason (contention?).
                if self.index_is_new:
                    carb.log_error(
                        f"Created new index, but: '{self.registry_file_remote}' already exist. Index desync happened, aborting."
                    )
                    return False

            # upload files
            for file in changed_paths:
                carb.log_info(f"Uploading file: {file}...")
                local_path = f"{self._local_path}/{file}"
                remote_path = replace_ext_with_gz(f"{self._remote_path}/{file}")

                with open(local_path, "rb") as f:
                    content = gzip.compress(f.read())
                    result = omni_client_write_file(remote_path, content)
                    if result != omni.client.Result.OK:
                        carb.log_error(
                            f"Failed to upload file from '{local_path}' to '{remote_path}'. Result: {result}."
                        )
                        return False

            # write changes log
            if True:
                self._write_changes_log()

            # At this point it was uploaded, not new for sure. We might use the same index to upload more right away.
            self.index_is_new = False

            self._changed_files = set()

            return True

    def _write_changes_log(self):
        # folder per month not to have too many files in one folder
        year_month = time.strftime("%Y-%m")
        # each change batch is a separate file to avoid conflicts
        timestamp = datetime.datetime.utcnow().isoformat(timespec="milliseconds").replace(":", "-")
        log_url = f"{self._remote_path}/logs/{year_month}/changes_{timestamp}.gz"
        data = json.dumps([dataclasses.asdict(change) for change in self._changes], indent=4)
        result = omni_client_write_file(log_url, gzip.compress(data.encode("utf-8")))
        if result != omni.client.Result.OK:
            carb.log_error(f"Failed to write changes log file: '{log_url}'. Result: '{result}'")
