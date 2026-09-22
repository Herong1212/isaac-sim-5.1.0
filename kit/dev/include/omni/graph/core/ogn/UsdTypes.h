// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// This file contains helper utilities for managing casting and interpretation of the USD
// data types. Keeping this separate enables the ability for any other libraries to
// provide their own type casting, so that the OGN code can use native types only.

// clang-format off
#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/base/gf/half.h>
#include <pxr/base/gf/matrix2d.h>
#include <pxr/base/gf/matrix3d.h>
#include <pxr/base/gf/matrix4d.h>
#include <pxr/base/gf/vec2d.h>
#include <pxr/base/gf/vec2f.h>
#include <pxr/base/gf/vec2h.h>
#include <pxr/base/gf/vec2i.h>
#include <pxr/base/gf/vec3d.h>
#include <pxr/base/gf/vec3f.h>
#include <pxr/base/gf/vec3h.h>
#include <pxr/base/gf/vec3i.h>
#include <pxr/base/gf/vec4d.h>
#include <pxr/base/gf/vec4f.h>
#include <pxr/base/gf/vec4h.h>
#include <pxr/base/gf/vec4i.h>
#include <pxr/base/gf/quatd.h>
#include <pxr/base/gf/quatf.h>
#include <pxr/base/gf/quath.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/sdf/timeCode.h>
#include <pxr/base/tf/token.h>
#include <omni/graph/core/PostUsdInclude.h>
#include <omni/fabric/IPath.h>
#include <omni/fabric/IToken.h>
#include <omni/graph/core/Type.h>
#include <omni/graph/core/ogn/TypeTraits.h>
// clang-format on

namespace omni
{
namespace graph
{
namespace core
{
namespace ogn
{
// GfHalf, TfToken, SdfPath, and SdfTimeCode are the base types that allow special casting
template <> struct attribute_base_t<pxr::GfHalf> { static constexpr BaseDataType value = BaseDataType::eHalf; };
template <> struct attribute_base_t<pxr::TfToken> { static constexpr BaseDataType value = BaseDataType::eToken; };
template <> struct attribute_base_t<pxr::SdfPath> { static constexpr BaseDataType value = BaseDataType::eRelationship; };
template <> struct attribute_base_t<pxr::SdfTimeCode> { static constexpr BaseDataType value = BaseDataType::eDouble; };
// All of the matrix and vector types have USD implementations
template <> struct attribute_base_t<pxr::GfMatrix2d> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<pxr::GfMatrix3d> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<pxr::GfMatrix4d> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<pxr::GfVec2d> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<pxr::GfVec2f> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<pxr::GfVec2h> { static constexpr BaseDataType value = BaseDataType::eHalf; };
template <> struct attribute_base_t<pxr::GfVec2i> { static constexpr BaseDataType value = BaseDataType::eInt; };
template <> struct attribute_base_t<pxr::GfVec3d> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<pxr::GfVec3f> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<pxr::GfVec3h> { static constexpr BaseDataType value = BaseDataType::eHalf; };
template <> struct attribute_base_t<pxr::GfVec3i> { static constexpr BaseDataType value = BaseDataType::eInt; };
template <> struct attribute_base_t<pxr::GfVec4d> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<pxr::GfVec4f> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<pxr::GfVec4h> { static constexpr BaseDataType value = BaseDataType::eHalf; };
template <> struct attribute_base_t<pxr::GfVec4i> { static constexpr BaseDataType value = BaseDataType::eInt; };
template <> struct attribute_base_t<pxr::GfQuatd> { static constexpr BaseDataType value = BaseDataType::eDouble; };
template <> struct attribute_base_t<pxr::GfQuatf> { static constexpr BaseDataType value = BaseDataType::eFloat; };
template <> struct attribute_base_t<pxr::GfQuath> { static constexpr BaseDataType value = BaseDataType::eHalf; };
} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni


namespace omni {
namespace graph {
namespace core {
namespace ogn {

// ==============================================================================================================
// Specializing the attribute_type_traits gives more options for casting data extracted from RuntimeAttributes.
//
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfHalf>();
template <>
struct attribute_type_traits<pxr::GfHalf>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = true;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfHalf>::value;
    using actual_t = pxr::GfHalf;
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfHalf;
    static constexpr int tupleCount = 1;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfHalf[]>();
template <>
struct attribute_type_traits<pxr::GfHalf[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = true;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfHalf>::value;
    using actual_t = pxr::GfHalf[];
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfHalf;
    static constexpr int tupleCount = 1;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::TfToken>();
template <>
struct attribute_type_traits<pxr::TfToken>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = true;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::TfToken>::value;
    using actual_t = pxr::TfToken;
    using element_t = pxr::TfToken;
    using data_t = pxr::TfToken;
    static constexpr int tupleCount = 1;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::TfToken[]>();
template <>
struct attribute_type_traits<pxr::TfToken[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = true;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::TfToken>::value;
    using actual_t = pxr::TfToken[];
    using element_t = pxr::TfToken;
    using data_t = pxr::TfToken;
    static constexpr int tupleCount = 1;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::SdfPath>();
template <>
struct attribute_type_traits<pxr::SdfPath>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = true;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::SdfPath>::value;
    using actual_t = pxr::SdfPath;
    using element_t = pxr::SdfPath;
    using data_t = pxr::SdfPath;
    static constexpr int tupleCount = 1;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::SdfPath[]>();
template <>
struct attribute_type_traits<pxr::SdfPath[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = true;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::SdfPath>::value;
    using actual_t = pxr::SdfPath[];
    using element_t = pxr::SdfPath;
    using data_t = pxr::SdfPath;
    static constexpr int tupleCount = 1;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::SdfTimeCode>();
template <>
struct attribute_type_traits<pxr::SdfTimeCode>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = true;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::SdfTimeCode>::value;
    using actual_t = pxr::SdfTimeCode;
    using element_t = pxr::SdfTimeCode;
    using data_t = pxr::SdfTimeCode;
    static constexpr int tupleCount = 1;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::SdfTimeCode[]>();
template <>
struct attribute_type_traits<pxr::SdfTimeCode[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = true;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::SdfTimeCode>::value;
    using actual_t = pxr::SdfTimeCode[];
    using element_t = pxr::SdfTimeCode;
    using data_t = pxr::SdfTimeCode;
    static constexpr int tupleCount = 1;
};// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfMatrix2d>();
template <>
struct attribute_type_traits<pxr::GfMatrix2d>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfMatrix2d>::value;
    using actual_t = pxr::GfMatrix2d;
    using element_t = double;
    using data_t = pxr::GfMatrix2d;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfMatrix2d[]>();
template <>
struct attribute_type_traits<pxr::GfMatrix2d[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfMatrix2d>::value;
    using actual_t = pxr::GfMatrix2d[];
    using element_t = double;
    using data_t = pxr::GfMatrix2d;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfMatrix3d>();
template <>
struct attribute_type_traits<pxr::GfMatrix3d>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfMatrix3d>::value;
    using actual_t = pxr::GfMatrix3d;
    using element_t = double;
    using data_t = pxr::GfMatrix3d;
    static constexpr int tupleCount = 9;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfMatrix3d[]>();
template <>
struct attribute_type_traits<pxr::GfMatrix3d[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfMatrix3d>::value;
    using actual_t = pxr::GfMatrix3d[];
    using element_t = double;
    using data_t = pxr::GfMatrix3d;
    static constexpr int tupleCount = 9;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfMatrix4d>();
template <>
struct attribute_type_traits<pxr::GfMatrix4d>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfMatrix4d>::value;
    using actual_t = pxr::GfMatrix4d;
    using element_t = double;
    using data_t = pxr::GfMatrix4d;
    static constexpr int tupleCount = 16;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfMatrix4d[]>();
template <>
struct attribute_type_traits<pxr::GfMatrix4d[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfMatrix4d>::value;
    using actual_t = pxr::GfMatrix4d[];
    using element_t = double;
    using data_t = pxr::GfMatrix4d;
    static constexpr int tupleCount = 16;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2d>();
template <>
struct attribute_type_traits<pxr::GfVec2d>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2d>::value;
    using actual_t = pxr::GfVec2d;
    using element_t = double;
    using data_t = pxr::GfVec2d;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2d[]>();
template <>
struct attribute_type_traits<pxr::GfVec2d[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2d>::value;
    using actual_t = pxr::GfVec2d[];
    using element_t = double;
    using data_t = pxr::GfVec2d;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2f>();
template <>
struct attribute_type_traits<pxr::GfVec2f>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2f>::value;
    using actual_t = pxr::GfVec2f;
    using element_t = float;
    using data_t = pxr::GfVec2f;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2f[]>();
template <>
struct attribute_type_traits<pxr::GfVec2f[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2f>::value;
    using actual_t = pxr::GfVec2f[];
    using element_t = float;
    using data_t = pxr::GfVec2f;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2h>();
template <>
struct attribute_type_traits<pxr::GfVec2h>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2h>::value;
    using actual_t = pxr::GfVec2h;
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfVec2h;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2h[]>();
template <>
struct attribute_type_traits<pxr::GfVec2h[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2h>::value;
    using actual_t = pxr::GfVec2h[];
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfVec2h;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2i>();
template <>
struct attribute_type_traits<pxr::GfVec2i>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2i>::value;
    using actual_t = pxr::GfVec2i;
    using element_t = int;
    using data_t = pxr::GfVec2i;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec2i[]>();
template <>
struct attribute_type_traits<pxr::GfVec2i[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec2i>::value;
    using actual_t = pxr::GfVec2i[];
    using element_t = int;
    using data_t = pxr::GfVec2i;
    static constexpr int tupleCount = 2;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3d>();
template <>
struct attribute_type_traits<pxr::GfVec3d>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3d>::value;
    using actual_t = pxr::GfVec3d;
    using element_t = double;
    using data_t = pxr::GfVec3d;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3d[]>();
template <>
struct attribute_type_traits<pxr::GfVec3d[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3d>::value;
    using actual_t = pxr::GfVec3d[];
    using element_t = double;
    using data_t = pxr::GfVec3d;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3f>();
template <>
struct attribute_type_traits<pxr::GfVec3f>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3f>::value;
    using actual_t = pxr::GfVec3f;
    using element_t = float;
    using data_t = pxr::GfVec3f;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3f[]>();
template <>
struct attribute_type_traits<pxr::GfVec3f[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3f>::value;
    using actual_t = pxr::GfVec3f[];
    using element_t = float;
    using data_t = pxr::GfVec3f;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3h>();
template <>
struct attribute_type_traits<pxr::GfVec3h>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3h>::value;
    using actual_t = pxr::GfVec3h;
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfVec3h;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3h[]>();
template <>
struct attribute_type_traits<pxr::GfVec3h[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3h>::value;
    using actual_t = pxr::GfVec3h[];
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfVec3h;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3i>();
template <>
struct attribute_type_traits<pxr::GfVec3i>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3i>::value;
    using actual_t = pxr::GfVec3i;
    using element_t = int;
    using data_t = pxr::GfVec3i;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec3i[]>();
template <>
struct attribute_type_traits<pxr::GfVec3i[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec3i>::value;
    using actual_t = pxr::GfVec3i[];
    using element_t = int;
    using data_t = pxr::GfVec3i;
    static constexpr int tupleCount = 3;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4d>();
template <>
struct attribute_type_traits<pxr::GfVec4d>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4d>::value;
    using actual_t = pxr::GfVec4d;
    using element_t = double;
    using data_t = pxr::GfVec4d;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4d[]>();
template <>
struct attribute_type_traits<pxr::GfVec4d[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4d>::value;
    using actual_t = pxr::GfVec4d[];
    using element_t = double;
    using data_t = pxr::GfVec4d;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4f>();
template <>
struct attribute_type_traits<pxr::GfVec4f>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4f>::value;
    using actual_t = pxr::GfVec4f;
    using element_t = float;
    using data_t = pxr::GfVec4f;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4f[]>();
template <>
struct attribute_type_traits<pxr::GfVec4f[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4f>::value;
    using actual_t = pxr::GfVec4f[];
    using element_t = float;
    using data_t = pxr::GfVec4f;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4h>();
template <>
struct attribute_type_traits<pxr::GfVec4h>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4h>::value;
    using actual_t = pxr::GfVec4h;
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfVec4h;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4h[]>();
template <>
struct attribute_type_traits<pxr::GfVec4h[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4h>::value;
    using actual_t = pxr::GfVec4h[];
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfVec4h;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4i>();
template <>
struct attribute_type_traits<pxr::GfVec4i>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4i>::value;
    using actual_t = pxr::GfVec4i;
    using element_t = int;
    using data_t = pxr::GfVec4i;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfVec4i[]>();
template <>
struct attribute_type_traits<pxr::GfVec4i[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfVec4i>::value;
    using actual_t = pxr::GfVec4i[];
    using element_t = int;
    using data_t = pxr::GfVec4i;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfQuatd>();
template <>
struct attribute_type_traits<pxr::GfQuatd>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfQuatd>::value;
    using actual_t = pxr::GfQuatd;
    using element_t = double;
    using data_t = pxr::GfQuatd;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfQuatd[]>();
template <>
struct attribute_type_traits<pxr::GfQuatd[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfQuatd>::value;
    using actual_t = pxr::GfQuatd[];
    using element_t = double;
    using data_t = pxr::GfQuatd;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfQuatf>();
template <>
struct attribute_type_traits<pxr::GfQuatf>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfQuatf>::value;
    using actual_t = pxr::GfQuatf;
    using element_t = float;
    using data_t = pxr::GfQuatf;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfQuatf[]>();
template <>
struct attribute_type_traits<pxr::GfQuatf[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfQuatf>::value;
    using actual_t = pxr::GfQuatf[];
    using element_t = float;
    using data_t = pxr::GfQuatf;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfQuath>();
template <>
struct attribute_type_traits<pxr::GfQuath>
{
    static constexpr bool isArray = false;
    static constexpr int arrayDepth = 0;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = true;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = false;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfQuath>::value;
    using actual_t = pxr::GfQuath;
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfQuath;
    static constexpr int tupleCount = 4;
};
// --------------------------------------------------------------------------------------------------------------
// auto value = runtimeAttribute.get<pxr::GfQuath[]>();
template <>
struct attribute_type_traits<pxr::GfQuath[]>
{
    static constexpr bool isArray = true;
    static constexpr int arrayDepth = 1;
    static constexpr bool isSimpleType = false;
    static constexpr bool isTupleType = false;
    static constexpr bool isArrayType = false;
    static constexpr bool isTupleArrayType = true;
    static constexpr BaseDataType baseType = attribute_base_t<pxr::GfQuath>::value;
    using actual_t = pxr::GfQuath[];
    using element_t = pxr::GfHalf;
    using data_t = pxr::GfQuath;
    static constexpr int tupleCount = 4;
};


} // namespace ogn
} // namespace core
} // namespace graph
} // namespace omni
