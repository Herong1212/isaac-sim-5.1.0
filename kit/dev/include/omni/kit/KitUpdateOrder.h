// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

/**
 * @file
 * @brief Helpers for kit update ordering
 *
 * Kit's event subscribers order numbers, which control the execution order flow of the application were previously
 * magic values scattered across dozens of extensions across multiple repositories. This centralizes it for now.
 *
 * This file defines a ordering that can be used to by extensions to have a deterministic execution flow.
 */
#pragma once

#include "../../carb/events/IEvents.h"


namespace omni
{
namespace kit
{

//! Namespace for kit update ordering values
namespace update
{

//! @defgroup updateorder Kit Update Ordering values
//! @todo Although it is good that these values are together, this is not the correct place for them. Many of the values
//!   are specific to Omniverse applications that consume Carbonite but are not based in Carbonite. They should likely
//!   be in a data-driven format such as a configuration file and instead referred to as names (i.e. using
//!   \ref carb::RString) that can be mapped to a value, and/or documented somewhere central.
//! @{

//! Ordering of events within a \ref omni::kit::RunLoop::preUpdate event loop.
//! \see updateorder
enum PreUpdateOrdering : int32_t
{
    eTelmetryInitialize = -50, //!< Initialize Telemetry profiling. Typically the first item in a frame.
    eFabricBeginFrame = -20, //!< Initiate a Fabric frame.
    eUnspecifiedPreUpdateOrder = carb::events::kDefaultOrder //!< Default pre-update order value
};

//! Ordering of events within a \ref omni::kit::RunLoop::update event loop.
//! \see updateorder
enum UpdateOrdering : int32_t
{
    //! Checks for HydraEngine::render completion on GPU.
    //!
    //! 1. Pushes StageRenderingEvent::NewFrame
    //! 2. Triggers renderingEventStream::pump
    eCheckForHydraRenderComplete = -100,

    //! Applies pending Timeline state changes
    eUsdTimelineStateRefresh = -90,

    //! asyncio.Future blocked awaiting (update loop begin)
    //!
    //! 1. IApp.next_pre_update_async
    //! 2. UsdContext.next_frame_async / next_usd_async
    ePythonAsyncFutureBeginUpdate = -50,

    //! Enables execution of all python blocked by \ref ePythonAsyncFutureBeginUpdate
    //!
    //! Enable python execution blocked awaiting UsdContext::RenderingEventStream::Pump()
    //! @see ePythonAsyncFutureBeginUpdate
    ePythonExecBeginUpdate = -45,

    //! Run OmniClient after python but before main simulation
    eOmniClientUpdate = -30,

    //! ITimeline wants to execute before \ref eUsdContextUpdate
    eUsdTimelineUpdate = -20,

    //! Core UsdUpdate execution
    //!
    //! 1. Update liveModeUpdate listeners
    //! 2. triggers stageEventStream::pump
    //! 3. MaterialWatcher::update
    //! 4. IHydraEngine::setTime
    //! 5. triggers IUsdStageUpdate::pump (see IUsdStageEventOrdering below)
    //! 6. AudioManager::update
    eUsdContextUpdate = -10,

    //! Default update order value
    //!
    //! @note extras::SettingWrapper is hardcoded to \ref carb::events::kDefaultOrder which means this is when during
    //! the main update cycle, event listeners for settings changes events will fire. There are a minimum of 60+ unique
    //! setting subscription listeners in a default kit session.
    eUnspecifiedUpdateOrder = carb::events::kDefaultOrder,

    //! Trigger UI/ImGui Drawing
    eUIRendering = 15,

    //! Fabric Flush after eUsdContextUpdate
    //! @see eUsdContextUpdate
    eFabricFlush = 20,

    //! Triggers HydraEngine::render
    eHydraRendering = 30,

    //! asyncio.Future blocked awaiting (update loop end)
    //!
    //! 1. IApp.next_update_async (legacy)
    ePythonAsyncFutureEndUpdate = 50,

    //! Enables execution of all python blocked by ePythonAsyncFutureEndUpdate and awaiting
    //! UsdContext::StageEventStream::Pump.
    ePythonExecEndUpdate = 100,
};

/*
 * IApp.next_update_async() is the original model of python scripting kit, a preferred
 * approach is either App.pre_update_async() and/or App.post_update_async(). Both can be used inside
 * a single app tick, pseudo python code:
 *       While true:
 *           await omni.kit.app.get_app().pre_update_async()
 *           # Do a bunch of python scripting things before USD Update or hydra rendering is scheduled
 *           await omni.kit.app.get_app().post_update_async()
 *           # Do a bunch of python scripting things after USD Update & hydra rendering has been scheduled
 *
 * Alternatively use either just pre_update_async() or post_update_async() in python depending on whether you want your
 * script to execute before USDUpdate or after.
 */

//! Ordering of events within a \ref omni::kit::RunLoop::postUpdate event loop.
//! \see updateorder
enum PostUpdateOrdering : int32_t
{
    //! Release GPU resources held by previous frame.
    eReleasePrevFrameGpuResources = -50,

    //! asyncio.Future blocked awaiting (post update loop).
    //!
    //! 1. IApp.post_update_async (deprecates IApp.next_update_async).
    ePythonAsyncFuturePostUpdate = -25,

    //! Enables execution of all python blocked by \ref ePythonAsyncFuturePostUpdate.
    ePythonExecPostUpdate = -10,

    //! Default post-update order value.
    eUnspecifiedPostUpdateOrder = carb::events::kDefaultOrder,

    //! Kit App Factory Update.
    eKitAppFactoryUpdate = eUnspecifiedPostUpdateOrder,

    //! Kit App OS Update.
    eKitAppOSUpdate = eUnspecifiedPostUpdateOrder,

    //! Kit Internal Update.
    eKitInternalUpdate = 100
};

#pragma push_macro("min")
#undef min

//! Ordering of events within a \ref omni::kit::RunLoop::postUpdate event loop.
//! \see updateorder
enum KitUsdStageEventOrdering : int32_t
{
    //! USD File Operation Stage Event.
    eKitUsdFileStageEvent = std::numeric_limits<carb::events::Order>::min() + 1,

    //! Default File Stage event order.
    eKitUnspecifiedUsdStageEventOrder = carb::events::kDefaultOrder,
};

#pragma pop_macro("min")

//! Ordering of USD Stage Update events during USD Context Update
//! \see eUsdContextUpdate, updateorder
enum IUsdStageEventOrdering : int32_t
{
    eIUsdStageUpdateAnimationGraph = 0, //!< Hard-coded in separate non kit-sdk repro (gitlab)
    eIUsdStageUpdatePinocchioPrePhysics = 8, //!< Hard-coded in separate non kit-sdk repro (gitlab)
    eIUsdStageUpdateTensorPrePhysics = 9, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdateForceFieldsPrePhysics = 9, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdatePhysicsVehicle = 9, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdatePhysicsCCT = 9, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdatePhysicsCameraPrePhysics = 9, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdatePhysics = 10, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdateFabricPostPhysics = 11, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdateVehiclePostPhysics = 12, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdateForceFieldsPostPhysics = 12, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdatePhysicsCameraPostPhysics = 12, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdatePhysicsUI = 12, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdatePinocchioPostPhysics = 13, //!< Hard-coded in separate non kit-sdk repro (gitlab)
    eIUsdStageUpdateOmnigraph = 100, //!< Defined inside kit-sdk
    eIUsdStageUpdatePhysxFC = 102, //!< Hard-coded in separate non kit-sdk repro (perforce)
    eIUsdStageUpdateDebugDraw = 1000, //!< Defined inside kit-sdk
    eIUsdStageUpdateLast = 2000 //!< Must always be last when all prior StageUpdate events have been handled
};

//! @}

} // namespace update
} // namespace kit
} // namespace omni
