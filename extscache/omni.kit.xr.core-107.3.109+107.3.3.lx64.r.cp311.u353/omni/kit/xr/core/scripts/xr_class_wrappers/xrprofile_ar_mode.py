# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Use these at your own risk, and forward-compatability is not supported

import carb


class XRProfileARMode:
    def __init__(self):
        self.__need_ar_unset = False
        self.__ar_mode = False

    def get_ar_mode(self) -> bool:
        """
        This function gets current AR mode.
        """
        return self.__ar_mode

    def set_ar_mode(self, ar_mode, profile) -> None:
        """
        This function sets AR mode.
        """

        if ar_mode:
            self.__ar_mode = True

            if profile.is_enabled():
                self.update_settings_ar(profile)
        else:
            self.reset_settings_ar()
            self.__ar_mode = False

    def update_settings_ar(self, profile) -> None:
        """
        Update all settings needed for AR
        """

        if self.__ar_mode:
            settings = carb.settings.get_settings()

            rtx_matte_object_enabled = settings.get("/rtx/matteObject/enabled")
            rtx_shadow_catcher_enabled = settings.get("/rtx/post/matteObject/enableShadowCatcher")
            rtx_ao_shadow_catcher_enabled = settings.get("/rtx/matteObject/enableAmbientShadowCatcher")
            ambient_shadow_catcher_factor = settings.get("/rtx/matteObject/ambientShadowCatcherFactor")
            ao_ray_length = settings.get("/rtx/ambientOcclusion/rayLength")

            match settings.get(profile.get_persistent_path() + "matteObject/mode"):
                case "enabled":
                    rtx_matte_object_enabled = True
                    rtx_shadow_catcher_enabled = False
                    rtx_ao_shadow_catcher_enabled = False
                case "disabled":
                    rtx_matte_object_enabled = False
                case "std_shadow_catcher":
                    rtx_matte_object_enabled = True
                    rtx_shadow_catcher_enabled = True
                    rtx_ao_shadow_catcher_enabled = False
                case "ao_shadow_catcher":
                    rtx_matte_object_enabled = True
                    rtx_ao_shadow_catcher_enabled = True
                    ambient_shadow_catcher_factor = settings.get_as_float(
                        profile.get_persistent_path() + "matteObject/ambientShadowCatcherFactor"
                    )
                    ao_ray_length = settings.get_as_float(profile.get_persistent_path() + "matteObject/aoRayLength")

            self.__need_ar_unset = True
            ar_render_settings_to_set = {
                "/rtx/post/backgroundZeroAlpha/enabled": True,
                "/rtx/post/backgroundZeroAlpha/backgroundComposite": False,
                "/rtx/post/backgroundZeroAlpha/outputAlphaInComposite": True,
                "/rtx/post/backgroundZeroAlpha/blackBackgroundInComposite": True,
                "/rtx/material/translucencyAsOpacity": True,
                "/rtx/post/lensFlares/enabled": False,
                "/rtx/post/motionblur/enabled": False,
                "/rtx/matteObject/enabled": rtx_matte_object_enabled,
                "/rtx/post/matteObject/enableShadowCatcher": rtx_shadow_catcher_enabled,
                "/rtx/matteObject/enableAmbientShadowCatcher": rtx_ao_shadow_catcher_enabled,
                "/rtx/matteObject/ambientShadowCatcherFactor": ambient_shadow_catcher_factor,
                "/rtx/ambientOcclusion/rayLength": ao_ray_length,
            }

            self.previous_ar_render_settings_states = {}
            for setting_path, value in ar_render_settings_to_set.items():
                self.previous_ar_render_settings_states[setting_path] = settings.get(setting_path)
                settings.set(setting_path, value)

    def reset_settings_ar(self) -> None:
        """
        Revert settings set when entered AR Mode
        """
        if self.__ar_mode and self.__need_ar_unset:
            self.__need_ar_unset = False
            settings = carb.settings.get_settings()
            for setting_path, value in self.previous_ar_render_settings_states.items():
                settings.set(setting_path, value)
