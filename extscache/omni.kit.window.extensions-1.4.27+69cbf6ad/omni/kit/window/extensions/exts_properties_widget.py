# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides a widget for managing and displaying properties of extensions in an application, including UI components for extension paths, registries, and cache, as well as options for exporting extension data."""

__all__ = ["ExtsPropertiesWidget"]

import carb
import carb.dictionary
import carb.settings
import carb.tokens
import omni.kit.app
import omni.ui as ui
from carb.eventdispatcher import get_eventdispatcher

from .common import COMMUNITY_TAB_TOGGLE_GLOBAL_EVENT, SettingBoolValue, get_options
from .exts_list_widget import ExtSummaryItem
from .exts_properties_paths import ExtsPathsWidget
from .exts_properties_registries import ExtsRegistriesWidget
from .styles import get_style
from .utils import cleanup_folder, copy_text, ext_id_to_name_version, get_setting, version_to_str


class ExtsPropertiesWidget:
    """A widget class used within an application to manage and display properties of extensions.

    This class provides functionality to manage extension properties, such as search paths and registries, and to clean and export extension data. It includes a user interface composed of various collapsable frames that allow users to interact with extension settings, view extension summaries, and perform actions such as opening extension paths or clearing extension caches.

    The widget is designed to be integrated into applications that support extension management and requires an extension manager to function. It subscribes to extension change events to refresh its contents dynamically.
    """

    def __init__(self):
        """Initialize the extension properties widget."""
        self._ext_manager = omni.kit.app.get_app().get_extension_manager()
        self._ext_change_sub = [
            get_eventdispatcher().observe_event(
                observer_name="exts_properties_widget",
                on_event=lambda _: self._refresh(),
                event_name=omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED,
            ),
            get_eventdispatcher().observe_event(
                observer_name="exts_properties_widget",
                on_event=lambda _: self._refresh(),
                event_name=omni.ext.GLOBAL_EVENT_FOLDER_CHANGED,
            ),
        ]

        self._registries_widget = None
        self._paths_widget = None

        self._frame = ui.Frame()

    def destroy(self):
        """Cleans up the widget and its subscriptions."""
        self._clean_widgets()
        self._ext_change_sub = None
        self._frame = None

    def set_visible(self, visible):
        """Sets the visibility of the widget.

        Args:
            visible (bool): Whether the widget should be visible."""
        self._frame.visible = visible
        self._refresh()

    def _clean_widgets(self):
        if self._registries_widget:
            self._registries_widget.destroy()
            self._registries_widget = None
        if self._paths_widget:
            self._paths_widget.destroy()
            self._paths_widget = None

    def _refresh(self):
        if not self._frame.visible:
            return

        self._clean_widgets()

        # Build UI
        with self._frame:
            with ui.ScrollingFrame(
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                identifier="exts_properties_widget",
            ):
                with ui.ZStack(style=get_style(self)):
                    ui.Rectangle(style_type_name_override="Properies.Background")
                    with ui.HStack():
                        ui.Spacer(width=20)
                        with ui.VStack(spacing=4, height=0):

                            def add_open_button(text, url):  # pragma: no cover
                                def open_url(url_=url):
                                    # Import it here instead of on the file root because it has long import time.
                                    import webbrowser

                                    webbrowser.open(url_)

                                ui.Button(text, width=0, clicked_fn=open_url, tooltip=url)

                            ui.Spacer(height=10)

                            # Extension Search Paths
                            with ui.CollapsableFrame("Extension Search Paths", collapsed=False):
                                self._paths_widget = ExtsPathsWidget()

                            # Registries
                            with ui.CollapsableFrame("Extension Registries", collapsed=False):
                                self._registries_widget = ExtsRegistriesWidget()

                            with ui.CollapsableFrame("Extension System Cache", collapsed=True):
                                with ui.VStack():
                                    ui.Spacer(height=10)

                                    cache_path = get_setting("/exts/omni.kit.registry.nucleus/cachePath", None)
                                    if cache_path:
                                        cache_path = carb.tokens.get_tokens_interface().resolve(cache_path)
                                        with ui.HStack():
                                            add_open_button("Open", cache_path)

                                            def clean(p_=cache_path):
                                                cleanup_folder(p_)

                                            ui.Button(
                                                "Clean",
                                                width=0,
                                                clicked_fn=clean,
                                                tooltip="Remove all downloaded extensions",
                                            )

                                            ui.Label(f"Path: {cache_path}")

                                    ui.Spacer(height=10)

                            with ui.CollapsableFrame("Options", collapsed=True):
                                with ui.VStack():

                                    def add_option(option: SettingBoolValue, name: str, evt: str = None):
                                        ui.Spacer(height=10)

                                        # Publishing enabled
                                        with ui.HStack(width=60):
                                            cb = ui.CheckBox()

                                            def on_change(model):
                                                option.set_bool(model.get_value_as_bool())
                                                if evt:
                                                    omni.kit.app.queue_event(evt)

                                            cb.model.set_value(option.get())
                                            cb.model.add_value_changed_fn(on_change)
                                            ui.Label(name)

                                    options = get_options()
                                    add_option(options.publishing, "Publishing Enabled")
                                    add_option(
                                        options.show_update_icon,
                                        "Show Update Icon in the Extension List",
                                        COMMUNITY_TAB_TOGGLE_GLOBAL_EVENT,
                                    )
                                    if options.community_tab is not None:
                                        add_option(
                                            options.community_tab,
                                            "Show Community Extensions",
                                            COMMUNITY_TAB_TOGGLE_GLOBAL_EVENT,
                                        )

                                    ui.Spacer(height=10)

                                # Export all exts data
                            with ui.CollapsableFrame("Miscellaneous", collapsed=True):
                                with ui.VStack():
                                    ui.Spacer(height=10)

                                    ext_summaries = self._ext_manager.fetch_extension_summaries()
                                    total_cnt = len(ext_summaries)
                                    builtin_cnt = sum(
                                        bool(e["flags"] & omni.ext.EXTENSION_SUMMARY_FLAG_BUILTIN)
                                        for e in ext_summaries
                                    )
                                    installed_cnt = sum(
                                        bool(e["flags"] & omni.ext.EXTENSION_SUMMARY_FLAG_INSTALLED)
                                        for e in ext_summaries
                                    )
                                    ui.Label(f"Total Extensions: {total_cnt}", height=20)
                                    ui.Label(f"Bultin Extensions: {builtin_cnt}", height=20)
                                    ui.Label(f"Installed Extensions: {installed_cnt}", height=20)
                                    registry_count = len(self._ext_manager.get_registry_extensions())
                                    ui.Label(f"Registry Packages: {registry_count}", height=20)

                                    ui.Spacer(height=10)

                                    ui.Button(
                                        "Copy all exts as CSV",
                                        width=100,
                                        height=30,
                                        clicked_fn=lambda: self.export_all_exts(ext_summaries),
                                    )

                                    # Export all exts data
                                    ui.Button(
                                        "Copy enabled exts as .kit file (top level)",
                                        width=100,
                                        height=30,
                                        clicked_fn=lambda: self.export_enabled_exts_as_kit_file(only_top_level=True),
                                    )

                                    # Export all exts data
                                    ui.Button(
                                        "Copy enabled exts as .kit file (all)",
                                        width=100,
                                        height=30,
                                        clicked_fn=lambda: self.export_enabled_exts_as_kit_file(only_top_level=False),
                                    )

                                    ui.Spacer()
                        ui.Spacer(width=20)

    def export_all_exts(self, ext_summaries):
        """Export all exts in CSV format with some of config params. print and copy result.

        Args:
            ext_summaries (list): A list of extension summaries to export."""
        ext_sum_dict = {}
        for ext_s in ext_summaries:
            item = ExtSummaryItem(ext_s)
            ext_sum_dict[ext_s["fullname"]] = item

        fields_to_export = [
            "package/name",
            "package/version",
            "can_update,latest_version",  # special case
            "state/enabled",
            "isKitFile",
            "package/category",
            "package/title",
            "package/description",
            "package/authors",
            "package/repository",
            "package/keywords",
            "package/readme",
            "package/changelog",
            "package/preview_image",
            "package/icon",
            "core/reloadable",
        ]

        # Header
        output = ",".join(["id"] + fields_to_export) + "\n"

        # Per ext row data
        for ext in self._ext_manager.get_extensions():
            d = self._ext_manager.get_extension_dict(ext["id"])
            row = ext["id"] + ","
            for f in fields_to_export:
                if f.startswith("can_update"):  # special case, do both rows at once
                    item = ext_sum_dict.get(ext["name"], None)
                    if item:
                        latest_version = version_to_str(item.latest_ext["version"][:4])
                        row += f'"{item.can_update}",'
                        row += f'"{latest_version}",'
                    else:
                        row += ",,"
                else:
                    row += f'"{str(d.get(f, ""))}",'

            row = row.replace("\n", r"\n")
            output += row + "\n"

        print(output)
        copy_text(output)

    def export_enabled_exts_as_kit_file(self, only_top_level=True):
        """Export all topmost exts in .kit format. print and copy result.

        Args:
            only_top_level (bool): Whether to export only top-level extensions."""

        excludes = {"omni.kit.registry.nucleus"}

        all_deps = set()
        all_exts = set()

        for ext in self._ext_manager.get_extensions():
            if ext["enabled"]:
                ext_id = ext["id"]
                info = self._ext_manager.get_extension_dict(ext_id)
                deps = info.get("state/dependencies", [])
                all_exts.add(ext_id)
                all_deps.update(deps)

        output = "[dependencies]\n"

        exported_exts = (all_exts - all_deps) if only_top_level else all_exts
        for e in exported_exts:
            if "-" not in e:
                print(f"skipping ext 1.0: {e}")
                continue
            name, version = ext_id_to_name_version(e)
            if name in excludes:
                continue
            output += '"{0}" = {{ version = "{1}", exact = true }}\n'.format(name, version)

        print(output)
        copy_text(output)
