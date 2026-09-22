// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/Types.h>

#include <cstddef>

namespace omni
{
namespace usd
{
namespace hydra // carbonite style interface to allow other plugins to access scene delegates
{

// defined in rtx/hydra/IHydraEngine.h
struct IHydraSceneDelegate;

struct ISceneDelegateFactory
{
    CARB_PLUGIN_INTERFACE("omni::hydra::ISceneDelegateFactory", 0, 1)

    void(CARB_ABI* getInterface)(IHydraSceneDelegate& delegateInterface);
};

} // namespace hydra
} // namespace usd
} // namespace omni
