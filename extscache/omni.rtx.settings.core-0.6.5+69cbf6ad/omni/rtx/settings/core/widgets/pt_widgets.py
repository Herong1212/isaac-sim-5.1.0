import omni.ui as ui
import omni.kit.app
import carb.settings
import math
from omni.kit.widget.settings import SettingType
from omni.rtx.window.settings.rtx_settings_stack import RTXSettingsStack
from omni.rtx.window.settings.settings_collection_frame import SettingsCollectionFrame

class AntiAliasingSettingsFrame(SettingsCollectionFrame):
    """ Anti-Aliasing """
    def _build_ui(self):
        pt_aa_ops = ["Box", "Triangle", "Gaussian", "Uniform"]
        self._add_setting_combo("Anti-Aliasing Sample Pattern", "/rtx/pathtracing/aa/op", pt_aa_ops, tooltip="\nSampling pattern used for Anti-Aliasing. Select between Box, Triangle, Gaussian and Uniform.")
        self._add_setting(SettingType.FLOAT, "Anti-Aliasing Radius", "/rtx/pathtracing/aa/filterRadius", 0.0001, 5.0, 0.001, tooltip="\nSampling footprint radius, in pixels, when generating samples with the selected antialiasing sample pattern.")


class FireflyFilterSettingsFrame(SettingsCollectionFrame):
    """ Firefly Filtering """
    def _frame_setting_path(self):
        return "/rtx/pathtracing/fireflyFilter/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity Glossy", "/rtx/pathtracing/fireflyFilter/maxUnexposedIntensityPerSample", 0, 100000, 100, tooltip="\nClamps the maximium ray intensity for glossy bounces. Can help prevent fireflies, but may result in energy loss. This value is automatically scaled with the exposure.")
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity Diffuse", "/rtx/pathtracing/fireflyFilter/maxUnexposedIntensityPerSampleDiffuse", 0, 100000, 100, tooltip="\nClamps the maximium ray intensity for diffuse bounces. Can help prevent fireflies, but may result in energy loss. This value is automatically scaled with the exposure.")
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity Emissive", "/rtx/pathtracing/fireflyFilter/maxPerEmissiveUnexposedIntensity", 0, 100000, 100, tooltip="\nClamps the maximium ray intensity for emissive contribution after primary bounce. Can help prevent fireflies, but may result in energy loss. This value is automatically scaled with the exposure.")


class PathTracingSettingsFrame(SettingsCollectionFrame):
    """ Path-Tracing """
    def _build_ui(self):
        clampSpp = self._settings.get("/rtx/pathtracing/clampSpp")
        if clampSpp > 1:  # better 0, but setting range = (1,1) completely disables the UI control range
            self._add_setting(SettingType.INT, "Samples per Pixel per Frame(1 to {})".format(clampSpp), "/rtx/pathtracing/spp", 1, clampSpp, tooltip="\nTotal number of samples for each rendered pixel, per frame.")
        else:
            self._add_setting(SettingType.INT, "Samples per Pixel per Frame", "/rtx/pathtracing/spp", 1, 1048576, tooltip="\nTotal number of samples for each rendered pixel, per frame.")

        self._add_setting(SettingType.INT, "Total Samples per Pixel (0 = inf)", "/rtx/pathtracing/totalSpp", 0, 100000,
                          tooltip="\nMaximum number of samples to accumulate per pixel. When this count is reached the rendering stops until"
                                  "\na scene or setting change is detected, restarting the rendering process. Set to 0 to remove this limit.")
        self._add_setting(SettingType.BOOL, "Adaptive Sampling", "/rtx/pathtracing/adaptiveSampling/enabled", tooltip="\nWhen enabled, noise values are computed for each pixel, and upon threshold level eached, the pixel is no longer sampled")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/pathtracing/adaptiveSampling/enabled", self._on_change)
        if self._settings.get("/rtx/pathtracing/adaptiveSampling/enabled"):
            self._add_setting(SettingType.FLOAT, "   Target Error", "/rtx/pathtracing/adaptiveSampling/targetError", 0.00001, 1, tooltip="\nThe noise value threshold after which the pixel would no longer be sampled.")

        ui.Line()
        # We must clamp the depth (bounce count) to avoid a crash.
        # The storage capacity is limited for performance reasons.
        # The limit is defined by LIGHT_BOUNCE_BIT_COUNT in PathTracingInterface.hlsl.
        lightBounceBitCount = 6
        maxLightBounceCount = (1 << lightBounceBitCount) - 1
        self._add_setting(SettingType.INT, "Max Bounces", "/rtx/pathtracing/maxBounces", 0, maxLightBounceCount, tooltip="\nMaximum number of ray bounces for any ray type. Higher values give more accurate results, but worse performance.")
        self._add_setting(SettingType.INT, "Max Specular and Transmission Bounces", "/rtx/pathtracing/maxSpecularAndTransmissionBounces", 1, maxLightBounceCount, tooltip="\nMaximum number of ray bounces for specular and trasnimission.")
        self._add_setting(SettingType.INT, "Max SSS Volume Scattering Bounces", "/rtx/pathtracing/maxVolumeBounces", 0, maxLightBounceCount, tooltip="\nMaximum number of ray bounces for SSS.")
        self._add_setting(SettingType.INT, "Max Fog Scattering Bounces", "/rtx/pathtracing/ptfog/maxBounces", 1, maxLightBounceCount, tooltip="\nMaximum number of bounces for volume scattering within a fog/sky volume.")
        # self._add_setting(SettingType.BOOL, "Dome Lights: High Quality Primary Rays", "/rtx/pathtracing/domeLight/primaryRaysEvaluateDomelightMdlDirectly")

        ui.Line()
        # self._add_setting(SettingType.BOOL, "Show Lights", "/rtx/pathtracing/showLights/enabled") # depreacted, use /rtx/raytracing/showLights instead
        self._add_setting(SettingType.BOOL, "Fractional Cutout Opacity", "/rtx/pathtracing/fractionalCutoutOpacity",
                          tooltip="\nIf enabled, fractional cutout opacity values are treated as a measure of surface 'presence',"
                                  "\nresulting in a translucency effect similar to alpha-blending. Path-traced mode uses stochastic"
                                  "\nsampling based on these values to determine whether a surface hit is valid or should be skipped.")
        self._add_setting(SettingType.BOOL, "Reset Accumulation on Time Change", "/rtx/resetPtAccumOnAnimTimeChange",
                          tooltip="\nIf enabled, rendering is restarted every time the MDL animation time changes.")

    def destroy(self):
        self._change_cb = None
        super().destroy()


class SamplingAndCachingSettingsFrame(SettingsCollectionFrame):
    """ Sampling & Caching """
    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Caching", "/rtx/pathtracing/cached/enabled", tooltip="\nEnables caching path-tracing results for improved performance at the cost of some accuracy.")
        self._add_setting(SettingType.BOOL, "Many-Light Sampling", "/rtx/pathtracing/lightcache/cached/enabled",
                          tooltip="\nEnables many-light sampling algorithm, resulting in faster rendering of scenes with many lights."
                                  "\nThis should generally be always enabled, and is exposed as an option for debugging potential algorithm artifacts.")
        self._add_setting(SettingType.BOOL, "Mesh-Light Sampling", "/rtx/pathtracing/ris/meshLights", tooltip="\nEnables direct illumination sampling of geometry with emissive materials.")
        # ui.Label("Neural Radiance Caching does not work on Multi-GPU and requires (spp=1)", alignment=ui.Alignment.CENTER)
        # self._add_setting(SettingType.BOOL, "Enable Neural Radiance Cache (Experimental)", "/rtx/pathtracing/nrc/enabled")


class DenoisingSettingsFrame(SettingsCollectionFrame):
    """ Denoising """
    def _frame_setting_path(self):
        return "/rtx/pathtracing/optixDenoiser/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "OptiX Denoiser Temporal Mode", "/rtx/pathtracing/optixDenoiser/temporalMode/enabled")
        self._add_setting(SettingType.FLOAT, "OptiX Denoiser Blend Factor", "/rtx/pathtracing/optixDenoiser/blendFactor", 0, 1, 0.001,
                          tooltip="\nA blend factor indicating how much to blend the denoised image with the original non-denoised image."
                                  "\n0 shows only the denoised image, 1.0 shows the image with no denoising applied.")
        self._add_setting(SettingType.BOOL, "Denoise AOVs", "/rtx/pathtracing/optixDenoiser/AOV", tooltip="\nIf enabled, the OptiX Denoiser will also denoise the AOVs.")


class NonUniformVolumesSettingsFrame(SettingsCollectionFrame):
    """ Path-Traced Volume """
    def _frame_setting_path(self):
        return "/rtx/pathtracing/ptvol/enabled"

    def _build_ui(self):
        """ Path-Traced Volume """
        pt_vol_tr_ops = ["Biased Ray Marching", "Ratio Tracking"]
        self._add_setting_combo("Transmittance Method", "/rtx/pathtracing/ptvol/transmittanceMethod", pt_vol_tr_ops, tooltip="\nChoose between Biased Ray Marching or Ratio Tracking. Biased ray marching is the ideal option in all cases.")
        self._add_setting(SettingType.INT, "Max Ray Steps (Scattering)", "/rtx/pathtracing/ptvol/maxCollisionCount", 0, 1024, 32, tooltip="\nMaximum delta tracking steps between bounces. Increase to more than 32 for highly scattering volumes like clouds.")
        self._add_setting(SettingType.INT, "Max Ray Steps (Shadow)", "/rtx/pathtracing/ptvol/maxLightCollisionCount", 0, 1024, 16, tooltip="\nMaximum ratio tracking delta steps for shadow rays. Increase to more than 32 for highly scattering volumes like clouds.")
        # We must clamp the depth (bounce count) to avoid a crash.
        # The storage capacity is limited for performance reasons.
        # The limit is defined by LIGHT_BOUNCE_BIT_COUNT in PathTracingInterface.hlsl.
        lightBounceBitCount = 6
        maxLightBounceCount = (1 << lightBounceBitCount) - 1
        self._add_setting(SettingType.INT, "Max Non-uniform Volume Scattering Bounces", "/rtx/pathtracing/ptvol/maxBounces", 1, maxLightBounceCount, 1, tooltip="\nMaximum number of bounces in non-uniform volumes.")


class AOVSettingsFrame(SettingsCollectionFrame):
    """ AOV Settings"""
    def _on_rebuild_ui_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        """ AOV Settings """
        self._add_setting(SettingType.FLOAT, "Minimum Z-Depth", "/rtx/pathtracing/zDepthMin", 0, 10000, 1)
        self._add_setting(SettingType.FLOAT, "Maximum Z-Depth", "/rtx/pathtracing/zDepthMax", 0, 10000, 1)
        self._add_setting(SettingType.BOOL, "32 Bit Depth AOV", "/rtx/pathtracing/depth32BitAov", tooltip="\nUses a 32-bit format for the depth AOV")
        ui.Label("Enables AOV Preview in Debug View", alignment=ui.Alignment.CENTER)
        self._add_setting(SettingType.BOOL, "Pre-Denoised Result", "/rtx/pathtracing/preDenoisedResultAOV", tooltip="\nShading result before denoiser process")
        self._add_setting(SettingType.BOOL, "Background", "/rtx/pathtracing/backgroundAOV", tooltip="\nShading of the background, such as the background resulting from rendering a Dome Light.")
        self._add_setting(SettingType.BOOL, "Diffuse Filter", "/rtx/pathtracing/diffuseFilterAOV", tooltip="\nThe raw color of the diffuse texture.")
        self._add_setting(SettingType.BOOL, "Direct Illumation", "/rtx/pathtracing/diAOV", tooltip="\nShading from direct paths to light sources.")
        self._add_setting(SettingType.BOOL, "Global Illumination", "/rtx/pathtracing/giAOV", tooltip="\nDiffuse shading from indirect paths to light sources.")
        self._add_setting(SettingType.BOOL, "Motion Vectors", "/rtx/pathtracing/motionAOV", tooltip="\nMotion vectors.")
        self._add_setting(SettingType.BOOL, "Reflection", "/rtx/pathtracing/reflectionsAOV", tooltip="\nShading from indirect reflection paths to light sources.")
        self._add_setting(SettingType.BOOL, "Reflection Filter", "/rtx/pathtracing/reflectionFilterAOV", tooltip="\nThe raw color of the reflection, before being multiplied for its final intensity.")
        self._add_setting(SettingType.BOOL, "Refraction", "/rtx/pathtracing/refractionsAOV", tooltip="\nShading from refraction paths to light sources.")
        self._add_setting(SettingType.BOOL, "Refraction Filter", "/rtx/pathtracing/refractionFilterAOV", tooltip="\nThe raw color of the refraction, before being multiplied for its final intensity.")
        self._add_setting(SettingType.BOOL, "Subsurface Scattering", "/rtx/pathtracing/subsurfaceScatteringAOV", tooltip="\nShading from diffuse transmission paths to light sources.")
        self._add_setting(SettingType.BOOL, "Subsurface Filter", "/rtx/pathtracing/subsurfaceFilterAOV", tooltip="\nThe raw color of the subsurface scattering texture.")
        self._add_setting(SettingType.BOOL, "Self-Illumination", "/rtx/pathtracing/selfIllumAOV", tooltip="\nShading of the surface's own emission value.")
        self._add_setting(SettingType.BOOL, "Volumes", "/rtx/pathtracing/volumesAOV", tooltip="\nShading from VDB volumes.")
        self._add_setting(SettingType.BOOL, "World Normal", "/rtx/pathtracing/worldNormalsAOV", tooltip="\nThe surface's normal in world-space.")
        self._add_setting(SettingType.BOOL, "World Position", "/rtx/pathtracing/worldPosAOV", tooltip="\nThe surface's position in world-space.")
        self._add_setting(SettingType.BOOL, "View Normal", "/rtx/pathtracing/viewNormalsAOV", tooltip="\nThe surface's normal in view-space.")
        self._add_setting(SettingType.BOOL, "Z-Depth", "/rtx/pathtracing/zDepthAOV", tooltip="\nThe surface's depth relative to the view position.")
        self._add_setting(SettingType.BOOL, "Luminance", "/rtx/pathtracing/luminanceAOV", tooltip="\nThe intensity of light emitted from a surface per unit area in a given direction.")
        self._add_setting(SettingType.BOOL, "Illuminance", "/rtx/pathtracing/illuminanceAOV", tooltip="\nThe amount of light falling onto (illuminating) and spreading over a given surface area")

    def destroy(self):
        super().destroy()

class MultiMatteSettingsFrame(SettingsCollectionFrame):
    def _on_multimatte_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        self._add_setting(SettingType.INT, "Channel Count:", "/rtx/pathtracing/multimatte/channelCount", 0, 24, 1,
            tooltip="\nMultimatte allows rendering AOVs of meshes which have a Multimatte ID index matching a Multimatte AOV's channel index."
                    "\nChannel Count determines how many channels can be used, which are distributed among the Multimatte AOVs' color channels."
                    "\nYou can preview a Multimatte AOV by selecting one in the Debug View.")
        self._change_channels = omni.kit.app.SettingChangeSubscription("/rtx/pathtracing/multimatte/channelCount", self._on_multimatte_change)

        def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value)

        channelCount = clamp(self._settings.get("/rtx/pathtracing/multimatte/channelCount"), 0, 24)

        if channelCount != 0:
            mapCount = math.ceil(channelCount / 3)
            channelIndex = 0

            for i in range(0, mapCount):
                ui.Label("Multimatte" + str(i), alignment=ui.Alignment.CENTER)
                self._add_setting(SettingType.INT, "Red Channel Multimatte ID Index", "/rtx/pathtracing/multimatte/channel" + str(channelIndex), -1, 1000000, 1, tooltip="\nThe Multimatte ID index to match for the red channel of this Multimatte AOV.")
                channelIndex += 1
                if channelIndex >= channelCount:
                    break
                self._add_setting(SettingType.INT, "Green Channel Multimatte ID Index", "/rtx/pathtracing/multimatte/channel" + str(channelIndex), -1, 1000000, 1, tooltip="\nThe Multimatte ID index to match for the green channel of this Multimatte AOV.")
                channelIndex += 1
                if channelIndex >= channelCount:
                    break
                self._add_setting(SettingType.INT, "Blue Channel Multimatte ID Index", "/rtx/pathtracing/multimatte/channel" + str(channelIndex), -1, 1000000, 1, tooltip="\nThe Multimatte ID index to match for the blue channel of this Multimatte AOV.")
                channelIndex += 1
                if channelIndex >= channelCount:
                    break

        # self._add_setting(SettingType.BOOL, "is material ID " + str(i), "/rtx/pathtracing/multimatte/channel" + str(i) + "_isMat")

    def destroy(self):
        self._change_channels = None
        super().destroy()


class MultiGPUSettingsFrame(SettingsCollectionFrame):
    """ Multi-GPU """
    def _frame_setting_path(self):
        return "/rtx/pathtracing/mgpu/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Auto Load Balancing","/rtx/pathtracing/mgpu/autoLoadBalancing/enabled", tooltip="\nAutomatically balance the amount of total path-tracing work to be performed by each GPU in a multi-GPU configuration.")
        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/pathtracing/mgpu/autoLoadBalancing/enabled", self._on_change)
        if not self._settings.get("/rtx/pathtracing/mgpu/autoLoadBalancing/enabled") :
            device_count = self._settings.get("/renderer/multiGpu/currentGpuCount")
            for d in range(0, device_count):
                label = "GPU " + str(d) + " Weight"
                setting = "/rtx/pathtracing/mgpu/weightGpu" + str(d)
                self._add_setting(SettingType.FLOAT, label, setting, 0, 1, 0.001,
                                  tooltip="\nThe amount of total Path-Tracing work (between 0 and 1) to be performed by the GPU in a Multi-GPU configuration."
                                          "\nActual workload is determined by normalization of weights.")
        self._add_setting(SettingType.BOOL, "Compress Radiance", "/rtx/pathtracing/mgpu/compressRadiance", tooltip="Enables lossy compression of per-pixel output radiance values.")
        self._add_setting(SettingType.BOOL, "Compress Albedo", "/rtx/pathtracing/mgpu/compressAlbedo", tooltip="Enables lossy compression of per-pixel output albedo values (needed by OptiX denoiser).")
        self._add_setting(SettingType.BOOL, "Compress Normals", "/rtx/pathtracing/mgpu/compressNormals", tooltip="Enables lossy compression of per-pixel output normal values (needed by OptiX denoiser).")
        self._add_setting(SettingType.BOOL, "Multi-Threading", "/rtx/multiThreading/enabled", tooltip="Enabling multi-threading improves UI responsiveness.")

    def destroy(self):
        self._change_cb1 = None
        super().destroy()


class GlobalVolumetricEffectsSettingsFrame(SettingsCollectionFrame):
    """ PT Only Global Volumetric Effects Settings"""
    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Rayleigh Atmosphere", "/rtx/pathtracing/ptvol/raySky", tooltip="\nEnables an additional medium of Rayleigh-scattering particles to simulate a physically-based sky.")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/pathtracing/ptvol/raySky", self._on_change)
        if self._settings.get("/rtx/pathtracing/ptvol/raySky"):
            self._add_setting(SettingType.FLOAT, "   Rayleigh Atmosphere Scale", "/rtx/pathtracing/ptvol/raySkyScale", 0.01, 100, 1, tooltip="\nScales the size of the Rayleigh sky.")
            self._add_setting(SettingType.BOOL, "   Skip Background", "/rtx/pathtracing/ptvol/raySkyDomelight",
                              tooltip="\nIf a domelight is rendered for the sky color, the Rayleight Atmosphere is applied to the"
                                      "\nforeground while the background sky color is left unaffected.")

    def destroy(self):
        self._change_cb = None
        super().destroy()

class PTSettingStack(RTXSettingsStack):
    def __init__(self) -> None:
        self._stack = ui.VStack(spacing=7, identifier=__class__.__name__)
        with self._stack:
            PathTracingSettingsFrame("Path-Tracing", parent=self)
            SamplingAndCachingSettingsFrame("Sampling & Caching", parent=self)
            AntiAliasingSettingsFrame("Anti-Aliasing", parent=self)
            FireflyFilterSettingsFrame("Firefly Filtering", parent=self)
            DenoisingSettingsFrame("Denoising", parent=self)
            NonUniformVolumesSettingsFrame("Non-uniform Volumes", parent=self)
            GlobalVolumetricEffectsSettingsFrame("Global Volumetric Effects", parent=self)
            AOVSettingsFrame("AOV", parent=self)
            MultiMatteSettingsFrame("Multi Matte", parent=self)
            gpu_count = carb.settings.get_settings().get("/renderer/multiGpu/currentGpuCount") or 0
            if gpu_count > 1:
                MultiGPUSettingsFrame("Multi-GPU", parent=self)
