// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "BundleAttrib.h"
#include "ConstBundlePrims.h"

#include <omni/graph/core/iComputeGraph.h>
#include <omni/graph/core/CppWrappers.h>

#include <omni/math/linalg/vec.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/quat.h>
#include <omni/math/linalg/half.h>

namespace omni
{
namespace math
{
namespace linalg
{

template <typename T>
struct TypeToBaseType
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eUnknown;
};
template <>
struct TypeToBaseType<half>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eHalf;
};
template <>
struct TypeToBaseType<float>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eFloat;
};
template <>
struct TypeToBaseType<double>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eDouble;
};
template <>
struct TypeToBaseType<bool>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eBool;
};
template <>
struct TypeToBaseType<unsigned char>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eUChar;
};
template <>
struct TypeToBaseType<int>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eInt;
};
template <>
struct TypeToBaseType<int64_t>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eInt64;
};
template <>
struct TypeToBaseType<unsigned int>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eUInt;
};
template <>
struct TypeToBaseType<uint64_t>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eUInt64;
};
template <>
struct TypeToBaseType<omni::fabric::Token>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eToken;
};
template <>
struct TypeToBaseType<omni::fabric::Path>
{
    constexpr static omni::graph::core::BaseDataType baseType = omni::graph::core::BaseDataType::eRelationship;
};
template <typename T, size_t N>
struct TypeToBaseType<base_vec<T, N>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T>
struct TypeToBaseType<vec2<T>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T>
struct TypeToBaseType<vec3<T>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T>
struct TypeToBaseType<vec4<T>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T>
struct TypeToBaseType<quat<T>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T, size_t N>
struct TypeToBaseType<base_matrix<T, N>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T>
struct TypeToBaseType<matrix2<T>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T>
struct TypeToBaseType<matrix3<T>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};
template <typename T>
struct TypeToBaseType<matrix4<T>>
{
    constexpr static omni::graph::core::BaseDataType baseType = TypeToBaseType<T>::baseType;
};

template <typename T>
struct TypeToComponentCount
{
    constexpr static size_t count = 1;
};
template <typename T, size_t N>
struct TypeToComponentCount<base_vec<T,N>>
{
    constexpr static size_t count = N;
};
template <typename T>
struct TypeToComponentCount<vec2<T>>
{
    constexpr static size_t count = 2;
};
template <typename T>
struct TypeToComponentCount<vec3<T>>
{
    constexpr static size_t count = 3;
};
template <typename T>
struct TypeToComponentCount<vec4<T>>
{
    constexpr static size_t count = 4;
};
template <typename T>
struct TypeToComponentCount<quat<T>>
{
    constexpr static size_t count = 4;
};
template <typename T, size_t N>
struct TypeToComponentCount<base_matrix<T,N>>
{
    constexpr static size_t count = N*N;
};
template <typename T>
struct TypeToComponentCount<matrix2<T>>
{
    constexpr static size_t count = 4;
};
template <typename T>
struct TypeToComponentCount<matrix3<T>>
{
    constexpr static size_t count = 9;
};
template <typename T>
struct TypeToComponentCount<matrix4<T>>
{
    constexpr static size_t count = 16;
};

} // namespace linalg
} // namespace math
} // namespace omni

namespace omni
{
namespace graph
{
namespace core
{

namespace detail
{

//
// Non-owning string buffer with compile time size evaluation
//
class StringBuffer
{
public:
    using value_type = char const*;
    using size_type = std::size_t;

    using const_iterator = char const*;

    constexpr StringBuffer(value_type data, size_type size) noexcept : m_data{ data }, m_size{ size }
    {
    }

    constexpr explicit StringBuffer(value_type data) noexcept : StringBuffer{ data, len(data) }
    {
    }

    constexpr StringBuffer(StringBuffer const&) = default;
    constexpr StringBuffer(StringBuffer&&) = default;

    constexpr value_type data() const noexcept
    {
        return m_data;
    }

    constexpr size_type size() const noexcept
    {
        return m_size;
    }

    constexpr const_iterator begin() const noexcept
    {
        return m_data;
    }

    constexpr const_iterator end() const noexcept
    {
        return m_data + m_size;
    }

private:
    constexpr size_type len(value_type start) const noexcept
    {
        value_type end = start;
        for (; *end != '\0'; ++end)
            ;
        return end - start;
    }

    value_type m_data;
    size_type m_size;
};

// Helper class to keep name and type together.
struct AttrDefinition
{
    AttrDefinition(StringBuffer _name, omni::graph::core::Type _type, omni::graph::core::NameToken _token) noexcept
        : name{ _name }
        , type{ _type }
        , token{ _token }
    {
    }

    AttrDefinition(omni::fabric::IToken const* iToken, char const* _text, omni::graph::core::Type _type) noexcept
        : AttrDefinition{ StringBuffer{_text}, _type, iToken->getHandle(_text) }
    {
    }

    AttrDefinition(AttrDefinition const&) = delete;
    AttrDefinition(AttrDefinition&&) = delete;

    AttrDefinition& operator=(AttrDefinition const&) = delete;
    AttrDefinition& operator=(AttrDefinition&&) = delete;

    StringBuffer name;  // Name and size of the attribute
    omni::graph::core::Type type;          // Type of the attribute
    omni::graph::core::NameToken token;    // Token representation of the name
};

// Attribute Level Definitions:
inline AttrDefinition const& getAttrInterpolationDefinition() noexcept
{
    using namespace omni::fabric;
    static AttrDefinition d{ carb::getCachedInterface<IToken>(), "interpolation", Type{ BaseDataType::eToken, 1, 0 } };
    return d;
}

inline AttrDefinition const& getAttrSourceDefinition() noexcept
{
    using namespace omni::fabric;
    static AttrDefinition d{ carb::getCachedInterface<IToken>(), "source", Type{ BaseDataType::eUChar, 1, 0 } };
    return d;
}

// Primitive Level Definitions:
inline AttrDefinition const& getPrimIndexDefinition() noexcept
{
    using namespace omni::fabric;
    static AttrDefinition d{ carb::getCachedInterface<IToken>(), "primIndex", Type{ BaseDataType::eUInt64, 1, 0 } };
    return d;
}

inline AttrDefinition const& getPrimPathDefinition() noexcept
{
    using namespace omni::fabric;
    static AttrDefinition d{ carb::getCachedInterface<IToken>(), "sourcePrimPath", Type{ BaseDataType::eToken, 1, 0 } };
    return d;
}

inline AttrDefinition const& getPrimTypeDefinition() noexcept
{
    using namespace omni::fabric;
    static AttrDefinition d{ carb::getCachedInterface<IToken>(), "sourcePrimType", Type{ BaseDataType::eToken, 1, 0 } };
    return d;
}

// Bundle Level Definitions:
inline AttrDefinition const& getBundlePrimIndexOffsetDefinition() noexcept
{
    using namespace omni::fabric;
    static AttrDefinition d{ carb::getCachedInterface<IToken>(), "bundlePrimIndexOffset", Type{ BaseDataType::eUInt64, 1, 0 } };
    return d;
}

// Constant types.
constexpr omni::graph::core::Type s_relationshipType{ omni::graph::core::BaseDataType::eRelationship, 1, 0 };

} // namespace detail

inline bool BundleAttrib::isRelationshipData() const noexcept
{
    return m_source == Source::Relationship && type() == detail::s_relationshipType;
}

inline bool BundleAttrib::setInterpolation(omni::graph::core::NameToken interpolation) noexcept
{
    using namespace omni::graph::core;

    if (m_interpolation == interpolation)
        return true;

    if (interpolation == omni::fabric::kUninitializedToken)
    {
        clearInterpolation();
        return true;
    }

    if (IBundle2* bundle = getBundlePtr())
    {
        auto& interpDef = detail::getAttrInterpolationDefinition();
        AttributeDataHandle interpolationAttr = bundle->getAttributeMetadataByName(m_name, interpDef.token);
        if (!interpolationAttr.isValid())
        {
            interpolationAttr = bundle->createAttributeMetadata(m_name, interpDef.token, interpDef.type);
        }

        m_interpolation = interpolation;

        auto context = bundle->getContext();
        *getDataW<NameToken>(context, interpolationAttr) = interpolation;

        return true;
    }

    return false;
}

inline bool BundleAttrib::setSource(Source source) noexcept
{
    using namespace omni::graph::core;

    if(m_source == source)
        return true;

    if (IBundle2* bundle = getBundlePtr())
    {
        auto& sourceDef = detail::getAttrSourceDefinition();
        AttributeDataHandle sourceAttr = bundle->getAttributeMetadataByName(m_name, sourceDef.token);
        if(!sourceAttr.isValid())
        {
            sourceAttr = bundle->createAttributeMetadata(m_name, sourceDef.token, sourceDef.type);
        }

        m_source = source;

        auto context = bundle->getContext();
        *omni::graph::core::getDataW<SourceType>(context, sourceAttr) = static_cast<SourceType>(source);

        return true;
    }

    return false;
}

inline void BundleAttrib::copyContentsFrom(BundleAttrib const& sourceAttr) noexcept
{
    using namespace omni::graph::core;

    IBundle2* dstBundle = getBundlePtr();
    IConstBundle2* srcBundle = sourceAttr.getConstBundlePtr();

    if (!dstBundle)
    {
        return;
    }

    auto context = dstBundle->getContext();

    // Copy Attribute
    AttributeDataHandle dstAttrHandle = dstBundle->getAttributeByName(m_name);
    ConstAttributeDataHandle srcAttrHandle = srcBundle->getConstAttributeByName(sourceAttr.m_name);

    // Ensure that copyData updated the type correctly, if needed.
    CARB_ASSERT(context.iAttributeData->getType(context, dstAttrHandle) == Type(m_type));
    context.iAttributeData->copyData(dstAttrHandle, context, srcAttrHandle);

    // Copy the cached type
    m_type = sourceAttr.m_type;

    // Copy the interpolation (does nothing if the same; clears interpolation if none on sourceAttr)
    setInterpolation(sourceAttr.interpolation());

    // Copy source
    setSource(sourceAttr.m_source);
}

inline void BundleAttrib::clearInterpolation() noexcept
{
    using namespace omni::graph::core;

    if (IBundle2* bundle = getBundlePtr())
    {
        auto& interpDef = detail::getAttrInterpolationDefinition();
        bundle->removeAttributeMetadata(m_name, interpDef.token);
        m_interpolation = omni::fabric::kUninitializedToken;
    }
}

inline ConstBundlePrim* BundleAttrib::getBundlePrim() const noexcept
{
    return m_bundlePrim;
}

inline void BundleAttrib::clearSource() noexcept
{
    using namespace omni::graph::core;

    if (IBundle2* bundle = getBundlePtr())
    {
        auto& sourceDef = detail::getAttrSourceDefinition();
        bundle->removeAttributeMetadata(m_name, sourceDef.token);
        m_source = BundleAttribSource::Attribute;
    }
}

inline omni::graph::core::NameToken BundleAttrib::name() const noexcept
{
    return m_name;
}

inline omni::graph::core::NameToken BundleAttrib::interpolation() const noexcept
{
    return m_interpolation;
}

inline omni::graph::core::Type BundleAttrib::type() const noexcept
{
    return omni::graph::core::Type(m_type);
}

inline bool BundleAttrib::isArray() const noexcept
{
    omni::graph::core::Type type{ m_type };
    CARB_ASSERT(type.arrayDepth < 2);
    return (type.arrayDepth != 0);
}

inline BundleAttrib::Source BundleAttrib::source() const noexcept
{
    return m_source;
}

inline bool BundleAttrib::isAttributeData() const noexcept
{
    return m_source == Source::Attribute;
}

inline omni::graph::core::NameToken BundleAttrib::prefixedName() const noexcept
{
    return m_name;
}

inline size_t BundleAttrib::size() const noexcept
{
    using namespace omni::graph::core;

    if (!isArray())
    {
        return 1;
    }

    IConstBundle2* bundle = getConstBundlePtr();
    auto context = bundle->getContext();

    ConstAttributeDataHandle attr = bundle->getConstAttributeByName(m_name);
    size_t count;
    context.iAttributeData->getElementCount(&count, context, &attr, 1);
    return count;
}

inline void BundleAttrib::resize(size_t arrayElementCount) noexcept
{
    using namespace omni::graph::core;

    CARB_ASSERT(isArray());
    if (IBundle2* bundle = getBundlePtr())
    {
        auto context = bundle->getContext();
        AttributeDataHandle attr = bundle->getAttributeByName(m_name);
        context.iAttributeData->setElementCount(context, attr, arrayElementCount);
    }
}

inline void* BundleAttrib::getDataInternal() noexcept
{
    using namespace omni::graph::core;

    if (IBundle2* bundle = getBundlePtr())
    {
        auto context = bundle->getContext();

        AttributeDataHandle attr = bundle->getAttributeByName(m_name);
        if (Type(m_type).arrayDepth == 0)
        {
            return getDataW<void>(context, attr);
        }
        return *getDataW<void*>(context, attr);

    }

    return nullptr;
}

inline void const* BundleAttrib::getDataInternal() const noexcept
{
    using namespace omni::graph::core;

    IConstBundle2* constBundle = getConstBundlePtr();
    GraphContextObj context = constBundle->getContext();

    ConstAttributeDataHandle attr = constBundle->getConstAttributeByName(m_name);
    if (Type(m_type).arrayDepth == 0)
    {
        return getDataR<void const>(context, attr);
    }
    return *getDataR<void const*>(context, attr);
}

inline omni::graph::core::AttributeDataHandle BundleAttrib::handle() noexcept
{
    using namespace omni::graph::core;

    if (IBundle2* bundle = getBundlePtr())
    {
        return AttributeDataHandle(AttrKey((HandleInt)bundle->getHandle(), m_name.token));
    }
    return AttributeDataHandle{ AttributeDataHandle::invalidValue() };
}

inline omni::graph::core::ConstAttributeDataHandle BundleAttrib::handle() const noexcept
{
    using namespace omni::graph::core;

    if(IConstBundle2* bundle = getConstBundlePtr())
    {
        return ConstAttributeDataHandle{ AttrKey((HandleInt)bundle->getConstHandle(), m_name.token) };
    }
    return ConstAttributeDataHandle{ ConstAttributeDataHandle::invalidValue() };
}

template <typename T>
T* BundleAttrib::getData() noexcept
{
    // It must be valid to request a pointer to type T.
    // requesting a float* or vec3f* for a vec3f type is valid, but double* or vec2f* is not.
    using namespace omni::math::linalg;
    using Type = omni::graph::core::Type;

    if (type() == detail::s_relationshipType)
    {
        if (IBundle2* bundle = getBundlePtr())
        {
            AttributeDataHandle attr = bundle->getAttributeByName(m_name);
            T** paths = getDataW<T*>(bundle->getContext(), attr);
            return paths ? *paths : nullptr;
        }
        return nullptr;
    }

    bool isSameBaseType = TypeToBaseType<T>::baseType == Type(m_type).baseType;
    bool const isSameCount = TypeToComponentCount<T>::count == Type(m_type).componentCount;
    bool const isValidCast = isSameBaseType && (TypeToComponentCount<T>::count == 1 || isSameCount);

    return isValidCast ? reinterpret_cast<T*>(getDataInternal()) : nullptr;
}

template <typename T>
T const* BundleAttrib::getData() const noexcept
{
    // It must be valid to request a pointer to type T.
    // requesting a float* or vec3f* for a vec3f type is valid, but double* or vec2f* is not.
    using namespace omni::math::linalg;
    using Type = omni::graph::core::Type;

    if (type() == detail::s_relationshipType)
    {
        if (IConstBundle2* constBundle = getConstBundlePtr())
        {
            ConstAttributeDataHandle attr = constBundle->getConstAttributeByName(m_name);
            T const* const* paths = getDataR<T const*>(constBundle->getContext(), attr);
            return paths ? *paths : nullptr;
        }
        return nullptr;
    }

    bool const isValidCast =
        TypeToBaseType<T>::baseType == Type(m_type).baseType &&
                             (TypeToComponentCount<T>::count == 1 ||
                              TypeToComponentCount<T>::count == Type(m_type).componentCount);

    return isValidCast ? reinterpret_cast<T const*>(getDataInternal()) : nullptr;
}

template <typename T>
T const* BundleAttrib::getConstData() const noexcept
{
    return getData<T>();
}

template <typename T>
T BundleAttrib::get() const noexcept
{
    using namespace omni::math::linalg;
    // TODO: Figure out how to support array attributes here.
    CARB_ASSERT(omni::graph::core::Type(m_type).arrayDepth == 0);
    // This has stronger requirements than getData, since get<float>() isn't valid
    // for a vec3f attribute, but getData<float>() is valid for a vec3f attribute.
    CARB_ASSERT(TypeToComponentCount<T>::count == omni::graph::core::Type(m_type).componentCount);
    return *getConstData<T>();
}

template <typename T>
void BundleAttrib::set(T const& value) noexcept
{
    using namespace omni::math::linalg;
    CARB_ASSERT(omni::graph::core::Type(m_type).arrayDepth == 0);
    // This has stronger requirements than getData, since set(1.0f) isn't valid
    // for a vec3f attribute, but getData<float>() is valid for a vec3f attribute.
    CARB_ASSERT(TypeToComponentCount<T>::count == omni::graph::core::Type(m_type).componentCount);
    *getData<T>() = value;
}

template <typename T>
void BundleAttrib::set(T const* values, size_t elementCount) noexcept
{
    using namespace omni::math::linalg;
    CARB_ASSERT(omni::graph::core::Type(m_type).arrayDepth == 1);
    // This has stronger requirements than getData, since set(float const*,size_t) isn't valid
    // for a vec3f attribute, but getData<float>() is valid for a vec3f attribute.
    CARB_ASSERT(TypeToComponentCount<T>::count == omni::graph::core::Type(m_type).componentCount);
    resize(elementCount);
    if (elementCount > 0)
    {
        T* p = getData<T>();
        for (size_t i = 0; i < elementCount; ++i)
        {
            p[i] = values[i];
        }
    }
}

inline void BundleAttrib::clearContents() noexcept
{
    using namespace omni::graph::core;

    /**
     * Remove attribute. Its metadata will be removed automatically together with it.
     */
    IBundle2* bundle = getBundlePtr();
    bundle->removeAttributeByName(m_name);

    /**
     * Invalidate data.
     */
    m_source = BundleAttribSource::Attribute;
    m_interpolation = omni::fabric::kUninitializedToken;

    m_type = omni::fabric::kUnknownType;
    m_name = omni::fabric::kUninitializedToken;

    m_bundlePrim = nullptr;
}

} // namespace core
} // namespace graph
} // namespace omni
