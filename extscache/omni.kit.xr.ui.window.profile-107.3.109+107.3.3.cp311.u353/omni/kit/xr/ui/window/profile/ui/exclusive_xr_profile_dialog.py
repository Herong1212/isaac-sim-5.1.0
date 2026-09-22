# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui
from omni.kit.xr.core import XRCore, XRWeakMethod


class XRExclusiveProfileDialog:
    """
    Dialog window is used to indicate that already XR profile is enabled, when user tries to enable another XR profile, without explicitly stopping the previous one.
    """

    DIALOG_TITLE = "XR Plugin Active"
    DIALOG_TEXT = (
        "An XR plugin is already running. Simultaneous XR plugins are not currently supported. "
        " Would you like to stop the current running plugin and start this one instead?"
    )

    def __init__(self, start_profile_fn):
        self.__profile_window = None
        self.__start_profile_fn = XRWeakMethod(start_profile_fn)
        self._create_dialog_window()

    def __del__(self):
        self.destroy()

    def destroy(self):

        if self.__profile_window is not None:
            self.__profile_window.destroy()
            self.__profile_window = None

    def handle_start_xr_profile(self) -> None:
        """
        If already XR is enabled, we show dialog (before starting other XR profile) to inform user that other XR profile is enabled.
        Otherwise, we start XR profile directly and do not show any dialog window.
        """

        is_xr_enabled = XRCore.get_singleton().is_xr_enabled()
        if is_xr_enabled:
            self._show_dialog()
        else:
            self.__start_profile_fn()

    def _start_profile_and_hide_dialog(self) -> None:
        self._hide_dialog()
        self.__start_profile_fn()

    def _show_dialog(self) -> None:
        self.__profile_window.visible = True

    def _hide_dialog(self) -> None:
        self.__profile_window.visible = False

    def _create_dialog_window(self) -> None:

        self.__profile_window = omni.ui.Window(
            self.DIALOG_TITLE, visible=False, height=0, dockPreference=omni.ui.DockPreference.DISABLED, auto_resize=True
        )

        self.__profile_window.flags = (
            omni.ui.WINDOW_FLAGS_NO_COLLAPSE
            | omni.ui.WINDOW_FLAGS_NO_RESIZE
            | omni.ui.WINDOW_FLAGS_NO_SCROLLBAR
            | omni.ui.WINDOW_FLAGS_MODAL
        )

        # Add information text into modal overlay window
        with self.__profile_window.frame:
            with omni.ui.VStack(width=500):
                omni.ui.Spacer(height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Label(
                        self.DIALOG_TEXT,
                        alignment=omni.ui.Alignment.CENTER,
                        word_wrap=True,
                        style={"font_size": 14},
                    )
                omni.ui.Spacer(height=10)
                with omni.ui.HStack(height=0):
                    omni.ui.Spacer(height=10)
                    omni.ui.Button("Ok", clicked_fn=self._start_profile_and_hide_dialog, width=150, height=24)
                    omni.ui.Button("Cancel", clicked_fn=self._hide_dialog, width=150, height=24)
                    omni.ui.Spacer(height=10)
