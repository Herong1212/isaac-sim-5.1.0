// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usdVol/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdVolTokensType

/// Provides standard set of public tokens for UsdVol schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdVolTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdVolTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdVolTokensType
{
    UsdVolTokensType();
    /// @brief "bool"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken bool_;
    /// @brief "Color"
    ///
    /// Possible value for UsdVolFieldAsset::GetVectorDataRoleHintAttr()
    const TfToken color;
    /// @brief "double2"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken double2;
    /// @brief "double3"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr(), Possible value for
    /// UsdVolField3DAsset::GetFieldDataTypeAttr()
    const TfToken double3;
    /// @brief "double"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr(), Possible value for
    /// UsdVolField3DAsset::GetFieldDataTypeAttr()
    const TfToken double_;
    /// @brief "field"
    ///
    /// This is the namespace prefix used to  specify the fields that make up a volume primitive.
    const TfToken field;
    /// @brief "fieldClass"
    ///
    /// UsdVolOpenVDBAsset
    const TfToken fieldClass;
    /// @brief "fieldDataType"
    ///
    /// UsdVolOpenVDBAsset, UsdVolField3DAsset, UsdVolFieldAsset
    const TfToken fieldDataType;
    /// @brief "fieldIndex"
    ///
    /// UsdVolFieldAsset
    const TfToken fieldIndex;
    /// @brief "fieldName"
    ///
    /// UsdVolFieldAsset
    const TfToken fieldName;
    /// @brief "fieldPurpose"
    ///
    /// UsdVolField3DAsset
    const TfToken fieldPurpose;
    /// @brief "filePath"
    ///
    /// UsdVolFieldAsset
    const TfToken filePath;
    /// @brief "float2"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken float2;
    /// @brief "float3"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr(), Possible value for
    /// UsdVolField3DAsset::GetFieldDataTypeAttr()
    const TfToken float3;
    /// @brief "float"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr(), Possible value for
    /// UsdVolField3DAsset::GetFieldDataTypeAttr()
    const TfToken float_;
    /// @brief "fogVolume"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldClassAttr()
    const TfToken fogVolume;
    /// @brief "half"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr(), Possible value for
    /// UsdVolField3DAsset::GetFieldDataTypeAttr()
    const TfToken half;
    /// @brief "half2"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken half2;
    /// @brief "half3"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr(), Possible value for
    /// UsdVolField3DAsset::GetFieldDataTypeAttr()
    const TfToken half3;
    /// @brief "int2"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken int2;
    /// @brief "int3"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken int3;
    /// @brief "int64"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken int64;
    /// @brief "int"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken int_;
    /// @brief "levelSet"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldClassAttr()
    const TfToken levelSet;
    /// @brief "mask"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken mask;
    /// @brief "matrix3d"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken matrix3d;
    /// @brief "matrix4d"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken matrix4d;
    /// @brief "None"
    ///
    /// Possible value for UsdVolFieldAsset::GetVectorDataRoleHintAttr(), Default value for
    /// UsdVolFieldAsset::GetVectorDataRoleHintAttr()
    const TfToken none;
    /// @brief "Normal"
    ///
    /// Possible value for UsdVolFieldAsset::GetVectorDataRoleHintAttr()
    const TfToken normal;
    /// @brief "Point"
    ///
    /// Possible value for UsdVolFieldAsset::GetVectorDataRoleHintAttr()
    const TfToken point;
    /// @brief "quatd"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken quatd;
    /// @brief "staggered"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldClassAttr()
    const TfToken staggered;
    /// @brief "string"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken string;
    /// @brief "uint"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldDataTypeAttr()
    const TfToken uint;
    /// @brief "unknown"
    ///
    /// Possible value for UsdVolOpenVDBAsset::GetFieldClassAttr()
    const TfToken unknown;
    /// @brief "Vector"
    ///
    /// Possible value for UsdVolFieldAsset::GetVectorDataRoleHintAttr()
    const TfToken vector;
    /// @brief "vectorDataRoleHint"
    ///
    /// UsdVolFieldAsset
    const TfToken vectorDataRoleHint;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdVolTokensType::UsdVolTokensType()
    : bool_("bool"),
      color("Color"),
      double2("double2"),
      double3("double3"),
      double_("double"),
      field("field"),
      fieldClass("fieldClass"),
      fieldDataType("fieldDataType"),
      fieldIndex("fieldIndex"),
      fieldName("fieldName"),
      fieldPurpose("fieldPurpose"),
      filePath("filePath"),
      float2("float2"),
      float3("float3"),
      float_("float"),
      fogVolume("fogVolume"),
      half("half"),
      half2("half2"),
      half3("half3"),
      int2("int2"),
      int3("int3"),
      int64("int64"),
      int_("int"),
      levelSet("levelSet"),
      mask("mask"),
      matrix3d("matrix3d"),
      matrix4d("matrix4d"),
      none("None"),
      normal("Normal"),
      point("Point"),
      quatd("quatd"),
      staggered("staggered"),
      string("string"),
      uint("uint"),
      unknown("unknown"),
      vector("Vector"),
      vectorDataRoleHint("vectorDataRoleHint")
{
}

struct UsdVolTokensTypeAccessor
{
    const UsdVolTokensType* operator->()
    {
        static const UsdVolTokensType tokens;
        return &tokens;
    }
};


inline UsdVolTokensTypeAccessor UsdVolTokens;


} // namespace usdrt
