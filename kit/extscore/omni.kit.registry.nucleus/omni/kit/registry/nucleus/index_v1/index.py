# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import datetime
import time
import json
import os
import tempfile

from typing import Tuple, List

import carb.dictionary
import carb.settings
import carb.tokens
import omni.kit.app
import omni.ext
import omni.client

from omni.client import CopyBehavior

from ..utils.common import _info, _print, _error, _warn, _get_setting, info_exec_time
from ..utils.omni_client_utils import (
    omni_client_lock_with_retry,
    omni_client_copy,
    omni_client_lock_with_retry,
    omni_client_stat,
)
from .index_operations import (
    save_index,
    is_locking_enabled,
    IndexDownloadTask,
    IndexDownloadState,
    try_restore_index,
)
from ..registry_globals import RegistryGlobals
from ..iregistry_index import IRegistryIndex, RegistryURLs
from ..index_shared.resources import upload_resources


# Retry with exp backoff: 1, 2, 4, 8, 16 seconds
INDEX_UPDATE_TRIES = 6
INDEX_UPDATE_DELAY = 1.0
INDEX_UPDATE_BACKOFF = 2


class RegistryIndexV1(IRegistryIndex):
    def __init__(self, name: str, url: str, optional: bool, registry_globals: RegistryGlobals):
        # Globals
        self._globals = registry_globals

        # Provider name
        self._name = name

        # Index dictionary item
        self._index_dict = None
        self._index_is_new = False

        # Flag to force index sync
        self._index_sync_required = True

        # Task for async index download
        self._download_task = None

        # Url to use
        self._index_url_root = url

        self._optional = optional

        # Use version for subfolders
        registryVersion = _get_setting("/app/extensions/registryVersion", "NOT_SET")
        self._index_url = self._index_url_root + f"/{registryVersion}"
        self._info(f"creating RegistryIndexV1(), index url: {self._index_url}")

        # Build common URLs
        self._urls = RegistryURLs(
            index=self._index_url,
            archives=f"{self._index_url}/archives",
            resources=f"{self._index_url}/resources",
            archives_alternatives=[f"{url}/2/archives", f"{url}/v2/archives"],
        )
        # Path to store index backups:
        self._index_url_bak = f"{self._urls.index}/bak"

        # New items to be added to the index (for batching few updates)
        self._update_index_queue = []  # List of tuples: (ext_id, ext_dict)

    def get_index_dict(self) -> carb.dictionary.Item:
        return self._index_dict

    def get_urls(self) -> RegistryURLs:
        return self._urls

    def _info(self, message):
        _info(f"[{self._name}] [v1] {message}")

    def _error(self, message):
        _error(f"[{self._name}] [v1] {message}")

    def _destroy_index_dict(self):
        if self._index_dict is not None:
            self._globals.defer_destroy_index(self._index_dict)
            self._index_dict = None

    def _cleanup_download_task(self):
        if self._download_task is not None:
            self._download_task.cleanup()
            self._download_task = None

    def shutdown(self):
        self._destroy_index_dict()
        self._cleanup_download_task()

    def refresh_index(self):
        if self._download_task is None:
            self._info("refresh_index() -> started.")
            self._download_task = IndexDownloadTask(self._urls.index, self._globals, optional=self._optional, is_async=True)
            return omni.ext.DownloadState.DOWNLOADING

        if self._download_task.state == IndexDownloadState.INPROGRESS:
            return omni.ext.DownloadState.DOWNLOADING

        if self._download_task.state == IndexDownloadState.SUCCESS:
            self._info("refresh_index() -> success.")
            self._index_sync_required = True
            return omni.ext.DownloadState.DOWNLOAD_SUCCESS
        else:
            self._info("refresh_index() -> failure.")
            self._cleanup_download_task()
            return omni.ext.DownloadState.DOWNLOAD_FAILURE

    def sync_index(self, resync):
        self._ensure_synced(resync=resync)
        self._globals.destroy_queued_indices()
        return self._index_dict, self._index_is_new

    def apply_index_changes_batch(self):
        self._info(" apply_index_changes_batch called.")
        res = bool(self._update_index())
        if not res:
            _error("Failed batch updating an index.")
        return res

    def _ensure_synced(self, resync=False):
        self._info(f"_ensure_synced(resync={resync}) called")

        if self._index_sync_required or resync:
            self._info("self._index_sync_required")
            self._destroy_index_dict()

        if self._index_dict is None:
            self._info("Downloading and reading index...")
            # Download and read index.toml

            if self._download_task is not None and self._download_task.state == IndexDownloadState.SUCCESS:
                # use previously downloaded async
                self._info("use previously downloaded index")
            else:
                # Kill previous task in case it is running and start new sync(blocking) task
                if self._download_task is not None:
                    self._cleanup_download_task()
                self._download_task = IndexDownloadTask(self._urls.index, self._globals, optional=self._optional, is_async=False)

            if self._download_task.state != IndexDownloadState.SUCCESS:
                return

            # Task now has index file downloaded, take it and load:
            index_local = self._download_task.index_local
            self._urls.index_file = self._download_task.index_remote
            self._index_dict = self._download_task.index_dict
            self._index_is_new = self._download_task.index_is_new
            if self._index_dict:
                _info(f"index was loaded from file: '{index_local}'. index_is_new: {self._index_is_new}")

            self._cleanup_download_task()
            self._index_sync_required = False

    def upload_resources(self, ext_id, ext_dict, **kwargs) -> bool:
        return upload_resources(ext_id, ext_dict, self.get_urls(), **kwargs)

    def add_to_index(self, ext_id, ext_dict):
        self._queue_update_index(ext_id, ext_dict)
        if not self._globals.is_index_changes_batching():
            if not self._update_index():
                return False
        return True

    def remove_from_index(self, ext_id):
        # 1. Update index: remove package with ext_id key
        d = carb.dictionary.get_dictionary()
        item = d.get_item(self._index_dict, ext_id)
        if item is None:
            self._error(f"Can't find package with id: '{ext_id}' on remote to unpublish.")
            return False
        d.destroy_item(item)

        # 2. Update index: upload on remote
        index_remote = self._urls.index_file
        with tempfile.TemporaryDirectory() as tmp_dir:
            res, index_backup = self._upload_index(self._index_dict, tmp_dir, index_remote)
            if not res:
                return False
        return True

    def _queue_update_index(self, ext_id: str, ext_dict: dict):
        self._update_index_queue.append((ext_id, ext_dict))

    @info_exec_time()
    def _update_index(self):
        changes_cnt = len(self._update_index_queue)
        if changes_cnt == 0:
            return True

        _print(f"Applying {changes_cnt} changes to the index...")

        attempt = 1
        delay = INDEX_UPDATE_DELAY

        while True:
            # retry with exp backoff
            if attempt > 1:
                if attempt > INDEX_UPDATE_TRIES:
                    _error(f"Index update failed after {INDEX_UPDATE_TRIES} tries. See warnings above.")
                    return False
                _warn(f"Index update failed, retrying: Attempt: {attempt}/{INDEX_UPDATE_TRIES}. Delay: {delay}s...")
                time.sleep(delay)
                delay *= INDEX_UPDATE_BACKOFF
            attempt += 1

            # Redownload index, it could have changed while zipping archives
            self._ensure_synced(resync=True)

            for ext_id, ext_dict in self._update_index_queue:
                # Update index: write a config file into it
                d = carb.dictionary.get_dictionary()
                temp_item = carb.dictionary.get_json_serializer().create_dictionary_from_string_buffer(json.dumps(ext_dict))
                d.update(self._index_dict, ext_id, temp_item, "", carb.dictionary.UpdateAction.OVERWRITE)
                d.destroy_item(temp_item)

            #  Update index: upload on remote
            index_remote = self._urls.index_file
            with tempfile.TemporaryDirectory() as tmp_dir:
                res, index_backup = self._upload_index(self._index_dict, tmp_dir, index_remote)
                if not res:
                    continue

            #  Verify
            self._ensure_synced(resync=True)
            verified = True
            for ext_id, _ in self._update_index_queue:
                if self._index_dict.get(ext_id, None) is None:
                    _warn(
                        f"Publishing verification failed. Can't find key: '{ext_id}' in the index. Write contention is a likely reason."
                    )
                    verified = False
                    break
            if not verified:
                continue

            # flush the queue
            self._update_index_queue = []

            return True

    @info_exec_time()
    def _upload_index(self, index_dict, tmp_dir: str, index_remote: str) -> Tuple[bool, str]:
        locking_enabled = is_locking_enabled(index_dict)

        _, ext = os.path.splitext(index_remote)
        index_file = os.path.basename(index_remote)
        index_local = save_index(index_dict, tmp_dir, ext)
        if not index_local or not os.path.exists(index_local):
            self._error(f"Failed to save index to '{index_local}'")
            self._index_sync_required = True
            return False, None

        index_local = index_local.replace("\\", "/")

        with omni_client_lock_with_retry(index_remote, locking_enabled) as result:
            if result not in {
                omni.client.Result.OK,
                omni.client.Result.ERROR_NOT_SUPPORTED,
                omni.client.Result.ERROR_NOT_FOUND,
            }:
                self._error(f"Failed to take a lock on {index_remote}. Result: '{result}'")
                return False, None

            # Delete on remote first as we don't have overwrite in omni.client API. Check if it already exists:
            # If index.toml exists backup and delete it.

            # wrap, and fix that non async call
            result, _ = omni_client_stat(index_remote)
            if result != omni.client.Result.OK and result != omni.client.Result.ERROR_NOT_FOUND:
                self._error(f"Failed check if {index_file} exists. Result: '{result}'")
                return False, None

            index_backup = None

            if result == omni.client.Result.OK:
                # Check once more if we are about to delete index while thinking that we are creating new index. That could
                # happen if when syncing index it was missing for some reason (contention?).
                if self._index_is_new:
                    self._error(
                        f"Created new index, but: '{index_remote}' already exist. Index desync happened, aborting."
                    )
                    self._index_sync_required = True
                    return False, None

                timestamp = (
                    datetime.datetime.utcnow().isoformat(timespec="milliseconds").replace(":", "-")
                )  # ':' is not path-friendly on windows
                index_backup = f"{self._index_url_bak}/{index_file}.{timestamp}"
                result = omni_client_copy(index_remote, index_backup, f"backing up {index_file}")
                if result != omni.client.Result.OK and result != omni.client.Result.ERROR_NOT_FOUND:
                    self._error(f"Failed to backup {index_file}: '{index_remote}'. Result: '{result}'")
                    self._index_sync_required = True
                    return False, None

            # Upload new index now
            result = omni_client_copy(index_local, index_remote, "uploading new index", behavior=CopyBehavior.OVERWRITE)
            if result != omni.client.Result.OK:
                self._error(
                    f"Failed to upload updated index from '{index_local}' to '{index_remote}'. Result: {result}."
                )
                # This is the worst place to fail currently, as index was removed and that will corrupt repository. Attempt to restore from backup.
                try_restore_index(index_remote, index_backup)
                self._index_sync_required = True
                return False, None

            # At this point it was uploaded, not new for sure. We might use the same index to upload more right away.
            self._index_is_new = False

            return True, index_backup

    def get_package_dict(self, package_id: str) -> dict:
        return self._index_dict.get(package_id, None)
