// Copyright (c) 2023-2024, NVIDIA CORPORATION. All rights reserved.
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

template <typename T>
constexpr BaseDataType Type::getBaseDataType()
{
    return BaseDataType::eUnknown;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<bool>()
{
    return BaseDataType::eBool;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<int8_t>()
{
    return BaseDataType::eUChar; // signed and unsigned have same BaseDataType, is this okay?
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<uint8_t>()
{
    return BaseDataType::eUChar;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<int16_t>()
{
    return BaseDataType::eHalf; // signed and unsigned have same BaseDataType, is this okay?
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<uint16_t>()
{
    return BaseDataType::eHalf;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<int32_t>()
{
    return BaseDataType::eInt;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<uint32_t>()
{
    return BaseDataType::eUInt;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<int64_t>()
{
    return BaseDataType::eInt64;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<uint64_t>()
{
    return BaseDataType::eUInt64;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<float>()
{
    return BaseDataType::eFloat;
}

template <>
inline constexpr BaseDataType Type::getBaseDataType<double>()
{
    return BaseDataType::eDouble;
}

template <typename T>
constexpr Type Type::getType()
{
    // fabric doesn't address pointers as data _at all_ so pointers are always arrays
    constexpr uint8_t arrayDepth = std::is_pointer<T>::value ? 1 : 0;

    using NoConstDataT = typename std::remove_cv<typename std::remove_pointer<T>::type>::type;
    // future: if we could extract a trait for the component count we could do something besides 1
    return Type(getBaseDataType<NoConstDataT>(), 1, arrayDepth);
}

template <typename T>
bool Type::isCompatibleWithInternal() const
{
#ifndef DEPRECATED_DISABLE_FABRIC_TRIVIALLY_COPYABLE_TYPES_ONLY
    static_assert(std::is_trivially_copyable<T>::value, "Fabric only supports trivially copyable types");
#endif // DEPRECATED_DISABLE_FABRIC_TRIVIALLY_COPYABLE_TYPES_ONLY

    const Type typeT = getType<T>();
    const bool isTemplateKnown = typeT.baseType != BaseDataType::eUnknown;
    const bool isThisTypeKnown = this->baseType != BaseDataType::eUnknown;
    const size_t templateDataSize = sizeof(typename std::remove_pointer<T>::type);
    const size_t thisTypeDataSize = size();

    // part 1: perform a type check if we have known types (if we were able to deduce a Type from T)
    if (isTemplateKnown && isThisTypeKnown)
    {
        if (baseType != typeT.baseType)
        {
            return false;
        }

        if (arrayDepth != typeT.arrayDepth)
        {
            return false;
        }

        // Type::size() is the size of the data in the array, not a pointer, so check that
        if (typeT.arrayDepth && thisTypeDataSize != templateDataSize)
        {
            return false;
        }
    }

    // part 2: perform a size check if we have a valid size (zero size is degenerate)
    //  caveat: we will do checks on null pointers, no data, which is size == 0
    if (thisTypeDataSize && thisTypeDataSize != templateDataSize)
    {
        return false;
    }

    return true;
}

template <typename T>
bool Type::isCompatibleWith() const
{
    using NoConstT = typename std::remove_cv<T>::type;
    const bool isTemplatePointer = std::is_pointer<NoConstT>::value;
    const bool isThisTypeArray = isArray();

    // if it's already a pointer, it's AoA access via pointer-to-pointer
    //  so we only add another pointer onto T if we know type this is an array and T is not
    //  if we remove the ability to return AoA from getAttribute(), this wrapper can go away
    //  because that's the only scenario when we allow pointer-to-pointer (above this level)
    //  pointer-to-pointer happens at a higher level because getAttribute returns T*, always
    //  example:
    //    const char* const* charPtrPtr = reinterpret_cast<const char* const*>(
    //      stageReaderWriter.getAttributeRd<const char*>(Path("/prim"), Token("attr")));
    if (isThisTypeArray && !isTemplatePointer)
    {
        return isCompatibleWithInternal<T*>();
    }
    else
    {
        return isCompatibleWithInternal<T>();
    }
}

} // namespace fabric
} // namespace omni
