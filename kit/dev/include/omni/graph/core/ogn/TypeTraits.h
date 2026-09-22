// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/Types.h>
#include <omni/graph/core/TemplateUtils.h>

namespace omni {
namespace graph {
namespace core {
namespace ogn {

// Helper that provides a templated conversion from C++ simple data type to the base data type enum in core::Type
template <typename CppType>
struct attribute_base_t { static constexpr BaseDataType value = BaseDataType::eUnknown; };
template <> struct attribute_base_t<bool> { static constexpr BaseDataType value = BaseDataType::eBool; };
template <> struct attribute_base_t<double> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<float> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<int> { static constexpr BaseDataType value = BaseDataType::eInt; };
template <> struct attribute_base_t<int64_t> { static constexpr BaseDataType value = BaseDataType::eInt64; };
template <> struct attribute_base_t<Token> { static constexpr BaseDataType value = BaseDataType::eToken; };
template <> struct attribute_base_t<NameToken> { static constexpr BaseDataType value = BaseDataType::eToken; };
template <> struct attribute_base_t<Path> { static constexpr BaseDataType value = BaseDataType::eRelationship; };
template <> struct attribute_base_t<TargetPath> { static constexpr BaseDataType value = BaseDataType::eRelationship; };
template <> struct attribute_base_t<uint32_t> { static constexpr BaseDataType value = BaseDataType::eUInt; };
template <> struct attribute_base_t<uint64_t> { static constexpr BaseDataType value = BaseDataType::eUInt64; };
template <> struct attribute_base_t<uint8_t> { static constexpr BaseDataType value = BaseDataType::eUChar; };
template <> struct attribute_base_t<char> { static constexpr BaseDataType value = BaseDataType::eUChar; };//char is used for string, but implemented as uchar

//carb base types
template <> struct attribute_base_t<carb::Float2> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<carb::Float3> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<carb::Float4> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<carb::Double2> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<carb::Double3> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<carb::Double4> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<carb::Int2> { static constexpr BaseDataType value = BaseDataType::eInt; };
template <> struct attribute_base_t<carb::Int3> { static constexpr BaseDataType value = BaseDataType::eInt; };
template <> struct attribute_base_t<carb::Int4> { static constexpr BaseDataType value = BaseDataType::eInt; };
template <> struct attribute_base_t<carb::Uint2> { static constexpr BaseDataType value = BaseDataType::eUInt; };
template <> struct attribute_base_t<carb::Uint3> { static constexpr BaseDataType value = BaseDataType::eUInt; };
template <> struct attribute_base_t<carb::Uint4> { static constexpr BaseDataType value = BaseDataType::eUInt; };




// Helper struct to convert at compile time from BaseDataType to corresponding cpp type
template <BaseDataType eBaseType>
struct attribute_t { using type = void; };
template <> struct attribute_t<BaseDataType::eBool> { using type = bool; };
template <> struct attribute_t<BaseDataType::eDouble> { using type = double; };
template <> struct attribute_t<BaseDataType::eFloat> { using type = float; };
template <> struct attribute_t<BaseDataType::eInt> { using type = int; };
template <> struct attribute_t<BaseDataType::eInt64> { using type = int64_t; };
template <> struct attribute_t<BaseDataType::eToken> { using type = Token; };
template <> struct attribute_t<BaseDataType::eUInt> { using type = uint32_t; };
template <> struct attribute_t<BaseDataType::eUInt64> { using type = uint64_t; };
template <> struct attribute_t<BaseDataType::eUChar> { using type = uint8_t; };



// Templated conversions defining attribute traits given the actual C++ data types they implement.
// The role does not enter in to this conversion as it is an interpretation of a data type, not a separate data type.
//
// Constants:
//    isArray    Boolean indicating if the data type includes an array of variable length
//    tupleCount Number of tuple values in the data type (1 for a simple value)
//    baseType   BaseDataType enum matching the data's unencumbered type
// Types:
//    actual_t     Actual data type to be handled (managing types that resolve to the same POD)
//    element_t    Data type for the unencumbered value (e.g float for a float[][3])
//    data_t       Data type for a single value (e.g. float for float/float[] but float[3] for float[3]/float[][3])
//
// The comments above the definitions give examples of how the values are set for representative template types
//
// Note: The pxr GfVec/GfMatrix types are not included here for simplicity, though they can be defined in a separate
//       file for those that wish to use them by specializing the attribute_type_traits struct.
template <typename CppType>
struct attribute_type_traits
{
    // float/float[3] -> false, float[]/float[][3] -> true
    static constexpr bool isArray = !is_bounded_array<CppType>::value && std::is_array<CppType>::value;
    static constexpr uint8_t arrayDepth = isArray ? 1 : 0;

    // Flags that break apart the data type into the four main mutually-exclusive categories used as accessors
    static constexpr bool isSimpleType = !is_bounded_array<CppType>::value && !std::is_array<CppType>::value;
    static constexpr bool isTupleType = is_bounded_array<CppType>::value;
    static constexpr bool isArrayType = std::is_array<CppType>::value && !is_bounded_array<CppType>::value && !is_bounded_array<std::remove_extent_t<CppType>>::value;
    static constexpr bool isTupleArrayType = std::is_array<CppType>::value && !is_bounded_array<CppType>::value && is_bounded_array<std::remove_extent_t<CppType>>::value;

    // Get the actual data type this class references. This is needed due to the fact that our token implementation,
    // NameToken, is typedefed to uint64_t, making it indistinguishable from a regular uint64_t to the compiler. By
    // passing ogn::Token/ogn::Token[] instead, the ambiguity can be resolved and the actual type deduced. (This
    // wouldn't quite work as-is if it supported tuples, but as it doesn't the extra complexity can be omitted.)
    using actual_t = std::conditional_t<std::is_same<std::remove_all_extents_t<CppType>, ogn::Token>::value,
        std::conditional_t<isArray, NameToken[], NameToken>,
        CppType
        >;

    // float/float[3]/float[]/float[][3] -> float
    using element_t = std::remove_const_t<std::remove_all_extents_t<actual_t>>;

    // float/float[]/float[3]/float[][3] -> BaseDataType::eFloat
    static constexpr BaseDataType baseType = attribute_base_t<element_t>::value;

    // float/float[] -> float, float[3]/float[][3] -> float[3]
    using data_t = std::conditional_t<isArray, std::remove_extent_t<actual_t>, actual_t>;

    // float/float[] -> 1, float[3]/float[][3] -> 3
    static constexpr int tupleCount = std::is_array<data_t>::value ? std::extent<data_t, 0>::value : 1;
};


} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
