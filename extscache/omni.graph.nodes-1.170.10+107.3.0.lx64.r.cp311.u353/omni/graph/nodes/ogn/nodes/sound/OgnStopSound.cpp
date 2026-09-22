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

#include <OgnStopSoundDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnStopSound
{
public:
    static bool compute(OgnStopSoundDatabase& db)
    {
        uint64_t const& soundId = db.inputs.soundId();
        auto iAudioPlayback = carb::getCachedInterface<carb::audio::IAudioPlayback>();
        auto voice = reinterpret_cast<carb::audio::Voice*>(soundId);
        iAudioPlayback->stopVoice(voice);
        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
