import omni.kit.app
import omni.ui as ui
import carb.settings
from omni.kit.widget.settings import SettingType
from omni.rtx.window.settings.rtx_settings_stack import RTXSettingsStack
from omni.rtx.window.settings.settings_collection_frame import SettingsCollectionFrame

DEBUG_OPTIONS = False

sampled_lighting_spp_items = {"1": 1, "2": 2, "4": 4, "8": 8}

class EcoMode(SettingsCollectionFrame):
    """ ECO Mode """
    def _frame_setting_path(self):
        return "/rtx/ecoMode/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.INT, "Stop Rendering After This Many Frames Without Changes", "/rtx/ecoMode/maxFramesWithoutChange", 0, 500)

class DLSSSettingsFrame(SettingsCollectionFrame):
    """ DLSS """
    def _on_antialiasing_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        # Note: values depend on rtx::postprocessing::AntialiasingMethod
        antialiasing_ops = dict()
        if self._settings.get("/rtx-transient/post/dlss/supported") is True:
            antialiasing_ops["DLSS"] = 3
            antialiasing_ops["DLAA"] = 4

        if self._settings.get("/rtx-transient/hashed/995bcbda752ace40e33a4d131067d270"):
            self._add_setting(SettingType.BOOL, "Frame Generation", "/rtx-transient/dlssg/enabled",
                              tooltip="\nDLSS Frame Generation boosts performance by using AI to generate more frames."
                                      "\nDLSS analyzes sequential frames and motion data to create additional high quality frames. This feature requires an Ada Lovelace architecture GPU.")

            self._change_cb4 = None


            # DLSS-G Settings:
            if self._settings.get("/rtx-transient/dlssg/enabled"):
                # set internally in DlssgContext after detecting BW+
                availableDlssgModes = { "Off": 0, "x2": 1 }
                if self._settings.get("/rtx-transient/dlssg/x3x4supported"):
                    availableDlssgModes["x3"] = 2
                    availableDlssgModes["x4"] = 3
                self._add_internal_setting_combo("FPS Multiplier", "/rtx-transient/internal/dlssg/interpolatedFrameCount",
                    availableDlssgModes,
                    tooltip=("\n\t\tEnables/disables DLSS-G with explicit control over the number of interpolated frames."
                        "\n\t\tThis setting is tied to /rtx-transient/dlssg/enabled."
                        "\n\t\tenabled==true maps to 'Off' and enabled==false maps to 'x2'"))
        self._change_cb3 = omni.kit.app.SettingChangeSubscription("/rtx-transient/hashed/995bcbda752ace40e33a4d131067d270", self._on_antialiasing_change)
        self._change_cb4 = omni.kit.app.SettingChangeSubscription("/rtx-transient/dlssg/enabled", self._on_antialiasing_change)

        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/post/aa/op", self._on_antialiasing_change)
        antialiasingOpIdx = self._settings.get("/rtx/post/aa/op")
        if antialiasingOpIdx == 3 or antialiasingOpIdx == 4:
            """ DLSS and DLAA """
            self._add_setting_combo("Super Resolution", "/rtx/post/aa/op", antialiasing_ops, tooltip="\nDLSS Super Resolution boosts performance by using AI to output higher resolution frames from a lower resolution input."
                                                                                                     "\nDLSS samples multiple lower resolution images and uses motion data and feedback from prior frames to reconstruct native quality images.")
            if antialiasingOpIdx == 3:
                # needs to be in sync with DLSSMode enum
                dlss_opts = {"Auto": 3, "Performance": 0, "Balanced": 1, "Quality": 2}
                self._add_setting_combo("   Mode", "/rtx/post/dlss/execMode", dlss_opts, tooltip="\nAuto: Selects the best DLSS Mode for the current output resolution.\nPerformance: Higher performance than balanced mode.\nBalanced: Balanced for optimized performance and image quality.\nQuality: Higher image quality than balanced mode.")
        else:
            ui.Label("Invalid AA Mode", alignment=ui.Alignment.CENTER)

    def destroy(self):
        self._change_cb1 = None
        self._change_cb2 = None
        self._change_cb3 = None
        self._change_cb4 = None
        super().destroy()


class DirectLightingSettingsFrame(SettingsCollectionFrame):
    """ Direct Lighting """
    def _frame_setting_path(self):
        return "/rtx/directLighting/enabled"

    def _build_ui(self):
        self._add_setting_combo("Samples per Pixel", "/rtx/directLighting/sampledLighting/samplesPerPixel", sampled_lighting_spp_items, tooltip="\nHigher values increase the direct lighting quality at the cost of performance.")
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity", "/rtx/directLighting/sampledLighting/maxRayUnexposedIntensity", 0.0, 1000000, 100, tooltip="\nClamps the brightness of a sample, which helps reduce fireflies, but may result in some loss of energy. This value is automatically scaled with the exposure.")
        self._add_setting(SettingType.BOOL, "Mesh-Light Sampling", "/rtx/directLighting/sampledLighting/ris/meshLights", tooltip="\nEnables direct illumination sampling of geometry with emissive materials.")
        self._add_setting(SettingType.BOOL, "Shadows", "/rtx/shadows/enabled", tooltip="\nWhen disabled, lights will not cast shadows.")

class ReflectionsSettingsFrame(SettingsCollectionFrame):
    """ Reflections """
    def _frame_setting_path(self):
        return "/rtx/reflections/enabled"

    def _build_ui(self):
        self._add_setting_combo("Samples per Pixel", "/rtx/reflections/sampledLighting/samplesPerPixel", sampled_lighting_spp_items, tooltip="\nHigher values increase the reflections quality at the cost of performance.")
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity", "/rtx/reflections/sampledLighting/maxRayUnexposedIntensity", 0.0, 1000000, 100, tooltip="\nClamps the brightness of a sample, which helps reduce fireflies, but may result in some loss of energy. This value is automatically scaled with the exposure.")
        self._add_setting(SettingType.INT, "Max Bounces", "/rtx/reflections/maxReflectionBounces", 0, 100, tooltip="\nNumber of bounces for reflection rays.")
        self._add_setting(SettingType.FLOAT, "Roughness Cache Threshold", "/rtx/reflections/maxRoughness", 0.0, 1.0, 0.02, tooltip="\nRoughness threshold for approximated reflections. Higher values result in better quality, at the cost of performance.")

class TranslucencySettingsFrame(SettingsCollectionFrame):
    """ Translucency (Refraction) """
    def _frame_setting_path(self):
        return "/rtx/translucency/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.INT, "Max Refraction Bounces", "/rtx/translucency/maxRefractionBounces", 0, 100, tooltip="\nNumber of bounces for refraction rays.")
        self._add_setting(SettingType.BOOL, "Reflection Seen Through Refraction", "/rtx/translucency/reflectAtAllBounce", tooltip="\n\t When enabled, reflection seen through refraction is rendered. When disabled, reflection is limited to first bounce only. More accurate, but worse performance")
        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/translucency/reflectAtAllBounce", self._on_change)

        if self._settings.get("/rtx/translucency/reflectAtAllBounce"):
            self._add_setting(SettingType.FLOAT, "Secondary Bounce Reflection Throughput Threshold", "/rtx/translucency/reflectionThroughputThreshold", 0.0, 1.0, 0.005, tooltip="\nThreshold below which reflection paths due to fresnel are no longer traced. Lower values result in higher quality at the cost of performance.")
        self._add_setting(SettingType.BOOL, "Fractional Cutout Opacity", "/rtx/raytracing/fractionalCutoutOpacity", tooltip="\nEnables fractional cutout opacity values resulting in a translucency-like effect similar to alpha-blending.")
        self._add_setting(SettingType.BOOL, "Depth Correction for DoF", "/rtx/translucency/virtualDepth", tooltip="\nImproves DoF for translucent (refractive) objects, but can result in worse performance.")
        self._add_setting(SettingType.BOOL, "Motion Vector Correction", "/rtx/translucency/virtualMotion", tooltip="\nEnables motion vectors for translucent (refractive) objects, which can improve temporal rendering such as denoising, but can result in worse performance.")
        self._add_setting(SettingType.FLOAT, "World Epsilon Threshold", "/rtx/translucency/worldEps", 0.0001, 5, 0.01, tooltip="\nTreshold below which image-based reprojection is used to compute refractions. Lower values result in higher quality at the cost performance.")
        self._add_setting(SettingType.BOOL, "Roughness Sampling", "/rtx/translucency/sampleRoughness", tooltip="\nEnables sampling roughness, such as for simulating frosted glass, but can result in worse performance.")
        self._add_setting(SettingType.FLOAT, "Max Ray Intensity", "/rtx/translucency/maxRayUnexposedIntensity", 0.0, 1000000, 100, tooltip="\nClamps the brightness of a sample, which helps reduce fireflies, but may result in some loss of energy. This value is automatically scaled with the exposure.")
        self._add_setting(SettingType.BOOL, "Invisible Light Behind Translucency in Reflections", "/rtx/raytracing/checkInvisLightRoughThrReflTrans",
                            tooltip="\nIf true, hide light reflection if it is behind translucent geometry."
                                    "\nSubject to the roughness thresholds of the light visibility settings.")

    def destroy(self):
        self._change_cb1 = None
        super().destroy()


class CausticsSettingsFrame(SettingsCollectionFrame):
    """ Caustics """
    def _frame_setting_path(self):
        return "/rtx/caustics/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.INT, "Photon Count Multiplier", "/rtx/raytracing/caustics/photonCountMultiplier", 1, 5000, tooltip="\nFactor multiplied by 1024 to compute the total number of photons to generate from each light.")
        self._add_setting(SettingType.INT, "Photon Max Bounces", "/rtx/raytracing/caustics/photonMaxBounces", 1, 20, tooltip="\nMaximum number of bounces to compute for each light/photon path.")
        self._add_setting(SettingType.FLOAT, "Position Phi", "/rtx/raytracing/caustics/positionPhi", 0.1, 50)
        self._add_setting(SettingType.FLOAT, "Normal Phi", "/rtx/raytracing/caustics/normalPhi", 0.3, 1)
        self._add_setting(SettingType.INT, "Filter Iterations", "/rtx/raytracing/caustics/eawFilteringSteps", 0, 10, tooltip="\nNumber of iterations for the denoiser applied to the results of the caustics tracing pass.")


class IndirectDiffuseLightingSettingsFrame(SettingsCollectionFrame):

    def _on_denoiser_change(self, *_):
        self._rebuild()

    def _build_ui(self):

        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/ambientOcclusion/enabled", self._on_change)
        self._change_cb2 = omni.kit.app.SettingChangeSubscription("/rtx/indirectDiffuse/enabled", self._on_change)

        self._add_setting(SettingType.BOOL, "Indirect Diffuse GI", "/rtx/indirectDiffuse/enabled", tooltip="\nEnables indirect diffuse GI sampling.")
        if self._settings.get("/rtx/indirectDiffuse/enabled"):
            self._add_setting(SettingType.INT, "   Samples per Pixel", "/rtx/indirectDiffuse/fetchSampleCount", 0, 4, tooltip="\nNumber of samples made for indirect diffuse GI. Higher number gives better GI quality, but worse performance.")
            self._add_setting(SettingType.FLOAT, "   Max Ray Intensity", "/rtx/indirectDiffuse/maxRayUnexposedIntensity", 0.0, 1000000, 100, tooltip="\nClamps the brightness of a sample, which helps reduce fireflies, but may result in some loss of energy. This value is automatically scaled with the exposure.")
            self._add_setting(SettingType.INT, "   Max Bounces", "/rtx/indirectDiffuse/maxBounces", 0, 16, tooltip="\nNumber of bounces approximated with indirect diffuse GI.")
            self._add_setting(SettingType.FLOAT, "   Intensity", "/rtx/indirectDiffuse/scalingFactor", 0.0, 20.0, 0.1, tooltip="\nMultiplier for the indirect diffuse GI contribution.")
        self._add_setting(SettingType.BOOL, "Ambient Occlusion", "/rtx/ambientOcclusion/enabled", tooltip="\nEnables ambient occlusion.")
        if self._settings.get("/rtx/ambientOcclusion/enabled"):
            self._add_setting(SettingType.FLOAT, "   Ray Length (cm)", "/rtx/ambientOcclusion/rayLength", 0.0, 2000.0, tooltip="\nThe radius around the intersection point which the ambient occlusion affects.")
            self._add_setting(SettingType.INT, "   Minimum Samples Per Pixel", "/rtx/ambientOcclusion/minSamples", 1, 16, tooltip="\nMinimum number of samples per frame for ambient occlusion sampling.")
            self._add_setting(SettingType.INT, "   Maximum Samples Per Pixel", "/rtx/ambientOcclusion/maxSamples", 1, 16, tooltip="\nMaximum number of samples per frame for ambient occlusion sampling.")
        self._add_setting(SettingType.COLOR3, "Ambient Light Color", "/rtx/sceneDb/ambientLightColor", tooltip="\nColor of the global environment lighting.")
        self._add_setting(SettingType.FLOAT, "Ambient Light Intensity", "/rtx/sceneDb/ambientLightIntensity", 0.0, 10.0, 0.1, tooltip="\nBrightness of the global environment lighting.")

    def destroy(self):
        self._change_cb1 = None
        self._change_cb2 = None
        super().destroy()


class RTMultiGPUSettingsFrame(SettingsCollectionFrame):
    """ Multi-GPU """
    def _frame_setting_path(self):
        return "/rtx/realtime/mgpu/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Automatic Tiling", "/rtx/realtime/mgpu/autoTiling/enabled",
                          tooltip="\nAutomatically determines the image-space grid used to distribute rendering to available GPUs."
                                  "\nThe image rendering is split into a large tile per GPU with a small overlap region between them."
                                  "\nNote that by default not necessarily all GPUs are used. The approximate number of tiles is viewport"
                                  "\nresolution divided by the Minimum Megapixels Per Tile setting, since at low resolution small tiles distributed"
                                  "\nacross too many devices decreases performance due to multi-GPU overheads."
                                  "\nDisable automatic tiling to manually specify the number of tiles to be distributed across devices.")
        self._change_cb2 = omni.kit.app.SettingChangeSubscription("/rtx/realtime/mgpu/autoTiling/enabled", self._on_change)
        if self._settings.get("/rtx/realtime/mgpu/autoTiling/enabled"):
            self._add_setting(SettingType.FLOAT, "   Minimum Megapixels Per Tile", "/rtx/realtime/mgpu/autoTiling/minMegaPixelsPerTile", 0.1, 2.0, 0.1, tooltip="\nThe minimum number of Megapixels each tile should have after screen-space subdivision.")
        else:
            currentGpuCount = self._settings.get("/renderer/multiGpu/currentGpuCount")
            self._add_setting(SettingType.INT, "Tile Count", "/rtx/realtime/mgpu/tileCount", 2, currentGpuCount, tooltip="\nNumber of tiles to split the image into. Usually this should match the number of GPUs, but can be less.")
        self._add_setting(SettingType.INT, "Tile Overlap (Pixels)", "/rtx/realtime/mgpu/tileOverlap", 0, 256, 0.1, tooltip="\nWidth, in pixels, of the overlap region between any two neighboring tiles.")
        self._add_setting(SettingType.FLOAT, "GPU 0 Weight", "/rtx/realtime/mgpu/masterDeviceLoadBalancingWeight", 0, 1, 0.001,
                          tooltip="\nThis normalized weight can be used to decrease the rendering workload on the primary device for each viewport"
                                  "\nin relation to the other secondary devices, which can be helpful for load balancing in situations where the primary"
                                  "\ndevice also needs to perform additional expensive operations such as denoising and post-processing.")
        self._add_setting(SettingType.BOOL, "Multi-Threading", "/rtx/multiThreading/enabled", tooltip="\nExecute per-device render command recording in separate threads.")


class SubsurfaceScatteringSettingsFrame(SettingsCollectionFrame):
    """ Subsurface Scattering """
    def _frame_setting_path(self):
        return "/rtx/raytracing/subsurface/enabled"

    def _on_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        self._add_setting(SettingType.INT, "Max Samples Per Frame", "/rtx/raytracing/subsurface/maxSamplePerFrame", 1, 128, tooltip="\nMax samples per frame for the infinitely-thick geometry SSS approximation.")
        # self._add_setting(SettingType.FLOAT, "History Weight", "/rtx/raytracing/subsurface/historyWeight", 0.001, 0.5, 0.02)
        # self._add_setting(SettingType.FLOAT, "Variance Threshold", "/rtx/raytracing/subsurface/targetVariance", 0.001, 1, 0.05)
        # self._add_setting(SettingType.FLOAT, "World space sample projection Threshold", "/rtx/raytracing/subsurface/shadowRayThreshold", 0, 1, 0.01)
        self._add_setting(SettingType.BOOL, "Firefly Filtering", "/rtx/raytracing/subsurface/fireflyFiltering/enabled", tooltip="\nEnables firefly filtering for the subsurface scattering. The maximum filter intensity is determined by '/rtx/directLighting/sampledLighting/maxRayUnexposedIntensity'.")
        self._add_setting(SettingType.BOOL, "Denoise Irradiance Input", "/rtx/directLighting/sampledLighting/irradiance/denoiser/enabled",
                            tooltip="\nDenoise the irradiance output from sampled lighting pass before it's used, helps in complex lighting conditions"
                                    "\nor if there are large area lights which makes irradiance estimation difficult with low sampled lighting sample count.")
        self._add_setting(SettingType.BOOL, "Transmission", "/rtx/raytracing/subsurface/transmission/enabled", tooltip="\nEnables transmission of light through the medium, but requires additional samples and denoising.")
        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/raytracing/subsurface/transmission/enabled", self._on_change)
        if self._settings.get("/rtx/raytracing/subsurface/transmission/enabled"):
            self._add_setting(SettingType.INT, "   BDSF Sample Count", "/rtx/raytracing/subsurface/transmission/bsdfSampleCount", 0, 8, tooltip="\nTransmission sample count per frame.")
            self._add_setting(SettingType.INT, "   Samples Per BSDF Sample", "/rtx/raytracing/subsurface/transmission/perBsdfScatteringSampleCount", 0, 16, tooltip="\nTransmission samples count per BSDF Sample. Samples per pixel per frame = BSDF Sample Count * Samples Per BSDF Sample.")
            self._add_setting(SettingType.FLOAT, "   Screen-Space Fallback Threshold", "/rtx/raytracing/subsurface/transmission/screenSpaceFallbackThresholdScale", 0.0001, 1, tooltip="\nTransmission threshold for screen-space fallback.")
            self._add_setting(SettingType.BOOL, "   Half-Resolution Rendering", "/rtx/raytracing/subsurface/transmission/halfResolutionBackfaceLighting", tooltip="\nEnables rendering transmission in half-resolution to improve performance at the expense of quality.")
            self._add_setting(SettingType.BOOL, "   Sample Guiding", "/rtx/raytracing/subsurface/transmission/ReSTIR/enabled", tooltip="\nEnables transmission sample guiding, which may help with complex lighting scenarios.")

    def destroy(self):
        self._change_cb1 = None
        super().destroy()


class GlobalVolumetricEffectsSettingsFrame(SettingsCollectionFrame):
    """ RT Only Global Volumetric Effects Settings"""
    def _build_ui(self):
        self._add_setting(SettingType.INT, "Accumulation Frames", "/rtx/raytracing/inscattering/maxAccumulationFrames", 0, 256, tooltip="\nNumber of frames samples accumulate over temporally. High values reduce noise, but increase lighting update times.")
        self._add_setting(SettingType.INT, "Depth Slices Count", "/rtx/raytracing/inscattering/depthSlices", 16, 1024, tooltip="\nNumber of layers in the voxel grid to be allocated. High values result in higher precision at the cost of memory and performance.")
        self._add_setting(SettingType.INT, "Pixel Density", "/rtx/raytracing/inscattering/pixelRatio", 4, 64, tooltip="\nLower values result in higher fidelity volumetrics at the cost of performance and memory (depending on the # of depth slices).")
        self._add_setting(SettingType.FLOAT, "Slice Distribution Exponent", "/rtx/raytracing/inscattering/sliceDistributionExponent", 1, 16, tooltip="\nControls the number (and relative thickness) of the depth slices.")
        self._add_setting(SettingType.INT, "Inscatter Upsample", "/rtx/raytracing/inscattering/inscatterUpsample", 1, 64, tooltip="\n")
        self._add_setting(SettingType.FLOAT, "Inscatter Blur Sigma", "/rtx/raytracing/inscattering/blurSigma", 0.0, 10.0, 0.01, tooltip="\nSigma parameter for the Gaussian filter used to spatially blur the voxel grid. 1 = no blur, higher values blur further.")
        self._add_setting(SettingType.FLOAT, "Inscatter Dithering Scale", "/rtx/raytracing/inscattering/ditheringScale", 0, 10000, tooltip="\nThe scale of the noise dithering. Used to reduce banding from quantization on smooth gradients.")
        self._add_setting(SettingType.FLOAT, "Spatial Sample Jittering Scale", "/rtx/raytracing/inscattering/spatialJitterScale", 0.0, 1, 0.0001, tooltip="\nScales how far light samples within a voxel are spatially jittered: 0 = only from the center, 1 = the entire voxel's volume.")
        self._add_setting(SettingType.FLOAT, "Temporal Reprojection Jittering Scale", "/rtx/raytracing/inscattering/temporalJitterScale", 0.0, 1, 0.0001,
                          tooltip="\nScales how far to offset temporally-reprojected samples within a voxel: 0 = only from the center, 1 = the entire voxel's volume."
                                  "\nActs like a temporal blur and helps reduce noise under motion.")
        self._add_setting(SettingType.BOOL, "Use 32-bit Precision", "/rtx/raytracing/inscattering/use32bitPrecision", tooltip="\nAllocate the voxel grid with 32-bit per channel color instead of 16-bit. This doubles memory usage and reduces performance, generally avoided.")
        self._add_setting(SettingType.BOOL, "Flow Sampling", "/rtx/raytracing/inscattering/enableFlowSampling", tooltip="\n")
        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/raytracing/inscattering/enableFlowSampling", self._on_change)
        if self._settings.get("/rtx/raytracing/inscattering/enableFlowSampling"):
            self._add_setting(SettingType.INT, "   Min Layer", "/rtx/raytracing/inscattering/minFlowLayer", 0, 64, tooltip="\n")
            self._add_setting(SettingType.INT, "   Max Layer", "/rtx/raytracing/inscattering/maxFlowLayer", 0, 64, tooltip="\n")
            self._add_setting(SettingType.FLOAT, "   Density Scale", "/rtx/raytracing/inscattering/flowDensityScale", 0.0, 100.0, tooltip="\n")
            self._add_setting(SettingType.FLOAT, "   Density Offset", "/rtx/raytracing/inscattering/flowDensityOffset", 0.0, 100.0, tooltip="\n")

    def destroy(self):
        self._change_cb1 = None
        super().destroy()


class RTSettingStack(RTXSettingsStack):
    def __init__(self) -> None:
        self._stack = ui.VStack(spacing=7, identifier=__class__.__name__)
        with self._stack:
            EcoMode("Eco Mode", parent=self)
            DLSSSettingsFrame("NVIDIA DLSS", parent=self)
            DirectLightingSettingsFrame("Direct Lighting", parent=self)
            IndirectDiffuseLightingSettingsFrame("Indirect Diffuse Lighting", parent=self)
            ReflectionsSettingsFrame("Reflections", parent=self)
            translucency = TranslucencySettingsFrame("Translucency", parent=self)
            SubsurfaceScatteringSettingsFrame("Subsurface Scattering", parent=translucency)
            CausticsSettingsFrame("Caustics", parent=self)
            GlobalVolumetricEffectsSettingsFrame("Global Volumetric Effects", parent=self)
            gpuCount = carb.settings.get_settings().get("/renderer/multiGpu/currentGpuCount")
            if gpuCount and gpuCount > 1:
                RTMultiGPUSettingsFrame("Multi-GPU", parent=self)
