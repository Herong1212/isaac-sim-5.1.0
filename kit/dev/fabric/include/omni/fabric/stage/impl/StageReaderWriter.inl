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

//-------------------- Creation/Metadata-------------------------------------

inline StageReaderWriter::StageReaderWriter()
{
    m_interface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_interface);
    m_stageReaderWriter = kInvalidStageReaderWriterId;
}

inline StageReaderWriter::StageReaderWriter(StageReaderWriterId stageId)
{
    m_interface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_interface);
    m_stageReaderWriter = stageId;
}

inline StageReaderWriter::StageReaderWriter(FabricId id)
{
    m_interface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_interface);
    m_stageReaderWriter = m_interface->createOrGetFromFabricId(id);
}

inline StageReaderWriter::StageReaderWriter(const StageReaderWriter& other)
{
    m_interface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_interface);
    m_stageReaderWriter = other.m_stageReaderWriter;
}
inline StageReaderWriter& StageReaderWriter::operator=(const StageReaderWriter& other)
{
    m_interface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_interface);
    m_stageReaderWriter = other.m_stageReaderWriter;
    return *this;
}

inline StageReaderWriter::StageReaderWriter(StageReaderWriter&& other)
{
    m_interface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_interface);
    m_stageReaderWriter = other.m_stageReaderWriter;
    other.m_stageReaderWriter = kInvalidStageReaderWriterId;
}
inline StageReaderWriter& StageReaderWriter::operator=(StageReaderWriter&& other)
{
    m_interface = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
    CARB_ASSERT(m_interface);
    m_stageReaderWriter = other.m_stageReaderWriter;
    other.m_stageReaderWriter = kInvalidStageReaderWriterId;
    return *this;
}

inline StageReaderWriter::~StageReaderWriter()
{
}

inline FabricId StageReaderWriter::getFabricId() const
{
    return m_interface->getFabricId(m_stageReaderWriter);
}

inline StageReaderWriterId StageReaderWriter::getId() const
{
    return m_stageReaderWriter;
}

inline void StageReaderWriter::printBucketNames() const
{
    m_interface->printBucketNames(m_stageReaderWriter);
}

//-------------------------------Prims/Attributes-------------------------------

inline bool StageReaderWriter::primExists(const Path& path)
{
    bool retval = m_interface->primExists(m_stageReaderWriter, path);
    return retval;
}

inline ValidMirrors StageReaderWriter::getAttributeValidBits(const Path& path, const Token& attrName) const
{
    return m_interface->getAttributeValidBits(m_stageReaderWriter, path, attrName);
}

template <typename T>
T* StageReaderWriter::getAttribute(const Path& path, const Token& attrName)
{
    SpanWithTypeC spanWithType = m_interface->getAttribute(m_stageReaderWriter, path, attrName);

    if (spanWithType.isValid())
    {
        return spanWithType.getTypedPointer<T>();
    }

    return nullptr;
}

// Specialization for Path (relationships)
// We used to store relationships as single paths, not arrays of paths
// To be backward compatible we do the following hack to allow the first
// element of a relationship array to be accessed as if it were a non-array attribute
template <>
inline Path* StageReaderWriter::getAttribute<Path>(const Path& path, const Token& attrName)
{
    // Make sure that the array has at least one element
    size_t oldElemCount = m_interface->getArrayAttributeSize(m_stageReaderWriter, path, attrName);
    if (oldElemCount == 0)
    {
        m_interface->setArrayAttributeSize(m_stageReaderWriter, path, attrName, 1);
    }

    SpanWithTypeC arrayData = m_interface->getArrayAttribute(m_stageReaderWriter, path, attrName);

    // Make sure that the pointer points to a Path before we reinterpret_cast
    if (Type(arrayData.type).baseType != BaseDataType::eRelationship || arrayData.elementCount == 0 ||
        arrayData.elementSize != sizeof(Path))
        return nullptr;

    Path* firstPathPtr = reinterpret_cast<Path*>(arrayData.ptr);
    return firstPathPtr;
}

template <typename T>
const T* StageReaderWriter::getAttributeRd(const Path& path, const Token& attrName)
{
    ConstSpanWithTypeC spanWithType = m_interface->getAttributeRd(m_stageReaderWriter, path, attrName);

    if (spanWithType.isValid())
    {
        return spanWithType.getTypedPointer<T>();
    }

    return nullptr;
}

inline void StageReaderWriter::setPrimTypeName(const Path& path, const Token& typeName)
{
    m_interface->setPrimTypeName(m_stageReaderWriter, path, typeName);
}

inline Token StageReaderWriter::getPrimTypeName(const Path& path)
{
    TokenC typeName = m_interface->getPrimTypeName(m_stageReaderWriter, path);
    return Token(typeName);
}

inline std::pair<std::vector<Token>, std::vector<Type>> StageReaderWriter::getAttributeNamesAndTypes(const Path& path)
{
    std::vector<Token> outNames;
    std::vector<Type> outTypes;

    size_t count = m_interface->getAttributeCount(m_stageReaderWriter, path);
    outNames.resize(count);
    outTypes.resize(count);

    m_interface->getAttributeNamesAndTypes(outNames.data(), outTypes.data(), count, m_stageReaderWriter, path);

    return { outNames, outTypes };
}

// Specialization for Path (relationships)
// We used to store relationships as single paths, not arrays of paths
// To be backward compatible we do the following hack to allow the first
// element of a relationship array to be accessed as if it were a non-array attribute
template <>
inline const Path* StageReaderWriter::getAttributeRd<Path>(const Path& path, const Token& attrName)
{
    ConstSpanWithTypeC arrayData = m_interface->getArrayAttributeRd(m_stageReaderWriter, path, attrName);

    // Make sure that the pointer points to a Path before we reinterpret_cast
    if (Type(arrayData.type).baseType != BaseDataType::eRelationship || arrayData.elementCount == 0 ||
        arrayData.elementSize != sizeof(Path))
        return nullptr;

    const Path* firstPathPtr = reinterpret_cast<const Path*>(arrayData.ptr);
    return firstPathPtr;
}

template <typename T>
T* StageReaderWriter::getAttributeWr(const Path& path, const Token& attrName)
{
    SpanWithTypeC spanWithType = m_interface->getAttributeWr(m_stageReaderWriter, path, attrName);

    if (spanWithType.isValid())
    {
        return spanWithType.getTypedPointer<T>();
    }

    return nullptr;
}

// Specialization for Path (relationships)
// We used to store relationships as single paths, not arrays of paths
// To be backward compatible we do the following hack to allow the first
// element of a relationship array to be accessed as if it were a non-array attribute
template <>
inline Path* StageReaderWriter::getAttributeWr<Path>(const Path& path, const Token& attrName)
{
    // Make sure that the array has at least one element
    size_t oldElemCount = m_interface->getArrayAttributeSize(m_stageReaderWriter, path, attrName);
    if (oldElemCount == 0)
    {
        m_interface->setArrayAttributeSize(m_stageReaderWriter, path, attrName, 1);
    }

    SpanWithTypeC arrayData = m_interface->getArrayAttributeWr(m_stageReaderWriter, path, attrName);

    // Make sure that the pointer points to a Path before we reinterpret_cast
    if (Type(arrayData.type).baseType != BaseDataType::eRelationship || arrayData.elementCount == 0 ||
        arrayData.elementSize != sizeof(Path))
        return nullptr;

    Path* firstPathPtr = reinterpret_cast<Path*>(arrayData.ptr);
    return firstPathPtr;
}

template <typename T>
T* StageReaderWriter::getAttributeGpu(const Path& path, const Token& attrName, int deviceId)
{
    SpanWithTypeC spanWithType = m_interface->getAttributeMGpu(m_stageReaderWriter, path, attrName, deviceId);

    if (spanWithType.isValid())
    {
        return spanWithType.getTypedPointer<T>();
    }
    
    return nullptr;
}

template <typename T>
const T* StageReaderWriter::getAttributeRdGpu(const Path& path, const Token& attrName, int deviceId)
{
    ConstSpanWithTypeC spanWithType = m_interface->getAttributeRdMGpu(m_stageReaderWriter, path, attrName, deviceId);

    if (spanWithType.isValid())
    {
        return spanWithType.getTypedPointer<T>();
    }

    return nullptr;
}

template <typename T>
T* StageReaderWriter::getAttributeWrGpu(const Path& path, const Token& attrName, int deviceId)
{
    SpanWithTypeC spanWithType = m_interface->getAttributeWrMGpu(m_stageReaderWriter, path, attrName, deviceId);

    if (spanWithType.isValid())
    {
        return spanWithType.getTypedPointer<T>();
    }

    return nullptr;
}

template <typename T>
T* StageReaderWriter::getOrCreateAttributeWr(const Path& path, const Token& attrName, Type type)
{
    SpanWithTypeC spanWithType =
        m_interface->getOrCreateAttributeWr(m_stageReaderWriter, path, attrName, TypeC(type));

    if (spanWithType.isValid())
    {
        return spanWithType.getTypedPointer<T>();
    }

    return nullptr;
}

template <typename T>
gsl::span<T> StageReaderWriter::getArrayAttribute(const Path& path, const Token& attrName)
{
    SpanWithTypeC arrayData = m_interface->getArrayAttributeWr(m_stageReaderWriter, path, attrName);

    if (arrayData.isValid())
    {
        carb::cpp::span<T> span = arrayData.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

template <typename T>
gsl::span<const T> StageReaderWriter::getArrayAttributeRd(const Path& path, const Token& attrName)
{
    ConstSpanWithTypeC arrayData = m_interface->getArrayAttributeRd(m_stageReaderWriter, path, attrName);

    if (arrayData.isValid())
    {
        carb::cpp::span<const T> span = arrayData.getTypedSpan<T>();
        return gsl::span<const T>(span.data(), span.size());
    }

    return gsl::span<const T>();
}

template <typename T>
gsl::span<T> StageReaderWriter::getArrayAttributeWr(const Path& path, const Token& attrName)
{
    SpanWithTypeC arrayData = m_interface->getArrayAttributeWr(m_stageReaderWriter, path, attrName);

    if (arrayData.isValid())
    {
        carb::cpp::span<T> span = arrayData.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

inline size_t StageReaderWriter::getArrayAttributeSize(const Path& path, const Token& attrName)
{
    return m_interface->getArrayAttributeSize(m_stageReaderWriter, path, attrName);
}

inline void StageReaderWriter::setArrayAttributeSize(const Path& path, const Token& attrName, size_t elemCount)
{
    m_interface->setArrayAttributeSize(m_stageReaderWriter, path, attrName, elemCount);
}

template <typename T>
gsl::span<T> StageReaderWriter::setArrayAttributeSizeAndGet(const PrimBucketList& primBucketList,
                                                            size_t primBucketListIndex,
                                                            size_t indexInBucket,
                                                            const Token& attrName,
                                                            size_t newElemCount)
{
    SpanWithTypeC newArrayC =
        m_interface->setArrayAttributeSizeAndGet(m_stageReaderWriter, primBucketList.m_primBucketListId,
            primBucketListIndex, indexInBucket, attrName, newElemCount);

    T* ptr = reinterpret_cast<T*>(newArrayC.ptr);
    if (ptr != nullptr) // can't do a .isValid() check because elementSize is set to zero
    {
        carb::cpp::span<T> span = newArrayC.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }
    return gsl::span<T>();
}

inline size_t* StageReaderWriter::getArrayAttributeSizePtr(const Path& path, const Token& attrName)
{
    return m_interface->getArrayAttributeSizePtr(m_stageReaderWriter, path, attrName);
}

inline const size_t* StageReaderWriter::getArrayAttributeSizeRdPtr(const Path& path, const Token& attrName)
{
    return m_interface->getArrayAttributeSizeRdPtr(m_stageReaderWriter, path, attrName);
}

inline size_t* StageReaderWriter::getArrayAttributeSizeWrPtr(const Path& path, const Token& attrName)
{
    return m_interface->getArrayAttributeSizeWrPtr(m_stageReaderWriter, path, attrName);
}

inline const size_t* StageReaderWriter::getArrayAttributeSizeRdGpuPtr(const Path& path, const Token& attrName)
{
    return m_interface->getArrayAttributeSizeRdGpuPtr(m_stageReaderWriter, path, attrName);
}

inline Type StageReaderWriter::getType(const Path& path, const Token& attrName)
{
    return m_interface->getType(m_stageReaderWriter, path, attrName);
}

inline size_t StageReaderWriter::getAttributeCount(const Path& path)
{
    return m_interface->getAttributeCount(m_stageReaderWriter, path);
}

inline std::vector<AttrNameAndType> StageReaderWriter::getAttrNamesAndTypes(const Path& path)
{
    size_t count = m_interface->getAttributeCount(m_stageReaderWriter, path);
    std::vector<AttrNameAndType> out(count);

    m_interface->getAttrNamesAndTypes(out.data(), out.size(), m_stageReaderWriter, path);
    return out;
}

inline void StageReaderWriter::createPrim(const Path& path)
{
    m_interface->createPrim(m_stageReaderWriter, path);
}

inline void StageReaderWriter::createPrims(const Span<const PathC>& paths,
                                           const Span<AttrNameAndType>& attributes,
                                           CreatePrimOptions createPrimOptions)
{
    m_interface->createPrims(m_stageReaderWriter, paths, attributes, createPrimOptions);
}

inline void StageReaderWriter::destroyPrim(const Path& path)
{
    m_interface->destroyPrim(m_stageReaderWriter, path);
}

inline void StageReaderWriter::destroyPrims(Span<PathC const> paths)
{
    m_interface->destroyPrims(m_stageReaderWriter, paths.data(), paths.size());
}

inline void StageReaderWriter::movePrim(const Path& oldPath, const Path& newPath)
{
    m_interface->movePrim(m_stageReaderWriter, oldPath, newPath);
}

inline bool StageReaderWriter::attributeExists(const Path& path, const Token& attrName) const
{
    return m_interface->attributeExists(m_stageReaderWriter, path, attrName);
}

inline bool StageReaderWriter::attributeExistsWithType(const Path& path, const Token& attrName, Type type) const
{
    return m_interface->attributeExistsWithType(m_stageReaderWriter, path, attrName, TypeC(type));
}

inline void StageReaderWriter::createAttribute(const Path& path, const Token& attrName, Type type)
{
    m_interface->createAttribute(m_stageReaderWriter, path, attrName, TypeC(type));
}

template <size_t n>
inline void StageReaderWriter::createAttributes(const Path& path, std::array<AttrNameAndType, n> attributes)
{
    std::array<TokenC, n> names;
    std::array<TypeC, n> types;

    for (size_t c = 0; c < n; ++c)
    {
        names[c] = attributes[c].name;
        types[c] = TypeC(attributes[c].type);
    }

    m_interface->createAttributes(m_stageReaderWriter, path, names.data(), types.data(), n);
}

inline void StageReaderWriter::createAttributes(const Path& path, std::vector<AttrNameAndType> attributes)
{
    std::vector<TokenC> names(attributes.size());
    std::vector<TypeC> types(attributes.size());

    for (size_t c = 0; c < attributes.size(); ++c)
    {
        names[c] = attributes[c].name;
        types[c] = TypeC(attributes[c].type);
    }

    m_interface->createAttributes(m_stageReaderWriter, path, names.data(), types.data(), (uint32_t)attributes.size());
}

inline void StageReaderWriter::destroyAttribute(const Path& path, const Token& attrName, Type)
{
    m_interface->destroyAttribute2(m_stageReaderWriter, path, attrName);
}

inline void StageReaderWriter::destroyAttribute(const Path& path, const Token& attrName)
{
    m_interface->destroyAttribute2(m_stageReaderWriter, path, attrName);
}

template <size_t n>
inline void StageReaderWriter::destroyAttributes(const Path& path, const std::array<Token, n>& attributes)
{
    std::array<TokenC, n> names;

    for (size_t c = 0; c < n; ++c)
    {
        names[c] = TokenC(attributes[c]);
    }

    m_interface->destroyAttributes(m_stageReaderWriter, path, names.data(), n);
}

inline void StageReaderWriter::destroyAttributes(const Path& path, const std::vector<Token>& attributes)
{
    const size_t n = attributes.size();
    std::vector<TokenC> names(n);

    for (size_t c = 0; c < n; ++c)
    {
        names[c] = TokenC(attributes[c]);
    }

    m_interface->destroyAttributes(m_stageReaderWriter, path, names.data(), (uint32_t)n);
}

inline void StageReaderWriter::createTag(const Path& path, const Token& attrName)
{
    const Type tagType(BaseDataType::eTag);
    createAttribute(path, attrName, tagType);
}

inline void StageReaderWriter::destroyTag(const Path& path, const Token& attrName)
{
    CARB_ASSERT(tagExists(path, attrName));
    const Type tagType(BaseDataType::eTag);
    destroyAttribute(path, attrName, tagType);
}

inline bool StageReaderWriter::tagExists(const Path& path, const Token& attrName) const
{
    const Type tagType(BaseDataType::eTag);
    return attributeExistsWithType(path, attrName, tagType);
}

inline PrimBucketList StageReaderWriter::allPrims()
{
    PrimBucketListId primBucketListId = m_interface->allPrims(m_stageReaderWriter);

    return PrimBucketList( primBucketListId, PrimBucketListOwnership::eOwned );
}

inline PrimBucketList StageReaderWriter::findPrims(const omni::fabric::set<AttrNameAndType>& all,
                                                   const omni::fabric::set<AttrNameAndType>& any,
                                                   const omni::fabric::set<AttrNameAndType>& none)
{
    PrimBucketListId primBucketListId = m_interface->findPrims(m_stageReaderWriter, all, any, none);

    return PrimBucketList( primBucketListId, PrimBucketListOwnership::eOwned );
}

inline Token StageReaderWriter::getBucketPrimTypeName(PrimBucketListId primBucketList, size_t primBucketListIndex)
{
    return Token(m_interface->getBucketPrimTypeName(m_stageReaderWriter, primBucketList, primBucketListIndex));
}

inline ArrayPointersAndSizesWithTypeC StageReaderWriter::getArrayAttributeArrayWithSizesGpu(
    PrimBucketListId primBucketList,
                                                                                    size_t primBucketListIndex,
                                                                                    const Token& attrName)
{
    return m_interface->getArrayAttributeArrayWithSizesGpu(
        m_stageReaderWriter, primBucketList, primBucketListIndex, attrName);
}

inline ConstArrayPointersAndSizesWithTypeC StageReaderWriter::getArrayAttributeArrayWithSizesRdGpu(
    PrimBucketListId primBucketList,
                                                                                           size_t primBucketListIndex,
                                                                                           const Token& attrName)
{
    return m_interface->getArrayAttributeArrayWithSizesRdGpu(
        m_stageReaderWriter, primBucketList, primBucketListIndex, attrName);
}

inline ArrayPointersAndSizesWithTypeC StageReaderWriter::getArrayAttributeArrayWithSizesWrGpu(
    PrimBucketListId primBucketList,
                                                                                      size_t primBucketListIndex,
                                                                                      const Token& attrName)
{
    return m_interface->getArrayAttributeArrayWithSizesWrGpu(
        m_stageReaderWriter, primBucketList, primBucketListIndex, attrName);
}

inline void StageReaderWriter::attributeEnableChangeTracking(const Token& attrName, ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    iChangeTrackerConfig->attributeEnable(m_stageReaderWriter, attrName, listenerId);
}

inline void StageReaderWriter::enablePrimCreateTracking(ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    iChangeTrackerConfig->enablePrimCreateTracking(m_stageReaderWriter, listenerId);
}

inline void StageReaderWriter::attributeDisableChangeTracking(const Token& attrName, ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    iChangeTrackerConfig->attributeDisable(m_stageReaderWriter, attrName, listenerId);
}

inline void StageReaderWriter::pauseChangeTracking(ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    iChangeTrackerConfig->pause(m_stageReaderWriter, listenerId);
}

inline void StageReaderWriter::resumeChangeTracking(ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    iChangeTrackerConfig->resume(m_stageReaderWriter, listenerId);
}

inline bool StageReaderWriter::isChangeTrackingPaused(ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    return iChangeTrackerConfig->isChangeTrackingPaused(m_stageReaderWriter, listenerId);
}

inline bool StageReaderWriter::isListenerAttached(ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    return iChangeTrackerConfig->isListenerAttached(m_stageReaderWriter, listenerId);
}

inline void StageReaderWriter::detachListener(ListenerId listenerId)
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    iChangeTrackerConfig->detachListener(m_stageReaderWriter, listenerId);
}

inline size_t StageReaderWriter::getListenerCount()
{
    auto iChangeTrackerConfig = carb::getCachedInterface<omni::fabric::IChangeTrackerConfig>();
    return iChangeTrackerConfig->getListenerCount(m_stageReaderWriter);
}

inline ChangedPrimBucketList StageReaderWriter::getChanges(ListenerId listenerId)
{
    PrimBucketListId changeListId = m_interface->getChanges(m_stageReaderWriter, listenerId);
    return ChangedPrimBucketList(changeListId, PrimBucketListOwnership::eOwned);
}

inline void StageReaderWriter::popChanges(ListenerId listenerId)
{
    m_interface->popChanges(m_stageReaderWriter, listenerId);
}

template <typename T>
gsl::span<T> StageReaderWriter::getAttributeArray(const PrimBucketList& primBucketList,
                                                  size_t primBucketListIndex,
                                                  const Token& attrName)
{
    SpanWithTypeC array;

    m_interface->getAttributeArray(
        &array, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    if (array.isValid())
    {
        carb::cpp::span<T> span = array.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

template <typename T>
Column<T> StageReaderWriter::getAttributeColumn(const PrimBucketList& primBucketList,
                                                size_t primBucketListIndex,
                                                const Token& attrName)
{
    size_t listenerCount = getListenerCount();
    std::vector<FineGrainedChangeTracker> dirtyElements(listenerCount);

    SpanWithTypeC array = m_interface->getAttributeColumn(m_stageReaderWriter, 
                                                          Span<FineGrainedChangeTracker>(dirtyElements.begin(), dirtyElements.end()),
                                                          primBucketList.m_primBucketListId, primBucketListIndex, attrName, WriteType::eModify);

    if (!array.isValid())
    {    
        return Column<T>();
    }

    carb::cpp::span<T> span = array.getTypedSpan<T>();
    return Column<T>(span.data(), span.size(), dirtyElements);
}

template <typename T>
gsl::span<const T> StageReaderWriter::getAttributeArrayRd(const PrimBucketList& primBucketList,
                                                          size_t primBucketListIndex,
                                                          const Token& attrName) const
{
    ConstSpanWithTypeC array;

    m_interface->getAttributeArrayRd(
        &array, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    if (array.isValid())
    {
        carb::cpp::span<const T> span = array.getTypedSpan<T>();
        return gsl::span<const T>(span.data(), span.size());
    }

    return gsl::span<const T>();
}

// getAttributeColumnRd intentionally does the same thing as
// getAttributeArrayRd.
// It is included just for completeness. A new user that was familar with
// columns might not know to use getAttributeArrayRd if they wanted
// read-only access.
// The return type is gsl::span<const T> instead of Column,
// because Column does fine grained write tracking, and access through this
// method does not allow writes.
template <typename T>
gsl::span<const T> StageReaderWriter::getAttributeColumnRd(const PrimBucketList& primBucketList,
                                                          size_t primBucketListIndex,
                                                          const Token& attrName) const
{
    return getAttributeArrayRd<T>(primBucketList, primBucketListIndex, attrName);
}

template <typename T>
gsl::span<T> StageReaderWriter::getAttributeArrayWr(const PrimBucketList& primBucketList,
    size_t primBucketListIndex,
    const Token& attrName)
{
    SpanWithTypeC array;

    m_interface->getAttributeArrayWr(
        &array, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    if (array.isValid())
    {
        carb::cpp::span<T> span = array.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

template <typename T>
Column<T> StageReaderWriter::getAttributeColumnWr(const PrimBucketList& primBucketList,
    size_t primBucketListIndex,
    const Token& attrName)
{
    size_t listenerCount = getListenerCount();
    std::vector<FineGrainedChangeTracker> dirtyElements(listenerCount);

    SpanWithTypeC array = m_interface->getAttributeColumn(
        m_stageReaderWriter,
        Span<FineGrainedChangeTracker>(dirtyElements.begin(), dirtyElements.end()),
        primBucketList.m_primBucketListId, primBucketListIndex, attrName, WriteType::eOverwrite);

    if (!array.isValid())
    {
        return Column<T>();
    }

    carb::cpp::span<T> span = array.getTypedSpan<T>();
    return Column<T>(span.data(), span.size(), dirtyElements);
}

template <typename T>
Column<gsl::span<T>> StageReaderWriter::getArrayAttributeColumnWr(const PrimBucketList& primBucketList,
    size_t primBucketListIndex,
    const Token& attrName)
{
    size_t listenerCount = getListenerCount();
    std::vector<FineGrainedChangeTracker> dirtyElements(listenerCount);

    ArrayPointersAndSizesWithTypeC pointersAndSizes = m_interface->getArrayAttributeColumn(
        m_stageReaderWriter, Span<FineGrainedChangeTracker>(dirtyElements.data(), dirtyElements.size()),
        primBucketList.m_primBucketListId, primBucketListIndex, attrName, WriteType::eOverwrite);

    if (!VERIFY(Type(pointersAndSizes.type).isCompatibleWith<T>()))
    {
        return Column<gsl::span<T>>();
    }

    Column<gsl::span<T>> arrays(pointersAndSizes, dirtyElements);
    return arrays;
}

template <typename T>
gsl::span<T> StageReaderWriter::getAttributeArrayGpu(const PrimBucketList& primBucketList,
                                                     size_t primBucketListIndex,
                                                     const Token& attrName,
                                                     int deviceId)
{
    SpanWithTypeC array;

    m_interface->getAttributeArrayMGpu(
        &array, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName, deviceId);

    if (array.isValid())
    {
        carb::cpp::span<T> span = array.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

template <typename T>
gsl::span<const T> StageReaderWriter::getAttributeArrayRdGpu(const PrimBucketList& primBucketList,
                                                             size_t primBucketListIndex,
                                                             const Token& attrName,
                                                             int deviceId) const
{
    ConstSpanWithTypeC array;

    m_interface->getAttributeArrayRdMGpu(
        &array, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName, deviceId);

    if (array.isValid())
    {
        carb::cpp::span<const T> span = array.getTypedSpan<T>();
        return gsl::span<const T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

template <typename T>
gsl::span<T> StageReaderWriter::getAttributeArrayWrGpu(const PrimBucketList& primBucketList,
                                                       size_t primBucketListIndex,
                                                       const Token& attrName,
                                                       int deviceId)
{
    SpanWithTypeC array;

    m_interface->getAttributeArrayWrMGpu(
        &array, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName, deviceId);

    if (array.isValid())
    {
        carb::cpp::span<T> span = array.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

template <typename T>
gsl::span<T> StageReaderWriter::getOrCreateAttributeArrayWr(const PrimBucketList& primBucketList,
                                                            size_t primBucketListIndex,
                                                            const Token& attrName,
                                                            Type type)
{
    SpanWithTypeC array;

    m_interface->getOrCreateAttributeArrayWr(
        &array, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName, type);

    if (array.isValid())
    {
        carb::cpp::span<T> span = array.getTypedSpan<T>();
        return gsl::span<T>(span.data(), span.size());
    }

    return gsl::span<T>();
}

template <typename T>
std::vector<gsl::span<T>> StageReaderWriter::getArrayAttributeArray(const PrimBucketList& primBucketList,
                                                                    size_t primBucketListIndex,
                                                                    const Token& attrName) const
{
    ArrayPointersAndSizesWithTypeC pointersAndSizes = m_interface->getArrayAttributeArrayWithSizes(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    if (!VERIFY(Type(pointersAndSizes.type).isCompatibleWith<T>()))
    {
        return std::vector<gsl::span<T>>();
    }

    size_t primCount = pointersAndSizes.elementCount;
    std::vector<gsl::span<T>> arrays(primCount);
    for (size_t i = 0; i != primCount; i++)
    {
        T* ptr = reinterpret_cast<T*>(pointersAndSizes.arrayPtrs[i]);
        const size_t size = pointersAndSizes.sizes[i];
        if (ptr == nullptr || size == 0)
        {
            arrays[i] = gsl::span<T>();
        }
        else
        {
            arrays[i] = gsl::span<T>(ptr, size);
        }
    }

    return arrays;
}

template <typename T>
Column<gsl::span<T>> StageReaderWriter::getArrayAttributeColumn(const PrimBucketList& primBucketList,
                                                                size_t primBucketListIndex,
                                                                const Token& attrName)
{
    size_t listenerCount = getListenerCount();
    std::vector<FineGrainedChangeTracker> dirtyElements(listenerCount);

    ArrayPointersAndSizesWithTypeC pointersAndSizes = m_interface->getArrayAttributeColumn(
        m_stageReaderWriter, Span<FineGrainedChangeTracker>(dirtyElements.begin(), dirtyElements.end()),
        primBucketList.m_primBucketListId, primBucketListIndex, attrName, WriteType::eModify);

    if (!VERIFY(Type(pointersAndSizes.type).isCompatibleWith<T>()))
    {
        return Column<gsl::span<T>>();
    }

    Column<gsl::span<T>> arrays(pointersAndSizes, dirtyElements);

    return arrays;
}

template <typename T>
std::vector<gsl::span<const T>> StageReaderWriter::getArrayAttributeArrayRd(const PrimBucketList& primBucketList,
                                                                            size_t primBucketListIndex,
                                                                            const Token& attrName) const
{
    ConstArrayPointersAndSizesWithTypeC pointersAndSizes = m_interface->getArrayAttributeArrayWithSizesRd(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    if (!VERIFY(Type(pointersAndSizes.type).isCompatibleWith<T>()))
    {
        return std::vector<gsl::span<const T>>();
    }

    size_t primCount = pointersAndSizes.elementCount;
    std::vector<gsl::span<const T>> arrays(primCount);
    for (size_t i = 0; i != primCount; i++)
    {
        const T* ptr = reinterpret_cast<const T*>(pointersAndSizes.arrayPtrs[i]);
        const size_t size = pointersAndSizes.sizes[i];
        if (ptr == nullptr || size == 0)
        {
            arrays[i] = gsl::span<const T>();
        }
        else
        {
            arrays[i] = gsl::span<const T>(ptr, size);
        }
    }

    return arrays;
}


// getArrayAttributeColumnRd intentionally does the same thing as
// getArrayAttributeArrayRd.
// It is included just for completeness. A new user that was familar with
// columns might not know to use getArrayAttributeArrayRd if they wanted
// read-only access.
// The return type is std::vector<gsl::span<const T>> instead of Column,
// because Column does fine grained write tracking, and access through this
// method does not allow writes.
template <typename T>
std::vector<gsl::span<const T>> StageReaderWriter::getArrayAttributeColumnRd(const PrimBucketList& primBucketList,
                                                                             size_t primBucketListIndex,
                                                                             const Token& attrName) const
{
    return getArrayAttributeArrayRd<T>(
        primBucketList, primBucketListIndex, attrName);
}

template <typename T>
std::vector<std::pair<gsl::span<const T>, ContentHashType>> StageReaderWriter::getArrayAttributeArrayOrHashRd(const PrimBucketList& primBucketList,
    size_t primBucketListIndex,
    const Token& attrName) const
{
    ConstArrayPointersAndSizesWithTypeC pointersAndSizes = m_interface->getSparseArrayAttributeArrayWithSizesRd(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);
    Span<const ContentHashType> hashes = m_interface->getArrayAttributeContentHashes(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    if (!VERIFY(Type(pointersAndSizes.type).isCompatibleWith<T>()))
    {
        return std::vector<std::pair<gsl::span<const T>, ContentHashType>>();
    }

    size_t primCount = pointersAndSizes.elementCount;
    std::vector<std::pair<gsl::span<const T>, ContentHashType>> arrays(primCount);

    auto assignSpan = [&pointersAndSizes, &arrays](size_t i)
    {
        const T* ptr = reinterpret_cast<const T*>(pointersAndSizes.arrayPtrs[i]);
        const size_t size = pointersAndSizes.sizes[i];
        if (ptr == nullptr || size == 0)
        {
            arrays[i].first = gsl::span<const T>();
        }
        else
        {
            arrays[i].first = gsl::span<const T>(ptr, size);
        }
    };

    size_t hashCount = hashes.size();
    for (size_t i = 0; i != hashCount; i++)
    {
        assignSpan(i);
        arrays[i].second = hashes[i];
    }
    for (size_t i = hashCount; i != primCount; i++)
    {
        assignSpan(i);
        arrays[i].second = {};
    }

    return arrays;
}

inline std::vector<ContentHashType> StageReaderWriter::getArrayAttributeHashRd(const PrimBucketList& primBucketList,
                                                                               size_t primBucketListIndex,
                                                                               const Token& attrName) const
{
    ConstArrayPointersAndSizesWithTypeC pointersAndSizes = m_interface->getSparseArrayAttributeArrayWithSizesRd(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    Span<const ContentHashType> hashes = m_interface->getArrayAttributeContentHashes(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    size_t primCount = pointersAndSizes.elementCount;
    std::vector<ContentHashType> arrays(primCount);

    size_t hashCount = hashes.size();
    for (size_t i = 0; i != hashCount; i++)
    {
        arrays[i] = hashes[i];
    }
    for (size_t i = hashCount; i != primCount; i++)
    {
        arrays[i] = {};
    }

    return arrays;
}

template <typename T>
std::vector<gsl::span<T>> StageReaderWriter::getArrayAttributeArrayWr(const PrimBucketList& primBucketList,
                                                                      size_t primBucketListIndex,
                                                                      const Token& attrName) const
{
    ArrayPointersAndSizesWithTypeC pointersAndSizes = m_interface->getArrayAttributeArrayWithSizesWr(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName);

    if (!VERIFY(Type(pointersAndSizes.type).isCompatibleWith<T>()))
    {
        return std::vector<gsl::span<T>>();
    }

    size_t primCount = pointersAndSizes.elementCount;
    std::vector<gsl::span<T>> arrays(primCount);
    for (size_t i = 0; i != primCount; i++)
    {
        T* ptr = reinterpret_cast<T*>(pointersAndSizes.arrayPtrs[i]);
        const size_t size = pointersAndSizes.sizes[i];
        if (ptr == nullptr || size == 0)
        {
            arrays[i] = gsl::span<T>();
        }
        else
        {
            arrays[i] = gsl::span<T>(ptr, size);
        }
    }

    return arrays;
}

inline void StageReaderWriter::dirtyAttribute(const PrimBucketList& primBucketList,
                                                size_t primBucketListIndex,
                                                const Token& attrName,
                                                size_t beginElem, size_t endElem) const
{
    m_interface->dirtyAttribute(m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex, attrName, beginElem, endElem);
}


inline gsl::span<const Path> StageReaderWriter::getPathArray(const PrimBucketList& primBucketList,
                                                             size_t primBucketListIndex) const
{
    ConstPathCSpan arrayC;

    m_interface->getPathArray(&arrayC, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex);

    const Path* ptr = reinterpret_cast<const Path*>(arrayC.ptr);
    if (ptr == nullptr)
    {
        return gsl::span<const Path>();
    }

    return gsl::span<const Path>(ptr, arrayC.elementCount);
}


inline void StageReaderWriter::logAttributeWriteForNotice(const Path& path, const Token& attrName)
{
    m_interface->logAttributeWriteForNotice(m_stageReaderWriter, path, attrName);
}


inline omni::fabric::set<AttrNameAndType> StageReaderWriter::getAttributeNamesAndTypes(const PrimBucketList& primBucketList,
                                                                                       size_t primBucketListIndex) const
{
    size_t attrCount = m_interface->getBucketAttributeCount(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex);

    omni::fabric::set<AttrNameAndType> namesAndTypes;
    namesAndTypes.v.resize(attrCount);
    // getBucketAttributeNamesAndTypes is guaranteed to return an ordered vector, so we don't have to sort namesAndTypes
    m_interface->getBucketAttributeNamesAndTypes(
        namesAndTypes.data(), attrCount, m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex);

    return namesAndTypes;
}

inline Token StageReaderWriter::getPrimTypeName(const PrimBucketList& primBucketList, size_t primBucketListIndex) const
{
    TokenC retval =
        m_interface->getBucketPrimTypeName(m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex);
    return Token(retval);
}

inline size_t StageReaderWriter::getBucketPrimCount(PrimBucketListId primBucketList,
                                                    size_t primBucketListIndex,
                                                    const Token& attrName)
{
    return m_interface->getBucketPrimCount(m_stageReaderWriter, primBucketList, primBucketListIndex, attrName);
}

inline size_t StageReaderWriter::getBucketAttributeCount(PrimBucketListId primBucketList, size_t primBucketListIndex)
{
    return m_interface->getBucketAttributeCount(m_stageReaderWriter, primBucketList, primBucketListIndex);
}

inline std::vector<AttrNameAndType> StageReaderWriter::getBucketAttributeNamesAndTypes(PrimBucketListId primBucketList,
                                                                                       size_t primBucketListIndex)
{
    size_t count = m_interface->getBucketAttributeCount(m_stageReaderWriter, primBucketList, primBucketListIndex);
    std::vector<AttrNameAndType> out(count);
    m_interface->getBucketAttributeNamesAndTypes(
        out.data(), out.size(), m_stageReaderWriter, primBucketList, primBucketListIndex);
    return out;
}

inline size_t StageReaderWriter::getAttributeCount(const PrimBucketList& primBucketList, size_t primBucketListIndex) const
{

    const size_t attrCount = m_interface->getBucketAttributeCount(
        m_stageReaderWriter, primBucketList.m_primBucketListId, primBucketListIndex);
    return attrCount;
}

// Connection API
inline void StageReaderWriter::createConnection(const Path& path, const Token& connectionName, const Connection& connection)
{
    m_interface->createConnection(m_stageReaderWriter, path, connectionName, connection);
}

inline void StageReaderWriter::createConnections(const Path& path,
                                                 const gsl::span<Token>& connectionNames,
                                                 const gsl::span<Connection>& connections)
{
    if (connectionNames.size() != connections.size())
        return;
    const TokenC* namesC = reinterpret_cast<const TokenC*>(connectionNames.data());
    m_interface->createConnections(m_stageReaderWriter, path, namesC, connections.data(), connectionNames.size());
}


inline void StageReaderWriter::destroyConnection(const Path& path, const Token& connectionName)
{
    m_interface->destroyConnection(m_stageReaderWriter, path, connectionName);
}

inline void StageReaderWriter::destroyConnections(const Path& path, const gsl::span<Token>& connectionNames)
{
    const TokenC* namesC = reinterpret_cast<const TokenC*>(connectionNames.data());
    m_interface->destroyConnections(m_stageReaderWriter, path, namesC, connectionNames.size());
}

inline Connection* StageReaderWriter::getConnection(const Path& path, const Token& connectionName)
{
    return m_interface->getConnection(m_stageReaderWriter, path, connectionName);
}

inline const Connection* StageReaderWriter::getConnectionRd(const Path& path, const Token& connectionName)
{
    return m_interface->getConnectionRd(m_stageReaderWriter, path, connectionName);
}

inline Connection* StageReaderWriter::getConnectionWr(const Path& path, const Token& connectionName)
{
    return m_interface->getConnectionWr(m_stageReaderWriter, path, connectionName);
}

inline void StageReaderWriter::copyAttributes(const Path& srcPath, const Path& dstPath)
{
    m_interface->copyAllAttributes(m_stageReaderWriter, srcPath, dstPath);
}

inline void StageReaderWriter::copyAttributes(const Path& srcPath, const gsl::span<Token>& srcAttrs, const Path& dstPath)
{
    size_t n = srcAttrs.size();
    const TokenC* srcAttrsC = reinterpret_cast<const TokenC*>(srcAttrs.data());
    m_interface->copySpecifiedAttributes(m_stageReaderWriter, srcPath, srcAttrsC, dstPath, srcAttrsC, n);
}

inline void StageReaderWriter::copyAttributes(const Path& srcPath,
                                              const gsl::span<Token>& srcAttrs,
                                              const Path& dstPath,
                                              const gsl::span<Token>& dstAttrs)
{
    if (srcAttrs.size() != dstAttrs.size())
    {
        return;
    }
    size_t n = srcAttrs.size();
    const TokenC* srcAttrsC = reinterpret_cast<const TokenC*>(srcAttrs.data());
    const TokenC* dstAttrsC = reinterpret_cast<const TokenC*>(dstAttrs.data());
    m_interface->copySpecifiedAttributes(m_stageReaderWriter, srcPath, srcAttrsC, dstPath, dstAttrsC, n);
}

inline void DONOTCALL_instantiateSRW(StageReaderWriter& srw, const Path& path, const Token& attrName)
{
    int* x0 = srw.getAttribute<int>(path, attrName);
    CARB_UNUSED(x0);
    const int* x1 = srw.getAttributeRd<int>(path, attrName);
    CARB_UNUSED(x1);
    int* x2 = srw.getAttributeWr<int>(path, attrName);
    CARB_UNUSED(x2);

    int* x3 = srw.getAttributeGpu<int>(path, attrName);
    CARB_UNUSED(x3);
    const int* x4 = srw.getAttributeRdGpu<int>(path, attrName);
    CARB_UNUSED(x4);
    int* x5 = srw.getAttributeWrGpu<int>(path, attrName);
    CARB_UNUSED(x5);

    int* x6 = srw.getOrCreateAttributeWr<int>(path, attrName, { BaseDataType::eInt, 1, 0, AttributeRole::eNone });
    CARB_UNUSED(x6);

    gsl::span<int> x7 = srw.getArrayAttribute<int>(path, attrName);
    CARB_UNUSED(x7);
    gsl::span<const int> x8 = srw.getArrayAttributeRd<int>(path, attrName);
    CARB_UNUSED(x8);
    gsl::span<int> x9 = srw.getArrayAttributeWr<int>(path, attrName);
    CARB_UNUSED(x9);

    PrimBucketList pbl = srw.findPrims({}, {}, {});
    gsl::span<int> x10 = srw.setArrayAttributeSizeAndGet<int>(pbl, 0, 0, attrName, 1);
    CARB_UNUSED(x10);
    gsl::span<int> x11 = srw.getAttributeArray<int>(pbl, 0, attrName);
    CARB_UNUSED(x11);
    gsl::span<const int> x12 = srw.getAttributeArrayRd<int>(pbl, 0, attrName);
    CARB_UNUSED(x12);
    gsl::span<int> x13 = srw.getAttributeArrayWr<int>(pbl, 0, attrName);
    CARB_UNUSED(x13);
    gsl::span<int> x14 = srw.getAttributeArrayGpu<int>(pbl, 0, attrName);
    CARB_UNUSED(x14);
    gsl::span<const int> x15 = srw.getAttributeArrayRdGpu<int>(pbl, 0, attrName);
    CARB_UNUSED(x15);
    gsl::span<int> x16 = srw.getAttributeArrayWrGpu<int>(pbl, 0, attrName);
    CARB_UNUSED(x16);

    gsl::span<int> x17 =
        srw.getOrCreateAttributeArrayWr<int>(pbl, 0, attrName, { BaseDataType::eInt, 1, 1, AttributeRole::eNone });
    CARB_UNUSED(x17);

    std::vector<gsl::span<int>> x18 = srw.getArrayAttributeArray<int>(pbl, 0, attrName);
    CARB_UNUSED(x18);
    std::vector<gsl::span<const int>> x19 = srw.getArrayAttributeArrayRd<int>(pbl, 0, attrName);
    CARB_UNUSED(x19);
    std::vector<gsl::span<int>> x20 = srw.getArrayAttributeArrayWr<int>(pbl, 0, attrName);
    CARB_UNUSED(x20);

    Column<int> x21 = srw.getAttributeColumn<int>(pbl, 0, attrName);
    CARB_UNUSED(x21);
    gsl::span<const int> x22 = srw.getAttributeColumnRd<int>(pbl, 0, attrName);
    CARB_UNUSED(x22);
    Column<int> x23 = srw.getAttributeColumnWr<int>(pbl, 0, attrName);
    CARB_UNUSED(x23);

    Column<gsl::span<int>> x24 = srw.getArrayAttributeColumn<int>(pbl, 0, attrName);
    CARB_UNUSED(x24);
    std::vector<gsl::span<const int>> x25 = srw.getArrayAttributeColumnRd<int>(pbl, 0, attrName);
    CARB_UNUSED(x25);
    Column<gsl::span<int>> x26 = srw.getArrayAttributeColumnWr<int>(pbl, 0, attrName);
    CARB_UNUSED(x26);
}

inline void StageReaderWriter::commit()
{
    m_interface->commit(m_stageReaderWriter);
}

inline size_t StageReaderWriter::getMutableEntityCount() const
{
    return m_interface->getMutableEntityCount(m_stageReaderWriter);
}

inline size_t StageReaderWriter::registerToken(const Token& token)
{
    size_t index = static_cast<size_t>(-1);
    m_interface->registerTokens(m_stageReaderWriter, {&token, 1}, {&index, 1});
    return index;
}

inline void StageReaderWriter::registerTokens(const gsl::span<const Token>& tokens,
    const gsl::span<size_t>& indexes)
{
    m_interface->registerTokens(m_stageReaderWriter, {tokens.data(), tokens.size()}, {indexes.data(), indexes.size()});
}

inline size_t StageReaderWriter::registerPath(const Path& path)
{
    size_t index = static_cast<size_t>(-1);
    m_interface->registerPaths(m_stageReaderWriter, {&path, 1}, {&index, 1});
    return index;
}

inline void StageReaderWriter::registerPaths(const gsl::span<const Path>& paths,
    const gsl::span<size_t>& indexes)
{
    m_interface->registerPaths(m_stageReaderWriter, {paths.data(), paths.size()}, {indexes.data(), indexes.size()});
}

inline bool StageReaderWriter::acceptBucket(const PrimBucketList& primBucketList, size_t bucketIndex,
    const omni::fabric::set<AttrNameAndType>& all,
    const omni::fabric::set<AttrNameAndType>& any,
    const omni::fabric::set<AttrNameAndType>& none)
{
    return m_interface->acceptBucket(m_stageReaderWriter, primBucketList.getId(), bucketIndex, all, any, none);
}

} // namespace fabric
} // namespace omni
