// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usdSkel/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdSkelTokensType

/// Provides standard set of public tokens for UsdSkel schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdSkelTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdSkelTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdSkelTokensType
{
    UsdSkelTokensType();
    /// @brief "bindTransforms"
    ///
    /// UsdSkelSkeleton
    const TfToken bindTransforms;
    /// @brief "blendShapes"
    ///
    /// UsdSkelAnimation
    const TfToken blendShapes;
    /// @brief "blendShapeWeights"
    ///
    /// UsdSkelAnimation
    const TfToken blendShapeWeights;
    /// @brief "ClassicLinear"
    ///
    /// Possible value for UsdSkelBindingAPI::GetSkelSkinningMethodAttr(), Default value for
    /// UsdSkelBindingAPI::GetSkelSkinningMethodAttr()
    const TfToken classicLinear;
    /// @brief "DualQuaternion"
    ///
    /// Possible value for UsdSkelBindingAPI::GetSkelSkinningMethodAttr()
    const TfToken dualQuaternion;
    /// @brief "jointNames"
    ///
    /// UsdSkelSkeleton
    const TfToken jointNames;
    /// @brief "joints"
    ///
    /// UsdSkelAnimation, UsdSkelSkeleton
    const TfToken joints;
    /// @brief "normalOffsets"
    ///
    /// UsdSkelBlendShape
    const TfToken normalOffsets;
    /// @brief "offsets"
    ///
    /// UsdSkelBlendShape
    const TfToken offsets;
    /// @brief "pointIndices"
    ///
    /// UsdSkelBlendShape
    const TfToken pointIndices;
    /// @brief "primvars:skel:geomBindTransform"
    ///
    /// UsdSkelBindingAPI
    const TfToken primvarsSkelGeomBindTransform;
    /// @brief "primvars:skel:jointIndices"
    ///
    /// UsdSkelBindingAPI
    const TfToken primvarsSkelJointIndices;
    /// @brief "primvars:skel:jointWeights"
    ///
    /// UsdSkelBindingAPI
    const TfToken primvarsSkelJointWeights;
    /// @brief "primvars:skel:skinningBlendWeights"
    ///
    /// UsdSkelBindingAPI
    const TfToken primvarsSkelSkinningBlendWeights;
    /// @brief "restTransforms"
    ///
    /// UsdSkelSkeleton
    const TfToken restTransforms;
    /// @brief "rotations"
    ///
    /// UsdSkelAnimation
    const TfToken rotations;
    /// @brief "scales"
    ///
    /// UsdSkelAnimation
    const TfToken scales;
    /// @brief "skel:animationSource"
    ///
    /// UsdSkelBindingAPI
    const TfToken skelAnimationSource;
    /// @brief "skel:blendShapes"
    ///
    /// UsdSkelBindingAPI
    const TfToken skelBlendShapes;
    /// @brief "skel:blendShapeTargets"
    ///
    /// UsdSkelBindingAPI
    const TfToken skelBlendShapeTargets;
    /// @brief "skel:joints"
    ///
    /// UsdSkelBindingAPI
    const TfToken skelJoints;
    /// @brief "skel:skeleton"
    ///
    /// UsdSkelBindingAPI
    const TfToken skelSkeleton;
    /// @brief "skel:skinningMethod"
    ///
    /// UsdSkelBindingAPI
    const TfToken skelSkinningMethod;
    /// @brief "translations"
    ///
    /// UsdSkelAnimation
    const TfToken translations;
    /// @brief "weight"
    ///
    /// UsdSkelInbetweenShape - The weight location at which the inbetween shape applies.
    const TfToken weight;
    /// @brief "WeightedBlend"
    ///
    /// Possible value for UsdSkelBindingAPI::GetSkelSkinningMethodAttr()
    const TfToken weightedBlend;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdSkelTokensType::UsdSkelTokensType()
    : bindTransforms("bindTransforms"),
      blendShapes("blendShapes"),
      blendShapeWeights("blendShapeWeights"),
      classicLinear("ClassicLinear"),
      dualQuaternion("DualQuaternion"),
      jointNames("jointNames"),
      joints("joints"),
      normalOffsets("normalOffsets"),
      offsets("offsets"),
      pointIndices("pointIndices"),
      primvarsSkelGeomBindTransform("primvars:skel:geomBindTransform"),
      primvarsSkelJointIndices("primvars:skel:jointIndices"),
      primvarsSkelJointWeights("primvars:skel:jointWeights"),
      primvarsSkelSkinningBlendWeights("primvars:skel:skinningBlendWeights"),
      restTransforms("restTransforms"),
      rotations("rotations"),
      scales("scales"),
      skelAnimationSource("skel:animationSource"),
      skelBlendShapes("skel:blendShapes"),
      skelBlendShapeTargets("skel:blendShapeTargets"),
      skelJoints("skel:joints"),
      skelSkeleton("skel:skeleton"),
      skelSkinningMethod("skel:skinningMethod"),
      translations("translations"),
      weight("weight"),
      weightedBlend("WeightedBlend")
{
}

struct UsdSkelTokensTypeAccessor
{
    const UsdSkelTokensType* operator->()
    {
        static const UsdSkelTokensType tokens;
        return &tokens;
    }
};


inline UsdSkelTokensTypeAccessor UsdSkelTokens;


} // namespace usdrt
