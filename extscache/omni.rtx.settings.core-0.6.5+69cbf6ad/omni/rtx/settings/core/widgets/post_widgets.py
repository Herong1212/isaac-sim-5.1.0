import omni.kit.app
import omni.ui as ui
from omni.kit.widget.settings import SettingType
from omni.rtx.window.settings.rtx_settings_stack import RTXSettingsStack
from omni.rtx.window.settings.settings_collection_frame import SettingsCollectionFrame
import carb.settings


class ToneMappingSettingsFrame(SettingsCollectionFrame):
    """ Tone Mapping """
    def _on_tonemap_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        # The main tonemapping layout contains only the combo box. All the other options
        # are saved in a different layout which can be swapped out in case the tonemapper changes.
        tonemapper_ops = [
            "Clamp",
            "Linear (Off)",
            "Reinhard",
            "Modified Reinhard",
            "HejlHableAlu",
            "HableUc2",
            "Aces",
            "Iray",
        ]
        self._add_setting_combo("Tone Mapping Operator", "/rtx/post/tonemap/op", tonemapper_ops,
                tooltip="\nTone Mapping Operator selector."
                "\n-Clamp: Leaves the radiance values unchanged, skipping any exposure adjustment."
                "\n-Linear (Off): Applies the exposure adjustments but leaves the tone values otherwise unchanged."
                "\n-Reinhard: Operator based on Erik Reinhard's tone mapping work."
                "\n-Modified Reinhard: Variation of the operator based on Erik Reinhard's tone mapping work."
                "\n-HejiHableAlu: John Hable's ALU approximation of Jim Heji's operator."
                "\n-HableUC2: John Hable's Uncharted 2 filmic tone map."
                "\n-ACES: Operator based on the Academy Color Encoding System."
                "\n-Iray: Reinhard-based operator that matches the operator used by NVIDIA Iray by default.")

        tonemapOpIdx = self._settings.get("/rtx/post/tonemap/op")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/post/tonemap/op", self._on_change)

        if tonemapOpIdx == 3:  # Modified Reinhard
            self._add_setting(SettingType.FLOAT, "   Max White Luminance", "/rtx/post/tonemap/maxWhiteLuminance", 0, 100, tooltip="\nMaximum HDR luminance value that will map to 1.0 post tonemap.")

        if tonemapOpIdx == 5:  # HableUc2
            self._add_setting(SettingType.FLOAT, "   White Scale Value", "/rtx/post/tonemap/whiteScale", 0, 100, tooltip="\nMaximum white value that will map to 1.0 post tonemap.")

        if tonemapOpIdx == 7:  # Iray
            self._add_setting(SettingType.FLOAT, "   Crush Blacks", "/rtx/post/tonemap/irayReinhard/crushBlacks", 0, 1, 0.02)
            self._add_setting(SettingType.FLOAT, "   Burn Highlights", "/rtx/post/tonemap/irayReinhard/burnHighlights", 0, 1, 0.02)
            self._add_setting(SettingType.BOOL, "   Burn Highlights per Component", "/rtx/post/tonemap/irayReinhard/burnHighlightsPerComponent")
            self._add_setting(SettingType.BOOL, "   Burn Highlights max Component", "/rtx/post/tonemap/irayReinhard/burnHighlightsMaxComponent")
            self._add_setting(SettingType.FLOAT, "   Saturation", "/rtx/post/tonemap/irayReinhard/saturation", 0, 1, 0.02)

        if tonemapOpIdx != 0:  # Clamp is never using srgb conversion
            self._add_setting(SettingType.BOOL, "   SRGB To Gamma Conversion", "/rtx/post/tonemap/enableSrgbToGamma", tooltip="\nAvailable with Linear/Reinhard/Modified Reinhard/HejiHableAlu/HableUc2 Tone Mapping.")

        self._add_setting(SettingType.FLOAT, "cm^2 Factor", "/rtx/post/tonemap/cm2Factor", 0, 2, tooltip="\nUse this factor to adjust for scene units being different from centimeters.")
        self._add_setting(SettingType.FLOAT, "Film ISO", "/rtx/post/tonemap/filmIso", 50, 1600, tooltip="\nSimulates the effect on exposure of a camera's ISO setting.")
        self._add_setting(SettingType.FLOAT, "Camera Exposure", "/rtx/post/tonemap/exposureTime", 0.0000000000001, 2.0, tooltip="\nCamera exposure time in seconds.")
        self._add_setting(SettingType.FLOAT, "F-stop", "/rtx/post/tonemap/fNumber", 1, 20, 0.1, tooltip="\nSimulates the effect on exposure of a camera's f-stop aperture.")
        self._add_setting(SettingType.COLOR3, "White Point", "/rtx/post/tonemap/whitepoint", tooltip="\nA color mapped to white on the output.")

        tonemapColorMode = ["sRGBLinear", "ACEScg"]
        self._add_setting_combo("Tone Mapping Color Space", "/rtx/post/tonemap/colorMode", tonemapColorMode, tooltip="\nTone Mapping Color Space selector.")
        self._add_setting(SettingType.FLOAT, "Wrap Value", "/rtx/post/tonemap/wrapValue", 0, 100000, tooltip="\nOffset")
        self._add_setting(SettingType.FLOAT, "Dither strength", "/rtx/post/tonemap/dither", 0, .02, .001, tooltip="\nRemoves banding artifacts in final images.")

    def destroy(self):
        self._change_cb = None
        super().destroy()

class OpenColorIoSettingsFrame(SettingsCollectionFrame):
    """ OpenColorIO """

    def __init__(self, frame_label: str, collapsed=True, parent=None) -> None:
        SettingsCollectionFrame.__init__(self, frame_label, collapsed, parent)

        self._change_cb_config_changed = None
        self._change_cb_display_changed = None

    def destroy(self):
        self._change_cb_config_changed = None
        self._change_cb_display_changed = None
        super().destroy()

    def _build_ui(self):
        self._change_cb_config_changed = None
        self._change_cb_display_changed = None

        self._add_setting(SettingType.BOOL, "Enable OpenColorIO", "/rtx/post/tonemap/ocio/enabled", tooltip="\nEnable color management based on OpenColorIO.")

        self._change_cb_config_changed = omni.kit.app.SettingChangeSubscription("/rtx/post/tonemap/ocio/cfgFilePath", self._on_change)
        self._change_cb_display_changed = omni.kit.app.SettingChangeSubscription("/rtx/post/tonemap/ocio/currentDisplay", self._on_change)

        self._add_setting("ASSET", "Config Path", "/rtx/post/tonemap/ocio/cfgFilePath", tooltip="\nThe path to an OpenColorIO configuration file.\nUse 'studio-config-latest' or 'cg-config-latest' for latest internal OpenColorIO default configurations.")

        cfg_file = str(self._settings.get("/rtx/post/tonemap/ocio/cfgFilePath"))

        current_display = str(self._settings.get("/rtx/post/tonemap/ocio/currentDisplay"))
        current_view = str(self._settings.get("/rtx/post/tonemap/ocio/currentView"))
        current_look = str(self._settings.get("/rtx/post/tonemap/ocio/currentLook"))

        # The currently selected display. The display determines which views are available.
        display_idx = -1
        displays = []
        views = []
        looks = dict()

        if not cfg_file:
            # Config file text box is empty. No further UI.
            return

        import omni.ocio as ocio

        ocio_ctx = ocio.get_context(cfg_file)
        if not ocio_ctx:
            carb.log_error(f"Failed to retrieve ocio context for config '{cfg_file}'")
            return
        if True:
            default_display = ocio.get_default_display_name(ocio_ctx)
            default_view = ocio.get_default_view_name(ocio_ctx, default_display)
            display_count = ocio.get_display_count(ocio_ctx)

            for i in range(display_count):
                display_name = str(ocio.get_display_name(ocio_ctx, i))
                displays.append(display_name)
                disp_views = dict()

                view_count = ocio.get_view_count(ocio_ctx, i)
                for k in range(view_count):
                    view_name = str(ocio.get_view_name(ocio_ctx, i, k))
                    disp_views[view_name] = view_name

                views.append(disp_views)

                if display_name == current_display:
                    display_idx = i

            look_count = ocio.get_look_count(ocio_ctx)
            for i in range(look_count):
                look_name = str(ocio.get_look_name(ocio_ctx, i))
                looks[look_name] = look_name

            if display_idx == -1:
                if default_display:
                    display_idx = displays.index(default_display)
                else:
                    # arbitrarily choose the first one
                    display_idx = 0

        ocio.release_context(ocio_ctx)

        # More info on 'Displays and Views' here: https://opencolorio.readthedocs.io/en/latest/guides/authoring/displays_views.html
        self._add_setting_combo("Display", "/rtx/post/tonemap/ocio/currentDisplay", displays, allow_non_items=True, tooltip="\nDisplay device that this image is presented on. Examples: 'sRGB' for artist workstations, 'DCIP3' for screening room projectors.")
        if display_idx != -1:
            self._add_setting_combo("View", "/rtx/post/tonemap/ocio/currentView", views[display_idx], allow_non_items=True, tooltip="\nView for this Display Device. Examples: 'Film' for final projected result, 'Log' for log-space pixel values, 'Raw' for data.")

        if looks:
            # If there are any looks, allow to select no look at all.
            looks["None"] = str()
            self._add_setting_combo("Look", "/rtx/post/tonemap/ocio/currentLook", looks, allow_non_items=True, tooltip="\nArtistic image modification in a specified image state.")
        else:
            ui.Label("No Looks available", alignment=ui.Alignment.CENTER)


class AutoExposureSettingsFrame(SettingsCollectionFrame):
    """ Auto Exposure """
    def _frame_setting_path(self):
        return "/rtx/post/histogram/enabled"

    def _build_ui(self):
        histFilter_types = ["Median", "Average"]
        self._add_setting_combo("Histogram Filter", "/rtx/post/histogram/filterType", histFilter_types, tooltip="\nSelect a method to filter the histogram. Options are Median and Average.")
        self._add_setting(SettingType.FLOAT, "Adaptation Speed", "/rtx/post/histogram/tau", 0.5, 10.0, 0.01, tooltip="\nHow fast automatic exposure compensation adapts to changes in overall light intensity.")
        self._add_setting(SettingType.FLOAT, "White Point Scale", "/rtx/post/histogram/whiteScale", 0.01, 80.0, 0.001,
                tooltip="\nControls how bright of an image the auto-exposure should aim for."
                        "\nLower values result in brighter images, higher values result in darker images.")

        self._add_setting(SettingType.BOOL, "Exposure Value Clamping", "/rtx/post/histogram/useExposureClamping", tooltip="\nClamps the exposure to a range within a specified minimum and maximum Exposure Value.")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/post/histogram/useExposureClamping", self._on_change)
        if self._settings.get("/rtx/post/histogram/useExposureClamping"):
            self._add_setting(SettingType.FLOAT, "   Minimum Value", "/rtx/post/histogram/minEV", 0.0, 1000000.0, 1, tooltip="\nClamps the exposure to a range within a specified minimum and maximum Exposure Value.")
            self._add_setting(SettingType.FLOAT, "   Maximum Value", "/rtx/post/histogram/maxEV", 0.0, 1000000.0, 1, tooltip="\nClamps the exposure to a range within a specified minimum and maximum Exposure Value.")
            # self._add_setting(SettingType.FLOAT, "Min Log Luminance", "/rtx/post/histogram/minloglum", -15, 5.0, 0.001)
            # self._add_setting(SettingType.FLOAT, "Log Luminance Range", "/rtx/post/histogram/loglumrange", 0.00001, 50.0, 0.001)

    def destroy(self):
        self._change_cb = None
        super().destroy()

class ColorCorrectionSettingsFrame(SettingsCollectionFrame):
    """ Color Correction """
    def _frame_setting_path(self):
        return "/rtx/post/colorcorr/enabled"

    def _on_colorcorrect_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        mode = ["ACES (Pre-Tonemap)", "Standard (Post-Tonemap)"]
        self._add_setting_combo("Mode", "/rtx/post/colorcorr/mode", mode, tooltip="\nChoose between ACES (Pre-Tone mapping) or Standard (Post-Tone mapping) mode.")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/post/colorcorr/mode", self._on_change)
        colorCorrectionMode = ["sRGBLinear", "ACEScg"]
        if self._settings.get("/rtx/post/colorcorr/mode") == 0:
            self._add_setting_combo("   Output Color Space", "/rtx/post/colorcorr/outputMode", colorCorrectionMode,
                    tooltip="\nDefines the color space used as output of Color Correction."
                            "\nsRGB Linear: scene linear space"
                            "\nAcesCG: ACES CG color space")
        self._add_setting(SettingType.COLOR3, "Saturation", "/rtx/post/colorcorr/saturation", tooltip="\nHigher values increase color saturation while lowering desaturates.")
        self._add_setting(SettingType.COLOR3, "Contrast", "/rtx/post/colorcorr/contrast", 0, 10, 0.005, tooltip="\nHigher values increase the contrast of darks/lights and colors.")
        self._add_setting(SettingType.COLOR3, "Gamma", "/rtx/post/colorcorr/gamma", 0.2, 10, 0.005, tooltip="\nGamma value in inverse gamma curve applied before output.")
        self._add_setting(SettingType.COLOR3, "Gain", "/rtx/post/colorcorr/gain", 0, 10, 0.005, tooltip="\nA factor applied to the color values.")
        self._add_setting(SettingType.COLOR3, "Offset", "/rtx/post/colorcorr/offset", -1, 1, 0.001, tooltip="\nAn offset applied to the color values.")

    def destroy(self):
        self._change_cb = None
        super().destroy()

class ColorGradingSettingsFrame(SettingsCollectionFrame):
    """ Color Grading """
    def _frame_setting_path(self):
        return "/rtx/post/colorgrad/enabled"

    def _on_colorgrade_change(self, *_):
        self._rebuild()

    def _build_ui(self):
        mode = ["ACES (Pre-Tonemap)", "Standard (Post-Tonemap)"]
        self._add_setting_combo("Mode", "/rtx/post/colorgrad/mode", mode, tooltip="\nChoose between ACES (Pre-Tonemap) or Standard (Post-Tonemap) Mode.")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/post/colorgrad/mode", self._on_change)
        colorGradingMode = ["sRGBLinear", "ACEScg"]
        if self._settings.get("/rtx/post/colorgrad/mode") == 0:
            self._add_setting_combo("   Output Color Space", "/rtx/post/colorgrad/outputMode", colorGradingMode,
                tooltip="\nChoose between ACES (Pre-Tonemap) or Standard (Post-Tonemap) Mode."
                "\nsRGB Linear: scene linear space"
                "\nAcesCG: ACES CG color space")
        self._add_setting(SettingType.COLOR3, "Black Point", "/rtx/post/colorgrad/blackpoint", -1, 1, 0.005, tooltip="\nDefines the Black Point value.")
        self._add_setting(SettingType.COLOR3, "White Point", "/rtx/post/colorgrad/whitepoint", 0, 10, 0.005, tooltip="\nDefines the White Point value.")
        self._add_setting(SettingType.COLOR3, "Contrast", "/rtx/post/colorgrad/contrast", 0, 10, 0.005, tooltip="\nHigher values increase the contrast of darks/lights and colors.")
        self._add_setting(SettingType.COLOR3, "Lift", "/rtx/post/colorgrad/lift", -10, 10, 0.005, tooltip="\nColor is multiplied by (Lift - Gain) and later Lift is added back.")
        self._add_setting(SettingType.COLOR3, "Gain", "/rtx/post/colorgrad/gain", 0, 10, 0.005, tooltip="\nColor is multiplied by (Lift - Gain) and later Lift is added back.")
        self._add_setting(SettingType.COLOR3, "Multiply", "/rtx/post/colorgrad/multiply", 0, 10, 0.005, tooltip="\nA factor applied to the color values.")
        self._add_setting(SettingType.COLOR3, "Offset", "/rtx/post/colorgrad/offset", -1, 1, 0.001, tooltip="\nColor offset: an offset applied to the color values.")
        self._add_setting(SettingType.COLOR3, "Gamma", "/rtx/post/colorgrad/gamma", 0.2, 10, 0.005, tooltip="\nGamma value in inverse gamma curve applied before output.")

    def destroy(self):
        self._change_cb = None
        super().destroy()

class MatteObjectSettingsFrame(SettingsCollectionFrame):
    def _frame_setting_path(self):
        return "/rtx/matteObject/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Shadow Catcher", "/rtx/post/matteObject/enableShadowCatcher",
                tooltip="\nTreats all matte objects as shadow catchers. Matte objects receives only shadow and "
                        "\nnot reflections or GI which improves rendering performance." )
        self._add_setting(SettingType.BOOL, "Ambient Shadow Catcher", "/rtx/matteObject/enableAmbientShadowCatcher",
                tooltip="\nIn Real-time mode, treats all matte objects as ambient shadow catchers. Matte objects only receive ambient occlusion.")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/matteObject/enableAmbientShadowCatcher", self._on_change)
        if self._settings.get("/rtx/matteObject/enableAmbientShadowCatcher"):
            self._add_setting(SettingType.FLOAT, "   Ease Factor", "/rtx/matteObject/ambientShadowCatcherFactor", 0.01, 5.0, 100, tooltip="\nRaise the AO strength to the power of this setting value.")
        self._add_setting(SettingType.FLOAT, "Matte Object Fade Out", "/rtx/matteObject/blend/fadeOut", 0.0, 1.0, 0.01, tooltip="\nTo allow matte object gradually blend into the background.")
        self._add_setting(SettingType.FLOAT, "Matte Object Composite Shift", "/rtx/matteObject/blend/shift", 0.0, 1.0, 0.01, tooltip="\nManually bias the matte object compositing so that it blends into the background better.")
        self._add_setting(SettingType.FLOAT, "Matte Object Composite Contrast", "/rtx/matteObject/blend/contrast", 0.0, 1.0, 0.01, tooltip="\nManually increase the contrast of matte shadow.")

    def destroy(self):
        self._change_cb = None
        super().destroy()

class CompositingSettingsFrame(SettingsCollectionFrame):
    def _frame_setting_path(self):
        return "/rtx/post/backgroundZeroAlpha/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Composite in Editor", "/rtx/post/backgroundZeroAlpha/backgroundComposite",
                tooltip="\nEnables alpha compositing with a backplate texture, instead of outputting the rendered image "
                        "\nwith an alpha channel, such as when saved to EXR or when to streamed to a Cloud XR stream.")
        self._add_setting(SettingType.BOOL, "Output Alpha in Composited Image", "/rtx/post/backgroundZeroAlpha/outputAlphaInComposite",
                tooltip="\nOutputs the matte compositing alpha in the composited image."
                        "\nOnly activates when not compositing in editor."
                        "\nThis option can interfere with DLSS, producing jaggied edges.")
        self._add_setting(SettingType.BOOL, "Output Black Background in Composited Image", "/rtx/post/backgroundZeroAlpha/blackBackgroundInComposite",
                tooltip="\nOutputs a black background in the composited image."
                        "\nOnly activates when not compositing in editor.")
        self._add_setting(SettingType.BOOL, "Multiply Color Value by Alpha in Composited Image", "/rtx/post/backgroundZeroAlpha/premultiplyColorByAlpha",
                tooltip="\nWhen enabled, the RGB color will be RGB * alpha.")
        ''''
        self._add_setting(SettingType.COLOR3, "Backplate Color", "/rtx/post/backgroundZeroAlpha/backgroundDefaultColor", tooltip="\nA constant color used if no backplate texture is set.")
        self._add_setting("ASSET", "Backplate Texture", "/rtx/post/backgroundZeroAlpha/backplateTexture", tooltip="\nThe path to a texture to use as a backplate.")
        self._add_setting(SettingType.BOOL, "   Is linear", "/rtx/post/backgroundZeroAlpha/backplateTextureIsLinear", tooltip="\nSets the color space for the Backplate Texture to linear space.")
        sampler_ops = { "Repeat": 0, "Mirror": 1, "Clamp": 2 }
        self._add_setting_combo("   UV Sampler", "/rtx/post/backgroundZeroAlpha/backplateTextureMode", sampler_ops,
                tooltip="\nRepeat: The texture UV value will get modulated with 1."
                "\nMirror: The UV value will get modulated by 2 then mirrored by x=1 and y=1."
                "\nClamp: The UV value will get clampped to [0, 1]."
                )
        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/post/backgroundZeroAlpha/backplateTextureMode", self._on_change)

        self._add_setting(SettingType.FLOAT, "   Luminance Scale", "/rtx/post/backgroundZeroAlpha/backplateLuminanceScaleV2", tooltip="\nScales the Backplate luminance.")
        '''
        self._add_setting(SettingType.BOOL, "Lens Distortion", "/rtx/post/backgroundZeroAlpha/enableLensDistortionCorrection",
                tooltip="\nEnables distortion of the rendered image using a set of lens distortion and undistortion maps."
                        "\nEach of these should refer to a <UDIM> EXR texture set, containing one image for each"
                        "\nof the discrete focal length values specified in the array of float settings under"
                        "\n/rtx/post/lensDistortion/lensFocalLengthArray (not currently exposed).")
        self._change_cb = omni.kit.app.SettingChangeSubscription("/rtx/post/backgroundZeroAlpha/enableLensDistortionCorrection", self._on_change)
        if self._settings.get("/rtx/post/backgroundZeroAlpha/enableLensDistortionCorrection"):
            self._add_setting("ASSET", "   Distortion Map", "/rtx/post/lensDistortion/distortionMap", tooltip="\n<UDIM> EXR texture path to store the distortion maps for specified focal lengths.")
            self._add_setting("ASSET", "   Undistortion Map", "/rtx/post/lensDistortion/undistortionMap", tooltip="\n<UDIM> EXR texture path to store the un-distortion maps for specified focal lengths.")

    def destroy(self):
        self._change_cb = None
        self._change_cb1 = None
        super().destroy()

class ChromaticAberrationSettingsFrame(SettingsCollectionFrame):
    """ Chromatic Aberration """
    def _frame_setting_path(self):
        return "/rtx/post/chromaticAberration/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.FLOAT, "Strength Red", "/rtx/post/chromaticAberration/strengthR", -1.0, 1.0, 0.01, tooltip="\nThe strength of the distortion applied on the Red channel.")
        self._add_setting(SettingType.FLOAT, "Strength Green", "/rtx/post/chromaticAberration/strengthG", -1.0, 1.0, 0.01, tooltip="\nThe strength of the distortion applied on the Green channel.")
        self._add_setting(SettingType.FLOAT, "Strength Blue", "/rtx/post/chromaticAberration/strengthB", -1.0, 1.0, 0.01, tooltip="\nThe strength of the distortion applied on the Blue channel.")
        chromatic_aberration_ops = ["Radial", "Barrel"]
        self._add_setting_combo("Algorithm Red", "/rtx/post/chromaticAberration/modeR", chromatic_aberration_ops, tooltip="\nSelects between Radial and Barrel distortion for the Red channel.")
        self._add_setting_combo("Algorithm Green", "/rtx/post/chromaticAberration/modeG", chromatic_aberration_ops, tooltip="\nSelects between Radial and Barrel distortion for the Green channel.")
        self._add_setting_combo("Algorithm Blue", "/rtx/post/chromaticAberration/modeB", chromatic_aberration_ops, tooltip="\nSelects between Radial and Barrel distortion for the Blue channel.")
        self._add_setting(SettingType.BOOL, "Use Lanczos Sampler", "/rtx/post/chromaticAberration/enableLanczos", tooltip="\nUse a Lanczos sampler when sampling the input image being distorted.")

        with ui.CollapsableFrame("Boundary Blending", height=0):
            with ui.VStack(height=0, spacing=5):
                self._add_setting(SettingType.BOOL, "Repeat Mirrored", "/rtx/post/chromaticAberration/mirroredRepeat", tooltip="\nEnables mirror repeat for texture lookups in out-of-lens regions. When disabled, out-of-lens regions are black.")
                self._add_setting(SettingType.FLOAT, "Blend Region Size", "/rtx/post/chromaticAberration/boundaryBlendRegionSize", 0.0, 1.0, 0.01, tooltip="\nDetermines the blend region size.")
                self._add_setting(SettingType.FLOAT, "Blend Region Falloff", "/rtx/post/chromaticAberration/boundaryBlendFalloff", 0.001, 5.0, 0.001, tooltip="\nDetermines the falloff in the blending region.")

class DepthOfFieldSettingsFrame(SettingsCollectionFrame):
    """ Depth of Field Camera Overrides """
    def _frame_setting_path(self):
        return "/rtx/post/dof/overrideEnabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Enable DOF", "/rtx/post/dof/enabled", tooltip="\nEnables Depth of Field. If disabled, camera parameters affecting Depth of Field are ignored.")
        self._add_setting(SettingType.FLOAT, "Subject Distance", "/rtx/post/dof/subjectDistance", -10000, 10000.0, tooltip="\nObjects at this distance from the camera will be in focus.")
        self._add_setting(SettingType.FLOAT, "Focal Length (mm)", "/rtx/post/dof/focalLength", 0, 1000, tooltip="\nThe focal length of the lens (in mm). The focal length divided by the f-stop is the aperture diameter.")
        self._add_setting(SettingType.FLOAT, "F-stop", "/rtx/post/dof/fNumber", 0, 1000, tooltip="\nF-stop (aperture) of the lens. Lower f-stop numbers decrease the distance range from the Subject Distance where objects remain in focus.")
        self._add_setting(SettingType.FLOAT, "Anisotropy", "/rtx/post/dof/anisotropy", -1, 1, 0.01, tooltip="\nAnisotropy of the lens. A value of -0.5 simulates the depth of field of an anamorphic lens.")


class MotionBlurSettingsFrame(SettingsCollectionFrame):
    """ Motion Blur """
    def _frame_setting_path(self):
        return "/rtx/post/motionblur/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.FLOAT, "Blur Diameter Fraction", "/rtx/post/motionblur/maxBlurDiameterFraction", 0, 0.5, 0.01, tooltip="\nThe fraction of the largest screen dimension to use as the maximum motion blur diameter.")
        self._add_setting(SettingType.FLOAT, "Exposure Fraction", "/rtx/post/motionblur/exposureFraction", 0, 5.0, 0.01, tooltip="\nExposure time fraction in frames (1.0 = one frame duration) to sample.")
        self._add_setting(SettingType.INT, "Number of Samples", "/rtx/post/motionblur/numSamples", 4, 32, 1, tooltip="\nNumber of samples to use in the filter. A higher number improves quality at the cost of performance.")

class DepthSensorSettingsFrame(SettingsCollectionFrame):
    """ Depth Sensor """
    def _frame_setting_path(self):
        return "/rtx/post/depthSensor/enabled"
    def _build_ui(self):
        self._add_setting(SettingType.FLOAT, "Baseline", "/rtx/post/depthSensor/baselineMM", -200, 200, tooltip="\nHorizontal baseline of the stereo pair in mm.")
        self._add_setting(SettingType.FLOAT, "Focal Length", "/rtx/post/depthSensor/focalLengthPixel", 0, 5000, tooltip="\nFocal length of the lens in pixels.")
        self._add_setting(SettingType.FLOAT, "Sensor Size", "/rtx/post/depthSensor/sensorSizePixel", 0, 5000, tooltip="\nFull sensor size in pixels.")
        self._add_setting(SettingType.FLOAT, "Max disparity", "/rtx/post/depthSensor/maxDisparityPixel", 0, 512, tooltip="\nMax disparity in pixels.")
        self._add_setting(SettingType.FLOAT, "Disparity Noise Mean", "/rtx/post/depthSensor/noiseMean", -10, 10, tooltip="\nMean for disparity/depth noise.")
        self._add_setting(SettingType.FLOAT, "Disparity Noise Sigma", "/rtx/post/depthSensor/noiseSigma", -10, 10, tooltip="\nStandard deviation for disparity/depth noise.")
        self._add_setting(SettingType.FLOAT, "Disparity Noise Downscale", "/rtx/post/depthSensor/noiseDownscaleFactorPixel", 1, 10, tooltip="\nScale for disparity/depth noise.")
        self._add_setting(SettingType.FLOAT, "Disparity Confidence", "/rtx/post/depthSensor/confidenceThreshold", 0, 1, tooltip="\nConfidence of disparity.")
        self._add_setting(SettingType.BOOL, "Outlier Removal", "/rtx/post/depthSensor/outlierRemovalEnabled", tooltip="\nLone invalid or valid depth pixels will be made to match neighbors.")
        self._add_setting(SettingType.FLOAT, "Min Distance", "/rtx/post/depthSensor/minDistance", 0, 1000, tooltip="\nMinimum distance to consider for disparity/depth in meters.")
        self._add_setting(SettingType.FLOAT, "Max Distance", "/rtx/post/depthSensor/maxDistance", 0, 1000, tooltip="\nMaximum distance to consider for disparity/depth in meters.")
        depthSensorRgbDepthOutputMode_types = ["LDRColor", "1m Sawtooth", "Grayscale Min-Max", "Rainbow Min-Max", "Depth (input)", "Depth (reprojected with confidence)", "Confidence Map", "Disparity"]
        self._add_setting_combo("RGB Depth Output Mode", "/rtx/post/depthSensor/rgbDepthOutputMode", depthSensorRgbDepthOutputMode_types, tooltip="\nSets the output to the color buffers.")
        self._add_setting(SettingType.BOOL, "Show distance", "/rtx/post/depthSensor/showDistance", tooltip="\nShow the distance at the center of the view.")


class FFTBloomSettingsFrame(SettingsCollectionFrame):
    """ FFT Bloom """
    def _frame_setting_path(self):
        return "/rtx/post/lensFlares/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.FLOAT, "Scale", "/rtx/post/lensFlares/flareScale", -1000, 1000, tooltip="\nOverall intensity of the bloom effect.")
        self._add_setting(SettingType.DOUBLE3, "Cutoff Point", "/rtx/post/lensFlares/cutoffPoint", tooltip="\nA cutoff color value to tune the radiance range for which Bloom will have any effect. ")
        self._add_setting(SettingType.FLOAT, "Cutoff Fuzziness", "/rtx/post/lensFlares/cutoffFuzziness", 0.0, 1.0,
            tooltip="\nIf greater than 0, defines the width of a 'fuzzy cutoff' region around the Cutoff Point values."
                    "\nInstead of a sharp cutoff, a smooth transition between 0 and the original values is used.")
        self._add_setting(SettingType.FLOAT, "Alpha channel scale", "/rtx/post/lensFlares/alphaExposureScale", 0.0, 100.0, tooltip="\nAlpha channel intensity of the bloom effect.")
        self._add_setting(SettingType.BOOL, "Energy Constrained", "/rtx/post/lensFlares/energyConstrainingBlend", tooltip="\nConstrains the total light energy generated by bloom.")
        self._add_setting(SettingType.BOOL, "Physical Model", "/rtx/post/lensFlares/physicalSettings", tooltip="\nChoose between a Physical or Non-Physical bloom model.")
        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/post/lensFlares/physicalSettings", self._on_change)
        if self._settings.get("/rtx/post/lensFlares/physicalSettings") == 1:
            self._add_setting(SettingType.BOOL, "   Circular Aperture", "/rtx/post/lensFlares/apertureShapeCircular", tooltip="\nMake the aperture a circular instead of a bladed iris.")
            self._change_cb2 = omni.kit.app.SettingChangeSubscription("/rtx/post/lensFlares/apertureShapeCircular", self._on_change)
            if self._settings.get("/rtx/post/lensFlares/apertureShapeCircular") == False:
                self._add_setting(SettingType.INT, "   Blades", "/rtx/post/lensFlares/blades", 3, 10, tooltip="\nThe number of physical blades of a simulated camera diaphragm causing the bloom effect. Values less than 3 will result in a circular aperture.")
            self._add_setting(SettingType.FLOAT, "   Aperture Rotation", "/rtx/post/lensFlares/apertureRotation", -1000, 1000, tooltip="\nRotation of the camera diaphragm.")
            self._add_setting(SettingType.FLOAT, "   Sensor Diagonal", "/rtx/post/lensFlares/sensorDiagonal", -1000, 1000, tooltip="\nDiagonal of the simulated sensor.")
            self._add_setting(SettingType.FLOAT, "   Sensor Aspect Ratio", "/rtx/post/lensFlares/sensorAspectRatio", -1000, 1000, tooltip="\nAspect ratio of the simulated sensor, results in the bloom effect stretching in one direction.")
            self._add_setting(SettingType.FLOAT, "   F-stop", "/rtx/post/lensFlares/fNumber", -1000, 1000, tooltip="\nIncreases/Decreases the sharpness of the bloom effect.")
            self._add_setting(SettingType.FLOAT, "   Focal Length (mm)", "/rtx/post/lensFlares/focalLength", -1000, 1000, tooltip="\nFocal length of the lens modeled to simulate the bloom effect.")
            self._add_setting(SettingType.FLOAT, "   Noise Strength", "/rtx/post/lensFlares/noiseStrength", 0, 1, tooltip="\nStrength of scattered noise in the aperture. Results in small random bright spots over entire view and reduces starburst.")
            self._add_setting(SettingType.FLOAT, "   Dust Strength", "/rtx/post/lensFlares/dustStrength", 0, 1, tooltip="\nStrength of simulated dust noise. Results in random bright spots in bloom starburst")
            self._add_setting(SettingType.FLOAT, "   Scratch Strength", "/rtx/post/lensFlares/scratchStrength", 0, 1, tooltip="\nStrength of simulated scratch noise. Results in random bright lines in bloom starburst")
            self._add_setting(SettingType.INT, "   Spectral Blur Samples", "/rtx/post/lensFlares/spectralBlurSamples", 0, 50, tooltip="\nNumber of samples to use in spectral blur. Set to 0 to disable.")
            self._add_setting(SettingType.FLOAT, "      Blur Scaling", "/rtx/post/lensFlares/spectralBlurIntensity", 0, 1000, tooltip="\nNon-physical scaling of blur output to maintain visual parity with non-blur output.")
            self._add_setting(SettingType.DOUBLE3, "      Blur Wavelength range (nm)", "/rtx/post/lensFlares/spectralBlurWavelengthRange", 100, 1000, tooltip="\nThe minimum, center, and maximum wavelength of the spectral blur effect.")
        else:
            self._add_setting(SettingType.DOUBLE3, "   Halo Radius", "/rtx/post/lensFlares/haloFlareRadius", tooltip="\nControls the size of each RGB component of the halo flare effect.")
            self._add_setting(SettingType.DOUBLE3, "   Halo Flare Falloff", "/rtx/post/lensFlares/haloFlareFalloff", tooltip="\nControls the falloff of each RGB component of the halo flare effect.")
            self._add_setting(SettingType.FLOAT, "   Halo Flare Weight", "/rtx/post/lensFlares/haloFlareWeight", -1000, 1000, tooltip="\nControls the intensity of the halo flare effect.")
            self._add_setting(SettingType.DOUBLE3, "   Aniso Falloff Y", "/rtx/post/lensFlares/anisoFlareFalloffY", tooltip="\nControls the falloff of each RGB component of the anistropic flare effect in the X direction.")
            self._add_setting(SettingType.DOUBLE3, "   Aniso Falloff X", "/rtx/post/lensFlares/anisoFlareFalloffX", tooltip="\nControls the falloff of each RGB component of the anistropic flare effect in the Y direction.")
            self._add_setting(SettingType.FLOAT, "   Aniso Flare Weight", "/rtx/post/lensFlares/anisoFlareWeight", -1000, 1000, tooltip="\nControl the intensity of the anisotropic flare effect.")
            self._add_setting(SettingType.DOUBLE3, "   Isotropic Flare Falloff", "/rtx/post/lensFlares/isotropicFlareFalloff", tooltip="\nControls the falloff of each RGB component of the isotropic flare effect.")
            self._add_setting(SettingType.FLOAT, "   Isotropic Flare Weight", "/rtx/post/lensFlares/isotropicFlareWeight", -1000, 1000, tooltip="\nControl the intensity of the isotropic flare effect.")
        lensflareDebugVisMode_types = ["Off", "Aperture", "Starburst"]
        self._add_setting_combo("Visualization", "/rtx/post/lensFlares/debugVisMode", lensflareDebugVisMode_types, tooltip="\nOutput visualization of aperture.")

    def destroy(self):
        self._change_cb1 = None
        self._change_cb2 = None
        super().destroy()


class TVNoiseGrainSettingsFrame(SettingsCollectionFrame):
    """ TV Noise | Film Grain """
    def _frame_setting_path(self):
        return "/rtx/post/tvNoise/enabled"

    def _build_ui(self):
        self._add_setting(SettingType.BOOL, "Enable Scanlines", "/rtx/post/tvNoise/enableScanlines", tooltip="\nEmulates a Scanline Distortion typical of old televisions.")
        self._change_cb1 = omni.kit.app.SettingChangeSubscription("/rtx/post/tvNoise/enableScanlines", self._on_change)
        if self._settings.get("/rtx/post/tvNoise/enableScanlines"):
            self._add_setting(SettingType.FLOAT, "   Scanline Spreading", "/rtx/post/tvNoise/scanlineSpread", 0.0, 2.0, 0.01, tooltip="\nHow wide the Scanline distortion will be.")
        self._add_setting(SettingType.BOOL, "Enable Scroll Bug", "/rtx/post/tvNoise/enableScrollBug", tooltip="\nEmulates sliding typical on old televisions.")
        self._add_setting(SettingType.BOOL, "Enable Vignetting", "/rtx/post/tvNoise/enableVignetting", tooltip="\nBlurred darkening around the screen edges.")
        self._change_cb2 = omni.kit.app.SettingChangeSubscription("/rtx/post/tvNoise/enableVignetting", self._on_change)
        if self._settings.get("/rtx/post/tvNoise/enableVignetting"):
            self._add_setting(SettingType.FLOAT, "   Vignetting Size", "/rtx/post/tvNoise/vignettingSize", 0.0, 255, tooltip="\nControls the size of vignette region.")
            self._add_setting(SettingType.FLOAT, "   Vignetting Strength", "/rtx/post/tvNoise/vignettingStrength", 0.0, 2.0, 0.01, tooltip="\nControls the intensity of the vignette.")
            self._add_setting(SettingType.BOOL, "   Enable Vignetting Flickering", "/rtx/post/tvNoise/enableVignettingFlickering", tooltip="\nEnables a slight flicker effect on the vignette.")
        self._add_setting(SettingType.BOOL, "Enable Ghost Flickering", "/rtx/post/tvNoise/enableGhostFlickering", tooltip="\nIntroduces a blurred flicker to help emulate an old television.")
        self._add_setting(SettingType.BOOL, "Enable Wavy Distortion", "/rtx/post/tvNoise/enableWaveDistortion", tooltip="\nIntroduces a Random Wave Flicker to emulate an old television.")
        self._add_setting(SettingType.BOOL, "Enable Vertical Lines", "/rtx/post/tvNoise/enableVerticalLines", tooltip="\nIntroduces random vertical lines to emulate an old television.")
        self._add_setting(SettingType.BOOL, "Enable Random Splotches", "/rtx/post/tvNoise/enableRandomSplotches", tooltip="\nIntroduces random splotches typical of old dirty television.")

        self._add_setting(SettingType.BOOL, "Enable Film Grain", "/rtx/post/tvNoise/enableFilmGrain", tooltip="\nEnables a film grain effect to emulate the graininess in high speed (ISO) film.")
        # Filmgrain is a subframe in TV Noise
        self._change_cb3 = omni.kit.app.SettingChangeSubscription("/rtx/post/tvNoise/enableFilmGrain", self._on_change)
        if self._settings.get("/rtx/post/tvNoise/enableFilmGrain"):
            self._add_setting(SettingType.FLOAT, "   Grain Amount", "/rtx/post/tvNoise/grainAmount", 0, 0.2, 0.002, tooltip="\nThe intensity of the film grain effect.")
            self._add_setting(SettingType.FLOAT, "   Color Amount", "/rtx/post/tvNoise/colorAmount", 0, 1.0, 0.02, tooltip="\nThe amount of color offset each grain will be allowed to use.")
            self._add_setting(SettingType.FLOAT, "   Luminance Amount", "/rtx/post/tvNoise/lumAmount", 0, 1.0, 0.02, tooltip="\nThe amount of offset in luminance each grain will be allowed to use.")
            self._add_setting(SettingType.FLOAT, "   Grain Size", "/rtx/post/tvNoise/grainSize", 1.5, 2.5, 0.02, tooltip="\nThe size of the film grains.")

    def destroy(self):
        self._change_cb1 = None
        self._change_cb2 = None
        self._change_cb3 = None
        super().destroy()


class ReshadeSettingsFrame(SettingsCollectionFrame):
    """ ReShade """
    def _frame_setting_path(self):
        return "/rtx/reshade/enable"

    def _build_ui(self):
        self._add_setting("ASSET", "Preset File Path", "/rtx/reshade/presetFilePath", tooltip="\nThe path to a preset.init file containing the Reshade preset to use.")
        widget = self._add_setting("ASSET", "Effect search dir path", "/rtx/reshade/effectSearchDirPath", tooltip="\nThe path to a directory containing the Reshade files that the preset can reference.")
        widget.is_folder=True
        widget = self._add_setting("ASSET", "Texture search dir path", "/rtx/reshade/textureSearchDirPath", tooltip="\nThe path to a directory containing the Reshade texture files that the preset can reference.")
        widget.is_folder=True


class PostSettingStack(RTXSettingsStack):
    def __init__(self) -> None:
        self._stack = ui.VStack(spacing=7, identifier=__class__.__name__)
        with self._stack:
            ToneMappingSettingsFrame("Tone Mapping", parent=self)
            OpenColorIoSettingsFrame("OpenColorIO", parent=self)
            AutoExposureSettingsFrame("Auto Exposure", parent=self)
            ColorCorrectionSettingsFrame("Color Correction", parent=self)
            ColorGradingSettingsFrame("Color Grading", parent=self)
            CompositingSettingsFrame("Compositing", parent=self)
            MatteObjectSettingsFrame("Matte Object", parent=self)
            ChromaticAberrationSettingsFrame("Chromatic Aberration", parent=self)
            DepthOfFieldSettingsFrame("Depth of Field Camera Overrides", parent=self)
            MotionBlurSettingsFrame("Motion Blur", parent=self)
            DepthSensorSettingsFrame("Depth Sensor", parent=self)
            FFTBloomSettingsFrame("FFT Bloom", parent=self)
            TVNoiseGrainSettingsFrame("TV Noise & Film Grain", parent=self)
            ReshadeSettingsFrame("ReShade", parent=self)
            ui.Spacer()
