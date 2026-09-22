// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <carb/audio/IAudioPlayback.h>
#include <carb/audio/AudioUtils.h>
#include <omni/usd/IStageAudio.h>

#include <OgnPauseSoundDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnPauseSound
{
public:
    static bool compute(OgnPauseSoundDatabase& db)
    {
        usd::audio::AudioManager* audioManager = usd::audio::getDefaultAudioManager();
        if (!audioManager)
        {
            db.logError("Unable to acquire Audio Manager!");
            return false;
        }

        uint64_t const& soundId = db.inputs.soundId();
        auto iAudioPlayback = carb::getCachedInterface<carb::audio::IAudioPlayback>();
        auto voice = reinterpret_cast<carb::audio::Voice*>(soundId);
        if (!voice)
        {
            return false;
        }

        carb::audio::VoiceParams params;
        iAudioPlayback->getVoiceParameters(voice, carb::audio::fVoiceParamPause, &params);
        if ((params.playbackMode & carb::audio::fPlaybackModePaused) != 0)
        {
            carb::audio::unpauseVoice(iAudioPlayback, voice);
        }
        else
        {
            carb::audio::pauseVoice(iAudioPlayback, voice);
        }

        carb::audio::Context* context = omni::usd::audio::getPlaybackContext(audioManager);
        iAudioPlayback->update(context);
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
