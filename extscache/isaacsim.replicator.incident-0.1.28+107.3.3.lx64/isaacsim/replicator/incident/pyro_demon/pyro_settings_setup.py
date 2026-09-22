import omni.kit.commands
import omni.usd
import carb
from pxr import Sdf


def setup_pyro_settings():
    stage = omni.usd.get_context().get_stage()
    prim_path = "/World/flowSimulate"
    if stage.GetPrimAtPath(prim_path):
        carb.log_info("flowSimulate already exists, using pre-existing settings")
        return
    success, prim = omni.kit.commands.execute("FlowCreatePrim", prim_path=prim_path, type_name="FlowSimulate")
    if not success:
        carb.log_error("Failed to create flowSimulate")
        return

    omni.kit.commands.execute("ChangeSetting", path="rtx/flow/enabled", value=True)
    omni.kit.commands.execute("ChangeSetting", path="rtx/flow/rayTracedReflectionsEnabled", value=True)
    omni.kit.commands.execute("ChangeSetting", path="rtx/flow/rayTracedTranslucencyEnabled", value=True)
    omni.kit.commands.execute("ChangeSetting", path="rtx/flow/pathTracingEnabled", value=True)

    # Basic simulation settings
    prim.CreateAttribute("autoCellSize", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("blockMinLifetime", Sdf.ValueTypeNames.UInt).Set(4)
    prim.CreateAttribute("clearOnRescale", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("densityCellSize", Sdf.ValueTypeNames.Float).Set(0.05)
    prim.CreateAttribute("enableHighPrecisionDensity", Sdf.ValueTypeNames.Bool, custom=True).Set(False)
    prim.CreateAttribute("enableHighPrecisionVelocity", Sdf.ValueTypeNames.Bool, custom=True).Set(False)
    prim.CreateAttribute("enableLowPrecisionDensity", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("enableLowPrecisionRescale", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("enableLowPrecisionVelocity", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("enableSmallBlocks", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("enableVariableTimeStep", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("forceClear", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("forceDisableCoreSimulation", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("forceDisableEmitters", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("forceSimulate", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("interpolateTimeSteps", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("layer", Sdf.ValueTypeNames.Int).Set(3)
    prim.CreateAttribute("level", Sdf.ValueTypeNames.Int).Set(0)
    prim.CreateAttribute("levelCellSizeMultiplier", Sdf.ValueTypeNames.Float).Set(0.5)
    prim.CreateAttribute("levelCount", Sdf.ValueTypeNames.Int).Set(1)
    prim.CreateAttribute("maxStepsPerSimulate", Sdf.ValueTypeNames.UInt).Set(1)
    prim.CreateAttribute("physicsCollisionEnabled", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("physicsConvexCollision", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("simulateWhenPaused", Sdf.ValueTypeNames.Bool).Set(False)
    prim.CreateAttribute("stepsPerSecond", Sdf.ValueTypeNames.Float).Set(60)
    prim.CreateAttribute("timeScale", Sdf.ValueTypeNames.Float).Set(1)
    prim.CreateAttribute("velocitySubSteps", Sdf.ValueTypeNames.UInt).Set(1)

    # Setup advection combustion parameters
    advection_prim = stage.GetPrimAtPath(f"{prim_path}/advection")
    if advection_prim:
        advection_prim.CreateAttribute("buoyancyMaxSmoke", Sdf.ValueTypeNames.Float).Set(1)
        advection_prim.CreateAttribute("buoyancyPerSmoke", Sdf.ValueTypeNames.Float).Set(0)
        advection_prim.CreateAttribute("buoyancyPerTemp", Sdf.ValueTypeNames.Float).Set(2)
        advection_prim.CreateAttribute("burnPerTemp", Sdf.ValueTypeNames.Float).Set(4)
        advection_prim.CreateAttribute("combustionEnabled", Sdf.ValueTypeNames.Bool).Set(True)
        advection_prim.CreateAttribute("coolingRate", Sdf.ValueTypeNames.Float).Set(1.5)
        advection_prim.CreateAttribute("divergencePerBurn", Sdf.ValueTypeNames.Float).Set(0)
        advection_prim.CreateAttribute("downsampleEnabled", Sdf.ValueTypeNames.Bool).Set(True)
        advection_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool).Set(True)
        advection_prim.CreateAttribute("forceFadeEnabled", Sdf.ValueTypeNames.Bool).Set(False)
        advection_prim.CreateAttribute("fuelPerBurn", Sdf.ValueTypeNames.Float).Set(0.25)
        advection_prim.CreateAttribute("globalFetch", Sdf.ValueTypeNames.Bool).Set(False)
        advection_prim.CreateAttribute("gravity", Sdf.ValueTypeNames.Float3).Set((0, 0, -9.81))
        advection_prim.CreateAttribute("ignitionTemp", Sdf.ValueTypeNames.Float).Set(0.05)
        advection_prim.CreateAttribute("smokePerBurn", Sdf.ValueTypeNames.Float).Set(3)
        advection_prim.CreateAttribute("tempPerBurn", Sdf.ValueTypeNames.Float).Set(5)

        # Setup channel parameters
        channels = {
            "velocity": {"damping": 0.01, "fade": 0.01},
            "divergence": {"damping": 0.01, "fade": 1.0},
            "temperature": {"damping": 0, "fade": 0},
            "fuel": {"damping": 0, "fade": 0},
            "burn": {"damping": 0, "fade": 0},
            "smoke": {"damping": 0.3, "fade": 0.65},
        }

        for channel, params in channels.items():
            channel_prim = stage.GetPrimAtPath(f"{prim_path}/advection/{channel}")
            if channel_prim:
                channel_prim.CreateAttribute("damping", Sdf.ValueTypeNames.Float).Set(params["damping"])
                channel_prim.CreateAttribute("fade", Sdf.ValueTypeNames.Float).Set(params["fade"])
                blend_factor = 0.9 if channel not in ["velocity", "divergence"] else 0.5
                channel_prim.CreateAttribute("secondOrderBlendFactor", Sdf.ValueTypeNames.Float).Set(blend_factor)
                channel_prim.CreateAttribute("secondOrderBlendThreshold", Sdf.ValueTypeNames.Float).Set(0.001)

    # Setup vorticity parameters
    vorticity_prim = stage.GetPrimAtPath(f"{prim_path}/vorticity")
    if vorticity_prim:
        vorticity_prim.CreateAttribute("burnMask", Sdf.ValueTypeNames.Float).Set(0)
        vorticity_prim.CreateAttribute("constantMask", Sdf.ValueTypeNames.Float).Set(0)
        vorticity_prim.CreateAttribute("densityMask", Sdf.ValueTypeNames.Float).Set(0)
        vorticity_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool).Set(True)
        vorticity_prim.CreateAttribute("forceScale", Sdf.ValueTypeNames.Float).Set(0.6)
        vorticity_prim.CreateAttribute("fuelMask", Sdf.ValueTypeNames.Float).Set(0)
        vorticity_prim.CreateAttribute("smokeMask", Sdf.ValueTypeNames.Float).Set(0)
        vorticity_prim.CreateAttribute("temperatureMask", Sdf.ValueTypeNames.Float).Set(0)
        vorticity_prim.CreateAttribute("velocityLinearMask", Sdf.ValueTypeNames.Float).Set(0)
        vorticity_prim.CreateAttribute("velocityLogScale", Sdf.ValueTypeNames.Float).Set(100)
        vorticity_prim.CreateAttribute("velocityMask", Sdf.ValueTypeNames.Float).Set(1)

    # Setup pressure parameters
    pressure_prim = stage.GetPrimAtPath(f"{prim_path}/pressure")
    if pressure_prim:
        pressure_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool).Set(True)

    # Setup summary allocation parameters
    summary_prim = stage.GetPrimAtPath(f"{prim_path}/summaryAllocate")
    if summary_prim:
        summary_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool).Set(True)
        summary_prim.CreateAttribute("enableNeighborAllocation", Sdf.ValueTypeNames.Bool).Set(True)
        summary_prim.CreateAttribute("smokeThreshold", Sdf.ValueTypeNames.Float).Set(0.02)
        summary_prim.CreateAttribute("speedThreshold", Sdf.ValueTypeNames.Float).Set(1)
        summary_prim.CreateAttribute("speedThresholdMinSmoke", Sdf.ValueTypeNames.Float).Set(0)

    # Create and setup flowOffscreen prim
    success, offscreen_prim = omni.kit.commands.execute(
        "FlowCreatePrim", prim_path="/World/flowOffscreen", type_name="FlowOffscreen"
    )
    if success:
        offscreen_prim.CreateAttribute("layer", Sdf.ValueTypeNames.Int).Set(3)
        offscreen_prim.CreateAttribute("level", Sdf.ValueTypeNames.Int).Set(0)

        # Setup shadow parameters
        shadow_prim = stage.GetPrimAtPath("/World/flowOffscreen/shadow")
        if shadow_prim:
            shadow_prim.CreateAttribute("attenuation", Sdf.ValueTypeNames.Float).Set(100)
            shadow_prim.CreateAttribute("coarsePropagate", Sdf.ValueTypeNames.Bool).Set(True)
            shadow_prim.CreateAttribute("colormapXMax", Sdf.ValueTypeNames.Float).Set(1)
            shadow_prim.CreateAttribute("colormapXMin", Sdf.ValueTypeNames.Float).Set(0)
            shadow_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool).Set(True)
            shadow_prim.CreateAttribute("enableRawMode", Sdf.ValueTypeNames.Bool).Set(False)
            shadow_prim.CreateAttribute("isPointLight", Sdf.ValueTypeNames.Bool).Set(False)
            shadow_prim.CreateAttribute("lightDirection", Sdf.ValueTypeNames.Float3).Set((-1, 1, 1))
            shadow_prim.CreateAttribute("lightPosition", Sdf.ValueTypeNames.Float3).Set((0, 0, 0))
            shadow_prim.CreateAttribute("minIntensity", Sdf.ValueTypeNames.Float).Set(0.02)
            shadow_prim.CreateAttribute("numSteps", Sdf.ValueTypeNames.UInt).Set(16)
            shadow_prim.CreateAttribute("rawModeIsosurface", Sdf.ValueTypeNames.Bool).Set(True)
            shadow_prim.CreateAttribute("rawModeNormalize", Sdf.ValueTypeNames.Bool).Set(True)
            shadow_prim.CreateAttribute("stepOffsetScale", Sdf.ValueTypeNames.Float).Set(1)
            shadow_prim.CreateAttribute("stepSizeScale", Sdf.ValueTypeNames.Float).Set(0.75)

        # Setup debug volume parameters
        debug_prim = stage.GetPrimAtPath("/World/flowOffscreen/debugVolume")
        if debug_prim:
            debug_prim.CreateAttribute("applyPreShadow", Sdf.ValueTypeNames.Bool, custom=True).Set(False)
            debug_prim.CreateAttribute("enabled", Sdf.ValueTypeNames.Bool).Set(True)
            debug_prim.CreateAttribute("enableDivergenceAsSmoke", Sdf.ValueTypeNames.Bool).Set(False)
            debug_prim.CreateAttribute("enableSpeedAsTemperature", Sdf.ValueTypeNames.Bool).Set(False)
            debug_prim.CreateAttribute("enableVelocityAsDensity", Sdf.ValueTypeNames.Bool).Set(False)
            debug_prim.CreateAttribute("outputBurnOffset", Sdf.ValueTypeNames.Float).Set(0)
            debug_prim.CreateAttribute("outputBurnScale", Sdf.ValueTypeNames.Float).Set(1)
            debug_prim.CreateAttribute("outputFuelOffset", Sdf.ValueTypeNames.Float).Set(0)
            debug_prim.CreateAttribute("outputFuelScale", Sdf.ValueTypeNames.Float).Set(1)
            debug_prim.CreateAttribute("outputScaleBySmoke", Sdf.ValueTypeNames.Bool).Set(False)
            debug_prim.CreateAttribute("outputSmokeOffset", Sdf.ValueTypeNames.Float).Set(0)
            debug_prim.CreateAttribute("outputSmokeScale", Sdf.ValueTypeNames.Float).Set(1)
            debug_prim.CreateAttribute("outputTemperatureOffset", Sdf.ValueTypeNames.Float).Set(0)
            debug_prim.CreateAttribute("outputTemperatureScale", Sdf.ValueTypeNames.Float).Set(1)
            debug_prim.CreateAttribute("slicePlane", Sdf.ValueTypeNames.Float4).Set((1, 0, 0, 0))
            debug_prim.CreateAttribute("slicePlaneThickness", Sdf.ValueTypeNames.Float).Set(0)
            debug_prim.CreateAttribute("velocityScale", Sdf.ValueTypeNames.Float3).Set((0.01, 0.01, 0.01))

        # Setup colormap parameters
        colormap_prim = stage.GetPrimAtPath("/World/flowOffscreen/colormap")
        if colormap_prim:
            colormap_prim.CreateAttribute("colorScale", Sdf.ValueTypeNames.Float).Set(2.5)
            colormap_prim.CreateAttribute("colorScalePoints", Sdf.ValueTypeNames.FloatArray).Set([1, 1, 1, 1, 1, 1])
            colormap_prim.CreateAttribute("resolution", Sdf.ValueTypeNames.UInt).Set(32)
            colormap_prim.CreateAttribute("rgbaPoints", Sdf.ValueTypeNames.Float4Array).Set(
                [
                    (0.0154, 0.0177, 0.0154, 0.004902),
                    (0.03575, 0.03575, 0.03575, 0.504902),
                    (0.03575, 0.03575, 0.03575, 0.504902),
                    (1, 0.1594, 0.0134, 0.8),
                    (13.53, 2.99, 0.12599, 0.8),
                    (78, 39, 6.1, 0.7),
                ]
            )
            colormap_prim.CreateAttribute("xPoints", Sdf.ValueTypeNames.FloatArray).Set([0, 0.05, 0.15, 0.6, 0.85, 1])

    # Create and setup flowRender prim
    success, render_prim = omni.kit.commands.execute(
        "FlowCreatePrim", prim_path="/World/flowRender", type_name="FlowRender"
    )
    if success:
        render_prim.CreateAttribute("layer", Sdf.ValueTypeNames.Int).Set(3)
        render_prim.CreateAttribute("level", Sdf.ValueTypeNames.Int).Set(0)

        # Setup ray march parameters
        raymarch_prim = stage.GetPrimAtPath("/World/flowRender/rayMarch")
        if raymarch_prim:
            raymarch_prim.CreateAttribute("attenuation", Sdf.ValueTypeNames.Float).Set(50)
            raymarch_prim.CreateAttribute("colormapXMax", Sdf.ValueTypeNames.Float).Set(1)
            raymarch_prim.CreateAttribute("colormapXMin", Sdf.ValueTypeNames.Float).Set(0)
            raymarch_prim.CreateAttribute("colorScale", Sdf.ValueTypeNames.Float).Set(1)
            raymarch_prim.CreateAttribute("enableBlockWireframe", Sdf.ValueTypeNames.Bool).Set(False)
            raymarch_prim.CreateAttribute("enableRawMode", Sdf.ValueTypeNames.Bool).Set(False)
            raymarch_prim.CreateAttribute("rawModeIsosurface", Sdf.ValueTypeNames.Bool).Set(True)
            raymarch_prim.CreateAttribute("rawModeNormalize", Sdf.ValueTypeNames.Bool).Set(True)
            raymarch_prim.CreateAttribute("shadowFactor", Sdf.ValueTypeNames.Float).Set(1)
            raymarch_prim.CreateAttribute("stepSizeScale", Sdf.ValueTypeNames.Float).Set(0.75)

            # Setup cloud parameters
            cloud_prim = stage.GetPrimAtPath("/World/flowRender/rayMarch/cloud")
            if cloud_prim:
                cloud_prim.CreateAttribute("ambientColor", Sdf.ValueTypeNames.Float3).Set((0.4, 0.55, 0.9))
                cloud_prim.CreateAttribute("ambientMultiplier", Sdf.ValueTypeNames.Float).Set(1)
                cloud_prim.CreateAttribute("attenuationMultiplier", Sdf.ValueTypeNames.Float3).Set((1, 1, 1))
                cloud_prim.CreateAttribute("densityMultiplier", Sdf.ValueTypeNames.Float).Set(0.5)
                cloud_prim.CreateAttribute("enableCloudMode", Sdf.ValueTypeNames.Bool).Set(False)
                cloud_prim.CreateAttribute("numShadowSteps", Sdf.ValueTypeNames.Int).Set(10)
                cloud_prim.CreateAttribute("shadowStepMultiplier", Sdf.ValueTypeNames.Float).Set(1)
                cloud_prim.CreateAttribute("sunDirection", Sdf.ValueTypeNames.Float3).Set((1, 1, 1))
                cloud_prim.CreateAttribute("volumeBaseColor", Sdf.ValueTypeNames.Float3).Set((1.1, 1, 0.95))
                cloud_prim.CreateAttribute("volumeColorMultiplier", Sdf.ValueTypeNames.Float).Set(1)

        # Setup render settings parameters
        settings_prim = stage.GetPrimAtPath("/World/flowRender/renderSettings")
        if settings_prim:
            settings_prim.CreateAttribute("compositeEnabled", Sdf.ValueTypeNames.Bool).Set(True)
            settings_prim.CreateAttribute("enableAutoApply", Sdf.ValueTypeNames.Bool).Set(True)
            settings_prim.CreateAttribute("flowEnabled", Sdf.ValueTypeNames.Bool).Set(True)
            settings_prim.CreateAttribute("maxBlocks", Sdf.ValueTypeNames.Int).Set(0)
            settings_prim.CreateAttribute("pathTracingEnabled", Sdf.ValueTypeNames.Bool).Set(True)
            settings_prim.CreateAttribute("pathTracingShadowsEnabled", Sdf.ValueTypeNames.Bool).Set(False)
            settings_prim.CreateAttribute("rayTracedReflectionsEnabled", Sdf.ValueTypeNames.Bool).Set(True)
            settings_prim.CreateAttribute("rayTracedShadowsEnabled", Sdf.ValueTypeNames.Bool).Set(False)
            settings_prim.CreateAttribute("rayTracedTranslucencyEnabled", Sdf.ValueTypeNames.Bool).Set(True)
