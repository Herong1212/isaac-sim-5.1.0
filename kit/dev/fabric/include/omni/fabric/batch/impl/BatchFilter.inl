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
namespace batch
{

inline AttributeRef BatchFilter::readAttribute(const omni::fabric::AttrNameAndType& nameAndType)
{
    Options options;
    options.filter = FilterMode::Include;
    options.access = DataAccessMode::Read;
    options.nameAndType = nameAndType;

    return addOptions(std::move(options));
}

inline AttributeRef BatchFilter::writeAttribute(const omni::fabric::AttrNameAndType& nameAndType)
{
    Options options;
    options.filter = FilterMode::Include;
    options.access = DataAccessMode::Write;
    options.nameAndType = nameAndType;

    return addOptions(std::move(options));
}

inline AttributeRef BatchFilter::readWriteAttribute(const omni::fabric::AttrNameAndType& nameAndType)
{
    Options options;
    options.filter = FilterMode::Include;
    options.access = DataAccessMode::ReadWrite;
    options.nameAndType = nameAndType;

    return addOptions(std::move(options));
}

inline AttributeRef BatchFilter::createAttribute(const omni::fabric::AttrNameAndType& nameAndType)
{
    // TODO: We enforce NameSuffix::none here because iStageReaderWriter::createAttributes does not allow NameSuffix
    // to be specified.
    CARB_ASSERT(nameAndType.suffix == NameSuffix::none);

    Options options;
    options.filter = FilterMode::Create;
    options.access = DataAccessMode::Write;
    options.nameAndType = nameAndType;

    return addOptions(std::move(options));
}

inline AttributeRef BatchFilter::excludeAttribute(const omni::fabric::AttrNameAndType& nameAndType)
{
    Options options;
    options.filter = FilterMode::Exclude;
    options.access = DataAccessMode::NoAccess;
    options.nameAndType = nameAndType;

    return addOptions(std::move(options));
}

inline void BatchFilter::includeTag(const omni::fabric::AttrNameAndType& nameAndType)
{
    Options options;
    options.filter = FilterMode::Include;
    options.access = DataAccessMode::NoAccess;
    options.ref = ATTRIBUTE_REF_MAX;
    options.nameAndType = nameAndType;

    addOptions(std::move(options));
}

inline void BatchFilter::excludeTag(const omni::fabric::AttrNameAndType& nameAndType)
{
    Options options;
    options.filter = FilterMode::Exclude;
    options.access = DataAccessMode::NoAccess;
    options.ref = ATTRIBUTE_REF_MAX;
    options.nameAndType = nameAndType;

    addOptions(std::move(options));
}

inline void BatchFilter::createTag(const omni::fabric::AttrNameAndType& nameAndType)
{
    Options options;
    options.filter = FilterMode::Create;
    options.access = DataAccessMode::NoAccess;
    options.ref = ATTRIBUTE_REF_MAX;
    options.nameAndType = nameAndType;

    addOptions(std::move(options));
}

inline AttributeRef BatchFilter::findRef(const omni::fabric::AttrNameAndType& nameAndType) const
{
    const auto iter = optionsMap.find(nameAndType);
    if (iter == optionsMap.end())
    {
        return ATTRIBUTE_REF_MAX;
    }

    return iter->second.ref;
}

inline void BatchFilter::reserve(const size_t count)
{
    optionsMap.reserve(count);
}

inline AttributeRef BatchFilter::addOptions(Options&& options)
{
    const auto& pair = optionsMap.emplace(options.nameAndType, std::move(options));
    if (!pair.second)
    {
        CARB_LOG_ERROR("BatchFilter addOptions refusing to add duplicate entry!");
        return ATTRIBUTE_REF_MAX;
    }

    // Only claim an AttributeRef if:
    // - we haven't added a duplicate
    // - we need data access
    // - we haven't exhausted our refs
    if (options.access != DataAccessMode::NoAccess)
    {
        CARB_ASSERT(nextRef < ATTRIBUTE_REF_MAX);
        if (nextRef >= ATTRIBUTE_REF_MAX)
        {
            CARB_LOG_ERROR("BatchFilter exceeded maximum AttributeRef (%u)!", ATTRIBUTE_REF_MAX);
            optionsMap.erase(pair.first);
            return ATTRIBUTE_REF_MAX;
        }

        AttributeRef ref = nextRef;
        ++nextRef;

        pair.first->second.ref = ref;
        return ref;
    }
    else
    {
        return ATTRIBUTE_REF_MAX;
    }
}

} // namespace batch
} // namespace fabric
} // namespace omni
