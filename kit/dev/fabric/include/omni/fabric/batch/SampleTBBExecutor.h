// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <tbb/parallel_for.h>

#include <omni/fabric/batch/Batch.h>
#include <omni/fabric/batch/BatchRunContextScope.h>
#include <omni/fabric/batch/Types.h>

namespace omni
{
namespace fabric
{
namespace batch
{

// SampleTBBExecutor implements an example way of driving execution over Batch API in deferred mode.
// This example uses tbb to drive execution.
//
// * Creates a BatchRunContextScope, which calls the requisite runPrologue() / runEpilogue() using a RAII pattern
// * Uses tbb::parallel_for to generate tasks 1:1 with the Batch's configured cpuConcurrencyWidth()
// * Each task concurrently calls runWithInitialQueueIndex
//
//   * We forward the tbb's blocked_range to runWithInitialQueueIndex. This initializes execution for each
//     task at an independent work queue, to maximize throughput and minimize synchronization.
//
//   * Batch API automatically employs work stealing, so there is no risk that cpuConcurrencyWidth tuning. thread
//   * availability, or cpu load will prevent total progression, so long as the Lambda provided doesn't deadlock
//.
struct SampleTBBExecutor
{
    inline SampleTBBExecutor()
    {
    }

    inline void operator()(omni::fabric::batch::Batch& batch) const
    {
        BatchRunContextScope runContextScope(batch.getId());

        tbb::parallel_for(
            tbb::blocked_range<size_t>(0, batch.cpuConcurrencyWidth(), 1),
            [this, &batch, &runContextScope](tbb::blocked_range<size_t>& r) {
                for (size_t index = r.begin(); index < r.end(); ++index)
                {
                    batch.runWithInitialQueueIndex(runContextScope.getId(), index);
                }
            },
            tbb::simple_partitioner());
    }

    static void run(omni::fabric::batch::Batch& batch)
    {
        SampleTBBExecutor()(batch);
    }
};

} // namespace batch
} // namespace fabric
} // namespace omni
