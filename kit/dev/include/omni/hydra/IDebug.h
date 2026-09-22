// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/InterfaceUtils.h>
#include <omni/hydra/OmniHydraTypes.h>

namespace omni
{
namespace usd
{
namespace hydra
{
struct IDebug
{
    CARB_PLUGIN_INTERFACE("omni::hydra::IDebug", 0, 1)

    size_t(CARB_ABI* getTimestampedTransformCount)();
    void(CARB_ABI* getTimestampedTransforms)(TimestampedTransform* out, size_t outCount);
};

}
}
}
