// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>


namespace omni
{
namespace audio
{

/** public container for a loaded editor UI sound.  These objects are returned from
 *  @ref IUiAudio::createSound().  These objects can be copied as needed.  Once destroyed,
 *  the sound itself will only be destroyed if the no other objects refer to it as well.
 */
class UiSound
{
public:
    /** Constructor: Creates a new `UiSound` object with the default construction. */
    UiSound() = default;

    /** Constructor: Copies another existing `UiSound` object into this one.
     *
     *  @param[in] other    The other object to copy state from.
     */
    UiSound(const UiSound& other) = default;
    virtual ~UiSound() = default;

    /** Assignment operator: copies another existing `UiSound` object into this one.
     *
     *  @param[in] other    The other object to copy state from.
     */
    virtual UiSound& operator=(const UiSound& other) = 0;
};

/** simple interface to manage editor UI sound objects.  This allows new sound objects to be
 *  created (and loaded) from local disk, sounds to be played, stopped, and queried.
 */
struct IUiAudio
{
    /** @private */
    CARB_PLUGIN_INTERFACE("omni::audio::IUiAudio", 0, 1);

    /** Loads an editor UI sound from local disk.
     *
     *  @param[in] filename     the path to the sound file to load.  This should be an absolute
     *                          path, but can be a relative path that will be resolved using the
     *                          current working directory for the process.  This may not be
     *                          nullptr.  Parts of this path may include some special path
     *                          specifiers that will be resolved when trying to open the file.
     *                          See the remarks section below for more info.  This may not be
     *                          nullptr or an empty string.
     *  @return the sound object representing the new loaded sound.  This sound can be passed to
     *          playSound() later.  Each sound object returned here must be destroyed by
     *          deleting it when it is no longer needed.  Note that destroying the sound object
     *          will stop all playing instances of it.  However, if more than one reference to
     *          the same sound object still exists, deleting one of the sound objects will not
     *          stop any of the instances from playing.  It is best practice to always explicitly
     *          stop a sound before destroying it.
     *  @return nullptr if the file could not be loaded could not be loaded.
     *
     *  @remarks This loads a sound that can be played with playSound() at a later time.  This
     *           sound only needs to be loaded once but can be played as many times as needed.
     *           When no longer needed, the sound should be destroyed by deleting it.
     *
     *  @remarks File names passed in here may contain special path markers.
     *
     *  @note This operation is always thread safe.
     */
    UiSound*(CARB_ABI* createSound)(const char* filename);

    /** Immediately plays the requested UI sound if it is loaded.
     *
     *  @param[in] sound    the name of the UI sound to be played.  This may not be nullptr.
     *  @return no return value.
     *
     *  @remarks This plays a single non-looping instance of a UI sound immediately.  The UI sound
     *           must have already been loaded.  If the sound resource was missing or couldn't be
     *           loaded, this call will simply be ignored.  This will return immediately after
     *           scheduling the sound to play.  It will never block for the duration of the sound's
     *           playback.  This sound may be prematurely stopped with stopSound().
     *
     *  @note This operation is always thread safe.
     */
    void(CARB_ABI* playSound)(UiSound* soundToPlay);

    /** Queries whether a sound object is currently playing.
     *
     *  @param[in] sound    the sound object to query the playing state for.  This may not be
     *                      nullptr.
     *  @return true if the sound object is currently playing.
     *  @return false if the sound has either finished playing or has not been played yet.
     *
     *  @remarks This queries whether a sound is currently playing.  If this fails, that may mean
     *           that the sound ended naturally on its own or it was explicitly stopped.  Note
     *           that this may continue to return true for a short period after a sound has been
     *           stopped with stopSound() or stopAllSounds().  This period may be up to 10
     *           milliseconds.
     */
    bool(CARB_ABI* isSoundPlaying)(const UiSound* sound);

    /** Immediately stops the playback of a sound.
     *
     *  @param[in] sound    the sound object to stop playback for.  This may not be nullptr.
     *  @return no return value.
     *
     *  @remarks This stops the playback of an active sound.  If the sound was not playing or had
     *           already naturally stopped on its own, this call is ignored.
     */
    void(CARB_ABI* stopSound)(UiSound* sound);

    /** Retrieves length of a sound in seconds (if known).
     *
     *  @param[in] sound    the sound to retrieve the length for.  This may not be nullptr.
     *  @return the play length of the sound in seconds if the asset is loaded and the length
     *          can be calculated.
     *  @return 0.0 if the sound asset is not available yet or the length could not be properly
     *          calculated.
     *
     *  @remarks This calculates the length of a UI sound in seconds.  This is just the length
     *           of the sound asset in seconds.
     */
    double(CARB_ABI* getSoundLength)(UiSound* sound);
};

}
}
