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
from omni.kit.xr.core import XRWeakMethod

from ..ui.settings_frame import XRSettingsFrame

# =======================================================
# Menu component describing RTX matte object used in XR
# =======================================================


class XRMenuMatteObjectFrame(XRSettingsFrame):

    _matte_object_mode_items = {
        "Disabled": "disabled",
        "Enabled": "enabled",
        "Standard Shadow Catcher": "std_shadow_catcher",
        "Ambient Occlusion Shadow Catcher": "ao_shadow_catcher",
    }

    _disable_rebuild = False

    def get_frame_name(self):
        return "Matte Object"

    def build_ui(self):
        self.add_setting(
            SettingType.BOOL,
            "Override Stage",
            self.get_persistent_path() + "matteObject/overrideStage",
            tooltip="Choose whether these matte object settings override the stage settings or simply mirror them.",
        )
        self.add_rebuild_subscription(self.get_persistent_path() + "matteObject/overrideStage")
        override_stage = carb.settings.get_settings().get(self.get_persistent_path() + "matteObject/overrideStage")

        ui.Spacer(height=2)

        self.add_setting_combo(
            "Matte Object Mode",
            self.get_persistent_path() + "matteObject/mode",
            self._matte_object_mode_items,
            XRWeakMethod(self._mode_callback),
            tooltip="Matte object mode to use in the XR session.",
        )

        # If we are not overriding the stage settings we need the stage settings to drive this UI, although making
        # changes to the UI will set the appropriate RTX settings
        if not override_stage:
            # This UI might be driven by the Post Processing Matte Object Render Settings, so we get
            # the relevant setting values now in case we want to use them later
            rtx_matte_object_enabled = carb.settings.get_settings().get("/rtx/matteObject/enabled")
            rtx_shadow_catcher_enabled = carb.settings.get_settings().get("/rtx/post/matteObject/enableShadowCatcher")
            rtx_ao_shadow_catcher_enabled = carb.settings.get_settings().get(
                "/rtx/matteObject/enableAmbientShadowCatcher"
            )

            self.add_rebuild_subscription("/rtx/matteObject/enabled")
            self.add_rebuild_subscription("/rtx/post/matteObject/enableShadowCatcher")
            self.add_rebuild_subscription("/rtx/matteObject/enableAmbientShadowCatcher")

            # All four possibilities are covered once and every if else branch has a unique outcome
            if rtx_matte_object_enabled:
                if rtx_ao_shadow_catcher_enabled:
                    carb.settings.get_settings().set(
                        self.get_persistent_path() + "matteObject/mode", "ao_shadow_catcher"
                    )
                else:
                    if rtx_shadow_catcher_enabled:
                        carb.settings.get_settings().set(
                            self.get_persistent_path() + "matteObject/mode", "std_shadow_catcher"
                        )
                    else:
                        carb.settings.get_settings().set(self.get_persistent_path() + "matteObject/mode", "enabled")
            else:
                carb.settings.get_settings().set(self.get_persistent_path() + "matteObject/mode", "disabled")
        else:
            self.add_rebuild_subscription(self.get_persistent_path() + "matteObject/mode")

        matte_object_mode = carb.settings.get_settings().get(self.get_persistent_path() + "matteObject/mode")

        if matte_object_mode == "ao_shadow_catcher":
            self.add_setting(
                SettingType.FLOAT,
                "Ease Factor",
                self.get_persistent_path() + "matteObject/ambientShadowCatcherFactor",
                0.01,
                5.0,
                0.01,
                tooltip="The amount to modulate the ambient occlusion strength, higher means darker.",
                callback=XRWeakMethod(self._ao_factor_callback),
            )

            self.add_setting(
                SettingType.FLOAT,
                "Ray Length (cm)",
                self.get_persistent_path() + "matteObject/aoRayLength",
                0.0,
                2000.0,
                1.0,
                tooltip="The length of ambient occlusion rays emitted from intersection points.",
                callback=XRWeakMethod(self._ao_ray_length_callback),
            )

            if not override_stage:
                rtx_ao_shadow_catcher_factor = carb.settings.get_settings().get_as_float(
                    "/rtx/matteObject/ambientShadowCatcherFactor"
                )
                carb.settings.get_settings().set_float(
                    self.get_persistent_path() + "matteObject/ambientShadowCatcherFactor", rtx_ao_shadow_catcher_factor
                )
                self.add_rebuild_subscription("/rtx/matteObject/ambientShadowCatcherFactor")

                rtx_ao_ray_length = carb.settings.get_settings().get_as_float("/rtx/ambientOcclusion/rayLength")
                carb.settings.get_settings().set_float(
                    self.get_persistent_path() + "matteObject/aoRayLength", rtx_ao_ray_length
                )
                self.add_rebuild_subscription("/rtx/ambientOcclusion/rayLength")

    def _mode_callback(self):
        override_stage = carb.settings.get_settings().get(self.get_persistent_path() + "matteObject/overrideStage")

        if not override_stage:
            # Only change what needs to be changed, don't alter the null space of the options
            match carb.settings.get_settings().get(self.get_persistent_path() + "matteObject/mode"):
                case "enabled":
                    if carb.settings.get_settings().get("/rtx/matteObject/enabled") == False:
                        carb.settings.get_settings().set("/rtx/matteObject/enabled", True)
                    if carb.settings.get_settings().get("/rtx/post/matteObject/enableShadowCatcher") == True:
                        carb.settings.get_settings().set("/rtx/post/matteObject/enableShadowCatcher", False)
                    if carb.settings.get_settings().get("/rtx/matteObject/enableAmbientShadowCatcher") == True:
                        carb.settings.get_settings().set("/rtx/matteObject/enableAmbientShadowCatcher", False)
                case "disabled":
                    if carb.settings.get_settings().get("/rtx/matteObject/enabled") == True:
                        carb.settings.get_settings().set("/rtx/matteObject/enabled", False)
                case "std_shadow_catcher":
                    if carb.settings.get_settings().get("/rtx/matteObject/enabled") == False:
                        carb.settings.get_settings().set("/rtx/matteObject/enabled", True)
                    if carb.settings.get_settings().get("/rtx/post/matteObject/enableShadowCatcher") == False:
                        carb.settings.get_settings().set("/rtx/post/matteObject/enableShadowCatcher", True)
                    if carb.settings.get_settings().get("/rtx/matteObject/enableAmbientShadowCatcher") == True:
                        carb.settings.get_settings().set("/rtx/matteObject/enableAmbientShadowCatcher", False)
                case "ao_shadow_catcher":
                    if carb.settings.get_settings().get("/rtx/matteObject/enabled") == False:
                        carb.settings.get_settings().set("/rtx/matteObject/enabled", True)
                    if carb.settings.get_settings().get("/rtx/matteObject/enableAmbientShadowCatcher") == False:
                        carb.settings.get_settings().set("/rtx/matteObject/enableAmbientShadowCatcher", True)

    def _ao_factor_callback(self):
        override_stage = carb.settings.get_settings().get(self.get_persistent_path() + "matteObject/overrideStage")

        if not override_stage:
            ao_shadow_catcher_factor = carb.settings.get_settings().get_as_float(
                self.get_persistent_path() + "matteObject/ambientShadowCatcherFactor"
            )

            self._disable_rebuild = True

            if (
                carb.settings.get_settings().get_as_float("/rtx/matteObject/ambientShadowCatcherFactor")
                != ao_shadow_catcher_factor
            ):
                carb.settings.get_settings().set_float(
                    "/rtx/matteObject/ambientShadowCatcherFactor", ao_shadow_catcher_factor
                )

            self._disable_rebuild = False

    def _ao_ray_length_callback(self):
        override_stage = carb.settings.get_settings().get(self.get_persistent_path() + "matteObject/overrideStage")

        if not override_stage:
            ao_ray_length = carb.settings.get_settings().get_as_float(
                self.get_persistent_path() + "matteObject/aoRayLength"
            )

            self._disable_rebuild = True

            if carb.settings.get_settings().get_as_float("/rtx/ambientOcclusion/rayLength") != ao_ray_length:
                carb.settings.get_settings().set_float("/rtx/ambientOcclusion/rayLength", ao_ray_length)

            self._disable_rebuild = False

    def _rebuild(self):
        if self._disable_rebuild:
            return

        super()._rebuild()
