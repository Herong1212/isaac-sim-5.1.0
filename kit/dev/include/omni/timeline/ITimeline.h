// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>
#include <carb/InterfaceUtils.h>
#include <carb/events/IEvents.h>

namespace omni
{
namespace timeline
{

class Timeline;

/**
 * Smart pointer managing an instance of the Timeline.
 */
using TimelinePtr = std::shared_ptr<Timeline>;

/**
 * Defines a timeline controller.
 */
class Timeline
{
public:
    /**
     * Plays animation with current timeCodePerSecond. if not set session start and end timecode, will play from 
       global start time to end time in stage.
     * 
     * @param startTimeCode start timeCode of session play, won't change the global StartTime.
     * @param endTimeCode start timeCode of session play, won't change the global EndTime.
     * @param looping true to enable session play looping, false to disable, won't change the global Looping.
     */
    virtual void play(double startTimeCode = 0, double endTimeCode = 0, bool looping = true) = 0;

    /**
     * Pauses animation.
     */
    virtual void pause() = 0;

    /**
     * Stops animation.
     */
    virtual void stop() = 0;

    /**
     * Rewinds the timeline by one frame.
     */
    virtual void rewindOneFrame() = 0;

    /**
     * Forwards the timeline by one frame.
     */
    virtual void forwardOneFrame() = 0;

    /**
     * Checks if animation is playing.
     *
     * @return true if animation is playing.
     */
    virtual bool isPlaying() const = 0;

    /**
     * Checks if animation is stopped, as opposed to paused.
     *
     * @return true if animation is stopped.
     */
    virtual bool isStopped() const = 0;

    /**
     * Turns on/off auto update
     *
     * @param autoUpdate autoUpdate true to enable auto update, false to disable.
     */
    virtual void setAutoUpdate(bool autoUpdate) = 0;

    /**
     * Checks if timeline auto updates the frame
     *
     * @return true if timeline is auto updating
     */
    virtual bool isAutoUpdating() const = 0;

    /**
     * Turns on/off prerolling status
     *
     * @param autoUpdate prerolling true to indicate timeline is in preroll state
     */
    virtual void setPrerolling(bool autoUpdate) = 0;

    /**
     * Checks if timeline is in prerolling mode
     *
     * @return true if timeline is in preroll
     */
    virtual bool isPrerolling() const = 0;

    /**
     * Sets animation looping mode.
     *
     * @param looping looping true to enable looping, false to disable.
     */
    virtual void setLooping(bool looping) = 0;

    /**
     * Checks if animation is looping.
     *
     * @return true if animation is looping.
     */
    virtual bool isLooping() const = 0;

    /**
     * Sets current time of animation in seconds.
     *
     * @param timeInSeconds Current time of animation in seconds.
     */
    virtual void setCurrentTime(double timeInSeconds) = 0;

    /**
     * Gets current time of animation in seconds.
     * 
     * Current time is defined as the beginning of the \b next frame. 
     * @note When queried inside time update callbacks, we are in the \b current frame, 
     * current time (defined as the beginning of the next frame) is the \b end of the current frame.
     *
     * @return Current time of animation in seconds.
     */
    virtual double getCurrentTime() const = 0;

    /**
     * Gets the start time of animation in seconds.
     * 
     * @note Start time is defined as the beginning of the first frame.
     *
     * @return Begin time of animation in seconds.
     */
    virtual double getStartTime() const = 0;

    /**
     * Sets the start time of animation in seconds. This will write into current opened stage.
     * 
     * @note The call enforces the time interval defined by start and end times to be at least one frame long.
     *
     * @param startTime Begin time of animation in seconds.
     */
    virtual void setStartTime(double startTime) = 0;

    /**
     * Gets the end time of animation in seconds.
     * 
     * @note End time means no frames can start strictly after this time point. When start and end time define an integer number of frames, end time is the end of the last animation frame.
     *
     * @return End time of animation in seconds.
     */
    virtual double getEndTime() const = 0;

    /**
     * Sets the end time of animation in seconds. This will write into current opened stage.
     *
     * @note The call enforces the time interval defined by start and end times to be at least one frame long.
     * 
     * @param endTime End time of animation in seconds.
     */
    virtual void setEndTime(double endTime) = 0;

    /**
     * Gets timeCodePerSecond metadata from currently opened stage. This is equivalent to calling GetTimeCodesPerSecond
     * on UsdStage.
     *
     * @return timeCodePerSecond for current UsdStage.
     */
    virtual double getTimeCodesPerSecond() const = 0;

    /**
     * Sets timeCodePerSecond metadata to currently opened stage. This is equivalent to calling SetTimeCodesPerSecond on
     * UsdStage.
     *
     * @param timeCodesPerSecond TimeCodePerSecond to set into current stage.
     */
    virtual void setTimeCodesPerSecond(double timeCodesPerSecond) = 0;

    /**
     * Gets TimelineEventStream, emitting TimelineEventType.
     *
     * @return IEventStream* of TimelineEventStream.
     */
    virtual carb::events::IEventStream* getTimelineEventStream() = 0;

    /**
     * Sets a tentative time of animation in seconds.
     *
     * @param timeInSeconds A tentative current time of animation in seconds.
     */
    virtual void setTentativeTime(double timeInSeconds) = 0;

     /**
     * Clear the tentative time of animation so it becomes invalid.
     * 
     */
    virtual void clearTentativeTime() = 0;

    /**
     * Gets the tentative time of animation in seconds.
     *
     * @return The tentative time if it is valid, current time if invalid.
     */
    virtual double getTentativeTime() const = 0;

    /**
     * Sets the tick count per frame, i.e. how many times update event is ticked per frame.
     *
     * @param ticksPerFrame The tick per frame count.
     */
    virtual void setTicksPerFrame(unsigned int ticksPerFrame) = 0;
    
    /**
     * Gets the tick count per frame, i.e. how many times update event is ticked per frame.
     *
     * @return The tick per frame count.
     */
    virtual unsigned int getTicksPerFrame() const = 0;

    /**
     * Gets the tick count per seconds, i.e. how many times update event is ticked per second.
     *
     * @return The tick per second count.
     */
    virtual double getTicksPerSecond() const = 0;

    /**
     * Gets the current tick index, starting from zero. Always returns zero when ticks per frame is one.
     *
     * @return The current tick index.
     */
    virtual unsigned int getCurrentTick() const = 0;

    /**
     * Turns fast mode on or off. Deprecated, same as setPlayEveryFrame.
     *
     * @param fastMode true to turn on fast mode, false to turn it off.
     */
    virtual void setFastMode(bool fastMode) = 0;

    /**
     * Checks if fast mode is on or off. Deprecated, same as getPlayEveryFrame.
     *
     * @return true is fast mode is on.
     */
    virtual bool getFastMode() const = 0;

    /**
     * Sets the target frame rate, which affects the derived FPS of the runloop in play mode.
     * Exact runloop FPS is usually not the same as this value, as it is always a multiple of getTimeCodesPerSecond.
     *
     * @param targetFrameRate The target frame rate.
     */
    virtual void setTargetFramerate(float targetFrameRate) = 0;

    /**
     * Gets the target frame rate, which affects the derived FPS of the runloop in play mode.
     * Exact runloop FPS is usually not the same as this value, as it is always a multiple of getTimeCodesPerSecond.
     *
     * @return The target frame rate.
     */
    virtual float getTargetFramerate() const = 0;

    // These new methods have no equivalent in the deprecated interface to encourage the use of the new interface

    /**
     * Converts time in seconds to time codes, w.r.t. the current timeCodesPerSecond setting of the timeline.
     *
     * @return The converted time code.
     */
    virtual double timeToTimeCode(double timeInSecs) const = 0;

    /**
     * Converts time codes to seconds, w.r.t. the current timeCodesPerSecond setting of the timeline.
     *
     * @return The converted time in seconds.
     */
    virtual double timeCodeToTime(double timeCodes) const = 0;

    /**
     * Applies all pending state changes and invokes all callbacks.
     * 
     * This method is not thread-safe, it should be called only from the main thread.
     *
     */
    virtual void commit() = 0;

    /**
     * Applies all pending state changes but does not invoke any callbacks.
     *
     * This method is thread-safe.
     *
     */
    virtual void commitSilently() = 0;

    /**
     * Turns frame skipping off (true) or on (false). Same as setFastMode.
     *
     * @param playEveryFrame true to turn frame skipping off.
     */
    virtual void setPlayEveryFrame(bool playEveryFrame) = 0;

    /**
     * Checks if the timeline sends updates every frame. Same as getFastMode.
     *
     * @return true if the timeline does not skip frames.
     */
    virtual bool getPlayEveryFrame() const = 0;

    /**
     * Sets a director Timeline.
     *
     * When a director is set, the timeline mimics its behavior and any
     *   state changing call from all other sources are ignored.

     * @param timeline The timeline object to be set as the director.
     *                 Pass nullptr to clear the current director.
     */
    virtual void setDirector(TimelinePtr timeline) = 0;

    /**
     * Returns the current director Timeline.
     *
     * @return The director timeline or nullptr if none is set.
     */
    virtual TimelinePtr getDirector() const = 0;

    /**
    * Sets the zoom range, i.e. the playback interval.
    *
    * Values are truncated to the [getStartTime(), getEndTime()] interval,
    *    which is also the default range.
    * A minimum of one frame long range is enforced.
    *
    * @param startTime: start time of zoom in seconds. Must be less or equal than endTime.
    * @param endTime: End time of zoom in seconds. Must be greater or equal than endTime.
    */
    virtual void setZoomRange(double startTime, double endTime) = 0;

    /**
    * Clears the zoom state, i.e. sets the zoom range to [getStartTime(), getEndTime()].
    */
    virtual void clearZoom() = 0;

    /**
    * Returns whether a zoom is set, i.e. the zoom range is not the entire
    *    [getStartTime(), getEndTime()] interval.
    * 
    * @return true if getStartTime() < getZoomStartTime() or getZoomEndTime() < getEndTime()
    *              (note that "<=" always holds).
    *         false otherwise.
    */
    virtual bool isZoomed() const = 0;

    /**
    * Gets the start time of zoomed animation in seconds.
    *
    * @return: The start time of zoomed animation in seconds.
    *          When no zoom is set, this function returns getStartTime().
    */
    virtual double getZoomStartTime() const = 0;

    /**
     * Gets the end time of zoomed animation in seconds.
     *
     * @return: The end time of zoomed animation in seconds.
     *          When no zoom is set, this function returns getEndTime().
     */
    virtual double getZoomEndTime() const = 0;
};

/**
 * Defines a Timeline controller factory. 
 * 
 * For compatibility reasons it also defines a timeline controller. This use case is deprecated.
 */
class ITimeline
{
public:
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::timeline::ITimeline", 1, 0);

    //----------------------
    // Deprecated interface
    //----------------------

    /**
     * Deprecated Plays animation with current timeCodePerSecond. if not set session start and end timecode, will play from 
       global start time to end time in stage.
     * 
     * @param startTimeCode start timeCode of session play, won't change the global StartTime.
     * @param endTimeCode start timeCode of session play, won't change the global EndTime.
     * @param looping true to enable session play looping, false to disable, won't change the global Looping.
     */
    virtual void play(double startTimeCode = 0, double endTimeCode = 0, bool looping = true) = 0;

    /**
     * Deprecated. Pauses animation.
     */
    virtual void pause() = 0;

    /**
     * Deprecated. Stops animation.
     */
    virtual void stop() = 0;

    /**
     * Deprecated. Rewinds the timeline by one frame.
     */
    virtual void rewindOneFrame() = 0;

    /**
     * Deprecated. Forwards the timeline by one frame.
     */
    virtual void forwardOneFrame() = 0;

    /**
     * Deprecated. Checks if animation is playing.
     *
     * @return true if animation is playing.
     */
    virtual bool isPlaying() const = 0;

    /**
     * Deprecated. Checks if animation is stopped, as opposed to paused.
     *
     * @return true if animation is stopped.
     */
    virtual bool isStopped() const = 0;

    /**
     * Deprecated. Turns on/off auto update
     *
     * @param autoUpdate autoUpdate true to enable auto update, false to disable.
     */
    virtual void setAutoUpdate(bool autoUpdate) = 0;

    /**
     * Deprecated. Checks if timeline auto updates the frame
     *
     * @return true if timeline is auto updating
     */
    virtual bool isAutoUpdating() const = 0;

    /**
     * Deprecated. Turns on/off prerolling status
     *
     * @param autoUpdate prerolling true to indicate timeline is in preroll state
     */
    virtual void setPrerolling(bool autoUpdate) = 0;

    /**
     * Deprecated. Checks if timeline is in prerolling mode
     *
     * @return true if timeline is in preroll
     */
    virtual bool isPrerolling() const = 0;

    /**
     * Deprecated. Sets animation looping mode.
     *
     * @param looping looping true to enable looping, false to disable.
     */
    virtual void setLooping(bool looping) = 0;

    /**
     * Deprecated. Checks if animation is looping.
     *
     * @return true if animation is looping.
     */
    virtual bool isLooping() const = 0;

    /**
     * Deprecated. Sets current time of animation in seconds.
     *
     * @param timeInSeconds Current time of animation in seconds.
     */
    virtual void setCurrentTime(double timeInSeconds) = 0;

    /**
     * Deprecated. Gets current time of animation in seconds.
     *
     * @return Current time of animation in seconds.
     */
    virtual double getCurrentTime() const = 0;

    /**
     * Deprecated. Gets the start time of animation in seconds.
     *
     * @return Begin time of animation in seconds.
     */
    virtual double getStartTime() const = 0;

    /**
     * Deprecated. Sets the start time of animation in seconds. This will write into current opened stage.
     *
     * @param startTime Begin time of animation in seconds.
     */
    virtual void setStartTime(double startTime) = 0;

    /**
     * Deprecated. Gets the end time of animation in seconds.
     *
     * @return End time of animation in seconds.
     */
    virtual double getEndTime() const = 0;

    /**
     * Deprecated. Sets the end time of animation in seconds. This will write into current opened stage.
     *
     * @param endTime End time of animation in seconds.
     */
    virtual void setEndTime(double endTime) = 0;

    /**
     * Deprecated. Gets timeCodePerSecond metadata from currently opened stage. This is equivalent to calling GetTimeCodesPerSecond
     * on UsdStage.
     *
     * @return timeCodePerSecond for current UsdStage.
     */
    virtual double getTimeCodesPerSecond() const = 0;

    /**
     * Deprecated. Sets timeCodePerSecond metadata to currently opened stage. This is equivalent to calling SetTimeCodesPerSecond on
     * UsdStage.
     *
     * @param timeCodesPerSecond TimeCodePerSecond to set into current stage.
     */
    virtual void setTimeCodesPerSecond(double timeCodesPerSecond) = 0;

    /**
     * Deprecated. Gets TimelineEventStream, emitting TimelineEventType.
     *
     * @return IEventStream* of TimelineEventStream.
     */
    virtual carb::events::IEventStream* getTimelineEventStream() = 0;

    /**
     * Deprecated. Sets a tentative time of animation in seconds.
     *
     * @param timeInSeconds A tentative current time of animation in seconds.
     */
    virtual void setTentativeTime(double timeInSeconds) = 0;

     /**
     * Deprecated. Clear the tentative time of animation so it becomes invalid.
     * 
     */
    virtual void clearTentativeTime() = 0;

    /**
     * Deprecated. Gets the tentative time of animation in seconds.
     *
     * @return The tentative time if it is valid, current time if invalid.
     */
    virtual double getTentativeTime() const = 0;

    /**
     * Deprecated. Sets the tick count per frame, i.e. how many times update event is ticked per frame.
     *
     * @param ticksPerFrame The tick per frame count.
     */
    virtual void setTicksPerFrame(unsigned int ticksPerFrame) = 0;
    
    /**
     * Deprecated. Gets the tick count per frame, i.e. how many times update event is ticked per frame.
     *
     * @return The tick per frame count.
     */
    virtual unsigned int getTicksPerFrame() const = 0;

    /**
     * Deprecated. Gets the tick count per seconds, i.e. how many times update event is ticked per second.
     *
     * @return The tick per second count.
     */
    virtual double getTicksPerSecond() const = 0;

    /**
     * Deprecated. Gets the current tick index, starting from zero. Always returns zero when ticks per frame is one.
     *
     * @return The current tick index.
     */
    virtual unsigned int getCurrentTick() const = 0;

    /**
     * Deprecated. Turns fast mode on or off.
     *
     * @param fastMode true to turn on fast mode, false to turn it off.
     */
    virtual void setFastMode(bool fastMode) = 0;

    /**
     * Deprecated. Checks if fast mode is on or off.
     *
     * @return true is fast mode is on.
     */
    virtual bool getFastMode() const = 0;

    /**
     * Deprecated. Sets the target frame rate, which affects the derived FPS of the runloop in play mode.
     * Exact runloop FPS is usually not the same as this value, as it is always a multiple of getTimeCodesPerSecond.
     *
     * @param targetFrameRate The target frame rate.
     */
    virtual void setTargetFramerate(float targetFrameRate) = 0;

    /**
     * Deprecated. Gets the target frame rate, which affects the derived FPS of the runloop in play mode.
     * Exact runloop FPS is usually not the same as this value, as it is always a multiple of getTimeCodesPerSecond.
     *
     * @return The target frame rate.
     */
    virtual float getTargetFramerate() const = 0;


    //---------------
    // New interface
    //---------------

    /**
     * Gets timeline with the given name. Creates a new one if it does not exist.
     *
     * @param name Name of the timeline.
     *
     * @return The timeline
     */
    virtual TimelinePtr getTimeline(const char* name = nullptr) = 0;

    /**
     * Destroys the timeline with the given name if nothing references it. Does not release the default timeline.
     *
     * @param name Name of the timeline.
     *
     * @return True if a timeline was deleted, false otherwise. The latter happens when the timeline does not exist, it is in use, or it is the default timeline.
     */
    virtual bool destroyTimeline(const char* name) = 0;
};

/**
 * Gets cached ITimeline interface.
 *
 * @return Cached ITimeline interface.
 */
inline TimelinePtr getTimeline(const char* name = nullptr)
{
    auto manager = carb::getCachedInterface<omni::timeline::ITimeline>();
    return manager == nullptr ? nullptr : manager->getTimeline(name);
}
}
}
