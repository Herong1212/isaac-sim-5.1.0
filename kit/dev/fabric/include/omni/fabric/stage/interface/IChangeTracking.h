// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#ifndef __CUDACC__

#include <carb/Interface.h>

namespace omni
{
namespace fabric
{

struct FineGrainedChangeTrackerId
{
    uint64_t id;

    bool operator==(FineGrainedChangeTrackerId other) const
    {
        return id == other.id;
    }
    bool operator!=(FineGrainedChangeTrackerId other) const
    {
        return id != other.id;
    }
};

static_assert(std::is_standard_layout<FineGrainedChangeTrackerId>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

static constexpr FineGrainedChangeTrackerId kInvalidFineGrainedChangeTrackerId = { (uint64_t)0 };

struct IFineGrainedChangeTracker
{
    CARB_PLUGIN_INTERFACE("omni::fabric::IFineGrainedChangeTracker", 0, 2);

    void(CARB_ABI* setDirty)(FineGrainedChangeTrackerId, uint64_t primIndex);
    bool(CARB_ABI* isDirty)(FineGrainedChangeTrackerId, uint64_t primIndex);
};

} // namespace fabric
} // namespace omni

#endif
