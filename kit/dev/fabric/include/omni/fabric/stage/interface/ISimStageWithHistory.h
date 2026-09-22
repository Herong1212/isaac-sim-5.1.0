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

#include <omni/fabric/core/AttrNameAndType.h>
#include <omni/fabric/core/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/Ordered_Set.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/interface/IPath.h>

#include <stdint.h>

namespace omni
{
namespace fabric
{

struct ISimStageWithHistory
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::ISimStageWithHistory", 0, 2);

    /** @brief gets or Creates a new SimStageWithHistory
     * This is a ref counted object internally and any getOrCreate call must
     * be matched by a destroy call
     *
     * @usdStageId[in] The identifier for the stage
     * @historyFrameCount[in] the size of the ring buffer for the simStage
     * @simPeriod[in] how often the ring buffer is expected to be incremented.
     * @computeType[in] the backing hardware resource type for GPU usage.
     */
    SimStageWithHistoryId(CARB_ABI* getOrCreate)(UsdStageId stageId,
                                                 size_t historyFrameCount,
                                                 FabricTime simPeriod,
                                                 GpuComputeType computeType);

    /** @brief get the simStageWithHistory
     * this call will increment the ref counter if the SimStageWithHistory exists
     *
     * @usdStageId[in] The identifier for the stage
     *
     */
    SimStageWithHistoryId(CARB_ABI* get)(UsdStageId usdStageId);


    /** @brief  Legacy call that is now a synonym for the newer release call.
     *    See release but do not use going forward.
     */
    CARB_DEPRECATED("Do not use - use release instead")
    void(CARB_ABI* destroy)(UsdStageId usdStageId);
    //
    // Create a snapshot of the simStageWithHistory for the usdStageId, this currently just resets
    // the stage in progress, but it probably should be extended to copy the entire ringbuffer if we intend to
    // so anything other than reset to the start frame.
    //
    StageWithHistorySnapshot(CARB_ABI* saveSnapshot)(UsdStageId usdStageId);

    bool(CARB_ABI* deleteSnapshot)(UsdStageId usdStageId, size_t snapshotId);

    bool(CARB_ABI* restoreFromSnapshot)(UsdStageId usdStageId, size_t snapshotId);

    // TODO: Should we have setters for these as well?  Would the side effects be weird?
    FabricTime(CARB_ABI* getSimPeriod)(UsdStageId usdStageId);
    size_t(CARB_ABI* getFrameHistoryCount)(UsdStageId usdStageId);

    // For multi-process replication. Stores the link between the stage id on the master process and the local stage id.
    void(CARB_ABI* setStageIdMapping)(UsdStageId usdStageIdMaster, UsdStageId usdStageIdLocal);

    CARB_DEPRECATED("Use the change tracker interface")
    ListenerId(CARB_ABI* createListener)();


    /** @brief Get the last frame that was written to the SimStageWithHistory
     *
     * @usdStageId[in] The identifier for the stage
     *
     * @return the time, and period of the last valid data written to the SimStageWithHistory
     *
     */
    FabricTime(CARB_ABI* getLatestFrame)(UsdStageId usdStageId);

    UsdStageId(CARB_ABI* getLocalStageId)(UsdStageId usdStageIdMaster);

    /** @brief release the simStageWithHistory acquired by get. If the ref count is reduced to zero
     * will delete the associated SimStageWithHistory
     *
     * @usdStageId[in] The identifier for the stage
     *
     */
    void(CARB_ABI* release)(UsdStageId stageId);

    /** @brief check if a simStageWithHistory currently exists for the given stage id
     *
     * @usdStageId[in] the indentifer for the stage
     *
     * @return true if the there is currently a SimStageWithHistory associate with the stageId
     * Note: Existence is only a momentary snap shot. If another process deletes the stage after the check
     * nothing prevents that.
     */
    bool(CARB_ABI* exists)(UsdStageId stageId);
};

enum class RingbufferReplicationFlags : uint32_t
{
    SkipRingBufferSlotLocking = (1 << 0), ///< skip locks when reading/writing to the ring buffer slots.
                                          ///< If this flag is passed, you must have acquired these locks
                                          ///< exclusively before calling replication
    Empty = 0x0,
};

}
}
