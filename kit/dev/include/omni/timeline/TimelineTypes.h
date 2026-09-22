// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

namespace omni
{
namespace timeline
{

/**
 * Defines timeline event types to be used by TimelineEventStream.
 */
enum class TimelineEventType
{
    ePlay, /**< Timeline started to play. */
    ePause, /**< Timeline paused. */
    eStop, /**< Timeline stopped. */
    eCurrentTimeChanged, /**< Deprecated. No longer used. */
    eCurrentTimeTickedPermanent, /**< Current time is ticked by update function (called per subframe=tick even if not playing). */
    eCurrentTimeTicked, /**< Current time is ticked by update function (called per subframe=tick when playing). */
    eLoopModeChanged, /**< Looping mode changed. */
    eStartTimeChanged, /**< Start time changed. */
    eEndTimeChanged, /**< End time changed. */
    eTimeCodesPerSecondChanged, /**< Timecode per second (animation framerate) changed. */
    eAutoUpdateChanged, /**< Auto update changed. */
    ePrerollingChanged, /**< Prerolling changed. */
    eTentativeTimeChanged, /**< Tentative current time is changed by user (isn't called when timeline ticked). */
    eTicksPerFrameChanged, /**< Ticks per frame count changed. */
    eFastModeChanged, /**< Fast mode changed. Same as eFastModeChanged, kept for backward compatibility. */
    ePlayEveryFrameChanged = eFastModeChanged, /**< Play every frame (no frame skipping) changed. */
    eTargetFramerateChanged, /**< Target runloop frame rate changed. */
    eDirectorChanged, /**< Timeline is driven by a new director timeline. */
    eZoomChanged /**< Zoom range changed. */
};

}
}
