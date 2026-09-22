// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

// Types and structs for XR development

#include <carb/events/IEvents.h>

#include <omni/kit/xr/IXRTokens.h>
#include <omni/kit/xr/XRError.h>
#include <omni/kit/xr/XRMath.h>

namespace carb
{
namespace dictionary
{
struct Item;
} // namespace dictionary
} // namespace carb

namespace omni
{
namespace kit
{
namespace xr
{

struct UsdStageState
{
    uint64_t usdStageId;
};

struct UsdStageLoadingStatus
{
    int32_t filesLoaded;
    int32_t totalFiles;
};

// Generation number for tracking changes
typedef uint64_t XRGenerationNumber;
typedef uint64_t XRUniqueId;

// Logging flags
typedef uint64_t XRFrameLogFlags;

constexpr XRFrameLogFlags kXRFrameLogFlags_DirtyOnly = 0x1000'0000ULL;

constexpr XRFrameLogFlags kXRFrameLogFlags_InputDevicesPoses = 0x01ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_InputDevicesModels = 0x02ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_InputDevicesGestures = 0x04ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_InputDevicesOverlaps = 0x08ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_InputDevicesOutputs = 0x20ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_InputDevicesAll = 0xFFULL;

constexpr XRFrameLogFlags kXRFrameLogFlags_EyesAll = 0xF00ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_DisplaysAll = 0xF000ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_ViewportMirrorsAll = 0xF'0000ULL;
constexpr XRFrameLogFlags kXRFrameLogFlags_AnchorSpacesAll = 0xF0'000ULL;

constexpr XRFrameLogFlags kXRFrameLogFlags_All = 0xFF'FFFULL;

// --- controllers and events ---

/**
 * A unique identifier for a system for calls that want to know what system something comes from.
 *
 * Can also be recognized/used as a regular XRSystem pointer.
 */
enum class XRSessionState : uint32_t
{
    eUnknown = 0,
    eIdle,
    ePreparing,
    eRunning,
    eStopping,
    eFailed,
    eNoXRSystem,
    eWaitingForConnection
};


struct XRComponentId
{
    XRToken name; // unique name
    XRToken type; // type of the component
};

inline bool operator==(const XRComponentId& a, const XRComponentId& b)
{
    return a.name == b.name && a.type == b.type;
}

inline bool operator!=(const XRComponentId& a, const XRComponentId& b)
{
    return !(a == b);
}

inline XRComponentId makeComponentId(XRToken name = 0, XRToken type = 0)
{
    XRComponentId result = { name, type };
    return result;
}

inline bool checkComponentId(XRComponentId id, XRToken handle)
{
    if (handle == 0)
    {
        return true;
    }
    return (handle == id.name || handle == id.type);
}


constexpr XRToken kXRInvalidId = 0;

enum class XRFoveationMode : uint32_t
{
    eNone = 0,
    eInset,
    eWarped,
};

enum class XRAppGuiMode : uint32_t
{
    eCurrent = 0,
    eMinimized,
    eFullscreen,
};

struct XRTimeStamp
{
    uint64_t frameNumber;
    double frameTime;
    double frameDuration;
    double frameCPUDuration;
    double frameGPUDuration;
};

// -- XR State management ---


enum class XRQuadViewMode
{
    eRenderQuadView,
    eRenderWarpedQuadView,
    eStereoWarpedToQuadView,
};

// --- XR Navigation options --

enum class XRAnchorMode
{
    eActiveCamera,
    eCustomAnchor,
    eSceneOrigin,
    eInvalid
};


enum class XROrientationAlignment
{
    eDeviceAligned = 0, // Coordinate system aligns with controller that has the beam
    eDeviceAlignedUpRight, // Coordinate system points up and faces controller
    eDeviceAlignedNoRoll, // Remove roll from coordinate system
    eAnchorAligned, // Coordinate system is aligned with anchor in world space
    eAnchorAlignedUpRight, // Coordinate system is aligned with anchor in world space but points up
    eAnchorAlignedNoRoll, // Coordinate system is aligned with anchor and removes roll from coordinate system
    eWorldAligned, // Coordinate system aligned with the world
    eCount
};

constexpr char const* kXROrientationAlignmentNames[static_cast<size_t>(XROrientationAlignment::eCount)] = {
    "deviceAligned", "deviceAlignedUpRight", "anchorAligned", "anchorAlignedUpRight", "worldAligned"
};

enum class XRUpAxis
{
    eYUp = 0,
    eZUp = 1
};

struct XRCoordinateSystem
{
    double metersPerUnit; // the amount of scene units for each meter
    XRUpAxis upAxis; // which axis points up
};

inline bool operator==(const XRCoordinateSystem& a, const XRCoordinateSystem& b)
{
    return a.metersPerUnit == b.metersPerUnit && a.upAxis == b.upAxis;
}

inline bool operator!=(const XRCoordinateSystem& a, const XRCoordinateSystem& b)
{
    return !(a == b);
}

constexpr XRCoordinateSystem kXRCoordinateSystemDefault = { 1.0f, XRUpAxis::eYUp };

enum class XRGraphicsSystem
{
    eDX12,
    eVulkan,
    eNone
};

enum class XRMirrorDisplayMode
{
    eBoth,
    eLeft,
    eRight,
    eViewport
};

enum class XRMirrorAspectRatio
{
    eStretch = 0,
    eLetterbox,
    eCrop,
};


// -- XR Matte Object State ---

enum class XRMatteObjectMode
{
    eDisabled = 0,
    eEnabled,
    eStdShadowCatcher,
    eAoShadowCatcher,
};


/**
 * @brief Pipeline goes through different stages
 */

enum class XRPipelineStage : uint32_t
{
    eUndefined, // Not yet defined

    /**
     * @brief ShutdownSession: This stage is executed when a session is being removed, this stage is run separately on
     * the frame and afterwards no more frame calls with this session are done.
     *
     * NOTE: This step guarantees that endFrame of previous frame has been called
     */
    eShutdownSession,

    /**
     * @brief SetupSession: This stage is executed when a new session is added, this stage is run for that session and
     * is the first stage to be run.
     */
    eSetupSession,

    /**
     * @brief SessionState: This stage is run each frame before BeginFrame. It allows updating the session state
     * If the session state is 'running' the next series from beginFrame to endFrame is run. If the state after this
     * call is not 'running' this session is excluded from the pipeline and beginFrame to endFrame are not run for this
     * session. The next call for this session in that case will be shutdownSession or another updateSessionState.
     *
     * NOTE: This call may be called before the previous frame calls endFrame.
     */
    eUpdateSessionState,

    /**
     * @brief SyncSystem: This stage is run without the lock in the main thread and waits and synchronizes the xr device
     * state. (waitPoses)
     */
    eSyncSystem,

    /**
     * @brief StartFrame: This stage is run for a frame when the session state is running. This is run before the main
     * synchronization of devices.
     */
    eBeginFrame,

    /**
     * @brief OverrideScaling: Allow scaling of the virtual -> physical world to be overwritten.
     */
    eOverrideScaling,

    /**
     * @brief VirtualWorldAlignment: This stage updates alignment of virtual world and physical world.
     */
    eVirtualWorldAlignment,

    /**
     * @brief DeviceTracking: This stage updates device poses in the frame.
     *
     */
    eUpdateTracking,

    /**
     * @brief UpdateDisplays: This stage updates which displays need to be calculated.
     */
    eUpdateDisplays,

    /**
     * @brief UpdateViewportMirrors: This stage updates how displays are mirrored in the viewport.
     */
    eUpdateViewportMirrors,

    // ==== Next stages are executed on render thread ====

    /**
     * @brief BeginRendering: this stage called when first on render thread.
     *
     * NOTE: This call may be skipped if render thread is stuck and simulation thread has prepared the next frame. This
     * is the case in some loading scenarios when the render thread blocks for more than a second. In that case new data
     * will be sync'd from devices.
     */
    eBeginRendering,

    /**
     * @brief PreComposition: This stage is called before any xr composition steps are executed.
     *
     * NOTE: This call may be skipped if render thread is stuck and simulation thread has prepared the next frame. This
     * is the case in some loading scenarios when the render thread blocks for more than a second. In that case new data
     * will be sync'd from devices.
     */
    ePreComposition,

    /**
     * @brief PostComposition: This stage is called after any composition steps are executed.
     *
     * NOTE: This call may be skipped if render thread is stuck and simulation thread has prepared the next frame. This
     * is the case in some loading scenarios when the render thread blocks for more than a second. In that case new data
     * will be sync'd from devices.
     */
    ePostComposition,

    /**
     * @brief PostQueueSubmit: Render Thread: After queue has been submitted but before the frame is finished.
     *
     * NOTE: This call may be skipped if render thread is stuck and simulation thread has prepared the next frame. This
     * is the case in some loading scenarios when the render thread blocks for more than a second. In that case new data
     * will be sync'd from devices.
     */
    ePostQueueSubmit,

    /**
     * @brief EndRendering: This stage is called at end of rendering.
     *
     * NOTE: This call may be skipped if render thread is stuck and simulation thread has prepared the next frame. This
     * is the case in some loading scenarios when the render thread blocks for more than a second. In that case new data
     * will be sync'd from devices.
     */
    eEndRendering,

    /**
     * @brief Called when frame will skip rendering and no beginRendering will be called
     *
     * NOTE: This one will be on the main/sim thread
     */
    eSkipRendering,

    eStageCount // Total number of stages
};

////////////////////////////////////////////////////
// Description of what type of session to create
////////////////////////////////////////////////////

struct XRSystemSessionDesc
{
    XRToken profileName; // Name of the profile on which the session is enabled
    XRToken mode; // The mode the system will be put in, e.g. VR, AR etc
};

struct XRSystemListDesc
{
    XRToken* modes; // Which modes are required
    size_t modesCount; // number of modes in the list
};

////////////////////////////////////////////////////
// Foveation parameters
////////////////////////////////////////////////////

struct XRWarpParams
{
    float resolutionMultiplier = 0.5f;
    float insetSize = 0.4f;
};

struct XRFoveationParams
{
    uint32_t unwarpedWidth = 0;
    uint32_t unwarpedHeight = 0;
    uint32_t warpedWidth = 0;
    uint32_t warpedHeight = 0;

    uint32_t fovCenterHorz = 0;
    uint32_t fovCenterVert = 0;
    uint32_t fovRadiusHorz = 0;
    uint32_t fovRadiusVert = 0;
};

inline bool operator==(const XRFoveationParams& a, const XRFoveationParams& b)
{
    return a.unwarpedWidth == b.unwarpedWidth && a.unwarpedHeight == b.unwarpedHeight &&
           a.fovCenterHorz == b.fovCenterHorz && a.fovCenterVert == b.fovCenterVert &&
           a.fovRadiusHorz == b.fovRadiusHorz && a.fovRadiusVert == b.fovRadiusVert && a.warpedWidth == b.warpedWidth &&
           a.warpedHeight == b.warpedHeight;
}

inline bool operator!=(const XRFoveationParams& a, const XRFoveationParams& b)
{
    return !(a == b);
}

struct XRClippingPlanes
{
    float nearPlane;
    float farPlane;
};

inline bool operator==(const XRClippingPlanes& a, const XRClippingPlanes& b)
{
    return a.nearPlane == b.nearPlane && a.farPlane == b.farPlane;
}

inline bool operator!=(const XRClippingPlanes& a, const XRClippingPlanes& b)
{
    return !(a == b);
}

// Utility function to prioritize getting a USDRT transform, but falls back to USD if Fabric doesn't have the prim
enum class XRPrimAccessMode : uint32_t
{
    USDRT = 0,
    USD,
};

typedef uint64_t XRPoseValidityFlags;
constexpr XRPoseValidityFlags kXRPoseValidityFlags_OrientationValid = 0x0000'0001ULL;
constexpr XRPoseValidityFlags kXRPoseValidityFlags_PositionValid = 0x0000'0002ULL;
constexpr XRPoseValidityFlags kXRPoseValidityFlags_OrientationTracked = 0x0000'0004ULL;
constexpr XRPoseValidityFlags kXRPoseValidityFlags_PositionTracked = 0x0000'0008ULL;

constexpr XRPoseValidityFlags kXRPoseValidityFlags_AllValidAndTracked =
    kXRPoseValidityFlags_OrientationValid | kXRPoseValidityFlags_PositionValid |
    kXRPoseValidityFlags_OrientationTracked | kXRPoseValidityFlags_PositionTracked;

constexpr XRPoseValidityFlags kXRPoseValidityFlags_LinearVelocityValid = 0x0001'0000ULL;
constexpr XRPoseValidityFlags kXRPoseValidityFlags_AngularVelocityValid = 0x0002'0000ULL;

} // namespace xr
} // namespace kit
} // namespace omni
