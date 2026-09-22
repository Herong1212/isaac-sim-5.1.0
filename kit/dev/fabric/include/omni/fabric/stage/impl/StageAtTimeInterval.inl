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
// StageAtTimeInterval implementation starts here
inline omni::fabric::IStageAtTimeInterval* StageAtTimeInterval::sIStageAtTimeInterval()
{
    return carb::getCachedInterface<omni::fabric::IStageAtTimeInterval>();
}

inline bool StageAtTimeInterval::getIntervalParameters(SimStageWithHistoryId simStageWithHistoryId,
                                                       FabricTime beginTime,
                                                       FabricTime endTime,
                                                       StageAtTimeIntervalFlags flags,
                                                       int64_t& beginFrame,
                                                       int64_t& endFrame,
                                                       int64_t& startRingbufferSlot,
                                                       int64_t& endRingbufferSlot,
                                                       int64_t& slotCount)
{
    return sIStageAtTimeInterval()->getIntervalParameters(simStageWithHistoryId, beginTime, endTime, flags, beginFrame,
                                                          endFrame, startRingbufferSlot, endRingbufferSlot, slotCount);
}


inline StageAtTimeInterval::StageAtTimeInterval(SimStageWithHistory& simStageWithHistory,
                                                FabricTime beginTime,
                                                FabricTime endTime,
                                                StageAtTimeIntervalFlags flags)
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);
    m_stageAtTimeInterval =
        m_interface->createWithFlags(simStageWithHistory.m_simStageWithHistory, beginTime, endTime, flags);

    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
}

inline StageAtTimeInterval::StageAtTimeInterval(SimStageWithHistoryId simStageWithHistoryId,
                                                FabricTime beginTime,
                                                FabricTime endTime,
                                                StageAtTimeIntervalFlags flags)
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);
    m_stageAtTimeInterval = m_interface->createWithFlags(simStageWithHistoryId, beginTime, endTime, flags);
    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
}

inline StageAtTimeInterval::StageAtTimeInterval(RingBufferId ringBufferId,
                                                FabricTime beginTime,
                                                FabricTime endTime,
                                                StageAtTimeIntervalFlags flags)
{

    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);
    EndPointOptions opt = (uint32_t(flags) & uint32_t(StageAtTimeIntervalFlags::IncludeEndTime)) != 0x0 ?
                              EndPointOptions::eIncludeBoth :
                              EndPointOptions::eIncludeStart;
    FabricTimeWindow window{ beginTime, endTime, opt };
    m_stageAtTimeInterval = m_interface->createFromRingBuffer(ringBufferId, window);
    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
}

inline StageAtTimeInterval::StageAtTimeInterval(RingBufferId ringBufferId, FabricTimeWindow window)
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);

    m_stageAtTimeInterval = m_interface->createFromRingBuffer(ringBufferId, window);
    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
}

inline StageAtTimeInterval::StageAtTimeInterval()
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);
    m_stageAtTimeInterval = kInvalidStageAtTimeIntervalId;
}

inline StageAtTimeInterval::StageAtTimeInterval(const StageAtTimeInterval& other)
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);

    m_stageAtTimeInterval = other.m_stageAtTimeInterval;
    m_interface->addRef(m_stageAtTimeInterval);

    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
}

inline StageAtTimeInterval& StageAtTimeInterval::operator=(const StageAtTimeInterval& other)
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);
    m_interface->release(m_stageAtTimeInterval);

    m_stageAtTimeInterval = other.m_stageAtTimeInterval;
    m_interface->addRef(m_stageAtTimeInterval);

    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
    return *this;
}

inline StageAtTimeInterval::StageAtTimeInterval(StageAtTimeInterval&& other)
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);
    
    m_stageAtTimeInterval = other.m_stageAtTimeInterval;
    
    other.m_stageAtTimeInterval = kInvalidStageAtTimeIntervalId;
    other.m_timeSamples.clear();

    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
}

inline StageAtTimeInterval& StageAtTimeInterval::operator=(StageAtTimeInterval&& other)
{
    m_interface = sIStageAtTimeInterval();
    CARB_ASSERT(m_interface);
    m_interface->release(m_stageAtTimeInterval);

    m_stageAtTimeInterval = other.m_stageAtTimeInterval;
    other.m_stageAtTimeInterval = kInvalidStageAtTimeIntervalId;
    other.m_timeSamples.clear();

    size_t count = m_interface->getTimesampleCount(m_stageAtTimeInterval);
    m_timeSamples.resize(count);
    m_interface->getTimestamps(m_timeSamples.data(), count, m_stageAtTimeInterval);
    return *this;
}

inline StageAtTimeInterval::~StageAtTimeInterval()
{
    m_interface->release(m_stageAtTimeInterval);
}

inline StageAtTimeIntervalId StageAtTimeInterval::getId()
{
    return m_stageAtTimeInterval;
}

inline const std::vector<FabricTime>& StageAtTimeInterval::getTimestamps() const
{
    return m_timeSamples;
}

inline size_t StageAtTimeInterval::getTimeSampleCount() const
{
    return m_timeSamples.size();
}

inline void StageAtTimeInterval::printBucketNames() const
{
    m_interface->printBucketNames(m_stageAtTimeInterval);
}

inline std::vector<uint8_t> StageAtTimeInterval::primExists(const Path& path) const
{
    std::vector<uint8_t> out(m_timeSamples.size());
    bool* data = (bool*)out.data();
    m_interface->primExists(&data, out.size(), m_stageAtTimeInterval, path);
    return out;
}

inline std::vector<uint8_t> StageAtTimeInterval::attributeExists(const Path& path, const Token& attr) const
{
    std::vector<uint8_t> out(m_timeSamples.size());
    bool* data = (bool*)out.data();
    m_interface->attributeExists(&data, out.size(), m_stageAtTimeInterval, path, attr);
    return out;
}

inline PrimBucketList StageAtTimeInterval::findPrims(const omni::fabric::set<AttrNameAndType>& all,
                                                     const omni::fabric::set<AttrNameAndType>& any,
                                                     const omni::fabric::set<AttrNameAndType>& none) const
{
    PrimBucketListId primBucketListId = m_interface->findPrims(m_stageAtTimeInterval, all, any, none);

    return PrimBucketList( primBucketListId, PrimBucketListOwnership::eOwned );
}

inline ValidMirrors StageAtTimeInterval::getAttributeValidBits(const PathC& path, const TokenC& attrName) const
{
    return m_interface->getAttributeValidBits(m_stageAtTimeInterval, path, attrName);
}

template <typename T>
std::vector<const T*> StageAtTimeInterval::getAttributeRd(const Path& path, const Token& attrName) const
{
    size_t count = m_timeSamples.size();
    std::vector<const T*> retval(count);
    const void** retvalData = reinterpret_cast<const void**>(retval.data());

    Type type = Type(m_interface->getAttributeRd(retvalData, count, m_stageAtTimeInterval, path, attrName));
    if (type.isValid() && VERIFY(type.isCompatibleWith<T>()))
    {
        return retval;
    }
    else
    {
        return std::vector<const T*>();
    }
}

template <typename T>
std::vector<const T*> StageAtTimeInterval::getAttributeRdGpu(const Path& path,
                                                             const Token& attrName,
                                                             int deviceId,
                                                             PtrToPtrKind wherePtr) const
{
    size_t count = m_timeSamples.size();
    std::vector<const T*> retval(count);
    std::vector<ConstSpanWithTypeC> arrays(count);

    m_interface->getAttributeRdMGpuMemType(
        arrays.data(), count, m_stageAtTimeInterval, path, attrName, wherePtr, deviceId);

    for (size_t i = 0; i != count; i++)
    {
        if (VERIFY(Type(arrays[i].type).isCompatibleWith<T>()))
        {
            retval[i] = reinterpret_cast<const T*>(arrays[i].ptr);
        }
        else
        {
            retval[i] = nullptr;
        }
    }

    return retval;
}

inline std::vector<size_t> StageAtTimeInterval::getArrayAttributeSize(const Path& path, const Token& attrName) const
{
    size_t count = m_timeSamples.size();
    std::vector<size_t> sizes(count);

    m_interface->getArrayAttributeSize(sizes.data(), count, m_stageAtTimeInterval, path, attrName);

    return sizes;
}

template <typename T>
std::vector<gsl::span<const T>> StageAtTimeInterval::getArrayAttributeRd(const Path& path, const Token& attrName) const
{
    size_t count = m_timeSamples.size();
    std::vector<ConstSpanWithTypeC> arrays(count);
    std::vector<gsl::span<const T>> retval(count);

    m_interface->getArrayAttributeWithSizeRd(arrays.data(), count, m_stageAtTimeInterval, path, attrName);

    for (size_t i = 0; i != count; i++)
    {
        const T* ptr = reinterpret_cast<const T*>(arrays[i].ptr);
        if (ptr == nullptr || !VERIFY(Type(arrays[i].type).isCompatibleWith<T>()))
        {
            retval[i] = gsl::span<T>();
        }
        else
        {
            retval[i] = gsl::span<const T>(ptr, arrays[i].elementCount);
        }
    }

    return retval;
}

inline std::vector<ConstArrayAsBytes> StageAtTimeInterval::getArrayAttributeRawRd(const Path& path,
                                                                                  const Token& attrName) const
{
    size_t count = m_timeSamples.size();
    std::vector<ConstSpanWithTypeC> arrays(count);
    std::vector<ConstArrayAsBytes> retval(count);

    m_interface->getArrayAttributeWithSizeRd(arrays.data(), count, m_stageAtTimeInterval, path, attrName);

    for (size_t i = 0; i != count; i++)
    {
        const gsl::byte* ptr = reinterpret_cast<const gsl::byte*>(arrays[i].ptr);
        if (ptr == nullptr)
        {
            retval[i].arrayBytes = gsl::span<const gsl::byte>();
        }
        else
        {
            retval[i].arrayBytes = gsl::span<const gsl::byte>(ptr, arrays[i].elementCount * arrays[i].elementSize);
        }
        retval[i].bytesPerElement = arrays[i].elementSize;
        retval[i].elementType = Type(arrays[i].type);
    }

    return retval;
}


template <typename T>
std::vector<gsl::span<const T>> StageAtTimeInterval::getAttributeArrayRd(const PrimBucketList& primBucketList,
                                                                         size_t primBucketListIndex,
                                                                         const Token& attrName) const
{
    size_t count = m_timeSamples.size();
    std::vector<ConstSpanWithTypeC> outC(count);
    ConstSpanWithTypeC* outCData = outC.data();

    m_interface->getAttributeArrayRd(
        outCData, count, m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    std::vector<gsl::span<const T>> retval(count);
    size_t i = 0;
    for (ConstSpanWithTypeC array : outC)
    {
        const T* ptr = reinterpret_cast<const T*>(array.ptr);
        if (ptr == nullptr || !VERIFY(Type(array.type).isCompatibleWith<T>()))
        {
            retval[i] = gsl::span<T>();
        }
        else
        {
            retval[i] = gsl::span<const T>(ptr, array.elementCount);
        }
        i++;
    }

    return retval;
}

template <typename T>
std::vector<gsl::span<const T>> StageAtTimeInterval::getAttributeArrayRdGpu(const PrimBucketList& primBucketList,
                                                                            size_t primBucketListIndex,
                                                                            const Token& attrName,
                                                                            int deviceId) const
{
    size_t count = m_timeSamples.size();
    std::vector<ConstSpanWithTypeC> outC(count);
    ConstSpanWithTypeC* outCData = outC.data();
    m_interface->getAttributeArrayRdMGpu(outCData, count, m_stageAtTimeInterval, primBucketList.m_primBucketListId,
                                         primBucketListIndex, attrName, deviceId);

    std::vector<gsl::span<const T>> retval(count);
    size_t i = 0;
    for (ConstSpanWithTypeC array : outC)
    {
        const T* ptr = reinterpret_cast<const T*>(array.ptr);
        if (ptr == nullptr || !VERIFY(Type(array.type).isCompatibleWith<T>()))
        {
            retval[i] = gsl::span<T>();
        }
        else
        {
            retval[i] = gsl::span<const T>(ptr, array.elementCount);
        }
        i++;
    }

    return retval;
}

template <typename T>
std::vector<std::vector<gsl::span<const T>>> StageAtTimeInterval::getArrayAttributeArrayRd(
    const PrimBucketList& primBucketList, size_t primBucketListIndex, const Token& attrName) const
{
    size_t count = m_timeSamples.size();
    std::vector<ConstArrayPointersAndSizesWithTypeC> outC(count);
    ConstArrayPointersAndSizesWithTypeC* outCData = outC.data();

    m_interface->getArrayAttributeArrayWithSizesRd(
        outCData, count, m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    std::vector<std::vector<gsl::span<const T>>> retval(count);
    size_t i = 0;
    for (ConstArrayPointersAndSizesWithTypeC pointersAndSizes : outC)
    {
        size_t primCount = pointersAndSizes.elementCount;
        retval[i].resize(primCount);
        for (size_t j = 0; j != primCount; j++)
        {
            const T* ptr = reinterpret_cast<const T*>(pointersAndSizes.arrayPtrs[j]);
            if (ptr == nullptr || !VERIFY(Type(pointersAndSizes.type).isCompatibleWith<T>()))
            {
                retval[i][j] = gsl::span<const T>();
            }
            else
            {
                retval[i][j] = gsl::span<const T>(ptr, pointersAndSizes.sizes[j]);
            }
        }
        i++;
    }

    return retval;
}

inline std::vector<gsl::span<const char>> StageAtTimeInterval::getAttributeArrayRawRd(const PrimBucketList& primBucketList,
                                                                                      size_t primBucketListIndex,
                                                                                      const Token& attrName) const
{
    size_t count = m_timeSamples.size();
    std::vector<ConstSpanWithTypeC> outC(count);
    ConstSpanWithTypeC* outCData = outC.data();

    m_interface->getAttributeArrayRd(
        outCData, count, m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    std::vector<gsl::span<const char>> retval(count);
    size_t i = 0;
    for (ConstSpanWithTypeC array : outC)
    {
        const char* ptr = reinterpret_cast<const char*>(array.ptr);
        if (ptr == nullptr)
        {
            retval[i] = gsl::span<const char>();
        }
        else
        {
            retval[i] = gsl::span<const char>(ptr, array.elementCount * array.elementSize);
        }
        i++;
    }

    return retval;
}

inline std::vector<gsl::span<const Path>> StageAtTimeInterval::getPathArray(const PrimBucketList& primBucketList,
                                                                            size_t primBucketListIndex) const
{
    size_t count = m_timeSamples.size();
    std::vector<ConstPathCSpan> outC(count);
    ConstPathCSpan* outCData = outC.data();

    m_interface->getPathArray(
        outCData, count, m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex);

    std::vector<gsl::span<const Path>> retval(count);
    size_t i = 0;
    for (ConstPathCSpan arrayC : outC)
    {
        const Path* ptr = reinterpret_cast<const Path*>(arrayC.ptr);
        if (ptr == nullptr)
        {
            retval[i] = gsl::span<const Path>();
        }
        else
        {
            retval[i] = gsl::span<const Path>(ptr, arrayC.elementCount);
        }
        i++;
    }

    return retval;
}

inline std::vector<const Connection*> StageAtTimeInterval::getConnectionRd(const Path& path,
                                                                           const Token& connectionName) const
{
    size_t count = m_timeSamples.size();
    std::vector<const Connection*> retval(count);
    const void** retvalData = reinterpret_cast<const void**>(retval.data());
    m_interface->getConnectionRd(retvalData, count, m_stageAtTimeInterval, path, connectionName);
    return retval;
}


inline std::vector<size_t> StageAtTimeInterval::getAttributeCounts(const PrimBucketList& primBucketList,
                                                                   size_t primBucketListIndex) const
{
    size_t count = m_timeSamples.size();
    std::vector<size_t> counts(count);
    m_interface->getAttributeCounts(
        m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex, count, counts.data());
    return counts;
}

inline std::pair<std::vector<std::vector<Token>>, std::vector<std::vector<Type>>> StageAtTimeInterval::getAttributeNamesAndTypes(
    const PrimBucketList& primBucketList, size_t primBucketListIndex) const
{
    size_t count = m_timeSamples.size();
    std::vector<std::vector<Token>> outNames(count);
    std::vector<std::vector<Type>> outTypes(count);

    std::vector<size_t> outSizes(count);
    m_interface->getAttributeCounts(
        m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex, count, outSizes.data());

    // Make array of pointers to inner arrays to allow us to call
    // getAttributeNamesAndTypes, which takes a C-style 2D array
    // not a std::vector<std::vector>.
    // Also set size of inner arrays
    std::vector<Token*> outNamesPtrs(count);
    std::vector<Type*> outTypesPtrs(count);
    for (size_t i = 0; i < count; ++i)
    {
        outNames[i].resize(outSizes[i]);
        outTypes[i].resize(outSizes[i]);
        outNamesPtrs[i] = outNames[i].data();
        outTypesPtrs[i] = outTypes[i].data();
    }

    m_interface->getAttributeNamesAndTypes(m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex,
                                           count, outSizes.data(), outNamesPtrs.data(), outTypesPtrs.data());
    return { outNames, outTypes };
}


inline size_t StageAtTimeInterval::getAttributeCount(const PrimBucketList& primBucketList,
                                                     size_t primBucketListIndex,
                                                     size_t timesampleIndex) const
{
    return m_interface->getAttributeCountForTimesample(
        m_stageAtTimeInterval, primBucketList.m_primBucketListId, primBucketListIndex, timesampleIndex);
}

inline std::pair<std::vector<Token>, std::vector<Type>> StageAtTimeInterval::getAttributeNamesAndTypes(
    const PrimBucketList& primBucketList, size_t primBucketListIndex, size_t timesampleIndex) const
{

    size_t attributeCount = getAttributeCount(primBucketList, primBucketListIndex, timesampleIndex);
    std::vector<Token> outNames(attributeCount);
    std::vector<Type> outTypes(attributeCount);

    m_interface->getAttributeNamesAndTypesForTimesample(m_stageAtTimeInterval, primBucketList.m_primBucketListId,
                                                        primBucketListIndex, timesampleIndex, attributeCount,
                                                        outNames.data(), outTypes.data());
    return { outNames, outTypes };
}

inline void StageAtTimeInterval::exportUsd(UsdStageId usdStageId) const
{
    m_interface->exportUsd(m_stageAtTimeInterval, usdStageId);
}

inline uint64_t StageAtTimeInterval::writeCacheToDisk(const char* file,
                                                      uint8_t* workingBuffer,
                                                      uint64_t workingBufferSize) const
{
    return m_interface->writeCacheToDisk(m_stageAtTimeInterval, file, workingBuffer, workingBufferSize);
}

inline void StageAtTimeInterval::addRefCount()
{
    return m_interface->addRefCount(m_stageAtTimeInterval);
}

inline bool StageAtTimeInterval::removeRefCount()
{
    return m_interface->removeRefCount(m_stageAtTimeInterval);
}

inline unsigned int StageAtTimeInterval::getRefCount()
{
    return m_interface->getRefCount(m_stageAtTimeInterval);
}

// Dummy function to force template instatiation at least once to get compiler checking
inline void DONOTCALL_instantiateSTTI(const StageAtTimeInterval& stti,
                                      const Path& path,
                                      const Token& attrName,
                                      const PrimBucketList& pbl)
{
    std::vector<const int*> out1 = stti.getAttributeRd<int>(path, attrName);
    CARB_UNUSED(out1);
    std::vector<const int*> out2 = stti.getAttributeRdGpu<int>(path, attrName);
    CARB_UNUSED(out2);
    std::vector<gsl::span<const int>> out3 = stti.getArrayAttributeRd<int>(path, attrName);
    CARB_UNUSED(out3);
    std::vector<gsl::span<const int>> out4 = stti.getAttributeArrayRd<int>(pbl, 0, attrName);
    CARB_UNUSED(out4);
    std::vector<gsl::span<const int>> out5 = stti.getAttributeArrayRdGpu<int>(pbl, 0, attrName);
    CARB_UNUSED(out5);
    std::vector<std::vector<gsl::span<const int>>> out6 = stti.getArrayAttributeArrayRd<int>(pbl, 0, attrName);
    CARB_UNUSED(out6);
}

} // namespace fabric
} // namespace omni
