// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>
#include <carb/IObject.h>

#include <omni/fabric/core/interface/IFabricSampleStorage.h> // OnAddSampleCallback, OnSetUneditableCallback
#include <omni/String.h>

#include <stdint.h>


namespace omni
{
namespace usd::hydra
{
struct FrameIdentifier;
}

namespace fabric
{

struct SampleIndex;
class SimStageWithHistory;
class FabricRenderingView;

class FabricContext : public carb::IObject
{
public:
    virtual omni::fabric::SimStageWithHistory* getStageWithHistory() = 0;
    virtual omni::fabric::FabricRenderingView* getFabricRenderingView() = 0;
}; 
using IFabricContextPtr = carb::ObjectPtr<FabricContext>;


struct IFabricContextManager
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IFabricContextManager", 1, 0);

    using PxrUsdStageID = long int;

    IFabricContextPtr (CARB_ABI* initializeFabric)(PxrUsdStageID usdStageId,
                                                   bool isAnonymousLayer,
                                                   const omni::string& materialBindingPurpose,
                                                   const omni::string& fabricCachePath,
                                                   omni::string rootIdentifier,
                                                   double timeCode,
                                                   const omni::fabric::SampleIndex& sampleIndex,
                                                   OnAddSampleCallback addSampleCallback,
                                                   OnSetUneditableCallback setUneditableCallback,
                                                   uint64_t* stagePopulationRequestHandle);

    bool(CARB_ABI* deinitializeFabric)(IFabricContextPtr fabricContext,
                                       PxrUsdStageID usdStageId);

    IFabricContextPtr (CARB_ABI* getFabricContextFromUsdStageId)(PxrUsdStageID usdStageId);

    bool (CARB_ABI* getFabricIdForTime)(PxrUsdStageID usdStageId,
                                        const omni::usd::hydra::FrameIdentifier& frameIdentifier,
                                        double time, /* usd-time currently unused */
                                        size_t fabricIdIndex, /* pass zero */
                                        omni::fabric::FabricId& fabricIdOut,
                                        omni::fabric::SampleIndex& sampleIndexOut,
                                        omni::fabric::FabricSampleStorageId& storageIdOut,
                                        omni::fabric::LockedReadSamplesId& fabricLockId);
};

} // namespace fabric
} // namespace omni
