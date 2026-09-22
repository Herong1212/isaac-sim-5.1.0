// Copyright (c) 2020-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/batch/interface/IBatch.h>
#include <omni/fabric/batch/Types.h>

namespace omni
{
namespace fabric
{
namespace batch
{

class Batch;

// RAII-style handle to automatically call IBatch::runPrologue on construction and IBatch::runEpilogue at scope exit
// Initialize with BatchId created using IBatch::createThreadOwnedBatch()
struct BatchRunContextScope
{
    inline BatchRunContextScope(const BatchId& batchId);
    inline ~BatchRunContextScope();

    inline BatchRunContextId getId() const;
    inline BatchRunContextId getBatchRunContextId() const;

private:
    omni::fabric::batch::IBatch* m_interface;
    BatchId m_batchId;
    BatchRunContextId m_batchRunContextId;
};

} // namespace batch
} // namespace fabric
} // namespace omni

#include "omni/fabric/batch/impl/BatchRunContextScope.inl"
