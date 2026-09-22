# Copyright (c) 023, NVIDIA CORPORATION. All rights reserved.
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

__all__ = ["XRViewportLayer"]

import asyncio
import os
from pathlib import Path

import carb
import omni.kit.app
import omni.ui
from omni.kit.viewport.utility import post_viewport_message
from omni.kit.xr.core import XRCore, XRCoreEventType, XRWeakMethod

# Error message will appear in the bar when an error is written in this setting
# This error needs to be cleared
XR_STATUS_ERROR_MESSAGE_PATH = "/xr/status/error"

# When there is no error and XR is enabled. The status message will inform
# user about the state of XR, e.g. whether cloudXR is connected etc.
XR_STATUS_MESSAGE_PATH = "/xr/status/message"

# Render resolution indicates resolution the renderer is operating on
XR_STATUS_RENDER_RESOLUTION_PATH = "/xr/status/renderResolution"

# Output resolution is what is actually going to the device (difference with renderer resolution is foveation)
XR_STATUS_OUTPUT_RESOLUTION_PATH = "/xr/status/outputResolution"

# XR measure of current frames per second
XR_STATUS_FPS_PATH = "/xr/status/fps"

# Whether XR status window is enabled in the viewport
XR_STATUS_ENABLED_PATH = "/xr/status/enabled"

# Whether XR status window is enabled in the viewport
XR_STATUS_ACTIONMAP_PATH = "/xr/status/actionMap"

# In full screen mode all UI is disabled, hence there needs to be a way to escape XR mode
# This indicates that fullscreen mode is enabled and the status bar must be shown to allow
# the exit XR button to be pressed
XR_STATUS_FULLSCREEN_PATH = "/xr/status/fullscreen"

# Whether to show toast popups for error messages
XR_STATUS_SHOWTOAST_PATH = "/xr/status/showToast"

# Whether the status bar is on top instead of at the bottom
XR_STATUS_POSITION_TOP_PATH = "/xr/status/position/top"

# ====================================================================================
# This class is the menu that appears in the viewport when the application is
# in XR mode
# ====================================================================================


class XRViewportLayer:
    def __init__(self, desc: dict):
        self.__subs = []
        update_fn = XRWeakMethod(self.update_ui)

        self.__subs.append(omni.kit.app.SettingChangeSubscription(XR_STATUS_ERROR_MESSAGE_PATH, lambda *_: update_fn()))
        self.__subs.append(omni.kit.app.SettingChangeSubscription(XR_STATUS_MESSAGE_PATH, lambda *_: update_fn()))
        self.__subs.append(
            omni.kit.app.SettingChangeSubscription(XR_STATUS_RENDER_RESOLUTION_PATH, lambda *_: update_fn())
        )
        self.__subs.append(
            omni.kit.app.SettingChangeSubscription(XR_STATUS_OUTPUT_RESOLUTION_PATH, lambda *_: update_fn())
        )
        self.__subs.append(omni.kit.app.SettingChangeSubscription(XR_STATUS_FPS_PATH, lambda *_: update_fn()))
        self.__subs.append(omni.kit.app.SettingChangeSubscription(XR_STATUS_ENABLED_PATH, lambda *_: update_fn()))
        self.__subs.append(omni.kit.app.SettingChangeSubscription(XR_STATUS_FULLSCREEN_PATH, lambda *_: update_fn()))
        self.__subs.append(omni.kit.app.SettingChangeSubscription(XR_STATUS_ACTIONMAP_PATH, lambda *_: update_fn()))

        self.__subs.append(
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(
                XRCoreEventType.xr_enabled, lambda *_: update_fn(), name="XR Profile change"
            )
        )

        self.__subs.append(
            XRCore.get_singleton()
            .get_message_bus()
            .create_subscription_to_pop_by_type(
                XRCoreEventType.xr_disabled, lambda *_: update_fn(), name="XR Profile change"
            )
        )

        self.__viewport_api = desc.get("viewport_api")
        if not self.__viewport_api:
            raise RuntimeError("Cannot create XRViewportLayer without a viewport")

        self.__root = omni.ui.Frame()
        self.__root.set_build_fn(XRWeakMethod(self.build_ui))

        self.__error_message = None
        self.__status_fps = None
        self.__render_res = None
        self.__output_res = None
        self.__status_message = None
        self.__status_action_map = None

        # Not enabling toasts by default, they are hard to notice in the current version
        carb.settings.get_settings().set_default_bool(XR_STATUS_SHOWTOAST_PATH, False)
        self.__show_toast = carb.settings.get_settings().get(XR_STATUS_SHOWTOAST_PATH)

        carb.settings.get_settings().set_default_bool(XR_STATUS_POSITION_TOP_PATH, False)
        self.__position_top = carb.settings.get_settings().get(XR_STATUS_POSITION_TOP_PATH)

        # The menu has icons in it: find them on disk
        extension_path = (
            omni.kit.app.get_app()
            .get_extension_manager()
            .get_extension_path_by_module("omni.kit.xr.ui.window.viewport")
        )
        self.__icon_path = Path(os.path.join(extension_path, "icons"))

        # colors used in the menu
        self.__background_color = omni.ui.color("#191A1B")
        self.__color = omni.ui.color("#25282A")
        self.__background_hovered = omni.ui.color("#34C7FF3B")
        self.__background_border_hovered = omni.ui.color("#34C7FF")
        self.__background_color = omni.ui.color(0.145, 0.157, 0.165, 1)

        # State of the menu
        self.__status_bar = None
        self.__error_bar = None
        self.__show_error = False
        self.__show_error_count = 0

    def rebuild(self):
        """
        Rebuild the UI
        """
        self.__root.rebuild()

    def _build_error_bar(self):
        """
        Build the error bar.
        """

        # We need a weak function to avoid circular dependency
        close_fn = XRWeakMethod(self._close_error)

        self.__error_bar = omni.ui.VStack(visible=False)
        with self.__error_bar:
            if self.__position_top:
                omni.ui.Spacer(height=20)
            else:
                omni.ui.Spacer()
            with omni.ui.HStack(height=0):
                omni.ui.Spacer()
                with omni.ui.ZStack(width=0, height=0):
                    omni.ui.Rectangle(
                        style={"background_color": self.__background_color, "border_radius": 4, "color": self.__color}
                    )
                    with omni.ui.HStack():
                        omni.ui.Spacer(width=8)
                        # Error message
                        self.__error_message = omni.ui.Label("", style={"color": 0xFF8888FF})
                        omni.ui.Spacer(width=8)
                        button_style = {
                            "Button": {
                                "background_color": self.__background_color,
                                "stack_direction": omni.ui.Direction.LEFT_TO_RIGHT,
                            },
                            "Button:hovered": {
                                "background_color": self.__background_hovered,
                                "color": self.__background_border_hovered,
                                "border_width": 2,
                                "border_color": self.__background_border_hovered,
                            },
                        }
                        # Close button
                        omni.ui.Button(
                            "",
                            image_url=str(os.path.join(self.__icon_path, "cross.svg")),
                            image_width=20,
                            image_height=20,
                            width=0,
                            style=button_style,
                            tooltip="Close Error",
                            clicked_fn=close_fn,
                        )

                omni.ui.Spacer()
            if self.__position_top:
                omni.ui.Spacer()
            else:
                omni.ui.Spacer(height=20)

    def _exit_xr_mode(self):
        """
        Exit XR mode and disable the current profile
        """
        XRCore.get_singleton().request_disable_profile()

    async def _close_on_wait_async(self, count):
        """
        Asynchronous function that executes the wait
        """
        await asyncio.sleep(30)

        # We use a count in case an new error was reported
        # That one should not be closed. The count ensures
        # we close the right error
        if count == self.__show_error_count:
            self.__show_error = False
            # Update the UI so the status bar is shown again
            self.update_ui()

    def _close_on_wait(self, count):
        """
        Setup asynchronous callback that will close the error bar after 30 seconds.
        """
        asyncio.ensure_future(self._close_on_wait_async(count))

    def _close_error(self):
        """
        Called when the user clicks on the exit button in the error bar.
        """
        self.__show_error = False
        self.update_ui()

    def _build_status_bar(self):
        """
        Build the status bar
        """

        # We need a weak function to avoid circular dependency
        exit_fn = XRWeakMethod(self._exit_xr_mode)

        self.__status_bar = omni.ui.VStack(visible=False)
        with self.__status_bar:
            if self.__position_top:
                omni.ui.Spacer(height=20)
            else:
                omni.ui.Spacer()
            with omni.ui.HStack(height=0):
                omni.ui.Spacer()
                with omni.ui.ZStack(width=0, height=0):
                    omni.ui.Rectangle(
                        style={"background_color": self.__background_color, "border_radius": 4, "color": self.__color}
                    )

                    button_style = {
                        "Button": {
                            "background_color": self.__background_color,
                            "stack_direction": omni.ui.Direction.LEFT_TO_RIGHT,
                        },
                        "Button:hovered": {
                            "background_color": self.__background_hovered,
                            "color": self.__background_border_hovered,
                            "border_width": 2,
                            "border_color": self.__background_border_hovered,
                        },
                    }

                    with omni.ui.HStack():
                        # Content of the status bar
                        omni.ui.Spacer(width=8)
                        omni.ui.Label("XR", width=0, style={"color": 0xFFFFFFFF})
                        omni.ui.Spacer(width=8)
                        omni.ui.Label("FPS: ", width=0, style={"color": 0xFFFFFFFF})
                        self.__status_fps = omni.ui.Label("", width=0)
                        omni.ui.Spacer(width=8)
                        omni.ui.Label("Render Res: ", width=0, style={"color": 0xFFFFFFFF})
                        self.__render_res = omni.ui.Label("", width=0)
                        omni.ui.Spacer(width=8)
                        omni.ui.Label("Output Res: ", width=0, style={"color": 0xFFFFFFFF})
                        self.__output_res = omni.ui.Label("", width=0)
                        # omni.ui.Spacer(width=8)
                        # omni.ui.Label("Action Map: ", width=0, style={"color": 0xFFFFFFFF})
                        # self.__status_action_map = omni.ui.Label("", width=0)
                        omni.ui.Spacer(width=8)
                        omni.ui.Label("Status: ", width=0, style={"color": 0xFFFFFFFF})
                        self.__status_message = omni.ui.Label("", width=0)
                        omni.ui.Spacer(width=8)
                        omni.ui.Button(
                            "",
                            spacing=10,
                            image_url=str(os.path.join(self.__icon_path, "exit.svg")),
                            image_width=20,
                            image_height=20,
                            width=0,
                            style=button_style,
                            clicked_fn=exit_fn,
                            tooltip="Exit XR Mode",
                        )
                omni.ui.Spacer()
            if self.__position_top:
                omni.ui.Spacer()
            else:
                omni.ui.Spacer(height=20)

    def build_ui(self):
        """
        Build the UI:
        This builds both pieces: error bar and status bar.
        """

        with omni.ui.VStack():
            self._build_error_bar()
            self._build_status_bar()

        self.update_ui()

    def update_ui(self):
        """
        Update the UI pieces and do not rebuild them.
        """

        # In case ui is no longer valid, exit
        if self.__status_bar is None or self.__error_bar is None:
            return

        xr_status_enabled = carb.settings.get_settings().get(XR_STATUS_ENABLED_PATH)
        if xr_status_enabled is None:
            xr_status_enabled = False

        xr_status_fullscreen = carb.settings.get_settings().get(XR_STATUS_FULLSCREEN_PATH)
        if xr_status_fullscreen is None:
            xr_status_fullscreen = False

        xr_enabled = XRCore.get_singleton().is_xr_enabled()
        error_message = carb.settings.get_settings().get(XR_STATUS_ERROR_MESSAGE_PATH)
        if error_message is None:
            error_message = ""

        # If there is an error message show it in the status bar
        if len(error_message) > 0:

            if self.__show_toast:
                # If error needs to be a toast, send it to the toast system
                post_viewport_message(self.__viewport_api, error_message)
            else:
                # Otherwise show error in status bar
                self.__error_message.text = error_message
                self.__show_error_count = self.__show_error_count + 1
                self.__show_error = True

            # Also log error in log for completeness
            carb.log_error(error_message)

            # Reset the message so it is shown only once for every time an error
            # is written
            carb.settings.get_settings().set(XR_STATUS_ERROR_MESSAGE_PATH, "")

        # Now the status bar part
        status_message = carb.settings.get_settings().get(XR_STATUS_MESSAGE_PATH)
        if status_message is None:
            status_message = ""

        status_action_map = carb.settings.get_settings().get(XR_STATUS_ACTIONMAP_PATH)
        if status_action_map is None:
            status_action_map = "None"

        render_res = carb.settings.get_settings().get(XR_STATUS_RENDER_RESOLUTION_PATH)
        if render_res is None:
            render_res = ""

        output_res = carb.settings.get_settings().get(XR_STATUS_OUTPUT_RESOLUTION_PATH)
        if output_res is None:
            output_res = ""

        status_fps = carb.settings.get_settings().get(XR_STATUS_FPS_PATH)
        if status_fps is None:
            status_fps = 0.0

        # Update which part of the status bar is visible: status part or error part
        self.__status_bar.visible = (xr_status_enabled or xr_status_fullscreen) and xr_enabled and not self.__show_error
        self.__error_bar.visible = self.__show_error

        # Write information into the the status bar
        self.__status_fps.text = "{:.1f}".format(status_fps)
        self.__render_res.text = render_res
        self.__output_res.text = output_res
        # self.__status_action_map.text = status_action_map
        self.__status_message.text = status_message

        if self.__show_error:
            # Error message will be removed after a certain amount of time
            self._close_on_wait(self.__show_error_count)

    def destroy(self):
        self.__root.clear()
        self.__root.destroy()
        self.__root = None

    @property
    def visible(self):
        return self.__root.visible

    @visible.setter
    def visible(self, value):
        self.__root.visible = value

    @property
    def categories(self):
        return ["xr"]

    @property
    def name(self):
        return "XR Status"
