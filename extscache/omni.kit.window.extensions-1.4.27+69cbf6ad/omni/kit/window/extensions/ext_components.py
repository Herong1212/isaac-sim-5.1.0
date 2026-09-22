# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides UI components and utility functions for managing and interacting with extensions in the Omni Kit window, including widgets for toggling extension states, searching, and selecting extension sources."""

import asyncio
import sys
from typing import Callable, Dict, List

import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.kit.widget.searchfield import SearchField

from .common import ExtensionCommonInfo, ExtSource, build_doc_urls, pull_extension_async_by_name, toggle_extension
from .styles import get_style
from .utils import get_setting, open_url, run_process


class ExtensionToggle:
    """A widget to toggle the state of an extension.

    This UI component is part of the extension management system, allowing users to install, enable, or disable extensions. It can also optionally display a label to indicate the current state of the extension.

    Args:
        item (:obj:`ExtensionCommonInfo`): The extension item to be managed.
        with_label (bool): Whether to display the label next to the toggle.
        show_install_button (bool): Whether to show the install button for non-local extensions.
        refresh_cb (Callable): Optional callback to invoke when the extension state changes."""

    def __init__(self, item: ExtensionCommonInfo, with_label=False, show_install_button=True, refresh_cb=None):
        """Initializes the extension toggle widget with various UI elements based on the extension's state and properties."""
        with ui.HStack(width=0, style=get_style(self)):
            if item.is_app:

                def on_click(is_local=item.is_local, ext_id=item.id):
                    manager = omni.kit.app.get_app().get_extension_manager()
                    if not is_local:
                        manager.pull_extension(ext_id)

                    args = [sys.argv[0]]
                    ext_info = manager.get_extension_dict(ext_id)
                    if ext_info.get("isKitFile", False):
                        args.append(ext_info["path"])
                    else:
                        args.extend(["--enable", ext_id])

                    # Pass all exts folders
                    for folder in get_setting("/app/exts/folders", default=[]):
                        args.extend(["--ext-folder", folder])

                    run_process(args)

                with ui.VStack():
                    ui.Spacer()
                    ui.Button("LAUNCH", name="LaunchButton", width=60, height=20, clicked_fn=on_click)
                    ui.Spacer()
            elif not item.is_local:
                if not show_install_button:
                    return

                with ui.VStack():
                    ui.Spacer()

                    if item.is_pulled:
                        ui.Button("INSTALLING...", name="DownloadingButton", width=60, height=20)
                    else:

                        def on_click(item=item):
                            asyncio.ensure_future(pull_extension_async_by_name(item.fullname))

                        ui.Button("INSTALL", name="InstallButton", width=60, height=20, clicked_fn=on_click)

                    ui.Spacer()

            else:
                if item.failed:
                    with ui.VStack():
                        ui.Spacer()
                        # OM-90861: Add tooltip for extension depdency solve failure
                        tooltip = "Failed to solve extension dependency."
                        if item.solver_error:
                            tooltip += f"\nError: {item.solver_error}"
                        ui.Image(name="Failed", width=26, height=26, tooltip=tooltip)
                        ui.Spacer()
                with ui.VStack():
                    ui.Spacer()
                    name = "clickable"
                    tb = ui.ToolButton(image_width=39, image_height=18, height=0, name=name)
                    tb.model.as_bool = item.enabled
                    tb.identifier = "toggle_button"

                    def toggle(model, ext_id=item.id, fullname=item.fullname):
                        enable = model.get_value_as_bool()
                        # If we about to enable, toggle other versions if enabled
                        if enable:
                            manager = omni.kit.app.get_app().get_extension_manager()
                            extensions = manager.fetch_extension_versions(fullname)
                            for e in extensions:
                                if e["enabled"] and e["id"] != ext_id:
                                    toggle_extension(e["id"], False)

                        if not toggle_extension(ext_id, enable=enable):
                            model.as_bool = not enable

                    if item.is_toggle_blocked:
                        tb.name = "nonclickable"

                        # TODO(anov): how to make ToolButton disabled?
                        def block_change(model, enabled=item.enabled):
                            model.as_bool = enabled

                        tb.model.add_value_changed_fn(block_change)
                    else:
                        tb.model.add_value_changed_fn(toggle)
                    ui.Spacer()

                if with_label:
                    ui.Spacer(width=8)
                    if item.enabled:
                        ui.Label("ENABLED", name="EnabledLabel")
                    else:
                        ui.Label("DISABLED", name="DisabledLabel")


class SimpleCheckBox:
    """A simple check box UI element with an optional text label.

    This class creates a checkbox with a label, and allows for a callback function to
    be executed when the checkbox state changes. It can be enabled or disabled and
    can have a bound data model.

    Args:
        checked (bool): Initial checked state of the checkbox.
        on_checked_fn (Callable): Function to call when checkbox state changes.
        text (str, optional): Text to display next to the checkbox. Defaults to None.
        model (:obj:`ui.SimpleBoolModel`, optional): Data model to bind to the checkbox. Defaults to None.
        enabled (bool, optional): Specifies if the checkbox is interactable. Defaults to True."""

    def __init__(self, checked: bool, on_checked_fn: Callable, text: str = None, model=None, enabled=True):
        """Initializes a simple checkbox with a label and a callback function."""
        with ui.HStack(width=0, style=get_style(self)):
            with ui.VStack(width=0):
                ui.Spacer()
                if enabled:
                    tb = ui.ToolButton(image_width=39, image_height=18, height=0, model=model)
                    tb.model.as_bool = checked
                    tb.model.add_value_changed_fn(lambda model: on_checked_fn(model.get_value_as_bool()))
                else:
                    name = "disabled_checked" if checked else "disabled_unchecked"
                    ui.Image(width=39, height=18, name=name)
                ui.Spacer()

            if text:
                ui.Label(text)


class SearchWidget(SearchField):
    """String field with a label overlay to type search string into.

    Args:
        on_search_fn (Callable[[str], None]): Function called with the search string."""

    def __init__(self, on_search_fn: Callable[[List[str]], None]):
        """Initializes the search widget and sets up the search field with callback."""
        self.clear_filters()
        super().__init__(on_search_fn=on_search_fn, subscribe_edit_changed=True, show_tokens=True, separator=None)

    def get_filters(self):
        """Gets the current set of filters applied to the search.

        Returns:
            list: The list of current filters."""
        return self._filters

    def toggle_filter(self, filter_to_toggle):
        """Toggles a filter on or off in the current search filters.

        Args:
            filter_to_toggle (str): The filter to toggle."""
        if filter_to_toggle in self._filters:
            self._filters.remove(filter_to_toggle)
        else:
            self._filters.append(filter_to_toggle)

    def clear_filters(self):
        """Clears all filters currently applied to the search."""
        self._filters = []


class ExtSourceSelector:
    """A class for selecting an extension source.

    Handles UI logic for selecting an extension source from a list of options.

    Args:
        on_selected_fn (Callable): Callback function invoked when a source is selected."""

    def __init__(self, on_selected_fn):
        """Initializes the ExtSourceSelector with a callback for selection events."""

        self._on_selected_fn = None
        self._buttons = {}

        with ui.HStack(height=20):
            for index, source in enumerate(ExtSource):
                ui.Spacer()

                tab_btn = ui.Button(
                    source.get_ui_name(),
                    width=0,
                    style_type_name_override="ExtensionDescription.Tab",
                    clicked_fn=lambda s=source: self.set_tab(s),
                )
                self._buttons[source] = tab_btn
                if index < len(ExtSource) - 1:
                    ui.Spacer()
                    ui.Line(
                        style_type_name_override="ExtensionDescription.TabLine",
                        alignment=ui.Alignment.H_CENTER,
                        height=20,
                        width=40,
                    )

            ui.Spacer()

        self.set_tab(ExtSource.NVIDIA)
        self._on_selected_fn = on_selected_fn

    def set_badge_number(self, source, number):
        """Sets the badge number for a given extension source.

        Args:
            source (:obj:`ExtSource`): The source for which to set the badge number.
            number (int): The number to display on the badge."""
        self._buttons[source].text = source.get_ui_name() + f" ({number})"

    def set_tab(self, source):
        """Activates the tab corresponding to the given source.

        Args:
            source (:obj:`ExtSource`): The source for which to activate the tab."""
        for b in self._buttons.values():
            b.selected = False

        self._buttons[source].selected = True

        if self._on_selected_fn:
            self._on_selected_fn(source)


def add_icon_button(name, on_click):
    """Creates a button with an icon.

    Args:
        name (str): The name of the button.
        on_click (Callable): The function to call when the button is clicked."""
    with ui.VStack(width=0):
        ui.Spacer()

        b = ui.Button(name=name, style_type_name_override="IconButton", width=23, height=18, clicked_fn=on_click)
        ui.Spacer()

        return b


def add_doc_link_button(ext_item: ExtensionCommonInfo, package_dict: Dict, docs_dict: Dict):
    """Adds a documentation link button to the UI if valid URLs are found.

    Args:
        ext_item (:obj:`ExtensionCommonInfo`): The extension item to get documentation URLs for.
        package_dict (Dict): Dictionary containing package information.
        docs_dict (Dict): Dictionary containing documentation information."""
    # Create a button, but hide.
    button = None
    with ui.VStack(width=0):
        ui.Spacer()
        button = ui.Button(
            name="OpenDoc",
            style_type_name_override="IconButton",
            width=23,
            height=18,
            style={"Label": {"color": 0xFF444444}},
        )
        ui.Spacer()

    button.visible = False

    def check_url_sync(url):
        import urllib

        try:
            return urllib.request.urlopen(url).getcode() == 200
        except urllib.error.HTTPError:
            return False

    async def check_urls(doc_urls):
        for doc_url in doc_urls:
            # run sync code on other thread not to block
            if await asyncio.get_event_loop().run_in_executor(None, check_url_sync, doc_url):
                button.visible = True

                def on_click(url=doc_url):
                    if carb.settings.get_settings().get("/persistent/exts/omni.kit.window.extensions/openInVSCode"):
                        open_url(url)

                button.set_clicked_fn(on_click)
                button.set_tooltip_fn(lambda url=doc_url: ui.Label(url))
                break

    # Async check for URLs and if valid show the button
    doc_urls = build_doc_urls(ext_item)
    if doc_urls:
        asyncio.ensure_future(check_urls(doc_urls))
