# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# pylint: disable=attribute-defined-outside-init, protected-access
# pylint: disable=access-member-before-definition
# pylint: disable=too-many-lines
"""This module provides a UI for managing and interacting with extensions, allowing users to search, filter, sort, and perform actions on extensions within a list view."""

from __future__ import annotations

__all__ = []

import asyncio
import contextlib
import fnmatch
from collections import OrderedDict, defaultdict
from enum import IntFlag
from functools import lru_cache
from typing import Callable, List, Optional

import carb
import carb.settings
import omni.ext
import omni.kit.app
import omni.kit.commands
import omni.ui as ui
from carb.eventdispatcher import get_eventdispatcher
from omni.kit.widget.filter import FilterButton
from omni.kit.widget.options_menu import OptionItem, OptionSeparator
from omni.ui import color as cl

from .common import (
    EXTENSION_PULL_STARTED_GLOBAL_EVENT,
    REGISTRIES_CHANGED_GLOBAL_EVENT,
    ExtAuthorGroup,
    ExtensionCommonInfo,
    ExtSource,
    PageBase,
    get_categories,
    get_options,
    is_community_tab_enabled,
)
from .ext_components import ExtensionToggle, ExtSourceSelector, SearchWidget
from .ext_controller import are_featured_exts_enabled, get_default_search_words
from .utils import get_ext_info_dict, get_extpath_git_ext

ext_manager = None


# Sync only once for now
@lru_cache()
def _sync_registry():
    if carb.settings.get_settings().get("/exts/omni.kit.window.extensions/sync_registry"):
        ext_manager.refresh_registry()


class ExtGroupItem(ui.AbstractItem):
    """A class representing a group of extensions in a UI list.

    This class holds information about an extension group, including its name, total item count, and
    associated items, in the context of a UI application that manages extensions.

    Args:
        name (str): The display name for the extension group."""

    def __init__(self, name):
        """Initializes a new instance of the ExtGroupItem with a given name."""
        super().__init__()
        self.name = name
        self.total_count = 0
        self.items = []
        self.ext_source = ExtSource.NVIDIA

    def contains(self, ext_summary):
        """Checks if the given extension summary is contained within the group.

        ext_summary (:obj:`ExtensionCommonInfo`): The extension summary to be checked against the group."""
        return True

    def is_expanded_by_default(self):
        """Determines if the group should be expanded by default when displayed."""
        return True


class ExtCoreGroupItem(ExtGroupItem):
    def contains(self, ext_summary: ExtSummaryItem):
        return ext_summary.is_core and not ext_summary.is_internal and not ext_summary.is_deprecated


class ExtSampleGroupItem(ExtGroupItem):
    def contains(self, ext_summary: ExtSummaryItem):
        return ext_summary.is_sample and not ext_summary.is_internal and not ext_summary.is_deprecated


class ExtInternalGroupItem(ExtGroupItem):
    def contains(self, ext_summary: ExtSummaryItem):
        return not ext_summary.is_sample and ext_summary.is_internal and not ext_summary.is_deprecated


class ExtDeprecatedGroupItem(ExtGroupItem):
    def contains(self, ext_summary: ExtSummaryItem):
        return ext_summary.is_deprecated

    def is_expanded_by_default(self):
        return False


class ExtToggleableGroupItem(ExtGroupItem):
    def contains(self, ext_summary):
        return ext_summary.toggleable


class ExtNonToggleableGroupItem(ExtGroupItem):
    def contains(self, ext_summary):
        return not ext_summary.toggleable

    def is_expanded_by_default(self):
        return False


class ExtAuthorGroupItem(ExtGroupItem):
    def __init__(self, name, author_group: ExtAuthorGroup):
        super().__init__(name)
        self.author_group = author_group
        self.ext_source = ExtSource.THIRD_PARTY

    def contains(self, ext_summary):
        return ext_summary.author_group == self.author_group

    def is_expanded_by_default(self):
        return True


class ExtSummaryItem(ui.AbstractItem):
    """An abstract item that represents an extension summary"""

    def __init__(self, ext_summary: dict):
        super().__init__()
        self.fullname = ext_summary["fullname"]
        self.flags = ext_summary["flags"]
        self.enabled_ext = ext_summary["enabled_version"]
        self.latest_ext = ext_summary["latest_version"]

        self.default_ext = self.latest_ext
        self.enabled = bool(self.flags & omni.ext.EXTENSION_SUMMARY_FLAG_ANY_ENABLED)

        if self.enabled:
            self.default_ext = self.enabled_ext

        self.id = self.default_ext["id"]
        current_ext = self.enabled_ext["id"] if self.enabled_ext["id"] else self.default_ext
        is_latest = current_ext == self.latest_ext["id"]
        self.can_update = self.enabled and not is_latest

        # Query more info
        ext_info, is_local = get_ext_info_dict(ext_manager, self.default_ext)

        # Take latest version (in terms of semver) and grab publish date from it if any, for sorting invert it.
        latest_info = ext_info if is_latest else get_ext_info_dict(ext_manager, self.latest_ext)[0]
        publish_date = latest_info.get("package", {}).get("publish", {}).get("date", 0)
        self.publish_date_rev = -publish_date

        # Move all attributes from ExtensionCommonInfo class to this class
        self.__dict__.update(ExtensionCommonInfo(self.id, ext_info, is_local).__dict__)


class ExtSummariesModel(ui.AbstractItemModel):
    """Extension summary model that watches the changes in ext manager.

    This model provides an organized view of extensions, including filtering,
    sorting, and categorization features. It keeps track of extension states and
    updates the view accordingly when changes are detected.

    Args:
        flat (Optional[bool]): If set to True, the model will flatten the hierarchy of extension groups."""

    class SortDirection(IntFlag):
        """An enumeration to define sorting directions.

        This enumeration provides flags to specify the sorting order for items, such as ascending or descending.

        Members:
        NONE: No sorting direction.
        Ascending: Items should be sorted in ascending order.
        Descending: Items should be sorted in descending order."""

        NONE = 0
        """IntFlag: Represents no sorting."""
        Ascending = 1
        """IntFlag: Represents ascending sorting."""
        Descending = 2
        """IntFlag: Represents descending sorting."""

    def __init__(self, flat=None):
        """Initializes a new instance of ExtSummariesModel."""
        super().__init__()

        global ext_manager
        app = omni.kit.app.get_app()
        ext_manager = app.get_extension_manager()

        self._ext_summaries = {}
        self._sorted_summaries = []
        self._subs = None
        self.tree_view = None
        self.on_refresh_cb = None
        self._filter_category = None
        self._filter_ext_source = None
        self._filter_name_text = None
        self._groups = None
        self._sort_attr = None
        self._sort_direction = None
        self._expanded_groups = False

        # Order matters here, because contains() matches first group
        self._groups = [
            ExtAuthorGroupItem("User", ExtAuthorGroup.USER),
            ExtAuthorGroupItem("Partner", ExtAuthorGroup.PARTNER),
            ExtAuthorGroupItem("Community - Verified", ExtAuthorGroup.COMMUNITY_VERIFIED),
            ExtAuthorGroupItem("Community - Unverified", ExtAuthorGroup.COMMUNITY_UNVERIFIED),
            ExtCoreGroupItem("Core"),
            ExtSampleGroupItem("Sample"),
            ExtInternalGroupItem("Internal"),
            ExtDeprecatedGroupItem("Deprecated"),
            # ExtToggleableGroupItem("Example"),
            # ExtNonToggleableGroupItem("Non-Toggleable"),
        ]

        # Attribute in ExtSummaryItem to sort by. For each attribute store order of sort in a dict (can be toggled)
        self._sort_attr = "name"
        self._sort_direction = ExtSummariesModel.SortDirection.Ascending

        # subscribe for ext manager changes and generic event
        def on_change(*_):
            self._resync_exts()

        self._subs = [
            get_eventdispatcher().observe_event(event_name=omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED, on_event=on_change),
            get_eventdispatcher().observe_event(event_name=omni.ext.GLOBAL_EVENT_FOLDER_CHANGED, on_event=on_change),
            get_eventdispatcher().observe_event(event_name=REGISTRIES_CHANGED_GLOBAL_EVENT, on_event=on_change),
            get_eventdispatcher().observe_event(event_name=EXTENSION_PULL_STARTED_GLOBAL_EVENT, on_event=on_change),
        ]

        # Current name filter
        self._filter_name_text = []

        # Current category filter
        self._filter_category = ""

        # Current ext source
        self._filter_ext_source = ExtSource.NVIDIA

        # Hacky link back to tree view to be able to update expanded state
        self.tree_view = None

        # on refresh callback
        self.on_refresh_cb = None

        # Builds a list
        self._resync_exts()

    def resync_registry(self):
        # NOTE: this call shows as memory leak
        # [Warning] [omni.ext._impl._internal] omni.kit.window.extensions-1.2.7 -> <class 'omni.kit.window.extensions.extension.ExtsWindowExtension'>:
        #           extension object is still alive, something holds a reference on it. References: [0]: type: <class 'cell'>, id: 0x1a3174b0970
        if carb.settings.get_settings().get("/exts/omni.kit.window.extensions/sync_registry"):
            ext_manager.refresh_registry()

    def refresh_all(self):
        self._resync_exts()

    def _resync_exts(self):
        get_extpath_git_ext.cache_clear()
        for _, _, clear_cache in ExtsListWidget.searches.values():
            if clear_cache is not None:
                clear_cache()

        _sync_registry()

        if not ext_manager:
            return
        ext_summaries = ext_manager.fetch_extension_summaries()

        # groups
        for g in self._groups:
            g.total_count = 0

        self._ext_summaries = {}
        for ext_s in ext_summaries:
            item = ExtSummaryItem(ext_s)

            # if extension is enabled but something went wrong during enabling, disable it
            if item.enabled and item.failed:
                omni.kit.app.get_app().get_extension_manager().set_extension_enabled(item.id, False)
                item.enabled = False

            # assign group
            item.group = next(x for x in self._groups if x.contains(item))
            item.group.total_count += 1

            self._item_changed(item)  # pylint: disable=not-callable
            self._ext_summaries[ext_s["fullname"]] = item

        self._item_changed(None)  # pylint: disable=not-callable

        # Update expanded state after tree was built and rendered
        if not self._expanded_groups:
            asyncio.ensure_future(self._delayed_expand())
            self._expanded_groups = True

        self._sorted_summaries = list(self._ext_summaries.values())
        self._make_sure_sorted()

    async def _delayed_expand(self):
        loop = 10
        while loop > 0:
            await omni.kit.app.get_app().next_update_async()
            if self.tree_view:
                for g in self._groups:
                    self.tree_view.set_expanded(g, g.is_expanded_by_default(), False)
                return
            loop += -1

    def _refresh_item_group_lists(self):
        # Filtering logic here:
        matching_fns = []

        # Split text in words and look for @keywords. Add matching functions and remove from the list.
        # To remove from list while iterating use backward iteration trick.
        parts = self._filter_name_text.copy()
        for i in range(len(parts) - 1, -1, -1):
            w = parts[i]
            if w.startswith("@"):
                # Predefined keywords or use default ones
                fn = ExtsListWidget.searches.get(w, [None, None, None])[1]
                if fn is None:
                    fn = lambda item, w=w: w[1:] in item.keywords
                matching_fns.append(fn)
                del parts[i]

        # Whatever left just use as wildcard search:
        if len(parts) > 0:
            for part in parts:
                filter_str = f"*{part.lower()}*"
                matching_fns.append(
                    lambda item, filter_str=filter_str: fnmatch.fnmatch(item.name.lower(), filter_str)
                    or fnmatch.fnmatch(item.fullname.lower(), filter_str)
                )

        # If category filter enabled, add matching function for it
        if len(self._filter_category) != 0:
            matching_fns.append(lambda item: self._filter_category == item.category)
        else:
            hidden_categories = [c for c, v in get_categories().items() if v.get("hidden", False)]
            matching_fns.append(lambda item: item.category not in hidden_categories)

        # Show item only if it matches all matching functions
        for group in self._groups:
            group.items = [v for v in self._sorted_summaries if v.group == group and all(f(v) for f in matching_fns)]
            self._item_changed(group)  # pylint: disable=not-callable

        # callback
        if self.on_refresh_cb:
            self.on_refresh_cb()

    def get_item_children(self, item):
        """Reimplemented from AbstractItemModel

        Args:
            item: The parent item whose children are to be retrieved.

        Returns:
            A list of child items."""

        if item is None:
            self._refresh_item_group_lists()
            return [g for g in self._groups if g.total_count and g.ext_source == self._filter_ext_source]
        if isinstance(item, ExtGroupItem):
            return item.items

        return []

    def get_item_value_model_count(self, item):
        """Gets the count of value models for a given item.

        Args:
            item: The item for which the value model count is requested.

        Returns:
            The count of value models for the item."""
        return 1

    def get_item_value_model(self, item, column_id):
        """Gets the value model for a given item and column.

        Args:
            item: The item for which the value model is requested.
            column_id (int): The column identifier.

        Returns:
            The requested value model."""
        return

    def filter_by_text(self, filters):
        """Specify the filter string that is used to reduce the model

        Args:
            filter_name_text (str): The text to filter by.
            filters (list): Additional filters to apply."""
        self._filter_name_text = filters

        # Avoid refreshing on every key typed, as it can be slow. Add delay:
        self._refresh_once_with_delay(delay=0.3)

    def select_category(self, filter_category):
        """Selects a specific category to filter the extensions by.

        Args:
            filter_category (str): The category to filter by."""
        # Special case for "All" => ""
        if self._filter_category == filter_category:
            return

        self._filter_category = filter_category
        self._refresh_once_with_delay(delay=0.1)

    def select_ext_source(self, ext_source):
        """Selects a specific extension source to filter the extensions by.

        Args:
            ext_source (ExtSource): The extension source to filter by."""
        if self._filter_ext_source == ext_source:
            return False

        self._filter_ext_source = ext_source
        self._resync_exts()
        return True

    def _refresh_once_with_delay(self, delay: float):
        """Call refresh once after `delay` seconds. If called again before `delay` is passed the timer gets reset."""

        async def _delayed_refresh():
            await asyncio.sleep(delay)
            self._item_changed(None)  # pylint: disable=not-callable

        with contextlib.suppress(Exception):
            self._refresh_task.cancel()

        self._refresh_task = asyncio.ensure_future(_delayed_refresh())

    def sort_by_attr(self, attr: str):
        """Sorts the model by a specified attribute.

        Args:
            attr (str): The attribute to sort by."""
        if attr is None:
            return

        if self._sort_attr != attr:
            self._sort_attr = attr

        self._make_sure_sorted()

    def sort_direction(self, direction: SortDirection):
        """Sets the sort direction for the model.

        Args:
            direction (SortDirection): The direction to sort by."""
        if direction is None:
            return

        self._sort_direction = direction

        self._make_sure_sorted()

    def _make_sure_sorted(self):
        # Sort order setting is global
        reverse = self._sort_direction == ExtSummariesModel.SortDirection.Descending

        # Attribute value getter
        key_fn = lambda x: getattr(x, self._sort_attr)
        cmp_fn = (lambda x, y: x >= y) if reverse else (lambda x, y: x <= y)

        # Check that it is already sorted to avoid list rebuild
        is_sorted_fn = lambda v: all(cmp_fn(key_fn(v[i]), key_fn(v[i + 1])) for i in range(len(v) - 1))

        if not is_sorted_fn(self._sorted_summaries):
            self._sorted_summaries = sorted(self._sorted_summaries, key=key_fn, reverse=reverse)
            self._item_changed(None)  # pylint: disable=not-callable

    def destroy(self):
        """Cleans up resources and references held by the ExtSummariesModel."""
        global ext_manager

        self._ext_summaries = {}
        self._sorted_summaries = []
        self._subs = None
        self.tree_view = None
        self.on_refresh_cb = None
        self._filter_category = None
        self._filter_ext_source = None
        self._filter_name_text = None
        self._groups = None
        self._sort_attr = None
        self._sort_direction = None
        ext_manager = None

    # public accessors
    delayed_expand = _delayed_expand


class ExtensionCardWidget:
    """A UI widget for displaying extension cards in a list.

    This widget is responsible for creating the visual representation of an extension summary item.
    It includes methods for building different parts of an extension card, such as the body,
    footer, and the list item itself. The widget is used in the context of a larger UI structure
    that displays a list of extensions, allowing users to view and interact with extensions
    available in the system."""

    @staticmethod
    def build_ext_card_body(item: ExtSummaryItem):
        """Builds the extension card body UI for a given extension item.

        Args:
            item (:obj:`ExtSummaryItem`): The extension summary item to build the UI for."""
        with ui.HStack(height=0):
            with ui.VStack(width=0, height=0):
                ui.Spacer(width=0, height=4)
                ui.Image(
                    item.icon_path,
                    style_type_name_override="ExtensionList.Image",
                    name="Icon",
                    width=48,
                    height=48,
                )
                ui.Spacer(width=0)
            with ui.VStack(height=0, spacing=0):
                with ui.HStack():
                    ui.Label(
                        item.title,
                        style_type_name_override="ExtensionList.Label",
                        name="Title",
                        elided_text=True,
                    )
                    ExtensionToggle(item, show_install_button=not item.is_untrusted)
                    ui.Spacer(width=4)
                with ui.HStack():
                    categories = get_categories()
                    display_category = item.category
                    if display_category in categories:
                        display_category = categories[display_category]["name"]

                    ui.Label(
                        display_category,
                        style_type_name_override="ExtensionList.Label",
                    )
                    if get_options().show_update_icon and item.can_update:
                        ui.Label(
                            "Update",
                            alignment=ui.Alignment.RIGHT_CENTER,
                            name="UpdateAvailable",
                        )
                        with ui.VStack(width=0):
                            ui.Spacer(width=0)
                            ui.Image(
                                name="UpdateAvailable",
                                width=18,
                                height=18,
                                alignment=ui.Alignment.RIGHT_CENTER,
                            )
                            ui.Spacer(width=0)
                ui.Label(
                    item.fullname,
                    style_type_name_override="ExtensionList.Label",
                    elided_text=True,
                )

    @staticmethod
    def build_ext_card_footer(item: ExtSummaryItem, height=0, full_width=False):
        """Builds the extension card footer UI for a given extension item.

        Args:
            item (:obj:`ExtSummaryItem`): The extension summary item to build the UI for.
            height (int): The height of the footer area.
            full_width (bool): Whether the footer should span the full width of the card."""
        with ui.Frame(style_type_name_override="ExtInfoFooter", height=height):
            with ui.ZStack():
                ui.Rectangle(style_type_name_override="ExtInfoFooter.Rectangle")
                with ui.HStack():

                    support_name = ""
                    if item.author_group == ExtAuthorGroup.NVIDIA:
                        if item.is_core:
                            support_name = "Core"
                        elif item.is_sample:
                            support_name = "Sample"
                        elif item.is_internal:
                            support_name = "Internal"
                        support_label = support_name
                    else:
                        support_name = "Community"
                        support_label = item.author_group.get_ui_name()

                    ui.Label(
                        support_label,
                        style_type_name_override="ExtensionList.Label",
                        name=support_name,
                        style={"margin_width": 4},
                    )

                    if item.is_deprecated:
                        ui.Label(
                            "Deprecated",
                            style_type_name_override="ExtensionList.Label",
                            name="Deprecation",
                            width=0,
                        )
                        ui.Spacer(width=20)

                    location_text = ""
                    if full_width or item.location_tag:
                        if full_width:
                            location_text = "Remote" if item.provider_name else "Local"
                        else:
                            location_text = item.location_tag.title()

                    ui.Label(
                        f"{location_text} | v{item.version}" if location_text else f"v{item.version}",
                        style_type_name_override="ExtensionList.Label",
                        identifier="ext_card_label",
                        name="Version",
                        width=132,
                        elided_text=True,
                        style={"margin_width": 4},
                    )

    @staticmethod
    def build_ext_list_item(item: ExtSummaryItem):
        """Builds the UI list item for a given extension item.

        Args:
            item (:obj:`ExtSummaryItem`): The extension summary item to build the UI for."""
        with ui.Frame(style_type_name_override="ExtensionItem.Frame"):
            with ui.ZStack():
                ui.Rectangle(style_type_name_override="ExtInfoBackgroundRect")
                with ui.VStack():
                    ExtensionCardWidget.build_ext_card_body(item)
                    ExtensionCardWidget.build_ext_card_footer(item, full_width=True)


class ExtsDelegate(ui.AbstractItemDelegate):
    """A delegate class used within the omni.kit.window.extensions-1.2.7 extension UI.

    This class is responsible for rendering the items within the extensions list. It handles the creation of widgets for each extension item and their groups, as well as the visuals for expanded or collapsed state of groups in the list.

    The class works in conjunction with the ExtSummariesModel, which provides the data for the extensions, and the ExtensionCardWidget, which provides the layout for each extension item.

    The delegate utilizes the ui.AbstractItemDelegate interface to manage the widgets displayed in the UI. It overrides the build_branch, build_widget, and build_header methods to provide the necessary functionality for the extensions list UI.
    """

    def build_branch(self, model, item, column_id, level, expanded):
        """ui.AbstractItemDelegate API: Create a branch widget that opens or closes subtree

        Args:
            model: The model associated with the tree view.
            item: The item for which to build the branch.
            column_id: The column identifier.
            level: The indentation level of the branch.
            expanded: Whether the branch is expanded or not."""
        return

    def _build_group_widget(self, item, expanded):
        with ui.ZStack():
            with ui.VStack():
                ui.Spacer(height=1)
                ui.Rectangle(height=30, name="ExtensionListGroup")
            with ui.HStack():
                image_name = "expanded" if expanded else ""
                ui.Image(
                    style_type_name_override="ExtensionList.Group.Icon",
                    name=image_name,
                    width=31,
                    height=31,
                    alignment=ui.Alignment.LEFT_CENTER,
                )
                ui.Label(
                    "{} ({}/{})".format(item.name, len(item.items), item.total_count),
                    style_type_name_override="ExtensionList.Group.Label",
                )

    def build_widget(self, model, item, column_id, level, expanded):
        """ui.AbstractItemDelegate API: Create a widget per column

        Args:
            model: The model associated with the tree view.
            item: The item for which to build the widget.
            column_id: The column identifier.
            level: The indentation level of the widget.
            expanded: Whether the branch is expanded or not."""

        if isinstance(item, ExtGroupItem):
            self._build_group_widget(item, expanded)
        else:
            ExtensionCardWidget.build_ext_list_item(item)

    def build_header(self, column_id):
        """Builds the header for a given column.

        Args:
            column_id: The column identifier."""


class SearchMenuPage(PageBase):
    def __init__(self, owner_cls=None):
        self._owner_cls = owner_cls
        self._search = None
        self._filter_button = None

    def build_tab(self, ext_info, ext_item: bool):
        # Search field
        with ui.HStack(width=ui.Fraction(2)):
            self._search = SearchWidget(on_search_fn=self._filter_by_text)
            default_search_words = get_default_search_words()
            if default_search_words:
                self._search.search_words = default_search_words

        ui.Spacer(width=10)
        # Category selector
        category_list = [("All", "")] + [(v["name"], c) for c, v in get_categories().items()]
        self._category_combo = ui.ComboBox(0, *[c[0] for c in category_list], style={"padding": 4})
        self._category_combo.model.add_item_changed_fn(
            lambda model, item: self._owner_cls._select_category(
                category_list[model.get_item_value_model(item).as_int][1]
            )
        )

        ui.Spacer(width=5)
        # Filter button
        self._build_filter_button()

    def destroy(self):
        self._owner_cls = None
        if self._search:
            self._search.destroy()
            self._search = None
        if self._filter_button:
            self._filter_button.destroy()
            self._filter_button = None

    def sort_index(self):
        return "1stMenuPage"

    @staticmethod
    def get_tab_name():
        return "SearchMenuPage"

    def rebuild_filter_menu(self):
        """Rebuilds the filter menu based on current filter settings."""
        if self._filter_button:
            option_items = self._build_filter_items()
            self._filter_button.model.rebuild_items(option_items)

    def close_menu(self):
        """Closes the filter menu."""
        if self._filter_button:
            fb = self._filter_button
            if fb._options_menu:
                fb._options_menu.hide()

    async def __update_filter(self, search_key: str) -> None:
        if search_key:
            self._search.toggle_filter(search_key)

        await omni.kit.app.get_app().next_update_async()
        self._filter_by_text(self._search.search_words)

    def _build_filter_items(self) -> List[OptionItem]:
        option_items = []
        filters = self._search.get_filters()
        for search_key, (search_description, _, _) in self._owner_cls.searches.items():
            if not search_description:
                option_items.append(OptionSeparator())
                continue
            option_item = OptionItem(
                search_description,
                on_value_changed_fn=lambda m, sk=search_key: asyncio.ensure_future(self.__update_filter(sk)),
            )
            option_item.model.set_value(search_key in filters)
            option_items.append(option_item)

        return option_items

    def _build_filter_button(self):
        option_items = self._build_filter_items()
        self._filter_button = FilterButton(option_items)

        # set defaults
        default_filter = carb.settings.get_settings().get("/exts/omni.kit.window.extensions/default_filter")
        if not isinstance(default_filter, list):
            default_filter = [default_filter]
        for fltr in default_filter:
            for item in self._filter_button._options_model.get_item_children(None):
                if item.name.lower() == fltr.lower():
                    item.value = True

    def _filter_by_text(self, search_words: Optional[List[str]]):
        """Set the search filter string to the models and widgets"""
        model = self._owner_cls._model
        if search_words is not None:
            model.filter_by_text(search_words + self._search.get_filters())
        else:
            model.filter_by_text(self._search.get_filters())


class SortMenuPage(PageBase):
    def __init__(self, owner_cls=None):
        self._owner_cls = owner_cls

        # Sort menu. One day it will be a hamburger. One can dream.
        self._sortby_menu = ui.Menu(
            "Sort By", style=ExtsListWidget.menu_style, menu_compatibility=False, tearable=False
        )
        self.rebuild_sortby_menu()

    def build_tab(self, ext_info, ext_item: bool):
        # Sort-By button
        self._sortby_button = ui.Button(name="sortby", width=24, height=24, clicked_fn=self._sortby_menu.show)

    def destroy(self):
        self._owner_cls = None
        self._sortby_menu = None
        self._sortby_button = None

    def sort_index(self):
        return "2ndMenuPage"

    @staticmethod
    def get_tab_name():
        return "SortMenuPage"

    def rebuild_sortby_menu(self):
        """Rebuilds the 'Sort By' menu with sort options for the extension list."""

        def reset_sort():
            asyncio.ensure_future(update_sort("name", ExtSummariesModel.SortDirection.Ascending))

        async def update_sort(sb: str, sd: ExtSummariesModel.SortDirection):
            model = self._owner_cls._model
            if sb:
                await omni.kit.app.get_app().next_update_async()
                model.sort_by_attr(sb)

            if sd is not ExtSummariesModel.SortDirection.NONE:
                await omni.kit.app.get_app().next_update_async()
                model.sort_direction(sd)

            sort_by = model._sort_attr
            sort_direction = model._sort_direction

            # change button color
            self._sortby_button.name = (
                "sortby"
                if sort_by == "name" and sort_direction == ExtSummariesModel.SortDirection.Ascending
                else "sortby_on"
            )

            self._sortby_menu.clear()
            with self._sortby_menu:
                ExtsListWidget.build_menu_header("Sort", reset_sort)

                ui.MenuItem(
                    "Name",
                    triggered_fn=lambda: asyncio.ensure_future(
                        update_sort("name", ExtSummariesModel.SortDirection.NONE)
                    ),
                    checkable=True,
                    checked=sort_by == "name",
                )
                ui.MenuItem(
                    "Enabled",
                    triggered_fn=lambda: asyncio.ensure_future(
                        update_sort("enabled", ExtSummariesModel.SortDirection.NONE)
                    ),
                    checkable=True,
                    checked=sort_by == "enabled",
                )
                ui.MenuItem(
                    "Publish Date",
                    triggered_fn=lambda: asyncio.ensure_future(
                        update_sort("publish_date_rev", ExtSummariesModel.SortDirection.NONE)
                    ),
                    checkable=True,
                    checked=sort_by == "publish_date_rev",
                )
                ui.Separator()
                ui.MenuItem(
                    "Ascending",
                    triggered_fn=lambda: asyncio.ensure_future(
                        update_sort(None, ExtSummariesModel.SortDirection.Ascending)
                    ),
                    checkable=True,
                    checked=sort_direction == ExtSummariesModel.SortDirection.Ascending,
                )
                ui.MenuItem(
                    "Descending",
                    triggered_fn=lambda: asyncio.ensure_future(
                        update_sort(None, ExtSummariesModel.SortDirection.Descending)
                    ),
                    checkable=True,
                    checked=sort_direction == ExtSummariesModel.SortDirection.Descending,
                )

        asyncio.ensure_future(update_sort(None, ExtSummariesModel.SortDirection.NONE))


class OptionsMenuPage(PageBase):
    def __init__(self, owner_cls=None):
        self._owner_cls = owner_cls

        self._options_menu = ui.Menu(
            "Options", style=ExtsListWidget.menu_style, menu_compatibility=False, tearable=False
        )
        self.rebuild_options_menu()

    def build_tab(self, ext_info, ext_item: bool):
        ui.Button(name="options", width=24, height=24, clicked_fn=self._options_menu.show)

    def destroy(self):
        self._owner_cls = None
        self._options_menu = None

    def sort_index(self):
        return "3rdMenuPage"

    @staticmethod
    def get_tab_name():
        return "OptionsMenuPage"

    def rebuild_options_menu(self):
        """Rebuilds the options menu for the extension list."""
        from .ext_export_import import import_ext

        self._options_menu.clear()
        with self._options_menu:
            ExtsListWidget.build_menu_header("Options", None)
            ui.MenuItem("Settings", triggered_fn=lambda: self._owner_cls._show_properties())
            ui.MenuItem("Refresh", triggered_fn=lambda: self._owner_cls._model.refresh_all())
            ui.MenuItem("Resync Registry", triggered_fn=lambda: self._owner_cls._model.resync_registry())
            ui.MenuItem("Import Extension", triggered_fn=import_ext)


class ExtsListWidget:
    """A widget for listing and interacting with extensions.

    This widget provides functionalities to create, search, filter, sort, and
    interact with extensions in a list view. It supports operations such as
    refreshing the list, resyncing the registry, importing extensions, and
    accessing extension settings. Additional features include displaying
    extension cards with detailed information, categorization of extensions, and
    a search field with advanced filtering capabilities."""

    menus = [SearchMenuPage, SortMenuPage, OptionsMenuPage]
    """list[PageBase] - List of menus added to the ExtInfoWidget as tabs"""

    menu_style = {
        "padding": 2,
        "Menu.Item.CheckMark": {"color": cl.shade(cl("#34C7FF"))},
        "Titlebar.Background": {"background_color": cl.shade(cl("#1F2123"))},
        "Titlebar.Title": {"color": cl.shade(cl("#848484"))},
        "Titlebar.Reset": {"background_color": 0},
        "Titlebar.Reset.Label": {"color": cl.shade(cl("#2E86A9"))},
        "Titlebar.Reset.Label:hovered": {"color": cl.shade(cl("#34C7FF"))},
    }
    """Menu style"""

    # Search configuration information as SearchKey:(SearchUiName, FilterBySearchKey, ClearSearchCache)
    searches = OrderedDict(
        {
            "@startup": ("Startup", lambda item: item.is_startup, None),
            "@update": ("Update Available", lambda item: item.can_update, None),
            "_1": (None, None, None),
            "@enabled": ("Enabled", lambda item: bool(item.flags & omni.ext.EXTENSION_SUMMARY_FLAG_ANY_ENABLED), None),
            "@nontoggleable": ("Non-Toggleable", lambda item: item.is_toggle_blocked, None),
            "_3": (None, None, None),
            "@feature": ("Featured", lambda item: item.feature or item.ext_source == ExtSource.THIRD_PARTY, None),
            "@bundled": ("Bundled", lambda item: bool(item.flags & omni.ext.EXTENSION_SUMMARY_FLAG_BUILTIN), None),
            "@app": ("App", lambda item: item.is_app, None),
            "_4": (None, None, None),
            "@installed": (
                "Installed",
                lambda item: bool(item.flags & omni.ext.EXTENSION_SUMMARY_FLAG_INSTALLED),
                None,
            ),
            "@remote": ("Remote", lambda item: not bool(item.flags & omni.ext.EXTENSION_SUMMARY_FLAG_BUILTIN), None),
        }
    )
    """OrderedDict[str, Tuple[Optional[str], Optional[Callable], Optional[Callable]]]: Configures search filters for extensions."""

    if are_featured_exts_enabled():
        searches["@feature"] = (
            "Featured",
            lambda item: item.is_featured or item.ext_source == ExtSource.THIRD_PARTY,
            None,
        )

    def __init__(self):
        """Initializes the ExtsListWidget with default settings."""
        import inspect

        # Extensions List Data Model
        self._model = ExtSummariesModel()
        self._model.on_refresh_cb = self._on_ext_list_refresh

        # Delegate to build list rows.
        self._delegate = ExtsDelegate()

        self.set_show_dependencies_fn(None)
        self.set_show_properties_fn(None)

        self.__menus = []
        for cls in ExtsListWidget.menus:
            # is constructor has "owner_cls" then pass owner_cls=self
            func = inspect.signature(cls.__init__)
            if "owner_cls" in func.parameters:
                self.__menus.append(cls(owner_cls=self))
            else:
                self.__menus.append(cls())

    @classmethod
    def build_menu_header(cls, title, clicked_fn):
        with ui.ZStack(height=0):
            ui.Rectangle(style_type_name_override="Titlebar.Background")
            with ui.VStack():
                ui.Spacer(height=3)
                with ui.HStack():
                    ui.Spacer(width=10)
                    ui.Label(title, style_type_name_override="Titlebar.Title")
                    ui.Spacer()
                    ui.Button(
                        "Reset all" if clicked_fn else " ",
                        style_type_name_override="Titlebar.Reset",
                        clicked_fn=clicked_fn,
                    )
                    ui.Spacer(width=10)
                ui.Spacer(height=2)

    def _on_key_pressed(self, key, mod, pressed):
        """Allow up/down arrow to be used to select prev/next extension"""

        def _select_next(treeview: ui.TreeView, model: ui.AbstractItemModel, after=True):
            full_list = model.get_item_children(None)
            selection = treeview.selection
            if not selection:
                treeview.selection = [full_list[0]]
            else:
                for group in full_list:
                    try:
                        group_list = group.items
                        index = group_list.index(selection[0])
                        index += 1 if after else -1
                        if index < 0 or index >= len(group_list):
                            return
                        treeview.selection = [group_list[index]]
                    except ValueError:
                        pass

        if not pressed:
            return
        if mod == 0 and key == int(carb.input.KeyboardInput.DOWN):
            _select_next(self.tree_view, self._model, after=True)
        elif mod == 0 and key == int(carb.input.KeyboardInput.UP):
            _select_next(self.tree_view, self._model, after=False)

    def _on_selection_changed(self, selection):
        item = selection[0] if len(selection) > 0 else None
        if item and isinstance(item, ExtGroupItem):
            self.tree_view.set_expanded(item, not self.tree_view.is_expanded(item), False)
            self.tree_view.clear_selection()
        else:
            self._ext_selected_fn(item)

    def _on_ext_list_refresh(self):
        cnt = defaultdict(int)
        for group in self._model._groups:
            cnt[group.ext_source] += len(group.items)
        for source, value in cnt.items():
            self._ext_source_selector.set_badge_number(source, value)

    def build(self):
        """Builds the main UI elements of the ExtsListWidget."""

        def get_page_index(page):
            if hasattr(page, "sort_index"):
                return page.sort_index()
            return f"999LastPage.{page.get_tab_name()}"

        menu_tabs = sorted(self.__menus, key=get_page_index)

        with ui.VStack(spacing=3):
            with ui.HStack(height=0):
                for page in menu_tabs:
                    page.build_tab(None, None)

            # Source selector (community tab)
            self._ext_source_selector = None
            if is_community_tab_enabled():
                self._ext_source_selector = ExtSourceSelector(self._select_ext_source)

            frame = ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                style_type_name_override="TreeView",
            )
            with frame:
                with ui.ZStack():
                    self.tree_view = ui.TreeView(
                        self._model,
                        header_visible=False,
                        delegate=self._delegate,
                        root_visible=False,
                        keep_expanded=False,
                    )
                    self._model.tree_view = self.tree_view
                    self.tree_view.set_selection_changed_fn(self._on_selection_changed)

                    # make that public
                    self.clear_selection = self.tree_view.clear_selection

            frame.set_key_pressed_fn(self._on_key_pressed)

    def set_show_dependencies_fn(self, fn: Callable):
        """{'Args': {'fn (Callable)': "The function to be called when the 'Show Extension Dependencies' option is selected."}}"""
        self._show_dependencies_fn = fn

    def set_ext_selected_fn(self, fn: Callable):
        """{'Args': {'fn (Callable)': 'The function to be called when an extension is selected from the list.'}}"""
        self._ext_selected_fn = fn

    def select_extension_by_name(self, name: str):
        """{'Args': {'name (str)': 'The name of the extension to select in the list.'}}"""
        for group in self._model.get_item_children(None):
            for item in group.items:
                if item.fullname == name:
                    self.tree_view.selection = [item]

    def _resync_registry(self):
        self._model.resync_registry()

    def _show_dependencies(self):
        if self._show_dependencies_fn:
            self._show_dependencies_fn()

    def set_show_properties_fn(self, fn: Callable):
        """{'Args': {'fn (Callable)': "The function to be called when the 'Settings' option is selected."}}"""
        self._show_properties_fn = fn

    def _show_properties(self):
        if self._show_properties_fn:
            self._show_properties_fn()

    def _select_category(self, category: str):
        """Set the category to show"""
        self._model.select_category(category)

    def _select_ext_source(self, ext_source):
        self._model.select_ext_source(ext_source)

    def rebuild_filter_menu(self):
        """Rebuilds the filter menu based on current filter settings."""
        for menu in self.__menus:
            if hasattr(menu, "rebuild_filter_menu"):
                menu.rebuild_filter_menu()

    def close_filter_menu(self):
        """Closes the filter menu."""
        for menu in self.__menus:
            if hasattr(menu, "close_menu"):
                menu.close_menu()

    def destroy(self):
        """Cleans up the ExtsListWidget and releases any associated resources."""
        self._delegate = None
        self._category_combo = None
        self._model.destroy()
        self._model = None
        self._ext_selected_fn = None
        self._ext_source_selector = None
        self._show_dependencies_fn = None
        self._show_properties_fn = None
        self.clear_selection = None
        self.searches = None
        self.tree_view = None
        for tab in self.__menus:
            if hasattr(tab, "close_menu"):
                tab.close_menu()
            tab.destroy()
        self.__menus = []

    def get_model(self):
        return self._model
