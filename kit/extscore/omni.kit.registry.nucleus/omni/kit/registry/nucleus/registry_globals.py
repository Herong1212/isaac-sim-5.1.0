# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import carb.dictionary
import omni.ext
import omni.kit.app

import logging
from threading import Lock

from .auth_manager import OmniAuthManager
from .cache import GlobalExtCache

logger = logging.getLogger(__name__)


class PublishResult:
    OK = "OK"
    OK_EXISTS = "OK_EXISTS"
    FAIL = "FAIL"
    SKIP = "SKIP"


class RegistryGlobals:
    """Shared state for all registry instances."""

    def __init__(self):
        # Local download cache
        self._exts_cache = GlobalExtCache()

        # Auth managers (host -> auth manager instance)
        self._auth_managers = {}

        # Toggle special mode where index is not updated, but changes batched instead (for performance)
        self._index_changes_batching = False

        # Queued indices to destroy
        self._index_destroy_queue = []

        # Empty index for cases when index is not available
        self.empty_index = carb.dictionary.get_dictionary().create_item(None, "", carb.dictionary.ItemType.DICTIONARY)

        # Publish results for API
        self.publish_results = {}
        self._publish_result_lock = Lock()

    def get_exts_cache(self) -> GlobalExtCache:
        return self._exts_cache

    def set_index_changes_batching(self, value: bool):
        """Stop updating index, all index changes will be accumulated until `apply_index_changes_batch` call."""
        self._index_changes_batching = value

    def is_index_changes_batching(self) -> bool:
        """Check if index changes batching mode is active."""
        return self._index_changes_batching

    def set_publish_results(self, ext_id: str, result: PublishResult):
        """Set publish result for extension."""
        with self._publish_result_lock:
            # Do not override a more specific OK_EXISTS result with OK
            if result == PublishResult.OK and self.publish_results.get(ext_id) == PublishResult.OK_EXISTS:
                return
            self.publish_results[ext_id] = result

    def get_publish_results(self) -> dict:
        """Get publish results."""
        return self.publish_results

    def get_auth_manager(self, url: str):
        # Auth is only supported for "omniverse" currently
        broken_url = omni.client.break_url(url)
        # TODO: do we support other kind of url for auth now?
        #if broken_url.scheme != "omniverse":
        #    return None
        # 1 auth manager per host
        host = broken_url.host
        if host not in self._auth_managers:
            self._auth_managers[host] = OmniAuthManager(host, url)
        return self._auth_managers[host]

    def defer_destroy_index(self, index_dict):
        """Defer index destroy until next sync_index call. Until that extension manager can still hold on to it's data."""
        self._index_destroy_queue.append(index_dict)

    def destroy_queued_indices(self):
        for index_dict in self._index_destroy_queue:
            carb.dictionary.get_dictionary().destroy_item(index_dict)
        self._index_destroy_queue = []

    def destroy(self):
        carb.dictionary.get_dictionary().destroy_item(self.empty_index)
        self.empty_index = None

        for m in self._auth_managers.values():
            m.shutdown()
        self._auth_managers = {}

        if self._exts_cache:
            self._exts_cache.destroy()
            self._exts_cache = None

        self.destroy_queued_indices()
