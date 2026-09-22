// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

// A few predefined names for XRSystems to use if wanted

#include <omni/kit/xr/IXRTokens.h>

namespace omni
{
namespace kit
{
namespace xr
{

///////////////////////////////////////////////////////////////////////
// Manifest Tokens:
///////////////////////////////////////////////////////////////////////

struct XRManifestTokens
{
    // Manifests for controller openxr bindings
    static inline XRTokenDefinition openxrControllerBindings = XRTokenDefinition("openxr_controller_bindings");

    // Manifests for controller openvr bindings
    static inline XRTokenDefinition openvrControllerBindings = XRTokenDefinition("openvr_controller_bindings");

    // Manifests for controller model resolving
    static inline XRTokenDefinition controllerModelResolvers = XRTokenDefinition("controller_model_resolvers");

    // Types of input devices defined by their properties
    static inline XRTokenDefinition inputDeviceTags = XRTokenDefinition("input_device_tags");

    // Usd Assets for input devices
    static inline XRTokenDefinition inputDeviceModels = XRTokenDefinition("input_device_models");

    // Controller action maps (describe how actions are mapped to components)
    static inline XRTokenDefinition actionMaps = XRTokenDefinition("action_maps");
};

///////////////////////////////////////////////////////////////////////
// SystemMetaData:
///////////////////////////////////////////////////////////////////////

struct XRSystemMetaDataTokens
{
    // Name to display in the menu
    static inline XRTokenDefinition displayName = XRTokenDefinition("displayName");

    // Whether system is simulated
    static inline XRTokenDefinition simulated = XRTokenDefinition("simulated");
};

///////////////////////////////////////////////////////////////////////
// Mode: specifies the modes in which a system can run
// a system session can have only a single mode and it determines
///////////////////////////////////////////////////////////////////////

struct XRModeTokens
{
    static inline XRTokenDefinition hmdVR = XRTokenDefinition("HmdVR");
    static inline XRTokenDefinition hmdAR = XRTokenDefinition("HmdAR");
    static inline XRTokenDefinition tabletVR = XRTokenDefinition("TabletVR");
    static inline XRTokenDefinition tabletAR = XRTokenDefinition("TabletAR");
};

///////////////////////////////////////////////////////////////////////
// Name tokens: describes a component's name
///////////////////////////////////////////////////////////////////////

struct XRAnchorSpaceNameTokens
{
    static inline XRTokenDefinition stageAnchor = XRTokenDefinition("stageAnchor");
};

struct XRInputDeviceNameTokens
{
    static inline XRTokenDefinition leftController = XRTokenDefinition("/user/hand/left");
    static inline XRTokenDefinition rightController = XRTokenDefinition("/user/hand/right");

    static inline XRTokenDefinition leftEye = XRTokenDefinition("/user/eye/left");
    static inline XRTokenDefinition rightEye = XRTokenDefinition("/user/eye/right");
    static inline XRTokenDefinition unifiedEye = XRTokenDefinition("/user/eye/unified");

    static inline XRTokenDefinition tablet = XRTokenDefinition("/user/hand/tablet");
    static inline XRTokenDefinition hmd = XRTokenDefinition("/user/head");

    static inline XRToken getEyeName(size_t idx)
    {
        if (idx == 0)
        {
            return leftEye;
        }
        else if (idx == 1)
        {
            return rightEye;
        }

        std::string token = std::string(getStringFromXRToken(XRInputDeviceNameTokens::eye)) + std::to_string(idx + 3);
        return getXRTokenFromString(token);
    }

    static inline XRToken getControllerName(size_t idx)
    {
        if (idx == 0)
        {
            return leftController;
        }
        else if (idx == 1)
        {
            return rightController;
        }

        std::string token =
            std::string(getStringFromXRToken(XRInputDeviceNameTokens::controller)) + std::to_string(idx + 3);
        return getXRTokenFromString(token);
    }

    static inline XRToken getTrackerName(size_t idx)
    {
        std::string token = std::string(getStringFromXRToken(XRInputDeviceNameTokens::tracker)) + std::to_string(idx + 1);
        return getXRTokenFromString(token);
    }

    static inline XRToken getReferenceName(size_t idx)
    {
        std::string token =
            std::string(getStringFromXRToken(XRInputDeviceNameTokens::reference)) + std::to_string(idx + 1);
        return getXRTokenFromString(token);
    }

    static inline XRToken getOtherName(size_t idx)
    {
        std::string token = std::string(getStringFromXRToken(XRInputDeviceNameTokens::other)) + std::to_string(idx + 1);
        return getXRTokenFromString(token);
    }

private:
    static inline XRTokenDefinition tracker = XRTokenDefinition("tracker");
    static inline XRTokenDefinition controller = XRTokenDefinition("controller");
    static inline XRTokenDefinition reference = XRTokenDefinition("reference");
    static inline XRTokenDefinition other = XRTokenDefinition("other");
    static inline XRTokenDefinition eye = XRTokenDefinition("eye");
};

struct XRDisplayNameTokens
{
    static inline XRTokenDefinition hmdLeft = XRTokenDefinition("hmdLeft");
    static inline XRTokenDefinition hmdRight = XRTokenDefinition("hmdRight");
    static inline XRTokenDefinition hmdLeftInset = XRTokenDefinition("hmdLeftInset");
    static inline XRTokenDefinition hmdRightInset = XRTokenDefinition("hmdRightInset");
    static inline XRTokenDefinition hmdLeftBackground = XRTokenDefinition("hmdLeftBackground");
    static inline XRTokenDefinition hmdRightBackground = XRTokenDefinition("hmdRightBackground");
    static inline XRTokenDefinition tablet = XRTokenDefinition("tablet");
    static inline XRTokenDefinition screen = XRTokenDefinition("screen");

    static inline XRToken getScreenName(size_t idx)
    {
        std::string token = std::string(getStringFromXRToken(XRDisplayNameTokens::screen)) + std::to_string(idx + 1);
        return getXRTokenFromString(token);
    }

    static inline XRToken getTabletName(size_t idx)
    {
        std::string token = std::string(getStringFromXRToken(XRDisplayNameTokens::tablet)) + std::to_string(idx + 1);
        return getXRTokenFromString(token);
    }
};

struct XRViewportMirrorNameTokens
{
    static inline XRTokenDefinition defaultViewport = XRTokenDefinition("defaultViewport");
};

///////////////////////////////////////////////////////////////////////
// Type tokens
///////////////////////////////////////////////////////////////////////

struct XRInputDeviceTypeTokens
{
    static inline XRTokenDefinition displayDevice = XRTokenDefinition("displayDevice");
    static inline XRTokenDefinition controller = XRTokenDefinition("controller");
    static inline XRTokenDefinition tracker = XRTokenDefinition("tracker");
    static inline XRTokenDefinition eye = XRTokenDefinition("eye");
    static inline XRTokenDefinition camera = XRTokenDefinition("camera");
    static inline XRTokenDefinition reference = XRTokenDefinition("reference");
    static inline XRTokenDefinition other = XRTokenDefinition("other");
};

struct XRDisplayTypeTokens
{
    static inline XRTokenDefinition hmd = XRTokenDefinition("hmd");
    static inline XRTokenDefinition tablet = XRTokenDefinition("tablet");
    static inline XRTokenDefinition screen = XRTokenDefinition("screen");
};

struct XRSystemNameTokens
{
    static inline XRTokenDefinition openxr = XRTokenDefinition("openxr");
    static inline XRTokenDefinition simulatedxr = XRTokenDefinition("simulatedxr");
};

///////////////////////////////////////////////////////////////////////
// Event key tokens
///////////////////////////////////////////////////////////////////////

struct XREventKeyTokens
{
    static inline XRTokenDefinition inputDevice = XRTokenDefinition("input_device");
    static inline XRTokenDefinition deviceType = XRTokenDefinition("input_device_type");
    static inline XRTokenDefinition profile = XRTokenDefinition("profile");
    static inline XRTokenDefinition system = XRTokenDefinition("system");
    static inline XRTokenDefinition actionMap = XRTokenDefinition("action_map");
    static inline XRTokenDefinition guiLayer = XRTokenDefinition("gui_layer");
    static inline XRTokenDefinition tool = XRTokenDefinition("tool");
    static inline XRTokenDefinition dt = XRTokenDefinition("dt");
    static inline XRTokenDefinition input = XRTokenDefinition("input");
    static inline XRTokenDefinition profiles = XRTokenDefinition("profiles");
    static inline XRTokenDefinition systems = XRTokenDefinition("systems");
    static inline XRTokenDefinition eventName = XRTokenDefinition("event_name");
    static inline XRTokenDefinition eventType = XRTokenDefinition("event_type");
};

///////////////////////////////////////////////////////////////////////
struct XROrientationTokens
{
    static inline XRTokenDefinition left = XRTokenDefinition("orientation/left");
    static inline XRTokenDefinition right = XRTokenDefinition("orientation/right");
};

struct XRDominantHandTokens
{
    static inline XRTokenDefinition left = XRTokenDefinition("left");
    static inline XRTokenDefinition right = XRTokenDefinition("right");
};

///////////////////////////////////////////////////////////////////////
// Pose Tokens
///////////////////////////////////////////////////////////////////////

struct XRPoseTokens
{
    static inline XRTokenDefinition grip = XRTokenDefinition("grip");
    static inline XRTokenDefinition aim = XRTokenDefinition("aim");
};

///////////////////////////////////////////////////////////////////////
// Gesture and Component Tokens
///////////////////////////////////////////////////////////////////////

struct XRGestureTokens
{
    static inline XRTokenDefinition click = XRTokenDefinition("click"); // boolean
    static inline XRTokenDefinition touch = XRTokenDefinition("touch"); // boolean
    static inline XRTokenDefinition proximity = XRTokenDefinition("proximity"); // boolean

    static inline XRTokenDefinition value = XRTokenDefinition("value"); // float
    static inline XRTokenDefinition force = XRTokenDefinition("force"); // float
    static inline XRTokenDefinition x = XRTokenDefinition("x"); // float
    static inline XRTokenDefinition y = XRTokenDefinition("y"); // float
    static inline XRTokenDefinition curl = XRTokenDefinition("curl"); // float
    static inline XRTokenDefinition slide = XRTokenDefinition("slide"); // float
};

struct XREventTypeTokens
{
    static inline XRTokenDefinition state = XRTokenDefinition("state");
    static inline XRTokenDefinition update = XRTokenDefinition("update");
    static inline XRTokenDefinition press = XRTokenDefinition("press");
    static inline XRTokenDefinition cancel = XRTokenDefinition("cancel");
    static inline XRTokenDefinition release = XRTokenDefinition("release");
    static inline XRTokenDefinition touch = XRTokenDefinition("touch");
    static inline XRTokenDefinition lift = XRTokenDefinition("lift");
    static inline XRTokenDefinition suspend = XRTokenDefinition("suspend");
    static inline XRTokenDefinition resume = XRTokenDefinition("resume");
    static inline XRTokenDefinition syncState = XRTokenDefinition("sync_state");
    static inline XRTokenDefinition syncUpdate = XRTokenDefinition("sync_update");
    static inline XRTokenDefinition syncPress = XRTokenDefinition("sync_press");
    static inline XRTokenDefinition syncRelease = XRTokenDefinition("sync_release");
    static inline XRTokenDefinition syncCancel = XRTokenDefinition("sync_cancel");
    static inline XRTokenDefinition syncTouch = XRTokenDefinition("sync_touch");
    static inline XRTokenDefinition syncLift = XRTokenDefinition("sync_lift");
};

struct XRInputSourceTokens
{
    static inline XRTokenDefinition inputDevice = XRTokenDefinition("input_device");
};

struct XRInputTokens
{
    static inline XRTokenDefinition select = XRTokenDefinition("select");
    static inline XRTokenDefinition back = XRTokenDefinition("back");
    static inline XRTokenDefinition menu = XRTokenDefinition("menu");
    static inline XRTokenDefinition squeeze = XRTokenDefinition("squeeze");
    static inline XRTokenDefinition trackpad = XRTokenDefinition("trackpad");
    static inline XRTokenDefinition thumbstick = XRTokenDefinition("thumbstick");
    static inline XRTokenDefinition thumbstickLeft = XRTokenDefinition("thumbstick_left");
    static inline XRTokenDefinition thumbstickRight = XRTokenDefinition("thumbstick_right");
    static inline XRTokenDefinition trigger = XRTokenDefinition("trigger");
    static inline XRTokenDefinition triggerLeft = XRTokenDefinition("trigger_left");
    static inline XRTokenDefinition triggerRight = XRTokenDefinition("trigger_right");
    static inline XRTokenDefinition system = XRTokenDefinition("system");
    static inline XRTokenDefinition a = XRTokenDefinition("a");
    static inline XRTokenDefinition b = XRTokenDefinition("b");
    static inline XRTokenDefinition x = XRTokenDefinition("x");
    static inline XRTokenDefinition y = XRTokenDefinition("y");
    static inline XRTokenDefinition dPadLeft = XRTokenDefinition("dpad_left");
    static inline XRTokenDefinition dPadRight = XRTokenDefinition("dpad_right");
    static inline XRTokenDefinition dPadUp = XRTokenDefinition("dpad_up");
    static inline XRTokenDefinition dPadDown = XRTokenDefinition("dpad_down");
    static inline XRTokenDefinition shoulderLeft = XRTokenDefinition("shoulder_left");
    static inline XRTokenDefinition shoulderRight = XRTokenDefinition("shoulder_right");
    static inline XRTokenDefinition trackpadUp = XRTokenDefinition("trackpad_up");
    static inline XRTokenDefinition trackpadDown = XRTokenDefinition("trackpad_down");
};

struct XRSubInputTokens
{
    static inline XRTokenDefinition tooltipLeft = XRTokenDefinition("tooltip_left");
    static inline XRTokenDefinition tooltipRight = XRTokenDefinition("tooltip_right");
    static inline XRTokenDefinition tooltipLeftRight = XRTokenDefinition("tooltip_left_right");

    static inline XRTokenDefinition tooltipUp = XRTokenDefinition("tooltip_up");
    static inline XRTokenDefinition tooltipDown = XRTokenDefinition("tooltip_down");
    static inline XRTokenDefinition tooltipUpDown = XRTokenDefinition("tooltip_up_down");

    static inline XRTokenDefinition tooltipButton = XRTokenDefinition("tooltip_button");
};

struct XRHandTrackingDataSourceTokens
{
    static inline XRTokenDefinition hand = XRTokenDefinition("hand");
    static inline XRTokenDefinition controller = XRTokenDefinition("controller");
};

struct XRDisplaySource
{
    static inline XRTokenDefinition full = XRTokenDefinition("full");
    static inline XRTokenDefinition background = XRTokenDefinition("background");
    static inline XRTokenDefinition inset = XRTokenDefinition("inset");
    static inline XRTokenDefinition warped = XRTokenDefinition("warped");
};

struct XRDisplayParamTokens
{
    static inline XRTokenDefinition linearizeDepth = XRTokenDefinition("linearizeDepth");
    static inline XRTokenDefinition displayAlpha = XRTokenDefinition("displayAlpha");
    static inline XRTokenDefinition submitFoveated = XRTokenDefinition("submitFoveated");
};

struct XRDisplayOutputTokens
{
    static inline XRTokenDefinition color = XRTokenDefinition("color");
    static inline XRTokenDefinition alpha = XRTokenDefinition("alpha");
    static inline XRTokenDefinition depth = XRTokenDefinition("depth");
};

struct XRCoreSettingsTokens
{
    static inline XRTokenDefinition debug = XRTokenDefinition("debug");

    static inline XRTokenDefinition logFrameLevel = XRTokenDefinition("log/frame/level");
    static inline XRTokenDefinition logFrameAll = XRTokenDefinition("log/frame/all");
    static inline XRTokenDefinition logFrameDirtyOnly = XRTokenDefinition("log/frame/dirtyOnly");

    static inline XRTokenDefinition logFrameAnchorSpaces = XRTokenDefinition("log/frame/anchorSpaces");
    static inline XRTokenDefinition logFrameInputDevices = XRTokenDefinition("log/frame/inputDevices");
    static inline XRTokenDefinition logFrameInputDevicesGestures = XRTokenDefinition("log/frame/inputDevicesGestures");
    static inline XRTokenDefinition logFrameInputDevicesOutputs = XRTokenDefinition("log/frame/inputDevicesOutputs");

    static inline XRTokenDefinition logFrameInputDevicesOverlaps = XRTokenDefinition("log/frame/inputDevicesOverlaps");

    static inline XRTokenDefinition logFrameInputDevicesPoses = XRTokenDefinition("log/frame/inputDevicesPoses");
    static inline XRTokenDefinition logFrameInputDevicesModels = XRTokenDefinition("log/frame/inputDevicesModels");

    static inline XRTokenDefinition logFrameEyes = XRTokenDefinition("log/frame/eyes");
    static inline XRTokenDefinition logFrameDisplays = XRTokenDefinition("log/frame/displays");
    static inline XRTokenDefinition logFrameViewportMirrors = XRTokenDefinition("log/frame/viewportMirrors");

    static inline XRTokenDefinition logManifestLevel = XRTokenDefinition("log/manifest/level");
    static inline XRTokenDefinition logManifestAll = XRTokenDefinition("log/manifest/all");

    static inline XRTokenDefinition dominantHand = XRTokenDefinition("tools/dominantHand");

    static inline XRTokenDefinition statusError = XRTokenDefinition("status/error");
    static inline XRTokenDefinition statusMessage = XRTokenDefinition("status/message");
};

struct XRProfileSettingsTokens
{
    static inline XRTokenDefinition enabled = XRTokenDefinition("enabled");
    static inline XRTokenDefinition displayName = XRTokenDefinition("displayName");

    static inline XRTokenDefinition systemDisplay = XRTokenDefinition("system/display");
    static inline XRTokenDefinition systemDisplayMode = XRTokenDefinition("system/displayMode");

    static inline XRTokenDefinition appGuiMode = XRTokenDefinition("app/guiMode");

    static inline XRTokenDefinition renderResolutionMultiplier = XRTokenDefinition("render/resolutionMultiplier");
    static inline XRTokenDefinition renderQuality = XRTokenDefinition("renderQuality");
    static inline XRTokenDefinition renderNearPlane = XRTokenDefinition("render/nearPlane");
    static inline XRTokenDefinition renderFarPlane = XRTokenDefinition("render/farPlane");

    static inline XRTokenDefinition disableDisplayOutput = XRTokenDefinition("disableDisplayOutput");
    static inline XRTokenDefinition enableEyeTracking = XRTokenDefinition("enableEyeTracking");

    static inline XRTokenDefinition foveationMode = XRTokenDefinition("foveation/mode");

    /////////////////////////////////////////
    // Stereo rendering 2 x warped

    static inline XRTokenDefinition foveationWarpedResolutionMultiplier =
        XRTokenDefinition("foveation/warped/resolutionMultiplier");
    static inline XRTokenDefinition foveationWarpedInsetSize = XRTokenDefinition("foveation/warped/insetSize");

    /////////////////////////////////////////
    // Quadview foveation mode

    static inline XRTokenDefinition quadviewMode = XRTokenDefinition("quadview/foveation/mode");

    /////////////////////////////////////////
    // Quadview rendering 4 x warped

    static inline XRTokenDefinition quadviewBackgroundFoveationWarpedResolutionMultiplier =
        XRTokenDefinition("quadview/background/foveation/warped/resolutionMultiplier");
    static inline XRTokenDefinition quadviewBackgroundFoveationWarpedInsetSize =
        XRTokenDefinition("quadview/background/foveation/warped/insetSize");

    static inline XRTokenDefinition quadviewInsetFoveationWarpedResolutionMultiplier =
        XRTokenDefinition("quadview/inset/foveation/warped/resolutionMultiplier");
    static inline XRTokenDefinition quadviewInsetFoveationWarpedInsetSize =
        XRTokenDefinition("quadview/inset/foveation/warped/insetSize");

    /////////////////////////////////////////
    // Quadview rendering  2 x warped to 4 views

    static inline XRTokenDefinition quadviewStereoFoveationWarpedResolutionMultiplier =
        XRTokenDefinition("quadview/stereo/foveation/warped/resolutionMultiplier");
    static inline XRTokenDefinition quadviewStereoFoveationWarpedInsetSize =
        XRTokenDefinition("quadview/stereo/foveation/warped/insetSize");

    /////////////////////////////////////////
    // Size of the quadview buffers

    static inline XRTokenDefinition quadviewRenderInsetResolutionMultiplier =
        XRTokenDefinition("quadview/render/inset/resolutionMultiplier");
    static inline XRTokenDefinition quadviewRenderBackgroundResolutionMultiplier =
        XRTokenDefinition("quadview/render/background/resolutionMultiplier");

    /////////////////////////////////////////

    /////////////////////////////////////////
    // Input smoothing

    static inline XRTokenDefinition inputSmoothingEnabled = XRTokenDefinition("inputSmoothing/enabled");
    static inline XRTokenDefinition inputSmoothingFactor = XRTokenDefinition("inputSmoothing/factor");

    static inline XRTokenDefinition sendComponentEvents = XRTokenDefinition("sendComponentEvents");

    /////////////////////////////////////////

    static inline XRTokenDefinition foveationInsetFullResSize = XRTokenDefinition("foveation/inset/fullResSize");
    static inline XRTokenDefinition foveationInsetBackgroundFactor =
        XRTokenDefinition("foveation/inset/backgroundFactor");

    static inline XRTokenDefinition foveationInsetHorizontalOffset =
        XRTokenDefinition("foveation/inset/horizontalOffset");
    static inline XRTokenDefinition foveationInsetVerticalOffset = XRTokenDefinition("foveation/inset/verticalOffset");

    static inline XRTokenDefinition foveationShowArea = XRTokenDefinition("foveation/showArea");
    static inline XRTokenDefinition foveationShowWarp = XRTokenDefinition("foveation/showWarp");
    static inline XRTokenDefinition foveationDimFactor = XRTokenDefinition("foveation/dimFactor");

    static inline XRTokenDefinition foveationInsetAspectRatio = XRTokenDefinition("foveation/inset/aspectRatio");

    static inline XRTokenDefinition viewportStatusEnabled = XRTokenDefinition("viewport/status/enabled");

    static inline XRTokenDefinition mirrorAspectRatio = XRTokenDefinition("mirror/aspectRatio");
    static inline XRTokenDefinition mirrorDisplayMode = XRTokenDefinition("mirror/displayMode");

    static inline XRTokenDefinition mirrorDisplayOutput = XRTokenDefinition("mirror/displayOutput");
    static inline XRTokenDefinition mirrorDepthNearPlane = XRTokenDefinition("mirror/depthNearPlane");
    static inline XRTokenDefinition mirrorDepthFarPlane = XRTokenDefinition("mirror/depthFarPlane");

    static inline XRTokenDefinition floorAlignedNavigation = XRTokenDefinition("floorAlignedNavigation");

    static inline XRTokenDefinition overrideFloorAlignedAnchor = XRTokenDefinition("overrideFloorAlignedAnchor");

    static inline XRTokenDefinition scaleFactor = XRTokenDefinition("scale/factor");
    static inline XRTokenDefinition scaleRelative = XRTokenDefinition("scale/relative");

    static inline XRTokenDefinition tooltipsVisible = XRTokenDefinition("tooltips/visible");
    static inline XRTokenDefinition controllersVisible = XRTokenDefinition("controllers/visible");

    static inline XRTokenDefinition navigationMode = XRTokenDefinition("navigationMode");

    static inline XRTokenDefinition anchorMode = XRTokenDefinition("anchorMode");
    static inline XRTokenDefinition customAnchor = XRTokenDefinition("customAnchor");
    static inline XRTokenDefinition adjustForUserHeight = XRTokenDefinition("adjustForUserHeight");

    static inline XRTokenDefinition enableNavigationControls = XRTokenDefinition("enableNavigationControls");
    static inline XRTokenDefinition relativeToAnchor = XRTokenDefinition("navigationTool/relativeToAnchor");

    static inline XRTokenDefinition teleportArcMaxHeight = XRTokenDefinition("teleport/arc/maxHeight");
    static inline XRTokenDefinition navigationSpeed = XRTokenDefinition("navigation/speed");

    static inline XRTokenDefinition quadviewEnabled = XRTokenDefinition("quadview/enabled");
    static inline XRTokenDefinition quadviewAvailable = XRTokenDefinition("quadview/available");
    static inline XRTokenDefinition quadviewActive = XRTokenDefinition("quadview/active");

    static inline XRTokenDefinition eyetrackingEnabled = XRTokenDefinition("eyetracking/enabled");
    static inline XRTokenDefinition eyetrackingAvailable = XRTokenDefinition("eyetracking/available");
    static inline XRTokenDefinition eyetrackingActive = XRTokenDefinition("eyetracking/active");

    static inline XRTokenDefinition viewportGuidesHidden = XRTokenDefinition("viewport/guides/hidden");
    static inline XRTokenDefinition viewportGridHidden = XRTokenDefinition("viewport/grid/hidden");
    static inline XRTokenDefinition viewportOutlineHidden = XRTokenDefinition("viewport/outline/hidden");

    static inline XRTokenDefinition toolsLayout = XRTokenDefinition("tools/layout");
    static inline XRTokenDefinition toolsDisable = XRTokenDefinition("tools/disable");
    static inline XRTokenDefinition toolsEnable = XRTokenDefinition("tools/enable");
    static inline XRTokenDefinition guiLayers = XRTokenDefinition("gui/layers");

    static inline XRTokenDefinition matteObjectOverrideStage = XRTokenDefinition("matteObject/overrideStage");
    static inline XRTokenDefinition matteObjectMode = XRTokenDefinition("matteObject/mode");
    static inline XRTokenDefinition matteObjectAoFactor = XRTokenDefinition("matteObject/ambientShadowCatcherFactor");
    static inline XRTokenDefinition matteObjectAoRayLength = XRTokenDefinition("matteObject/aoRayLength");
};

struct XRInputDeviceHandTrackingPoseTokens
{
    static inline XRTokenDefinition palm = XRTokenDefinition("palm");
    static inline XRTokenDefinition wrist = XRTokenDefinition("wrist");
    static inline XRTokenDefinition thumbMetacarpal = XRTokenDefinition("thumb_metacarpal");
    static inline XRTokenDefinition thumbProximal = XRTokenDefinition("thumb_proximal");
    static inline XRTokenDefinition thumbDistal = XRTokenDefinition("thumb_distal");
    static inline XRTokenDefinition thumbTip = XRTokenDefinition("thumb_tip");
    static inline XRTokenDefinition indexMetacarpal = XRTokenDefinition("index_metacarpal");
    static inline XRTokenDefinition indexProximal = XRTokenDefinition("index_proximal");
    static inline XRTokenDefinition indexIntermediate = XRTokenDefinition("index_intermediate");
    static inline XRTokenDefinition indexDistal = XRTokenDefinition("index_distal");
    static inline XRTokenDefinition indexTip = XRTokenDefinition("index_tip");
    static inline XRTokenDefinition middleMetacarpal = XRTokenDefinition("middle_metacarpal");
    static inline XRTokenDefinition middleProximal = XRTokenDefinition("middle_proximal");
    static inline XRTokenDefinition middleIntermediate = XRTokenDefinition("middle_intermediate");
    static inline XRTokenDefinition middleDistal = XRTokenDefinition("middle_distal");
    static inline XRTokenDefinition middleTip = XRTokenDefinition("middle_tip");
    static inline XRTokenDefinition ringMetacarpal = XRTokenDefinition("ring_metacarpal");
    static inline XRTokenDefinition ringProximal = XRTokenDefinition("ring_proximal");
    static inline XRTokenDefinition ringIntermediate = XRTokenDefinition("ring_intermediate");
    static inline XRTokenDefinition ringDistal = XRTokenDefinition("ring_distal");
    static inline XRTokenDefinition ringTip = XRTokenDefinition("ring_tip");
    static inline XRTokenDefinition littleMetacarpal = XRTokenDefinition("little_metacarpal");
    static inline XRTokenDefinition littleProximal = XRTokenDefinition("little_proximal");
    static inline XRTokenDefinition littleIntermediate = XRTokenDefinition("little_intermediate");
    static inline XRTokenDefinition littleDistal = XRTokenDefinition("little_distal");
    static inline XRTokenDefinition littleTip = XRTokenDefinition("little_tip");
};

inline constexpr const char* XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES[] = {
    "palm",
    "wrist",
    "thumb_metacarpal",
    "thumb_proximal",
    "thumb_distal",
    "thumb_tip",
    "index_metacarpal",
    "index_proximal",
    "index_intermediate",
    "index_distal",
    "index_tip",
    "middle_metacarpal",
    "middle_proximal",
    "middle_intermediate",
    "middle_distal",
    "middle_tip",
    "ring_metacarpal",
    "ring_proximal",
    "ring_intermediate",
    "ring_distal",
    "ring_tip",
    "little_metacarpal",
    "little_proximal",
    "little_intermediate",
    "little_distal",
    "little_tip",
};
inline constexpr size_t XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES_COUNT =
    sizeof(XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES) / sizeof(XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES[0]);

} // namespace xr
} // namespace kit
} // namespace omni
