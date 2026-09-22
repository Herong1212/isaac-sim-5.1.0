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
#include <carb/audio/IAudioCapture.h>

namespace omni
{
namespace audio
{

/** The audio recorder instance.
 *  This is created to reserve a device that can record audio.
 */
struct AudioRecorder;

/** A callback to read data from the audio device.
 *  @param[in]    data    The audio data that was recorded.
 *  @param[in]    frames  The number of frames of audio that are available in @p data.
 *  @param[inout] context A user-defined context that gets passed through to the callback.
 */
using ReadCallback = void (*)(const void* data, size_t frames, void* context);

/** The descriptor used to create a recording session. */
struct AudioRecordDesc
{
    /** Flags for future expansion.
     *  This must be set to 0.
     */
    uint32_t flags = 0;

    /** The filename to write the output audio to.
     *  This can be nullptr to use @p callback to receive audio instead.
     */
    const char* filename = nullptr;

    /** The read callback to receive data with.
     *  This will be called periodically when data is available.
     *  This can be nullptr if @ref filename is non-null.
     *  If this is set to non-null and @ref filename is non-null, this callback
     *  will be called after the data has been written to the file (the data may
     *  not have been flushed at this point though).
     *  Note that if this callback takes too long, it can cause a recording overrun.
     *  This callback occurs asynchronously under the recursive mutex of the
     *  @ref AudioRecorder; if a lock is acquired in @ref callback, it is
     *  important to ensure this does not result in the two locks being
     *  acquired in different orders, which could potentially cause deadlock.
     */
    ReadCallback callback = nullptr;

    /** A parameter that gets passed into the callback.
     *  This is ignored if @ref callback is nullptr.
     */
    void* callbackContext = nullptr;

    /** The frame rate to capture audio at.
     *  This may be set to 0 to use the default rate for the device.
     *  You can query the device's rate with IAudioRecorder::getDeviceCaps().
     *  If this is not a frame rate supported by the device, a resampler will be
     *  introduced, which adds a small performance cost.
     */
    size_t frameRate = 0;

    /** The number of channels that the audio is being captured at.
     *  This may be set to 0 to use the default channel count for the device.
     *  You can query the device's channel count with IAudioRecorder::getDeviceCaps().
     *  If this is different than the device's channel count an up/downmixing
     *  operation may have to be introduced, which add a small performance cost.
     *  The channel mixing matrices chosen are chosen based on the set of
     *  default speaker modes used by carb.audio for a given channel count;
     *  see carb::audio::getSpeakerModeForCount() for this list of defaults.
     */
    size_t channels = 0;

    /** The format that data will be produced by the capture device.
     *  This may be @ref carb::audio::SampleFormat::eDefault to use the device's
     *  preferred format.
     *  You can query the device's rate with IAudioRecorder::getDeviceCaps().
     *  This must be set to a PCM format if @ref callback is non-null.
     *  If this is not a format supported by the device, a format conversion
     *  will be introduced which adds a very small performance cost.
     */
    carb::audio::SampleFormat sampleFormat = carb::audio::SampleFormat::eDefault;

    /** The format that gets written to the file.
     *  This is only used if @ref filename is non-null.
     *  This can be any valid sample format.
     *  If this is set to @ref carb::audio::SampleFormat::eDefault, @ref sampleFormat
     *  is used.
     */
    carb::audio::SampleFormat outputFormat = carb::audio::SampleFormat::eDefault;

    /** The length of the recording buffer.
     *  This setting, combined with @ref period will allow you to choose the
     *  recording latency, as well as the tolerance for variance in recording
     *  latency.
     *  It is important to set this to a large enough value that fluctuation
     *  in system timing can be handled without the audio buffer filling up.
     *  The length can be set to 0 to use the device's default buffer length.
     */
    size_t bufferLength = 0;

    /** The time between read callbacks.
     *  This value can be used to reduce latency without reducing the ability to
     *  handle fluctuations in timing; for example, setting @ref bufferLength to
     *  64ms and setting @ref period to 8ms will result in roughly 8ms latency
     *  but the ability to tolerate up to 56ms of lag.
     *  The default value is @ref bufferLength / 2.
     *  This will be clamped to the default period if it exceeds the default period.
     *  Two callbacks may be sent for a given period to handle the end of the
     *  ring buffer.
     *  This may send more data than expected for a given period if the system's
     *  timing fluctuates.
     */
    size_t period = 0;

    /** Describes how @ref bufferLength and @ref period should be interpreted.
     *  This value is ignored if @ref bufferLength and @ref period are 0.  Note
     *  that the buffer size will always be rounded up to the next frame
     *  boundary even if the size is specified in bytes.
     */
    carb::audio::UnitType lengthType = carb::audio::UnitType::eFrames;
};

/** Simple interface to be able to record audio. */
struct IAudioRecorder
{
    CARB_PLUGIN_INTERFACE("omni::audio::IAudioRecorder", 0, 1);

    /** Create an audio recorder instance.
     *  @returns A new audio recorder if creation succeeded.
     *           This must be passed to destroyAudioRecorder() when you are
     *           finished with the instance.
     *  @returns nullptr if creation failed.
     *
     *  @remarks This creates an audio system that can record audio to a file or to a callback.
     *
     *  @note Each call to createAudioRecorder() opens a connection to the audio
     *        recording device set in the preferences (@ref kSettingCaptureDeviceName).
     *        It is not recommended to open a large number of these connections.
     */
    AudioRecorder*(CARB_ABI* createAudioRecorder)();

    /** Destroy an audio recorder instance.
     *  @param[inout] recorder The recorder to destroy.
     *
     *  @remarks This function frees the memory allocated to the @ref AudioRecorder.
     *           This will stop the recorder if it was recoding audio when this is called.
     */
    void(CARB_ABI* destroyAudioRecorder)(AudioRecorder* recorder);

    /** Being recording audio.
     *  @param[inout] recorder The audio recorder to begin recording with.
     *                         This should not be nullptr.
     *  @param[in]    desc     The descriptor for how audio should be recorded.
     *                         This should not be nullptr.
     *
     *  @returns true If recording has started.
     *  @returns false if @p recorder or @p desc are nullptr.
     *  @returns false if another error occurred.
     */
    bool(CARB_ABI* beginRecording)(AudioRecorder* recorder, const AudioRecordDesc* desc);

    /** Stop recording audio.
     *  @param[inout] recorder The audio recorder to stop recording on.
     *                         This should not be nullptr.
     *  @param[in]    flush    Set this to true to flush the rest of the data
     *                         that is currently in the capture device's buffer.
     *                         Set this to false to discard any remaining queued
     *                         data.
     *
     *  @remarks This should be called when beginRecording() has been previously
     *           called and you want to stop recording.
     */
    void(CARB_ABI* stopRecording)(AudioRecorder* recorder, bool flush);

    /** Retrieves the sound format for the recorder.
     *  @param[in]  recorder The recorder to retrieve the device information for.
     *                       This should not be nullptr.
     *  @param[out] format   Receives the format.
     *                       This should not be nullptr.
     *                       If beginRecording() was called, this will return
     *                       the current format that is being used for recording.
     *                       If beginRecording() has not been called yet, this
     *                       will return the default format specified by the device.
     *  @returns true if the device info was successfully retrieved.
     *  @returns false if either parameter was nullptr.
     *  @returns false if the call fails for any other reason.
     */
    bool(CARB_ABI* getFormat)(AudioRecorder* recorder, carb::audio::SoundFormat* format);
};

}
}
