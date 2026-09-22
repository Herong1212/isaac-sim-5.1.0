# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a class for fetching, caching, and retrieving JSON data related to extension archives from online sources."""

__all__ = ["ExtDataFetcher"]

import asyncio
import json
import logging
from functools import lru_cache
from typing import Callable, List

import omni.kit.app

from .common import ExtensionCommonInfo

logger = logging.getLogger(__name__)


class ExtDataFetcher:  # pragma: no cover
    """Fetches json files near extension archives from the registry and caches them"""

    def __init__(self):
        """Initializes the ExtDataFetcher with default properties."""
        # Notify when anything new fetched
        self.on_data_fetched_fn: Callable = None

        # Cached data
        self._data = {}

    def get_ext_data(self, package_id) -> dict:
        """Retrieves the cached data for a given package ID.

        Args:
            package_id (str): The unique identifier of the package."""
        return self._data.get(package_id, None)

    def fetch(self, ext_item: ExtensionCommonInfo):
        """Fetches and caches the data for the given extension item.

        Args:
            ext_item (:obj:`ExtensionCommonInfo`): The extension item to fetch data for."""
        if self.get_ext_data(ext_item.package_id):
            return
        json_data_urls = self._build_json_data_urls(ext_item)
        if json_data_urls:

            async def read_data():
                for json_data_url in json_data_urls:
                    result, _, content = await omni.client.read_file_async(json_data_url)
                    if result == omni.client.Result.OK:
                        try:
                            content = memoryview(content).tobytes().decode("utf-8")
                            self._data[ext_item.package_id] = json.loads(content)
                            if self.on_data_fetched_fn:
                                self.on_data_fetched_fn(ext_item.package_id)  # noqa
                            break
                        except Exception as e:  # noqa
                            logger.error("Error reading extra registry data from: %s. Error: %s", json_data_url, e)

            asyncio.ensure_future(read_data())

    def _build_json_data_urls(self, ext_item: ExtensionCommonInfo) -> List[str]:
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        ext_remote_info = ext_manager.get_registry_extension_dict(ext_item.package_id)
        try:
            from omni.kit.registry.nucleus import get_extension_metadata_possible_urls
        except ImportError:
            return None
        return get_extension_metadata_possible_urls(ext_remote_info)


@lru_cache()
def get_ext_data_fetcher():  # pragma: no cover
    return ExtDataFetcher()
