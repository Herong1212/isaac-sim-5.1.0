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

/** @brief The Serializer interface provides the C-ABI compatible functions for
 *         working with all serialization of SWH and workflows. This covers
 *            (1) In-memory serialization/deserialization
 *            (2) Serialization to Disk and From
 *            (3) Functions to support replication based on serialization
 *         Because of the nature of SWH there are multiple places one might want to
 *         actually serialize the cache from, we provide some convenience functions
 *         that wrap this up, but also the direct functionality to serialize a
 *         PathToAttributesMap directly to/from a buffer for convenience.
 *
 */
struct ISerializer
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::ISerializer", 0, 3);

    //
    // deprecated for more appropriately named serializeRingBuffer
    //
    uint64_t(CARB_ABI* serializeStage)(SimStageWithHistoryId simStageWithHistoryId,
                                       size_t slot,
                                       uint8_t* dest,
                                       size_t destSize);

    //
    // deprecated for more appropriately named deserializeIntoRingBuffer
    //
    bool(CARB_ABI* deserializeStage)(SimStageWithHistoryId simStageWithHistoryId,
                                     size_t slot,
                                     const uint8_t* input,
                                     const size_t inputSize,
                                     int64_t simFrameNumber,
                                     omni::fabric::FabricTime simFrameTime);

    /** @brief Attempt to serialize the stage into the provided buffer. This function
     *         is intended to be used when you want to serialize all the data within a
     *         ring buffer entry, however this is often more data than needs to be sent.
     *
     * @stage[in] The SimStageWithHistory with the ring buffer to be serialized
     * @slot[in] The slot from the ring buffer to send
     * @dest[in/out] Pointer to buffer to be written to, will start writing to head
     *       of pointer. dest will be left pointing to the point after the last write
     * @destSize Size of buffer that was allocated for the data (in bytes)
     *
     * @return Number of bytes written success is determined by (return <= @destSize)
     *
     *
     * @invariant It is safe to write to any memory within[dest, dest+size] for the
     *            duration of the function call.
     *
     * @note If the cache will not fit into the size of memory allocated in
     *       @dest then it will stop writing, but continue to run the serialize
     *       algorithm to calculate the actual amount of data that needs to be
     *       written
     *
     */
    uint64_t(CARB_ABI* serializeRingBuffer)(SimStageWithHistoryId simStageWithHistoryId,
                                            size_t slot,
                                            uint8_t* dest,
                                            size_t destSize);

    /** @brief Given a buffer that has the serialized version of a cache written
     *         using the serialize function, this function will override all the data
     *         in the ringbuffer at the requested slot with the data encoded in the
     *         buffer. This function will only succeed if the SimStageWithHistory that
     *         is passed in was created from the same UsdStage (opened at the same root layer)
     *         that was used to create the original serialized cache.
     *
     *
     * @stageWithHistoryId[in] The stage to write the data to
     * @slot[in] The index in the ring buffer to pull to
     * @input[in] Pointer to buffer of data containing serialized cache
     * @inputSize[in] Size of data in the buffer
     * @simFrameNumber[in] The frame of the simulation to set the ring buffer entry to
     * @simFrameTime[in] The simFrame time to set the ring buffer to
     *
     * @return True if buffer was successfully de-serialized
     *
     * @TODO: whould we care that it came from the same version of the USD file?
     */
    bool(CARB_ABI* deserializeIntoRingBuffer)(SimStageWithHistoryId simStageWithHistoryId,
                                              size_t slot,
                                              const uint8_t* input,
                                              const size_t inputSize,
                                              int64_t simFrameNumber,
                                              omni::fabric::FabricTime simFrameTime);

    /** @brief Replicate the ring buffers from the master to the workers when running
     *         multiple processes. Data is serialized into buffers allocated and broadcast
     *         by Realm, followed by deserialization into the remote ring buffers. This
     *         function is synchronous, i.e., the remote Fabrics have finished updating
     *         when this function returns.
     *  @param[in] flags to control ring buffer replication
     */
    void(CARB_ABI* replicateRingBuffers)();

    /** @brief Same as @see replicateRingBuffers, allowing extra flags to control the replication process
     */
    void(CARB_ABI* replicateRingBuffersWithFlags)(RingbufferReplicationFlags flags);
};

} // namespace fabric
} // namespace omni
