# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import copy
import time
from typing import Callable, List, Optional, Tuple, Union

import carb
import omni.kit.app
import omni.kit.menu.utils
import omni.kit.ui
import omni.ui
from omni.kit.xr.core import XRCore, XRCoreEventType, XREditorMenuToggleItem, XRProfile, XRShutdown, XRWeakMethod
from omni.kit.xr.core.recorder import start_replay_if_enabled

from .menu.xr_menu_openxr_utils import has_valid_openxr_runtime
from .ui.exclusive_xr_profile_dialog import XRExclusiveProfileDialog
from .ui.settings_stack import XRSettingsStack
from .ui.style import get_style

XR_STATUS_ERROR_MESSAGE_PATH = "/xr/status/error"
ACTIVE_RENDERER_SETTING_PATH = "/renderer/active"
ACTIVE_RENDER_MODE_SETTING_PATH = "/rtx/rendermode"


# Modal window is used to indicate switching of modes and also blocks input to allow for ui assets to load
# This avoids multiple simultaneous loads
class XRModalDialog:
    def __init__(self, name: str, profile: XRProfile, show_greeting_dialog: bool = False) -> None:
        self.__modal_window = None
        self.__subs = {}
        self.__name = name
        self.__show_greeting_dialog = show_greeting_dialog
        self.__profile = profile

        # listen to when the profile gets activated
        show_dialog_fn = XRWeakMethod(self.show_dialog)
        self.__subs["enable"] = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(
                XRCoreEventType.profile_enable(profile.get_name()), lambda *_: show_dialog_fn(), order=2
            )
        )

        # track first time for information dialog
        self.__first_time_enabled = True

        # assert that object is deleted
        XRShutdown.assert_object_deletion_upon_shutdown(self)

    def __del__(self):
        self.destroy()

    def destroy(self):
        """
        Called when modal overlay is destroyed
        """
        self.__subs = None

        if self.__modal_window is not None:
            self.__modal_window.destroy()
            self.__modal_window = None

    def show_dialog(self) -> None:
        """
        Executed when user enters an XR profile
        """

        guiMode = carb.settings.get_settings().get(self.__profile.get_persistent_path() + "app/guiMode")
        if guiMode is not None and guiMode == "fullscreen":
            return

        if self.__first_time_enabled and self.__show_greeting_dialog:
            # Dispatch an event that this is first time the mode is enabled
            XRCore.get_singleton().get_message_bus().dispatch(XRCoreEventType.first_launch_greeting, payload={})
            self.__first_time_enabled = False
        else:
            self._show_modal_dialog()

    def _show_modal_dialog(self) -> None:
        """
        Internal function called to show a dialog to block input for a few seconds
        """

        # Create window that blocks input
        self.__modal_window = omni.ui.Window(
            "Switching Mode", visible=False, height=0, dockPreference=omni.ui.DockPreference.DISABLED, auto_resize=True
        )
        if self.__modal_window is None:  # Add None value checking here to bypass mypy attr error
            raise ValueError("self.__modal_window is None")

        # Make it an overlay window
        self.__modal_window.flags = (
            omni.ui.WINDOW_FLAGS_NO_COLLAPSE
            | omni.ui.WINDOW_FLAGS_NO_RESIZE
            | omni.ui.WINDOW_FLAGS_NO_SCROLLBAR
            | omni.ui.WINDOW_FLAGS_MODAL
            | omni.ui.WINDOW_FLAGS_NO_CLOSE
            | omni.ui.WINDOW_FLAGS_NO_TITLE_BAR
        )

        # Add information text into modal overlay window
        with self.__modal_window.frame:
            with omni.ui.VStack(width=400):
                omni.ui.Spacer(height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Label(
                        "... Entering " + self.__name + " Mode ...",
                        alignment=omni.ui.Alignment.CENTER,
                        style={"font_size": 20},
                    )

                omni.ui.Spacer(height=10)

        self.__modal_window.visible = True
        self.__modal_cur_count = 0
        self.__modal_target_count = 60
        self.__time = time.time()

        # Add function that switches off modal window after 2 seconds
        def on_update(ev: carb.events.IEvent):
            self.__modal_cur_count = self.__modal_cur_count + 1
            MAX_TIME_SEC = 2
            if self.__modal_cur_count == self.__modal_target_count or (time.time() - self.__time) > MAX_TIME_SEC:
                self.__subs["modal_wait"] = None
                self.__modal_window.destroy()
                self.__modal_window = None

        # Add destroy function to on_update in the app
        self.__subs["modal_wait"] = (
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(XRCoreEventType.post_sync_update, on_update, name="Update", order=0)
        )


# Class with settings window
class XRProfileSettingsWindow:
    def __init__(
        self,
        name: str,
        ext_name: str,
        component_list: List[Callable],
        icons: Union[None, List[str]] = None,
        show_greeting_dialog: bool = False,
    ) -> None:

        self.__settings = carb.settings.get_settings()
        self.__xr_core = XRCore.get_singleton()

        self.__subs: Optional[dict] = {}
        self.__name = name
        self.__component_list = component_list
        self.__profile = self.__xr_core.get_profile(self.__name)
        self.__display_name = self.__settings.get(self.__profile.get_non_persistent_path() + "displayName")
        self.__window: Union[None, omni.ui.Window] = None

        self.__extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(ext_name)

        self.__icons = icons

        start_profile_on_app_ready_setting = self.__settings.get(f"/xr/{self.__name}/enabled")
        show_settings = self.__settings.get("exts/" + ext_name + "/show_settings")
        if show_settings is None or start_profile_on_app_ready_setting:
            show_settings = True

        self.__settings.set_default("/xr/profiles/menu/location", "Window/Rendering")
        self.__root_menu_location = self.__settings.get("/xr/profiles/menu/location")
        add_to_editor_menu = (self.__root_menu_location is not None) and (self.__root_menu_location != "")

        if add_to_editor_menu:
            menu_location = f"{self.__root_menu_location}/{self.__display_name}"
            self.__menu_item = XREditorMenuToggleItem(
                ext_name, menu_location, XRWeakMethod(self._show_settings_window), value=show_settings
            )

        self._show_settings_window(menu_location, show_settings)
        self.__modal: Optional[XRModalDialog] = XRModalDialog(self.__display_name, self.__profile, show_greeting_dialog)
        self.__exclusive_profile_dialog: Optional[XRExclusiveProfileDialog] = XRExclusiveProfileDialog(
            self._start_profile
        )

        # We create subscription only if we passed that option
        if start_profile_on_app_ready_setting:
            start_profile_on_app_ready_fn = XRWeakMethod(self._start_profile_on_app_ready)
            self.__subs["start_profile_when_app_became_ready"] = (
                omni.kit.app.get_app()
                .get_startup_event_stream()
                .create_subscription_to_pop_by_type(
                    omni.kit.app.EVENT_APP_READY,
                    lambda *_: start_profile_on_app_ready_fn(),
                    name="Start Profile On App ready",
                )
            )

        XRShutdown.assert_object_deletion_upon_shutdown(self)

    def __del__(self) -> None:
        self.destroy()

    def destroy(self) -> None:
        self.__subs = None

        if self.__window is not None:
            self.__window.set_visibility_changed_fn(None)
            self.__window.frame.set_build_fn(None)
            self.__window.destroy()
            self.__window = None

        if self.__modal is not None:
            self.__modal.destroy()
            self.__modal = None

        self.__profile = None

        if self.__exclusive_profile_dialog is not None:
            self.__exclusive_profile_dialog.destroy()
            self.__exclusive_profile_dialog = None

        self.__menu_item = None

    def _create_settings_window(self) -> None:
        self.__window = omni.ui.Window(self.__display_name, dockPreference=omni.ui.DockPreference.RIGHT_BOTTOM)
        self.__window.deferred_dock_in("Property", omni.ui.DockPolicy.TARGET_WINDOW_IS_ACTIVE)

        self.__window.set_visibility_changed_fn(XRWeakMethod(self._updated_visibility))
        self.__window.frame.set_build_fn(XRWeakMethod(self._build_ui))
        self.__window.frame.rebuild()

    def _updated_visibility(self, visible) -> None:
        if self.__menu_item:
            self.__menu_item.ticked_value = visible

    def _rebuild_frame(self) -> None:
        if self.__window:
            self.__window.frame.rebuild()

    def _check_system_can_start(self) -> Tuple[bool, Optional[str]]:
        current_system = self.__settings.get(self.__profile.get_persistent_path() + "system/display")
        if current_system == "OpenXR" and not has_valid_openxr_runtime():
            return (
                False,
                "Cannot start OpenXR! No valid active runtime is set. Please select a different OpenXR runtime or check your XR headset's configuration to activate OpenXR and relaunch this app.",
            )
        if not XRCore.check_current_renderer_supported(self.get_display_name(), False):
            renderer = self.__settings.get(ACTIVE_RENDERER_SETTING_PATH)
            render_mode = self.__settings.get(ACTIVE_RENDER_MODE_SETTING_PATH)
            return (
                False,
                f"The currently active renderer '{renderer} ({render_mode})' is not supported by XR.  Switch to the RTX renderer.",
            )
        return True, None

    def _start_profile(self) -> None:
        can_start, error_msg = self._check_system_can_start()
        if not can_start:
            # Shows error in viewport and logs to console (see viewport_layer)
            self.__settings.set(XR_STATUS_ERROR_MESSAGE_PATH, error_msg)
        else:
            # monado service needs to be started earlier than profile
            # so that monado IPC client can connect to it
            start_replay_if_enabled(self.__profile)
            self.__settings.set(self.__profile.get_non_persistent_path() + "enabled", True)

    def _stop_profile(self) -> None:
        self.__settings.set(self.__profile.get_non_persistent_path() + "enabled", False)

    def _build_ui(self) -> None:
        if self.__exclusive_profile_dialog is None or self.__window is None or self.__subs is None:
            raise ValueError(f"{self.__exclusive_profile_dialog=}, {self.__window=}, {self.__subs=}")

        start_fn = XRWeakMethod(self.__exclusive_profile_dialog.handle_start_xr_profile)
        stop_fn = XRWeakMethod(self._stop_profile)
        rebuild_frame_fn = XRWeakMethod(self._rebuild_frame)

        style = get_style()
        self.__window.frame.set_style(style)

        self.__subs["enable"] = omni.kit.app.SettingChangeSubscription(
            self.__profile.get_non_persistent_path() + "enabled", lambda *_: rebuild_frame_fn()
        )

        self.__subs["rebuild_when_display_system_changes"] = omni.kit.app.SettingChangeSubscription(
            self.__profile.get_persistent_path() + "system/display", lambda *_: rebuild_frame_fn()
        )

        self.__subs["rebuild_when_renderer_changes"] = omni.kit.app.SettingChangeSubscription(
            ACTIVE_RENDERER_SETTING_PATH, lambda *_: rebuild_frame_fn()
        )

        self.__subs["rebuild_when_renderer_mode_changes"] = omni.kit.app.SettingChangeSubscription(
            ACTIVE_RENDER_MODE_SETTING_PATH, lambda *_: rebuild_frame_fn()
        )

        self.__subs["rebuild_when_openxr_runtime_changes"] = omni.kit.app.SettingChangeSubscription(
            "/persistent/xr/system/openxr/runtime", lambda *_: rebuild_frame_fn()
        )

        can_start, start_error_msg = self._check_system_can_start()

        with self.__window.frame:
            with omni.ui.ScrollingFrame():
                with omni.ui.HStack(spacing=0):
                    with omni.ui.VStack(height=0, spacing=10):
                        omni.ui.Spacer(height=1)
                        with omni.ui.ZStack(height=30):
                            icon = None
                            icon_color = 0xFFFFFFFF
                            if self.__settings.get(self.__profile.get_non_persistent_path() + "enabled"):
                                text = "Stop " + self.__display_name
                                click_fn = stop_fn
                                tooltip = "Click here to stop " + self.__display_name
                                if self.__icons is not None and len(self.__icons) == 2:
                                    icon = self.__extension_path + "/" + self.__icons[1]
                                color = 0xFFFFAA66
                            else:
                                text = "Start " + self.__display_name
                                click_fn = start_fn
                                tooltip = "Click here to start " + self.__display_name
                                if can_start:
                                    if self.__icons is not None and len(self.__icons) == 2:
                                        icon = self.__extension_path + "/" + self.__icons[0]
                                    color = 0xFFEEEEEE
                                else:
                                    icon = "resources/glyphs/error.svg"
                                    color = 0xFF8888FF
                                    icon_color = color

                            omni.ui.Rectangle(
                                style={
                                    "Rectangle": {"background_color": 0xFF222222, "border_radius": 8},
                                    "Rectangle:hovered": {"background_color": 0xFF333333},
                                }
                            )
                            self._button = omni.ui.HStack(height=36, alignment=omni.ui.Alignment.CENTER)
                            self._button.set_mouse_released_fn(lambda *_: click_fn())
                            self._button.set_tooltip(tooltip)

                            with self._button:
                                style = {"Label": {"font_size": 20, "color": color}}

                                omni.ui.Spacer()
                                if icon is not None:
                                    omni.ui.Image(icon, width=28, height=36, style={"Image": {"color": icon_color}})
                                    omni.ui.Spacer(width=16)
                                self._button = omni.ui.Label(
                                    text, style=style, width=0, alignment=omni.ui.Alignment.CENTER
                                )
                                omni.ui.Spacer()

                        if not can_start:
                            style = {"Label": {"font_size": 16, "color": color, "margin": 10}}
                            omni.ui.Spacer()
                            omni.ui.Label(
                                start_error_msg, style=style, alignment=omni.ui.Alignment.CENTER, word_wrap=True
                            )

                        self.__settings_frame = XRSettingsStack(self.__component_list)
                        self.__settings_frame.build_ui(self.__profile)
                    omni.ui.Spacer(width=5)

    def _show_settings_window(self, menu_path: str, enabled: bool) -> None:
        # create the window late and only if needed
        if enabled and self.__window is None:
            self._create_settings_window()

        if self.__window:
            self.__window.visible = enabled

        self._updated_visibility(enabled)

        if self.__menu_item:
            self.__menu_item.ticked_value = enabled

    def _start_profile_on_app_ready(self) -> None:
        self._start_profile()
        if self.__subs:
            self.__subs["start_profile_when_app_became_ready"] = None  # Removing subscription

    def get_profile(self) -> XRProfile:
        return self.__profile

    def get_display_name(self) -> str:
        return self.__display_name

    @property
    def component_list(self):
        return copy.deepcopy(self.__component_list)

    @property
    def icons(self):
        icons = []
        for icon in self.__icons:
            icons.append(self.__extension_path + "/" + icon)
        return icons
