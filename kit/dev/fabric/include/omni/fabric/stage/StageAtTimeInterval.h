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
#include <carb/logging/Log.h>
#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/fabric/PrimChanges.h>
#include <omni/fabric/Type.h>

#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/stage/SimStageWithHistory.h>

#include <gsl/span>

#include <map>
#include <stdint.h>

namespace omni
{
namespace fabric
{

/**
 * @invariant arrayBytes.size() must be a multiple of bytesPerElement
 */
class ConstArrayAsBytes
{
public:
    gsl::span<const gsl::byte> arrayBytes;
    size_t bytesPerElement;
    Type elementType;
};

// The following two classes, StageAtTime and StageAtTimeInterval
// are used by reader threads to read the history. StageAtTime is
// used when the state of a stage is needed at a particular point in time.
// StageAtTimeInterval is used when we need all the stage history in a given time
// window.
//
// There can be multiple threads reading the history buffer, for example
// multiple sensor renderers running at different rates. We use shared locks
// to allow multiple threads to read the same frame of history.
//
// StageAtTimeInterval takes an RAII approach to locking, constructing one locks
// a range of slots for reading, and destructing unlocks them.
class StageAtTimeInterval
{
    StageAtTimeIntervalId m_stageAtTimeInterval;
    omni::fabric::IStageAtTimeInterval* m_interface;
    std::vector<FabricTime> m_timeSamples;
    static omni::fabric::IStageAtTimeInterval* sIStageAtTimeInterval();

public:
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
    static bool getIntervalParameters(SimStageWithHistoryId simStageWithHistoryId,
                                      FabricTime beginTime,
                                      FabricTime endTime,
                                      StageAtTimeIntervalFlags flags,
                                      int64_t& beginFrame,
                                      int64_t& endFrame,
                                      int64_t& startRingbufferSlot,
                                      int64_t& endRingbufferSlot,
                                      int64_t& slotCount);


    // The constructor locks frames of history
    StageAtTimeInterval(SimStageWithHistory& simStageWithHistory,
                        FabricTime beginTime,
                        FabricTime endTime,
                        StageAtTimeIntervalFlags flags = StageAtTimeIntervalFlags::Empty);

    StageAtTimeInterval(SimStageWithHistoryId simStageWithHistoryId,
                        FabricTime beginTime,
                        FabricTime endTime,
                        StageAtTimeIntervalFlags flags = StageAtTimeIntervalFlags::Empty);

    StageAtTimeInterval(RingBufferId ringBufferId, FabricTimeWindow window);

    StageAtTimeInterval(RingBufferId ringBufferId,
                        FabricTime beginTime,
                        FabricTime endTime,
                        StageAtTimeIntervalFlags flags = StageAtTimeIntervalFlags::Empty);
    
    StageAtTimeInterval();
    StageAtTimeInterval(const StageAtTimeInterval& other);
    StageAtTimeInterval& operator=(const StageAtTimeInterval& other);
    StageAtTimeInterval(StageAtTimeInterval&& other);
    StageAtTimeInterval& operator=(StageAtTimeInterval&& other);


    // Unlocks elements to allow them to be reused.
    ~StageAtTimeInterval();

    StageAtTimeIntervalId getId();

    // Get timestamps of locked elements
    const std::vector<FabricTime>& getTimestamps() const;

    size_t getTimeSampleCount() const;

    // TODO: replace with an iterator for iterating over bucket names
    void printBucketNames() const;

    /** @brief checks if a prim exists in Fabric
     *
     * @param[in] path the prim
     * @return a vector of samples containing true if the prim exists in that sample
     */
    std::vector<uint8_t> primExists(const Path& path) const;

    /** @brief checks if a prim with the given attribute exists in Fabric
     *
     * @param[in] path the prim
     * @param[in] attr the attribute
     * @return a vector of samples containing true if that prim with that attribute exists in that sample
     */
    std::vector<uint8_t> attributeExists(const Path& path, const Token& attr) const;


    // findPrims() finds prims that have all the attributes in "all", and any
    // of the attributes in "any", and none of the attributes in "none".
    // The attributes of the resulting prims can be accessed as piecewise
    // contiguous arrays, using getAttributeArray() below, which is typically
    // faster than calling getAttribute for each prim.
    PrimBucketList findPrims(const omni::fabric::set<AttrNameAndType>& all,
                             const omni::fabric::set<AttrNameAndType>& any = {},
                             const omni::fabric::set<AttrNameAndType>& none = {}) const;

    ValidMirrors getAttributeValidBits(const PathC& path, const TokenC& attrName) const;

    // Get values of locked elements
    template <typename T>
    std::vector<const T*> getAttributeRd(const Path& path, const Token& attrName) const;

    // Get GPU pointer and size of locked elements
    template <typename T>
    std::vector<const T*> getAttributeRdGpu(const Path& path,
                                            const Token& attrName,
                                            int deviceId = 0,
                                            PtrToPtrKind wherePtr = PtrToPtrKind::eCpuPtrToGpuPtr) const;

    // Get the size of an array attribute. When writing CPU code, it isn't
    // normally necessary to use this method, as getArrayAttribute returns a
    // span containing the data pointer and the size.
    // However, when writing mixed CPU/GPU code it is wasteful to copy the
    // array data from GPU to CPU when just the size is required, so use this
    // method in that case.
    std::vector<size_t> getArrayAttributeSize(const Path& path, const Token& attrName) const;

    /**
     * @brief Get an array-valued attribute for reading from a single prim
     *
     * @param path The path of the prim
     * @param attrName The name of the attribute
     *
     * @return a vector of array spans, one for each time sample within the current StageAtTimeInterval
     */
    template <typename T>
    std::vector<gsl::span<const T>> getArrayAttributeRd(const Path& path, const Token& attrName) const;

    /**
     * @brief Get an array-valued attribute as bytes for reading from a single prim.
     *        This is useful for converting to VtValue
     *
     * @param path The path of the prim
     * @param attrName The name of the attribute
     *
     * @return a vector of array spans, one for each time sample within the
     *         current StageAtTimeInterval
     */
    std::vector<ConstArrayAsBytes> getArrayAttributeRawRd(const Path& path, const Token& attrName) const;


    // getAttributeArray(primBucketList, index, attrName) returns for each
    // timesample, a read-only, contiguous array of the values of attribute
    // "attrName" for each prim of bucket "index" of "primBucketList".
    // "index" must be in the range [0..primBucketList.getBucketCount())
    template <typename T>
    std::vector<gsl::span<const T>> getAttributeArrayRd(const PrimBucketList& primBucketList,
                                                        size_t primBucketListIndex,
                                                        const Token& attrName) const;

    template <typename T>
    std::vector<gsl::span<const T>> getAttributeArrayRdGpu(const PrimBucketList& primBucketList,
                                                           size_t primBucketListIndex,
                                                           const Token& attrName,
                                                           int deviceId = 0) const;
    template <typename T>
    std::vector<std::vector<gsl::span<const T>>> getArrayAttributeArrayRd(const PrimBucketList& primBucketList,
                                                                          size_t primBucketListIndex,
                                                                          const Token& attrName) const;

    /**
     * @brief Read a raw byte representation for a given attribute from a given bucket. This is useful for doing things
     * such as batched type conversions.
     *
     * @param primBucketList the list of buckets
     * @param primBucketListIndex the specific bucket to search
     * @param attrName the token describing the desired attribute
     *
     * @return a vector of byte arrays, one for each time sample within the current StageAtTimeInterval
     */
    std::vector<gsl::span<const char>> getAttributeArrayRawRd(const PrimBucketList& primBucketList,
                                                              size_t primBucketListIndex,
                                                              const Token& attrName) const;

    // getPathArray(primBucketList, index) returns for each timesample a
    // read-only contiguous array of the paths of the prims of bucket "index"
    // of "primBucketList".
    // "index" must be in the range [0..primBucketList.getBucketCount())
    // The reason a separate path array is returned per sample is that prims
    // can be added and deleted from frame to frame, and we need to check which
    // prim a sample corresponds to when interpolating.
    std::vector<gsl::span<const Path>> getPathArray(const PrimBucketList& primBucketList,
                                                    size_t primBucketListIndex) const;

    /**
     * @brief Get a Connection on a target prim
     *
     * @param path the target prim
     * @param connectionName the connection name
     * @return a vector of read only pointers to connections
     */
    std::vector<const Connection*> getConnectionRd(const Path& path, const Token& connectionName) const;

    // Get the number of attributes for a given bucket.
    std::vector<size_t> getAttributeCounts(const PrimBucketList& primBucketList, size_t primBucketListIndex) const;

    // Get the name and type of each attribute for a given bucket.
    std::pair<std::vector<std::vector<Token>>, std::vector<std::vector<Type>>> getAttributeNamesAndTypes(
        const PrimBucketList& primBucketList, size_t primBucketListIndex) const;


    size_t getAttributeCount(const PrimBucketList& primBucketList,
                                          size_t primBucketListIndex,
                                          size_t timesampleIndex) const;

    std::pair<std::vector<Token>, std::vector<Type>> getAttributeNamesAndTypes(
        const PrimBucketList& primBucketList, size_t primBucketListIndex, size_t timesampleIndex) const;

    /**
     * @brief write the current data for this StageReaderWriter to the specified UsdStage
     *        this will write all attributes at the currentTime in getFrameNumber()
     *
     * @param usdStageId Valid usdStage in the stage cache
     *
     * @return none
     */
    void exportUsd(UsdStageId usdStageId) const;

    /** @brief Write a cache file to disk at a specified location
     *
     * @note Many parameters to this function are optional
     * @note This currently only writes the first time in the interval
     *
     * @file[in The location the file is desired to be written to
     * @workingBuffer[in] [Optional] In order to avoid costly reallocations
     *                    the code will attempt to re-use the memory at the buffer
     *                    location if it is large enough. If the buffer isn't larg
     *                    enough the cost of allocation, and re-traversal may be paid
     * @workingBufferSize[in] [Optional] If workingBuffer is non null, then this desrcibes the length
     *                        of the buffer
     * @return The amount of data needed to serialize the cache, a return value of 0 indicates an error
     *
     */
    uint64_t writeCacheToDisk(const char* file, uint8_t* workingBuffer, uint64_t workingBufferSize) const;

    /** @brief Add a ref count to any data backed by the StageAtTimeIntercal
     *
     * @note The ref count will not enforce any behavior currently, but will
     *       print a warning if backing data is deleted before all ref counts
     *       are cleared
     *
     * @return None
     *
     */
    void addRefCount();

    /** @brief Remove a ref count from an existing timeInterval
     *
     * @return True if ref count was removed successfully, failure conditions may
     *         include
     *           (1) StageAtTimeInterval doesn't exist
     *           (2) RefCount was already 0
     */
    bool removeRefCount();

    /** @brief Query ref count for a stage at time
     *
     * @note A stage at time might be represented by multiple actual data sources
     *       in that case we return the largest refcount of all the data sources
     *
     * @return number of reference counts
     */
    unsigned int getRefCount();
};

} // namespace fabric
} // namespace omni

#include <omni/fabric/stage/impl/StageAtTimeInterval.inl>
