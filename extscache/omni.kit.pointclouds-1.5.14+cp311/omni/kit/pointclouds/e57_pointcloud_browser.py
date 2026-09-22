# Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from __future__ import annotations

import asyncio
import weakref
from pathlib import Path
from typing import List, Optional

import carb
import omni.client

from .e57_potree_api_delegate import E57PotreeApiDelegate


class E57Item:
    def __del__(self):
        self.destroy()

    def __init__(self, name: str, icon_path: Optional[str] = None, url: str = ""):
        self.__children = []
        self.__icon_path = icon_path
        self.__name = name
        self.__sort_children = False
        self.__url = url

    def add_child(self, child: E57Item):
        self.__children.append(child)
        self.__sort_children = True

    def destroy(self):
        self.__children = None
        self.__icon_path = None
        self.__name = None
        self.__url = None
        self.__sort_children = None

    def get_children(self, sorted: bool = True) -> List[E57Item]:
        if self.__sort_children and sorted:
            self.__children.sort(key=lambda child: child.__get_sort_value())
            self.__sort_children = False
        return self.__children

    def get_icon_path(self) -> Optional[str]:
        return self.__icon_path

    def get_name(self) -> str:
        return self.__name

    def get_url(self) -> str:
        return self.__url

    def __get_sort_value(self) -> str:
        prefix = "0" if len(self.__children) > 0 else "1"
        return f"{prefix}:{self.__name.lower()}"


class E57PointCloudBrowser:
    def __del__(self):
        self.destroy()

    def __init__(self):
        self.__browser_root = None
        self.__fetch_files = True

    def destroy(self):
        if self.__browser_root:
            content_browser_api = E57PointCloudBrowser.__get_content_browser_api()
            if content_browser_api:
                content_browser_api.remove_point_cloud_container(self.__browser_root)
        self.__browser_root = None
        self.__fetch_files = None

    def fetch_e57_files(self):
        if self.__fetch_files:
            self.__fetch_files = False
            asyncio.ensure_future(E57PointCloudBrowser.__async_fetch_e57_files(weakref.ref(self)))

    def __add_browser_items_recursive(self, content_browser_api, item: E57Item, parent: Optional[E57Item] = None):
        url = item.get_url()
        if url:
            return content_browser_api.add_point_cloud(
                item.get_name(), url, icon_path=item.get_icon_path(), parent=parent, publish_event=False
            )
        children = item.get_children()
        if len(children) > 0:
            browser_item = content_browser_api.add_point_cloud_container(
                item.get_name(), icon_path=item.get_icon_path(), parent=parent
            )
            for child in children:
                self.__add_browser_items_recursive(content_browser_api, child, browser_item)
            return browser_item
        return None

    @staticmethod
    def __get_content_browser_api():
        try:
            import omni.pointcloud.content_browser

            content_browser_api = omni.pointcloud.content_browser.api()
            if content_browser_api and content_browser_api.is_valid():
                return content_browser_api
        except ImportError:
            pass
        return None

    @staticmethod
    async def __async_fetch_e57_files(self_ref):
        browser_sources = carb.settings.get_settings().get("exts/omni.kit.pointclouds/browser_sources")
        cache_base_path = ""
        try:
            from omni.pointcloud.manager import PointCloudSettings

            cache_base_path = PointCloudSettings.get_cache_path()
        except ImportError:
            pass
        icon_folder = Path(__file__).parent.absolute().parent.parent.parent.joinpath("data").joinpath("icons")
        root_item = E57Item("E57 Sources")
        for browser_source in browser_sources:
            name = browser_source
            if name.startswith("omniverse://"):
                name = name[12:]
            browser_item = E57Item(name, icon_path=f"{icon_folder}/browser_icon.svg")
            await E57PointCloudBrowser.__async_fetch_e57_files_recursive(
                browser_item, browser_source, cache_base_path, icon_folder
            )
            if len(browser_item.get_children()) > 0:
                root_item.add_child(browser_item)
        if len(root_item.get_children()) > 0:
            content_browser_api = E57PointCloudBrowser.__get_content_browser_api()
            self = self_ref()
            if content_browser_api and self:
                self.__browser_root = self.__add_browser_items_recursive(content_browser_api, root_item)

    @staticmethod
    async def __async_fetch_e57_files_recursive(parent_item: E57Item, url: str, cache_base_path: str, icon_folder: str):
        result, list_entries = await omni.client.list_async(url)
        if result == omni.client.Result.OK:
            for list_entry in list_entries:
                child_name = list_entry.relative_path
                child_url = f"{url}/{child_name}"
                if list_entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
                    child_item = E57Item(child_name)
                    await E57PointCloudBrowser.__async_fetch_e57_files_recursive(
                        child_item, child_url, cache_base_path, icon_folder
                    )
                    if len(child_item.get_children()) > 0:
                        parent_item.add_child(child_item)
                elif child_name.lower().endswith(".e57"):
                    cache_url = await E57PotreeApiDelegate.async_get_cache_url(cache_base_path, child_url)
                    result, _ = await omni.client.stat_async(cache_url)
                    icon_path = None
                    if result != omni.client.Result.OK:
                        icon_path = f"{icon_folder}/browser_warning.svg"
                    parent_item.add_child(E57Item(child_name, icon_path=icon_path, url=child_url))
