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

import carb.settings
import omni.ui as ui
from omni.kit.widget.settings import SettingType

from ..ui.settings_frame import XRSettingsFrame

# =======================================================
# Menu component describing which render settings should
# be overridden
#
# Contains:
# - Quality selector for render settings
# - Foveation mode
# - Resolution settings for different foveation options
# - Foveation denoiser settings
# =======================================================


class XRMenuFoveationSettingsFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Foveation Settings"

    def build_ui(self):
        self.add_rebuild_subscription(self.get_persistent_path() + "foveation/mode")
        self.add_rebuild_subscription(self.get_non_persistent_path() + "foveation/showArea")
        self.add_rebuild_subscription(self.get_persistent_path() + "quadview/foveation/mode")

        quadview_active = self.is_quadview_active()

        self.add_setting(
            SettingType.BOOL,
            "Enable Quadview if Available",
            self.get_persistent_path() + "quadview/enabled",
            tooltip="Enable quadview rendering if option is available",
        )

        if quadview_active is True:
            quadview_mode_items = {
                "Render 4 views": "render_quadview",
                "Render 4 warped views": "render_warped_quadview",
                "Render 2 warped views": "stereo_warped_to_quadview",
            }

            self.add_setting_combo(
                "Quadview Foveation Mode",
                self.get_persistent_path() + "quadview/foveation/mode",
                quadview_mode_items,
            )

            ui.Spacer(height=5)
            ui.Line()
            ui.Spacer(height=5)

            self.add_setting(
                SettingType.BOOL,
                "Highlight High Resolution Area",
                self.get_non_persistent_path() + "foveation/showArea",
                tooltip="Whether to highlight the high resolution area in the rendering.",
            )
            showArea = carb.settings.get_settings().get(self.get_non_persistent_path() + "foveation/showArea")

            if showArea:
                self.add_setting(
                    SettingType.FLOAT,
                    "Brightness - Non-foveated Area",
                    self.get_persistent_path() + "foveation/dimFactor",
                    0,
                    1,
                    0.01,
                    tooltip="Dim factor for surroundings to highlight where image is foveated.",
                )

            foveation_mode = carb.settings.get_settings().get(self.get_persistent_path() + "quadview/foveation/mode")

            if foveation_mode != "render_quadview":
                if not showArea:
                    self.add_setting(
                        SettingType.BOOL,
                        "Show Warped Image",
                        self.get_non_persistent_path() + "foveation/showWarp",
                        tooltip="Do not unwarp image on desktop to illustrate what actually is rendered in warped foveation mode.",
                    )

            if foveation_mode == "render_warped_quadview":
                ui.Spacer(height=15)
                ui.Line()
                ui.Spacer(height=5)

                self.add_setting(
                    SettingType.FLOAT,
                    "Background Pct of Full Res",
                    self.get_persistent_path() + "quadview/background/foveation/warped/resolutionMultiplier",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The resolution multiplier indicating the reduction in pixels rendered in warped foveation mode for background image.",
                )
                self.add_setting(
                    SettingType.FLOAT,
                    "Background Size of Unwarped Area",
                    self.get_persistent_path() + "quadview/background/foveation/warped/insetSize",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The percentage of the pixels that is dedicated to the high resolution area for background image.",
                )

                self.add_setting(
                    SettingType.FLOAT,
                    "Inset Pct of Full Res",
                    self.get_persistent_path() + "quadview/inset/foveation/warped/resolutionMultiplier",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The resolution multiplier indicating the reduction in pixels rendered in warped foveation mode for inset image.",
                )
                self.add_setting(
                    SettingType.FLOAT,
                    "Inset Size of Unwarped Area",
                    self.get_persistent_path() + "quadview/inset/foveation/warped/insetSize",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The percentage of the pixels that is dedicated to the high resolution area for inset image.",
                )

            if foveation_mode == "stereo_warped_to_quadview":
                ui.Spacer(height=15)
                ui.Line()
                ui.Spacer(height=5)

                self.add_setting(
                    SettingType.FLOAT,
                    "Percentage of Full Resolution",
                    self.get_persistent_path() + "quadview/stereo/foveation/warped/resolutionMultiplier",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The resolution multiplier indicating the reduction in pixels rendered in warped foveation mode.",
                )
                self.add_setting(
                    SettingType.FLOAT,
                    "Relative Size of Unwarped Area",
                    self.get_persistent_path() + "quadview/stereo/foveation/warped/insetSize",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The percentage of the pixels that is dedicated to the high resolution area.",
                )

        else:
            foveation_mode = carb.settings.get_settings().get(self.get_persistent_path() + "foveation/mode")

            foveation_mode_items = {
                "None": "none",
                "High Resolution Inset": "inset",
                "Warped Foveation": "warped",
            }
            self.add_setting_combo(
                "Foveation Mode",
                self.get_persistent_path() + "foveation/mode",
                foveation_mode_items,
                tooltip="Foveation modes reduce render quality outside of the fovea and generally improve rendering speed.",
            )

            # show high-res/foveated area
            if foveation_mode != "none":
                ui.Spacer(height=5)
                ui.Line()
                ui.Spacer(height=5)

                self.add_setting(
                    SettingType.BOOL,
                    "Highlight High Resolution Area",
                    self.get_non_persistent_path() + "foveation/showArea",
                    tooltip="Whether to highlight the high resolution area in the rendering.",
                )

                showArea = carb.settings.get_settings().get(self.get_non_persistent_path() + "foveation/showArea")

                if showArea:
                    self.add_setting(
                        SettingType.FLOAT,
                        "Brightness - Non-foveated Area",
                        self.get_persistent_path() + "foveation/dimFactor",
                        0,
                        1,
                        0.01,
                        tooltip="Dim factor for surroundings to highlight where image is foveated.",
                    )
                elif foveation_mode == "warped":
                    # foveation percentages
                    self.add_setting(
                        SettingType.BOOL,
                        "Show Warped Image",
                        self.get_non_persistent_path() + "foveation/showWarp",
                        tooltip="Do not unwarp image on desktop to illustrate what actually is rendered in warped foveation mode.",
                    )

            # handle warped foveation
            if foveation_mode == "warped":

                ui.Spacer(height=15)
                ui.Line()
                ui.Spacer(height=5)

                self.add_setting(
                    SettingType.FLOAT,
                    "Percentage of Full Resolution",
                    self.get_persistent_path() + "foveation/warped/resolutionMultiplier",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The resolution multiplier indicating the reduction in pixels rendered in warped foveation mode.",
                )
                self.add_setting(
                    SettingType.FLOAT,
                    "Relative Size of Unwarped Area",
                    self.get_persistent_path() + "foveation/warped/insetSize",
                    0.05,
                    0.95,
                    0.01,
                    format="%.2f",
                    tooltip="The percentage of the pixels that is dedicated to the high resolution area.",
                )

            # handle inset foveation
            if foveation_mode == "inset":
                ui.Spacer(height=15)
                ui.Line()
                ui.Spacer(height=5)

                self.add_setting(
                    SettingType.FLOAT,
                    "Percentage at Full Resolution",
                    self.get_persistent_path() + "foveation/inset/fullResSize",
                    0.1,
                    1,
                    0.01,
                    format="%.2f",
                    tooltip="Percentage of screen that is rendered at full resolution.",
                )
                self.add_setting(
                    SettingType.FLOAT,
                    "Background Resolution Factor",
                    self.get_persistent_path() + "foveation/inset/backgroundFactor",
                    0.1,
                    1,
                    0.01,
                    format="%.2f",
                    tooltip="Resolution multiplier to determine background resolution.",
                )

                self.add_setting(
                    SettingType.FLOAT,
                    "Horizontal Offset",
                    self.get_persistent_path() + "foveation/inset/horizontalOffset",
                    -0.5,
                    0.5,
                    0.01,
                    format="%.2f",
                    tooltip="Horizontal offset of high resolution area from center of the display.",
                )
                self.add_setting(
                    SettingType.FLOAT,
                    "Vertical Offset",
                    self.get_persistent_path() + "foveation/inset/verticalOffset",
                    -0.5,
                    0.5,
                    0.01,
                    format="%.2f",
                    tooltip="Vertical offset of high resolution area from center of the display.",
                )
