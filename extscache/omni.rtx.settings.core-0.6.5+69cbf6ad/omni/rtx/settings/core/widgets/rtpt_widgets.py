# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.ui as ui
import omni.kit.app
import carb.settings
import math
from omni.kit.widget.settings import SettingType
from omni.rtx.window.settings.rtx_settings_stack import RTXSettingsStack
from omni.rtx.window.settings.settings_collection_frame import SettingsCollectionFrame
from .rt_widgets import DLSSSettingsFrame
from .rt_widgets import SubsurfaceScatteringSettingsFrame
from .rt_widgets import GlobalVolumetricEffectsSettingsFrame
from .pt_widgets import AOVSettingsFrame
from .pt_widgets import MultiMatteSettingsFrame
from .pt_widgets import MultiGPUSettingsFrame

class EcoMode(SettingsCollectionFrame):
    """ ECO Mode """
    def _frame_setting_path(self):
        return "/rtx/ecoMode/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.INT, "Stop Rendering After This Many Frames Without Changes", "/rtx/ecoMode/maxFramesWithoutChange", 0, 500)
 
class SamplingAndCachingSettingsFrame(SettingsCollectionFrame):
    """ Sampling & Caching """
    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Caching", "/rtx/rtpt/cached/enabled", tooltip="\nEnables caching path-tracing results for improved performance at the cost of some accuracy.")
        self._add_setting(SettingType.BOOL, "Many-Light Sampling", "/rtx/rtpt/lightcache/cached/enabled",
                          tooltip="\nEnables many-light sampling algorithm, resulting in faster rendering of scenes with many lights."
                                  "\nThis should generally be always enabled, and is exposed as an option for debugging potential algorithm artifacts.")
        self._add_setting(SettingType.BOOL, "Mesh-Light Sampling", "/rtx/rtpt/ris/meshLights", tooltip="\nEnables direct illumination sampling of geometry with emissive materials.")

class FireflyFilterSettingsFrame(SettingsCollectionFrame):
    """ Firefly Filtering """
    def _frame_setting_path(self):
        return "/rtx/rtpt/fireflyFilter/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity Glossy", "/rtx/rtpt/fireflyFilter/maxUnexposedIntensityPerSample", 0, 100000, 100, tooltip="\nClamps the maximium ray intensity for glossy bounces. Can help prevent fireflies, but may result in energy loss. This value is automatically scaled with the exposure.")
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity Diffuse", "/rtx/rtpt/fireflyFilter/maxUnexposedIntensityPerSampleDiffuse", 0, 100000, 100, tooltip="\nClamps the maximium ray intensity for diffuse bounces. Can help prevent fireflies, but may result in energy loss. This value is automatically scaled with the exposure.")
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity Emissive", "/rtx/rtpt/fireflyFilter/maxPerEmissiveUnexposedIntensity", 0, 100000, 100, tooltip="\nClamps the maximium ray intensity for emissive contribution after primary bounce. Can help prevent fireflies, but may result in energy loss. This value is automatically scaled with the exposure.")

class RTPTSettingsFrame(SettingsCollectionFrame):
    """ RTPT (Experimental) """
    def _build_ui(self):
        # We must clamp the depth (bounce count) to avoid a crash.
        # The storage capacity is limited for performance reasons.
        # The limit is defined by LIGHT_BOUNCE_BIT_COUNT in PathTracingInterface.hlsl.
        lightBounceBitCount = 6
        maxLightBounceCount = (1 << lightBounceBitCount) - 1
        # Limit RTPT bounces to a maximum of 6, also make sure to stay within the bounce counter bit size limit.
        rtptMaxLightBounceCount = min(maxLightBounceCount, 6)
        self._add_setting(SettingType.INT, "Max Bounces", "/rtx/rtpt/maxBounces", 0, rtptMaxLightBounceCount, tooltip="\nMaximum number of ray bounces for any ray type. Higher values give more accurate results, but worse performance.")
        self._add_setting(SettingType.INT, "Max Specular and Transmission Bounces", "/rtx/rtpt/maxSpecularAndTransmissionBounces", 1, rtptMaxLightBounceCount, tooltip="\nMaximum number of ray bounces for specular and trasnimission.")
        self._add_setting(SettingType.INT, "Max SSS Volume Scattering Bounces", "/rtx/rtpt/maxVolumeBounces", 0, maxLightBounceCount, tooltip="\nMaximum number of ray bounces for SSS.")
        ui.Line()
        self._add_setting(SettingType.BOOL, "Fractional Cutout Opacity", "/rtx/pathtracing/fractionalCutoutOpacity",
                          tooltip="\nIf enabled, fractional cutout opacity values are treated as a measure of surface 'presence',"
                                  "\nresulting in a translucency effect similar to alpha-blending. Path-traced mode uses stochastic"
                                  "\nsampling based on these values to determine whether a surface hit is valid or should be skipped.")
        self._add_setting(SettingType.FLOAT, "Roughness Threshold", "/rtx/rtpt/maxRoughness", 0.0, 1.0, 0.001,
                          tooltip="\nRoughness threshold at which a material with higher roughness is considered a rough surface."
                                  "\nThe rough surface will be rendered using approaches and approximations that favor performance.")
        ui.Line()
        self._add_setting(SettingType.BOOL, "Translucent Motion Vector Correction", "/rtx/rtpt/translucency/virtualMotion/enabled", tooltip="\nEnables motion vectors for translucent (refractive) objects, which can improve temporal rendering such as denoising, but can result in worse performance.")

    def destroy(self):
        self._change_cb = None
        super().destroy()

class RTPTSettingStack(RTXSettingsStack):
    def __init__(self) -> None:
        self._stack = ui.VStack(spacing=7, identifier=__class__.__name__)
        with self._stack:
            EcoMode("Eco Mode", parent=self)
            DLSSSettingsFrame("NVIDIA DLSS", parent=self)
            RTPTSettingsFrame("Path-Tracing", parent=self)
            SamplingAndCachingSettingsFrame("Sampling & Caching", parent=self)
            FireflyFilterSettingsFrame("Firefly Filtering", parent=self)
            SubsurfaceScatteringSettingsFrame("Subsurface Scattering", parent=self)
            GlobalVolumetricEffectsSettingsFrame("Global Volumetric Effects", parent=self)
            AOVSettingsFrame("AOV", parent=self)
            MultiMatteSettingsFrame("Multi Matte", parent=self)
            gpu_count = carb.settings.get_settings().get("/renderer/multiGpu/currentGpuCount") or 0
            if gpu_count > 1:
                MultiGPUSettingsFrame("Multi-GPU", parent=self)
