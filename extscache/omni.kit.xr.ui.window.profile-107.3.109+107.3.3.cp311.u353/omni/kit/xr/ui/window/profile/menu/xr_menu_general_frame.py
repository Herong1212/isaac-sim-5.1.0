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


import pathlib

import carb
import omni.kit.app
import omni.ui as ui
from omni.kit.widget.settings import SettingType
from omni.kit.xr.core import XRWeakMethod
from omni.ui import color as cl

from ..ui.settings_frame import XRSettingsFrame

try:
    from omni.kit.xr.system.openxr import get_cloudxr_runtime_version

    CLOUDXR_RUNTIME_VERSION = get_cloudxr_runtime_version()
except ImportError:
    CLOUDXR_RUNTIME_VERSION = None

# =======================================================
# General VR Settings
# - System to use for communication, e.g. OpenVR, OpenXR, etc
# - Render Quality that controls rendering settings
# - Multiplier with resolution for VR system
# - Whether tooltips are shown in VR
# =======================================================


class XRMenuGeneralFrame(XRSettingsFrame):
    def build_ui(self):
        # Selected output plugin
        if self._config.get("show_selected_output_plugin", False):
            available_systems = self.get_available_systems()
            self.add_setting_combo(
                "Selected Output Plugin",
                self.get_persistent_path() + "system/display",
                available_systems,
                tooltip="System for communicating with HMD",
                has_reset=False,
            )

            # Add OpenXR runtime selection when OpenXR is selected
            self.add_rebuild_subscription(self.get_persistent_path() + "system/display")
            selected_system = carb.settings.get_settings().get(self.get_persistent_path() + "system/display")

            if selected_system == "OpenXR":
                if CLOUDXR_RUNTIME_VERSION is not None:
                    cloudxr_version_str = f"{CLOUDXR_RUNTIME_VERSION[0]}.{CLOUDXR_RUNTIME_VERSION[1]}"
                else:
                    cloudxr_version_str = "Unknown"

                runtime_options = {
                    "System OpenXR Runtime": "system",
                    f"CloudXR Runtime ({cloudxr_version_str})": "cloudxr",
                    "Custom": "custom",
                }

                # Add a subscription to rebuild the UI when the runtime changes
                rebuild_fn = XRWeakMethod(self._rebuild)
                self._subs.append(
                    omni.kit.app.SettingChangeSubscription(
                        "/persistent/xr/system/openxr/runtime", lambda *_: rebuild_fn()
                    )
                )

                self.add_setting_combo(
                    "OpenXR Runtime",
                    "/persistent/xr/system/openxr/runtime",
                    runtime_options,
                    tooltip="Select which OpenXR runtime to use",
                    has_reset=False,
                )

                # Add file picker for custom runtime path
                selected_runtime = carb.settings.get_settings().get("/persistent/xr/system/openxr/runtime")
                is_test = carb.settings.get_settings().get("/app/isTestRun")

                # Only show the file picker UI when custom option is selected
                if selected_runtime == "custom" and not is_test:
                    self.add_setting(
                        "ASSET",
                        "Custom Runtime Path",
                        "/persistent/xr/system/openxr/activeRuntimeJSON",
                        tooltip="Path to the custom OpenXR runtime JSON file",
                        has_reset=False,
                    )

        render_quality_items = self._config.get("render_quality_items", [])
        self.add_setting_combo(
            "Quality Preset",
            self.get_persistent_path() + "renderQuality",
            render_quality_items,
            tooltip="Switch between different render settings for better quality or performance",
        )

        if self._profile.get_name() == "vr":
            self.add_setting_combo(
                "Dominant Hand",
                self.get_non_profile_persistent_path() + "tools/dominantHand",
                {"Right": "right", "Left": "left"},
                tooltip="Set dominant hand for controller layout",
                has_reset=False,
            )

        if self._config.get("show_resolution_multiplier", False):
            ui.Spacer(height=15)

            quadview_active = self.is_quadview_active()

            self.add_rebuild_subscription(self.get_persistent_path() + "quadview/foveation/mode")
            self.add_rebuild_subscription("xr/system/openxr/xcr/capture/enabled")
            self.add_rebuild_subscription("xr/system/openxr/xcr/capture/filepath")

            quadview_mode = carb.settings.get_settings().get(self.get_persistent_path() + "quadview/foveation/mode")

            if quadview_active is True and (quadview_mode != "stereo_warped_to_quadview"):
                self.add_setting(
                    SettingType.FLOAT,
                    "Background Resolution Multiplier",
                    self.get_persistent_path() + "quadview/render/background/resolutionMultiplier",
                    0.1,
                    2.0,
                    0.01,
                    format="%.2f",
                    tooltip="Multiplier that controls the size of the background render buffer",
                )

                self.add_setting(
                    SettingType.FLOAT,
                    "Inset Resolution Multiplier",
                    self.get_persistent_path() + "quadview/render/inset/resolutionMultiplier",
                    0.1,
                    2.0,
                    0.01,
                    format="%.2f",
                    tooltip="Multiplier that controls the size of the inset render buffer",
                )

            if (quadview_active is False) or (quadview_mode == "stereo_warped_to_quadview"):
                self.add_setting(
                    SettingType.FLOAT,
                    "Resolution Multiplier",
                    self.get_persistent_path() + "render/resolutionMultiplier",
                    0.1,
                    2.0,
                    0.01,
                    format="%.2f",
                    tooltip="Multiplier that controls the size of the render buffer",
                )

        if self._config.get("show_tooltips", False):
            ui.Spacer(height=15)

            self.add_setting(
                SettingType.BOOL,
                "Show Tooltips",
                self.get_persistent_path() + "tooltips/visible",
                tooltip="Enable this to show tooltips on the VR controllers",
            )

            self.add_setting(
                SettingType.BOOL,
                "Show Controllers",
                self.get_persistent_path() + "controllers/visible",
                tooltip="Enable this to show vr controllers",
            )

        self.add_setting(
            SettingType.BOOL,
            "Enable Input Smoothing",
            self.get_persistent_path() + "inputSmoothing/enabled",
            tooltip="Enable smoothing of device poses",
        )

        self.add_setting(
            SettingType.FLOAT,
            "Input Smoothing Factor",
            self.get_persistent_path() + "inputSmoothing/factor",
            0.0,
            1.0,
            0.01,
            tooltip="Input device smoothing factor(0.0 = no smoothing, 1.0 = max smoothing)",
        )
