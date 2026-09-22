# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from typing import List, Union

import carb.settings
import omni.kit.commands
import omni.ui as ui
from omni.kit.xr.core import XRCore, XRCoreEventType, XRProfile, XRShutdown, XRSystem, XRWeakMethod

from .settings_widget import create_setting_widget, create_setting_widget_combo
from .settings_widget_builder import SettingsWidgetBuilder
from .style import get_colors


class XRSettingsFrame:
    def __init__(self, profile: XRProfile, config: dict = {}) -> None:
        self._profile = profile
        self._config = config
        self._settings = carb.settings.get_settings()

        collapsed = self.is_collapsed()
        if "collapsed" in config:
            collapsed = config["collapsed"]

        collapsable = self.is_collapsable()
        if "collapsable" in self._config:
            collapsable = self._config["collapsable"]

        colors = get_colors()
        self._collapsedState = collapsed

        name = "XRPanel"
        panel_color = colors["panel"]
        highlight_color = colors["panel_highlight"]

        if self.is_advanced():
            panel_color = colors["advanced_panel"]
            highlight_color = colors["advanced_panel_highlight"]
            name = "XRAdvancedPanel"

        if self.is_info():
            panel_color = colors["info_panel"]
            highlight_color = colors["info_panel_highlight"]
            name = "XRInfoPanel"

        padding = 4
        if not collapsable:
            padding = 0

        # TODO: CollapsableFrame is not applying style correctly
        # for now use inline styles that seem to be working correctly

        style = {
            "CollapsableFrame": {
                "background_color": panel_color,
                "secondary_color": panel_color,
                "border_radius": 4,
                "padding": padding,
            },
            "CollapsableFrame:hovered": {"secondary_color": highlight_color},
            "CollapsableFrame:pressed": {"secondary_color": highlight_color},
        }

        self._widget = ui.CollapsableFrame(
            "CollapsableFrame",
            build_fn=self._build,
            build_header_fn=self.build_header,
            skip_draw_when_clipped=True,
            collapsed=self._collapsedState,
            style=style,
            style_type_name_override=name,
        )

        self.sub_widgets: list = []
        self.sub_models: list = []
        self._subs: list = []

        if carb.settings.get_settings().get("/xr/persistence/enabled") is True:
            self.__persistence_prefix = "/persistent/xr/"
        else:
            self.__persistence_prefix = "/xr/"

        XRShutdown.assert_object_deletion_upon_shutdown(self)

    def is_advanced(self):
        return False

    def is_info(self):
        return False

    def is_collapsed(self):
        return False

    def is_collapsable(self):
        return True

    def get_config(self):
        return self._config

    def get_profile_name(self) -> str:
        return self._profile.get_name()

    def get_profile_path(self) -> str:
        return self._profile.get_profile_path()

    def get_persistent_path(self) -> str:
        return self._profile.get_persistent_path()

    def get_non_persistent_path(self) -> str:
        return self._profile.get_non_persistent_path()

    def get_scene_persistent_path(self) -> str:
        return self._profile.get_scene_persistent_path()

    def get_non_profile_persistent_path(self) -> str:
        return self.__persistence_prefix

    def get_non_profile_path(self) -> str:
        return "/xr/"

    def get_profile(self):
        return self._profile

    def get_frame_name(self) -> str:
        return ""

    def destroy(self) -> None:
        """
        We need to explicitly destroy widgets/models -  there's usually a number of circular ref
        between model and Widget which can be difficult to track down and keep widgets alive
        after the Frame is rebuilt
        """
        self._subs = []

        for w in self.sub_models:
            w.destroy()
        self.sub_models = []

        self.sub_widgets = []

        if self._widget is not None:
            self._widget.set_collapsed_changed_fn(None)
            self._widget.set_build_fn(None)
            self._widget.clear()
            self._widget = None

    def build_header(self, collapsed, title):
        collapsable = self.is_collapsable()
        if "collapsable" in self._config:
            collapsable = self._config["collapsable"]

        if collapsable:
            triangle_alignment = ui.Alignment.RIGHT_CENTER
            triangle_width = 4
            triangle_height = 6
            if not collapsed:
                triangle_alignment = ui.Alignment.CENTER_BOTTOM
                triangle_width = 7
                triangle_height = 5

            with ui.HStack(height=20, style={"HStack": {"margin_height": 5}}):
                ui.Spacer(width=5)
                with ui.VStack(width=15):
                    ui.Spacer()
                    ui.Triangle(
                        alignment=triangle_alignment,
                        name="title",
                        width=triangle_width,
                        height=triangle_height,
                    )
                    ui.Spacer()

                self._title = ui.Label(self.get_frame_name(), name="title", width=0)
                ui.Spacer()

    def _build(self):
        self._subs = []

        collapsable = self.is_collapsable()
        if "collapsable" in self._config:
            collapsable = self._config["collapsable"]
        padding = 0
        if not collapsable:
            padding = 4

        style = {"Frame": {"padding": padding}}
        margin = 10
        if self.is_advanced() or self.is_info():
            margin = 2

        with ui.Frame(height=0, style=style):
            with ui.VStack(height=0, spacing=5, style={"VStack": {"margin_width": margin}}):
                ui.Spacer(height=5)
                self.build_ui()
                ui.Spacer(height=5)

    def _rebuild(self):
        if self._widget:
            self._subs = []
            self._widget.rebuild()
            self._title = self.get_frame_name()

    def _restore_defaults(self, path: str):
        omni.kit.commands.execute("RestoreDefaultSettingCommand", path=path)

    def _add_text(self, text: str):
        """Add a non-editable label"""
        SettingsWidgetBuilder.createLabelMultiline(text)

    def add_info(self, name: str, path: str):
        with ui.HStack(skip_draw_when_clipped=True):
            SettingsWidgetBuilder._create_label(name, "", "")
            text = carb.settings.get_settings().get(path)
            if text is None:
                text = False

            if not isinstance(text, str):
                text = str(text)
            ui.Label(text, name="label", word_wrap=True)

    def add_info_bool(self, name: str, path: str, trueText: str, falseText: str):
        with ui.HStack(skip_draw_when_clipped=True):
            SettingsWidgetBuilder._create_label(name, "", "")
            val = carb.settings.get_settings().get(path)
            if val is None:
                val = False

            if not isinstance(val, bool):
                val = False
            text = falseText
            if val is True:
                text = trueText
            ui.Label(text, name="label", word_wrap=True)

    def add_setting(
        self,
        setting_type,
        name: str,
        path: str,
        range_from=0,
        range_to=0,
        step=0.01,
        has_reset=True,
        tooltip="",
        callback=None,
        **kwargs,
    ):
        if "filtered_settings" in self.get_config():
            filtered_settings = self.get_config()["filtered_settings"]
            if path in filtered_settings:
                return None

        with ui.HStack(skip_draw_when_clipped=True):
            SettingsWidgetBuilder._create_label(name, path, tooltip)
            widget, model = create_setting_widget(path, setting_type, range_from, range_to, step, **kwargs)
            self.sub_widgets.append(widget)
            self.sub_models.append(model)
            if has_reset:
                button = SettingsWidgetBuilder._build_reset_button(path)
                model.set_reset_button(button)
            else:
                ui.Spacer(width=35)

            if callback is not None:
                subs = self._subs
                subs.append(omni.kit.app.SettingChangeSubscription(path, lambda *_: callback()))

        return widget

    def add_setting_combo(
        self,
        name: str,
        path: str,
        items: Union[list, dict],
        callback=None,
        has_reset=True,
        tooltip="",
    ):
        if "filtered_settings" in self.get_config():
            filtered_settings = self.get_config()["filtered_settings"]
            if path in filtered_settings:
                return None

        with ui.HStack(skip_draw_when_clipped=True):
            SettingsWidgetBuilder._create_label(name, path, tooltip)
            widget, model = create_setting_widget_combo(path, items)
            self.sub_widgets.append(widget)
            self.sub_models.append(model)
            if has_reset:
                button = SettingsWidgetBuilder._build_reset_button(path)
                model.set_reset_button(button)
            else:
                ui.Spacer(width=35)

            if callback is not None:
                subs = self._subs
                subs.append(omni.kit.app.SettingChangeSubscription(path, lambda *_: callback()))
        return widget

    def build_ui(self):
        """virtual function that will be called in the Collapsable frame"""
        pass

    def add_rebuild_subscription(self, path: str) -> None:
        rebuild_fn = XRWeakMethod(self._rebuild)

        self._subs.append(omni.kit.app.SettingChangeSubscription(path, lambda *_: rebuild_fn()))

    def add_rebuild_on_messagebus(self, message_name: str) -> None:
        rebuild_fn = XRWeakMethod(self._rebuild)

        evstream = XRCore.get_singleton().get_message_bus()
        message_type = carb.events.type_from_string(message_name)
        self._subs.append(
            evstream.create_subscription_to_pop_by_type(message_type, lambda *_: rebuild_fn(), order=1000)
        )

    def get_available_systems(self) -> List[XRSystem]:
        rebuildUI = XRWeakMethod(self._rebuild)
        self._subs.append(
            omni.kit.app.SettingChangeSubscription(
                self.get_persistent_path() + "system/display", lambda *_: rebuildUI()
            )
        )

        self._subs.append(
            omni.kit.app.SettingChangeSubscription(
                self.get_non_persistent_path() + "system/displaySupported",
                lambda *_: rebuildUI(),
            )
        )

        evstream = XRCore.get_singleton().get_message_bus()
        self._subs.append(
            evstream.create_subscription_to_pop_by_type(XRCoreEventType.system_list_updated, lambda *_: rebuildUI())
        )

        available_systems = carb.settings.get_settings().get(self.get_non_persistent_path() + "system/displaySupported")

        if not isinstance(available_systems, list):
            systemDisplayMode = carb.settings.get_settings().get(self.get_non_persistent_path() + "system/displayMode")
            systems = XRCore.get_singleton().get_systems(systemDisplayMode)

            available_systems = []
            for system in systems:
                available_systems.append(system.get_name())

        selected_system = carb.settings.get_settings().get(self.get_persistent_path() + "system/display")

        if len(list(set(available_systems).intersection(set([selected_system])))) == 0:
            if len(available_systems) > 0:
                carb.settings.get_settings().set(self.get_persistent_path() + "system/display", available_systems[0])

        return available_systems

    def get_current_system(self) -> Union[None, XRSystem]:
        selected_system = carb.settings.get_settings().get(self.get_persistent_path() + "system/display")
        return XRCore.get_singleton().get_system(selected_system)

    def is_quadview_active(self) -> bool:

        self.add_rebuild_subscription(self.get_non_persistent_path() + "quadview/active")

        quadview_active = carb.settings.get_settings().get(self.get_non_persistent_path() + "quadview/active")
        if quadview_active is None:
            quadview_active = False

        return quadview_active
