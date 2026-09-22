// Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/events/IEvents.h>
#include <memory>

namespace omni
{
namespace anim
{
namespace graph
{

template <typename T>
struct span
{
    T* ptr;
    size_t size;
};

namespace DirectModeEventTypes
{
    const carb::events::EventType kEventTypeAnimationLoop = CARB_EVENTS_TYPE_FROM_STR("EVENT_TYPE_ANIMATION_LOOP");
    const carb::events::EventType kEventTypeBlendInComplete = CARB_EVENTS_TYPE_FROM_STR("EVENT_TYPE_ANIMATION_BLEND_IN_COMPLETE");
    const carb::events::EventType kEventTypeBlendOutStart = CARB_EVENTS_TYPE_FROM_STR("EVENT_TYPE_ANIMATION_BLEND_OUT_START");
    const carb::events::EventType kEventTypeEnd = CARB_EVENTS_TYPE_FROM_STR("EVENT_TYPE_ANIMATION_END");
}

namespace DirectModeAnimationOptions
{
    static constexpr unsigned looping = 0x01;
    static constexpr unsigned paused = 0x02;
}

struct DirectModeAnimation
{
    std::shared_ptr<void> asset;
    unsigned options = 0;
    float layer = 0;
    float opacity = 1;
    float blendIn = 0;
    float blendOut = 0;
};

}
}
}
