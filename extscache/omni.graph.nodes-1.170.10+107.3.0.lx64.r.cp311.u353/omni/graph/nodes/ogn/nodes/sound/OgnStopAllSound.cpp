// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "UsdPCH.h"
// clang-format on

#include <carb/audio/IAudioPlayback.h>
#include <omni/usd/IStageAudio.h>

#include <OgnStopAllSoundDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnStopAllSound
{
public:
    static bool compute(OgnStopAllSoundDatabase& db)
    {
        usd::audio::AudioManager* audioManager = usd::audio::getDefaultAudioManager();
        if (!audioManager)
        {
            db.logError("Unable to acquire Audio Manager!");
            return false;
        }

        carb::audio::Context* context = omni::usd::audio::getPlaybackContext(audioManager);
        auto iAudioPlayback = carb::getCachedInterface<carb::audio::IAudioPlayback>();
        iAudioPlayback->stopAllVoices(context);
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
