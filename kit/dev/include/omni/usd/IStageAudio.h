// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once


#include <carb/events/IEvents.h>
#include <carb/audio/IAudioPlayback.h>
#include <carb/audio/IAudioUtils.h>

#include <omni/usd/Api.h>

#include <limits.h>

namespace omni
{
namespace usd
{
namespace audio
{

class AudioManager;

/** base type for a streamer handle value.  This uniquely identifies a single streamer
 *  that has been created in the audio manager.  A value of this type can be
 *  @ref kInvalidStreamerId to indicate an invalid handle.
 */
using StreamerId = size_t;

/** an invalid handle value for a streamer.  This can be returned from createCaptureStreamer(). */
constexpr StreamerId kInvalidStreamerId = (size_t)(SIZE_MAX);

/** The status of a sound's asset's loading. */
enum class AssetLoadStatus
{
    eDone, /**< Asset has finished loading */
    eInProgress, /**< Asset loading is in progress */
    eFailed, /**< Asset has failed to load */
    eNotRegistered, /**< Prim was not registered from hydra yet. */
    eNoAssetPath, /**< No asset path has been set for the prim.  No load has been queued. */
};

/** The default value to be used for a setting. */
enum class FeatureDefault
{
    eOn, /**< The setting is enabled when a value is not explicitly set. */
    eOff, /**< The setting is disabled when a value is not explicitly set. */
    eForceOn, /**< The setting is always enabled.
               *   This is intended to allow users to override all sounds in
               *   a scene to test what a specific feature does. */
    eForceOff, /**< The setting is always disabled.
                *   This is intended to allow users to override all sounds in
                *   a scene to test what a specific feature does. */
};

/** Names for the various change notification events that can be sent on the event
 *  stream from UsdAudioContext::getMetadataChangeStream().
 */
enum class EventType
{
    /** An event type that is sent from UsdAudioContext::getMetadataChangeStream().
     *  This indicates that the audio metadata has changed for the current stage.
     *  This is also sent when a new stage is loaded.
     */
    eMetadataChange = 1,

    /** An event type that is sent from UsdAudioContext::getMetadataChangeStream().
     *  This indicates that the stage's listener state has changed and any property
     *  windows should be updated.  This change may include a new listener being
     *  added to the stage or an existing listener being removed from the stage.
     */
    eListenerListChange,

    /** An event type that is sent from UsdAudioContext::getMetadataChangeStream().
     *  This indicates that the active listener in the stage has changed and any
     *  property windows displaying it should be updated.
     */
    eActiveListenerChange,

    /** The context object has been created and is now valid.  It can be retrieved with a call to
     *  getPlaybackContext().
     */
    eContextCreated,

    /** The context object will be destroyed soon.  External callers that hold the context object
     *  should invalidate their pointer and avoid using it further.
     */
    eContextWillBeDestroyed,

    /** The context object has been destroyed.  External calls that held the context object should
     *  already no longer be using this object.  This is just a notification that the object
     *  destruction has been completed.
     */
    eContextDestroyed,
};

/** The method that will be used to calculate the length of a sound prim. */
enum class SoundLengthType
{
    /** The length of time the sound is estimated to play for in the stage once
     *  it's triggered.
     *  This will be the lesser of the difference between the sound's start and
     *  end times (if an end time is set on the prim) or the length of the
     *  actual sound itself (including `mediaOffsetStart`, `mediaOffsetEnd`
     *  and `timeScale`), multiplied by loop count.
     *  Note that timeScale is taken into account when calculating the play time
     *  of an asset.
     *  For sounds that are set to loop infinitely, this will be a very large
     *  number (on the scale of 100 days).
     */
    ePlayLength,

    /** The length of the sound.
     *  This doesn't include the sound's start time, end time or loop count.
     *  This is calculated using `mediaOffsetStart` and `mediaOffsetEnd` if those
     *  are set; otherwise, this just returns the sound asset's length.
     *  `timeScale` will also affect the length of the sound in this case.
     */
    eSoundLength,

    /** The length of the underlying sound asset, ignoring any USD parameters. */
    eAssetLength
};

/** A pure virtual class for streaming audio data from an @ref AudioManager. */
class Streamer
{
public:
    /** A callback for when a stream opens.
     *  @param[inout] format  The format of the stream.
     *                        This format can be edited to whatever is needed by the
     *                        callback and the audio engine will convert the data to
     *                        the desired format.
     *  @param[inout] context The user-specified context.
     *  @returns `true` if the stream was initialized successfully.
     *  @returns `false` if the stream should be abandoned.
     */
    virtual bool open(carb::audio::SoundFormat* format) noexcept = 0;

    /** A callback for when a stream closes.
     *  @param[inout] context The user-specified context.
     */
    virtual void close() noexcept = 0;

    /** A callback that receives audio data.
     *  @param[in]    data    The buffer of audio data.
     *  @param[in]    bytes   The number of bytes of data specified in @p data.
     *                        This buffer is only valid until the callback returns.
     *  @param[inout] context The user-specified context.
     *  @note This callback is sent from the audio engine's thread, so this callback
     *        must do minimal work and return to avoid stalling the audio engine.
     *        Any callback that wants to do something expensive, such as rendering
     *        an image or performing a FFT should use the callback to copy data to
     *        a buffer, then process that buffer in a separate thread.
     *  @note It's not possible to change the rate at which data is received.
     *        Because Kit plays audio to a physical device, that device must be
     *        allowed to control the data rate to avoid underruns/overruns.
     */
    virtual void writeData(const void* data, size_t bytes) noexcept = 0;
};

/** A descriptor for drawWaveform(). */
struct AudioImageDesc
{
    /** Flags that alter the drawing style. */
    carb::audio::AudioImageFlags flags;

    /** This specifies which audio channel from @ref sound will be rendered.
     *  This is ignored when @ref fAudioImageMultiChannel or @ref fAudioImageSplitChannels
     *  is set on @ref flags.
     */
    size_t channel;

    /** The buffer that holds the image data.
     *  The image format is RGBA8888.
     *  This must be @ref height * @ref pitch bytes long.
     *  This may not be nullptr.
     */
    void* image;

    /** The width of the image in pixels. */
    size_t width;

    /** The width of the image buffer in bytes.
     *  This can be set to 0 to use 4 * @ref width as the pitch.
     *  This may be used for applications such as writing a subimage or an
     *  image that needs some specific alignment.
     */
    size_t pitch;

    /** The height of the image in pixels. */
    size_t height;

    /** The background color to write to the image in normalized RGBA color.
     *  The alpha channel in this color is not used to blend this color with
     *  the existing data in @ref image; use @ref fAudioImageNoClear if you
     *  want to render on top of an existing image.
     *  This value is ignored when @ref fAudioImageNoClear is set on @ref flags.
     */
    carb::Float4 background;

    /** The colors to use for the image in normalized RGBA colors.
     *  If @ref carb::audio::fAudioImageMultiChannel or @ref
     *  carb::audio::fAudioImageSplitChannels are set, each element in this
     *  array maps to each channel in the output audio data; otherwise, element
     *  0 is used as the color for the single channel.
     */
    carb::Float4 colors[carb::audio::kMaxChannels];
};


/** The IStageAudio interface.
 *  This was previously a Carbonite interface, but it was changed to a regular
 *  C interface due to linking issues related to the USD shared lib.
 *  This may return to being a Carbonite interface eventually.
 *  @{
 */

/** Get the default audio manager.
 *  @returns The default audio manager.
 *           This is equivalent to calling UsdContext::getContext()->getAudioManager(),
 *           except that you don't have to include UsdContext.h in your module.
 *           At the time of writing, UsdContext.h pulls in the USD headers, which
 *           causes conflicts with pybind11 modules.
 *  @returns nullptr if audio is disabled.
 *  @returns nullptr if the UsdContext couldn't be retrieved for whatever reason.
 */
OMNI_USD_API AudioManager* getDefaultAudioManager();

/** Retrieve the audio playback context for an audio manager.
 *
 *  @param[in] mgr  The audio manager to retrieve the playback context from.  This may
 *                  not be `nullptr`.  This can be the audio manager object returned
 *                  from getDefaultAudioManager().
 *  @returns The audio playback context that the requested audio manager is using.
 *
 *  @remarks This retrieves the audio playback context object for the requested
 *           audio manager object.  This can be used by external callers to play
 *           their own sounds on the same context that the main USD stage does.
 *
 *           Notifications about the creation and destruction of the context object
 *           can be received by subscribing to the event stream returned by
 *           getMetadataChangeStream().  The interesting events in this case will be
 *           the @a EventType::eContext* events.  Note that the context is only ever
 *           created when the given audio manager is first created.  This means that
 *           most callers would not be subscribed to the event stream by that point.
 *           This is normally acceptable since the same context is reused from one
 *           stage to the next.  The more important notification will be the
 *           @ref EventType::eContextWillBeDestroyed event.  When this is received, the
 *           context object should be considered invalidated and all future operations
 *           on it stopped.  The playback context object is typically only destroyed
 *           during shutdown when the audio manager is unloading.
 */
OMNI_USD_API carb::audio::Context* getPlaybackContext(AudioManager* mgr);

/** Retrieves the total number of registered sound objects in the USD stage.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *
 *  @return the total number of sounds in the stage.  This will be one larger than
 *           the highest valid index of sound prims in the current USD stage.
 *
 *  @note Sounds that have not had their asset loaded yet (or their asset failed
 *        to load) will not show up in the sound count unless they've been passed
 *        to an IStageAudio function.
 */
OMNI_USD_API size_t getSoundCount(AudioManager* mgr);

/** Immediately plays the requested USD stage sound if it is loaded.
 *
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to sound prim to play.
 *  @return no return value.
 *
 *  @remarks This plays a single non-looping instance of a USD stage sound immediately.  The
 *           sound must have already been loaded.  If the sound resource was missing or
 *           couldn't be loaded, this call will simply be ignored.  This will return
 *           immediately after scheduling the sound to play.  It will never block for the
 *           duration of the sound playback.  This sound may be prematurely stopped with
 *           stopSound().
 *
 *  @note This operation is always thread safe.
 *
 *  @note The loopCount parameter of the prim parameter is ignored in this call.
 *        This functionality will be added in a future revision.
 *
 *  @note If the sound at path @p path is playing when this is called, the
 *        previous playing instance will continue playing.
 *        The previously playing instance will no longer receive updates when
 *        the USD prim at path @p path is changed.
 *        The only way to stop this previously playing instance is for it to
 *        end on its own or for the timeline to stop.
 *        In the future, this function may stop the previously playing instance.
 *        For cases where playing the same sound repeatedly in a fire-and-forget
 *        fashion is desired, use spawnVoice().
 *
 *  @note The playing sound will stop when the timeline is stopped.
 *        This behavior may change in the future.
 *
 *  @note OmniSound prims that are scheduled to play in an animation should not also
 *        be played with playSound(), since it may prevent them from playing
 *        when they are scheduled to play.
 */
OMNI_USD_API void playSound(AudioManager* mgr, const char* path);

/** Queries whether a sound object is currently playing.
 *
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to sound prim to query the playing state for.
 *  @return true if the sound object is currently playing.
 *  @return false if the sound has either finished playing or has not been played yet.
 *
 *  @remarks This queries whether a sound is currently playing.  If this fails, that may mean
 *           that the sound ended naturally on its own or it was explicitly stopped.  Note
 *           that this may continue to return true for a short period after a sound has been
 *           stopped with stopSound() or stopAllSounds().  This period may be up to 10
 *           milliseconds.
 *
 *  @note This only checks the most recently playing instance of a sound,
 *        if multiple simultaneous sounds have been spawned with playSound().
 */
OMNI_USD_API bool isSoundPlaying(AudioManager* mgr, const char* path);

/** Immediately schedules the stop of the playback of a sound.
 *
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to sound prim to stop playback for.
 *
 *  @remarks This stops the playback of an active sound.  If the sound was not playing or had
 *           already naturally stopped on its own, this call is ignored.
 *
 *  @note This only stops the most recently played instance of a sound, if
 *        multiple overlapping instances of a sound were played with playSound().
 */
OMNI_USD_API void stopSound(AudioManager* mgr, const char* path);

/** Retrieves length of a sound in seconds (if known).
 *
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to sound prim to retrieve the length for.
 *  @return the play length of the sound in seconds if the asset is loaded and the length
 *          can be calculated.
 *  @return 0.0 if the sound asset is not available yet or the length could not be properly
 *          calculated.
 *
 *  @remarks This calculates the length of a USD stage sound in seconds.  This will be the
 *           lesser of the difference between the sound's start and end times (if an end time
 *           is set on the prim) or the length of the actual sound asset itself (if not
 *           looping).  In either case, this will be the amount of time that the sound would
 *           be expected to play for if it were triggered.  For sounds that are set to loop,
 *           the returned time will include all scheduled loop iterations.  For sounds that
 *           are set to loop infinitely, this will be a very large number (on the scale of
 *           100 days).
 *           This is equivalent to calling getSoundLengthEx() with `type` set to `ePlayLength`.
 */
OMNI_USD_API double getSoundLength(AudioManager* mgr, const char* path);

/** Retrieves length of a sound in seconds (if known).
 *
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to sound prim to retrieve the length for.
 *  @param[in] type The type of calculation to perform.
 *  @return The play length of the sound in seconds if the asset is loaded and the length
 *          can be calculated.
 *  @return 0.0 if the sound asset is not available yet or the length could not be properly
 *          calculated.
 */
OMNI_USD_API double getSoundLengthEx(AudioManager* mgr, const char* path, SoundLengthType type);

/** Stops all currently playing USD stage sounds.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *
 *  @return no return value.
 *
 *  @remarks This stops all currently playing stage sounds.  Any sounds that have been
 *           queued for playback will be stopped.  UI sounds will not be affected.  This
 *           is intended to be used to reset the sound playback system when an animation
 *           sequence is stopped.  This will be automatically called internally whenever
 *           the animation sequence is stopped or it loops.
 */
OMNI_USD_API void stopAllSounds(AudioManager* mgr);

/** Immediately plays the requested USD stage sound as a new @ref carb::audio::Voice if it is loaded.
 *
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to sound prim to spawn a voice from.
 *
 *  @returns The new voice that was spawned.
 *           This returns a handle, so there is no need to free the result; the
 *           pointer can be discarded.
 *           This voice's settings are only a snapshot of the sound prim that
 *           they were based off. Updates to these parameters will have to be
 *           performed on the returned voice through the IAudioPlayback interface.
 *  @returns nullptr if a new voice could not be spawned.
 *
 *  @remarks This begins playing the requested sound as a new @ref carb::audio::Voice.
 *           The sound must have already been loaded or nullptr will be returned.
 *           The spawned voice plays the sound asynchronously for the lifetime
 *           of the voice.
 *           This is intended for cases where the behavior of playSound() is too
 *           limiting.
 *
 *  @note This operation is always thread safe.
 *
 *  @note stopAllSounds() and stopSound() do not affect the playing voices
 *        spawned from this call.
 *
 *  @note Unlike playSound(), the loopCount parameter of the prim is used, so
 *        the voice must be explicitly stopped if the voice is infinitely
 *        looping.
 *
 *  @note Unlike playSound(), these voice handles are managed separately from
 *        the voice handles of the timeline, so spawning a voice from a sound
 *        that will play on the timeline shouldn't affect that sound's timeline
 *        playback.
 *        Stopping the timeline will also not stop these playing voices.
 */
OMNI_USD_API carb::audio::Voice* spawnVoice(AudioManager* mgr, const char* path);

/** Queries whether the asset of an individual sound has been fully loaded.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to sound prim to retrieve the status of.
 *  @return AssetLoadStatus::eInProgress if the asset is in the process of loading.
 *  @return AssetLoadStatus::eDone if the asset has finished loading and is ready
 *          for immediate playback.
 *  @return AssetLoadStatus::eFailed if the asset has failed to load.
 *  @return AssetLoadStatus::eFailed if the audio manager has not loaded.
 *  @return AssetLoadStatus.NotRegistered if the sound prim has not been
 *          registered with the audio manager yet. This happens when the
 *          hydra renderer hasn't started creating the prims yet.
 */
OMNI_USD_API AssetLoadStatus getSoundAssetStatus(AudioManager* mgr, const char* path);

/** Bind a callback for when assets are loaded.
 *  @param[in] mgr             The AudioManager instance that this function acts upon.
 *  @param[in] path            The path to sound prim to bind a callback to.
 *  @param[in] callback        The callback to fire once a load has occurred.
 *                             The parameter passed to this callback is @p callbackContext.
 *  @param[in] callbackContext The context parameter to pass to @p callback.
 *
 *  @returns true if the callback was bound successfully.
 *  @returns true if the callback was executed immediately.
 *  @returns false if the prim path passed corresponds to a prim that's not
 *                 of type `OmniSound`.
 *  @returns false if the prim path passed did not correspond to any prim.
 *  @returns false if an unexpected error prevents the callback from occurring.
 *
 *  @remarks This will fire the callback when the sound's asset is loaded or
 *           immediately if the asset was already loaded.  The callback will
 *           only fire once.
 */
OMNI_USD_API bool subscribeToAssetLoad(AudioManager* mgr, const char* path, void (*callback)(void*), void* callbackContext);

/** Change the active Listener prim in the scene.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] path The path to the Listener prim to set.
 *                  This can be nullptr to leave the active camera as the
 *                  active listener.
 *  @returns true if the prim at @p path was set as the active prim.
 *  @returns false if the prim at @p path was not registered with hydra.
 *           This can occur if hydra has not informed the audio manager about
 *           its existence yet.
 */
OMNI_USD_API bool setActiveListener(AudioManager* mgr, const char* path);

/** Get the active Listener prim in the scene.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @returns The path to the active listener if one is set.
 *  @returns nullptr if no active listener is set, which means the active camera
 *           is being used as the listener.
 */
OMNI_USD_API const char* getActiveListener(AudioManager* mgr);

/** Retrieves the total number of listener prims in the current stage.
 *
 *  @param[in] mgr  The stage audio manager instance that this function acts upon.  This
 *                  must not be nullptr.
 *  @returns The total number of listener prims in the current stage.  Note that this will
 *           reflect the total number of listener prims that have been registered with the
 *           audio manager.  This will not necessarily always match with the number of
 *           listener prims that USD knows about from one moment to the next.  There may be
 *           a small delay between when a prim is added or removed and when the audio manager
 *           is notified of that change.
 */
OMNI_USD_API size_t getListenerCount(AudioManager* mgr);

/** Retrieves the SDF path of an indexed listener prim in the current stage.
 *
 *  @param[in] mgr      The stage audio manager instance that this function acts upon.  This
 *                      must not be `nullptr`.
 *  @param[in] index    The zero based index of the listener prim to retrieve the SDF path for.
 *                      This should be between 0 and one less than the most recent return value
 *                      from getListenerCount().
 *  @param[out] sdfPath Receives the SDF path of the requested listener prim.  This may not be
 *                      `nullptr`.
 *  @param[in] maxLen   The maximum number of characters including the terminating null that can
 *                      fit in @p sdfPath.
 *  @returns `true` if the path of the requested listener prim is successfully returned.  Returns
 *           `false` otherwise.
 */
OMNI_USD_API bool getListenerByIndex(AudioManager* mgr, size_t index, char* sdfPath, size_t maxLen);

/** Set the default value for whether doppler calculations are enabled for the current USD Stage.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] value The value to set this as.
 *                   The default value of this is @ref FeatureDefault::eOff.
 *                   This is the default because Doppler effect's implementation
 *                   is still experimental. The default will be switched to
 *                   @ref FeatureDefault::eOn when the feature is stabilized.
 *  @remarks This will append the USD Stage metadata to add this new scene setting.
 */
OMNI_USD_API void setDopplerDefault(AudioManager* mgr, FeatureDefault value = FeatureDefault::eOff);

/** Get the default value for whether doppler calculations are enabled for the current USD Stage.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @returns The default value for whether doppler calculations are enabled for the current USD Stage.
 */
OMNI_USD_API FeatureDefault getDopplerDefault(AudioManager* mgr);

/** Set the default value for whether distance delayed audio is enable for the current USD Stage.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] value The value to set this as.
 *                   The default value of this is @ref FeatureDefault::eOff.
 *                   This is the default because distance delay can have a very
 *                   confusing effect if worldUnitScale hasn't been set correctly.
 *  @remarks This will append the USD Stage metadata to add this new scene setting.
 */
OMNI_USD_API void setDistanceDelayDefault(AudioManager* mgr, FeatureDefault value = FeatureDefault::eOff);

/** Set the default value for whether distance delayed audio is enable for the current USD Stage.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @returns The default value for whether distance delayed audio is enable for the current USD Stage.
 */
OMNI_USD_API FeatureDefault getDistanceDelayDefault(AudioManager* mgr);

/** Set the default value for whether interaural delay is enabled for the current USD Stage.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] value The value to set this as.
 *                   The default value of this is @ref FeatureDefault::eOff.
 *                   This feature is currently not implemented.
 *  @remarks This will append the USD Stage metadata to add this new scene setting.
 */
OMNI_USD_API void setInterauralDelayDefault(AudioManager* mgr, FeatureDefault value = FeatureDefault::eOff);

/** Get the default value for whether interaural delay is enabled for the current USD Stage.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @returns the default value for whether interaural delay is enabled for the current USD Stage.
 */
OMNI_USD_API FeatureDefault getInterauralDelayDefault(AudioManager* mgr);

/** The minimum number of sounds in a scene that can be played concurrently.
 *  @param[in] mgr    The stage audio manager instance that this function acts upon.
 *                    This must not be nullptr.
 *  @param[in] value  The new value for the number of concurrent voices.
 *
 *  @remarks In a scene where `concurrentVoice` is set to `N` and `N + 1`
 *           sounds are played concurrently, Omniverse Kit will choose to not
 *           play the `N+1`th sound to the audio device and just track it as a
 *           'virtual' voice.
 *           The voices chosen to become 'virtual' will be the lowest priority
 *           or silent. A 'virtual' voice should begin playing again as soon
 *           as one of the `N` playing voices has finished.
 */
OMNI_USD_API void setConcurrentVoices(AudioManager* mgr, int32_t value = 64);

/** Gets the minimum number of sounds in a scene that can be played concurrently.
 *  @param[in] mgr    The stage audio manager instance that this function acts upon.
 *                    This must not be nullptr.
 *  @returns the minimum number of sounds in a scene that can be played concurrently.
 */
OMNI_USD_API int32_t getConcurrentVoices(AudioManager* mgr);

/** Sets the speed of sound in the medium surrounding the listener (typically air).
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @param[in] value The new value for the speed of sound.
 *
 *  @remarks This is measured in meters per second.
 *           This would typically be adjusted when doing an underwater scene.
 *           The speed of sound in dry air at sea level is approximately 340.0m/s.
 *
 */
OMNI_USD_API void setSpeedOfSound(AudioManager* mgr, double value = carb::audio::kDefaultSpeedOfSound);

/** Gets the speed of sound in the medium surrounding the listener (typically air).
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @returns The speed of sound in the medium surrounding the listener.
 */
OMNI_USD_API double getSpeedOfSound(AudioManager* mgr);

/** Sets a scaler that can exaggerate or lessen the Doppler effect.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @param[in] value The new value for the doppler scale.
 *
 *  @remarks Setting this above 1.0 will exaggerate the Doppler effect.
 *           Setting this below 1.0 will lessen the Doppler effect.
 *           Negative values and zero are not allowed.
 *           Doppler effects alter the pitch of a sound based on its relative
 *           velocity to the listener.
 */
OMNI_USD_API void setDopplerScale(AudioManager* mgr, double value = 1.0);

/** Gets a scaler for the doppler effect.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @returns The scaler for the doppler effect.
 */
OMNI_USD_API double getDopplerScale(AudioManager* mgr);

/** Sets a Limit on the maximum Doppler pitch shift that can be applied to a playing voice.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @param[in] value The new value for the doppler limit.
 *
 *  @remarks Since Omniverse Kit does not handle supersonic spatial audio, a
 *           maximum frequency shift must be set for prims that move toward the
 *           listener at or faster than the speed of sound.  This is mostly
 *           useful for handling edge cases such as teleporting an object far
 *           away while it's playing a sound.
 */
OMNI_USD_API void setDopplerLimit(AudioManager* mgr, double value = 2.0);

/** Gets a Limit on the maximum Doppler pitch shift that can be applied to a playing voice.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @returns The Limit on the maximum Doppler pitch shift that can be applied to a playing voice.
 */
OMNI_USD_API double getDopplerLimit(AudioManager* mgr);

/**  This sets the timescale modifier for all spatial voices.
 *   @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                    This must not be nullptr.
 *   @param[in] value The new value for the spatial timescale.
 *
 *   @remarks Each spatial OmniSound prim multiplies its timeScale attribute by this value.
 *            For example, setting this to 0.5 will play all spatial sounds at
 *            half speed and setting this to 2.0 will play all non-spatial
 *            sounds at double speed.
 *            This affects delay times for the distance delay effect.
 *            Altering the playback speed of a sound will affect the pitch of the sound.
 *            The limits of this setting under Omniverse Kit are [1/1024, 1024].
 *            This feature is intended to allow time-dilation to be performed with the
 *            sound effects in the scene without affecting non-spatial elements like
 *            the background music.
 */
OMNI_USD_API void setSpatialTimeScale(AudioManager* mgr, double value = 1.0);

/** This gets the timescale modifier for all spatial voices.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @returns The timescale modifier for all spatial voices.
 */
OMNI_USD_API double getSpatialTimeScale(AudioManager* mgr);

/** The timescale modifier for all non-spatial voices.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be ptr.
 *  @param[in] value The new value for the non-spatial timescale.
 *
 *  @remarks Each prim multiplies its timeScale attribute by this value.
 *           For example, setting this to 0.5 will play all non-spatial sounds
 *           at half speed and setting this to 2.0 will play all non-spatial
 *           sounds at double speed.
 *           Altering the playback speed of a sound will affect the pitch of the sound.
 *           The limits of this setting under Omniverse Kit are [1/1024, 1024].
 */
OMNI_USD_API void setNonSpatialTimeScale(AudioManager* mgr, double value = 1.0);

/** The timescale modifier for all non-spatial voices.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be ptr.
 *  @returns The timescale modifier for all non-spatial voices.
 */
OMNI_USD_API double getNonSpatialTimeScale(AudioManager* mgr);


/** Test whether the Hydra audio plugin is accessible.
 *  @returns This returns true if the plugin could load.
 *  @returns This returns false if the plugin failed to load or doesn't exist.
 *  @remarks This is intended to allow the tests to check whether the Hydra audio
 *           plugin is still working.
 */
OMNI_USD_API bool testHydraPlugin();

/** Switch to use a new device for for audio output.
 *
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be ptr.
 *  @param[in] deviceName   the name or GUID of the device to set as active.  This must
 *                          exactly match the name or GUID of one of the devices attached
 *                          to the system at the time.  If the given name or GUID doesn't
 *                          match one of the connected devices, the default device will be
 *                          used instead.  This may be set to nullptr or an empty string
 *                          to use the system's default device.
 *  @returns no return value.
 *
 *  @remarks This sets the device that the audio manager will use for its output.  If the
 *           requested device cannot be used for any reason, the default output device will
 *           be used instead.  The device may change the final output format.  If a streamer
 *           is attached to the previous output, its stream will be closed before opening
 *           a new stream on the new device.  Even if the new device name matches the current
 *           device's name, the device will still be changed and any stream reset.
 *
 *  @note If multiple devices attached to the system have the same name, the one that is
 *        chosen may be undefined.  This can be a common issue with certain devices showing
 *        up in the system as simply "Speakers".  Using the device's GUID instead will allow
 *        a specific device to be used instead, even its name exactly matches that of another
 *        device.
 */
OMNI_USD_API void setDevice(AudioManager* mgr, const char* deviceName);

/** creates a new capture streamer.
 *
 *  @param[in] mgr  the audio manager to create the new streamer on.  This may not be nullptr.
 *  @returns the handle to a new capture streamer if it is successfully created.  When this
 *           handle is no longer needed, it must be destroyed with destroyCaptureStreamer().
 *  @returns @ref kInvalidStreamerId if the new capture streamer could not be created.
 */
OMNI_USD_API StreamerId createCaptureStreamer(AudioManager* mgr);

/** destroys a capture streamer.
 *
 *  @param[in] mgr  the audio manager to destroy the streamer for.  This may not be nullptr.
 *  @param[in] id   the streamer to be destroyed.  If this streamer is currently running a
 *                  capture, it will be stopped first.  Note that currently stopping one
 *                  streamer will stop all installed streamers.  All but the removed one
 *                  will be restarted afterward.  This will have the side effect of
 *                  overwriting each other streamer's file though.  This can be avoided
 *                  by stopping all streamers simultaneously first with stopCaptures().
 *  @returns no return value.
 */
OMNI_USD_API void destroyCaptureStreamer(AudioManager* mgr, StreamerId id);

/** sets the filename that a capture streamer will write to.
 *
 *  @param[in] mgr      the audio manager that owns the streamer @p id.  This may not be nullptr.
 *  @param[in] id       the streamer to set the filename for.  This handle will have been
 *                      returned from a previous call to createCaptureStreamer().  This may
 *                      not be @ref kInvalidStreamerId.
 *  @param[in] filename the name and path of the file to write the streamer's data to once
 *                      its capture is started.  If the filename is set here, a nullptr
 *                      filename may be passed into startCapture().
 *  @returns `true` if the given filename is valid and writable.
 *  @returns `false` if the streamer ID @p id is not valid.
 *  @returns `false` if the given filename is not writable.
 *
 *  @note A streamer can have one of: a filename, an interface or an event stream.
 *        Attaching this filename will remove the interface set by @ref setCaptureInterface()
 *        or the event stream set by @ref createEventStreamForCapture().
 *        Calling either of @ref setCaptureInterface() or @ref createEventStreamForCapture()
 *        will remove the attached filename.
 *
 */
OMNI_USD_API bool setCaptureFilename(AudioManager* mgr, StreamerId id, const char* filename);

/** Sets the streamer interface that data will be streamed to.
 *  @param[in] mgr      The audio manager that owns the streamer @p id.  This may not be nullptr.
 *  @param[in] id       The streamer to set the callbacks for.  This handle will have been
 *                      returned from a previous call to createCaptureStreamer().  This may
 *                      not be @ref kInvalidStreamerId.
 *  @param[in] streamer The interface that data will be sent to.
 *                      This may not be nullptr.
 *                      The lifetime of this object is managed by the caller.
 *                      This object must remain valid until destroyCaptureStreamer() is called.
 *  @returns `true` if the operation succeeded.
 *  @returns `false` if an error occurred.
 *
 *  @note A streamer can have one of: a filename, an interface or an event stream.
 *        Attaching this interface will remove the filename set by @ref setCaptureFilename()
 *        or the event stream set by @ref createEventStreamForCapture().
 *        Calling either of @ref setCaptureFilename() or @ref createEventStreamForCapture()
 *        will remove the attached interface.
 */
OMNI_USD_API bool setCaptureInterface(AudioManager* mgr, StreamerId id, Streamer* streamer);

/** Creates an event stream that the capture streamer will send data to.
 *  @param[in] mgr      The audio manager that owns the streamer @p id.  This may not be nullptr.
 *  @param[in] id       The streamer to set the callbacks for.  This handle will have been
 *                      returned from a previous call to createCaptureStreamer().  This may
 *                      not be @ref kInvalidStreamerId.
 *
 *  @returns The newly created event stream that's attached to streamer @p id.
 *           This event streamer is a @ref carb::audio::EventStreamer, so you can
 *           use @ref carb::audio::EventListener or another interoperable
 *           implementation to subscribe to this event stream.
 *           `IEventStreamPtr` objects are RAII ref counted, so you discard the
 *           object or call `release()` on it when you're done with it.
 *           If another streamer output is set with @ref setCaptureFilename() or
 *           @ref setCaptureInterface() after this, the returned object will
 *           still be valid but events will no longer be pushed to it.
 *
 *  @note A streamer can have one of: a filename, an interface or an event stream.
 *        Creating this event stream will remove the filename set by @ref setCaptureFilename()
 *        or the interface set by @ref setCaptureInterface().
 *        Calling either of @ref setCaptureFilename() or @ref setCaptureInterface()
 *        will disconnect the returned event stream.
 */
OMNI_USD_API carb::events::IEventStreamPtr createEventStreamForCapture(AudioManager* mgr, StreamerId id);

/** starts the capture on a single streamer.
 *
 *  @param[in] mgr      the audio manager that owns the streamer @p id.  This may not be nullptr.
 *  @param[in] id       the handle of the streamer to start.  This handle will have been
 *                      returned from a previous call to createCaptureStreamer().  This
 *                      may not be @ref kInvalidStreamerId.
 *  @param[in] filename the name and path of the filename to write the streamer's data to
 *                      once its capture is started.  If a filename was set with a previous
 *                      call to setCaptureFilename() on the same streamer, this may be
 *                      nullptr to use that filename.  If a non-nullptr and non-empty
 *                      filename is given here, it will always override any filename
 *                      previously set on the streamer.
 *                      Set this to `nullptr` if you're using a capture callback.
 *  @returns true if the streamer is successfully started.  Note that starting a streamer
 *           currently has the side effect of stopping and restarting all other streamers
 *           that are currently running a capture.  This will result in each streamer's
 *           output file being overwritten.  If multiple streamers need to be started
 *           simultaneously, startCaptures() should be used instead.
 *  @returns false if the streamer could not be started.
 */
OMNI_USD_API bool startCapture(AudioManager* mgr, StreamerId id, const char* filename = nullptr);

/** starts multiple streamers simultaneously.
 *
 *  @param[in] mgr      the audio manager that owns the streamer handles in @p ids.  This
 *                      may not be nullptr.
 *  @param[in] ids      the table of streamers to start a capture on.  Any entries that
 *                      are set to @ref kInvalidStreamerId in this table will be ignored.
 *                      Each valid entry must have had its filename set with
 *                      setCaptureFilename() first otherwise it will be skipped.  Any
 *                      streamer that is already running a capture will be skipped, but
 *                      a side effect of this operation will be that its stream will be
 *                      closed and reopened thereby overwriting its file.  this may not
 *                      be nullptr.
 *  @param[in] count    the total number of entries in the @p streamers table to start.
 *                      Since @ref kInvalidStreamerId entries are allowed in the table,
 *                      this count must include those invalid entries.
 *  @returns true if at least one streamer is successfully started.
 *  @returns false if no streamers could be started or all streamers were skipped for one
 *           of the reasons listed under @p streamers.
 *
 *  @remarks This attempts to start one or more streamers simultaneously.  If successful,
 *           all streamers are guaranteed to be started in sync with each other such that
 *           their first written audio frame matches.  If this method is used to start
 *           multiple streamers, the stopCaptures() function must also be used to stop
 *           those same streamers simultaneously.  If another streamer starts or stops
 *           independently, it will cause all streamers to be closed then reopened
 *           which will overwrite each of their files.
 */
OMNI_USD_API bool startCaptures(AudioManager* mgr, StreamerId* ids, size_t count);

/** stops the capture on a single streamer.
 *
 *  @param[in] mgr  the audio manager that owns the streamer @p id.  This may not be nullptr.
 *  @param[in] id   the handle to the streamer to stop.  This will have been returned from
 *                  a previous call to createCaptureStreamer().  If a capture is not running
 *                  on this streamer, it will be ignored.  This may not be
 *                  @ref kInvalidStreamerId.
 *  @returns true if the streamer is successfully stopped.
 *  @returns false if the streamer handle was invalid or a capture was not running on it.
 */
OMNI_USD_API bool stopCapture(AudioManager* mgr, StreamerId id);

/** stops the capture on multiple streamers simultaneously.
 *
 *  @param[in] mgr      the audio manager that owns the streamer handles in @p ids.  This
 *                      may not be nullptr.
 *  @param[in] ids      the table of streamers to stop the capture on.  Any
 *                      @ref kInvalidStreamerId entries will be ignored.  Each valid
 *                      entry must be currently running a capture otherwise it will be
 *                      skipped.  This may not be nullptr.
 *  @param[in] count    the total number of entries in the @p streamers table to stop.
 *                      Since @ref kInvalidStreamerId entries are allowed in the table,
 *                      this count must include those invalid entries.
 *  @returns true if at least one streamer is successfully stopped.
 *  @returns false if no streamers could be stopped.
 */
OMNI_USD_API bool stopCaptures(AudioManager* mgr, StreamerId* ids, size_t count);

/** Wait until the capture streamer has been disconnected.
 *  @param[in] mgr  The audio manager that owns the streamer handles in @p ids.  This
 *                  may not be nullptr.
 *  @param[in] id   The handle to the streamer to wait for.  This will have been returned from
 *                  a previous call to createCaptureStreamer().  If a capture is not running
 *                  on this streamer, it will be ignored.  This may not be
 *                  @ref kInvalidStreamerId.
 *  @param[in] timeoutMilliseconds The maximum number of milliseconds to wait for the streamer to close.
 *  @returns `true` if the capture streamer has disconnected.
 *  @returns `false` if the call timed out before the streamer could disconnect.
 *  @returns `false` if @p id uses an event stream; that system is asynchronous
 *           and may continue to send data after the streamer has disconnected.
 *           Unsubscribe from the event stream to ensure data callbacks will no
 *           longer be sent. You can call the `unsubscribe()` method on the
 *           `ISubscriptionPtr` object to unsubscribe from the stream.
 *  @remarks Because stopCapture() does not stop the audio system or otherwise block
 *           to ensure that the streamer is disconnected, you must call waitForCapture()
 *           to verify that a capture streamer has actually finished.
 *           This is mainly useful if you need to verify that a file written by
 *           a streamer has finished being written.
 *           For a callback streamer, waitForCapture() will begin returning true
 *           immediately before close() is called.
 */
OMNI_USD_API bool waitForCapture(AudioManager* mgr, StreamerId id, size_t timeoutMilliseconds);

/** retrieve the event stream for metadata changes.
 *  @param[in] mgr   The stage audio manager instance that this function acts upon.
 *                   This must not be nullptr.
 *  @returns An event stream which is pushed when metadata is changed.
 *  @returns nullptr if the event stream could not be created for some reason.
 *
 *  @remarks This generates events of type @ref kEventMetadataChange when the
 *           audio metadata in the USD scene changes.
 */
OMNI_USD_API carb::events::IEventStream* getMetadataChangeStream(AudioManager* mgr);

/** Draw the waveform for the sound asset of an audio prim.
 *  @param[in] mgr The stage audio manager instance that this function acts upon.
 *                 This must not be nullptr.
 *  @param[in] primPath The path to sound prim which has the sound asset that will
 *                      be rendered.
 *                      Note that the `mediaOffsetStart` and `mediaOffsetEnd`
 *                      properties of the prim are used to choose the region of
 *                      the sound that is drawn.
 *                      The asset for this prim must have been loaded or the
 *                      call will fail.
 *  @param[in] image The description of how the image should be rendered.
 *                   If this descriptor is invalid, the call will fail.
 *
 *  @returns `true` if the image was successfully drawn.
 *  @returns `false` if @p primPath isn't a valid prim.
 *  @returns `false` if the sound asset has not been loaded yet.
 *  @returns `false` if @p image was invalid.
 *
 *  @remarks This will draw an RGBA image of the waveform of the sound asset
 *           in use by a `OmniSound` prim.
 */
OMNI_USD_API bool drawWaveform(AudioManager* mgr, const char* primPath, AudioImageDesc *image);

/** @} */

}
}
}
