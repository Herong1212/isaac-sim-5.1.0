// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
//! @file
//! @brief Defines an interface to provide a simple audio player interface.
#pragma once

#include <carb/Interface.h>
#include <carb/Types.h>

namespace omni
{
namespace audio
{

/** Handle for a created audio player object.  This will be `nullptr` to indicate an invalid
 *  audio player object.
 */
struct AudioPlayer;

/** Prototype of a callback function to signal that a sound data log operation completed.
 *
 *  @param[in] success  Set to `true` if the load operation was successful.  Set to `false`
 *                      otherwise.
 *  @param[in] context  The original caller specified context value that was provided when
 *                      this callback was registered in either IAudioPlayer::playSound() or
 *                      IAudioPlayer::loadSound() families of functions.
 *  @returns No return value.
 */
using OnLoadedCallback = void (*)(bool success, void* context);

/** Prototype of a callback function to signal that a sound completed its playback.
 *
 *  @param[in] context  The original caller specified context value that was provided when
 *                      this callback was registered in either IAudioPlayer::playSound()
 *                      family of functions.
 *  @returns No return value.
 */
using OnEndedCallback = void (*)(void* context);


/** Base type for flags that can be provided to IAudioPlayer::loadSoundInMemory() or
 *  IAudioPlayer::playSoundInMemory().
 *  @{
 */
using AudioPlayerFlags = uint32_t;

/** Flag to indicate that the data blob being passed in only contains the raw PCM data and
 *  no header or format information.  When this flag is used, the frame rate, channel count,
 *  and sample data format must also be specified when passing the blob to either
 *  IAudioPlayer::loadSoundInMemory() or IAudioPlayer::playSoundInMemory().
 */
constexpr AudioPlayerFlags fPlayerFlagRawData = 0x01;

/** Flag to indicate that the data blob should be reloaded even if it is already cached in
 *  the audio player object.
 */
constexpr AudioPlayerFlags fPlayerFlagForceReload = 0x02;
/** @} */


/** The supported PCM formats for loading or playing raw PCM data through the
 *  IAudioPlayer::loadSoundInMemory() or IAudioPlayer::playSoundInMemory() functions.
 */
enum class RawPcmFormat
{
    ePcm8, ///< unsigned 8-bits per sample integer PCM data.
    ePcm16, ///< signed 16-bits per sample integer PCM data.
    ePcm32, ///< signed 32-bits per sample integer PCM data.
    ePcmFloat, ///< 32-bits per sample floating point PCM data.
};


/** The descriptor for IAudioPlayer::drawWaveform(). */
struct DrawWaveformDesc
{
    /** The name for the output image file.
     * This path supports the standard path aliases (e.g. "${resources}")
     * The path must point to an existing directory on disk.
     * This must be nullptr to store the image in @p outputBuffer.
     */
    const char* filename;

    /** The buffer to store the raw RGBA8888 in.
     *  @p filename must be nullptr for this to be used.
     *  This needs to be at least @p width * @p height * 4 bytes long.
     */
    uint8_t* outputBuffer;

    /** The width of the output image, in pixels. */
    size_t width;

    /** The height of the output image, in pixels. */
    size_t height;

    /**  The foreground color in normalized RGBA color. */
    carb::Float4 fgColor;

    /** The background color in normalized RGBA color. */
    carb::Float4 bgColor;
};


/** Descriptor of a blob of audio data in memory.  This data can either be a full supported sound
 *  file in memory, or just simple raw PCM data.  If raw PCM data is provided, the information
 *  about the data format must also be provided.
 */
struct AudioDataInMemory
{
    /** The name to be used to cache the file data in the audio player.  This may be `nullptr` or
     *  an empty string to indicate that it shouldn't be cached.  If it is not cached, the sound
     *  is only expected to be played once.  If it is played again, it will be reloaded instead of
     *  pulling a cached version that was previously loaded or played.
     */
    const char* name = nullptr;

    /** The buffer of sound data to be loaded.  This is interpreted according to the flags passed
     *  to either IAudioPlayer::loadSoundInMemory() or IAudioPlayer::playSoundInMemory().  If the
     *  flags indicate that raw data is passed in, the frame rate, channel count, and data format
     *  values will also be required.  This may not be `nullptr`.
     */
    const void* buffer;

    /** The size of @ref buffer in bytes.  This may not be 0. */
    size_t byteCount;

    /** The frame rate to play the audio data back at.  This must be a non-zero value if raw PCM
     *  data is being provided.  This is measured in Hertz.  Typical values for this are 44100Hz,
     *  or 48000Hz.  Any value in the range from 1000Hz to 200000Hz is generally accepted.  Though
     *  note that if this value is not correct for the given sound data, it may play back either
     *  to quickly or too slowly.  The pitch of the sound will also be affected accordingly.  This
     *  value will be ignored if the blob in @ref buffer already contains format information.
     */
    size_t frameRate = 0;

    /** The number of channels in each frame of data in the sound.  This must be a non-zero value
     *  if raw PCM data is being provided.  If this is incorrect for the given data, the sound will
     *  play incorrectly.  This value will be ignored if the blob in @ref buffer already contains
     *  format information.
     */
    size_t channels = 0;

    /** The format of the PCM data.  This must be a valid value if raw PCM data is being provided.
     *  This must be well known by the caller otherwise the audio data will load incorrectly and
     *  undefined output would be likely to result (it won't be generally problematic except to
     *  the ears of listeners).  This value will be ignored if the bob in @ref buffer already
     *  contains format information.
     */
    RawPcmFormat format = RawPcmFormat::ePcm16;
};


/** Simple interface to be able to play audio assets.
 *  All of the calls to this interface are internally serialized by a mutex.
 *  This provides an interface for an audio player that has one voice and
 *  allows individual assets to be played.
 *  Multiple audio players can be opened per-process but they all share the same
 *  IAudioPlayer backend which limits the number of simultaneously playing audio
 *  players to 4.
 */
struct IAudioPlayer
{
    CARB_PLUGIN_INTERFACE("omni::audio::IAudioPlayer", 0, 3);

    /** Create an audio player instance.
     *  @returns A new audio player if creation succeeded.
     *  @returns nullptr if creation failed.
     *
     *  @remarks This creates an audio system with 1 voice that can play sound assets.
     */
    AudioPlayer*(CARB_ABI* createAudioPlayer)();

    /** Destroy an audio player instance.
     *  @param[in] player The player to destroy.
     *
     *  @remarks This will stop any audio playing, release all assets and free
     *           the memory of @p player.
     */
    void(CARB_ABI* destroyAudioPlayer)(AudioPlayer* player);

    /** Play a sound asset.
     *  @param[in] player      The player to play this sound on.
     *  @param[in] path        The path to the sound asset to play.
     *                         This must be an absolute file path to a sound asset.
     *  @param[in] onLoaded    A callback to execute once the asset has
     *                         loaded and is about to play.
     *                         This may be used for something like turning
     *                         off a spinner icon to indicate that the
     *                         asset has loaded.
     *                         The first parameter of this callback indicates
     *                         whether the load request succeeded.
     *                         The second parameter is @p context.
     *                         This may be nullptr if the callback is not needed.
     *  @param[in] onEnded     A callback to execute once the asset has finished
     *                         playing or has been stopped.
     *                         The parameter passed is @p context.
     *                         This may be nullptr if the callback is not needed.
     *  @param[in] context     The parameter to pass into @p onLoaded and @p onEnded.
     *  @param[in] startTime   The time offset into the sound to start playing it
     *                         at. This is measured in seconds.
     *
     *  @remarks This will spawn a task to play this sound asset once it has loaded.
     *           This is intended to be used for auditioning sounds to a user
     *           from something like the content window, to allow them to hear
     *           a sound before they use it in their scene.
     *
     *  @note If another sound is currently playing, it will be stopped before
     *        playing this sound.
     *
     *  @note The callbacks are called within an internal static recursive
     *        mutex, so the callbacks must be careful to avoid deadlock if they
     *        need to acquire another lock, such as the python GIL.
     *
     *  @note Playing the sound will fail if too many other audio players are
     *        playing simultaneously.
     */
    void(CARB_ABI* playSound)(AudioPlayer* player,
                              const char* path,
                              OnLoadedCallback onLoaded,
                              OnEndedCallback onEnded,
                              void* context,
                              double startTime);

    /** Load a sound asset for future playback
     *  @param[in] player      The player to play this sound on.
     *  @param[in] path        The path to the sound asset to play.
     *                         This must be an absolute file path to a sound asset.
     *  @param[in] onLoaded    A callback to execute once the asset has
     *                         loaded and is about to play.
     *                         This may be used for something like turning
     *                         off a spinner icon to indicate that the
     *                         asset has loaded.
     *                         The first parameter of this callback indicates
     *                         whether the load request succeeded.
     *                         The second parameter is @p context.
     *                         This may be nullptr if the callback is not needed.
     *  @param[in] context     The parameter to pass into @p onLoaded and @p onEnded.
     *
     *  @remarks This will fetch an asset so that the next call to playSound()
     *           can begin playing the sound immediately.
     *           This will also stop the currently playing sound, if any.
     *           This function will also cause getSoundLength() to begin
     *           returning the length of this sound.
     */
    void(CARB_ABI* loadSound)(AudioPlayer* player, const char* path, OnLoadedCallback onLoaded, void* context);

    /** Stop playing the current sound, if any.
     *  @param[in] player The player to play this sound on.
     */
    void(CARB_ABI* stopSound)(AudioPlayer* player);

    /** Pause playback of the current sound, if any.
     *  @param[in] player The player to play this sound on.
     */
    void(CARB_ABI* pauseSound)(AudioPlayer* player);

    /** Unpause playback of the current sound, if any.
     *  @param[in] player The player to play this sound on.
     */
    void(CARB_ABI* unpauseSound)(AudioPlayer* player);

    /** Get the length of the currently playing sound.
     *  @param[in] player The player to play this sound on.
     *  @returns The length of the currently playing sound in seconds.
     *  @returns 0.0 if there is no playing sound.
     */
    double(CARB_ABI* getSoundLength)(AudioPlayer* player);

    /** Get the play cursor position in the currently playing sound.
     *  @param[in] player The player to play this sound on.
     *  @returns The play cursor position in the currently playing sound in seconds.
     *  @returns 0.0 if there is no playing sound.
     */
    double(CARB_ABI* getPlayCursor)(AudioPlayer* player);

    /** Set the cursor in the sound.
     *  @param[in] player      The player to use to set the cursor in the sound.
     *  @param[in] onLoaded    A callback to execute once the asset has
     *                         loaded and is about to play.
     *                         This may be used for something like turning
     *                         off a spinner icon to indicate that the
     *                         asset has loaded.
     *                         The first parameter of this callback indicates
     *                         whether the load request succeeded.
     *                         The second parameter is @p context.
     *                         This may be nullptr if the callback is not needed.
     *  @param[in] onEnded     A callback to execute once the asset has finished
     *                         playing or has been stopped.
     *                         The parameter passed is @p context.
     *                         This may be nullptr if the callback is not needed.
     *  @param[in] context     The parameter to pass into @p onLoaded and @p onEnded.
     *  @param[in] startTime   The time offset to set the cursor to. This is measured in seconds.
     *
     *  @note The previous onEnded() callback that was passed to playSound() will
     *        be called after @p onLoaded() is called.
     */
    void(CARB_ABI* setPlayCursor)(AudioPlayer* player,
                                  OnLoadedCallback onLoaded,
                                  OnEndedCallback onEnded,
                                  void* context,
                                  double startTime);

    /** Render the waveform to an image to a file.
     *  @param[in] player The player whose waveform image will be rendered.
     *  @param[in] desc   The descriptor for the waveform to draw.
     *  @return true if the operation was successful.
     *  @returns false if the file could not be generated.
     *
     *  @note The functionality of writing to a file is a temporary workaround.
     *        This will eventually be changed to output a memory buffer.
     */
    bool(CARB_ABI* drawWaveform)(AudioPlayer* player, const DrawWaveformDesc* desc);

    /** Play a sound asset from data in memory.
     *
     *  @param[in] player       The player to play this sound on.
     *  @param[in] data         The descriptor of the data blob and its required format
     *                          information.  This must include the format information for the
     *                          sound if the @ref fPlayerFlagRawData flag is given in @p flags.
     *                          This may not be `nullptr`.
     *  @param[in] onLoaded     A callback to execute once the asset has loaded and is about to
     *                          play.  This may be used for something like turning off a spinner
     *                          icon to indicate that the asset has loaded.  The first parameter
     *                          of this callback indicates whether the load request succeeded.
     *                          The second parameter is @p context.  This may be `nullptr` if the
     *                          callback is not needed.
     *  @param[in] onEnded      A callback to execute once the asset has finished playing or has
     *                          been stopped.  The parameter passed is @p context.  This may be
     *                          `nullptr` if the callback is not needed.
     *  @param[in] context      The parameter to pass into @p onLoaded and @p onEnded.
     *  @param[in] startTime    The time offset into the sound to start playing it at.  This is
     *                          measured in seconds.
     *  @param[in] flags        Flags to control how the sound data is loaded and cached.  If the
     *                          data blob does not contain format information and is just raw PCM
     *                          sample data, the @ref fPlayerFlagRawData flag must be specified
     *                          and the @a frameRate, @a channels, and @a format values in @p data
     *                          must also be given.  Without these, the sound data cannot be
     *                          properly loaded.
     *  @returns No return value.
     *
     *  @remarks The sound asset will start playing asynchronously when the asset has loaded.
     *           The asset is given as a data blob in memory.  The data may either be a full
     *           file loaded into memory or just raw PCM data.  If raw PCM data is given,
     *           additional parameters must be used to specify the sample type, channel count,
     *           and frame rate so that the data can be successfully decoded.
     *
     *  @note If another sound is currently playing, it will be stopped before
     *        playing this sound.
     *
     *  @note The callbacks are called within an internal static recursive
     *        mutex, so the callbacks must be careful to avoid deadlock if they
     *        need to acquire another lock, such as the python GIL.
     *
     *  @note Playing the sound will fail if too many other audio players are
     *        playing simultaneously.
     */
    void(CARB_ABI* playSoundInMemory)(AudioPlayer* player,
                                      const AudioDataInMemory* data,
                                      OnLoadedCallback onLoaded,
                                      OnEndedCallback onEnded,
                                      void* context,
                                      double startTime,
                                      AudioPlayerFlags flags);

    /** Play a sound asset from data in memory.
     *
     *  @param[in] player       The player to play this sound on.
     *  @param[in] data         The descriptor of the data blob and its required format
     *                          information.  This must include the format information for the
     *                          sound if the @ref fPlayerFlagRawData flag is given in @p flags.
     *                          This may not be `nullptr`.
     *  @param[in] onLoaded     A callback to execute once the asset has loaded and is about to
     *                          play.  This may be used for something like turning off a spinner
     *                          icon to indicate that the asset has loaded.  The first parameter
     *                          of this callback indicates whether the load request succeeded.
     *                          The second parameter is @p context.  This may be `nullptr` if the
     *                          callback is not needed.
     *  @param[in] context      The parameter to pass into @p onLoaded and @p onEnded.
     *  @param[in] flags        Flags to control how the sound data is loaded and cached.  If the
     *                          data blob does not contain format information and is just raw PCM
     *                          sample data, the @ref fPlayerFlagRawData flag must be specified
     *                          and the @a frameRate, @a channels, and @a format values in @p data
     *                          must also be given.  Without these, the sound data cannot be
     *                          properly loaded.
     *  @returns No return value.
     *
     *  @remarks This will fetch an asset in memory so that the next call to playSound() can begin
     *           playing the sound immediately.  In order for this to be useful, the @a name value
     *           in @p data must be a non-empty string so that the loaded sound is cached.  If no
     *           name is given, the operation will just fail immediately.  This will also stop the
     *           currently playing sound, if any.  This function will also cause getSoundLength()
     *           to begin returning the length of this sound.
     */
    void(CARB_ABI* loadSoundInMemory)(AudioPlayer* player,
                                      const AudioDataInMemory* data,
                                      OnLoadedCallback onLoaded,
                                      void* context,
                                      AudioPlayerFlags flags);
};

}
}
