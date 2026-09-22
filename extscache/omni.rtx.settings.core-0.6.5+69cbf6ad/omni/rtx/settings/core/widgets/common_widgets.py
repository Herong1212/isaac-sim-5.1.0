import omni.ui as ui
from omni.kit.widget.settings import SettingType
import omni.kit.commands
from omni.rtx.window.settings.rtx_settings_stack import RTXSettingsStack
from omni.rtx.window.settings.settings_collection_frame import SettingsCollectionFrame
from omni.kit.widget.settings import SettingsWidgetBuilder
import carb

from .photometric_heatmap_bar import *

class GeometrySettingsFrame(SettingsCollectionFrame):
    """ Geometry """
    def _build_ui(self):
        tbnMode = ["Auto", "CPU", "GPU", "Force GPU"]
        scale_option = {"Default": -1, "Small - 1cm": 0.01, "Medium - 10 cm": 0.1, "Big - 100 cm": 1}
        with ui.CollapsableFrame("Misc Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting_combo("Normal & Tangent Space Generation Mode", "/rtx/hydra/TBNFrameMode", tbnMode,
                                        tooltip="\nMode selection for vertex Normals and Tangents generation. Options are:"
                                                "\n-AUTO: Selects the mode depending on available data and data update pattern."
                                                "\n-CPU: Uses mikktspace to generate tangent basis on the CPU."
                                                "\n-GPU: Allows normal and tangent basis update on the GPU to avoid the CPU overhead, such as for deforming meshes."
                                                "\n-Force GPU: Forces GPU mode.")
                self._add_setting(SettingType.BOOL, "Back Face Culling", "/rtx/hydra/faceCulling/enabled",
                                  tooltip="\nEnables back face culling for 'Single Sided' primitives."
                                          "\nThis applies to UsdGeom prims set to 'Single Sided' since the Double Sided flag is ignored.")
                self._add_setting(SettingType.BOOL, "USD ST Main Texcoord as Default UV Set", "/rtx/hydra/uvsets/stIsDefaultUvSet", tooltip="\nIf enabled, ST is considered to be the default UV set name.")
                self._add_setting(SettingType.BOOL, "Hide Geometry That Uses Opacity (debug)", "/rtx/debug/onlyOpaqueRayFlags", tooltip="\nAllows hiding all objects which have opacity enabled in their material.")
                self._add_setting(SettingType.BOOL, "Instance Selection", "/rtx/hydra/instancePickingEnabled", tooltip="\nEnables the picking of instances.")
                # if set to zero, override to scene unit, which means the scale factor would be 1
                self._add_setting_combo("Renderer-Internal Meters Per Unit", "/rtx/scene/renderMeterPerUnit", scale_option,
                                        tooltip="\nNumber of units per meter used by the renderer relative to the scene scale."
                                                "\nSome materials depend on scene scale, such as subsurface scattering and volumetric shading.")
                self._add_setting(SettingType.FLOAT, "Ray Offset (0 = auto)", "/rtx/raytracing/rayOffset", 0.0, 5.0, 0.001, tooltip="\nOffset used to prevent ray-triangle self intersections." )

                self._add_setting(SettingType.FLOAT, "Points Default Width", "/persistent/rtx/hydra/points/defaultWidth", tooltip="\nUses this value if width is not specified in UsdGeomPoints.")

        with ui.CollapsableFrame("Wireframe Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.BOOL, "Per-primitive Wireframe uses World Space Thickness", "/rtx/wireframe/wireframeThicknessWorldSpace", tooltip="\nInterprets the per-primitive wireframe thickness value in world space instead of screen space.")
                self._add_setting(SettingType.BOOL, "Global Wireframe uses World Space Thickness", "/rtx/wireframe/globalWireframeThicknessWorldSpace", tooltip="\nInterprets the global wireframe thickness value in world space instead of screen space.")
                self._add_setting(SettingType.FLOAT, "Thickness", "/rtx/wireframe/wireframeThickness", 0.1, 100, 0.1, tooltip="\nWireframe thickness in wireframe mode.")

        def clear_refinement_overrides():
            omni.kit.commands.execute("ClearRefinementOverrides")

        with ui.CollapsableFrame("Subdivision Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.INT, "Global Refinement Level", "/rtx/hydra/subdivision/refinementLevel", 0, 8, hard_range=True,
                                  tooltip="\nThe refinement level for all primitives with Subdivision Schema not set to None."
                                          "\nEach increment increases the mesh triangle count by a factor of 4.")
                ui.Button("Clear Refinement Override in All Prims", clicked_fn=clear_refinement_overrides, tooltip="\nClears the Refinement Override set in all Prims.")

        def clear_splits_overrides():
            omni.kit.commands.execute("ClearCurvesSplitsOverridesCommand")

        with ui.CollapsableFrame("Curves Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.INT, "Global Number of BVH Splits", "/rtx/hydra/curves/splits", 1, 8, hard_range=True,
                                  tooltip="\nHigher number of splits results in faster rendering but longer BVH build time."
                                          "\nThe speed up depends on the geometry: long and thin curve segments tend to benefit from more splits."
                                          "\nMemory used by the BVH grows linearly with the number of splits.")
                ui.Button("Clear Number of BVH Splits Overrides in All Prims", clicked_fn=clear_splits_overrides, tooltip="\nClears the Number of BVH Splits Refinement Override set in all Prims.")

class MaterialsSettingsFrame(SettingsCollectionFrame):
    """ Materials """
    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Translucency as Opacity", "/rtx/material/translucencyAsOpacity", tooltip="\nWhen enabled, the translucent material will be converted into opacity blending based surface.")
        with ui.CollapsableFrame("MDL Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.FLOAT, "Animation Time Override", "/rtx/animationTime", tooltip="\nOverrides the time value provided to MDL materials.")
                self._add_setting(SettingType.BOOL, "Animation Time Use Wallclock", "/rtx/animationTimeUseWallclock", tooltip="\nUse actual elapsed time for animation instead of simulated time.")
                self._add_setting(SettingType.BOOL, "MDL displacement", "/rtx/material/enableMDLDisplacement", tooltip="\nEnable MDL material displacement. Enabling it can negatively impact stage load time when there are many materials with displacement support (like OmniSurface) in a stage. Requires stage reload to take effect.")
                # self._add_setting(SettingType.BOOL, "Omni RTX Enable Opacity Override", "/rtx/material/omniRtxEnableOpacityOverride", tooltip="\nEnables override cutout opacity and transmission properties (material's attributes omni:rtx:enableCutoutOpacity and omni:rtx:enableTransmission) for custom MDL materials for which the RTX Renderer was unable to automatically derive such properties")

class BackgroundSettingsFrame(SettingsCollectionFrame):
    """ Background """
    def _build_ui(self):
        background_source_op = { "None": 0, "Texture": 1, "Color": 2 }
        self._add_setting_combo("Background Override", "/rtx/background/source/type", background_source_op,
                tooltip="\nBy default the background is sourced from a dome light if one is rendered, "
                        "\notherwise the Background Texture if one is assigned, otherwise the Background Color."
                        "\nThis can be overriden to force the use of either the Texture or Color."
                )

        self._add_setting("ASSET", "Background Texture", "/rtx/background/source/texture/path", tooltip="\nThe path to the texture to use as the background.")
        sampler_ops = { "Repeat": 0, "Mirror": 1, "Clamp": 2 }
        self._add_setting_combo("   UV Sampler", "/rtx/background/source/texture/textureMode", sampler_ops,
                tooltip="\nRepeat: The texture UV value will get modulated with 1."
                "\nMirror: The UV value will get modulated by 2 then mirrored by x=1 and y=1."
                "\nClamp: The UV value will get clampped to [0, 1]."
                )
        color_space_op = { "sRGB": 0, "lin_rec709": 1}
        self._add_setting_combo("   Color Space", "/rtx/background/source/texture/colorSpace", color_space_op,
                tooltip="\nSets the color space for the background texture."
                )
        self._add_setting(SettingType.FLOAT, "   Luminance Scale", "rtx/background/source/texture/luminanceScale", tooltip="\nScales the background texture luminance.")

        self._add_setting(SettingType.COLOR3, "Background Color", "/rtx/background/source/color", tooltip="\nThe color to use as the background.")

    def destroy(self):
        super().destroy()

class LightingSettingsFrame(SettingsCollectionFrame):
    """ Lighting """
    def _build_ui(self):
        with ui.CollapsableFrame("Light Visibility Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                # Common show light setting for all render modes - this makes the /pathracing/showLights and /directLighting/showLights deprecated and should be used instead
                # see LightTypes.hlslh for enum
                show_lights_settings = {
                    "Per-Light Enable": 0,
                    "Force Enable": 1,
                    "Force Disable": 2
                }
                self._add_setting_combo("Show Area Lights In Primary Rays", "/rtx/raytracing/showLights", show_lights_settings, tooltip="\nDefines if area lights are visible or invisible in primary rays.")
                self._add_setting(SettingType.FLOAT, "Invisible Light Refractions Roughness Threshold", "/rtx/raytracing/invisLightRoughnessThreshold", 0, 1, 0.001,
                                  tooltip="\nDefines the roughness threshold below which lights invisible in primary rays"
                                          "\nare also invisible in refractions.")
                self._add_setting(SettingType.FLOAT, "Invisible Light Reflections Roughness Threshold", "/rtx/raytracing/invisLightReflectionsRoughnessThreshold", 0, 1, 0.001,
                                  tooltip="\nDefines the roughness threshold below which lights invisible in primary rays"
                                          "\nare also invisible in reflections.")
                self._add_setting(SettingType.BOOL, "Use First Distant Light & First Dome Light Only", "/rtx/scenedb/skipMostLights", tooltip="\nDisable all lights except the first distant light and first dome light.")
                self._add_setting(SettingType.FLOAT, "Shadow Bias", "/rtx/raytracing/shadowBias", 0.0, 5.0, 0.001, tooltip="\nOffset applied for shadow ray origin along the surface normal. Reduces self-shadowing artifacts.")

        with ui.CollapsableFrame("Dome Light Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                dome_lighting_sampling_type = {
                    "Image-Based Lighting": 0,
                    "Approximated Image-Based Lighting": 4,
                    "Environment Mapped Image-Based Lighting": 3
                }
                self._add_setting_combo("Lighting Mode", "/rtx/domeLight/upperLowerStrategy", dome_lighting_sampling_type,
                                        tooltip="\n-Image-Based Lighting: Most accurate even for high-frequency Dome Light textures. Can introduce sampling artefacts in real-time mode."
                                                "\n-Approximated Image-Based Lighting: Fast and artefacts-free sampling in real-time mode but only works well with a low-frequency texture,"
                                                "\nfor example a sky with no sun disc where the sun is instead a separate Distant Light."
                                                "\n-Limited Image-Based Lighting: Only sampled for reflection and refraction. Fastest, but least accurate. Good for cases where the Dome Light"
                                                "\ncontributes less than other light sources.")
                dome_texture_resolution_items = {
                    "16": 16,
                    "32": 32,
                    "64": 64,
                    "128": 128,
                    "256": 256,
                    "512": 512,
                    "1024": 1024,
                    "2048": 2048,
                    "4096": 4096,
                    "8192": 8192,
                }
                self._add_setting_combo("Baking Resolution", "/rtx/domeLight/baking/resolution", dome_texture_resolution_items, tooltip="\nThe baking resolution of the Dome Light texture when an MDL material is used as its image source.")

        with ui.CollapsableFrame("Units", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.BOOL, "Correct IES Units", "/rtx/directLighting/units/correctIES", tooltip="\nWhen enabled, intensity (candela) values in IES files will be converted correctly to luminance in the renderer."
                                                                                                                         "\nThis means that the brightness of the light will be dependent on the scale of the scene. As long as the scene is"
                                                                                                                         "\nmodelled accurately and the scene metersPerUnit is set correctly, lights with IES profiles will generate the correct"
                                                                                                                         "\nillumination."
                                                                                                                         "\nWhen this is enabled, setting the IES normalize flag will also normalize the IES profile in units of power.")

class GlobalVolumetricEffectsSettingsFrame(SettingsCollectionFrame):
    """ Global Volumetric Effects Common Settings RT & PT """
    def _frame_setting_path(self):
        return "/rtx/raytracing/globalVolumetricEffects/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.FLOAT, "Fog Height", "/rtx/raytracing/inscattering/atmosphereHeight", -2000, 100000, 10, tooltip="\nHeight in world units (centimeters) at which the medium ends. Useful for atmospheres with distant lights or dome lights.")
        self._add_setting(SettingType.FLOAT, "Fog Height Fall Off", "/rtx/pathtracing/ptvol/fogHeightFallOff", 10, 2000, 1, tooltip="\nExponential decay of the fog above the Fog Height.")
        self._add_setting(SettingType.FLOAT, "Maximum inscattering Distance", "/rtx/raytracing/inscattering/maxDistance", 10, 1000000,
                          tooltip="\nMaximum depth in world units (centimeters) the voxel grid is allocated to."
                                  "\nIf set to 10,000 with 10 depth slices, each slice will span 1,000 units (assuming a slice distribution exponent of 1)."
                                  "\nIdeally this should be kept as low as possible without causing artifacts to make the most of the fixed number of depth slices.")
        self._add_setting(SettingType.FLOAT, "Density Multiplier", "/rtx/raytracing/inscattering/densityMult", 0, 2, 0.001, tooltip="\nScales the fog density.")
        self._add_setting(SettingType.FLOAT, "Transmittance Measurment Distance", "/rtx/raytracing/inscattering/transmittanceMeasurementDistance", 0.0001, 1000000, 10, tooltip="\nControls how far light can travel through fog. Lower values yield thicker fog.")
        self._add_setting(SettingType.COLOR3, "Transmittance Color", "/rtx/raytracing/inscattering/transmittanceColor",
                          tooltip="\nAssuming a white light, it represents its tint after traveling a number of units through"
                                  "\nthe volume as specified in Transmittance Measurement Distance.")
        self._add_setting(SettingType.COLOR3, "Single Scattering Albedo", "/rtx/raytracing/inscattering/singleScatteringAlbedo", tooltip="\nThe ratio of scattered-light to attenuated-light for an interaction with the volume. Values closer to 1 indicate high scattering.")
        self._add_setting(SettingType.FLOAT, "Anisotropy Factor (g)", "/rtx/raytracing/inscattering/anisotropyFactor", -0.999, 0.999, 0.01,
                          tooltip="\nAnisotropy of the volumetric phase function, or the degree of light scattering asymmetry."
                                  "\n-1 is back-scattered, 0 is isotropic, 1 is forward-scattered.")
        with ui.CollapsableFrame("Density Noise Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.BOOL, "Apply Density Noise", "/rtx/raytracing/inscattering/useDetailNoise", tooltip="\nEnables modulating the density with a noise. Enabling this option can reduce performance.")
                self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/raytracing/inscattering/useDetailNoise", self._on_change)
                if self._settings.get("/rtx/raytracing/inscattering/useDetailNoise"):
                    self._add_setting(SettingType.FLOAT, "   World Scale", "/rtx/raytracing/inscattering/detailNoiseScale", 0.0, 1, 0.00001, tooltip="\nA scale multiplier for the noise. Smaller values produce more sparse noise.")
                    self._add_setting(SettingType.FLOAT, "   Animation Speed X", "/rtx/raytracing/inscattering/noiseAnimationSpeedX", -1.0, 1.0, 0.01, tooltip="\nThe X vector for the noise shift when animated.")
                    self._add_setting(SettingType.FLOAT, "   Animation Speed Y", "/rtx/raytracing/inscattering/noiseAnimationSpeedY", -1.0, 1.0, 0.01, tooltip="\nThe Y vector for the noise shift when animated.")
                    self._add_setting(SettingType.FLOAT, "   Animation Speed Z", "/rtx/raytracing/inscattering/noiseAnimationSpeedZ", -1.0, 1.0, 0.01, tooltip="\nThe Z vector for the noise shift when animated.")
                    self._add_setting(SettingType.FLOAT, "   Scale Min", "/rtx/raytracing/inscattering/noiseScaleRangeMin", -1.0, 5.0, 0.01,
                                      tooltip="\nA range to map the noise values of each noise octave."
                                              "\nTypically these should be 0 and 1."
                                              "\nTo make sparse points in the noise less sparse a higher Min can be used, or a lower Max for dense points to be less dense.")
                    self._add_setting(SettingType.FLOAT, "   Scale Max", "/rtx/raytracing/inscattering/noiseScaleRangeMax", -1.0, 5.0, 0.01,
                                      tooltip="\nA range to map the noise values of each noise octave."
                                              "\nTypically these should be 0 and 1. To make sparse points in the noise less sparse"
                                              "\na higher Min can be used, or a lower Max for dense points to be less dense.")
                    self._add_setting(SettingType.INT, "   Octave Count", "/rtx/raytracing/inscattering/noiseNumOctaves", 1, 8, tooltip="\nA higher octave count results in greater noise detail, at the cost of performance.")

    def destroy(self):
        self._change_cb1 = None
        super().destroy()

class SimpleFogSettingsFrame(SettingsCollectionFrame):
    """ Simple Fog """
    def _frame_setting_path(self):
        return "/rtx/fog/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.COLOR3, "Color", "/rtx/fog/fogColor", tooltip="\nThe color or tint of the fog volume.")
        self._add_setting(SettingType.FLOAT, "Intensity", "/rtx/fog/fogColorIntensity", 1, 1000000, 1, tooltip="\nThe intensity of the fog effect.")
        self._add_setting(SettingType.BOOL, "Height-based Fog - Use +Z Axis", "/rtx/fog/fogZup/enabled", tooltip="\nUse positive Z axis for height-based fog. Otherwise use the positive Y axis.")
        self._add_setting(SettingType.FLOAT, "Height-based Fog - Plane Height", "/rtx/fog/fogStartHeight", -1000000, 1000000, 0.01, tooltip="\nThe starting height (in meters) for height-based fog.")
        self._add_setting(SettingType.FLOAT, "Height Density", "/rtx/fog/fogHeightDensity", 0, 1, 0.001, tooltip="\nDensity of the height-based fog. Higher values result in thicker fog.")
        self._add_setting(SettingType.FLOAT, "Height Falloff", "/rtx/fog/fogHeightFalloff", 0, 1000, 0.002, tooltip="\nRate at which the height-based fog falls off.")
        self._add_setting(SettingType.FLOAT, "Start Distance to Camera", "/rtx/fog/fogStartDist", 0, 1000000, 0.1, tooltip="\nDistance from the camera at which the fog begins.")
        self._add_setting(SettingType.FLOAT, "End Distance to Camera", "/rtx/fog/fogEndDist", 0, 1000000, 0.1, tooltip="\nDistance from the camera at which the fog achieves maximum density.")
        self._add_setting(SettingType.FLOAT, "Distance Density", "/rtx/fog/fogDistanceDensity", 0, 1, 0.001, tooltip="\nThe fog density at the End Distance.")

    def destroy(self):
        super().destroy()

class FlowSettingsFrame(SettingsCollectionFrame):
    """ Flow """
    def _frame_setting_path(self):
        return "/rtx/flow/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Flow in Real-Time Ray Traced Shadows", "/rtx/flow/rayTracedShadowsEnabled")
        self._add_setting(SettingType.BOOL, "Flow in Real-Time Ray Traced Reflections", "/rtx/flow/rayTracedReflectionsEnabled")
        self._add_setting(SettingType.BOOL, "Flow in Real-Time Ray Traced Translucency", "/rtx/flow/rayTracedTranslucencyEnabled")
        self._add_setting(SettingType.BOOL, "Flow in Path-Traced Mode", "/rtx/flow/pathTracingEnabled")
        self._add_setting(SettingType.BOOL, "Flow in Path-Traced Mode Shadows", "/rtx/flow/pathTracingShadowsEnabled")
        self._add_setting(SettingType.BOOL, "Composite with Flow Library Renderer", "/rtx/flow/compositeEnabled")
        self._add_setting(SettingType.BOOL, "Use Flow Library Self Shadow", "/rtx/flow/useFlowLibrarySelfShadow")
        self._add_setting(SettingType.INT, "Max Blocks", "/rtx/flow/maxBlocks")

    def destroy(self):
        super().destroy()

class IndexCompositeSettingsFrame(SettingsCollectionFrame):
    """ NVIDIA IndeX Compositing """

    def __init__(self, frame_label: str, collapsed=True, parent=None) -> None:
        super().__init__(frame_label, collapsed, parent)
        self._update_visibility()
        self._nvindex_compositing_cb = omni.kit.app.SettingChangeSubscription("/nvindex/compositeRenderingAvailable", self._update_visibility)

    def _update_visibility(self, *_):
        # Only show IndeX composite settings if the extension is loaded
        self._widget.visible = carb.settings.get_settings().get("/nvindex/compositeRenderingAvailable")

    def _frame_setting_path(self):
        return "/rtx/index/compositeEnabled"

    def _build_ui(self):
        ui.Label("You can activate IndeX composite rendering for individual Volume or Points prims "
                 "by enabling their 'Use IndeX compositing' property.", word_wrap=True)
        ui.Separator()

        depth_compositing_settings = {
            "Disable": 0,
            "Before Anti-Aliasing": 1,
            "After Anti-Aliasing": 2,
            "After Anti-Aliasing (Stable Depth)": 3
        }

        self._add_setting_combo(
            "Depth Compositing",
            "/rtx/index/compositeDepthMode",
            depth_compositing_settings,
            tooltip="Depth-correct compositing between renderers")

        self._add_setting(
            SettingType.FLOAT,
            "Color Scaling",
            "/rtx/index/colorScale",
            0.0,
            100.0,
            tooltip="Scale factor for color output",
        )

        self._add_setting(
            SettingType.BOOL,
            "sRGB Conversion",
            "/rtx/index/srgbConversion",
            tooltip="Apply color space conversion to IndeX rendering",
        )

        self._add_setting(
            SettingType.FLOAT,
            "Opacity Scaling",
            "/rtx/index/opacityScale",
            0.0,
            1.0,
            tooltip="Scales the opacity of the entire IndeX rendering",
        )

        self._add_setting(
            SettingType.INT,
            "Resolution Scaling",
            "/rtx/index/resolutionScale",
            1,
            100,
            tooltip="Reduces the IndeX rendering resolution (in percent relative to the viewport resolution)",
        )

        self._add_setting(
            SettingType.INT,
            "Rendering Samples",
            "/rtx/index/renderingSamples",
            1,
            32,
            tooltip="Number of samples per pixel used during rendering",
        )

        self._add_setting(
            SettingType.FLOAT,
            "Default Point Width",
            "/rtx/index/defaultPointWidth",
            tooltip="Default point width for new point clouds loaded from USD. If set to 0, a simple heuristic will be used.",
        )

    def destroy(self):
        self._nvindex_compositing_cb = None
        super().destroy()

class GPUResourcesManagement(SettingsCollectionFrame):
    """ GPU Resources Management """
    def _build_ui(self):

        if self._settings.get("/rtx-transient/resourcemanager/enableTextureStreaming"):
            self._add_setting(SettingType.FLOAT, "Texture Streaming Budget Priority", "/rtx/resourcemanager/texturestreaming/gpuBudgetPriority", 0, 1, tooltip="\nSets the priority at which GPU memory is assigned to texture streaming over other memory requests like geometry streaming. \n0 - least priority to texture streaming, 1 - highest priority to texture streaming.")
        if self._settings.get("/rtx-transient/hydra/geometrystreaming/active"):
            self._add_setting(SettingType.FLOAT, "Geometry Streaming Budget Priority", "/rtx/hydra/geometrystreaming/gpuBudgetPriority", 0, 1, tooltip="\nSets the priority at which GPU memory is assigned to geometry streaming over other memory requests like texture streaming. \n0 - least priority to geometry streaming, 1 - highest priority to geometry streaming.")
            self._add_setting(SettingType.INT, "Instance Streaming Budget", "/rtx/hydra/geometrystreaming/instanceBudget", 0, 16000000, tooltip="\nThe most relevant instances among all instances in memory are rendered, up to this instance budget count. \nA high instance count can result in slow top-level acceleration structure (TLAS) construction time, \nmaking performance sub-optimal for real-time rendering.")
            self._change_cb1 = omni.kit.app.SettingChangeSubscription("/UJITSO/geometrystreaming/LODAutogenerate", self._on_change)
            self._add_setting(SettingType.BOOL, "Auto Generation of LODs", "/UJITSO/geometrystreaming/LODAutogenerate", tooltip="\nEnables auto generating LODs when processing geometry.")
            if self._settings.get("/UJITSO/geometrystreaming/LODAutogenerate"):
                self._add_setting(SettingType.FLOAT, "   Reduction factor per LOD level", "/UJITSO/geometrystreaming/LODReductionPerLevel", 0.01, 1.0, tooltip="\nReduction factor per LOD level.")
                self._add_setting(SettingType.INT, "   Vertex count at which to stop generating LODs", "/UJITSO/geometrystreaming/LODStopAtVertexCount", 1, 10000, tooltip="\nVertex count at which to stop at generating LODs.")
                self._add_setting(SettingType.INT, "   Vertex count at which to use cpu parallel decimator", "/UJITSO/geometrystreaming/CpuParallelVertexCountThreshold", 0, 100000000, tooltip="\nVertex count at which to use cpu parallel decimator.")

    def destroy(self):
        self._change_cb1 = None
        super().destroy()

# Check based on the target's name if the pass is related heatmap or not.
# If we are using pass related to heat map, we should add options related to heatmap using "add_heat_map_ui_options".
# This is made into a function so it can be shared with dev_stack.py
def is_debug_view_heatmap(target):
    is_timing_heat_map = target == "timingHeatMap"
    is_any_hit_count_heat_map = target == "anyHitCountHeatMap"
    is_intersection_count_heat_map = target == "intersectionCountHeatMap"
    return is_timing_heat_map or is_any_hit_count_heat_map or is_intersection_count_heat_map

# Add options related to heatmap using "add_heat_map_ui_options".
# This is made into a function so it can be shared with dev_stack.py
def add_heat_map_ui_options(target, settings_frame):
    is_timing_heat_map = target == "timingHeatMap"
    is_any_hit_count_heat_map = target == "anyHitCountHeatMap"
    is_intersection_count_heat_map = target == "intersectionCountHeatMap"

    #  'heat_map_view_items' MUST perfectly match with 'HeatMapSelectablePass' in 'RtxRendererContext.h'
    heat_map_view_items = {
        "GBuffer RT": 1,
        "Path Tracing": 2,
        "Shadow RT": 3,
        "Deferred LTC Lighting RT": 4,
        "Deferred Sampled Lighting RT": 5,
        "Reflections LTC RT ": 6,
        "Reflections Sampled RT": 7,
        "Back Lighting": 8,
        "Translucency RT": 9,
        "SSS RT": 10,
        "Transmission RT": 11,
        "Indirect Diffuse RT (Apply Cache)": 12,
        "Ray Traced Ambient Occlusion": 13
    }

    # 'heat_map_color_palette_items' MUST perfectly match with condition in 'temperature' function in 'DebugView.cs.hlsl'
    heat_map_color_palette_items = {
        "Rainbow": 0,
        "Viridis": 1,
        "Turbo": 2,
        "Plasma": 3
    }

    settings_frame._add_setting_combo("   Pass To Visualize ", "/rtx/debugView/heatMapPass", heat_map_view_items)

    if is_timing_heat_map:
        settings_frame._add_setting(SettingType.FLOAT, "   Maximum Time (µs)", "/rtx/debugView/heatMapMaxTime", 0, 100000.0, 1.0)
    elif is_any_hit_count_heat_map:
        settings_frame._add_setting(SettingType.INT, "   Maximum Any Hit", "/rtx/debugView/heatMapMaxAnyHitCount", 1, 100)
    elif is_intersection_count_heat_map:
        settings_frame._add_setting(SettingType.INT, "   Maximum Intersection", "/rtx/debugView/heatMapMaxIntersectionCount", 1, 100)

    settings_frame._add_setting_combo("   Color Palette", "/rtx/debugView/heatMapColorPalette", heat_map_color_palette_items)
    settings_frame._add_setting(SettingType.BOOL, "   Show Color Bar", "/rtx/debugView/heatMapOverlayHeatMapScale")

def _hsv_to_rgb(h, s, v):
    """Convert HSV color to RGB"""
    if s == 0.0:
        return (v, v, v)

    h = h * 6.0  # H range is [0,1]
    i = int(h)
    f = h - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))

    if i == 0:
        return (v, t, p)
    elif i == 1:
        return (q, v, p)
    elif i == 2:
        return (p, v, t)
    elif i == 3:
        return (p, q, v)
    elif i == 4:
        return (t, p, v)
    else:
        return (v, p, q)

class ViewSettingsFrame(SettingsCollectionFrame):
    """ View Settings"""

    def _on_open_illuminance_bar(self):
        if not hasattr(self, '_illuminance_legend') or self._illuminance_legend is None:
            self._illuminance_legend = ui.Window("RTX - Interactive Illuminance Legend", width=400, height=100)
            self._illuminance_legend.set_visibility_changed_fn(self._on_illum_window_visibility_changed)
            with self._illuminance_legend.frame:
                with ui.VStack():
                    PhotometricHeatmapBarWidget(self._illuminance_legend, 400, 100, 5, "illumination")
        else:
            self._illuminance_legend.visible = True

    def _on_open_luminance_bar(self):
        if not hasattr(self, '_luminance_legend') or self._luminance_legend is None:
            self._luminance_legend = ui.Window("RTX - Interactive Luminance Legend", width=400, height=100)
            self._luminance_legend.set_visibility_changed_fn(self._on_lum_window_visibility_changed)
            with self._luminance_legend.frame:
                with ui.VStack():
                    PhotometricHeatmapBarWidget(self._luminance_legend, 400, 100, 5, "lumination")
        else:
            self._luminance_legend.visible = True

    # TODO Consider disabling update callback when visibility is set to off
    # currently toggle off luminance/illuminance legends they still do the redraw
    # computation that can affect frame rate when they are not used
    # after open for the first time
    def _on_illum_window_visibility_changed(self, val):
        pass

    def _on_lum_window_visibility_changed(self, val):
        pass

    def _on_rebuild_ui_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        """ View Settings """

        with ui.CollapsableFrame("Per-View TLAS", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.BOOL, "Enabled", "/rtx/rendering/perViewTlas",
                                          tooltip="\nRebuild TLAS per view. This is to improve ray intersection precision when cameras"
                                                  "\nare far apart.")

                self._add_setting(SettingType.FLOAT, "Min Separation", "/rtx/rendering/perViewTlasMinSeparation",
                                    tooltip="\nDefine a minimum distance between cameras within wich Per-View TLAS is automatically disabled."
                                            "\nIf a camera is separated from the others more than this minimum distance, Per-View TLAS"
                                            "\nrebuild is enabled for all cameras.")

        with ui.CollapsableFrame("Data Window", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.BOOL, "Fit output to data window", "/rtx/dataWindow/fitOutputToDataWindow", tooltip="\nWhen enabled, the output AOV sizes will match the data window dimensions. Otherwise, they will be set to the display window dimensions.")
                self._add_setting(SettingType.FLOAT, "X Min", "/rtx/dataWindowNDC/0", -1, 2, 0.1, tooltip="X min coordinates, in normalized device coordinates (NDC).")
                self._add_setting(SettingType.FLOAT, "Y Min", "/rtx/dataWindowNDC/1", -1, 2, 0.1, tooltip="Y min coordinates, in normalized device coordinates (NDC).")
                self._add_setting(SettingType.FLOAT, "X Max", "/rtx/dataWindowNDC/2", -1, 2, 0.1, tooltip="X max coordinates, in normalized device coordinates (NDC).")
                self._add_setting(SettingType.FLOAT, "Y Max", "/rtx/dataWindowNDC/3", -1, 2, 0.1, tooltip="Y max coordinates, in normalized device coordinates (NDC).")
                
        with ui.CollapsableFrame("Debug View", height=0):
            with ui.VStack(height=0, spacing=5):
                debug_view_items = {
                    "Off": "",
                    "3D Motion Vectors [WARNING: Flashing Colors]": "targetMotion",
                    "3D Motion Vector Arrows [WARNING: Flashing Colors]": "targetMotionArrows",
                    "3D Final Motion Vector Arrows [WARNING: Flashing Colors]": "finalMotion",
                    "Barycentrics": "barycentrics",
                    "Beauty After Tonemap": "beautyPostTonemap",
                    "Beauty Before Tonemap": "beautyPreTonemap",
                    "Depth": "depth",
                    "Instance ID": "instanceId",
                    "Interpolated Normal": "normal",
                    "Heat Map: Any Hit": "anyHitCountHeatMap",
                    "Heat Map: Intersection": "intersectionCountHeatMap",
                    "Heat Map: Timing": "timingHeatMap",
                    "SDG: Cross Correspondence": "sdgCrossCorrespondence",
                    "SDG: Motion": "sdgMotion",
                    "Semantic ID": "semanticId",
                    "Stable ID": "stableId",
                    "Non-Visual Material ID": "nonVisualMaterialId",
                    "Tangent U": "tangentu",
                    "Tangent V": "tangentv",
                    "Texture Coordinates 0": "texcoord0",
                    "Texture Coordinates 1": "texcoord1",
                    "Triangle Normal": "triangleNormal",
                    "Wireframe": "wire",
                    "RT Ambient Occlusion": "ao",
                    "RT Caustics": "caustics",
                    "RT Diffuse GI": "indirectDiffuse",
                    "RT Diffuse GI (Not Accumulated)": "indirectDiffuseNonAccum",
                    "RT Diffuse Reflectance": "diffuseReflectance",
                    "RT Material Normal": "materialGeometryNormal",
                    "RT Matte Object Compositing Alpha": "matteObjectAlpha",
                    "RT Matte Object Mask": "matteObjectMask",
                    "RT Matte Object View Before Postprocessing": "matteBeforePostprocessing",
                    "RT Radiance": "radiance",
                    "RT Reflections": "reflections",
                    "RT Reflections (Not Accumulated)": "reflectionsNonAccum",
                    "RT Reflections 3D Motion Vectors [WARNING: Flashing Colors]": "reflectionsMotion",
                    "RT Roughness": "roughness",
                    "RT Specular Reflectance": "reflectance",
                    "RT Subsurface Radiance": "subsurface",
                    "RT Subsurface Transmission Radiance": "subsurfaceTransmission",
                    "RT Translucency": "translucency",
                    "RT World Position": "worldPosition",
                    "PT Adaptive Sampling Error [WARNING: Flashing Colors]": "PTAdaptiveSamplingError",
                    "PT Denoised Result": "pathTracerDenoised",
                    "PT Noisy Result": "pathTracerNoisy",
                    "PT Pre-Denoised Result": "aov:ePtPreDenoisedResult",
                    "PT AOV Background": "aov:ePtBackground",
                    "PT AOV Diffuse Filter": "aov:ePtDiffuseFilter",
                    "PT AOV Direct Illumation": "aov:ePtDirectIllumation",
                    "PT AOV Global Illumination": "aov:ePtGlobalIllumination",
                    "PT AOV Illuminance": "aov:ePtIlluminance",
                    "PT AOV Luminance": "aov:ePtLuminance",
                    "PT AOV Motion Vectors": "aov:ePtMotion",
                    "PT AOV Reflections": "aov:ePtReflections",
                    "PT AOV Reflection Filter": "aov:ePtReflectionFilter",
                    "PT AOV Refractions": "aov:ePtRefractions",
                    "PT AOV Refraction Filter": "aov:ePtRefractionFilter",
                    "PT AOV Subsurface Scattering": "aov:ePtSubsurfaceScattering",
                    "PT AOV Subsurface Filter": "aov:ePtSubsurfaceFilter",
                    "PT AOV Self-Illumination": "aov:ePtSelfIllumination",
                    "PT AOV Volumes": "aov:ePtVolumes",
                    "PT AOV World Normal": "aov:ePtWorldNormal",
                    "PT AOV World Position": "aov:ePtWorldPos",
                    "PT AOV View Normal": "aov:ePtViewNormal",
                    "PT AOV Z-Depth": "aov:ePtZDepth",
                    "PT AOV Multimatte0": "PTAOVMultimatte0",
                    "PT AOV Multimatte1": "PTAOVMultimatte1",
                    "PT AOV Multimatte2": "PTAOVMultimatte2",
                    "PT AOV Multimatte3": "PTAOVMultimatte3",
                    "PT AOV Multimatte4": "PTAOVMultimatte4",
                    "PT AOV Multimatte5": "PTAOVMultimatte5",
                    "PT AOV Multimatte6": "PTAOVMultimatte6",
                    "PT AOV Multimatte7": "PTAOVMultimatte7",
                }

                self._add_setting_searchable_combo("Render Target", "/rtx/debugView/target", debug_view_items, "Off", "\nA list of all render passes which can be visualized.")
                debug_view_target = self._settings.get("/rtx/debugView/target")

                # Trigger the combo update to reflect the current selection when the ui is rebuilt
                self._settings.set("/rtx/debugView/target", debug_view_target)

                # Subscribe this frame to the target setting so we can show the heat map controls if necessary.
                # This will remove the subscription from the searchable combo, but we will have a chance to update it
                # because the new callback does a rebuild.

                self._change_debugViewTarget = omni.kit.app.SettingChangeSubscription("/rtx/debugView/target", self._on_rebuild_ui_change)

                currentDebugView = self._settings.get("/rtx/debugView/target")

                if is_debug_view_heatmap(debug_view_target):
                    add_heat_map_ui_options(debug_view_target, self)
                elif currentDebugView == "aov:ePtLuminance":
                    self._add_setting(SettingType.STRING, "   Luminance Value", "/rtx/pathtracing/luminanceVal", tooltip="\nThe luminance value at the last clicked position")
                    self._add_setting(SettingType.BOOL, "   Display Luminance As Heatmap", "/rtx/pathtracing/displayLuminanceAsHeatmap", tooltip="\nDisplay luminance aov as heatmap")

                    self._add_setting(SettingType.BOOL, "      Auto Range", "/rtx/pathtracing/luminanceAutoRange", tooltip="\nEnable/disable auto range")
                    self._change_luminanceAutoRange = omni.kit.app.SettingChangeSubscription("/rtx/pathtracing/luminanceAutoRange", self._on_rebuild_ui_change)

                    if self._settings.get("/rtx/pathtracing/luminanceAutoRange") == True:
                        self._add_setting(SettingType.FLOAT, "         Range Min", "/rtx/pathtracing/luminanceMin", tooltip="Min luminance range value for luminance aov heatmap mode")
                        self._add_setting(SettingType.FLOAT, "         Range Max", "/rtx/pathtracing/luminanceMax", tooltip="Max luminance range value for luminance aov heatmap mode")
                    else:
                        self._add_setting(SettingType.FLOAT, "      Range Min", "/rtx/pathtracing/luminanceUserMin", tooltip="User min luminance range value for luminance aov heatmap mode")
                        self._add_setting(SettingType.FLOAT, "      Range Max", "/rtx/pathtracing/luminanceUserMax", tooltip="User max luminance range value for luminance aov heatmap mode")
                    with ui.HStack():
                        ui.Button("Show Luminance Legend", clicked_fn=self._on_open_luminance_bar)
                elif currentDebugView == "aov:ePtIlluminance":
                    self._add_setting(SettingType.STRING, "   Illuminance Value", "/rtx/pathtracing/illuminanceVal", tooltip="\nThe illuminance value at the last clicked position")
                    self._add_setting(SettingType.BOOL, "   Display Illuminance As Heatmap", "/rtx/pathtracing/displayIlluminanceAsHeatmap", tooltip="\nDisplay illuminance aov as heatmap")

                    self._add_setting(SettingType.BOOL, "      Auto Range", "/rtx/pathtracing/illuminanceAutoRange", tooltip="\nEnable/disable auto range")
                    self._change_illuminanceAutoRange = omni.kit.app.SettingChangeSubscription("/rtx/pathtracing/illuminanceAutoRange", self._on_rebuild_ui_change)

                    if self._settings.get("/rtx/pathtracing/illuminanceAutoRange") == True:
                        self._add_setting(SettingType.FLOAT, "         Range Min", "/rtx/pathtracing/illuminanceMin", tooltip="Min illuminance range value for illuminance aov heatmap mode")
                        self._add_setting(SettingType.FLOAT, "         Range Max", "/rtx/pathtracing/illuminanceMax", tooltip="Max illuminance range value for illuminance aov heatmap mode")
                    else:
                        self._add_setting(SettingType.FLOAT, "      Range Min", "/rtx/pathtracing/illuminanceUserMin", tooltip="User min illuminance range value for illuminance aov heatmap mode")
                        self._add_setting(SettingType.FLOAT, "      Range Max", "/rtx/pathtracing/illuminanceUserMax", tooltip="User max illuminance range value for illuminance aov heatmap mode")
                    with ui.HStack():
                        ui.Button("Show Illuminance Legend", clicked_fn=self._on_open_illuminance_bar)
                elif currentDebugView == "nonVisualMaterialId":
                    with ui.VStack(height=0, spacing=5):
                        # enable pixel debug
                        self._add_setting(SettingType.BOOL, "Enable Pixel Debug", "/rtx/debugView/pixelDebug/enabled", tooltip="\nEnable pixel debug")
                        self._settings.set("/rtx/debugView/pixelDebug/debugAsUint", True)
                        # Create checkboxes for base materials (first 48 bits)
                        material_names = [
                            "None", "Aluminum", "Steel", "Oxidized Steel", "Iron",
                            "Oxidized Iron", "Silver", "Brass", "Bronze",
                            "Oxidized Bronze Patina", "Tin", "Plastic", "Fiberglass",
                            "Carbon Fiber", "Vinyl", "Plexiglass", "PVC", "Nylon",
                            "Polyester", "Clear Glass", "Frosted Glass", "One Way Mirror",
                            "Mirror", "Ceramic Glass", "Asphalt", "Concrete",
                            "Leaf Grass", "Dead Leaf Grass", "Rubber", "Wood", "Bark",
                            "Cardboard", "Paper", "Fabric", "Skin", "Fur Hair",
                            "Leather", "Marble", "Brick", "Stone", "Gravel", "Dirt",
                            "Mud", "Water", "Salt Water", "Snow", "Ice",
                            "Calibration Lambertian"
                        ]

                        def create_material_checkbox(i, name):
                            if i < 32:
                                bit_pos = i
                                bitfield_path = "/rtx/debugView/nonVisualMaterialIdBitfield0"
                            else:
                                bit_pos = i - 32
                                bitfield_path = "/rtx/debugView/nonVisualMaterialIdBitfield1"
                            current_bit = (self._settings.get(bitfield_path) & (1 << bit_pos)) != 0

                            with ui.HStack():
                                def make_clicked_fn(index=bit_pos, path=bitfield_path):
                                    def on_clicked(model):
                                        new_value = self._settings.get(path)
                                        if model.get_value_as_bool():
                                            new_value |= (1 << index)
                                        else:
                                            new_value &= ~(1 << index)
                                        self._settings.set(path, new_value)
                                    return on_clicked

                                checkbox = ui.CheckBox(width=20, height=20)
                                checkbox.model.set_value(current_bit)
                                checkbox.model.add_value_changed_fn(make_clicked_fn())

                                # Add color box
                                hue = (i % 50) / 50.0
                                r, g, b = _hsv_to_rgb(0.0, 1.0, 1.0) if (i == 0) else _hsv_to_rgb(hue, 0.8, 1.0)
                                r = int(r * 255)
                                g = int(g * 255) << 8
                                b = int(b * 255) << 16
                                a = 255 << 24
                                with ui.ZStack(width=20, height=20):
                                    ui.Rectangle(style={
                                        "background_color": (r+g+b+a),
                                        "border_radius": 3,
                                        "margin": 2
                                    })
                                ui.Label(f"{i} {name}")

                        # Create checkboxes for base materials (first 48 bits)
                        with ui.CollapsableFrame("Base Material Filter", height=0):
                            with ui.HStack(height=0):
                                # Left column
                                with ui.VStack(height=0, spacing=5):
                                    for i in range(0, len(material_names)//2):
                                        create_material_checkbox(i, material_names[i])

                                # Right column
                                with ui.VStack(height=0, spacing=5):
                                    for i in range(len(material_names)//2, len(material_names)):
                                        create_material_checkbox(i, material_names[i])

                        with ui.HStack(height=0):
                            # Coating Filter (next 4 bits, last bit reserved)
                            with ui.CollapsableFrame("Coating Filter", height=0):
                                with ui.VStack(height=0, spacing=5):
                                    coating_names = [
                                        "None", "Paint", "Clearcoat"
                                    ]

                                    for i, name in enumerate(coating_names):
                                        current_bit = (self._settings.get("/rtx/debugView/nonVisualMaterialIdBitfield1") & (1 << (i + 16))) != 0
                                        with ui.HStack():
                                            def make_clicked_fn(index=i):
                                                def on_clicked(model):
                                                    new_value = self._settings.get("/rtx/debugView/nonVisualMaterialIdBitfield1")
                                                    if model.get_value_as_bool():
                                                        new_value |= (1 << (index + 16))   # Set bit, offset by 16 for coatings
                                                    else:
                                                        new_value &= ~(1 << (index + 16))  # Clear bit
                                                    self._settings.set("/rtx/debugView/nonVisualMaterialIdBitfield1", new_value)
                                                return on_clicked
                                            checkbox = ui.CheckBox(width=20, height=20)
                                            checkbox.model.set_value(current_bit)
                                            checkbox.model.add_value_changed_fn(make_clicked_fn())
                                            ui.Label(name)

                            # Attribute Filter (next 6 bits, last bit reserved)
                            with ui.CollapsableFrame("Attribute Filter", height=0):
                                with ui.VStack(height=0, spacing=5):
                                    attribute_names = [
                                        "None", "Emissive", "Retroreflective", "Single Sided", "Visually Transparent"
                                    ]

                                    for i, name in enumerate(attribute_names):
                                        current_bit = (self._settings.get("/rtx/debugView/nonVisualMaterialIdBitfield1") & (1 << (i + 20))) != 0
                                        with ui.HStack():
                                            def make_clicked_fn(index=i):
                                                def on_clicked(model):
                                                    new_value = self._settings.get("/rtx/debugView/nonVisualMaterialIdBitfield1")
                                                    if model.get_value_as_bool():
                                                        new_value |= (1 << (index + 20))   # Set bit, offset by 20 for attributes
                                                    else:
                                                        new_value &= ~(1 << (index + 20))  # Clear bit
                                                    self._settings.set("/rtx/debugView/nonVisualMaterialIdBitfield1", new_value)
                                                return on_clicked
                                            checkbox = ui.CheckBox(width=20, height=20)
                                            checkbox.model.set_value(current_bit)
                                            checkbox.model.add_value_changed_fn(make_clicked_fn())
                                            ui.Label(name)
                else:
                    self._add_setting(SettingType.FLOAT, "   Output Value Scaling", "/rtx/debugView/scaling", -1000000, 1000000, 1.0, tooltip="\nScales the output value by this factor. Useful to accentuate differences.")

    def destroy(self):
        if hasattr(self, '_illuminance_legend') and self._illuminance_legend:
            self._illuminance_legend.destroy()
            self._illuminance_legend = None
        if hasattr(self, '_luminance_legend') and self._luminance_legend:
            self._luminance_legend.destroy()
            self._luminance_legend = None
        self._change_debugViewTarget = None
        self._change_luminanceAutoRange = None
        self._change_illuminanceAutoRange = None
        super().destroy()

class DebugSettingsFrame(SettingsCollectionFrame):
    """ Debug """
    def _build_ui(self):

        with ui.CollapsableFrame("Streaming Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx-transient/resourcemanager/enableTextureStreaming", self._on_change)
                self._add_setting(SettingType.BOOL, "Texture Streaming (toggling requires scene reload)", "/rtx-transient/resourcemanager/enableTextureStreaming", tooltip="\nEnables texture streaming.")
                if self._settings.get("/rtx-transient/resourcemanager/enableTextureStreaming"):
                    self._add_setting(SettingType.FLOAT, "Texture Streaming Budget (% of GPU memory)", "/rtx-transient/resourcemanager/texturestreaming/memoryBudget", 0, 1, tooltip="\nLimits the GPU memory budget used for texture streaming.")
                    self._add_setting(SettingType.INT, "Texture Streaming Budget Per Request (in MB)", "/rtx-transient/resourcemanager/texturestreaming/streamingBudgetMB", 0, 10000,
                        tooltip="\nMaximum budget per streaming request. 0 = unlimited but could lead to stalling during streaming."
                                "\nHigh or unlimited budget could lead to stalling during streaming.")
                if self._settings.get("/rtx-transient/hydra/geometrystreaming/active"):
                    self._add_setting(SettingType.INT, "Geometry Streaming Budget Per Request (in MB)", "/rtx-transient/hydra/geometrystreaming/streamingBudgetMB", 0, 10000,
                    tooltip="\nMaximum budget per streaming request. 0 = unlimited but could lead to stalling during streaming."
                            "\nHigh or unlimited budget could lead to stalling during streaming.")

        with ui.CollapsableFrame("Materials", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.BOOL, "Disable Material Loading", "/app/renderer/skipMaterialLoading", tooltip="\nScenes will be loaded without materials. This can lower scene loading time.")

        qualitySettings = {
                "Fastest": 0,
                "Normal": 1,
                "Production": 2,
                "Highest" : 3
            }

        # The setting is maxMipCount, to make it more user friendly we expose it in the API as max resolution
        texture_mip_sizes = {
            "64": 7,
            "128": 8,
            "256": 9,
            "512": 10,
            "1024": 11,
            "2048": 12,
            "4096": 13,
            "8192": 14,
            "16384": 15,
            "32768": 16,
        }

        with ui.CollapsableFrame("Texture Compression Settings", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting_combo("Texture Compression Quality", "/rtx-transient/materialdb/blockCompression/quality", qualitySettings)
                self._add_setting(SettingType.INT, "Compression Size Threshold", "/rtx-transient/resourcemanager/compressionMipSizeThreshold", 0, 8192, tooltip="\nTextures smaller than this size won't be compressed. 0 disables compression.")
                self._add_setting_combo("Max Resolution", "/rtx-transient/resourcemanager/maxMipCount", texture_mip_sizes,
                    tooltip="\nTextures larger than this will be downsampled at this resolution."
                            "\nTo programmatically set the value, these are the corresponding int to max resolution values:"
                            "\n7 = 64, 8 = 128, 9 = 256, 10 = 512, 11 = 1024, 12 = 2048, 13 = 4096, 14 = 8192, 15 = 16384, 16 = 32768")
                self._add_setting(SettingType.BOOL, "Normal Map Mip-Map Generation (toggling requires scene reload)", "/rtx-transient/resourcemanager/genMipsForNormalMaps", tooltip="\nEnables mip-map generation for normal maps to reduce memory usage at the expense of quality.")
                if self._settings.get("/rtx-transient/resourcemanager/genMipsForNormalMaps"):
                    self._add_setting(SettingType.BOOL, "Normal Map Roughness generation (toggling requires scene reload)", "/rtx-transient/resourcemanager/createNormalRoughness", tooltip="\nEnables roughness generation for normal maps for improved specular reflection with mip mapping enabled.")
                self._add_setting_combo("Dome Light Texture Compression Quality", "/rtx-transient/domeLight/blockCompression/quality", qualitySettings)

    def destroy(self):
        self._change_cb1 = None
        super().destroy()

class CommonSettingStack(RTXSettingsStack):

    def __init__(self) -> None:
        self._stack = ui.VStack(spacing=7, identifier=__class__.__name__)
        with self._stack:
            GeometrySettingsFrame("Geometry", parent=self)
            MaterialsSettingsFrame("Materials", parent=self)
            BackgroundSettingsFrame("Background", parent=self)
            LightingSettingsFrame("Lighting", parent=self)
            SimpleFogSettingsFrame("Simple Fog", parent=self)
            GlobalVolumetricEffectsSettingsFrame("Global Volumetric Effects", parent=self)
            FlowSettingsFrame("Flow", parent=self)
            IndexCompositeSettingsFrame("NVIDIA IndeX Compositing", parent=self)
            GPUResourcesManagement("GPU Resources Management", parent=self)
            ViewSettingsFrame("View", parent=self)
            DebugSettingsFrame("Debug", parent=self)
