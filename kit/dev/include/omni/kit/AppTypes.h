// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief omni.kit.app utilities
#pragma once

#include "../String.h"
#include "../../carb/RString.h"
#include "../../carb/events/EventsTypes.h"

// Forward declarations
namespace carb::events
{
class IEventStream;
} // namespace carb::events

namespace omni::kit
{

//! \defgroup appstruct IApp structs
//! @{

/**
 * Application descriptor.
 * @see IApp::startup()
 */
struct AppDesc
{
    const char* carbAppName; //!< Carb application name. If `nullptr` it is derived from the executable filename.
    const char* carbAppPath; //!< Carb application path. If `nullptr` it is derived from the executable folder.
    int argc; //!< Number of values in `argv`
    char** argv; //!< Array of arguments
};

/**
 * Build information.
 * @see IApp::getBuildInfo()
 */
struct BuildInfo
{
    omni::string kitVersion; //!< Full kit version, e.g. `103.5+release.7032.aac30830.tc.windows-x86_64.release'
    omni::string kitVersionShort; //!< Short kit version, `major.minor` e.g. `103.5`
    omni::string kitVersionHash; //!< Git hash of kit build, 8 letters, e.g. `aac30830`

    //! Full kernel version, e.g. `103.5+release.7032.aac30830.tc.windows-x86_64.release'
    //! Note that this may be different than `kitVersion`
    omni::string kernelVersion;
};

/**
 * Platform information.
 * @see IApp::getPlatformInfo()
 */
struct PlatformInfo
{
    const char* config; //!< Build configuration e.g. "debug", "release"

    //! Platform descriptor e.g. "windows-x86_64", "linux-x86_64", "linux-aarch64"
    const char* platform;
    const char* pythonVersion; //!< Python version e.g. "cp310" for Python 3.10
};

/**
 * App information.
 * @see IApp::getAppInfo(), AppDesc
 */
struct AppInfo
{
    omni::string filename; //!< App filename. Name of a kit file or just 'kit'
    omni::string name; //!< App name. It is app/name setting if defined, otherwise same as `filename`
    omni::string version; //!< App version. Version in kit file or kit version
    omni::string versionShort; //!< Short app version, currently major.minor, e.g. `2021.3`

    //! Environment the application is running in, from `/app/environment/name` setting
    //! e.g. "teamcity", "launcher", "etm", "default", etc.
    omni::string environment;
    bool isExternal; //!< Is external (public) configuration
};

/**
 * Run Loop.
 *
 * A Run Loop is a collection of event streams that are pumped in order for each Run Loop iteration.
 * @see IApp::getRunLoop(), carb::events::IEventStream, carb::events::IEvents
 */
class RunLoop
{
public:
    //! Pre update events pushed every loop and stream is pumped.
    CARB_DEPRECATED("use IEventDispatcher") carb::events::IEventStream* preUpdate;
    //! Update events pushed every loop and stream is pumped.
    CARB_DEPRECATED("use IEventDispatcher") carb::events::IEventStream* update;
    //! Post update events pushed every loop and stream is pumped.
    CARB_DEPRECATED("use IEventDispatcher") carb::events::IEventStream* postUpdate;

    //! Stream for extensions to push events to, pumped every loop after postUpdate.
    CARB_DEPRECATED("use IEventDispatcher") carb::events::IEventStream* messageBus;
};

//! @}

/**
 * How to handle passed arguments when restarting an app.
 * @see IApp::restart()
 */
enum class RestartArgsPolicy
{
    eAppend, //!< Append to existing args
    eReplace, //!< Replace existing args
};

// Few predefined run loop names. Serve as hints, doesn't have to use only those.

//! \defgroup apprunloop Run Loop Names
//! @{

//! Predefined Run Loop name
//!
//! Predefined names serve as hints for Run Loops but other names may also exist
constexpr char kRunLoopDefault[] = "main";
//! @copydoc kRunLoopDefault
constexpr char kRunLoopSimulation[] = "simulation";
//! @copydoc kRunLoopDefault
constexpr char kRunLoopRendering[] = "rendering";
//! @copydoc kRunLoopDefault
constexpr char kRunLoopUi[] = "ui";

//! @}

//! \defgroup appevents App Events
//! @{

//! A shutdown event that is dispatched during the next update after postQuit is called.
//!
//! Once \ref IApp::postQuit() is called, the next \ref IApp::update() call will check for shutdown requests and start
//! the shutdown sequence. The first step of this sequence is that this event (`kGlobalEventPostQuit`) is dispatched.
//! During this event, any calls to \ref IApp::tryCancelShutdown() will abort this process (unless the posted quit
//! request is noncancellable). If no attempt to cancel the shutdown has been made, \ref kGlobalEventPreShutdown will be
//! dispatched.
//! @see IApp::postQuit(), IApp::tryCancelShutdown(), IApp::postUncancellableQuit()
//! \par Event Arguments
//! * "uncancellable" (bool) a `true` value indicates that the shutdown is not cancellable
const auto kGlobalEventPostQuit = carb::RString("omni.kit.app:post_quit");

//! A shutdown event that is dispatched to indicate the start of shutdown.
//! @see kGlobalEventPostQuit, IApp::postQuit(), IApp::tryCancelShutdown(),
//!   IApp::postUncancellableQuit()
//! \par Event Arguments
//! * None
const auto kGlobalEventPreShutdown = carb::RString("omni.kit.app:pre_shutdown");

//! An event that is dispatched at app startup time.
//!
//! This event is dispatched globally via \ref carb::eventdispatcher::IEventDispatcher immediately before
//! \ref IApp::startup() returns. This event is dispatched _before_ \ref kGlobalEventAppReady.
//! \par Event Arguments
//! * None
const auto kGlobalEventAppStarted = carb::RString("omni.kit.app:started");

//! An event that is dispatched when the application becomes ready.
//!
//! After application startup (see \ref kGlobalEventAppStarted), every call to \ref IApp::update() after the first call
//! will check for readiness. Readiness can be delayed with \ref IApp::delayAppReady() which must be called during each
//! main run loop iteration to prevent readiness. Once a run loop completes with no calls to \ref IApp::delayAppReady()
//! the application is considered "ready" and this event is dispatched via \ref carb::eventdispatcher::IEventDispatcher.
//! \par Event Arguments
//! * None
const auto kGlobalEventAppReady = carb::RString("omni.kit.app:ready");

//! The first early event that is dispatched at the beginning of the main RunLoop frame.
//!
//! The pre-update event for non-main runloops is named `runloop:<name>:preUpdate`.
//! \par Event Arguments
//! * `dt` (double) - Effectively the length of time (in seconds) of the previous frame. The first frame is `1.0/60.0`.
//! * `SWHFrameNumber` (int64) - The frame number beginning at 0.
const auto kGlobalEventPreUpdate = carb::RString("preUpdate");

//! The main update event that is dispatched during the main RunLoop frame.
//!
//! The update event for non-main runloops is named `runloop:<name>:update`.
//! \par Event Arguments
//! * `dt` (double) - Effectively the length of time (in seconds) of the previous frame. The first frame is `1.0/60.0`.
//! * `SWHFrameNumber` (int64) - The frame number beginning at 0.
const auto kGlobalEventUpdate = carb::RString("update");

//! The final update event that is dispatched during the main RunLoop frame.
//!
//! The post-update event for non-main runloops is named `runloop:<name>:postUpdate`.
//! \par Event Arguments
//! * `dt` (double) - Effectively the length of time (in seconds) of the previous frame. The first frame is `1.0/60.0`.
//! * `SWHFrameNumber` (int64) - The frame number beginning at 0.
const auto kGlobalEventPostUpdate = carb::RString("postUpdate");

//! The name of the message bus for the main RunLoop.
//!
//! This is used as a \ref carb::eventdispatcher::IMessageQueue name which messages can be posted into and it will run
//! once per runloop.
//!
//! The message bus `IMessageQueue` for non-main runloops is named `runloop:<name>:messageBus`.
const auto kGlobalMessageBus = carb::RStringKey("messageBus");

/**
 * Legacy version of \ref kGlobalEventPostQuit.
 *
 * For backwards compatibility, this event is dispatched to the local legacy event stream obtainable with
 * \ref IApp::getShutdownEventStream().
 * \par Event Arguments
 * * "uncancellable" (bool) a `true` value indicates that the shutdown is not cancellable
 */
constexpr carb::events::EventType kPostQuitEventType = 0;

/**
 * Legacy version of \ref kGlobalEventPreShutdown.
 *
 * For backwards compatibility, this event is dispatched to the local legacy event stream obtainable with
 * \ref IApp::getShutdownEventStream().
 * \par Event Arguments
 * * None
 */
constexpr carb::events::EventType kPreShutdownEventType = 1;

/**
 * Legacy version of \ref kGlobalEventAppStarted.
 *
 * For backwards compatibility, this event is dispatched to the local legacy event stream obtainable with
 * \ref IApp::getStartupEventStream().
 * \par Event Arguments
 * * None
 */
const carb::events::EventType kEventAppStarted = CARB_EVENTS_TYPE_FROM_STR("APP_STARTED");

/**
 * Legacy version of \ref kGlobalEventAppReady.
 *
 * For backwards compatibility, this event is dispatched to the local legacy event stream obtainable with
 * \ref IApp::getStartupEventStream().
 * \par Event Arguments
 * * None
 */
const carb::events::EventType kEventAppReady = CARB_EVENTS_TYPE_FROM_STR("APP_READY");


//! @}

} // namespace omni::kit
