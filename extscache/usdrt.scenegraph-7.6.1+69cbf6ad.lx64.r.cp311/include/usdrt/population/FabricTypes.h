// Copyright (c) 2023-2025, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/Type.h>

namespace usdrt
{

namespace population
{

constexpr omni::fabric::Type typeToken(omni::fabric::BaseDataType::eToken, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeTokenArray(omni::fabric::BaseDataType::eToken, 1, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeAsset(omni::fabric::BaseDataType::eAsset, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeAssetArray(omni::fabric::BaseDataType::eAsset, 1, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeChar(omni::fabric::BaseDataType::eUChar, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeString(omni::fabric::BaseDataType::eUChar, 1, 1, omni::fabric::AttributeRole::eText);
constexpr omni::fabric::Type typeRelationship(omni::fabric::BaseDataType::eRelationship, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typePath(omni::fabric::BaseDataType::ePath, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeFloat(omni::fabric::BaseDataType::eFloat, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeFloat2(omni::fabric::BaseDataType::eFloat, 2, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeFloat3(omni::fabric::BaseDataType::eFloat, 3, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeFloat3Vector(omni::fabric::BaseDataType::eFloat, 3, 0, omni::fabric::AttributeRole::eVector);
constexpr omni::fabric::Type typeFloat4(omni::fabric::BaseDataType::eFloat, 4, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt(omni::fabric::BaseDataType::eInt, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt2(omni::fabric::BaseDataType::eInt, 2, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt3(omni::fabric::BaseDataType::eInt, 3, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt4(omni::fabric::BaseDataType::eInt, 4, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt64(omni::fabric::BaseDataType::eInt64, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt64_2(omni::fabric::BaseDataType::eInt64, 2, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt64_3(omni::fabric::BaseDataType::eInt64, 3, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInt64_4(omni::fabric::BaseDataType::eInt64, 4, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeUint(omni::fabric::BaseDataType::eUInt, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeUint64(omni::fabric::BaseDataType::eUInt64, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDouble(omni::fabric::BaseDataType::eDouble, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDouble2(omni::fabric::BaseDataType::eDouble, 2, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDouble3(omni::fabric::BaseDataType::eDouble, 3, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDouble4(omni::fabric::BaseDataType::eDouble, 4, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDoubleArray(omni::fabric::BaseDataType::eDouble, 1, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDouble2Array(omni::fabric::BaseDataType::eDouble, 2, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDouble3Array(omni::fabric::BaseDataType::eDouble, 3, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeDouble4Array(omni::fabric::BaseDataType::eDouble, 4, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeHalf(omni::fabric::BaseDataType::eHalf, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeHalf2(omni::fabric::BaseDataType::eHalf, 2, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeHalf3(omni::fabric::BaseDataType::eHalf, 3, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeHalf4(omni::fabric::BaseDataType::eHalf, 4, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeQuath(omni::fabric::BaseDataType::eHalf, 4, 0, omni::fabric::AttributeRole::eQuaternion);
constexpr omni::fabric::Type typeQuatf(omni::fabric::BaseDataType::eFloat, 4, 0, omni::fabric::AttributeRole::eQuaternion);
constexpr omni::fabric::Type typeQuatd(omni::fabric::BaseDataType::eDouble, 4, 0, omni::fabric::AttributeRole::eQuaternion);
constexpr omni::fabric::Type typeIntArray(omni::fabric::BaseDataType::eInt, 1, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeUIntArray(omni::fabric::BaseDataType::eUInt, 1, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeFloat2Array(omni::fabric::BaseDataType::eFloat,
                                             2,
                                             1,
                                             omni::fabric::AttributeRole::eTexCoord);
constexpr omni::fabric::Type typeFloat3Array(omni::fabric::BaseDataType::eFloat, 3, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typePoint3fArray(omni::fabric::BaseDataType::eFloat,
                                              3,
                                              1,
                                              omni::fabric::AttributeRole::ePosition);
constexpr omni::fabric::Type typeNormal3fArray(omni::fabric::BaseDataType::eFloat,
                                               3,
                                               1,
                                               omni::fabric::AttributeRole::eNormal);
constexpr omni::fabric::Type typeHalf3Array(omni::fabric::BaseDataType::eHalf, 3, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeFloat4Array(omni::fabric::BaseDataType::eFloat, 4, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeHalf4Array(omni::fabric::BaseDataType::eHalf,
                                            4,
                                            1,
                                            omni::fabric::AttributeRole::eQuaternion);
constexpr omni::fabric::Type typeFloatArray(omni::fabric::BaseDataType::eFloat, 1, 1, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeRange3d(omni::fabric::BaseDataType::eDouble, 6, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeBool(omni::fabric::BaseDataType::eBool, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeAppliedSchemaTag(omni::fabric::BaseDataType::eTag,
                                                  1,
                                                  0,
                                                  omni::fabric::AttributeRole::eAppliedSchema);
constexpr omni::fabric::Type typePrimTypeTag(omni::fabric::BaseDataType::eTag,
                                             1,
                                             0,
                                             omni::fabric::AttributeRole::ePrimTypeName);
constexpr omni::fabric::Type typeAncestorPrimTypeTag(omni::fabric::BaseDataType::eTag,
                                                     1,
                                                     0,
                                                     omni::fabric::AttributeRole::eAncestorPrimTypeName);
constexpr omni::fabric::Type typeTag(omni::fabric::BaseDataType::eTag, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeUInt(omni::fabric::BaseDataType::eUInt, 1, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeInstancedAttributeTag(omni::fabric::BaseDataType::eTag,
                                                       1,
                                                       0,
                                                       omni::fabric::AttributeRole::eInstancedAttribute);
constexpr omni::fabric::Type typeHashValue(omni::fabric::BaseDataType::eUInt64, 2, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeHashKey(omni::fabric::BaseDataType::eUInt64, 4, 0, omni::fabric::AttributeRole::eNone);
constexpr omni::fabric::Type typeMatrix2f(omni::fabric::BaseDataType::eFloat, 4, 0, omni::fabric::AttributeRole::eMatrix);
constexpr omni::fabric::Type typeMatrix3f(omni::fabric::BaseDataType::eFloat, 9, 0, omni::fabric::AttributeRole::eMatrix);
constexpr omni::fabric::Type typeMatrix4f(omni::fabric::BaseDataType::eFloat, 16, 0, omni::fabric::AttributeRole::eMatrix);
constexpr omni::fabric::Type typeMatrix2d(omni::fabric::BaseDataType::eDouble, 4, 0, omni::fabric::AttributeRole::eMatrix);
constexpr omni::fabric::Type typeMatrix3d(omni::fabric::BaseDataType::eDouble, 9, 0, omni::fabric::AttributeRole::eMatrix);
constexpr omni::fabric::Type typeMatrix4d(omni::fabric::BaseDataType::eDouble, 16, 0, omni::fabric::AttributeRole::eMatrix);
constexpr omni::fabric::Type typeMatrix4dArray(omni::fabric::BaseDataType::eDouble,
                                               16,
                                               1,
                                               omni::fabric::AttributeRole::eMatrix);

constexpr omni::fabric::Type typeVector3f(omni::fabric::BaseDataType::eFloat, 3, 0, omni::fabric::AttributeRole::eVector);
constexpr omni::fabric::Type typeVector3fArray = { omni::fabric::BaseDataType::eFloat, 3, 1,
                                                   omni::fabric::AttributeRole::eVector };
constexpr omni::fabric::Type typeVector3hArray = { omni::fabric::BaseDataType::eHalf, 3, 1,
                                                   omni::fabric::AttributeRole::eVector };

constexpr omni::fabric::Type typeQuatfArray = { omni::fabric::BaseDataType::eFloat, 4, 1,
                                                omni::fabric::AttributeRole::eQuaternion };
constexpr omni::fabric::Type typeQuathArray = { omni::fabric::BaseDataType::eHalf, 4, 1,
                                                omni::fabric::AttributeRole::eQuaternion };

constexpr omni::fabric::Type typeColor3d = { omni::fabric::BaseDataType::eDouble, 3, 0,
                                             omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor3dArray = { omni::fabric::BaseDataType::eDouble, 3, 1,
                                                  omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor4d = { omni::fabric::BaseDataType::eDouble, 4, 0,
                                             omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor4dArray = { omni::fabric::BaseDataType::eDouble, 4, 1,
                                                  omni::fabric::AttributeRole::eColor };

constexpr omni::fabric::Type typeColor3f = { omni::fabric::BaseDataType::eFloat, 3, 0,
                                             omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor3fArray = { omni::fabric::BaseDataType::eFloat, 3, 1,
                                                  omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor4f = { omni::fabric::BaseDataType::eFloat, 4, 0,
                                             omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor4fArray = { omni::fabric::BaseDataType::eFloat, 4, 1,
                                                  omni::fabric::AttributeRole::eColor };

constexpr omni::fabric::Type typeColor3h = { omni::fabric::BaseDataType::eHalf, 3, 0,
                                             omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor3hArray = { omni::fabric::BaseDataType::eHalf, 3, 1,
                                                  omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor4h = { omni::fabric::BaseDataType::eHalf, 4, 0,
                                             omni::fabric::AttributeRole::eColor };
constexpr omni::fabric::Type typeColor4hArray = { omni::fabric::BaseDataType::eHalf, 4, 1,
                                                  omni::fabric::AttributeRole::eColor };

constexpr omni::fabric::Type typeTimeCode(omni::fabric::BaseDataType::eDouble, 1, 0, omni::fabric::AttributeRole::eTimeCode);
constexpr omni::fabric::Type typeTimeCodeArray(omni::fabric::BaseDataType::eDouble,
                                               1,
                                               1,
                                               omni::fabric::AttributeRole::eTimeCode);

constexpr omni::fabric::Type typeCompactTransform(omni::fabric::BaseDataType::eCompactTransform,
                                                   1,
                                                   0,
                                                   omni::fabric::AttributeRole::eTransform);
} // namespace population

} // namespace usdrt
