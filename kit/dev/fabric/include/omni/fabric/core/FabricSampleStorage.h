// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/Enums.h>
#include <omni/fabric/core/FabricTypes.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/Fabric.h>
#include <omni/fabric/core/interface/IFabricSampleStorage.h>

#include <memory>

namespace omni
{
namespace fabric
{
class FabricSampleStorage
{
    FabricSampleStorageId m_id;
    IFabricSampleStorage* m_interface;

public:
    FabricSampleStorage();

    FabricSampleStorage(SampleIndex initialIndex);

    FabricSampleStorage(FabricId fabricId, Span<FabricCopyFilter> filters, bool editable, SampleIndex initialIndex);

    FabricSampleStorage(SampleIndex initialIndex,
                        OnAddSampleCallback sample,
                        OnSetUneditableCallback edit,
                        bool executeSampleCallback,
                        bool executeUneditableCallback);

    FabricSampleStorage(FabricId fabricId,
                        Span<FabricCopyFilter> filters,
                        bool editable,
                        SampleIndex initialIndex,
                        OnAddSampleCallback sample,
                        OnSetUneditableCallback edit,
                        bool executeSampleCallback,
                        bool executeUneditableCallback);


    FabricSampleStorage(const FabricSampleStorage& other);
    FabricSampleStorage& operator=(const FabricSampleStorage& other);

    FabricSampleStorage(FabricSampleStorage&& other);
    FabricSampleStorage& operator=(FabricSampleStorage&& other);
    ~FabricSampleStorage();

    bool setInitialFabric(FabricId fabricId,
                          Span<FabricCopyFilter> filters,
                          bool editable,
                          SampleIndex initialIndex,
                          bool executeSampleCallback,
                          bool executeUneditableCallback);
    bool setOnAddSampleCallback(OnAddSampleCallback callback);
    bool setOnUneditableCallback(OnSetUneditableCallback callback);

    // Control the max number of samples held by the storage. if count < current_max eviction will occur
    bool setMaxSampleStorage(uint64_t count);
    uint64_t getMaxSampleStorage();
    uint64_t getCurrentSampleCount();

    bool isEmpty();
    bool isEditable(SampleIndex index);

    bool addSample(SampleIndex index, bool editable);

    // Note: Removal is safe even while a sample is being read or written as the  locks
    // will keep things alive until processing is finished.
    // Removes all samples at or older than the given sampleIndex... If all samples would be removed, will
    // leave newest sample in place
    size_t evictSamples(SampleIndex index);
    size_t purgeEvictedSamples();

    SampleIndex getReadWaterMark();
    bool setReadWaterMark(SampleIndex readMark);

    SampleIndex getWriteWaterMark();
    bool setWriteWaterMark(SampleIndex writeMark);

    LockedReadSamplesId lockSampleForRead(const SampleIndex& index);
    LockedReadSamplesId lockSamplesForRead(const std::vector<SampleIndex>& indices);
    
    // Locks all samples in the range [start, end]
    // kEmptySampleIndex is equivalent to 0 for start, and is the maximum for end
    // e.g. lockSamplesInRangeForRead(kEmptySampleIndex, kEmptySampleIndex) will lock ALL samples
    // and lockSamplesInRangeForRead(5, 10) will lock existing samples between 5 and 10 (even if 5 and 10 do not exist)
    // Note: this only advances watermarks as high as the highest existing sample, not the highest requested read.
    LockedReadSamplesId lockSamplesInRangeForRead(const SampleIndex& start, const SampleIndex& end);
    
    LockedReadSamplesId lockAllSamplesForRead_DebugOnly();
    bool unlockSamplesForRead(LockedReadSamplesId id);

    size_t getSampleCount(LockedReadSamplesId id);
    std::vector<std::pair<Fabric, SampleIndex>> getReadFabrics(LockedReadSamplesId id);

    LockedWriteSampleId lockSampleForWrite(SampleIndex index);
    bool unlockSampleForWrite(LockedWriteSampleId id);
    std::pair<Fabric, SampleIndex> getWriteFabric(LockedWriteSampleId id);


    FabricSampleStorage(FabricSampleStorageId id);
    FabricSampleStorageId getId() const;
};


// Helper struct that utilizes RAII principle to automatically handle proper locking and unlocking of samples
// for reading.
struct ScopedReadSampleLock
{
public:
    ScopedReadSampleLock(omni::fabric::FabricSampleStorage& fabricSampleStorage)
        : m_lockedReadSamplesId(kInvalidLockedReadSamplesId)
        , m_fabricSampleStorage(fabricSampleStorage)
    {
    }

    ScopedReadSampleLock(omni::fabric::FabricSampleStorage& fabricSampleStorage,
                         const std::vector<omni::fabric::SampleIndex>& indices)
        : m_fabricSampleStorage(fabricSampleStorage)
    {
        m_lockedReadSamplesId = fabricSampleStorage.lockSamplesForRead(indices);
    }

    ScopedReadSampleLock(omni::fabric::FabricSampleStorage& fabricSampleStorage, const omni::fabric::SampleIndex& index)
        : m_fabricSampleStorage(fabricSampleStorage)
    {
        m_lockedReadSamplesId = fabricSampleStorage.lockSampleForRead(index);
    }

    ScopedReadSampleLock(omni::fabric::FabricSampleStorage& fabricSampleStorage, const omni::fabric::SampleIndex& start, const omni::fabric::SampleIndex& end)
        : m_fabricSampleStorage(fabricSampleStorage)
    {
        m_lockedReadSamplesId = fabricSampleStorage.lockSamplesInRangeForRead(start, end);
    }

    ~ScopedReadSampleLock()
    {
        if (m_lockedReadSamplesId != kInvalidLockedReadSamplesId)
        {
            if (!m_fabricSampleStorage.unlockSamplesForRead(m_lockedReadSamplesId))
            {
                // TODO: Should we have some sort of logging?
            }
        }
    }

    ScopedReadSampleLock(const ScopedReadSampleLock&) = delete;
    ScopedReadSampleLock& operator=(const ScopedReadSampleLock&) = delete;

    ScopedReadSampleLock(ScopedReadSampleLock&& other)
        : m_lockedReadSamplesId(other.m_lockedReadSamplesId)
        , m_fabricSampleStorage(other.m_fabricSampleStorage)
    {
        other.m_lockedReadSamplesId = kInvalidLockedReadSamplesId;
    }

    ScopedReadSampleLock& operator=(ScopedReadSampleLock&& other)
    {
        if (m_lockedReadSamplesId != kInvalidLockedReadSamplesId)
        {
            m_fabricSampleStorage.unlockSamplesForRead(m_lockedReadSamplesId);
        }

        CARB_ASSERT(&m_fabricSampleStorage == &other.m_fabricSampleStorage);
        m_lockedReadSamplesId = other.m_lockedReadSamplesId;
        other.m_lockedReadSamplesId = kInvalidLockedReadSamplesId;
        return *this;
    }

    omni::fabric::LockedReadSamplesId getId()
    {
        return m_lockedReadSamplesId;
    }

    omni::fabric::FabricSampleStorage& getStorage()
    {
        return m_fabricSampleStorage;
    }

private:
    omni::fabric::LockedReadSamplesId m_lockedReadSamplesId;
    omni::fabric::FabricSampleStorage& m_fabricSampleStorage;
};


// Helper struct that utilizes RAII principle to automatically handle proper locking and unlocking of an sample
// for write
struct ScopedWriteSampleLock
{
public:
    ScopedWriteSampleLock(omni::fabric::FabricSampleStorage& fabricSampleStorage)
        : m_lockedWriteSampleId(kInvalidLockedWriteSampleId)
        , m_fabricSampleStorage(fabricSampleStorage)
    {
    }

    ScopedWriteSampleLock(omni::fabric::FabricSampleStorage& fabricSampleStorage, omni::fabric::SampleIndex index)
        : m_fabricSampleStorage(fabricSampleStorage)
    {
        m_lockedWriteSampleId = fabricSampleStorage.lockSampleForWrite(index);
    }

    ~ScopedWriteSampleLock()
    {
        if (m_lockedWriteSampleId != kInvalidLockedWriteSampleId)
        {
            if (!m_fabricSampleStorage.unlockSampleForWrite(m_lockedWriteSampleId))
            {
                // TODO: Should we have some sort of logging?
            }
        }
    }

    ScopedWriteSampleLock(const ScopedWriteSampleLock&) = delete;
    ScopedWriteSampleLock& operator=(const ScopedWriteSampleLock&) = delete;

    ScopedWriteSampleLock(ScopedWriteSampleLock&& other)
        : m_lockedWriteSampleId(other.m_lockedWriteSampleId)
        , m_fabricSampleStorage(other.m_fabricSampleStorage)
    {
        other.m_lockedWriteSampleId = kInvalidLockedWriteSampleId;
    }

    ScopedWriteSampleLock& operator=(ScopedWriteSampleLock&& other)
    {
        if (m_lockedWriteSampleId != kInvalidLockedWriteSampleId)
        {
            m_fabricSampleStorage.unlockSampleForWrite(m_lockedWriteSampleId);
        }

        CARB_ASSERT(&m_fabricSampleStorage == &other.m_fabricSampleStorage);
        m_lockedWriteSampleId = other.m_lockedWriteSampleId;
        other.m_lockedWriteSampleId = kInvalidLockedWriteSampleId;
        return *this;
    }

    omni::fabric::LockedWriteSampleId getId()
    {
        return m_lockedWriteSampleId;
    }

private:
    omni::fabric::LockedWriteSampleId m_lockedWriteSampleId;
    omni::fabric::FabricSampleStorage& m_fabricSampleStorage;
};


} // namespace fabric
} // namespace omni

#include <omni/fabric/core/impl/FabricSampleStorage.inl>
