// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/API.h>
#include <omni/fabric/core/AttrNameAndType.h>
#include <omni/fabric/core/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/Ordered_Set.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/interface/IPath.h>

#include <omni/fabric/stage/IdTypes.h>

#include <stdint.h>

namespace omni
{
namespace fabric
{

enum class StageAtTimeIntervalFlags : uint32_t
{
    IncludeEndTime = (1 << 0), ///< Include end time in time range
    WaitForReadLock = (1 << 1), ///< Instead of a try lock, use a blocking read lock
    Empty = 0x0,
};

struct IStageAtTimeInterval
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IStageAtTimeInterval", 0, 7);

    // DEPRECATED: use create() passing StageAtTimeIntervalFlags instead
    StageAtTimeIntervalId(CARB_ABI* create)(SimStageWithHistoryId simStageWithHistoryId,
                                            FabricTime beginTime,
                                            FabricTime endTime,
                                            bool includeEndTime);

    FABRIC_ABI_DUMMY(1)

    size_t(CARB_ABI* getTimesampleCount)(StageAtTimeIntervalId stageAtTimeIntervalId);
    void(CARB_ABI* getTimestamps)(FabricTime* out, size_t outCount, StageAtTimeIntervalId stageAtTimeIntervalId);

    // Single attribute accessor
    CARB_DEPRECATED("Use getAttributeRd(), which returns a span with type instead.")
    size_t(CARB_ABI* getAttributeRd_DEPRECATED)(
        const void** out, size_t outCount, StageAtTimeIntervalId stageAtTimeIntervalId, PathC path, TokenC attrName);

    // Attribute SOA accessors
    PrimBucketListId(CARB_ABI* findPrims)(StageAtTimeIntervalId stageAtTimeIntervalId,
                                          const omni::fabric::set<AttrNameAndType>& all,
                                          const omni::fabric::set<AttrNameAndType>& any,
                                          const omni::fabric::set<AttrNameAndType>& none);

    CARB_DEPRECATED("Use getAttributeArrayRd(), which returns a span with type instead.")
    void(CARB_ABI* getAttributeArrayRd_DEPRECATED)(ConstSpanC* out,
                                        size_t outCount,
                                        StageAtTimeIntervalId stageAtTimeIntervalId,
                                        PrimBucketListId primBucketList,
                                        size_t primBucketListIndex,
                                        TokenC attrName);

    CARB_DEPRECATED("Use getArrayAttributeArrayWithSizesRd(), which returns a span with type instead.")
    void(CARB_ABI* getArrayAttributeArrayWithSizesRd_DEPRECATED)(ConstArrayPointersAndSizesC* out,
                                                      size_t outCount,
                                                      StageAtTimeIntervalId stageAtTimeIntervalId,
                                                      PrimBucketListId primBucketList,
                                                      size_t primBucketListIndex,
                                                      TokenC attrName);

    void(CARB_ABI* getPathArray)(ConstPathCSpan* out,
                                 size_t outCount,
                                 StageAtTimeIntervalId stageAtTimeIntervalId,
                                 PrimBucketListId primBucketList,
                                 size_t primBucketListIndex);

    void(CARB_ABI* printBucketNames)(StageAtTimeIntervalId stageAtTimeIntervalId);

    void(CARB_ABI* exportUsd)(StageAtTimeIntervalId stageAtTimeIntervalId, UsdStageId usdStageId);

    FabricTime(CARB_ABI* getSimPeriod)(UsdStageId usdStageId);

    void(CARB_ABI* getAttributeCounts)(StageAtTimeIntervalId stageAtTimeIntervalId,
                                       PrimBucketListId primBucketList,
                                       size_t primBucketListIndex,
                                       size_t timesamples,
                                       size_t* outCounts);

    void(CARB_ABI* getAttributeNamesAndTypes)(StageAtTimeIntervalId stageAtTimeIntervalId,
                                              PrimBucketListId primBucketList,
                                              size_t primBucketListIndex,
                                              size_t timesamples,
                                              const size_t* attributeCounts,
                                              Token** outNames,
                                              Type** outTypes);

    size_t(CARB_ABI* getAttributeCountForTimesample)(StageAtTimeIntervalId stageAtTimeIntervalId,
                                                     PrimBucketListId primBucketList,
                                                     size_t primBucketListIndex,
                                                     size_t timesampleIndex);

    void(CARB_ABI* getAttributeNamesAndTypesForTimesample)(StageAtTimeIntervalId stageAtTimeIntervalId,
                                                           PrimBucketListId primBucketList,
                                                           size_t primBucketListIndex,
                                                           size_t timesampleIndex,
                                                           size_t attributeCount,
                                                           Token* outNames,
                                                           Type* outTypes);

    void(CARB_ABI* getArrayAttributeWithSizeRd)(ConstSpanWithTypeC* out,
                                                size_t outCount,
                                                StageAtTimeIntervalId stageAtTimeIntervalId,
                                                omni::fabric::PathC path,
                                                omni::fabric::TokenC attrName);
    /** @brief Write a cache file to disk at a specified location
     *
     * @note Many parameters to this function are optional
     * @note This currently only writes the first time in the interval
     * @stageAtTimeIntervalId[in] The stage at time to be written to disk
     * @file[in The location the file is desired to be written to
     * @workingBuffer[in] [Optional] In order to avoid costly reallocations
     *                    the code will attempt to re-use the memory at the buffer
     *                    location if it is large enough. If the buffer isn't larg
     *                    enough the cost of allocation, and re-traversal may be paid
     * @workingBufferSize[in] [Optional] If workingBuffer is non null, then this desrcibes the length
     *                        of the buffer
     * @return The amount of data needed to serialize the cache, if a working buffer is provided return value greater
     * than bufferSize indicates an error.
     *
     */
    uint64_t(CARB_ABI* writeCacheToDisk)(StageAtTimeIntervalId stageAtTimeIntervalId,
                                         const char* file,
                                         uint8_t* workingBuffer,
                                         uint64_t workingBufferSize);
    /** @brief Add a ref count to any data backed by the StageAtTimeIntercal
     *
     * @note The ref count will not enforce any behavior currently, but will
     *       print a warning if backing data is deleted before all ref counts
     *       are cleared
     *
     * @stageAtTimeIntervalId[in] The stage at time tracked for the ref counting
     *
     * @return None
     *
     */
    void(CARB_ABI* addRefCount)(StageAtTimeIntervalId stageAtTimeIntervalId);

    /** @brief Remove a ref count from an existing timeInterval
     *
     *
     * @stageAtTimeIntervalId[in] The stage at time tracked for the ref counting
     *
     * @return True if ref count was removed successfully, failure conditions may
     *         include
     *           (1) StageAtTimeInterval doesn't exist
     *           (2) RefCount was already 0
     *
     */
    bool(CARB_ABI* removeRefCount)(StageAtTimeIntervalId stageAtTimeIntervalId);

    /** @brief Query ref count for a stage at time
     *
     * @note A stage at time might be represented by multiple actual data sources
     *       in that case we return the largest refcount of all the data sources
     *
     * @stageAtTimeIntervalId[in] The stage at time tracked for the ref counting
     *
     * @return number of reference counts
     *
     */
    unsigned int(CARB_ABI* getRefCount)(StageAtTimeIntervalId stageAtTimeIntervalId);

    // Access GPU Array attribute
    void(CARB_ABI* getAttributeArrayRdGpu)(ConstSpanC* out,
                                           size_t outCount,
                                           StageAtTimeIntervalId stageAtTimeIntervalId,
                                           PrimBucketListId primBucketList,
                                           size_t primBucketListIndex,
                                           TokenC attrName);
    // Access GPU pointer attribute
    CARB_DEPRECATED("Use getAttributeRdGpu(), which returns a span with type instead.")
    void(CARB_ABI* getAttributeRdGpu_DEPRECATED)(ConstSpanC* out,
                                                 size_t outCount,
                                                 StageAtTimeIntervalId stageAtTimeIntervalId,
                                                 PathC path,
                                                 TokenC attrName);
    // Access GPU pointer attribute
    CARB_DEPRECATED("Use getAttributeRdGpuMemType(), which returns a span with type instead.")
    void(CARB_ABI* getAttributeRdGpuMemType_DEPRECATED)(ConstSpanC* out,
                                             size_t outCount,
                                             StageAtTimeIntervalId stageAtTimeIntervalId,
                                             PathC path,
                                             TokenC attrName,
                                             PtrToPtrKind wherePtr);
    // Get array size, useful for GPU attributes
    size_t(CARB_ABI* getArrayAttributeSize)(
        size_t* out, size_t outCount, StageAtTimeIntervalId stageAtTimeIntervalId, PathC path, TokenC attrName);
    /** @brief Returns which mirrors of the array are valid: CPU, GPU, etc.
     *
     * @stageAtTimeIntervalId[in] The stage to query validity from
     * @path[in] The prim path
     * @attrName[in] The attribute name
     *
     * @return ValidMirrors struct
     *
     */
    ValidMirrors(CARB_ABI* getAttributeValidBits)(StageAtTimeIntervalId stageAtTimeIntervalId,
                                                  const PathC& path,
                                                  const TokenC& attrName);

    /**
     * @brief  Retrieves a connection attribute from a prim
     *
     * @param[out] the connection samples found
     * @param[in] the number of connection samples desired.
     * @param[in] stageId the stage to work on
     * @param[in] path the prim to fetch the connection from
     * @param[in] connectionName the name of the connection attribute to fetch
     * @return a read only pointer to the connection
     */
    void(CARB_ABI* getConnectionRd)(const void** out,
                                    size_t outCount,
                                    StageAtTimeIntervalId stageAtTimeIntervalId,
                                    PathC path,
                                    TokenC connectionName);

    /** @brief checks if a prim exists in Fabric
     *
     * @param[out] out an array of samples that indicate if the prim exists in that sample
     * @param[in] outCount the size of the out, should match the number of samples in the timeinterval
     * @param[in] stageId the stage id to check
     * @param[in] path the prim
     * @return true if the prim exists in fabric
     */
    void(CARB_ABI* primExists)(bool** out, size_t outCount, StageAtTimeIntervalId stageId, PathC path);

    /** @brief checks if a prim with the given attribute exists in Fabric
     *
     * @param[out] out an array of samples that indicate if the prim exists in that sample
     * @param[in] outCount the size of the out, should match the number of samples in the timeinterval
     * @param[in] stageId the stage id to check
     * @param[in] path the prim
     * @param[in] attri the attribute
     * @return true if the prim with attribute exists in fabric
     */
    void(CARB_ABI* attributeExists)(bool** out, size_t outCount, StageAtTimeIntervalId stageId, PathC path, TokenC attr);

    FABRIC_ABI_DUMMY(2)

    // MGPU versions of existing GPU functions that support specifying a particular device id on which the
    // attribute/array should be made available
    CARB_DEPRECATED("Use getAttributeArrayRdMGp(), which returns a span with type instead.")
    void(CARB_ABI* getAttributeArrayRdMGpu_DEPRECATED)(ConstSpanC* out,
                                            size_t outCount,
                                            StageAtTimeIntervalId stageAtTimeIntervalId,
                                            PrimBucketListId primBucketList,
                                            size_t primBucketListIndex,
                                            TokenC attrName,
                                            int deviceId);

    CARB_DEPRECATED("Use getAttributeRdMGpu(), which returns a span with type instead.")
    void(CARB_ABI* getAttributeRdMGpu_DEPRECATED)(ConstSpanC* out,
                                       size_t outCount,
                                       StageAtTimeIntervalId stageAtTimeIntervalId,
                                       PathC path,
                                       TokenC attrName,
                                       int deviceId);

    CARB_DEPRECATED("Use getAttributeRdMGpuMemType(), which returns a span with type instead.")
    void(CARB_ABI* getAttributeRdMGpuMemType_DEPRECATED)(ConstSpanC* out,
                                              size_t outCount,
                                              StageAtTimeIntervalId stageAtTimeIntervalId,
                                              PathC path,
                                              TokenC attrName,
                                              PtrToPtrKind wherePtr,
                                              int deviceId);

    /**
     * @brief Calculate several parameters relating to the time range passed in
     *
     * @param[in] SimStageWithHistoryId the stage id to use
     * @param[in] beginTime start of the time range
     * @param[in] beginTime end of the time range
     * @param[in] flags for the time range
     * @param[out] beginFrame the first simulation frame of the time range
     * @param[out] endFrame the last simulation frame of the time range
     * @param[out] startRingbufferSlot the first ring buffer slot for the time range
     * @param[out] endRingBufferSlot the last ring buffer slot for the time range
     * @param[out] slotCount the ring buffer slot count for the time range
     * @return true if obtaining the values succeeded
     */
    bool(CARB_ABI* getIntervalParameters)(SimStageWithHistoryId simStageWithHistoryId,
                                          FabricTime beginTime,
                                          FabricTime endTime,
                                          StageAtTimeIntervalFlags flags,
                                          int64_t& beginFrame,
                                          int64_t& endFrame,
                                          int64_t& startRingbufferSlot,
                                          int64_t& endRingbufferSlot,
                                          int64_t& slotCount);

    /**
     * @brief Create a StageAtTimeInterval for the given time range
     *
     * @param[in] SimStageWithHistoryId the stage id to use
     * @param[in] beginTime start of the time range
     * @param[in] beginTime end of the time range
     * @param[in] flags to control the creation
     */
    StageAtTimeIntervalId(CARB_ABI* createWithFlags)(SimStageWithHistoryId simStageWithHistoryId,
                                                     FabricTime beginTime,
                                                     FabricTime endTime,
                                                     StageAtTimeIntervalFlags flags);

    /**
     * @brief Create a StageAtTimeInterval for the given time range for a FabricRingBuffer
     *
     * @param[in] ringBufferId the ringBuffer  to use
     * @param[in] window A FabricTimeWindow containing the start and end times plus the end point conditions
     */
    StageAtTimeIntervalId(CARB_ABI* createFromRingBuffer)(RingBufferId ringBufferId, FabricTimeWindow window);
    
    // These are on the stage at time interval and not related to the addRefCount calls above
    void (CARB_ABI* addRef)(StageAtTimeIntervalId stageId);
    void (CARB_ABI* release)(StageAtTimeIntervalId stageId);

    TypeC (CARB_ABI* getAttributeRd)(
        const void** out, size_t outCount, StageAtTimeIntervalId stageAtTimeIntervalId, PathC path, TokenC attrName);

    void(CARB_ABI* getAttributeArrayRd)(ConstSpanWithTypeC* out,
                                        size_t outCount,
                                        StageAtTimeIntervalId stageAtTimeIntervalId,
                                        PrimBucketListId primBucketList,
                                        size_t primBucketListIndex,
                                        TokenC attrName);

    void(CARB_ABI* getArrayAttributeArrayWithSizesRd)(ConstArrayPointersAndSizesWithTypeC* out,
                                                      size_t outCount,
                                                      StageAtTimeIntervalId stageAtTimeIntervalId,
                                                      PrimBucketListId primBucketList,
                                                      size_t primBucketListIndex,
                                                      TokenC attrName);

    void(CARB_ABI* getAttributeRdGpu)(ConstSpanWithTypeC* out,
                                      size_t outCount,
                                      StageAtTimeIntervalId stageAtTimeIntervalId, 
                                      PathC path,
                                      TokenC attrName);

    void(CARB_ABI* getAttributeRdMGpu)(ConstSpanWithTypeC* out,
                                       size_t outCount,
                                       StageAtTimeIntervalId stageAtTimeIntervalId,
                                       PathC path,
                                       TokenC attrName,
                                       int deviceId);

    void(CARB_ABI* getAttributeRdGpuMemType)(ConstSpanWithTypeC* out,
                                             size_t outCount,
                                             StageAtTimeIntervalId stageAtTimeIntervalId,
                                             PathC path,
                                             TokenC attrName,
                                             PtrToPtrKind wherePtr);

    void(CARB_ABI* getAttributeArrayRdMGpu)(ConstSpanWithTypeC* out,
                                            size_t outCount,
                                            StageAtTimeIntervalId stageAtTimeIntervalId,
                                            PrimBucketListId primBucketList,
                                            size_t primBucketListIndex,
                                            TokenC attrName,
                                            int deviceId);

    void(CARB_ABI* getAttributeRdMGpuMemType)(ConstSpanWithTypeC* out,
                                              size_t outCount,
                                              StageAtTimeIntervalId stageAtTimeIntervalId,
                                              PathC path,
                                              TokenC attrName,
                                              PtrToPtrKind wherePtr,
                                              int deviceId);

};


// LEGACY SUPPORT FUNCTIONS TO USE AS WE TRANSITION TO HIDE FABRIC IMPL DETAILS

// DO NOT USE IN NEW CODE UNLESS ABSOLUTELY NECESARRY
// ALMOST ALL OF THIS WILL GO AWAY IN FAVOR OF THE UPCOMING QUERY INTERFACES

// DO NOT WRITE C++ WRAPPERS FOR THESE CALLS
struct IStageAtTimeIntervalLegacy
{
    CARB_PLUGIN_INTERFACE("omni::fabric::IStageAtTimeIntervalLegacy", 0, 1);

    FABRIC_ABI_DUMMY(1)

    // OM-108563 - accessor for the realm serialization event precondition
    void(CARB_ABI* getPrecondition)(StageAtTimeIntervalId stageAtTimeIntervalId, void** dataPtr);

};

} // namespace fabric
} // namespace omni
