// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>
#include <carb/InterfaceUtils.h> // used by BatchScope.inl for inlined implementation
#include <carb/cpp/Span.h>

#include <omni/fabric/batch/Types.h>
#include <omni/fabric/IdTypes.h>

namespace omni
{
namespace fabric
{
namespace batch
{

// IBatch (Batch API) is a canonical way to interact with data hosted by Fabric. It is an entirely optional suite of
// tools to aid with common Fabric data integration patterns. It is a general solution that is optimized for maximum
// throughput and minimal overhead. It is not guaranteed to be more efficient than an entirely bespoke solution, but it
// is intended to reach near-peak performance with much less effort.
//
// For detailed discussion on the API, see the public documentation.
struct IBatch
{
    CARB_PLUGIN_INTERFACE("omni::fabric::batch::iBatch", 0, 3);

    BatchId(CARB_ABI* createThreadOwnedBatch)();

    void(CARB_ABI* destroyBatch)(const BatchId& batchId);

    void(CARB_ABI* changeOwnerToCurrentThread)(const BatchId& batchId);

    const struct View&(CARB_ABI* generateView)(const BatchId& batchId,
                                               const omni::fabric::FabricId& fabricId,
                                               const ViewGenerationOptions& options,
                                               const struct BatchFilter& filter);

    void(CARB_ABI* setPreferences)(const BatchId& batchId, const struct BatchPreferences& preferences);

    void(CARB_ABI* addFabricId)(const BatchId& batchId, const omni::fabric::FabricId& fabricId);

    size_t(CARB_ABI* addLambda)(const BatchId& batchId, const struct Lambda& lambda);

    void(CARB_ABI* clear)(const BatchId& batchId);

    void(CARB_ABI* bake)(const BatchId& batchId);

    size_t(CARB_ABI* cpuConcurrencyWidth)(const BatchId& batchId);

    BatchRunContextId(CARB_ABI* runPrologue)(const BatchId& batchId);

    void(CARB_ABI* runEpilogue)(const BatchId& batchId, const BatchRunContextId& contextId);

    void(CARB_ABI* run)(const BatchId& batchId, const BatchRunContextId& contextId);

    void(CARB_ABI* runWithInitialQueueIndex)(const BatchId& batchId,
                                             const BatchRunContextId& contextId,
                                             const size_t desiredQueueIndex);

    void(CARB_ABI* cancel)(const BatchId& batchId);

    void(CARB_ABI* print)(const BatchId& batchId);

    void(CARB_ABI* markViewsValid)(const BatchId& batchId);

    void(CARB_ABI* reportStatistics)(const BatchId& batchId, const size_t iterations);

    void(CARB_ABI* reportRunTime)(const BatchId& batchId, const size_t iterations);

    void(CARB_ABI* resetStatistics)(const BatchId& batchId);

    void(CARB_ABI* setDeveloperSettings)(const BatchId& batchId, const struct BatchDeveloperSettings& developer);

    carb::cpp::span<const batch::AttributeSpecification>(CARB_ABI* getAttributeSpecifications)(const BatchId& batchId,
                                                                                               const size_t lambdaIndex);
};

} // namespace batch
} // namespace fabric
} // namespace omni
