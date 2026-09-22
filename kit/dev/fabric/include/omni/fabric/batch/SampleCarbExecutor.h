// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/tasking/ITasking.h>

#include <omni/fabric/batch/Batch.h>
#include <omni/fabric/batch/BatchRunContextScope.h>
#include <omni/fabric/batch/Types.h>

namespace omni
{
namespace fabric
{
namespace batch
{


// SampleCarbExecutor implements an example way of driving execution over Batch API in deferred mode.
// This example uses carb::tasking to drive execution.
//
// * Creates a BatchRunContextScope, which calls the requisite runPrologue() / runEpilogue() using a RAII pattern
// * Uses carb::tasking::ITasking::applyBatchRange to generate tasks 1:1 with the Batch's configured cpuConcurrencyWidth()
// * Each carb task concurrently calls runWithInitialQueueIndex
//
//   * We forward the carb scheduler's 'index' to runWithInitialQueueIndex. This initializes execution for each
//     fiber at an independent work queue, to maximize throughput and minimize synchronization.
//
//   * Batch API automatically employs work stealing, so there is no risk that cpuConcurrencyWidth tuning, fiber
//   * availability, or cpu load will prevent total progression, so long as the user-provided Lambda doesn't deadlock
//.
struct SampleCarbExecutor
{
    inline SampleCarbExecutor()
        : tasking(carb::getCachedInterface<carb::tasking::ITasking>())
    {
    }

    inline void operator()(omni::fabric::batch::Batch& batch) const
    {
        BatchRunContextScope runContextScope(batch.getId());

        tasking->applyRangeBatch(batch.cpuConcurrencyWidth(), 1, [this, &batch, &runContextScope](const size_t begin, const size_t end) {
            for (size_t index = begin; index < end; ++index)
            {
                batch.runWithInitialQueueIndex(runContextScope.getId(), index);
            }
        });
    }

    static void run(omni::fabric::batch::Batch& batch)
    {
        SampleCarbExecutor()(batch);
    }

    carb::tasking::ITasking* tasking;
};

} // namespace batch
} // namespace fabric
} // namespace omni
