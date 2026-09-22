// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/SettingsUtils.h>


/** audio setting group names.  These provide the starting path to all of the common
 *  audio settings.
 *  @{
 */
/** the group name for all playback audio settings in Kit. */
#define AUDIO_SETTING_GROUP_CONTEXT "/audio/context"
/** @} */

/** setting leaf names.  These must be prefixed by @ref AUDIO_SETTING_GROUP_CONTEXT
 *  to be valid for a settings lookup.
 *  @{
 */
#define AUDIO_SETTING_NAME_MAXBUSES "maxBuses"
#define AUDIO_SETTING_NAME_SPEAKERMODE "speakerMode"
#define AUDIO_SETTING_NAME_STREAMERFILE "streamerFile"
#define AUDIO_SETTING_NAME_ENABLESTREAMER "enableStreamer"
#define AUDIO_SETTING_NAME_DEVICENAME "deviceName"
#define AUDIO_SETTING_NAME_CAPTUREDEVICENAME "captureDeviceName"
#define AUDIO_SETTING_NAME_AUTOSTREAM "autoStreamThreshold"
#define AUDIO_SETTING_NAME_AUDIO_PLAYER_AUTOSTREAM "audioPlayerAutoStreamThreshold"
#define AUDIO_SETTING_NAME_CLOSEONSOUNDSTOP "closeAudioPlayerOnStop"
#define AUDIO_SETTING_NAME_MASTERVOLUME "masterVolume"
#define AUDIO_SETTING_NAME_USDVOLUME "usdVolume"
#define AUDIO_SETTING_NAME_SPATIALVOLUME "spatialVolume"
#define AUDIO_SETTING_NAME_NONSPATIALVOLUME "nonSpatialVolume"
#define AUDIO_SETTING_NAME_UIVOLUME "uiVolume"
/** @} */

/********************************** Audio Settings Paths *****************************************/
namespace omni
{
namespace audio
{

/** full path suffixes for the Kit audio settings.  For the app preferences settings values
 *  that should persist between launches of Kit, these names should each be prefixed with
 *  @ref PERSISTENT_SETTINGS_PREFIX.  If a value should not persist but instead be reset
 *  between launches, it should not have a prefix.
 *
 *  Each of these settings paths should be created by concatenating an optional persistence
 *  prefix, one AUDIO_SETTING_GROUP_* name, a group separator (ie: @ref SETTING_SEP), and one
 *  AUDIO_SETTING_NAME_* value name.
 *
 *  @{
 */
/** the number of buses to create the main audio playback context with.  This will control
 *  the maximum number of simultaneous voices that can be heard during playback.  Any playing
 *  voices beyond this count will be 'virtual' and will only be heard when another voice
 *  releases its bus.  This defaults to 0 which lets the context decide on creation.
 */
constexpr char kSettingMaxBuses[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_MAXBUSES;

/** the standard speaker layout to use for playback.  This defaults to the speaker mode that
 *  most closely corresponds to the device's preferred channel count.
 */
constexpr char kSettingSpeakerMode[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_SPEAKERMODE;

/** the name of the file to stream output to.  This will be written as a RIFF wave file in
 *  the same data format that the playback context chooses.  The file will not be created
 *  unless audio (even silent audio) is written to it.  The file will also only be created
 *  if the @ref AUDIO_SETTING_NAME_ENABLESTREAMER setting is also enabled.  This defaults
 *  to an empty string.
 */
constexpr char kSettingStreamerFile[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_STREAMERFILE;

/** boolean option to control whether the streamer is used or not for the current session.
 *  Note that this setting is intentionally not persistent.  This should always be disabled
 *  on launch.  If it were persistent, it would lead to all audio being recorded even when
 *  not intended, and potentially filling up the local drive.
 */
constexpr char kSettingEnableStreamer[] =
    AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_ENABLESTREAMER;

/** the identifier of the device that should be used for audio playback.  This name can be
 *  retrieved from the omni::audio::IAudioDeviceEnum interface using the getDeviceId()
 *  function.  This name may consist of a device GUID, a friendly device name, or a
 *  combination of both.  If a GUID is provided, a connected device using that name will
 *  be chosen if found.  If a GUID is not provided or no connected device matches the
 *  given GUID, the device will attempt to match by its friendly name.  Note that this
 *  friendly name is not necessarily unique in the system and the wrong device may end
 *  up being selected in this case (if multiple devices with the same friendly name
 *  are connected).  This defaults to an empty string indicating that the system's default
 *  device should always be used.
 */
constexpr char kSettingDeviceName[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_DEVICENAME;

/** The identifier of the device that should be used for audio capture.
 *  This functions identically to @ref kSettingDeviceName, except that it's used
 *  to specify the capture device instead of the playback device.
 */
constexpr char kSettingCaptureDeviceName[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_CAPTUREDEVICENAME;

/** the current auto-stream threshold setting in kilobytes.  This controls when the audio
 *  data system decides to stream an encoded sound versus decode it fully on load.  This
 *  threshold represents the decoded size of a sound above which it will be streamed instead
 *  of decoded.  If the decoded size of the sound is less than this threshold, it will be
 *  decoded on load instead.
 */
constexpr char kSettingAutoStream[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_AUTOSTREAM;


/** the current auto-stream threshold setting in kilobytes specifically for the audio player.
 *  This controls when the audio data system decides to stream an encoded sound versus decode it fully on load.
 *  This threshold represents the decoded size of a sound above which it will be streamed instead
 *  of decoded.  If the decoded size of the sound is less than this threshold, it will be
 *  decoded on load instead. Note that this setting is only for the audio player. Use @ref kSettingAutoStream
 *  for the Audio Manager's auto stream threshold.
 */
constexpr char kSettingAudioPlayerAutoStream[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_AUDIO_PLAYER_AUTOSTREAM;

/** The option to close the audio player window when the sound is stopped.
 *  If this is enabled, then the audio player will be automatically closed when the user clicks
 *  the stop button or when the sound reaches its natural end.
 */
constexpr char kSettingCloseOnSoundStop[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_CLOSEONSOUNDSTOP;

/** the master volume level setting to use.  This master volume affects all audio output
 *  from the USD stage audio manager, UI audio manager, and the audio player interfaces.
 *  This level should be set to 1.0 for full volume and 0.0 for silence.  The volume scale
 *  is approximately linear.  This defaults to 1.0.
 */
constexpr char kSettingMasterVolume[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_MASTERVOLUME;

/** the master volume for the USD stage audio manager to use.  This does not affect the
 *  UI audio manager or the audio player interfaces.  This level should be set to 1.0 for
 *  full volume and 0.0 for silence.  The volume scale is approximately linear.  This
 *  defaults to 1.0.
 */
constexpr char kSettingUsdVolume[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_USDVOLUME;

/** the relative volume level for spatial audio sounds in the USD stage audio manager.  This
 *  volume level will effectively be multiplied by the master volume and USD volume levels
 *  above to get the final effective volume level for spatial sounds.  This level should be
 *  set to 1.0 for full volume and 0.0 for silence.  The volume scale is approximately linear.
 *  This defaults to 1.0.
 */
constexpr char kSettingSpatialVolume[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_SPATIALVOLUME;

/** the relative volume level for non-spatial audio sounds in the USD stage audio manager.  This
 *  volume level will effectively be multiplied by the master volume and USD volume levels above
 *  to get the final effective volume level for non-spatial sounds.  This level should be set to
 *  1.0 for full volume and 0.0 for silence.  The volume scale is approximately linear.  This
 *  defaults to 1.0.
 */
constexpr char kSettingNonSpatialVolume[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_NONSPATIALVOLUME;

/** the master volume level for the UI audio manager.  This level should be set to 1.0 for full
 *  volume, and 0.0 for silence.  The volume scale is approximately linear.  This defaults to
 *  1.0.
 */
constexpr char kSettingUiVolume[] =
    PERSISTENT_SETTINGS_PREFIX AUDIO_SETTING_GROUP_CONTEXT SETTING_SEP AUDIO_SETTING_NAME_UIVOLUME;
/** @} */

}
}
