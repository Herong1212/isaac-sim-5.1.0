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

inline FabricRingBuffer::FabricRingBuffer(RingBufferId id)
{
    m_interface = carb::getCachedInterface<IFabricRingBuffer>();
    CARB_ASSERT(m_interface);
    m_interface->addRef(id);
    m_id = id;
}

inline FabricRingBuffer::FabricRingBuffer(size_t slots, FabricTime rate, FabricOptions options)
{
    m_interface = carb::getCachedInterface<IFabricRingBuffer>();
    CARB_ASSERT(m_interface);
    m_id = m_interface->create(slots, rate, options);
}

inline FabricRingBuffer::FabricRingBuffer(const FabricRingBuffer& other)
{
    m_interface = carb::getCachedInterface<IFabricRingBuffer>();
    CARB_ASSERT(m_interface);
    m_interface->addRef(other.m_id);
    m_id = other.m_id;
}

inline FabricRingBuffer& FabricRingBuffer::operator=(const FabricRingBuffer& other)
{
    m_interface = carb::getCachedInterface<IFabricRingBuffer>();
    CARB_ASSERT(m_interface);

    m_interface->addRef(other.m_id);
    m_interface->release(m_id);
    m_id = other.m_id;
    return *this;
}

inline FabricRingBuffer::FabricRingBuffer(FabricRingBuffer&& other)
{
    m_interface = carb::getCachedInterface<IFabricRingBuffer>();
    CARB_ASSERT(m_interface);
    m_id = other.m_id;
    other.m_id = kInvalidRingBufferId;
}

inline FabricRingBuffer& FabricRingBuffer::operator=(FabricRingBuffer&& other)
{
    m_interface = carb::getCachedInterface<IFabricRingBuffer>();
    CARB_ASSERT(m_interface);
    m_interface->release(m_id);
    m_id = other.m_id;
    other.m_id = kInvalidRingBufferId;
    return *this;
}

inline FabricRingBuffer::~FabricRingBuffer()
{
    m_interface->release(m_id);
}

inline bool FabricRingBuffer::pushNextSlot()
{
    return m_interface->pushNextSlot(m_id);
}

inline bool FabricRingBuffer::tryPushNextSlot()
{
    return m_interface->tryPushNextSlot(m_id);
}

inline bool FabricRingBuffer::pushNextSlot(FabricTime timestamp)
{
    return m_interface->pushNextSlotWithTimeStamp(m_id, timestamp);
}

inline bool FabricRingBuffer::tryPushNextSlot(FabricTime timestamp)
{
    return m_interface->tryPushNextSlotWithTimeStamp(m_id, timestamp);
}

inline LockedRingBufferWindowId FabricRingBuffer::lockWindow(FabricTimeWindow window)
{
    return m_interface->lockTimeWindowForRead(m_id, window);
}

inline LockedRingBufferWindowId FabricRingBuffer::lockSamples(FabricTime time)
{
    return m_interface->lockImplicitWindowForRead(m_id, time);
}

inline void FabricRingBuffer::unlockWindow(LockedRingBufferWindowId window)
{
    m_interface->unlockTimeWindowForRead(m_id, window);
}

inline size_t FabricRingBuffer::getSampleCount(LockedRingBufferWindowId window)
{
    return m_interface->getSampleCountForTimeWindow(m_id, window);
}

inline std::vector<std::pair<Fabric, FabricTime>> FabricRingBuffer::getFabrics(LockedRingBufferWindowId window)
{
    Span<FabricId> ids;
    Span<FabricTime> times;
    size_t samples = m_interface->getFabricIdsForTimeWindow(m_id, window, &ids, &times);
    std::vector<std::pair<Fabric, FabricTime>> out;
    out.reserve(samples);
    for (size_t i = 0; i < samples; ++i)
    {
        out.push_back(std::make_pair(Fabric(ids[i]), times[i]));
    }
    return out;
}

inline void FabricRingBuffer::attach(const Fabric& cache)
{
    m_interface->attachToFabric(m_id, cache.getId());
}

inline void FabricRingBuffer::attach(Span<Fabric> caches)
{
    std::vector<FabricId> ids;
    ids.reserve(caches.size());
    for (size_t i = 0; i < caches.size(); ++i)
    {
        ids.push_back(caches[i].getId());
    }
    m_interface->attachToFabrics(m_id, ids);
}

inline void FabricRingBuffer::detach(const Fabric& cache)
{
    m_interface->detachFromFabric(m_id, cache.getId());
}

inline void FabricRingBuffer::detach(Span<Fabric> caches)
{
    std::vector<FabricId> ids;
    ids.reserve(caches.size());
    for (size_t i = 0; i < caches.size(); ++i)
    {
        ids.push_back(caches[i].getId());
    }
    m_interface->detachFromFabrics(m_id, ids);
}

inline void FabricRingBuffer::detachAllSources()
{
    m_interface->detachAllSources(m_id);
}

inline size_t FabricRingBuffer::growBuffer(size_t growthAmount)
{
    return m_interface->growBuffer(m_id, growthAmount);
}


inline void FabricRingBuffer::setFilter(Span<FabricCopyFilter> filters)
{
    m_interface->setFilter(m_id, filters);
}

inline FabricTime FabricRingBuffer::getRate() const
{
    return m_interface->getRate(m_id);
}

inline RingBufferId FabricRingBuffer::getId() const
{
    return m_id;
}

} // namespace fabric
} // namespace omni
