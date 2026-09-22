// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file
//!
//! @brief  Basic Sdf data types

#include "valueTypeName.h"

/* Here's a lookup table of types as TypeC / unint32_t
 * Generated 1/21/22 - if the structure of TypeC has changed
 * since
 * then, this table is no longer valid.
 */

#ifndef DOXYGEN_BUILD
#    define TYPEC_ASSET 268
#    define TYPEC_ASSET_ARRAY 65804
#    define TYPEC_BOOL 257
#    define TYPEC_BOOL_ARRAY 65793
#    define TYPEC_COLOR3D 67109641
#    define TYPEC_COLOR3D_ARRAY 67175177
#    define TYPEC_COLOR3F 67109640
#    define TYPEC_COLOR3F_ARRAY 67175176
#    define TYPEC_COLOR3H 67109639
#    define TYPEC_COLOR3H_ARRAY 67175175
#    define TYPEC_COLOR4D 67109897
#    define TYPEC_COLOR4D_ARRAY 67175433
#    define TYPEC_COLOR4F 67109896
#    define TYPEC_COLOR4F_ARRAY 67175432
#    define TYPEC_COLOR4H 67109895
#    define TYPEC_COLOR4H_ARRAY 67175431
#    define TYPEC_DOUBLE 265
#    define TYPEC_DOUBLE2 521
#    define TYPEC_DOUBLE2_ARRAY 66057
#    define TYPEC_DOUBLE3 777
#    define TYPEC_DOUBLE3_ARRAY 66313
#    define TYPEC_DOUBLE4 1033
#    define TYPEC_DOUBLE4_ARRAY 66569
#    define TYPEC_DOUBLE_ARRAY 65801
#    define TYPEC_FLOAT 264
#    define TYPEC_FLOAT2 520
#    define TYPEC_FLOAT2_ARRAY 66056
#    define TYPEC_FLOAT3 776
#    define TYPEC_FLOAT3_ARRAY 66312
#    define TYPEC_FLOAT4 1032
#    define TYPEC_FLOAT4_ARRAY 66568
#    define TYPEC_FLOAT_ARRAY 65800
#    define TYPEC_FRAME 134221833
#    define TYPEC_FRAME_ARRAY 134287369
#    define TYPEC_HALF 263
#    define TYPEC_HALF2 519
#    define TYPEC_HALF2_ARRAY 66055
#    define TYPEC_HALF3 775
#    define TYPEC_HALF3_ARRAY 66311
#    define TYPEC_HALF4 1031
#    define TYPEC_HALF4_ARRAY 66567
#    define TYPEC_HALF_ARRAY 65799
#    define TYPEC_INT 259
#    define TYPEC_INT2 515
#    define TYPEC_INT2_ARRAY 66051
#    define TYPEC_INT3 771
#    define TYPEC_INT3_ARRAY 66307
#    define TYPEC_INT4 1027
#    define TYPEC_INT4_ARRAY 66563
#    define TYPEC_INT64 261
#    define TYPEC_INT64_ARRAY 65797
#    define TYPEC_INT_ARRAY 65795
#    define TYPEC_TRANSFORM4D 234882057
#    define TYPEC_TRANSFORM4D_ARRAY 234947593
#    define TYPEC_TRANSFORM4F 234882056
#    define TYPEC_TRANSFORM4F_ARRAY 234947592
#    define TYPEC_TRANSFORM9D 234883337
#    define TYPEC_TRANSFORM9D_ARRAY 234948873
#    define TYPEC_TRANSFORM9F 234883336
#    define TYPEC_TRANSFORM9F_ARRAY 234948872
#    define TYPEC_TRANSFORM16D 234885129
#    define TYPEC_TRANSFORM16D_ARRAY 234950665
#    define TYPEC_TRANSFORM16F 234885128
#    define TYPEC_TRANSFORM16F_ARRAY 234950664
#    define TYPEC_NORMAL3D 33555209
#    define TYPEC_NORMAL3D_ARRAY 33620745
#    define TYPEC_NORMAL3F 33555208
#    define TYPEC_NORMAL3F_ARRAY 33620744
#    define TYPEC_NORMAL3H 33555207
#    define TYPEC_NORMAL3H_ARRAY 33620743
#    define TYPEC_POSITION3D 50332425
#    define TYPEC_POSITION3D_ARRAY 50397961
#    define TYPEC_POSITION3F 50332424
#    define TYPEC_POSITION3F_ARRAY 50397960
#    define TYPEC_POSITION3H 50332423
#    define TYPEC_POSITION3H_ARRAY 50397959
#    define TYPEC_QUATERNION4D 100664329
#    define TYPEC_QUATERNION4D_ARRAY 100729865
#    define TYPEC_QUATERNION4F 100664328
#    define TYPEC_QUATERNION4F_ARRAY 100729864
#    define TYPEC_QUATERNION4H 100664327
#    define TYPEC_QUATERNION4H_ARRAY 100729863
#    define TYPEC_STRING 167837954
#    define TYPEC_STRING_ARRAY 167903490
#    define TYPEC_TEXCOORD2D 83886601
#    define TYPEC_TEXCOORD2D_ARRAY 83952137
#    define TYPEC_TEXCOORD2F 83886600
#    define TYPEC_TEXCOORD2F_ARRAY 83952136
#    define TYPEC_TEXCOORD2H 83886599
#    define TYPEC_TEXCOORD2H_ARRAY 83952135
#    define TYPEC_TEXCOORD3D 83886857
#    define TYPEC_TEXCOORD3D_ARRAY 83952393
#    define TYPEC_TEXCOORD3F 83886856
#    define TYPEC_TEXCOORD3F_ARRAY 83952392
#    define TYPEC_TEXCOORD3H 83886855
#    define TYPEC_TEXCOORD3H_ARRAY 83952391
#    define TYPEC_TIMECODE 150995209
#    define TYPEC_TIMECODE_ARRAY 151060745
#    define TYPEC_TOKEN 266
#    define TYPEC_TOKEN_ARRAY 65802
#    define TYPEC_UCHAR 258
#    define TYPEC_UCHAR_ARRAY 65794
#    define TYPEC_UINT 260
#    define TYPEC_UINT64 262
#    define TYPEC_UINT64_ARRAY 65798
#    define TYPEC_UINT_ARRAY 65796
#    define TYPEC_VECTOR3D 16777993
#    define TYPEC_VECTOR3D_ARRAY 16843529
#    define TYPEC_VECTOR3F 16777992
#    define TYPEC_VECTOR3F_ARRAY 16843528
#    define TYPEC_VECTOR3H 16777991
#    define TYPEC_VECTOR3H_ARRAY 16843527
#    define TYPEC_RANGE3D 1545
#    define TYPEC_RANGE3D_ARRAY 67081
#endif // DOXYGEN_BUILD

namespace usdrt
{

struct SdfValueTypeNamesType
{
    SdfValueTypeName Bool = SdfValueTypeName(BaseDataType::eBool);
    SdfValueTypeName UChar = SdfValueTypeName(BaseDataType::eUChar);
    SdfValueTypeName Int = SdfValueTypeName(BaseDataType::eInt);
    SdfValueTypeName UInt = SdfValueTypeName(BaseDataType::eUInt);
    SdfValueTypeName Int64 = SdfValueTypeName(BaseDataType::eInt64);
    SdfValueTypeName UInt64 = SdfValueTypeName(BaseDataType::eUInt64);
    SdfValueTypeName Half = SdfValueTypeName(BaseDataType::eHalf);
    SdfValueTypeName Float = SdfValueTypeName(BaseDataType::eFloat);
    SdfValueTypeName Double = SdfValueTypeName(BaseDataType::eDouble);
    SdfValueTypeName TimeCode = SdfValueTypeName(BaseDataType::eDouble, 1, 0, AttributeRole::eTimeCode);
    SdfValueTypeName Token = SdfValueTypeName(BaseDataType::eToken);
    SdfValueTypeName Asset = SdfValueTypeName(BaseDataType::eAsset);
    SdfValueTypeName String = SdfValueTypeName(BaseDataType::eUChar, 1, 1, AttributeRole::eText);
    SdfValueTypeName Int2 = SdfValueTypeName(BaseDataType::eInt, 2);
    SdfValueTypeName Int3 = SdfValueTypeName(BaseDataType::eInt, 3);
    SdfValueTypeName Int4 = SdfValueTypeName(BaseDataType::eInt, 4);
    SdfValueTypeName Half2 = SdfValueTypeName(BaseDataType::eHalf, 2);
    SdfValueTypeName Half3 = SdfValueTypeName(BaseDataType::eHalf, 3);
    SdfValueTypeName Half4 = SdfValueTypeName(BaseDataType::eHalf, 4);
    SdfValueTypeName Float2 = SdfValueTypeName(BaseDataType::eFloat, 2);
    SdfValueTypeName Float3 = SdfValueTypeName(BaseDataType::eFloat, 3);
    SdfValueTypeName Float4 = SdfValueTypeName(BaseDataType::eFloat, 4);
    SdfValueTypeName Double2 = SdfValueTypeName(BaseDataType::eDouble, 2);
    SdfValueTypeName Double3 = SdfValueTypeName(BaseDataType::eDouble, 3);
    SdfValueTypeName Double4 = SdfValueTypeName(BaseDataType::eDouble, 4);
    SdfValueTypeName Range3d = SdfValueTypeName(BaseDataType::eDouble, 6);
    SdfValueTypeName Point3h = SdfValueTypeName(BaseDataType::eHalf, 3, 0, AttributeRole::ePosition);
    SdfValueTypeName Point3f = SdfValueTypeName(BaseDataType::eFloat, 3, 0, AttributeRole::ePosition);
    SdfValueTypeName Point3d = SdfValueTypeName(BaseDataType::eDouble, 3, 0, AttributeRole::ePosition);
    SdfValueTypeName Vector3h = SdfValueTypeName(BaseDataType::eHalf, 3, 0, AttributeRole::eVector);
    SdfValueTypeName Vector3f = SdfValueTypeName(BaseDataType::eFloat, 3, 0, AttributeRole::eVector);
    SdfValueTypeName Vector3d = SdfValueTypeName(BaseDataType::eDouble, 3, 0, AttributeRole::eVector);
    SdfValueTypeName Normal3h = SdfValueTypeName(BaseDataType::eHalf, 3, 0, AttributeRole::eNormal);
    SdfValueTypeName Normal3f = SdfValueTypeName(BaseDataType::eFloat, 3, 0, AttributeRole::eNormal);
    SdfValueTypeName Normal3d = SdfValueTypeName(BaseDataType::eDouble, 3, 0, AttributeRole::eNormal);
    SdfValueTypeName Color3h = SdfValueTypeName(BaseDataType::eHalf, 3, 0, AttributeRole::eColor);
    SdfValueTypeName Color3f = SdfValueTypeName(BaseDataType::eFloat, 3, 0, AttributeRole::eColor);
    SdfValueTypeName Color3d = SdfValueTypeName(BaseDataType::eDouble, 3, 0, AttributeRole::eColor);
    SdfValueTypeName Color4h = SdfValueTypeName(BaseDataType::eHalf, 4, 0, AttributeRole::eColor);
    SdfValueTypeName Color4f = SdfValueTypeName(BaseDataType::eFloat, 4, 0, AttributeRole::eColor);
    SdfValueTypeName Color4d = SdfValueTypeName(BaseDataType::eDouble, 4, 0, AttributeRole::eColor);
    SdfValueTypeName Quath = SdfValueTypeName(BaseDataType::eHalf, 4, 0, AttributeRole::eQuaternion);
    SdfValueTypeName Quatf = SdfValueTypeName(BaseDataType::eFloat, 4, 0, AttributeRole::eQuaternion);
    SdfValueTypeName Quatd = SdfValueTypeName(BaseDataType::eDouble, 4, 0, AttributeRole::eQuaternion);
    SdfValueTypeName Matrix2d = SdfValueTypeName(BaseDataType::eDouble, 4, 0, AttributeRole::eMatrix);
    SdfValueTypeName Matrix2f = SdfValueTypeName(BaseDataType::eFloat, 4, 0, AttributeRole::eMatrix);
    SdfValueTypeName Matrix3d = SdfValueTypeName(BaseDataType::eDouble, 9, 0, AttributeRole::eMatrix);
    SdfValueTypeName Matrix3f = SdfValueTypeName(BaseDataType::eFloat, 9, 0, AttributeRole::eMatrix);
    SdfValueTypeName Matrix4d = SdfValueTypeName(BaseDataType::eDouble, 16, 0, AttributeRole::eMatrix);
    SdfValueTypeName Matrix4f = SdfValueTypeName(BaseDataType::eFloat, 16, 0, AttributeRole::eMatrix);
    SdfValueTypeName Frame4d = SdfValueTypeName(BaseDataType::eDouble, 16, 0, AttributeRole::eFrame);
    SdfValueTypeName TexCoord2h = SdfValueTypeName(BaseDataType::eHalf, 2, 0, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord2f = SdfValueTypeName(BaseDataType::eFloat, 2, 0, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord2d = SdfValueTypeName(BaseDataType::eDouble, 2, 0, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord3h = SdfValueTypeName(BaseDataType::eHalf, 3, 0, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord3f = SdfValueTypeName(BaseDataType::eFloat, 3, 0, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord3d = SdfValueTypeName(BaseDataType::eDouble, 3, 0, AttributeRole::eTexCoord);

    SdfValueTypeName BoolArray = SdfValueTypeName(BaseDataType::eBool, 1, 1);
    SdfValueTypeName UCharArray = SdfValueTypeName(BaseDataType::eUChar, 1, 1);
    SdfValueTypeName IntArray = SdfValueTypeName(BaseDataType::eInt, 1, 1);
    SdfValueTypeName UIntArray = SdfValueTypeName(BaseDataType::eUInt, 1, 1);
    SdfValueTypeName Int64Array = SdfValueTypeName(BaseDataType::eInt64, 1, 1);
    SdfValueTypeName UInt64Array = SdfValueTypeName(BaseDataType::eUInt64, 1, 1);
    SdfValueTypeName HalfArray = SdfValueTypeName(BaseDataType::eHalf, 1, 1);
    SdfValueTypeName FloatArray = SdfValueTypeName(BaseDataType::eFloat, 1, 1);
    SdfValueTypeName DoubleArray = SdfValueTypeName(BaseDataType::eDouble, 1, 1);
    SdfValueTypeName TimeCodeArray = SdfValueTypeName(BaseDataType::eDouble, 1, 1, AttributeRole::eTimeCode);
    SdfValueTypeName TokenArray = SdfValueTypeName(BaseDataType::eToken, 1, 1);
    SdfValueTypeName AssetArray = SdfValueTypeName(BaseDataType::eAsset, 1, 1);
    SdfValueTypeName StringArray = SdfValueTypeName(BaseDataType::eUChar, 1, 2, AttributeRole::eText);
    SdfValueTypeName Int2Array = SdfValueTypeName(BaseDataType::eInt, 2, 1);
    SdfValueTypeName Int3Array = SdfValueTypeName(BaseDataType::eInt, 3, 1);
    SdfValueTypeName Int4Array = SdfValueTypeName(BaseDataType::eInt, 4, 1);
    SdfValueTypeName Half2Array = SdfValueTypeName(BaseDataType::eHalf, 2, 1);
    SdfValueTypeName Half3Array = SdfValueTypeName(BaseDataType::eHalf, 3, 1);
    SdfValueTypeName Half4Array = SdfValueTypeName(BaseDataType::eHalf, 4, 1);
    SdfValueTypeName Float2Array = SdfValueTypeName(BaseDataType::eFloat, 2, 1);
    SdfValueTypeName Float3Array = SdfValueTypeName(BaseDataType::eFloat, 3, 1);
    SdfValueTypeName Float4Array = SdfValueTypeName(BaseDataType::eFloat, 4, 1);
    SdfValueTypeName Double2Array = SdfValueTypeName(BaseDataType::eDouble, 2, 1);
    SdfValueTypeName Double3Array = SdfValueTypeName(BaseDataType::eDouble, 3, 1);
    SdfValueTypeName Double4Array = SdfValueTypeName(BaseDataType::eDouble, 4, 1);
    SdfValueTypeName Range3dArray = SdfValueTypeName(BaseDataType::eDouble, 6, 1);
    SdfValueTypeName Point3hArray = SdfValueTypeName(BaseDataType::eHalf, 3, 1, AttributeRole::ePosition);
    SdfValueTypeName Point3fArray = SdfValueTypeName(BaseDataType::eFloat, 3, 1, AttributeRole::ePosition);
    SdfValueTypeName Point3dArray = SdfValueTypeName(BaseDataType::eDouble, 3, 1, AttributeRole::ePosition);
    SdfValueTypeName Vector3hArray = SdfValueTypeName(BaseDataType::eHalf, 3, 1, AttributeRole::eVector);
    SdfValueTypeName Vector3fArray = SdfValueTypeName(BaseDataType::eFloat, 3, 1, AttributeRole::eVector);
    SdfValueTypeName Vector3dArray = SdfValueTypeName(BaseDataType::eDouble, 3, 1, AttributeRole::eVector);
    SdfValueTypeName Normal3hArray = SdfValueTypeName(BaseDataType::eHalf, 3, 1, AttributeRole::eNormal);
    SdfValueTypeName Normal3fArray = SdfValueTypeName(BaseDataType::eFloat, 3, 1, AttributeRole::eNormal);
    SdfValueTypeName Normal3dArray = SdfValueTypeName(BaseDataType::eDouble, 3, 1, AttributeRole::eNormal);
    SdfValueTypeName Color3hArray = SdfValueTypeName(BaseDataType::eHalf, 3, 1, AttributeRole::eColor);
    SdfValueTypeName Color3fArray = SdfValueTypeName(BaseDataType::eFloat, 3, 1, AttributeRole::eColor);
    SdfValueTypeName Color3dArray = SdfValueTypeName(BaseDataType::eDouble, 3, 1, AttributeRole::eColor);
    SdfValueTypeName Color4hArray = SdfValueTypeName(BaseDataType::eHalf, 4, 1, AttributeRole::eColor);
    SdfValueTypeName Color4fArray = SdfValueTypeName(BaseDataType::eFloat, 4, 1, AttributeRole::eColor);
    SdfValueTypeName Color4dArray = SdfValueTypeName(BaseDataType::eDouble, 4, 1, AttributeRole::eColor);
    SdfValueTypeName QuathArray = SdfValueTypeName(BaseDataType::eHalf, 4, 1, AttributeRole::eQuaternion);
    SdfValueTypeName QuatfArray = SdfValueTypeName(BaseDataType::eFloat, 4, 1, AttributeRole::eQuaternion);
    SdfValueTypeName QuatdArray = SdfValueTypeName(BaseDataType::eDouble, 4, 1, AttributeRole::eQuaternion);
    SdfValueTypeName Matrix2dArray = SdfValueTypeName(BaseDataType::eDouble, 4, 1, AttributeRole::eMatrix);
    SdfValueTypeName Matrix2fArray = SdfValueTypeName(BaseDataType::eFloat, 4, 1, AttributeRole::eMatrix);
    SdfValueTypeName Matrix3dArray = SdfValueTypeName(BaseDataType::eDouble, 9, 1, AttributeRole::eMatrix);
    SdfValueTypeName Matrix3fArray = SdfValueTypeName(BaseDataType::eFloat, 9, 1, AttributeRole::eMatrix);
    SdfValueTypeName Matrix4dArray = SdfValueTypeName(BaseDataType::eDouble, 16, 1, AttributeRole::eMatrix);
    SdfValueTypeName Matrix4fArray = SdfValueTypeName(BaseDataType::eFloat, 16, 1, AttributeRole::eMatrix);
    SdfValueTypeName Frame4dArray = SdfValueTypeName(BaseDataType::eDouble, 16, 1, AttributeRole::eFrame);
    SdfValueTypeName TexCoord2hArray = SdfValueTypeName(BaseDataType::eHalf, 2, 1, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord2fArray = SdfValueTypeName(BaseDataType::eFloat, 2, 1, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord2dArray = SdfValueTypeName(BaseDataType::eDouble, 2, 1, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord3hArray = SdfValueTypeName(BaseDataType::eHalf, 3, 1, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord3fArray = SdfValueTypeName(BaseDataType::eFloat, 3, 1, AttributeRole::eTexCoord);
    SdfValueTypeName TexCoord3dArray = SdfValueTypeName(BaseDataType::eDouble, 3, 1, AttributeRole::eTexCoord);

    SdfValueTypeName PrimTypeTag = SdfValueTypeName(BaseDataType::eTag, 1, 0, AttributeRole::ePrimTypeName);
    SdfValueTypeName AppliedSchemaTypeTag = SdfValueTypeName(BaseDataType::eTag, 1, 0, AttributeRole::eAppliedSchema);
    SdfValueTypeName AncestorPrimTypeTag =
        SdfValueTypeName(BaseDataType::eTag, 1, 0, AttributeRole::eAncestorPrimTypeName);
    SdfValueTypeName Tag = SdfValueTypeName(BaseDataType::eTag);
};

inline const SdfValueTypeNamesType* GetTypeNamesType()
{
    static const SdfValueTypeNamesType typeNames;
    return &typeNames;
}

struct SdfValueTypeNamesTypeAccessor
{
    const SdfValueTypeNamesType* operator->()
    {
        return GetTypeNamesType();
    }
};

//! SdfValueTypeNames accessor. This maps SdfValueTypes to omni::fabric::Type.
//!
//! Usage example:
//! SdfValueTypeNames->Bool
inline SdfValueTypeNamesTypeAccessor SdfValueTypeNames;

} // namespace usdrt
