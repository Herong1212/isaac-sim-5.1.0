# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
import omni.client

from typing import Dict
from datetime import datetime
from omni.kit.widget.filebrowser import (
    FileBrowserModel,
    FileBrowserItem,
    find_thumbnails_for_files_async,
    FileBrowserItemFields,
)
from omni.kit.search_core import AbstractSearchModel, AbstractSearchItem


class SearchResultsItem(FileBrowserItem):
    """A class representing a search result item in Omni UI file browser.

    This class inherits from FileBrowserItem and encapsulates details of a search result item, including its path, metadata fields, and whether it represents a folder.

    Args:
        path (str): The path or identifier for the search item.
        fields (FileBrowserItemFields): A collection of metadata fields associated with the search item.
        is_folder (bool): A flag indicating if the search item is a folder.
    """

    _thumbnail_dict: Dict = {}

    def __init__(self, path: str, fields: FileBrowserItemFields, is_folder: bool = False):
        """Initializes a new SearchResultsItem instance."""
        super().__init__(path, fields, is_folder=is_folder)

    class _RedirectModel(ui.AbstractValueModel):
        def __init__(self, search_model, field):
            super().__init__()
            self._search_model = search_model
            self._field = field

        def get_value_as_string(self):
            value = self._search_model[self._field]
            if isinstance(value, datetime):
                return FileBrowserItem.datetime_as_string(value)
            if isinstance(value, int) and self._field == "size":
                return FileBrowserItem.size_as_string(value)
            return str(value)

        def set_value(self, value):
            pass

        def __str__(self):
            return self.get_value_as_string()

    async def get_custom_thumbnails_for_folder_async(self) -> Dict:
        """Returns the thumbnail dictionary for this (folder) item.

        Returns:
            Dict: With children url's as keys, and url's to thumbnail files as values.
        """
        if not self.is_folder:
            return {}

        # Files in the root folder only
        file_urls = []
        for _, item in self.children.items():
            if item.is_folder or item.path in self._thumbnail_dict:
                # Skip if folder or thumbnail previously found
                pass
            else:
                file_urls.append(item.path)

        thumbnail_dict = await find_thumbnails_for_files_async(file_urls)

        for url, thumbnail_url in thumbnail_dict.items():
            if url and thumbnail_url:
                self._thumbnail_dict[url] = thumbnail_url

        return self._thumbnail_dict


class SearchResultsItemFactory:
    @staticmethod
    def create_item(search_item: AbstractSearchItem) -> SearchResultsItem:
        if not search_item:
            return None
        access = omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE
        fields = FileBrowserItemFields(search_item.name, search_item.date, search_item.size, access)
        item = SearchResultsItem(search_item.path, fields, is_folder=search_item.is_folder)
        item._models = (
            SearchResultsItem._RedirectModel(search_item, "name"),
            SearchResultsItem._RedirectModel(search_item, "date"),
            SearchResultsItem._RedirectModel(search_item, "size"),
        )
        return item

    @staticmethod
    def create_group_item(name: str, path: str) -> SearchResultsItem:
        access = omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE
        fields = FileBrowserItemFields(name, datetime.now(), 0, access)
        item = SearchResultsItem(path, fields, is_folder=True)
        return item


class SearchResultsModel(FileBrowserModel):
    """Class representing the search results model.

    This class extends FileBrowserModel to display and manage search results obtained from a search model. It creates a root group item labeled 'Search Results' and subscribes to changes provided by the search model. The subscription ensures that any updates in the search items are reflected in the file browser view.

    The destroy method removes the subscription and cleans up the search model to prevent circular dependencies. The get_item_children method retrieves the children items from the root group. If a filter function is set, it applies the filter to the list of children before returning them.

    Args:
        search_model (AbstractSearchModel): The instance that provides search items and controls the search logic.
    """

    def __init__(self, search_model: AbstractSearchModel, **kwargs):
        """Initializes a SearchResultsModel with a search model and optional keyword arguments. Sets up the root group and subscribes to item changes."""
        super().__init__(**kwargs)
        self._root = SearchResultsItemFactory.create_group_item("Search Results", "search_results://")
        self._search_model = search_model
        # Circular dependency
        self._dirty_item_subscription = self._search_model.subscribe_item_changed(self.__on_item_changed)

    def destroy(self):
        """Destroys the SearchResultsModel instance by removing subscriptions and releasing resources."""
        # Remove circular dependency
        self._dirty_item_subscription = None
        if self._search_model:
            self._search_model.destroy()
        self._search_model = None

    def get_item_children(self, item: SearchResultsItem) -> [SearchResultsItem]:
        """Retrieves child items from the search results. If the root group is not populated, it creates children from the search model and then applies optional filtering.

        Args:
            item (SearchResultsItem): The search item to retrieve children for.

        Returns:
            List[SearchResultsItem]: List of child items associated with the provided search item.
        """
        if self._search_model is None or item is not None:
            return []
        # OM-92499: Skip populate for empty search model items
        if not self._root.populated and self._search_model.items:
            for search_item in self._search_model.items:
                self._root.add_child(SearchResultsItemFactory.create_item(search_item))
            self._root.populated = True
        children = list(self._root.children.values())
        if self._filter_fn:
            return list(filter(self._filter_fn, children))
        else:
            return children

    def __on_item_changed(self, item):
        self._item_changed(item)
