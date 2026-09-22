// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
//! @file
//! @brief Provides an interface that allows the connected audio devices to be enumerated.
#pragma once

#include <carb/Interface.h>
#include <carb/extras/Guid.h>


namespace omni
{
namespace audio
{

/** The direction to collect device information for.  This is passed to most functions in the
 *  IAudioDeviceEnum interface to specify which types of devices are currently interesting.
 */
enum class Direction
{
    ePlayback, ///< Enumerate audio playback devices only.
    eCapture, ///< Enumerate audio capture devices only.
};

/** Names for the type of sample that an audio device can use. */
enum class SampleType
{
    eUnknown, ///< Could not determine the sample type or an invalid device index was given.
    ePcmSignedInteger, ///< Signed integer PCM samples.  This is usually used for 16-bit an up.
    ePcmUnsignedInteger, ///< Unsigned integer PCM samples.  This is often used for 8-bit samples.
    ePcmFloat, ///< Single precision floating point PCM samples.
    eCompressed, ///< A compressed sample format such as ADPCM, MP3, Vorbis, etc.
};

/** An interface to provide simple audio device enumeration functionality.  This is able to
 *  enumerate all audio devices attached to the system at any given point and collect the
 *  information for each device.  This is only intended to collect the device information
 *  needed to display to the user for device selection purposes.  If a device is to be
 *  chosen based on certain needs (ie: channel count, frame rate, etc), it should be done
 *  directly through the audio playback or capture context during creation.  This is able
 *  to collect information for both playback and capture devices.
 *
 *  Note that audio devices in the system are generally volatile - they can be added or
 *  removed at any time with no control from this interface.  Because of this, it is
 *  highly suggested that device information not be cached, but instead queried each time
 *  it needs to be refreshed.
 *
 *  Currently this interface does not expose a device change notifier.  This is only
 *  available from the `carb::audio::IAudioDevice` interface for the moment.  A future
 *  version of this interface may expose an event stream for device change notifications.
 *  The caller may then use those notifications to decide when to refresh the cached
 *  device information in the UI for example.
 */
struct IAudioDeviceEnum
{
    /** @private */
    CARB_PLUGIN_INTERFACE("omni::audio::IAudioDeviceEnum", 0, 1);

    /** Retrieves the total number of devices attached to the system of a requested type.
     *
     *  @param[in] dir  The audio direction to get the device count for.
     *  @returns The total number of connected audio devices of the requested type.
     *  @returns 0 if no audio devices are connected to the system.
     */
    size_t(CARB_ABI* getDeviceCount)(Direction dir);

    /** Retrieves a descriptive string for a requested audio device.
     *
     *  @param[in]  dir         The audio direction to get the description string for.
     *  @param[in]  index       The index of the device to retrieve the description for.  This
     *                          should be between 0 and one less than the most recent return
     *                          value of getDeviceCount().
     *  @param[out] desc        Receives the description string for the requested device if
     *                          it is still present in the system and its information can be
     *                          retrieved.  This may not be nullptr.
     *  @param[in]  maxLength   The maximum number of characters including the null terminator
     *                          that can be stored in the output buffer.
     *  @returns `true` if the device description was successfully created.
     *  @returns `false` if the device index was out of range.
     *
     *  @remarks This retrieves a descriptive string for the requested device.  This string is
     *           suitable for display to a user in a menu or selection list.
     */
    bool(CARB_ABI* getDeviceDescription)(Direction dir, size_t index, char* desc, size_t maxLength);

    /** Retrieves the friendly name of a requested device.
     *
     *  @param[in]  dir         The audio direction to get the device name for.
     *  @param[in]  index       The index of the device to retrieve the name for.  This
     *                          should be between 0 and one less than the most recent return
     *                          value of getDeviceCount().
     *  @param[out] name        Receives the name of the requested device if it could be
     *                          retrieved.  This may not be nullptr.
     *  @param[in]  maxLength   The maximum number of characters including the null terminator
     *                          that can be stored in the output buffer.
     *  @returns `true` if the device name was successfully retrieved.
     *  @returns `false` if the device index was out of range.
     */
    bool(CARB_ABI* getDeviceName)(Direction dir, size_t index, char* name, size_t maxLength);

    /** Retrieves the GUID of a requested device.
     *
     *  @param[in]  dir         The audio direction to get the device GUID for.
     *  @param[in]  index       The index of the device to retrieve the GUID for.  This
     *                          should be between 0 and one less than the most recent return
     *                          value of getDeviceCount().
     *  @param[out] guid        Receives the GUID of the requested device if it could be
     *                          retrieved.  This may not be nullptr.
     *  @returns `true` if the device GUID was successfully retrieved.
     *  @returns `false` if the device index was out of range.
     */
    bool(CARB_ABI* getDeviceGuid)(Direction dir, size_t index, carb::extras::Guid* guid);

    /** Retrieves the unique identifier for the requested device.
     *
     *  @param[in] dir          The audio direction to get the device name for.
     *  @param[in] index        The index of the device to retrieve the identifier for.  This
     *                          should be between 0 and one less than the most recent return
     *                          value of getDeviceCount().
     *  @param[out] id          Receives the identifier of the requested device if it could be
     *                          retrieved.  This may not be nullptr.
     *  @param[in] maxLength    The maximum number of characters including the null terminator
     *                          that can be stored in the output buffer.
     *  @returns `true` if the device identifier was successfully retrieved.
     *  @returns `false` if the device index was out of range.
     */
    bool(CARB_ABI* getDeviceId)(Direction dir, size_t index, char* id, size_t maxLength);

    /** Retrieves the closest matching device index from an identifier.
     *
     *  @param[in] dir  The audio direction to get the device index for.
     *  @param[in] id   The identifier of the device to match to the current device list.
     *  @returns The index of the device that matches the given identifier if an exact match
     *           was found.  Note that the match may have been made either by the device's
     *           friendly name or by its unique identifier.  This should be an identifier
     *           returned from a previous call to getDeviceId() or getDeviceName().  Note
     *           that this identifier may be stored persistently to attempt access to the
     *           same device in a future launch.
     *  @returns 0 if no matching device was found and the system's default device was
     *           chosen instead.
     *
     *  @remarks This checks the current system device list to find a device that matches
     *           the given identifier.  The device identifiers returned from getDeviceId()
     *           contain both the device's friendly name and its unique identifier code.
     *           Matches will first check the unique identifier.  If no match is found,
     *           it will compare against the friendly name.  If the unique identifier portion
     *           is not present, a match by the friendly name will be attempted instead.  Note
     *           that the device's friendly name may not necessarily be unique, even among
     *           different removeable devices.  For example, multiple USB headsets may have
     *           their output sides appear to the system as just simply "Speakers".  If a
     *           persistent storage of the device identifier is needed, the name returned
     *           from getDeviceId() should be preferred over that of getDeviceName().
     */
    size_t(CARB_ABI* getDeviceIndexFromId)(Direction dir, const char* id);

    /** Retrieves the preferred frame rate of a requested device.
     *
     *  @param[in]  dir         The audio direction to get the preferred frame rate for.
     *  @param[in]  index       The index  of the device to retrieve the frame rate for.  This
     *                          should be between 0 and one less than the most recent return
     *                          value of getDeviceCount().
     *  @returns The preferred frame rate of the requested device if it could be retrieved.
     *  @returns 0 if the device index was out of range.
     *
     *  @remarks This retrieves the preferred frame rate of a requested device.  The preferred
     *           frame rate is the rate at which the device natively wants to process audio data.
     *           Using the device at other frame rates may be possible but would require extra
     *           processing time.  Using a device at a different frame rate than its preferred
     *           one may also result in degraded quality depending on what the processing versus
     *           preferred frame rate is.
     *
     *  @note This function will open the audio device to test on some systems.
     *        The caller should ensure that isDirectHardwareBackend() returns
     *        false before calling this.
     *        Calling this on a 'direct hardware' backend could result in this call
     *        taking a substantial amount of time (e.g. 100ms) or failing unexpectedly.
     */
    size_t(CARB_ABI* getDeviceFrameRate)(Direction dir, size_t index);

    /** Retrieves the maximum channel count for a requested device.
     *
     *  @param[in]  dir         The audio direction to get the maximum channel count for.
     *  @param[in]  index       The index  of the device to retrieve the channel count for.
     *                          This should be between 0 and one less than the most recent
     *                          return value of getDeviceCount().
     *  @returns The maximum channel count of the requested device if it could be retrieved.
     *  @returns 0 if the device index was out of range.
     *
     *  @remarks This retrieves the maximum channel count for a requested device.  This count
     *           is the maximum number of channels that the device can natively handle without
     *           having to trim or reprocess the data.  Using a device with a different channel
     *           count than its maximum is allowed but will result in extra processing time to
     *           upmix or downmix channels in the stream.  Note that downmixing channel counts
     *           (ie: 7.1 to stereo) will often result in multiple channels being blended
     *           together and can result in an unexpected final signal in certain cases.
     *
     *  @note This function will open the audio device to test on some systems.
     *        The caller should ensure that isDirectHardwareBackend() returns
     *        false before calling this.
     *        Calling this on a 'direct hardware' backend could result in this call
     *        taking a substantial amount of time (e.g. 100ms) or failing unexpectedly.
     */
    size_t(CARB_ABI* getDeviceChannelCount)(Direction dir, size_t index);

    /** Retrieves the native sample size for a requested device.
     *
     *  @param[in]  dir         The audio direction to get the native sample size for.
     *  @param[in]  index       The index  of the device to retrieve the sample size for.
     *                          This should be between 0 and one less than the most recent
     *                          return value of getDeviceCount().
     *  @returns The native sample size in bits per sample of the requested device if it
     *           could be retrieved.
     *  @returns 0 if the device index was out of range.
     *
     *  @remarks This retrieves the bits per sample that a requested device prefers to process
     *           its data at.  It may be possible to use the device at a different sample size,
     *           but that would likely result in extra processing time.  Using a device at a
     *           different sample rate than its native could degrade the quality of the final
     *           signal.
     *
     *  @note This function will open the audio device to test on some systems.
     *        The caller should ensure that isDirectHardwareBackend() returns
     *        false before calling this.
     *        Calling this on a 'direct hardware' backend could result in this call
     *        taking a substantial amount of time (e.g. 100ms) or failing unexpectedly.
     */
    size_t(CARB_ABI* getDeviceSampleSize)(Direction dir, size_t index);

    /** Retrieves the native sample data type for a requested device.
     *
     *  @param[in]  dir         The audio direction to get the native sample data type for.
     *  @param[in]  index       The index  of the device to retrieve the sample data type for.
     *                          This should be between 0 and one less than the most recent
     *                          return value of getDeviceCount().
     *  @returns The native sample data type of the requested device if it could be retrieved.
     *  @returns @ref SampleType::eUnknown if the device index was out of range.
     *
     *  @remarks This retrieves the sample data type that a requested device prefers to process
     *           its data in.  It may be possible to use the device with a different data type,
     *           but that would likely result in extra processing time.  Using a device with a
     *           different sample data type than its native could degrade the quality of the
     *           final signal.
     *
     *  @note This function will open the audio device to test on some systems.
     *        The caller should ensure that isDirectHardwareBackend() returns
     *        false before calling this.
     *        Calling this on a 'direct hardware' backend could result in this call
     *        taking a substantial amount of time (e.g. 100ms) or failing unexpectedly.
     */
    SampleType(CARB_ABI* getDeviceSampleType)(Direction dir, size_t index);

    /** Check if the audio device backend uses direct hardware access.
     *  @returns `true` if this backend has direct hardware access.
     *           This will be returned when ALSA is in use.
     *  @returns `false` if the backend is an audio mixing server.
     *           This will be returned when Pulse Audio or Window Audio Services
     *           are in use.
     *
     *  @remarks A direct hardware audio backend is capable of exclusively locking
     *           audio devices, so devices are not guaranteed to open successfully
     *           and opening devices to test their format may be disruptive to the system.
     *
     *  @remarks ALSA is the only 'direct hardware' backend that's currently supported.
     *           Some devices under ALSA will exclusively lock the audio device;
     *           these may fail to open because they're busy.
     *           Additionally, some devices under ALSA can fail to open because
     *           they're misconfigured (Ubuntu's default ALSA configuration can
     *           contain misconfigured devices).
     *           In addition to this, opening some devices under ALSA can take
     *           a substantial amount of time (over 100ms).
     *           For these reasons, it is important to verify that you are not
     *           using a 'direct hardware' backend if you are going to call certain
     *           functions in this interface.
     */
    bool(CARB_ABI* isDirectHardwareBackend)();
};

}
}
