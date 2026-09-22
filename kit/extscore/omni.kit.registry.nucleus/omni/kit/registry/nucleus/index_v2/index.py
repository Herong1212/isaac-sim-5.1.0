# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import time
import os
from threading import Lock

import carb.dictionary
import carb.settings
import carb.tokens
import omni.kit.app
import omni.ext
import omni.client

from ..utils.common import _info, _print, _error, _warn, info_exec_time, sha1_str, _get_setting, rmpath
from ..registry_globals import RegistryGlobals
from ..iregistry_index import IRegistryIndex, RegistryURLs
from ..index_v2.index_sync import IndexSync, IndexSyncState
from ..index_v2.summaries_file import SUMMARIES_FILENAME_REMOTE
from ..index_shared.resources import upload_resources


# Retry with exp backoff: 1, 2, 4, 8, 16 seconds
INDEX_UPDATE_TRIES = 6
INDEX_UPDATE_DELAY = 1.0
INDEX_UPDATE_BACKOFF = 2


class RegistryIndexV2(IRegistryIndex):
    def __init__(self, name: str, url: str, optional: bool, registry_globals: RegistryGlobals, reset_local_cache=False):
        # Globals
        self._globals = registry_globals

        # Provider name
        self._name = name

        # Flag to force index sync
        self._index_sync_required = True

        # Index sync object (both fetch and push operations)
        self._index_sync = None

        # Url to use
        self._index_url_root = omni.client.normalize_url(url)

        # Registry is optional if inability to connect to it doesn't produce an error, it is just skipped
        self._optional = optional

        # Use version for subfolders
        self._index_url = omni.client.combine_urls(self._index_url_root + "/", f"v2")

        # local cache
        index_cache_path = self._globals.get_exts_cache().get_index_cache_path()
        index_subpath = sha1_str(self._index_url)[:8]
        self._index_cache_path = f"{index_cache_path}/{index_subpath}"
        if _get_setting("/exts/omni.kit.registry.nucleus/resetLocalIndexCache", False) or reset_local_cache:
            carb.log_info(f"Resetting local index cache at: {self._index_cache_path}")
            rmpath(self._index_cache_path)
        os.makedirs(self._index_cache_path, exist_ok=True)
        self._info(
            f"creating RegistryIndexV2(), index url: {self._index_url}, index local cache: {self._index_cache_path}"
        )

        # Build common URLs
        self._urls = RegistryURLs(
            index=self._index_url,
            archives=f"{self._index_url}/archives",
            resources=f"{self._index_url}/resources",
            archives_alternatives=[f"{url}/3/archives", f"{url}/2/archives"],
            index_file=f"{self._index_url}/{SUMMARIES_FILENAME_REMOTE}",
        )
        # New items to be added to the index (for batching few updates)
        self._update_index_queue = []  # List of tuples: (ext_id, ext_dict, add: bool)
        self._update_index_queue_lock = Lock()

    def get_index_dict(self) -> carb.dictionary.Item:
        return self._index_sync.get_summaries_dict()

    def get_urls(self) -> RegistryURLs:
        return self._urls

    def _info(self, message):
        _info(f"[{self._name}] [v2] {message}")

    def _error(self, message):
        _error(f"[{self._name}] [v2] {message}")

    def _cleanup_index_sync(self):
        if self._index_sync is not None:
            self._index_sync.cleanup()
            self._index_sync = None

    def shutdown(self):
        self._cleanup_index_sync()

    def refresh_index(self):
        if self._index_sync is None:
            self._info("refresh_index() -> started.")
            self._index_sync = self._create_index_sync()
            return omni.ext.DownloadState.DOWNLOADING

        if self._index_sync.state == IndexSyncState.INPROGRESS:
            return omni.ext.DownloadState.DOWNLOADING

        if self._index_sync.state == IndexSyncState.SUCCESS:
            self._info("refresh_index() -> success.")
            self._index_sync_required = True
            return omni.ext.DownloadState.DOWNLOAD_SUCCESS
        else:
            self._info("refresh_index() -> failure.")
            self._cleanup_index_sync()
            return omni.ext.DownloadState.DOWNLOAD_FAILURE

    def sync_index(self, resync):
        self._ensure_synced(resync=resync)
        self._globals.destroy_queued_indices()
        return self._index_sync.get_summaries_dict(), self._index_sync.index_is_new

    def apply_index_changes_batch(self):
        self._info(" apply_index_changes_batch called.")
        try:
            res = bool(self._update_index())
            if not res:
                _error("Failed batch updating an index.")
            return res
        except Exception as e:
            _error(f"Failed batch updating an index: {e}")
            return False

    def _create_index_sync(self):
        return IndexSync(self._index_cache_path, self._urls.index, self._globals, self._optional)

    def _ensure_synced(self, resync=False) -> bool:
        self._info(f"_ensure_synced(resync={resync}) called")

        if self._index_sync_required or resync:
            self._info("Syncing index...")

            if self._index_sync is not None and self._index_sync.state == IndexSyncState.SUCCESS and not resync:
                # use previously downloaded async
                self._info("use previously downloaded index")
            else:
                # Kill previous task in case it is running and start new sync(blocking) task
                if self._index_sync is not None:
                    self._cleanup_index_sync()
                self._index_sync = self._create_index_sync()
                self._index_sync.wait()

            if self._index_sync.state != IndexSyncState.SUCCESS:
                return False

            if self._index_sync.get_summaries_dict():
                _info(f"index synced. index_is_new: {self._index_sync.index_is_new}")

            self._index_sync_required = False

        return True

    def upload_resources(self, ext_id, ext_dict, **kwargs) -> bool:
        return upload_resources(ext_id, ext_dict, self.get_urls(), **kwargs)

    def add_to_index(self, ext_id, ext_dict):
        return self._queue_update_index(ext_id, ext_dict, add=True)

    def remove_from_index(self, ext_id):
        return self._queue_update_index(ext_id, None, add=False)

    def _queue_update_index(self, ext_id: str, ext_dict: dict, add: bool):
        with self._update_index_queue_lock:
            self._update_index_queue.append((ext_id, ext_dict, add))
        if not self._globals.is_index_changes_batching():
            if not self._update_index():
                return False
        return True

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
            if not self._ensure_synced(resync=True):
                continue

            # Take lock to make sure other process doesn't modify local index while we are pushing changes
            with self._index_sync.lock():
                # Apply package changes
                self._info(f"Applying {changes_cnt} changes to the index...")
                for ext_id, ext_dict, add in self._update_index_queue:
                    self._index_sync.apply_change(ext_id, ext_dict, add=add)

                # push changes
                if not self._index_sync.push_changes():
                    continue

            #  Verify
            if not self._ensure_synced(resync=True):
                continue

            verified = True
            for ext_id, _, add in self._update_index_queue:
                package_dict = self.get_package_dict(ext_id)
                if add and package_dict is None:
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

    def get_package_dict(self, package_id: str) -> dict:
        return self._index_sync.get_package_dict(package_id)
