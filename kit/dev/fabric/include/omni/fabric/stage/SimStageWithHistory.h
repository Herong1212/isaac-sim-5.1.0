// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/Interface.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/interface/IPath.h>
#include <omni/fabric/core/interface/IToken.h>

#include<omni/fabric/stage/interface/IStageReaderWriter.h>
#include<omni/fabric/stage/interface/ISimStageWithHistory.h>
#include <omni/fabric/core/FabricTime.h>

#include <carb/logging/Log.h>

#include <gsl/span>
#include <stdint.h>

namespace omni
{
namespace fabric
{

// Construction will create a SimStageWithHistory if one does not exist.
// Destruction will invoke the destroy call which attempts to destroy the
// SimStageWithHistory. This may not succeed if other things are holding a reference.
class SimStageWithHistory
{
    SimStageWithHistoryId m_simStageWithHistory;
    UsdStageId m_usdStageId;
    FabricId m_workingFabricId;
    StageReaderWriterId m_workingStageReaderWriter;
    IStageReaderWriter* m_SRWInterface;
    ISimStageWithHistory* m_SSWHInterface;

    friend class StageReaderWriter;
    friend class StageAtTimeInterval;

    void internalSetup(UsdStageId id);

public:

    static void createForAllStages(int64_t simFrameNumber);
    static void flushAllStagesToRingBuffer();
    /**
     * @brief  Static function to check the existence of a simstageWithHistory associated with stageId
     *
     * @param stageId the UsdStageId to check for exists
     * @return whether or not a SimStageWithHistory exists associated with the stageId
     */
    static bool exists(UsdStageId stageId);

    /**
     * @brief Construct a new SimStageWithHistory object. Will create a new SimStageWithHistory if one does not exist
     *
     * @param usdStageId the stageId to associate with the SimStageWithHistory
     * @param historyFrameCount the number of frames to store
     * @param simPeriod the frame rate of this stage
     * @param withCuda should cuda be enabled
     */
    SimStageWithHistory(UsdStageId usdStageId, size_t historyFrameCount, FabricTime simPeriod,  omni::fabric::GpuComputeType computeType =  omni::fabric::GpuComputeType::eNone);
    /**
     * @brief Constructs a new SimStageWithHistory object that will point to an existing stage
     * but will not create one if one does not exist
     *
     * @param usdStageId  the stageId associated with the existing SimStageWithHistory
     */
    SimStageWithHistory(UsdStageId usdStageId);

    SimStageWithHistory();
    SimStageWithHistory(SimStageWithHistory& other);
    SimStageWithHistory& operator=(const SimStageWithHistory& other);
    SimStageWithHistory(SimStageWithHistory&& other);
    SimStageWithHistory& operator=(SimStageWithHistory&& other);

    ~SimStageWithHistory();

    /**
     * @brief Get the associated USD StageId
     *
     * @return the UsdStageID
     */
    UsdStageId getUsdStageId() const;

    /**
     * @brief Get the SimStageWithHistory's Id
     *
     * @return the simStageWithHistory
     */
    SimStageWithHistoryId getId() const;

    FabricId getWorkingFabricId() const;

    void setFrameNumber(int64_t simFrameNumber);
    int64_t getFrameNumber() const;

    FabricTime getFrameTime() const;

        /**
     * @brief Get the Sim Period
     *
     * @return the sim period as a rational time
     */

    FabricTime getSimPeriod() const;
    /**
     * @brief Get the Frame History Count
     *
     * @return the number of history frames
     */

    size_t getFrameHistoryCount() const;
    /**
     * @brief Get the Latest Frame id
     *
     * @return the latest frame Time as a Rational Time
     */
    FabricTime getLatestFrame() const;

    void flushToRingBuffer();

    /**
     * @brief Obtains the current simulation frame and ring buffer slot that will be used when flushing to ring buffer
     *
     * @param[out] simFrameNumber the simulation frame number we are writting the data for
     * @param[out] writeSlot the simStageWithHistory ring buffer slot we will be writing to
     */
    void getWriteParameters(int64_t& simFrameNumber, int64_t& writeSlot);

    /**
     * @brief Acquires write locks to the ring buffer slot relating to the current simulation frame
     *
     * @param[out] lockedSnapshot the snapshot of the paramaters relating to the simStageWithHistory ring buffer slot we
     * locked
     */
    void exclusiveAcquireAndInitRingBufferSlotForCurrentSimStage(SimStageWithHistoryLockSnapshot& lockedSnapshot);

    /**
     * @brief Same as @see flushToRingBuffer, but instead keeps the exclusive write lock on the ring buffer slot
     * relating to the current simulation
     *
     */
    void flushToRingBufferAlreadyLocked();

    /**
     * @brief unlock previous locked ring buffer slots relating to the current simulation frame
     *
     * @param[in] lockedSnapshot the previously aquired snapshot
     */
    void unlock(SimStageWithHistoryLockSnapshot& lockedSnapshot);

    void prefetchPrimFromUsdStage(const Path& path);

    /**
     * @brief Creates a new snapshot for the current simStageWithHistory
     *
     * @return StageWithHistorySnapshot
     */
    StageWithHistorySnapshot saveSnapshot();

    /**
     * @brief Delete a snapshot
     *
     * @param snapshotId the snapshot to be deleted
     * @return Whether or not the deletion was successful
     */
    bool deleteSnapshot(size_t snapshotId);

    /**
     * @brief reset the current SimStageWithHistory to the snapshot state
     *
     * @param snapshotId The snapshot to restore from.
     * @return whether or not the restoration succeded
     */
    bool restoreFromSnapshot(size_t snapshotId);
};

} // namespace fabric
} // namespace omni


#include <omni/fabric/stage/impl/SimStageWithHistory.inl>
