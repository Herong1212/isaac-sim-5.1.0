// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/Interface.h>

namespace omni
{
namespace fabric
{

enum class PlatformId : uint8_t
{
    Global /* c++17 [[deprecated]] */ = 0,
    Count /* c++17 [[deprecated]] */,
};

struct Platform;
struct IPlatform
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IPlatform", 0, 2);

    [[deprecated]]
    const Platform&(CARB_ABI* get)(const PlatformId& platformId);

    [[deprecated]]
    Platform&(CARB_ABI* getMutable)(const PlatformId& platformId);

    [[deprecated]]
    void(CARB_ABI* reset)(const PlatformId& platformId);

    [[deprecated]]
    void(CARB_ABI* resetAll)();

    Platform&(CARB_ABI* getSingleton)();
};

} // namespace fabric
} // namespace omni
