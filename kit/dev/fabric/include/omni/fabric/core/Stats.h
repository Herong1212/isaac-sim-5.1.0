// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/interface/IStats.h>

namespace omni
{
namespace fabric
{

// Public interface to Fabric internal stats
struct Stats
{
    /** Retrieves requested Fabric memory stats
     *
     * @return true of span was large enough for requested stats
     */
    inline static bool getMemoryStats(MemoryStatsC&);
};

} // namespace fabric
} // namespace omni

#include "Stats.inl"
