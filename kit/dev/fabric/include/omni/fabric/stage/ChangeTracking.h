// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#ifdef __CUDACC__
#error
#endif

#include <carb/Interface.h>
#include <carb/InterfaceUtils.h>
#include <omni/fabric/stage/interface/IChangeTracking.h>

namespace omni
{
namespace fabric
{

class FineGrainedChangeTracker
{
    FineGrainedChangeTrackerId fineGrainedChangeTrackerId;

public:
    FineGrainedChangeTracker() : fineGrainedChangeTrackerId(kInvalidFineGrainedChangeTrackerId)
    {
    }
    FineGrainedChangeTracker(FineGrainedChangeTrackerId id) : fineGrainedChangeTrackerId(id)
    {
    }

    void setDirty(uint64_t primIndex)
    {
        carb::getCachedInterface<omni::fabric::IFineGrainedChangeTracker>()->setDirty(
            fineGrainedChangeTrackerId, primIndex);
    }

    bool isDirty(uint64_t primIndex) const
    {
        return carb::getCachedInterface<omni::fabric::IFineGrainedChangeTracker>()->isDirty(
            fineGrainedChangeTrackerId, primIndex);
    }
};

} // namespace fabric
} // namespace omni
