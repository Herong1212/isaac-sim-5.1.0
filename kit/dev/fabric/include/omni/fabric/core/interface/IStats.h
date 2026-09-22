// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
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

#include <omni/fabric/core/FabricTypes.h>

namespace omni
{
namespace fabric
{

struct MemoryStatsC
{
    const size_t sizeOf = sizeof(*this);

    // v1
    size_t allocCount;
    size_t allocBytes;
    size_t peakAllocCount;
    size_t peakAllocBytes;
    size_t minAllocBytes;
    size_t maxAllocBytes;
};

struct IStats
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IStats", 1, 0);

    bool (CARB_ABI* getMemoryStats)(MemoryStatsC&);
};

} // namespace fabric
} // namespace omni
