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

#include <omni/fabric/core/AttrNameAndType.h>
#include <omni/fabric/core/FabricRingBuffer.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/Type.h>
#include <omni/fabric/core/interface/IPath.h>
#include <omni/fabric/core/interface/IToken.h>

#include <omni/fabric/stage/PrimBucketList.h>
#include <omni/fabric/stage/PrimChanges.h>
#include <omni/fabric/stage/StageAtTimeInterval.h>
#include <omni/fabric/stage/SimStageWithHistory.h>

#include <gsl/span>
#include <map>
#include <stdint.h>

#include <carb/cpp/Optional.h>
using carb::cpp::optional;

namespace omni
{
namespace fabric
{
// The comments in this file are intended to be read top to bottom, like a book.

// This file defines omni::fabric::SimStageWithHistory, an instance of which stores
// the current stage and a configurable number of frames of state history. It
// is thread safe, in the sense that the current state can be safely read and
// written in parallel with multiple threads reading the history. The class
// definition is towards the end of this file. We first define some basic types,
// a read/write accessor class for use by the main/game/sim thread, and two
// read-only accessor classes for use on render threads. These classes provide
// access to an interpolated state and a window of state history respectively.

// To specify paths, attribute names, and attribute types we use
// omni::fabric::Path, omni::fabric::Token and graph::Type types, rather than
// USD's SdfPath, TfToken and TfType. This allows us to access the stage and
// history without including USD headers.


// The main class is this file is SimStageWithHistory, which is defined towards
// the end of the file.
class SimStageWithHistory;

template <typename T>
class AttributeArrayResult;

// StageAtTime is used when the state of a stage is needed at
// a particular point in time, which may or may not be one of the times sampled
// in the history. If it is, then getAttributeRd returns the exact value sampled.
// If not, it linearly interpolates using the two closest samples in the history.
//
// StageAtTime takes an RAII approach to locking, constructing one
// locks one or two frames in the history (depending on whether interpolation
// is needed), and destructing unlocks them.

class StageAtTime
{
    // Invariants:
    // I0: if sampleTimes.size()==2, m_theta = (m_time - sampleTimes[0]) /
    //                                         (sampleTimes[1] - sampleTimes[0])
    //       where sampleTimes = m_historyWindow.getTimestamps()
    //
    //     In particular, m_theta increases linearly from 0 to 1 as m_time
    //     increases from sampleTimes[0] to sampleTimes[1]
    //
    // TODO: do we need to delay conversion from rational number to double?
    StageAtTimeInterval m_historyWindow;
    FabricTime m_time;
    double m_theta;
    size_t m_minSampleIdx;
    size_t m_maxSampleIdx;

    //TODO: What happens if t < start or t > end? 
    void computeTheta(FabricTime start, FabricTime end)
    {
        m_theta = omni::fabric::computeTheta(start, end, m_time);
    }

    void initInterpolation()
    {
        std::vector<FabricTime> sampleTimes = m_historyWindow.getTimestamps();

        // Find the two samples closest to the target time
        if (sampleTimes.size() > 2)
        {
            FabricTime minSample = sampleTimes.front();
            FabricTime maxSample = sampleTimes.back();
            m_minSampleIdx = 0;
            m_maxSampleIdx = sampleTimes.size()-1;

            for (size_t i = 0; i < sampleTimes.size(); ++i)
            {
                const FabricTime& time = sampleTimes[i];
                if (time <= m_time && minSample < time)
                {
                    m_minSampleIdx = i;
                    minSample = time;
                }
                if (m_time <= time && time < maxSample)
                {
                    m_maxSampleIdx = i;
                    maxSample = time;
                }
            }
            computeTheta(minSample, maxSample);
        }
        else if (sampleTimes.size() == 2)
        {
            m_minSampleIdx = 0;
            m_maxSampleIdx = 1;
            computeTheta(sampleTimes[0], sampleTimes[1]);
        }
        else if (sampleTimes.size() == 1)
        {
            m_minSampleIdx = 0;
            m_maxSampleIdx = 0;
            m_theta = 0.0;
        }
    }

public:
    // Locks one or two history elements for read.
    StageAtTime(SimStageWithHistory& simStageWithHistory, FabricTime time)
        : m_historyWindow(simStageWithHistory, time, time, StageAtTimeIntervalFlags::IncludeEndTime), m_time(time)
    {
        initInterpolation();
    }

    StageAtTime(SimStageWithHistoryId simStageWithHistoryId, FabricTime time)
        : m_historyWindow(simStageWithHistoryId, time, time, StageAtTimeIntervalFlags::IncludeEndTime), m_time(time)
    {
        initInterpolation();
    }

    StageAtTime(RingBufferId id, FabricTime time)
        : m_historyWindow(id, time, time, StageAtTimeIntervalFlags::IncludeEndTime), m_time(time)
    {
        initInterpolation();
    }

    StageAtTime(const FabricRingBuffer& ringBuf, FabricTime time)
        : m_historyWindow(ringBuf.getId(), time, time, StageAtTimeIntervalFlags::IncludeEndTime), m_time(time)
    {
        initInterpolation();
    }

    StageAtTime(const FabricRingBuffer& ringBuf, FabricTime time, FabricTime start, FabricTime end)
        : m_historyWindow(ringBuf.getId(), start, end, StageAtTimeIntervalFlags::IncludeEndTime), m_time(time)
    {
        initInterpolation();
    }

    // Auxiliary method to communicate attributes of types which will not be interpolated
    // Supported types: bool, int, uint
    // no samples found: return nullopt
    // samples found:    return pair{value of sample in frame n, value of sample in frame n+1}
    template <typename T>
    optional<std::pair<optional<T>, optional<T>>> getNonInterpolatableAttributeRd(const Path& path,
                                                                                  const Token& attrName) const;

    ValidMirrors getAttributeValidBits(const PathC& path, const TokenC& attrName) const;

    // Read interpolated elements
    template <typename T>
    optional<T> getAttributeRd(const Path& path, const Token& attrName) const;

    // Read GPU elements (interpolation not supported yet!)
    template <typename T>
    const T* getAttributeRdGpu(const Path& path, const Token& attrName) const;

    // Get array attribute size, useful for GPU attributes
    size_t getArrayAttributeSize(const Path& path, const Token& attrName) const;

    // Get arrau attribute read
    template <typename T>
    gsl::span<const T> getArrayAttributeRd(const Path& path, const Token& attrName) const;

    // findPrims() finds prims that have all the attributes in "all", and any
    // of the attributes in "any", and none of the attributes in "none".
    // The attributes of the resulting prims can be accessed as piecewise
    // contiguous arrays, using getAttributeArray() below, which is typically
    // faster than calling getAttribute for each prim.
    PrimBucketList findPrims(const omni::fabric::set<AttrNameAndType>& all,
                             const omni::fabric::set<AttrNameAndType>& any = {},
                             const omni::fabric::set<AttrNameAndType>& none = {})
    {
        return m_historyWindow.findPrims(all, any, none);
    }

    // getAttributeArray(primBucketList, index, attrName) returns a read-only
    // contiguous array of the values of attribute "attrName" for each prim of
    // bucket "index" of "primBucketList".
    // "index" must be in the range [0..primBucketList.getBucketCount())
    template <typename T>
    AttributeArrayResult<T> getAttributeArrayRd(const PrimBucketList& primBucketList,
                                                size_t primBucketListIndex,
                                                const Token& attrName) const;

    template <typename T>
    AttributeArrayResult<T> getAttributeArrayRdGpu(const PrimBucketList& primBucketList,
                                                   size_t primBucketListIndex,
                                                   const Token& attrName) const;

    template <typename T>
    AttributeArrayResult<std::vector<T>> getArrayAttributeArrayRd(const PrimBucketList& primBucketList,
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
     * @return a vector of byte arrays, one for each time sample underlying the current StageAtTime. Note: Does not
     * perform any interpolation.
     */
    std::vector<gsl::span<const char>> getAttributeArrayRawRd(const PrimBucketList& primBucketList,
                                                              size_t primBucketListIndex,
                                                              const Token& attrName) const;

    // getPathArray(primBucketList, index) returns a read-only contiguous array
    // of the paths of the prims of bucket "index" of "primBucketList".
    // "index" must be in the range [0..primBucketList.getBucketCount())
    gsl::span<const Path> getPathArray(const PrimBucketList& primBucketList, size_t primBucketListIndex) const;

    /**
     * @brief Get a read only pointer to a connection on a prim
     *
     * @param path the target prim
     * @param connectionName the target connection
     * @return returns a vector read only pointers to connections, one per time sample
     */
    std::vector<const Connection*> getConnectionRd(const Path& path, const Token& connectionName);

    // TODO: replace with an iterator for iterating over bucket names
    void printBucketNames() const;

    // Get the number of attributes for a given bucket.
    size_t getAttributeCount(const PrimBucketList& primBucketList, size_t primBucketListIndex) const;

    // Get the name and type of each attribute for a given bucket.
    std::pair<std::vector<Token>, std::vector<Type>> getAttributeNamesAndTypes(const PrimBucketList& primBucketList,
                                                                               size_t primBucketListIndex) const;

    // Unlocks elements to allow them to be reused.
    ~StageAtTime() = default;

    /** @brief Write a cache file to disk at a specified location
     *
     * @note Many parameters to this function are optional
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

    /** @brief Add a ref count to any data backed by the StageAtTimeInterval
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

#include <omni/fabric/stage/impl/StageAtTime.inl>
