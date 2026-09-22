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

inline FabricSampleStorage::FabricSampleStorage(FabricSampleStorageId id)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_interface->addRef(id);
    m_id = id;
}

inline FabricSampleStorage::FabricSampleStorage()
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_id = m_interface->createEmptyStorage();
}

inline FabricSampleStorage::FabricSampleStorage(SampleIndex initialIndex)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_id = m_interface->createStorage(initialIndex);
}

inline FabricSampleStorage::FabricSampleStorage(FabricId fabricId,
                                                Span<FabricCopyFilter> filters,
                                                bool editable,
                                                SampleIndex initialIndex)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_id = m_interface->createStorageFromFabric(fabricId, filters, editable, initialIndex);
}

inline FabricSampleStorage::FabricSampleStorage(SampleIndex initialIndex,
                                                OnAddSampleCallback sample,
                                                OnSetUneditableCallback edit,
                                                bool executeSampleCallback,
                                                bool executeUneditableCallback)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_id = m_interface->createStorageWithCallbacks(
        initialIndex, std::move(sample), std::move(edit),
        executeSampleCallback, executeUneditableCallback);
}

inline FabricSampleStorage::FabricSampleStorage(FabricId fabricId,
                                                Span<FabricCopyFilter> filters,
                                                bool editable,
                                                SampleIndex initialIndex,
                                                OnAddSampleCallback sample,
                                                OnSetUneditableCallback edit,
                                                bool executeSampleCallback,
                                                bool executeUneditableCallback)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_id = m_interface->createStorageFromFabricWithCallbacks(
        fabricId, filters, editable, initialIndex, std::move(sample), std::move(edit),
        executeSampleCallback, executeUneditableCallback);
}

inline FabricSampleStorage::FabricSampleStorage(const FabricSampleStorage& other)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_interface->addRef(other.m_id);
    m_id = other.m_id;
}

inline FabricSampleStorage& FabricSampleStorage::operator=(const FabricSampleStorage& other)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);

    m_interface->addRef(other.m_id);
    m_interface->release(m_id);
    m_id = other.m_id;
    return *this;
}

inline FabricSampleStorage::FabricSampleStorage(FabricSampleStorage&& other)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_id = other.m_id;
    other.m_id = kInvalidFabricSampleStorageId;
}

inline FabricSampleStorage& FabricSampleStorage::operator=(FabricSampleStorage&& other)
{
    m_interface = carb::getCachedInterface<IFabricSampleStorage>();
    CARB_ASSERT(m_interface);
    m_interface->release(m_id);
    m_id = other.m_id;
    other.m_id = kInvalidFabricSampleStorageId;
    return *this;
}

inline FabricSampleStorage::~FabricSampleStorage()
{
    m_interface->release(m_id);
}

inline bool FabricSampleStorage::setInitialFabric(FabricId fabricId,
                                                  Span<FabricCopyFilter> filters,
                                                  bool editable,
                                                  SampleIndex initialIndex,
                                                  bool executeSampleCallback,
                                                  bool executeUneditableCallback)
{
    return m_interface->setInitialFabric(
        m_id, fabricId, filters, editable, initialIndex, executeSampleCallback, executeUneditableCallback);
}

inline bool FabricSampleStorage::setOnAddSampleCallback(OnAddSampleCallback callback)
{
    return m_interface->setOnAddSampleCallback(m_id, std::move(callback));
}

inline bool FabricSampleStorage::setOnUneditableCallback(OnSetUneditableCallback callback)
{
    return m_interface->setOnUneditableCallback(m_id, std::move(callback));
}

// Control the max number of samples held by the storage. if count < current_max eviction will occur
inline bool FabricSampleStorage::setMaxSampleStorage(uint64_t count)
{
    return m_interface->setMaxSampleStorage(m_id, count);
}

inline uint64_t FabricSampleStorage::getMaxSampleStorage()
{
    return m_interface->getMaxSampleStorage(m_id);
}

inline uint64_t FabricSampleStorage::getCurrentSampleCount()
{
    return m_interface->getCurrentSampleCount(m_id);
}

inline bool FabricSampleStorage::isEmpty()
{
    return m_interface->isEmpty(m_id);
}

inline bool FabricSampleStorage::isEditable(SampleIndex index)
{
    return m_interface->isEditable(m_id, index);
}

inline bool FabricSampleStorage::addSample(SampleIndex index, bool editable)
{
    return m_interface->addSample(m_id, index, editable);
}

inline size_t FabricSampleStorage::evictSamples(SampleIndex index)
{
    return m_interface->evictSamples(m_id, index);
}

inline size_t FabricSampleStorage::purgeEvictedSamples()
{
    return m_interface->purgeEvictedSamples(m_id);
}

inline SampleIndex FabricSampleStorage::getWriteWaterMark()
{
    return m_interface->getWriteWaterMark(m_id);
}

inline bool FabricSampleStorage::setWriteWaterMark(SampleIndex writeMark)
{
    return m_interface->setWriteWaterMark(m_id, writeMark);
}

inline SampleIndex FabricSampleStorage::getReadWaterMark()
{
    return m_interface->getReadWaterMark(m_id);
}

inline bool FabricSampleStorage::setReadWaterMark(SampleIndex readMark)
{

    return m_interface->setReadWaterMark(m_id, readMark);
}

inline LockedReadSamplesId FabricSampleStorage::lockSampleForRead(const SampleIndex& index)
{
    return m_interface->lockSamplesForRead(m_id, &index, 1);
}
inline LockedReadSamplesId FabricSampleStorage::lockSamplesForRead(const std::vector<SampleIndex>& indices)
{
    return m_interface->lockSamplesForRead(m_id, indices.data(), indices.size());
}
inline LockedReadSamplesId FabricSampleStorage::lockSamplesInRangeForRead(const SampleIndex& start, const SampleIndex& end)
{
    return m_interface->lockSamplesInRangeForRead(m_id, start, end);
}

inline LockedReadSamplesId FabricSampleStorage::lockAllSamplesForRead_DebugOnly()
{
    return m_interface->lockAllSamplesForRead_DebugOnly(m_id);
}

inline bool FabricSampleStorage::unlockSamplesForRead(LockedReadSamplesId id)
{
    return m_interface->unlockSamplesForRead(m_id, id);
}

inline size_t FabricSampleStorage::getSampleCount(LockedReadSamplesId id)
{
    return m_interface->getReadSampleCount(m_id, id);
}

inline std::vector<std::pair<Fabric, SampleIndex>> FabricSampleStorage::getReadFabrics(LockedReadSamplesId id)
{
    Span<FabricId> ids;
    Span<SampleIndex> indices;
    size_t samples = m_interface->getReadSampleFabricIds(m_id, id, &ids, &indices);
    std::vector<std::pair<Fabric, SampleIndex>> out;
    out.reserve(samples);
    for (size_t i = 0; i < samples; ++i)
    {
        out.emplace_back(Fabric(ids[i]), indices[i]);
    }
    return out;
}

inline LockedWriteSampleId FabricSampleStorage::lockSampleForWrite(SampleIndex index)
{
    return m_interface->lockSampleForWrite(m_id, index);
}

inline bool FabricSampleStorage::unlockSampleForWrite(LockedWriteSampleId id)
{
    return m_interface->unlockSampleForWrite(m_id, id);
}

inline std::pair<Fabric, SampleIndex> FabricSampleStorage::getWriteFabric(LockedWriteSampleId id)
{
    FabricId fabricId;
    SampleIndex index;
    m_interface->getWriteSampleFabricId(m_id, id, &fabricId, &index);
    return std::make_pair(fabricId, index);
}

inline FabricSampleStorageId FabricSampleStorage::getId() const
{
    return m_id;
}

} // namespace fabric
} // namespace omni
