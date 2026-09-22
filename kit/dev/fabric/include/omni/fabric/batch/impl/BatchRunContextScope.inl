// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
namespace omni
{
namespace fabric
{
namespace batch
{

BatchRunContextScope::BatchRunContextScope(const BatchId& batchId)
    : m_interface(carb::getCachedInterface<omni::fabric::batch::IBatch>()), m_batchId(batchId)
{
    CARB_ASSERT(m_interface);
    m_batchRunContextId = m_interface->runPrologue(m_batchId);
}

BatchRunContextScope::~BatchRunContextScope()
{
    m_interface->runEpilogue(m_batchId, m_batchRunContextId);
    m_batchRunContextId = BATCH_RUN_CONTEXT_ID_INVALID;
}

BatchRunContextId BatchRunContextScope::getId() const
{
    return m_batchRunContextId;
}

BatchRunContextId BatchRunContextScope::getBatchRunContextId() const
{
    return m_batchRunContextId;
}

} // namespace batch
} // namespace fabric
} // namespace omni
