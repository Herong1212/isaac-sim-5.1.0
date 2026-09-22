# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

import platform
from functools import partial

import carb
import omni.ui as ui
from omni.kit.widget.settings import SettingType
from omni.kit.xr.core.recorder import get_xcr_capture_filepath, on_capture_button_clicked
from omni.ui import color as cl

from ..ui.settings_frame import XRSettingsFrame
from .xr_menu_openxr_utils import is_xcr_capture_layer_requested


class XRMenuXCRFrame(XRSettingsFrame):
    capture_layer_path_setting = "/xr/system/openxr/xcr/capture/enabled"
    replay_enabled_path_setting = "/xr/system/openxr/xcr/replay/enabled"
    replay_file_path_setting = "/xr/system/openxr/xcr/replay/replayFile"

    def _get_current_system(self) -> str:
        return carb.settings.get_settings().get(self.get_persistent_path() + "system/display")

    def get_frame_name(self):
        return "XCR: Capture & Replay"

    def build_ui(self):
        carb_setting = carb.settings.get_settings()
        is_capture_layer_selected = carb_setting.get(self.capture_layer_path_setting)
        is_replay_selected = carb_setting.get(self.replay_enabled_path_setting)
        default_capture_directory = get_xcr_capture_filepath()

        self.add_rebuild_subscription(self.capture_layer_path_setting)
        self.add_rebuild_subscription(self.replay_enabled_path_setting)
        ui.Label(
            "Capture",
            alignment=ui.Alignment.LEFT_CENTER,
            style={"font_size": 15.0, "color": 0xFFFFFFFF},
        )

        if is_xcr_capture_layer_requested():
            ui.Spacer(height=5)
            self.add_setting(
                SettingType.BOOL,
                "Enable OpenXR session capture",
                self.capture_layer_path_setting,
                tooltip="Enable capture of all OpenXR sessions",
                has_reset=False,
            )

            if is_capture_layer_selected:
                msg = (
                    f"OpenXR sessions will be captured to:\n{default_capture_directory}\n"
                    "The file will be named with timestamp (e.g., 03_03_15_10_55_655.bin)\n"
                    "Create OpenXR session by starting profile first, then use buttons below to start/stop capture"
                )
                ui.Label(msg, style={"font_size": 15})

                def swap_start_and_stop(is_capture_started: bool):
                    self.start_button.enabled, self.stop_button.enabled = not is_capture_started, is_capture_started

                self.start_button = ui.Button(
                    "Start capture",
                    clicked_fn=lambda: (on_capture_button_clicked(True, self), swap_start_and_stop(True)),
                    width=120,
                    height=30,
                    enabled=carb_setting.get(self.get_profile().get_non_persistent_path() + "enabled"),
                )
                self.stop_button = ui.Button(
                    "Stop capture",
                    clicked_fn=lambda: (on_capture_button_clicked(False, self), swap_start_and_stop(False)),
                    width=120,
                    height=30,
                    enabled=carb_setting.get(self.get_profile().get_non_persistent_path() + "enabled"),
                )
        else:
            ui.Label(
                "Capture Layer is not present in Registry (Windows) or environment variable (Linux). Refer to README.md to install it.",
                style={"font_size": 13, "color": cl.red},
            )

        ui.Spacer(height=5)
        ui.Label(
            "Replay",
            alignment=ui.Alignment.LEFT_CENTER,
            style={"font_size": 15.0, "color": 0xFFFFFFFF},
        )
        ui.Spacer(height=5)
        self.add_setting(
            SettingType.BOOL,
            "Enable OpenXR session replay",
            self.replay_enabled_path_setting,
            tooltip="Enable replay of OpenXR sessions",
            has_reset=False,
        )

        if is_replay_selected:
            msg = "The selected replay file will automatically start when this profile is activated"
            self.add_setting(
                "ASSET",
                "Select a replay file",
                self.replay_file_path_setting,
                tooltip=msg,
            )
            ui.Label(msg, style={"font_size": 15})
