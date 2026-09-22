// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file semantics/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class SemanticsTokensType

/// Provides standard set of public tokens for Semantics schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// SemanticsTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use SemanticsTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct SemanticsTokensType
{
    SemanticsTokensType();
    /// @brief "params:semanticData"
    ///
    /// SemanticsSemanticsAPI
    const TfToken paramsSemanticData;
    /// @brief "params:semanticType"
    ///
    /// SemanticsSemanticsAPI
    const TfToken paramsSemanticType;
    /// @brief "semantic"
    ///
    /// Property namespace prefix for the SemanticsSemanticsAPI schema.
    const TfToken semantic;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline SemanticsTokensType::SemanticsTokensType()
    : paramsSemanticData("params:semanticData"),
      paramsSemanticType("params:semanticType"),
      semantic("semantic")
{
}

struct SemanticsTokensTypeAccessor
{
    const SemanticsTokensType* operator->()
    {
        static const SemanticsTokensType tokens;
        return &tokens;
    }
};


inline SemanticsTokensTypeAccessor SemanticsTokens;


}
