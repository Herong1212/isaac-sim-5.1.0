# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# pylint: disable=protected-access, access-member-before-definition

"""This module provides a widget for displaying detailed information about extensions in the Extension Manager UI, including overview, changelog, dependencies, and available packages."""

__all__ = ["PageBase", "OverviewPage", "ChangelogPage", "DependenciesPage", "PackagesPage", "ExtInfoWidget"]

import asyncio
import contextlib
import os
import time
import weakref
from datetime import datetime, timezone
from typing import Callable

import omni.kit.app
import omni.kit.clipboard
import omni.kit.commands
import omni.ui as ui
from carb.eventdispatcher import get_eventdispatcher

from . import ext_controller
from .common import (
    ExtensionCommonInfo,
    PageBase,
    build_ext_info,
    check_can_be_toggled,
    check_can_be_toggled_with_popup,
    get_categories,
    get_icons_path,
    get_options,
    pull_extension_async,
    toggle_extension,
)
from .ext_components import ExtensionToggle, SimpleCheckBox, add_doc_link_button
from .ext_data_fetcher import get_ext_data_fetcher
from .ext_export_import import export_ext
from .exts_dependency_window import ExtsDependencyWidget
from .exts_list_widget import ExtensionCardWidget
from .markdown_renderer import MarkdownText
from .styles import CATEGORY_ICON_SIZE, EXT_ICON_SIZE_LARGE
from .utils import clip_text, is_vscode_installed, open_in_vscode_if_enabled, version_to_str

ICON_ZONE_WIDTH = 120
CATEGORY_ZONE_WIDTH = 120


def get_ext_text_content(key: str, ext_info, ext_item: ExtensionCommonInfo):
    """Get extension readme/changelog from either local dict or registry extra data

    Args:
        key (str): The key to access the content ('readme' or 'changelog').
        ext_info: The dictionary containing extension info.
        ext_item (:obj:`ExtensionCommonInfo`): The common extension item information.

    Returns:
        The extension's readme or changelog content as a string."""

    content_str = ""
    # Get the data
    if ext_item.is_local:
        content_str = ext_info.get("package", {}).get(key, "")
    else:
        fetcher = get_ext_data_fetcher()
        ext_data = fetcher.get_ext_data(ext_item.package_id)
        if ext_data:
            content_str = ext_data.get("package", {}).get(key, "")

    # Figure out if it is a path to a file or actual data
    if content_str and "\n" not in content_str:
        ext_path = ext_info.get("path", "")
        # If it is a path -> load file content
        readme_file = os.path.join(ext_path, content_str)
        if os.path.exists(readme_file):
            with open(readme_file, "r", encoding="utf-8") as f:
                content_str = f.read()

    if not content_str:
        content_str = "```{csv-table}\n**Extension**: {{ extension_version }},**Documentation Generated**: {sub-ref}`today`\n```\n"

    return content_str


def select_best_version(extensions, summary_default_version):
    selected_ext = None
    for e in extensions:
        if e["version"][:4] == summary_default_version[:4]:
            selected_ext = e

    # If selected version is not available, select latest. That can happen if latest published is incompatible with
    # current target. In summaries it will show later version than the one you can select by default.
    if not selected_ext:
        selected_ext = extensions[0]

    # If selected version can't be toggled, try to find one that can be toggled to show instead
    # In some cases solver takes too long and there could be hundres versions, so we limit the total time.
    time_limit = 2.0  # seconds
    if not check_can_be_toggled(selected_ext["id"]):
        # try other versions:
        t = time.time()
        for e in extensions:
            if check_can_be_toggled(e["id"]):
                selected_ext = e
                break
            if time.time() - t > time_limit:
                break

    return selected_ext["version"]


def build_package_info(ext_info, ext_item):
    """Generates a dictionary with detailed package information.

    Args:
        ext_info (dict): Extension information to extract package info from.
        ext_item (:obj:`ExtensionCommonInfo`): The common extension item."""
    if ext_info is None:
        return

    package_dict = ext_info.get("package", {})
    publish_dict = package_dict.get("publish", {})

    def add_info(name, value):
        if not value:
            return
        if isinstance(value, (tuple, list)):
            value = ", ".join(value)
        if isinstance(value, dict):
            value = str(value)

        with ui.HStack():
            ui.Label(name, width=100, style_type_name_override="ExtensionDescription.Content")

            if value.startswith("http://") or value.startswith("https://"):

                def open_link():
                    import webbrowser

                    webbrowser.open(value)

                ui.Label(
                    value,
                    style_type_name_override="ExtensionDescription.ContentLink",
                    mouse_pressed_fn=lambda x, y, b, a: b == 0 and open_link(),
                )
            else:
                ui.Label(value, style_type_name_override="ExtensionDescription.ContentValue")

    def add_package_info(name, key):
        add_info(name, package_dict.get(key, None))

    # Package info
    if ext_item.is_deprecated:
        ui.Label("DEPRECATED", style_type_name_override="ExtensionDescription.DeprecatedTitle")
        ui.Label(
            ext_item.deprecation_msg, style_type_name_override="ExtensionDescription.DeprecatedBody", word_wrap=True
        )

    add_package_info("Authors", "authors")
    add_package_info("Keywords", "keywords")
    add_info("Repo Name", publish_dict.get("repoName", None))
    add_package_info("Repo Url", "repository")
    add_package_info("Github Release", "githubRelease")

    # Publish info
    ts = publish_dict.get("date", None)
    if not ts:
        ts = package_dict.get("publishDate", None)  # backward compatibility for deprecated key
    if ts:
        add_info("Publish Date", str(datetime.fromtimestamp(ts, tz=timezone.utc).astimezone()))
    add_info("Build Number", publish_dict.get("buildNumber", None))
    add_info("Kit Version", publish_dict.get("kitVersion", None))
    add_package_info("Target", "target")

    # Test info
    test = ext_info.get("test", None)
    if isinstance(test, (list, tuple)):
        for t in test:
            add_info("Test Waiver", t.get("waiver", None))


class OverviewPage(PageBase):
    """
    Build a class with same interface and add it to ExtInfoWidget.pages
    below to have it show up as a tab
    """

    def __init__(self):
        super().__init__()
        self._preview_placeholder_path = f"{get_icons_path()}/data/preview-placeholder.png"

    def build_tab(self, ext_info, ext_item: ExtensionCommonInfo):
        """Builds the content for the overview tab.

        Args:
            ext_info (dict): The dictionary containing extension information.
            ext_item (:obj:`ExtensionCommonInfo`): The common info about the extension."""

        readme_str = get_ext_text_content("readme", ext_info, ext_item)

        with ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        ):
            with ui.ZStack():
                ui.Rectangle(style_type_name_override="ExtensionDescription.ContentBackground")
                with ui.HStack():
                    ui.Spacer(width=10)
                    with ui.VStack(height=0):
                        ui.Spacer(height=10)

                        # Readme
                        MarkdownText(readme_str, ext_info, ext_item)

                        # Preview ?
                        if ext_item.preview_image_path:
                            ui.Image(
                                ext_item.preview_image_path,
                                alignment=ui.Alignment.H_CENTER,
                                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                                width=512,
                                height=512,
                            )
                        else:
                            ui.Image(
                                self._preview_placeholder_path,
                                alignment=ui.Alignment.H_CENTER,
                                fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                                width=448,
                                height=448,
                            )
                        ui.Spacer(height=15)

    def destroy(self):
        """Cleans up resources and UI elements associated with the overview tab."""

    def sort_index(self):
        return "1stPage"

    @staticmethod
    def get_tab_name():
        """Get the name used for the tab name in the UI

        Returns:
            str: The name of the tab."""
        return "OVERVIEW"


class ChangelogPage(PageBase):
    """A tab page within the Extension Manager UI that displays the changelog of an extension.

    The ChangelogPage allows users to view the list of changes, updates, bug fixes, and other modifications made to an extension over time. It presents this information in a formatted text area, often leveraging markdown for better readability.

    The changelog content is dynamically retrieved based on the extension's information, either from a local dictionary or from the registry's extra data. If no changelog is present, a default message indicating the absence of a changelog is shown to the user.

    This class inherits from the PageBase interface, adhering to its contract for building and destroying tab content within the Extension Manager UI.
    """

    def build_tab(self, ext_info, ext_item: ExtensionCommonInfo):
        """Builds the changelog tab with extension information.

        Args:
            ext_info (dict): The extension info dictionary containing extension details.
            ext_item (:obj:`ExtensionCommonInfo`): The common info object for the extension."""
        changelog_str = get_ext_text_content("changelog", ext_info, ext_item)
        if not changelog_str:
            changelog_str = "[no changelog]"

        # word_wrap is important here because changelog can
        # be Markdown, and if word_wrap is defalut, Label
        # ignores everything after double hash. word_wrap fixes it.
        with ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        ):
            with ui.ZStack():
                ui.Rectangle(style_type_name_override="ExtensionDescription.ContentBackground")
                with ui.HStack():
                    ui.Spacer(width=10)
                    with ui.VStack(height=0):
                        ui.Spacer(height=10)
                        MarkdownText(changelog_str, ext_info, ext_item)

    def destroy(self):
        """Destroys the changelog tab and performs any necessary cleanup."""

    def sort_index(self):
        return "2ndPage"

    @staticmethod
    def get_tab_name():
        """Retrieves the name to be used for the changelog tab in the UI.

        Returns:
            str: The name of the tab."""
        return "CHANGELOG"


class DependenciesPage(PageBase):
    """A tab page within the Extension Manager UI that displays dependencies information for an extension.

    This page shows the dependencies required by the selected extension, including their versions and whether they are optional. It lists the extensions that would be enabled as a result of enabling the selected extension, along with any errors that would prevent enabling.
    """

    def __init__(self):
        """Initialize the DependenciesPage."""
        self._ext_dependencies = None

    def build_tab(self, ext_info, ext_item: ExtensionCommonInfo):
        """Builds the dependencies tab for the given extension.

        Args:
            ext_info (dict): Information about the extension.
            ext_item (:obj:`ExtensionCommonInfo`): The extension item to build dependencies for."""
        # Dependencies only available if extension is enabled:
        if ext_info.get("state", {}).get("enabled", False):
            self._ext_dependencies = ExtsDependencyWidget(ext_info.get("package").get("id"))
        else:
            with ui.VStack(height=0):
                # Enable result
                if not ext_item.solver_result:
                    ui.Label(
                        "Enabling this extension will fail with the following error:",
                        style_type_name_override="ExtensionDescription.Header",
                    )
                    ui.Label(ext_item.solver_error, style_type_name_override="ExtensionDescription.ContentError")
                else:
                    ui.Label(
                        "Enabling this extension will enable the following extensions in order:",
                        style_type_name_override="ExtensionDescription.Header",
                    )
                    ui.Label(
                        "".join(f"\n - {ext['id']}" for ext in ext_item.solver_exts),
                        style_type_name_override="ExtensionDescription.Content",
                    )
                ui.Spacer(height=30)

                # Dependencies
                ui.Label("Dependencies (in config):", style_type_name_override="ExtensionDescription.Header")
                ui.Spacer(height=4)
                for k, v in ext_info.get("dependencies", {}).items():
                    label_text = f"{k}"
                    tag = v.get("tag", None)
                    if tag:
                        label_text += f"-{tag}"

                    version = v.get("version", "*.*.*")
                    if version:
                        label_text += f"  |  v{version}"

                    optional = v.get("optional", False)
                    if optional:
                        label_text += "(optional)"
                    ui.Label(label_text, style_type_name_override="ExtensionDescription.Content")

    def destroy(self):
        """Cleans up any resources or subscriptions."""

    def sort_index(self):
        return "3rdPage"

    @staticmethod
    def get_tab_name():
        """Returns the name of the tab."""
        return "DEPENDENCIES"


class PackagesPage(PageBase):
    """A UI component representing a tabbed page in the Extension Manager that displays a list of all available packages for a specific version of an extension.

    This class is responsible for querying the extension manager for available packages related to a particular extension version and presenting them in a structured format within the Extension Manager UI. It allows users to view detailed information about each package, including its dependencies and other metadata.

    The build_tab method is used to construct the user interface elements and populate them with the retrieved package data. The destroy method ensures proper cleanup of resources when the PackagesPage is no longer needed.
    """

    def build_tab(self, ext_info, ext_item: ExtensionCommonInfo):
        """Builds the tab content for the given extension.

        Args:
            ext_info (dict): The dictionary containing extension metadata.
            ext_item (:obj:`ExtensionCommonInfo`): The common info object for the extension."""
        manager = omni.kit.app.get_app().get_extension_manager()
        package_info = ext_info.get("package")
        packages = manager.fetch_extension_packages(package_info.get("id"))

        with ui.VStack(height=0):
            ui.Label(
                "All available packages for version {} :".format(package_info["version"]),
                style_type_name_override="ExtensionDescription.Title",
            )
            for p in packages:
                package_id = p["package_id"]
                with ui.CollapsableFrame(package_id, collapsed=True):
                    with ui.HStack():
                        ui.Spacer(width=20)
                        with ui.VStack():
                            build_package_info(manager.get_registry_extension_dict(package_id), ext_item)

    def destroy(self):
        """Destroys the tab and cleans up resources."""

    def sort_index(self):
        return "4thPage"

    @staticmethod
    def get_tab_name():
        """Retrieves the name of the tab.

        Returns:
            str: The name of the tab."""
        return "PACKAGES"


class DeveloperPage(PageBase):
    """
    Build a class with same interface and add it to ExtInfoWidget.pages
    below to have it show up as a tab
    """

    def __init__(self):
        super().__init__()
        self._preview_placeholder_path = f"{get_icons_path()}/data/preview-placeholder.png"

    def build_tab(self, ext_info, ext_item: ExtensionCommonInfo):
        """Builds the content for the developer tab.

        Args:
            ext_info (dict): The dictionary containing extension information.
            ext_item (:obj:`ExtensionCommonInfo`): The common info about the extension."""

        with ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        ):
            with ui.ZStack():
                ui.Rectangle(style_type_name_override="ExtensionDescription.ContentBackground")
                with ui.HStack():
                    ui.Spacer(width=10)
                    with ui.VStack(height=0):
                        ui.Spacer(height=10)

                        # All the meta info about the package (version, date, authors)
                        build_package_info(ext_info, ext_item)

    def destroy(self):
        """Cleans up resources and UI elements associated with the overview tab."""

    def sort_index(self):
        return "5thPage"

    @staticmethod
    def get_tab_name():
        """Retrieves the name to be used for the changelog tab in the UI.

        Returns:
            str: The name of the tab."""
        return "DEVELOPER"


class ExtInfoWidget:
    """A widget for displaying detailed information about extensions in the Extension Manager UI.

    This widget provides a comprehensive view of an extension's overview, changelog, dependencies, and available packages. It allows users to select different versions of the extension, install or update it, and view additional metadata and documentation. The widget also offers functionality to copy extension IDs, open extension folders, and export extensions.

    The widget is designed to be dynamically updated based on the selected extension and provides tabs for navigating between different sections of extension information. It is also responsible for handling extension-related actions such as installation, updating, enabling autoload, and other management tasks.
    """

    pages = [OverviewPage, ChangelogPage, DependenciesPage, PackagesPage, DeveloperPage]
    """list[PageBase] - List of pages added to the ExtInfoWidget as tabs"""
    current_page = 0
    """int - Index of the currently displayed page or tab"""

    def __init__(self):
        """Initializes the ExtInfoWidget instance with default values and subscriptions."""
        # Widgets for tabs
        self.__tabs = []
        self.__pages = []

        # Put into frame to enable rebuilding of UI
        self._frame = ui.Frame()

        self._ext_manager = omni.kit.app.get_app().get_extension_manager()
        self._ext_change_sub = [
            get_eventdispatcher().observe_event(
                observer_name="ext_info_widget",
                on_event=lambda *_: self._refresh_once_next_frame(),
                event_name=omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED,
            ),
            get_eventdispatcher().observe_event(
                observer_name="ext_info_widget",
                on_event=lambda *_: self._refresh_once_next_frame(),
                event_name=omni.ext.GLOBAL_EVENT_FOLDER_CHANGED,
            ),
        ]
        self._ext_dependencies = None
        self._version_menu = None

        self._selected_version = None
        self._selected_package_id = None

        # Refresh when new ext data fetched
        fetcher = get_ext_data_fetcher()

        def on_data_fetched(package_id):
            if self._selected_package_id == package_id:
                self._refresh_once_next_frame()

        fetcher.on_data_fetched_fn = on_data_fetched

        self.select_ext(None)

        self.page_tabs = []
        self.update_tabs()

        self.set_show_dependencies_fn(None)

    def update_tabs(self):
        """Updates the tabs in the ExtInfoWidget based on the current pages."""
        self.page_tabs = []
        for page in self.pages:
            self.page_tabs.append(page())

    def set_visible(self, visible):
        """Sets the visibility of the ExtInfoWidget.

        Args:
            visible (bool): Whether the widget should be visible."""
        self._frame.visible = visible

    def select_ext(self, ext_summary):
        """Select extension to display info about. Can be None

        Args:
            ext_summary (:obj:`ExtensionCommonInfo`): The summary of the extension to display."""
        self._ext_summary = ext_summary
        self._selected_version = None
        self._selected_package_id = None
        self._refresh_once_next_frame()

    def _refresh(self):

        # Fetch all extensions for currently selected extension summary
        extensions = []
        if self._ext_summary is not None:
            extensions = self._ext_manager.fetch_extension_versions(self._ext_summary.fullname)
            if not extensions:
                # This happens when extension has no compatible packages with the current target (platform, kit version)
                # Extension still shows up on the summary list, but when clicking we have nothing to show. Pick at least
                # 1 incompatible package here to show something. Ideally, we should improve the UI to support that case.
                # E.g. INSTALL button will not work right now and there is no indication that it is not compatible.
                extensions = self._ext_manager.fetch_extension_packages(self._ext_summary.fullname)[:1]

        def _draw_empty_page():
            with self._frame:
                ui.Label("Select an extension")

        if len(extensions) == 0:
            _draw_empty_page()
            return

        # If user hasn't yet changed the version to display summary advices which should be shown by default:
        if self._selected_version is None:
            self._selected_version = select_best_version(extensions, self._ext_summary.default_ext["version"])

        # Now actual extension is selected (including version). Get all the info for it
        selected_index = next(
            (i for i, v in enumerate(extensions) if v["version"][:4] == self._selected_version[:4]), None
        )

        if selected_index is None:
            _draw_empty_page()
            return

        selected_ext = extensions[selected_index]
        is_version_latest = selected_index == 0
        ext_id = selected_ext["id"]
        package_id = selected_ext["package_id"]
        self._selected_package_id = package_id

        # If this extension is enabled or other version of this extension is enabled:
        any_version_enabled = any(ext["enabled"] for ext in extensions)

        ext_item, ext_info = build_ext_info(ext_id, package_id)  # -> Tuple[ExtensionCommonInfo, dict]:

        # Get ext info either from local or remote index
        if not ext_info:
            _draw_empty_page()
            return

        # Gather more info by solving dependencies. When other version of this extension is already enabled solving is
        # known to fail because of conflict. It will always display a red icon then.
        # When we actually toggle it we will first turn off that version. So for that case do not solve extensions.
        # An alternative solution might be to manually build a list of all enabled extensions, but exclude current one.
        if not any_version_enabled:
            ext_item.solve_extensions()

        if not ext_item.is_local:
            fetcher = get_ext_data_fetcher()
            fetcher.fetch(ext_item)

        ext_path = ext_info.get("path", "")

        package_dict = ext_info.get("package", {})
        docs_dict = ext_info.get("documentation", {})
        if ext_item.is_local:
            # For local extensions add version to ext_id to make it more concrete (for later enabling etc.)
            name = package_dict.get("name")
            version = package_dict.get("version", None)
            ext_id = name + "-" + version if version else name
        name = package_dict.get("name", "")
        enabled = ext_item.enabled

        category = get_categories().get(ext_item.category)

        ################################################################################################################
        # Build version selector menu

        def select_version(version):
            self._selected_version = version
            self._refresh_once_next_frame()

        self._version_menu = ui.Menu("Version")
        with self._version_menu:

            ui.MenuItem("Version(s)", enabled=False)
            ui.Separator()

            for i, e in enumerate(extensions):
                version = e["version"]
                version_str = version_to_str(version[:4])
                color = 0xFF76B900 if selected_index == i else 0xFFC0C0C0
                ui.MenuItem(
                    version_str,
                    checked=selected_index == i,
                    checkable=True,
                    style={"color": color, "margin": 0},
                    triggered_fn=lambda v=version: select_version(v),
                )

            # Publish / Unpublish buttons
            if get_options().publishing:
                ui.Separator()
                ui.MenuItem("Publishing", enabled=False)
                ui.Separator()
                if ext_item.is_local:
                    ui.MenuItem(
                        "PUBLISH", triggered_fn=lambda ext_id=ext_id: self._ext_manager.publish_extension(ext_id)
                    )
                else:
                    ui.MenuItem(
                        "UNPUBLISH", triggered_fn=lambda ext_id=ext_id: self._ext_manager.unpublish_extension(ext_id)
                    )

            # Uninstall
            can_be_uninstalled = not ext_item.enabled and ext_item.location_tag == "INSTALLED"
            if can_be_uninstalled:
                ui.Separator()
                ui.MenuItem(
                    "UNINSTALL", triggered_fn=lambda ext_id=ext_id: self._ext_manager.uninstall_extension(ext_id)
                )

        ################################################################################################################
        ################################################################################################################

        def draw_icon_block():
            # Icon
            with ui.HStack(width=ICON_ZONE_WIDTH):
                ui.Spacer()
                with ui.VStack(width=EXT_ICON_SIZE_LARGE[0]):
                    ui.Spacer()
                    ui.Image(ext_item.icon_path, height=EXT_ICON_SIZE_LARGE[1], style={"color": 0xFFFFFFFF})
                    ui.Spacer()
                ui.Spacer()

        ################################################################################################################

        def draw_top_row_block():
            with ui.HStack(identifier="top_row"):

                # Big button
                if not ext_item.is_local:
                    if ext_info.get("state", {}).get("isPulled", False):
                        ui.Button(
                            "INSTALLING...",
                            style_type_name_override="ExtensionDescription.DownloadingButton",
                            width=100,
                            height=30,
                        )
                    else:

                        def on_click(item=ext_item):
                            asyncio.ensure_future(pull_extension_async(item, self._refresh_once_next_frame))

                        ui.Button(
                            "INSTALL",
                            style_type_name_override="ExtensionDescription.InstallButton",
                            width=100,
                            height=30,
                            clicked_fn=on_click,
                        )
                else:
                    latest_ext = extensions[0]
                    can_update = not is_version_latest and check_can_be_toggled(latest_ext["id"])
                    is_autoload_enabled = ext_controller.is_autoload_enabled(ext_item.id)
                    if not ext_item.enabled and ext_item.is_toggle_blocked and is_autoload_enabled:

                        def on_click():
                            omni.kit.app.get_app().restart()

                        ui.Button(
                            "RESTART APP",
                            style_type_name_override="ExtensionDescription.RestartButton",
                            clicked_fn=on_click,
                            width=100,
                            height=30,
                        )
                    elif can_update:

                        def on_click(ext_id=ext_id, switch_off_on=(enabled and not ext_item.is_toggle_blocked)):
                            latest_ext_id = latest_ext["id"]
                            latest_ext_version = latest_ext["version"]

                            # If autoload for that one is enabled, move it to latest:
                            if ext_controller.is_autoload_enabled(ext_id):
                                ext_controller.toggle_autoload(ext_id, False)
                                if check_can_be_toggled_with_popup(latest_ext_id, for_autoload=True):
                                    ext_controller.toggle_autoload(latest_ext_id, True)

                            # If extension is enabled, switch off to latest:
                            if switch_off_on:
                                toggle_extension(ext_id, False)
                                toggle_extension(latest_ext_id, True)

                            # Finally switch UI to show newest version
                            select_version(latest_ext_version)

                        ui.Button(
                            "UPDATE",
                            style_type_name_override="ExtensionDescription.UpdateButton",
                            clicked_fn=on_click,
                            width=100,
                            height=30,
                            identifier="update_button",
                        )
                    else:
                        ui.Button(
                            "UP TO DATE",
                            style_type_name_override="ExtensionDescription.UpToDateButton",
                            width=100,
                            height=30,
                        )

                # Version selector
                with ui.VStack(width=0):
                    ui.Spacer()
                    ui.Button(
                        name="options",
                        width=40,
                        height=22,
                        clicked_fn=self._version_menu.show,
                        identifier="version_selector",
                    )
                    ui.Spacer()

                # Toggle
                ui.Spacer(width=15)
                ExtensionToggle(ext_item, with_label=True, show_install_button=False)

                # Autoload toggle
                with ui.HStack():
                    ui.Spacer(width=20)

                    def toggle_autoload(value, ext_id=ext_id):
                        if check_can_be_toggled_with_popup(ext_id, for_autoload=True):
                            ext_controller.toggle_autoload(ext_id, value)
                        self._refresh_once_next_frame()

                    SimpleCheckBox(
                        ext_controller.is_autoload_enabled(ext_id), toggle_autoload, "AUTOLOAD", enabled=True
                    )
                ui.Spacer(width=20)

                def add_icon_button(name, on_click, tooltip=None):
                    with ui.VStack(width=0):
                        ui.Spacer()

                        # cannot get style tooltip override to work, so force it here
                        b = ui.Button(
                            name=name,
                            style_type_name_override="IconButton",
                            width=23,
                            height=18,
                            clicked_fn=on_click,
                            style={"Label": {"color": 0xFF444444}},
                        )
                        if tooltip:
                            b.set_tooltip_fn(lambda *_: ui.Label(tooltip))

                        ui.Spacer()

                        return b

                def add_open_button(url, name, prefer_vscode=False, tooltip=None):
                    def on_click(url=url):
                        open_in_vscode_if_enabled(url, prefer_vscode)

                    b = add_icon_button(name, on_click)
                    if not tooltip:
                        tooltip = url
                    b.set_tooltip_fn(lambda *_: ui.Label(tooltip))

                # Doc button
                add_doc_link_button(ext_item, package_dict, docs_dict)
                ui.Spacer(width=8)

                if ext_item.is_local:
                    # Extension "open folder" button
                    ext_folder = os.path.dirname(ext_path) if os.path.isfile(ext_path) else ext_path
                    add_open_button(ext_folder, name="OpenFolder")

                    ui.Spacer(width=8)

                    # Extension "open folder" button
                    if is_vscode_installed():
                        add_open_button(ext_folder, name="OpenInVSCode", prefer_vscode=True, tooltip="Open in VSCode")
                        ui.Spacer(width=8)

                    # Extension "open config" button
                    add_open_button(ext_info.get("configPath", ""), name="OpenConfig", prefer_vscode=True)

                    ui.Spacer(width=8)

                    # Extension export button
                    def on_export(ext_id=ext_id):
                        export_ext(ext_id)

                    add_icon_button("Export", on_export, tooltip=f"Export {ext_info['package']['packageId']}")

        ################################################################################################################

        def draw_extension_name_block():
            with ui.HStack():
                # Extension id
                ui.Label(
                    ext_item.title,
                    height=0,
                    width=0,
                    style_type_name_override="ExtensionDescription.Label",
                    tooltip=ext_id,
                )
                ui.Spacer()

        ################################################################################################################

        def draw_extension_id_block():
            def copy_ext_id():
                omni.kit.clipboard.copy(f'"{ext_item.fullname}" = {{ version = "{ext_item.version}" }}')

            with ui.HStack(spacing=4):
                # Extension id
                ui.Label(
                    ext_item.fullname,
                    height=0,
                    width=0,
                    style_type_name_override="ExtensionDescription.Label",
                )

                with ui.VStack(width=0):
                    ui.Spacer()
                    ui.Button(
                        name="Copy",
                        style_type_name_override="IconButton",
                        width=23,
                        height=18,
                        clicked_fn=copy_ext_id,
                        style={"Label": {"color": 0xFF444444}},
                        tooltip="Copy extension ID.",
                        identifier="copy_ext_id",
                    )
                    ui.Spacer()
                ui.Spacer()

        ################################################################################################################

        def draw_extension_description_block():
            with ui.HStack():

                ui.Label(
                    clip_text(ext_item.description),
                    height=0,
                    width=50,
                    style_type_name_override="ExtensionDescription.Label",
                )

        ################################################################################################################

        def draw_category_block():
            # Category Info and Icon
            with ui.HStack(width=CATEGORY_ZONE_WIDTH):
                ui.Spacer()
                with ui.VStack(width=CATEGORY_ICON_SIZE[0]):
                    ui.Spacer()
                    ui.Image(category["image"], width=CATEGORY_ICON_SIZE[0], height=CATEGORY_ICON_SIZE[1])
                    ui.Spacer(height=10)
                    ui.Label(category["name"], alignment=ui.Alignment.CENTER)
                    ui.Spacer()
                ui.Spacer()

        def draw_ext_source_block():
            ExtensionCardWidget.build_ext_card_footer(ext_item, full_width=True)

        def draw_content_block():
            def get_page_index(page):
                if hasattr(page, "sort_index"):
                    return page.sort_index()
                return f"999LastPage.{page.get_tab_name()}"

            page_tabs = sorted(self.page_tabs, key=get_page_index)

            def set_page(index):
                for i in self.__tabs:
                    i.selected = False
                for i in self.__pages:
                    i.visible = False

                self.__tabs[index].selected = True
                self.__pages[index].visible = True
                ExtInfoWidget.current_page = index

            ui.Spacer(height=10)

            with ui.HStack(height=20):

                tab_buttons = []

                for index, page in enumerate(page_tabs):
                    tab_btn = ui.Button(
                        page.get_tab_name(),
                        width=0,
                        style_type_name_override="ExtensionDescription.Tab",
                        clicked_fn=lambda i=index: set_page(i),
                        identifier=f"tab_{page.get_tab_name().lower()}",
                    )
                    tab_buttons.append(tab_btn)
                    if index < len(page_tabs) - 1:
                        ui.Line(
                            style_type_name_override="ExtensionDescription.TabLine",
                            alignment=ui.Alignment.H_CENTER,
                            height=20,
                            width=40,
                        )

                ui.Spacer()
                self.__tabs[:] = tab_buttons

            ui.Spacer(height=8)

            with ui.ZStack():
                pages = []
                for page_tab in page_tabs:
                    page = ui.Frame(build_fn=lambda i=ext_info, e=ext_item, page_tab=page_tab: page_tab.build_tab(i, e))
                    pages.append(page)

                self.__pages[:] = pages

            set_page(ExtInfoWidget.current_page)  # Default page

        ################################################################################################################
        ################################################################################################################
        # Build Actual UI Layout of all blocks

        with self._frame:
            with ui.ZStack():
                ui.Rectangle(style_type_name_override="ExtensionDescription.Background")
                with ui.VStack(spacing=4, identifier="ext_info_widget"):
                    # Top Margin
                    ui.Spacer(height=4)
                    with ui.HStack(height=0, spacing=5):
                        draw_icon_block()
                        with ui.VStack():
                            draw_top_row_block()
                            ui.Spacer(height=10)
                            draw_extension_name_block()
                            draw_extension_id_block()
                            draw_extension_description_block()
                        draw_category_block()

                    draw_ext_source_block()

                    with ui.HStack():
                        ui.Spacer(width=10)

                        # Content page
                        with ui.VStack():
                            # Separator line
                            ui.Line(
                                height=0,
                                alignment=ui.Alignment.BOTTOM,
                                style_type_name_override="ExtensionDescription.TabLineFull",
                            )

                            draw_content_block()

                        ui.Spacer(width=10)
                    ui.Spacer(height=5)

    def _refresh_once_next_frame(self):
        async def _delayed_refresh(weak_widget):
            await omni.kit.app.get_app().next_update_async()

            w = weak_widget()
            if w:
                w._refresh_task = None
                w._refresh()

        with contextlib.suppress(Exception):
            self._refresh_task.cancel()

        self._refresh_task = asyncio.ensure_future(_delayed_refresh(weakref.ref(self)))

    def set_show_dependencies_fn(self, fn: Callable):
        """Assigns a function to be called to show the extension dependencies.

        Args:
            fn (:obj:`Callable`): The function to call."""
        self._show_dependencies_fn = fn

    def _show_dependencies(self, ext_id):
        if self._show_dependencies_fn:
            self._show_dependencies_fn(ext_id)

    def destroy(self):
        """Cleans up resources and subscriptions."""
        self._ext_change_sub = None
        if self._ext_dependencies:
            self._ext_dependencies.destroy()
            self._ext_dependencies = None

        for page in self.page_tabs:
            page.destroy()
        # We want to None the instances also

        self._version_menu = None
        self.__tabs = []
        self.__pages = []
