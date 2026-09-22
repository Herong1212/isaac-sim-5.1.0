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
inline Fabric::Fabric(FabricId id)
{
    m_interface = carb::getCachedInterface<IFabric>();
    CARB_ASSERT(m_interface);
    m_interface->addRef(id);
    m_id = id;
}

inline Fabric::Fabric(FabricOptions opt)
{
    m_interface = carb::getCachedInterface<IFabric>();
    CARB_ASSERT(m_interface);
    m_id = m_interface->createFabricCache(opt);
}

inline Fabric::Fabric(const Fabric& other)
{
    m_interface = carb::getCachedInterface<IFabric>();
    CARB_ASSERT(m_interface);
    m_interface->addRef(other.m_id);
    m_id = other.m_id;
}

inline Fabric& Fabric::operator=(const Fabric& other)
{
    m_interface = carb::getCachedInterface<IFabric>();
    CARB_ASSERT(m_interface);
    m_interface->release(m_id);
    m_interface->addRef(other.m_id);
    m_id = other.m_id;
    return *this;
}

inline Fabric::Fabric(Fabric&& other)
{
    m_interface = carb::getCachedInterface<IFabric>();
    CARB_ASSERT(m_interface);
    m_id = other.m_id;
    other.m_id = kInvalidFabricId;
}

inline Fabric& Fabric::operator=(Fabric&& other)
{
    m_interface = carb::getCachedInterface<IFabric>();
    CARB_ASSERT(m_interface);
    m_interface->release(m_id);
    m_id = other.m_id;
    other.m_id = kInvalidFabricId;
    return *this;
}

inline Fabric::~Fabric()
{
    m_interface->release(m_id);
}

inline FabricId Fabric::getId() const
{
    return m_id;
}

inline bool Fabric::writeToDisk(carb::cpp::string_view file, std::vector<uint8_t>& workingBuffer, uint64_t& bytesWritten)
{
    return m_interface->writeFabricCacheToDisk(
        m_id, file.data(), workingBuffer.data(), workingBuffer.size(), &bytesWritten);
}

inline bool Fabric::readFromDisk(carb::cpp::string_view file, std::vector<uint8_t>& workingBuffer, uint64_t& bytesRead)
{
    return m_interface->readFabricCacheFromDisk(
        m_id, file.data(), workingBuffer.data(), workingBuffer.size(), &bytesRead);
}

inline void Fabric::enableGpuCompute(GpuComputeType type)
{
    m_interface->enableGpuCompute(type);
}

inline void Fabric::clearData()
{
    m_interface->clearFabricCacheData(m_id);
}

inline void Fabric::configureSerialization(SerializationOption option)
{

    m_interface->configureSerialization(m_id, option);
}

inline uint64_t Fabric::serialize(Span<uint8_t> dest)
{
    return m_interface->serializeFabricCache(m_id, dest.data(), dest.size());
}

inline bool Fabric::deserialize(const Span<uint8_t> input, bool skipConfirmation)
{
    return m_interface->deserializeFabricCache(m_id, input.data(), input.size(), skipConfirmation);
}

inline void Fabric::setDebugName(carb::cpp::string_view name)
{
    m_interface->setFabricDebugName(m_id, name.data());
}

inline std::string Fabric::getDebugName()
{
    return std::string(m_interface->getFabricDebugName(m_id));
}

inline bool Fabric::cloneData(const Fabric& src)
{
    return m_interface->cloneFabricCache(src.m_id, m_id);
}

inline bool Fabric::appendData(const Fabric& src, Span<FabricCopyFilter> filters)
{
    return m_interface->appendFabricCache(src.m_id, m_id, filters);
}

inline bool Fabric::appendData(Span<Fabric> srcFabrics, Span<FabricCopyFilter> filters)
{
    std::vector<FabricId> ids;
    ids.reserve(srcFabrics.size());
    for (size_t i = 0; i < srcFabrics.size(); ++i)
    {
        ids.push_back(srcFabrics[i].m_id);
    }
    return m_interface->appendFabricCaches(ids, m_id, filters);
}

inline bool Fabric::copyOrMergeData(const Fabric& src,
                                    Span<FabricCopyFilter> filters,
                                    bool overwritePrims,
                                    bool createNewPrims)
{
    return m_interface->copyOrMergeFabricCache(src.m_id, m_id, filters, overwritePrims, createNewPrims);
}

inline bool Fabric::copyOrMergeData(Span<Fabric> srcFabrics,
                                    Span<FabricCopyFilter> filters,
                                    bool overwritePrims,
                                    bool createNewPrims)
{
    std::vector<FabricId> ids;
    ids.reserve(srcFabrics.size());
    for (size_t i = 0; i < srcFabrics.size(); ++i)
    {
        ids.push_back(srcFabrics[i].m_id);
    }
    return m_interface->copyOrMergeFabricCaches(ids, m_id, filters, overwritePrims, createNewPrims);
}

inline bool Fabric::moveData(Fabric& src, Span<FabricCopyFilter> filters, bool overwritePrims, bool createNewPrims)
{
    return m_interface->moveFabricCache(src.m_id, m_id, filters, overwritePrims, createNewPrims);
}

inline bool Fabric::copyBucketData(const Fabric& src, FabricCopyFilter filter)
{
    return m_interface->copyFabricCacheBuckets(src.m_id, m_id, filter);
}

inline uint64_t Fabric::getTopologyVersion()
{
    return m_interface->getTopologyVersion(m_id);
}

} // namespace fabric
} // namespace omni
