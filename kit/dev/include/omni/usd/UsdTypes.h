// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Types.h>
#include <carb/RString.h>

#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace omni
{
namespace usd
{

typedef uint64_t SubscriptionId;

/**
 * Defines the USD state types.
 */
enum class StageState
{
    /// USD is closed/unopened.
    eClosed,

    /// USD is opening.
    eOpening,

    /// USD is opened.
    eOpened,

    /// USD is closing.
    eClosing
};

/**
 * Defines the usd event types.
 */
enum class StageEventType
{
    /// USD file saved.
    eSaved,

    /// Failed to save USD.
    eSaveFailed,

    /// USD stage is opening.
    eOpening,

    /// USD stage is opened successfully.
    eOpened,

    /// USD stage failed to open.
    eOpenFailed,

    /// USD stage is about to close. This is a good opportunity to shutdown anything depends on USD stage.
    eClosing,

    /// USD stage is fully closed.
    eClosed,

    /// USD Prim selection has changed.
    eSelectionChanged,

    /// Current batch of async asset loading has been completed.
    eAssetsLoaded,

    /// Current batch of async asset loading has been aborted.
    eAssetsLoadAborted,

    /// Started or stopped tracking (hovering) on a gizmo
    eGizmoTrackingChanged,

    /// MDL parameter is loaded for a MDL UsdShadeShader.
    eMdlParamLoaded,

    /// Stage settings have loaded
    eSettingsLoaded,

    /// Stage settings are being saved
    eSettingsSaving,

    /// OmniGraph play has started
    eOmniGraphStartPlay,

    /// OmniGraph play has stopped
    eOmniGraphStopPlay,

    /// Simulation play has started
    eSimulationStartPlay,

    /// Simulation play has stopped
    eSimulationStopPlay,

    /// Animation playback has started
    eAnimationStartPlay,

    /// Animation playback has stopped
    eAnimationStopPlay,

    /// Dirty state of USD stage has changed. Dirty state means if it has unsaved changes or not.
    eDirtyStateChanged,

    /// A new batch of async asset loading has started.
    eAssetsLoading,

    /// Number of active lights in the scene has changed. This signal should be triggered
    /// every time a scene has been loaded or number of lights has been changed. A few
    /// features, for instance view lighting mode, need to detect when a number of active
    /// lights becomes zero / become non-zero.
    eActiveLightsCountChanged,

    /// USD stage hierarchy has changed.
    eHierarchyChanged,

    /// Fabric Scene Delegate sends this when starting to stream rprims.
    eHydraGeoStreamingStarted,

    /// Fabric Scene Delegate sends this when stopping to stream rprims.
    eHydraGeoStreamingStopped,

    /// Fabric Scene Delegate sends this when geometry streaming stops loading more geometry because of insufficient device memory
    eHydraGeoStreamingStoppedNotEnoughMem,

    /// Fabric Scene Delegate sends this when stopping to stream rprims because of the limit set by the user.
    eHydraGeoStreamingStoppedAtLimit,

    /// Starting to save stage.
    eSaving,

    /// Count only
    eCount // MUST BE LAST
};

//! \cond DEV
namespace detail
{
/**
 * Generates an event name based on the StageEventType and the optional context.
 * @param event The StageEventType for the event.
 * @param context An optional context name. If not specified, the default (empty) context is used.
 * @returns a `carb::RString` event name for the given event and context in the format
 *   `omni.usd:<context>:stage:<event>`.
 */
inline carb::RString stageEventName(StageEventType event, carb::cpp::string_view context = {}) noexcept
{
    // clang-format off
    static carb::RString mapping[] = {
        carb::RString("omni.usd::stage:saved"),                     carb::RString("omni.usd::stage:save_failed"),
        carb::RString("omni.usd::stage:opening"),                   carb::RString("omni.usd::stage:opened"),
        carb::RString("omni.usd::stage:open_failed"),               carb::RString("omni.usd::stage:closing"),
        carb::RString("omni.usd::stage:closed"),                    carb::RString("omni.usd::stage:selection_changed"),
        carb::RString("omni.usd::stage:assets_loaded"),             carb::RString("omni.usd::stage:assets_load_aborted"),
        carb::RString("omni.usd::stage:gizmo_tracking_changed"),    carb::RString("omni.usd::stage:mdl_param_loaded"),
        carb::RString("omni.usd::stage:settings_loaded"),           carb::RString("omni.usd::stage:settings_saving"),
        carb::RString("omni.usd::stage:og_start_play"),             carb::RString("omni.usd::stage:og_stop_play"),
        carb::RString("omni.usd::stage:sim_start_play"),            carb::RString("omni.usd::stage:sim_stop_play"),
        carb::RString("omni.usd::stage:anim_start_play"),           carb::RString("omni.usd::stage:anim_stop_play"),
        carb::RString("omni.usd::stage:dirty_state_changed"),       carb::RString("omni.usd::stage:assets_loading"),
        carb::RString("omni.usd::stage:active_lights_changed"),     carb::RString("omni.usd::stage:hierarchy_changed"),
        carb::RString("omni.usd::stage:geo_streaming_started"),     carb::RString("omni.usd::stage:geo_streaming_stopped"),
        carb::RString("omni.usd::stage:geo_stopped_mem"),           carb::RString("omni.usd::stage:geo_stopped_limit"),
        carb::RString("omni.usd::stage:saving"),
    };
    // clang-format on
    static_assert(CARB_COUNTOF(mapping) == size_t(StageEventType::eCount), "Add missing entry");
    CARB_ASSERT(size_t(event) < CARB_COUNTOF(mapping));

    auto name = mapping[size_t(event)];

    // Default/empty context: just return the base event
    if (context.empty())
        return name;

    CARB_ASSERT(carb::cpp::zstring_view(name.c_str(), name.length()).find("omni.usd::") == 0);

    // Other contexts: need to insert the context name so that our string is "omni.usd:<context>:stage:<event>"
    static constexpr char kPrefix[] = "omni.usd:";
    constexpr size_t kPrelen = carb::cpp::zstring_view(kPrefix).length();

    auto buf = CARB_STACK_ALLOC(char, name.length() + context.length() + 1);
    memcpy(buf, kPrefix, kPrelen);
    memcpy(buf + kPrelen, context.data(), context.length());
    memcpy(buf + kPrelen + context.length(), name.c_str() + kPrelen, name.length() - kPrelen);
    buf[name.length() + context.length()] = '\0';
    return carb::RString(buf, name.length() + context.length());
}
}
//! \endcond

/**
 * Parses the StageEventType from a stage event RString.
 * @param event The event name, typically generated from `stageEventName()`.
 * @param pContext May be `nullptr`. If not `nullptr` and a valid `optional` is returned, this will receive the USD
 *   context name parsed from the event name. If `carb::cpp::nullopt` is returned, the pointed at `string_view` is in an
 *   unspecified state.
 * @returns A valid `optional` containing the determined `StageEventType` if parsing is successful. Otherwise,
 *   `carb::cpp::nullopt` is returned to indicate that the given event name is not a valid stage event name.
 */
inline carb::cpp::optional<StageEventType> stageEventType(carb::RString event, carb::cpp::string_view* pContext = nullptr) noexcept
{
    constexpr static carb::cpp::string_view kPrefix("omni.usd:");
    constexpr static carb::cpp::string_view kStage(":stage:");
    auto sv = carb::cpp::string_view(event);
    if (!sv.starts_with(kPrefix))
        return carb::cpp::nullopt;
    
    auto pos = sv.rfind(kStage);
    if (pos == decltype(sv)::npos)
        return carb::cpp::nullopt;

    if (pContext)
        *pContext = sv.substr(kPrefix.length(), pos - kPrefix.length());

    auto name = sv.substr(pos + kStage.length());
    switch (carb::hashBuffer(name.data(), name.length()))
    {
    case CARB_HASH_STRING("saved"): return StageEventType::eSaved;
    case CARB_HASH_STRING("save_failed"): return StageEventType::eSaveFailed;
    case CARB_HASH_STRING("opening"): return StageEventType::eOpening;
    case CARB_HASH_STRING("opened"): return StageEventType::eOpened;
    case CARB_HASH_STRING("open_failed"): return StageEventType::eOpenFailed;
    case CARB_HASH_STRING("closing"): return StageEventType::eClosing;
    case CARB_HASH_STRING("closed"): return StageEventType::eClosed;
    case CARB_HASH_STRING("selection_changed"): return StageEventType::eSelectionChanged;
    case CARB_HASH_STRING("assets_loaded"): return StageEventType::eAssetsLoaded;
    case CARB_HASH_STRING("assets_load_aborted"): return StageEventType::eAssetsLoadAborted;
    case CARB_HASH_STRING("gizmo_tracking_changed"): return StageEventType::eGizmoTrackingChanged;
    case CARB_HASH_STRING("mdl_param_loaded"): return StageEventType::eMdlParamLoaded;
    case CARB_HASH_STRING("settings_loaded"): return StageEventType::eSettingsLoaded;
    case CARB_HASH_STRING("settings_saving"): return StageEventType::eSettingsSaving;
    case CARB_HASH_STRING("og_start_play"): return StageEventType::eOmniGraphStartPlay;
    case CARB_HASH_STRING("og_stop_play"): return StageEventType::eOmniGraphStopPlay;
    case CARB_HASH_STRING("sim_start_play"): return StageEventType::eSimulationStartPlay;
    case CARB_HASH_STRING("sim_stop_play"): return StageEventType::eSimulationStopPlay;
    case CARB_HASH_STRING("anim_start_play"): return StageEventType::eAnimationStartPlay;
    case CARB_HASH_STRING("anim_stop_play"): return StageEventType::eAnimationStopPlay;
    case CARB_HASH_STRING("dirty_state_changed"): return StageEventType::eDirtyStateChanged;
    case CARB_HASH_STRING("assets_loading"): return StageEventType::eAssetsLoading;
    case CARB_HASH_STRING("active_lights_changed"): return StageEventType::eActiveLightsCountChanged;
    case CARB_HASH_STRING("hierarchy_changed"): return StageEventType::eHierarchyChanged;
    case CARB_HASH_STRING("geo_streaming_started"): return StageEventType::eHydraGeoStreamingStarted;
    case CARB_HASH_STRING("geo_streaming_stopped"): return StageEventType::eHydraGeoStreamingStopped;
    case CARB_HASH_STRING("geo_stopped_mem"): return StageEventType::eHydraGeoStreamingStoppedNotEnoughMem;
    case CARB_HASH_STRING("geo_stopped_limit"): return StageEventType::eHydraGeoStreamingStoppedAtLimit;
    case CARB_HASH_STRING("saving"): return StageEventType::eSaving;
    }
    static_assert(size_t(StageEventType::eCount) == 29, "add missing entry");
    return carb::cpp::nullopt;
}

enum class StageRenderingEventType
{
    /// New frame available for Viewport, params are ViewportHandle, FrameNo, RenderResults
    eNewFrame,

    /// Frames complete for a single hydra engine render() invocation.
    /// Payload is {
    ///     render_results: [ { viewport_handle: ViewportHandle, product: HydraRenderProduct*, subframe_count: int32_t } ],
    ///     average_frame_time_ns: float,
    ///     swh_frame_number: uint64_t,
    /// }
    eHydraEngineFramesComplete,

    /// Frames added to the GPU queue for a single hydra engine.
    /// This event signifies that the frame is scheduled for GPU rendering and has not been rendered yet.
    /// The payload structure is the same as eHydraEngineFramesComplete.
    eHydraEngineFramesAdded,

    /// Recording of the frame is done, but has not been submitted for execution yet.
    /// Payload is {
    ///     results: HydraRenderResults*
    ///     product_path_handle: usd::PathH
    ///     rendergraph: gpu::RenderGraph::RenderGraph*
    /// }
    /// This event is never push()ed; it is only ever dispatch()ed. This means that push subscriptions will never be
    /// triggered. This also means that it can execute out of order with respect to other events in the same stream; A
    /// OnEventFunction for this function can not rely on the execution order of other events in the same stream.
    /// Execution of this event will block the rendering thread - it should be used only to add operations to the end of
    /// the RenderGraph, after rendering has added all operations, but before it is submitted.
    eRendererRecordingComplete,

    /// Count only
    eCount // MUST BE LAST
};

//! \cond DEV
namespace detail
{
/**
 * Generates an event name based on the StageRenderingEventType and the optional context.
 * @param event The StageRenderingEventType for the event.
 * @param context An optional context name. If not specified, the default (empty) context is used.
 * @param immediate If true, the event name will be the name of the event that is dispatched immediately when the
 *   situation occurs that produces the event. If false (default), the event is the name that is deferred and dispatched
 *   at a later, safer time during the frame.
 * @returns a `carb::RString` event name for the given event and context in the format
 *   `omni.usd:<context>:rendering:<event>[:immediate]`.
 */
inline carb::RString stageRenderingEventName(StageRenderingEventType event, carb::cpp::string_view context = {}, bool immediate = false) noexcept
{
    // clang-format off
    static carb::RString mapping[2][4] = { {
        carb::RString("omni.usd::rendering:new_frame"),
        carb::RString("omni.usd::rendering:frames_complete"),
        carb::RString("omni.usd::rendering:frames_added"),
        carb::RString("omni.usd::rendering:recording_complete"),
    }, {
        carb::RString("omni.usd::rendering:new_frame:immediate"),
        carb::RString("omni.usd::rendering:frames_complete:immediate"),
        carb::RString("omni.usd::rendering:frames_added:immediate"),
        carb::RString("omni.usd::rendering:recording_complete"), // doesn't have an immediate version
    } };
    // clang-format on
    static_assert(CARB_COUNTOF(mapping[0]) == size_t(StageRenderingEventType::eCount), "Add missing entry");
    CARB_ASSERT(size_t(event) < CARB_COUNTOF(mapping[0]));

    auto name = mapping[immediate][size_t(event)];

    // Default/empty context: just return the base event
    if (context.empty())
        return name;

    CARB_ASSERT(carb::cpp::zstring_view(name.c_str(), name.length()).find("omni.usd::") == 0);

    // Other contexts: need to insert the context name so that our string is "omni.usd:<context>:stage:<event>"
    static constexpr char kPrefix[] = "omni.usd:";
    constexpr size_t kPrelen = carb::cpp::zstring_view(kPrefix).length();

    auto buf = CARB_STACK_ALLOC(char, name.length() + context.length() + 1);
    memcpy(buf, kPrefix, kPrelen);
    memcpy(buf + kPrelen, context.data(), context.length());
    memcpy(buf + kPrelen + context.length(), name.c_str() + kPrelen, name.length() - kPrelen);
    buf[name.length() + context.length()] = '\0';
    return carb::RString(buf, name.length() + context.length());
}
}
//! \endcond

/**
 * Parses the StageRenderingEventType from a stage rendering event RString.
 * @param event The event name, typically generated from `stageRenderingEventName()`.
 * @param pContext May be `nullptr`. If not `nullptr` and a valid `optional` is returned, this will receive the USD
 *   context name parsed from the event name. If `carb::cpp::nullopt` is returned, the pointed at `string_view` is in an
 *   unspecified state.
 * @param pImmediate May be `nullptr`. If not `nullptr` and a valid `optional` is returned, this will receive whether
 *   the event name is an 'immediate' event that occurs at the point where the event situation occurs. If `false` is
 *   received, the event is a deferred even that happens at a safer point in the frame.
 * @returns A valid `optional` containing the determined `StageRenderingEventType` if parsing is successful. Otherwise,
 *   `carb::cpp::nullopt` is returned to indicate that the given event name is not a valid stage event name.
 */
inline carb::cpp::optional<StageRenderingEventType> stageRenderingEventType(carb::RString event, carb::cpp::string_view* pContext = nullptr, bool* pImmediate = nullptr) noexcept
{
    constexpr static carb::cpp::string_view kPrefix("omni.usd:");
    constexpr static carb::cpp::string_view kStage(":rendering:");
    auto sv = carb::cpp::string_view(event);
    if (!sv.starts_with(kPrefix))
        return carb::cpp::nullopt;
    
    auto pos = sv.rfind(kStage);
    if (pos == decltype(sv)::npos)
        return carb::cpp::nullopt;

    if (pContext)
        *pContext = sv.substr(kPrefix.length(), pos - kPrefix.length());
    
    if (pImmediate)
        *pImmediate = sv.ends_with(":immediate");

    auto name = sv.substr(pos + kStage.length());
    switch (carb::hashBuffer(name.data(), name.length()))
    {
    case CARB_HASH_STRING("new_frame"): return StageRenderingEventType::eNewFrame;
    case CARB_HASH_STRING("frames_complete"): return StageRenderingEventType::eHydraEngineFramesComplete;
    case CARB_HASH_STRING("frames_added"): return StageRenderingEventType::eHydraEngineFramesAdded;
    case CARB_HASH_STRING("recording_complete"): return StageRenderingEventType::eRendererRecordingComplete;
    }
    static_assert(size_t(StageRenderingEventType::eCount) == 4, "add missing entry");
    return carb::cpp::nullopt;
}

/**
* @brief Stage result callback.
*
* @see UsdContext::newStage, UsdContext::openStage, UsdContext::closeStage, UsdContext::attachStage
*/
using OnStageResultFn = std::function<void(bool result, const char* err)>;

/**
* @brief Stage save callback.
*
* @see UsdContext::saveStage, UsdContext::saveAsStage, UsdContext::saveLayers
*/
using OnLayersSavedResultFn =
    std::function<void(bool result, const char* err, const std::vector<std::string>& savedLayers)>;


/**
 * Internal.
 */
using stuff = carb::Double3;
using OnPickingCompleteFn = std::function<void(const char* path, const carb::Double3* worldPos)>;

}
}
