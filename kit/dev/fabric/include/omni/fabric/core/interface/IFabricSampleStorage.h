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
#include <carb/extras/Uuid.h>

#include <omni/Function.h>

#include <omni/fabric/AttrNameAndType.h>
#include <omni/fabric/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/IdTypes.h>
#include <omni/fabric/core/Ordered_Set.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/TimeWindow.h>

#include <stdint.h>
#include <limits>

namespace omni
{
namespace fabric
{

// Opaque ID to an element in the List.
// The list assumes IDs are monotonically increasing and that
// any attempt to store an id that is older than the current tail is a failure condition
struct SampleIndex
{
    uint64_t m_id;

    bool operator==(const SampleIndex& other) const
    {
        return m_id == other.m_id;
    }
    bool operator!=(const SampleIndex& other) const
    {
        return m_id != other.m_id;
    }
    bool operator<(const SampleIndex& other) const
    {
        return m_id < other.m_id;
    }
    bool operator<=(const SampleIndex& other) const
    {
        return m_id <= other.m_id;
    }
    bool operator>(const SampleIndex& other) const
    {
        return m_id > other.m_id;
    }
    bool operator>=(const SampleIndex& other) const
    {
        return m_id >= other.m_id;
    }
    SampleIndex(uint64_t id)
    {
        m_id = id;
    }
    constexpr SampleIndex() : m_id(std::numeric_limits<uint64_t>::max())
    {
    }

    bool isValid() const
    {
        return m_id != std::numeric_limits<uint64_t>::max();
    }
};

// If there are 2^63-1 samples things are non-ideal
static constexpr SampleIndex kEmptySampleIndex{};
static_assert(std::is_standard_layout<SampleIndex>::value,
              "Struct must be standard layout as it is used in C-ABI interfaces");

// TODO: When a sample is marked as being no longer editable or we add a new sample
// there are some clean up things that need to happen regarding change tracking
// and hierarchies in FabricSceneDelegate land.  Rather, than do the hard thing
// of moving this logic to other extensions and other such things now we'll
// abuse the power of callbacks to solve all our problems... once and for all.
using OnAddSampleCallback = omni::function<void(FabricId)>;
using OnSetUneditableCallback = omni::function<void(FabricId)>;

// A list of Fabric Caches.
struct IFabricSampleStorage
{
    //! @private to avoid doxygen problems
    CARB_PLUGIN_INTERFACE("omni::fabric::IFabricSampleStorage", 0, 3);
    // Meant for internal use mostly, avoid direct usage
    void(CARB_ABI* addRef)(FabricSampleStorageId id);
    void(CARB_ABI* release)(FabricSampleStorageId id);

    FabricSampleStorageId(CARB_ABI* createStorage)(SampleIndex initialIndex);

    FabricSampleStorageId(CARB_ABI* createStorageFromFabric)(FabricId fabricId,
                                                             Span<FabricCopyFilter> filters,
                                                             bool editable,
                                                             SampleIndex initialIndex);

    FabricSampleStorageId(CARB_ABI* createStorageWithCallbacks)(SampleIndex initialIndex,
                                                                OnAddSampleCallback sample,
                                                                OnSetUneditableCallback edit,
                                                                bool executeSampleCallback,
                                                                bool executeUneditableCallback);

    FabricSampleStorageId(CARB_ABI* createStorageFromFabricWithCallbacks)(FabricId fabricId,
                                                                          Span<FabricCopyFilter> filters,
                                                                          bool editable,
                                                                          SampleIndex initialIndex,
                                                                          OnAddSampleCallback sample,
                                                                          OnSetUneditableCallback edit,
                                                                          bool executeSampleCallback,
                                                                          bool executeUneditableCallback);

    FabricSampleStorageId(CARB_ABI* createEmptyStorage)();

    bool(CARB_ABI* setOnAddSampleCallback)(FabricSampleStorageId id, OnAddSampleCallback callback);
    bool(CARB_ABI* setOnUneditableCallback)(FabricSampleStorageId id, OnSetUneditableCallback callback);

    // can only be called once on an empty storage
    bool(CARB_ABI* setInitialFabric)(FabricSampleStorageId id,
                                     FabricId fabricId,
                                     Span<FabricCopyFilter> filters,
                                     bool editable,
                                     SampleIndex initialIndex,
                                     bool executeSampleCallback,
                                     bool executeUneditableCallback);

    // Control the max number of samples held by the storage. if count < current_max eviction will occur
    bool(CARB_ABI* setMaxSampleStorage)(FabricSampleStorageId id, uint64_t count);
    uint64_t(CARB_ABI* getMaxSampleStorage)(FabricSampleStorageId id);
    uint64_t(CARB_ABI* getCurrentSampleCount)(FabricSampleStorageId id);

    bool(CARB_ABI* isEmpty)(FabricSampleStorageId id);
    bool(CARB_ABI* isEditable)(FabricSampleStorageId id, SampleIndex index);

    // adding a sample will evict older samples
    // A sample can be added at the writeWatermark if no sample exists there or after the 
    // writewatermark.
    bool(CARB_ABI* addSample)(FabricSampleStorageId id, SampleIndex index, bool editable);

    // This call will remove all samples older than the given ID.. It will always
    // leave at least one sample in the storage though.
    size_t(CARB_ABI* evictSamples)(FabricSampleStorageId id, SampleIndex index);

    // This actualy deletes evicted samples which are not still being read.
    size_t(CARB_ABI* purgeEvictedSamples)(FabricSampleStorageId id);

    // Reads older than this water mark cannot be honored.
    SampleIndex(CARB_ABI* getReadWaterMark)(FabricSampleStorageId id);
    // This will mark older samples as evicted and they will be purged next time a purge is called.
    bool(CARB_ABI* setReadWaterMark)(FabricSampleStorageId id, SampleIndex readMark);
    // Writes older than this water mark cannot be honored
    SampleIndex(CARB_ABI* getWriteWaterMark)(FabricSampleStorageId id);
    bool(CARB_ABI* setWriteWaterMark)(FabricSampleStorageId id, SampleIndex writeMark);

    LockedReadSamplesId(CARB_ABI* lockSamplesForRead)(FabricSampleStorageId id, SampleIndex const* indices, size_t sampleCount);

    bool(CARB_ABI* unlockSamplesForRead)(FabricSampleStorageId id, LockedReadSamplesId readId);

    size_t(CARB_ABI* getReadSampleCount)(FabricSampleStorageId id, LockedReadSamplesId readId);

    size_t(CARB_ABI* getReadSampleFabricIds)(FabricSampleStorageId id,
                                             LockedReadSamplesId readId,
                                             Span<FabricId>* ids,
                                             Span<SampleIndex>* indices);

    LockedWriteSampleId(CARB_ABI* lockSampleForWrite)(FabricSampleStorageId id, SampleIndex index);

    bool(CARB_ABI* unlockSampleForWrite)(FabricSampleStorageId id, LockedWriteSampleId writeId);

    bool(CARB_ABI* getWriteSampleFabricId)(FabricSampleStorageId id,
                                           LockedWriteSampleId writeId,
                                           FabricId* fabricId,
                                           SampleIndex* index);

    LockedReadSamplesId(CARB_ABI* lockAllSamplesForRead_DebugOnly)(FabricSampleStorageId id);
    LockedReadSamplesId(CARB_ABI* lockSamplesInRangeForRead)(FabricSampleStorageId id, SampleIndex start, SampleIndex end);
};

} // namespace fabric
} // namespace omni

namespace std
{

template <>
struct hash<omni::fabric::SampleIndex>
{
    //! Returns a hash value for the type, using its bit-value for the hash
    std::size_t operator()(omni::fabric::SampleIndex const& key) const noexcept
    {
        return hash<uint64_t>()(key.m_id);
    }
};

} // namespace std
