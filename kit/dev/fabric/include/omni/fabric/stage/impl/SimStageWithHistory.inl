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

inline void SimStageWithHistory::createForAllStages(int64_t simFrameNumber)
{
    auto SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    SRWInterface->createForAllStages(simFrameNumber);
}

inline void SimStageWithHistory::flushAllStagesToRingBuffer()
{
    auto SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    SRWInterface->flushAllStagesToRingBuffer();
}

// SimStageWithHistory implementation starts here
inline bool SimStageWithHistory::exists(UsdStageId stageId)
{
    auto SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    return SSWHInterface->exists(stageId);
}

inline void SimStageWithHistory::internalSetup(UsdStageId id)
{
    if (m_simStageWithHistory != kInvalidSimStageWithHistoryId)
    {
        m_usdStageId = id;
        m_workingStageReaderWriter = m_SRWInterface->get(m_usdStageId);
        m_workingFabricId = m_SRWInterface->getFabricId(m_workingStageReaderWriter);
    }
    else
    {
        m_usdStageId = kUninitializedStage;
        m_workingStageReaderWriter = kInvalidStageReaderWriterId;
        m_workingFabricId = kInvalidFabricId;
    }

}

inline SimStageWithHistory::SimStageWithHistory(UsdStageId usdStageId,
                                                size_t historyFrameCount,
                                                FabricTime simPeriod,
                                                omni::fabric::GpuComputeType computeType)
{
    m_SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    m_SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_SSWHInterface);
    CARB_ASSERT(m_SRWInterface);

    m_simStageWithHistory = m_SSWHInterface->getOrCreate(
        usdStageId, historyFrameCount, simPeriod,
        computeType);
    internalSetup(usdStageId);
}

inline SimStageWithHistory::SimStageWithHistory(UsdStageId usdStageId)
{
    m_SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    m_SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_SSWHInterface);
    CARB_ASSERT(m_SRWInterface);

    m_simStageWithHistory = m_SSWHInterface->get(usdStageId);
    internalSetup(usdStageId);
}

inline SimStageWithHistory::SimStageWithHistory()
{
    m_SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    m_SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_SSWHInterface);
    CARB_ASSERT(m_SRWInterface);
    m_simStageWithHistory = kInvalidSimStageWithHistoryId;
    internalSetup(kUninitializedStage);
}

inline SimStageWithHistory::SimStageWithHistory(SimStageWithHistory& other)
{
    m_SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    m_SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_SSWHInterface);
    CARB_ASSERT(m_SRWInterface);

    m_simStageWithHistory = m_SSWHInterface->get(other.m_usdStageId);
    internalSetup(other.m_usdStageId);
}

inline SimStageWithHistory& SimStageWithHistory::operator=(const SimStageWithHistory& other)
{
    m_SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    m_SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_SSWHInterface);
    CARB_ASSERT(m_SRWInterface);
    m_SSWHInterface->release(m_usdStageId);
    m_simStageWithHistory = m_SSWHInterface->get(other.m_usdStageId);
    internalSetup(other.m_usdStageId);
    return *this;
}

inline SimStageWithHistory::SimStageWithHistory(SimStageWithHistory&& other)
{
    m_SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    m_SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_SSWHInterface);
    CARB_ASSERT(m_SRWInterface);
    m_simStageWithHistory = m_SSWHInterface->get(other.m_usdStageId);
    internalSetup(other.m_usdStageId);

    m_SSWHInterface->release(other.m_usdStageId);
    other.m_simStageWithHistory = kInvalidSimStageWithHistoryId;
    other.m_usdStageId = kUninitializedStage;
    other.m_workingStageReaderWriter = kInvalidStageReaderWriterId;
    other.m_workingFabricId = kInvalidFabricId;
}

inline SimStageWithHistory& SimStageWithHistory::operator=(SimStageWithHistory&& other)
{
    m_SSWHInterface = carb::getCachedInterface<omni::fabric::ISimStageWithHistory>();
    m_SRWInterface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_SSWHInterface);
    CARB_ASSERT(m_SRWInterface);
    m_SSWHInterface->release(m_usdStageId);
    m_simStageWithHistory = m_SSWHInterface->get(other.m_usdStageId);
    internalSetup(other.m_usdStageId);
    
    m_SSWHInterface->release(other.m_usdStageId);
    other.m_simStageWithHistory = kInvalidSimStageWithHistoryId;
    other.m_usdStageId = kUninitializedStage;
    other.m_workingStageReaderWriter = kInvalidStageReaderWriterId;
    other.m_workingFabricId = kInvalidFabricId;

    return *this;
}

inline SimStageWithHistory::~SimStageWithHistory()
{
    // Don't release if we never got a valid stage to begin with.  If that happened
    // a stage could have been created after this object was created thus mucking up the refcount.
    if (m_simStageWithHistory != kInvalidSimStageWithHistoryId)
        m_SSWHInterface->release(m_usdStageId);
}

inline SimStageWithHistoryId SimStageWithHistory::getId() const
{
    return m_simStageWithHistory;
}

inline UsdStageId SimStageWithHistory::getUsdStageId() const
{
    return m_usdStageId;
}

inline FabricId SimStageWithHistory::getWorkingFabricId() const
{
    return m_workingFabricId;
}

inline void SimStageWithHistory::setFrameNumber(int64_t simFrameNumber)
{
    m_SRWInterface->create(m_usdStageId, simFrameNumber);
}

inline int64_t SimStageWithHistory::getFrameNumber() const
{
    return (int64_t)m_SRWInterface->getFrameNumber(m_workingStageReaderWriter);
}

inline FabricTime SimStageWithHistory::getFrameTime() const
{
    return m_SRWInterface->getFrameTime(m_workingStageReaderWriter);
}

inline FabricTime SimStageWithHistory::getSimPeriod() const
{
    return m_SSWHInterface->getSimPeriod(m_usdStageId);
}

inline size_t SimStageWithHistory::getFrameHistoryCount() const
{
    return m_SSWHInterface->getFrameHistoryCount(m_usdStageId);
}

inline FabricTime SimStageWithHistory::getLatestFrame() const
{
    return m_SSWHInterface->getLatestFrame(m_usdStageId);
}

inline void SimStageWithHistory::flushToRingBuffer()
{
    m_SRWInterface->flushToRingBuffer(m_usdStageId);
}

inline void SimStageWithHistory::getWriteParameters(int64_t& simFrameNumber, int64_t& writeSlot)
{
    m_SRWInterface->getWriteParameters(m_usdStageId, simFrameNumber, writeSlot);
}

inline void SimStageWithHistory::exclusiveAcquireAndInitRingBufferSlotForCurrentSimStage(
    SimStageWithHistoryLockSnapshot& lockedSnapshot)
{
    m_SRWInterface->exclusiveAcquireAndInitRingBufferSlotForCurrentSimStage(m_usdStageId, lockedSnapshot);
}

inline void SimStageWithHistory::flushToRingBufferAlreadyLocked()
{
    m_SRWInterface->flushToRingBufferAlreadyLocked(m_usdStageId);
}

inline void SimStageWithHistory::unlock(SimStageWithHistoryLockSnapshot& lockedSnapshot)
{
    m_SRWInterface->unlock(lockedSnapshot);
}

inline void SimStageWithHistory::prefetchPrimFromUsdStage(const Path& path)
{
    m_SRWInterface->prefetchPrim(m_usdStageId, path);
}

inline StageWithHistorySnapshot SimStageWithHistory::saveSnapshot()
{
    return m_SSWHInterface->saveSnapshot(m_usdStageId);
}

inline bool SimStageWithHistory::deleteSnapshot(size_t snapshotId)
{
    return m_SSWHInterface->deleteSnapshot(m_usdStageId, snapshotId);
}

inline bool SimStageWithHistory::restoreFromSnapshot(size_t snapshotId)
{
    return m_SSWHInterface->restoreFromSnapshot(m_usdStageId, snapshotId);
}

} // namespace fabric
} // namespace omni
