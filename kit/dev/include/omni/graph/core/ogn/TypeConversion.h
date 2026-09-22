// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/ogn/TypeTraits.h>

namespace omni
{
namespace graph
{
namespace core
{
namespace ogn
{

// Utility struct to implement conversion between 2 BaseDataType
// Note: simple runtime dispatch on the source type (dst type must be known at compile time)
static constexpr BaseDataType kLastBaseType = BaseDataType::eToken;

template <typename DST_TYPE, BaseDataType BASE_SRC_TYPE = kLastBaseType>
struct BaseTypeConversion
{
    using next = BaseTypeConversion<DST_TYPE, (BaseDataType)((uint8_t)BASE_SRC_TYPE - 1)>;
    static int canConvertFrom(BaseDataType srcType)
    {
        if (srcType == BASE_SRC_TYPE)
            return false;
        return next::canConvertFrom(srcType);
    }
    static bool convert(DST_TYPE* dst, void const* src, BaseDataType srcType, size_t count)
    {
        if (srcType == BASE_SRC_TYPE)
            return false;
        return next::convert(dst, src, srcType, count);
    }
};

template <typename T>
struct BaseTypeConversion<T, BaseDataType::eUnknown>
{
    static constexpr int canConvertFrom(BaseDataType) { return 0; }
    static bool convert(T*, void const*, BaseDataType, size_t) { return false; }
};

template<typename T, BaseDataType eDataType>
struct BaseTypeConversionBase
{
    using next = BaseTypeConversion<T, (BaseDataType)((uint8_t)eDataType - 1)>;

    static bool canConvertFromBase(BaseDataType srcType)
    {
        if (eDataType == srcType)
            return true;
        return false;
    }

    template<typename FUNC>
    static bool convertBase(T* dst, void const* srcBuffer, BaseDataType srcType, size_t count, FUNC const& func)
    {
        if (eDataType == srcType)
        {
            using srcType = typename attribute_t<eDataType>::type;
            srcType const* srcPtr = (srcType const*)srcBuffer;
            while (count--)
                func(*dst++, *srcPtr++);
            return true;
        }
        return next::convert(dst, srcBuffer, srcType, count);
    }
};

#define IMPLEMENT_BASE_TYPE_CONVERSION(dstType, srcBaseType, func)\
    template <>  struct BaseTypeConversion<dstType, srcBaseType> : public BaseTypeConversionBase<dstType, srcBaseType> {\
    static int canConvertFrom(BaseDataType srcType) {if(canConvertFromBase(srcType)) return __LINE__; return next::canConvertFrom(srcType);}\
    static bool convert(dstType* dst, void const* srcBuffer, BaseDataType srcType, size_t count) {return convertBase(dst, srcBuffer, srcType, count, func);}}

#define IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(SRC, DST) \
    IMPLEMENT_BASE_TYPE_CONVERSION(DST, attribute_base_t<SRC>::value, [](DST& dst, SRC const& src) { dst = (DST)src; })

//! <summary>
//! Implements all conversions
//! Note: order is important for BOTH source type and destination type
//!     source type oder : template instantiation needs to happen in order of the enum since higher type ID template
//!                         will call lower ones (so they need to be already defined)
//!                         => ORDER IN THE BASE TYPE ENUM ORDER
//!     dst type order   : conversion precedence will follow order of declaration
//!                        ie. : when several conversions are possible, the one declared before the others will be used
//!                         => ORDER BY "QUALITY" OF THE CONVERSION
//! </summary>


IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int, unsigned int); // signed -> unsigned is allowed by fabric
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int, int64_t);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int, float);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int, double);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int, bool);

IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(unsigned int, uint64_t);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(unsigned int, int);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(unsigned int, int64_t);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(unsigned int, float);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(unsigned int, double);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(unsigned int, bool);


IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int64_t, uint64_t); // signed -> unsigned is allowed by fabric
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int64_t, int);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int64_t, double);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int64_t, float);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(int64_t, bool);

IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(uint64_t, int64_t);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(uint64_t, unsigned int);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(uint64_t, int);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(uint64_t, double);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(uint64_t, float);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(uint64_t, bool);

IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(float, double);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(float, int);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(float, int64_t);

IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(double, float);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(double, int64_t);
IMPLEMENT_BASE_TYPE_CONVERSION_AS_CAST(double, int);

//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//
//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//

// This implements the Double dispatch solve, when none of the type are known at compile time
template <BaseDataType BASE_DST_TYPE = kLastBaseType>
struct BaseDoubleDispatchTypeConversionTest
{
    using TYPE = typename attribute_t<BASE_DST_TYPE>::type;

    static int canConvert(BaseDataType from, BaseDataType to)
    {
        if (BASE_DST_TYPE == to)
            return BaseTypeConversion<TYPE>::canConvertFrom(from);
        return BaseDoubleDispatchTypeConversionTest<(BaseDataType)((uint8_t)BASE_DST_TYPE - 1)>::canConvert(from, to);
    }

    static bool convert(void* dstBuffer, BaseDataType dstType, void const* srcBuffer, BaseDataType srcType, size_t count)
    {
        if (BASE_DST_TYPE == dstType)
            return BaseTypeConversion<TYPE>::convert((TYPE*) dstBuffer, srcBuffer, srcType, count);
        return BaseDoubleDispatchTypeConversionTest<(BaseDataType)((uint8_t)BASE_DST_TYPE - 1)>::convert(dstBuffer, dstType, srcBuffer, srcType, count);
    }
};
template <>
struct BaseDoubleDispatchTypeConversionTest<BaseDataType::eUnknown>
{
    static int canConvert(BaseDataType from, BaseDataType to)
    {
        return 0;
    }
    static bool convert(void* dst, BaseDataType dstType, void const* srcBuffer, BaseDataType srcType, size_t count)
    {
        return false;
    }
};
//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//
//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//!//

//Convert at compile time a type to its corresponding BaseDataType
template<typename T>
constexpr BaseDataType getDataType()
{
    using U = std::decay_t<T>;
    using V = std::remove_pointer_t<U>;
    return attribute_base_t<V>::value;
}

//Returns a positive value if a conversion exists between the 2 provided types, 0 else
// The lower the returned value is, the prefered is the conversion
static inline int isRawDataConvertible(BaseDataType from, BaseDataType to)
{
    return BaseDoubleDispatchTypeConversionTest<>::canConvert(from, to);
}

// Indicate whether, for a given type pair reputed to be convertible, the actual conversion can be bypassed
static inline bool isRawBinaryDataCompatible(BaseDataType t0, BaseDataType t1)
{
    if (t0 == t1)
        return true;

    if (t0 > t1)
        std::swap(t0, t1);

    switch (t0)//always smaller
    {
    case omni::graph::core::BaseDataType::eUnknown:
        break;
    case omni::graph::core::BaseDataType::eBool:
        break;
    case omni::graph::core::BaseDataType::eUChar:
        break;
    case omni::graph::core::BaseDataType::eInt:
        break;
    case omni::graph::core::BaseDataType::eUInt:
        break;
    case omni::graph::core::BaseDataType::eInt64:
        break;
    case omni::graph::core::BaseDataType::eUInt64:
        return t1 == omni::graph::core::BaseDataType::eToken;
        break;
    case omni::graph::core::BaseDataType::eHalf:
        break;
    case omni::graph::core::BaseDataType::eFloat:
        break;
    case omni::graph::core::BaseDataType::eDouble:
        break;
    case omni::graph::core::BaseDataType::eToken:
        break;
    case omni::graph::core::BaseDataType::eRelationship:
        break;
    case omni::graph::core::BaseDataType::eAsset:
        break;
    case omni::graph::core::BaseDataType::eDeprecated1:
        break;
    case omni::graph::core::BaseDataType::eConnection:
        break;
    case omni::graph::core::BaseDataType::eTag:
        break;
    default:
        break;
    }
    return false;
}

//Perform the actual conversion between 2 instantiated values
template <typename Dst>
static inline bool doConversion(Dst* dst, void const* src, BaseDataType srcType, size_t count)
{
    static_assert(getDataType<Dst>() != BaseDataType::eUnknown, "");
    CARB_ASSERT(srcType != BaseDataType::eUnknown);
    using UnderlyingType = typename attribute_t<getDataType<Dst>()>::type;//ex: Vec3 -> float
    return BaseTypeConversion<UnderlyingType>::convert((UnderlyingType*)dst, src, srcType, count);
}

static inline bool doConversion(void* dst, BaseDataType dstType, void const* src, BaseDataType srcType, size_t count)
{
    CARB_ASSERT(dstType != BaseDataType::eUnknown);
    CARB_ASSERT(srcType != BaseDataType::eUnknown);
    return BaseDoubleDispatchTypeConversionTest<>::convert(dst, dstType, src, srcType, count);
}

// Helper to determine if the given roles are compatible for matching base type
static inline bool areMatchedBaseTypesRoleCompatible(BaseDataType baseType, AttributeRole srcRole, AttributeRole destRole)
{
    if (baseType == omni::fabric::BaseDataType::eUChar)
    {
        // Path and strings are compatible
        bool isSrcString = (srcRole == AttributeRole::ePath || srcRole == AttributeRole::eText);
        bool isDstString = (destRole == AttributeRole::ePath || destRole == AttributeRole::eText);
        return isSrcString == isDstString;
    }

    if (baseType == BaseDataType::eRelationship)
    {
        // no role is compatible with all relationship types
        if (srcRole == AttributeRole::eNone || destRole == AttributeRole::eNone)
        {
            return true;
        }

        // Connecting bundle to target type is soft deprecated.
        if (srcRole == AttributeRole::eBundle)
        {
            return (destRole == AttributeRole::eBundle) || (destRole == AttributeRole::eTarget);
        }

        if (srcRole == AttributeRole::eTarget)
        {
            return (destRole == AttributeRole::eTarget);
        }
    }

    return true;
};

static inline bool hasRestrictedRole(const Type& type)
{
    return type.role == AttributeRole::eObjectId ||
           type.role == AttributeRole::eExecution;
}

// Helper to return true if the given types are compatible
static inline int areTypesCompatible(const Type& srcType, const Type& destType)
{
    if (srcType == destType)
        return 1;

    // They aren't exactly the same, but check for signed/unsigned compatibility, which FC can support
    if (srcType.arrayDepth != destType.arrayDepth)
        return 0;

    if (srcType.componentCount != destType.componentCount)
        return 0;

    // Check for custom roles where the entire type must match exact. These typically use common base types (e.g. int), and this
    // avoid unintended conversion between compatible base types without a role (e.g. int -> ObjectId)
    if (hasRestrictedRole(srcType) || hasRestrictedRole(destType))
        return srcType == destType;

    // If base types match, we are compatible with a possible exception for the role
    if (srcType.baseType == destType.baseType)
        return areMatchedBaseTypesRoleCompatible(srcType.baseType, srcType.role, destType.role) ? 1 : 0;

    // Arrays are not convertible
    // but arrays of int(64) signed <-> unsigned are through fabric
    if (srcType.arrayDepth)
    {
        return ((srcType.baseType == BaseDataType::eInt || srcType.baseType == BaseDataType::eUInt) &&
                (destType.baseType == BaseDataType::eInt || destType.baseType == BaseDataType::eUInt)) ||
               ((srcType.baseType == BaseDataType::eInt64 || srcType.baseType == BaseDataType::eUInt64) &&
                (destType.baseType == BaseDataType::eInt64 || destType.baseType == BaseDataType::eUInt64)) ? 1 : 0;
    }
    return isRawDataConvertible(srcType.baseType, destType.baseType);
};

// Helper to return if there is any compatibility between two type groups
static inline int areAnyTypesCompatible(const std::vector<Type>& srcTypes, const std::vector<Type>& destTypes)
{
    for (const auto& src: srcTypes)
    {
        for (const auto& dst: destTypes)
        {
            if (areTypesCompatible(src, dst))
                return true;
        }
    }
    return false;
}

// Method that adjusts the role from a type based on its component count and/or array depth
static inline Type makeValidRole(const Type& type)
{
    Type adjustedType = type;
    switch (type.role)
    {
    case AttributeRole::eVector:
    case AttributeRole::eNormal:    // fallthrough intentional
    case AttributeRole::ePosition:  // fallthrough intentional
        adjustedType.role = (type.componentCount == 3) ? type.role : AttributeRole::eNone;
        break;
    case AttributeRole::eColor:
        adjustedType.role = (type.componentCount == 3 || type.componentCount == 4) ? type.role : AttributeRole::eNone;
        break;
    case AttributeRole::eTexCoord:
        adjustedType.role = (type.componentCount == 2 || type.componentCount == 3) ? type.role : AttributeRole::eNone;
        break;
    case AttributeRole::eQuaternion:
        adjustedType.role = (type.componentCount == 4) ? type.role : AttributeRole::eNone;
        break;
    case AttributeRole::eFrame:
        adjustedType.role = (type.componentCount == 16) ? type.role : AttributeRole::eNone;
        break;
    case AttributeRole::eTimeCode:
    case AttributeRole::eObjectId: // fallthrough intentional
        adjustedType.role = (type.componentCount == 1) ? type.role : AttributeRole::eNone;
        break;
    case AttributeRole::eText:
    case AttributeRole::ePath:   // fallthrough intentional
        adjustedType.role = (type.arrayDepth >= 1) ? type.role : AttributeRole::eNone;
        break;
    case AttributeRole::eMatrix:
        adjustedType.role = (type.componentCount == 4 || type.componentCount == 9 || type.componentCount == 16) ? type.role : AttributeRole::eNone;
        break;
    default:
        break;
    }
    return adjustedType;
}


//Small struct helper that:
// - hold the converted value so a reference can be returned
// - specialize to an empty pass-through if no conversion exists
template <typename DataType, BaseDataType eType = getDataType<DataType>()>
struct Converter
{
private:
    using DataStore = typename std::remove_const<DataType>::type;
    mutable DataStore convertedValue{};

public:
    Converter(){}
    DataType const* convertValue(DataType const* originalData, Type const& originalDataType) const
    {
        constexpr BaseDataType dstDataType = getDataType<DataType>();
        if (!isRawBinaryDataCompatible(originalDataType.baseType, dstDataType))
        {
            if constexpr (std::is_array<DataStore>::value)
            {
                doConversion(
                    &convertedValue[0], dstDataType, &(*originalData)[0], originalDataType.baseType,
                    std::min(size_t(originalDataType.componentCount), std::extent_v<DataStore>));
            }
            else
            {
                doConversion(
                    &convertedValue, dstDataType, originalData, originalDataType.baseType,
                    originalDataType.componentCount);
            }
            return &convertedValue;
        }
        return originalData;
    }

    bool willConvert(Type const& originalDataType) const
    {
        return !isRawBinaryDataCompatible(originalDataType.baseType, getDataType<DataType>());
    }
};
template <typename DataType>
struct Converter<DataType, BaseDataType::eUnknown>
{
    inline DataType const* convertValue(DataType const* originalData, Type const&) const
    {
        return originalData;
    }
    bool willConvert(Type const& originalDataType) const
    {
        return false;
    }
};


} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
