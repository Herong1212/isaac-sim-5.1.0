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
from omni.kit.xr.core import XRCore, XRCoreEventType, XRWeakMethod

from ..ui.settings_frame import XRSettingsFrame

# =======================================================
# Menu component describing XRDepth used in XR
#
# Contains:
# - XRDepth
# - XRDepthHitType
# - XRDepthRefraction
# - XRDepthRefractionMask
# - XRDepthRefractionMaskMaxCurvature
# - XRDepthRefractionMaskMaxRefractionAngle (Degrees)
# =======================================================


class XRMenuXRDepthFrame(XRSettingsFrame):
    def get_frame_name(self):
        return "Depth"

    def build_ui(self):
        # Depending on what render mode we using, different depth types are available
        render_mode_path = "/rtx/rendermode"
        self.add_rebuild_subscription(render_mode_path)
        render_mode = carb.settings.get_settings().get(render_mode_path)

        if render_mode == "RaytracedLighting":
            default_depth_aov = "GBufferDepth"  # For RT we'll stick with 'GBufferDepth' as the default for now
            depth_types = [
                "XRDepth",
                "GBufferDepth",
                "StableDepth",
                "Depth",
            ]
        else:
            default_depth_aov = "XRDepth"  # 'Depth' AOV isn't fully supported with MGPU, so use 'XRDepth' by default
            depth_types = [
                "XRDepth",
                "Depth",
            ]

        # Make sure the current depth aov is one of the supported values for the current renderer
        depth_aov_path = "/xr/depth/aov"
        carb.settings.get_settings().set("/defaults" + depth_aov_path, default_depth_aov)
        depth_aov = carb.settings.get_settings().get(depth_aov_path)
        if depth_aov not in depth_types:
            carb.log_warn(
                f"[XR] Depth AOV {depth_aov} is not supported by the current renderer mode {render_mode}, defaulting to {default_depth_aov}"
            )
            depth_aov = default_depth_aov
            carb.settings.get_settings().set(depth_aov_path, depth_aov)
        self._depth_aov_combo = self.add_setting_combo(
            "Depth AOV",
            depth_aov_path,
            depth_types,
            XRWeakMethod(self._rebuild_callback),
            tooltip="Select the type of depth to use in XR.",
        )

        # Listen out to XR enable/disable events so that we can disable the AOV combo-box when XR is enabled
        evstream = XRCore.get_singleton().get_message_bus()
        self._subs.append(
            evstream.create_subscription_to_pop_by_type(
                carb.events.type_from_string("xr.update"), XRWeakMethod(self.on_xr_update)
            )
        )
        self._subs.append(
            evstream.create_subscription_to_pop_by_type(XRCoreEventType.xr_disabled, XRWeakMethod(self.on_xr_disable))
        )

        # If we are not using XRDepth, we don't need to expose the XRDepth settings
        if depth_aov != "XRDepth":
            return

        if render_mode == "RaytracedLighting":
            depth_hit_types = [
                "Opaque",
                "First",
                "Refracted",
            ]
        else:
            depth_hit_types = [
                "Opaque",
                "First",
            ]

        depth_hit_type_path = "/xr/xrdepth/hitType"

        carb.settings.get_settings().set("/defaults" + depth_hit_type_path, "Opaque")
        depth_hit_type = carb.settings.get_settings().get(depth_hit_type_path)
        if depth_hit_type not in depth_hit_types:
            carb.log_warn(f"[XR] Depth hit type {depth_hit_type} is not supported, defaulting to Opaque")
            depth_hit_type = "Opaque"
            carb.settings.get_settings().set(depth_hit_type_path, depth_hit_type)
        self.add_setting_combo(
            "Depth Hit Type",
            depth_hit_type_path,
            depth_hit_types,
            XRWeakMethod(self._rebuild_callback),
            tooltip="Select the type of depth hit to use in XR.",
        )

        depth_hit_type_rtx_path = "/rtx" + depth_hit_type_path

        depth_hit_type_int = 0 if depth_hit_type == "Opaque" else 1 if depth_hit_type == "First" else 2
        carb.settings.get_settings().set_int(depth_hit_type_rtx_path, depth_hit_type_int)

        # If hit type is first hit, we don't need to expose the any XRDepth settings
        if depth_hit_type == "First" or render_mode != "RaytracedLighting":
            return

        if depth_hit_type == "Refracted":
            self.add_rebuild_subscription("/rtx/xr/xrdepth/refraction/mask/enabled")

            # Add default values here since these settings don't quite fit into the standard KitXR format
            carb.settings.get_settings().set_bool("/defaults/rtx/xr/xrdepth/refraction/mask/enabled", True)
            carb.settings.get_settings().set_float("/defaults/rtx/xr/xrdepth/refraction/mask/maxCurvature", 0.01)
            carb.settings.get_settings().set_float("/defaults/rtx/xr/xrdepth/refraction/mask/maxRefractionAngle", 1.0)

            self.add_setting(
                SettingType.BOOL,
                "Refraction Mask",
                "/rtx/xr/xrdepth/refraction/mask/enabled",
                tooltip="Use geometric information from the scene to mask areas of the image that result in poor depth values when using refracted depth rays.  For these parts of the image fallback to non-refracted depth rays.",
            )
            ui.Spacer(height=1)

            xrDepthRefractionMaskEnabled = carb.settings.get_settings().get_as_bool(
                "/rtx/xr/xrdepth/refraction/mask/enabled"
            )

            if xrDepthRefractionMaskEnabled:
                self.add_setting(
                    SettingType.FLOAT,
                    "Max Curvature",
                    "/rtx/xr/xrdepth/refraction/mask/maxCurvature",
                    0.0,
                    1.0,
                    0.001,
                    tooltip="When computing XRDepth for refracted depth rays, fallback to non-refracted depth rays if the normal curvature of the first hit exceeds this amount.",
                )

                self.add_setting(
                    SettingType.FLOAT,
                    "Max Refraction Angle (Degrees)",
                    "/rtx/xr/xrdepth/refraction/mask/maxRefractionAngle",
                    0.0,
                    60,
                    0.1,
                    tooltip="When computing XRDepth for refracted depth rays, fallback to non-refracted depth rays if the difference in angle between the rays entering and exiting the translucent object differ by more than this amount.",
                )

    def _rebuild_callback(self):
        self._rebuild()

    def on_xr_update(self, event):
        self._depth_aov_combo.enabled = False

        # Need to disable visibility for the reset button since setting enable to false does not disable mouse clicks!
        self._depth_aov_combo.model._reset_button.visible = False

    def on_xr_disable(self, event):
        self._depth_aov_combo.enabled = True
        self._depth_aov_combo.model._reset_button.visible = True
