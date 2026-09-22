# Copyright (c) 2020-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.client
from omni.pointcloud.manager import PotreeApiDelegate


class E57PotreeApiDelegate(PotreeApiDelegate):
    __E57_URL_HASH_CACHE = {}

    def __init__(self):
        super().__init__()

    def can_handle_url(self, url: str) -> bool:
        return E57PotreeApiDelegate.__can_handle_url(url)

    def get_cache_root(self, cache_base_path: str, url: str) -> str:
        return ""

    def get_allow_write_bin_files(self) -> bool:
        return False

    def get_allow_write_hrc_files(self) -> bool:
        return False

    def get_allow_write_metadata_file(self) -> bool:
        return False

    def get_allow_write_usd_files(self) -> bool:
        return False

    def get_allow_write_vdb_files(self) -> bool:
        return False

    def get_cache_url(self, cache_base_path: str, url: str) -> str:
        if cache_base_path and url and self.can_handle_url(url):
            if url not in E57PotreeApiDelegate.__E57_URL_HASH_CACHE:
                result, list_entry = omni.client.stat(url)
                if result == omni.client.Result.OK and list_entry.hash:
                    E57PotreeApiDelegate.__E57_URL_HASH_CACHE[url] = list_entry.hash
            if url in E57PotreeApiDelegate.__E57_URL_HASH_CACHE:
                hash = E57PotreeApiDelegate.__E57_URL_HASH_CACHE[url]
                return omni.client.normalize_url(f"{cache_base_path}/{hash}")
        return ""

    def get_url_root(self, cache_base_path: str, url: str) -> str:
        return self.get_cache_url(cache_base_path, url)

    @staticmethod
    async def async_get_cache_url(cache_base_path: str, url: str) -> str:
        if cache_base_path and url and E57PotreeApiDelegate.__can_handle_url(url):
            if url not in E57PotreeApiDelegate.__E57_URL_HASH_CACHE:
                result, list_entry = await omni.client.stat_async(url)
                if result == omni.client.Result.OK and list_entry.hash:
                    E57PotreeApiDelegate.__E57_URL_HASH_CACHE[url] = list_entry.hash
            if url in E57PotreeApiDelegate.__E57_URL_HASH_CACHE:
                hash = E57PotreeApiDelegate.__E57_URL_HASH_CACHE[url]
                return omni.client.normalize_url(f"{cache_base_path}/{hash}")
        return ""

    @staticmethod
    def __can_handle_url(url: str) -> bool:
        url_lower = url.lower()
        return True if url_lower.startswith("omniverse://") and url_lower.endswith(".e57") else False
