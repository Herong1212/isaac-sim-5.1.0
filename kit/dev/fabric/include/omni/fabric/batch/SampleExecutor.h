// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/batch/Batch.h>
#include <omni/fabric/batch/BatchRunContextScope.h>
#include <omni/fabric/batch/Types.h>

namespace omni
{
namespace fabric
{
namespace batch
{

// SampleExecutor implements an example way of driving execution over Batch API in deferred mode.
// This example executes on the calling thread.
//
// * Creates a BatchRunContextScope, which calls the requisite runPrologue() / runEpilogue() using a RAII pattern

// * This is the simplest, single-threaded execution model.
//
struct SampleExecutor
{
    inline SampleExecutor()
    {
    }

    inline void operator()(omni::fabric::batch::Batch& batch) const
    {
        BatchRunContextScope runContextScope(batch.getId());

        batch.run(runContextScope.getId());
    }

    static void run(omni::fabric::batch::Batch& batch)
    {
        SampleExecutor()(batch);
    }
};

} // namespace batch
} // namespace fabric
} // namespace omni
