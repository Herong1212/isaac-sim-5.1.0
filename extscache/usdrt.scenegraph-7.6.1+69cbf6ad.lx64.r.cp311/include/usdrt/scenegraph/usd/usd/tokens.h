// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usd/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdTokensType

/// Provides standard set of public tokens for Usd schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdTokensType
{
    UsdTokensType();
    /// @brief "apiSchemas"
    ///
    /// A listop metadata containing the API schemas which have been applied to this prim, using the Apply() method on
    /// the particular schema class.
    const TfToken apiSchemas;
    /// @brief "clips"
    ///
    /// Dictionary that contains the definition of the clip sets on this prim. See \ref UsdClipsAPI::GetClips.
    const TfToken clips;
    /// @brief "clipSets"
    ///
    /// ListOp that may be used to affect how opinions from clip sets are applied during value resolution.  See \ref
    /// UsdClipsAPI::GetClipSets.
    const TfToken clipSets;
    /// @brief "collection"
    ///
    /// Property namespace prefix for the UsdCollectionAPI schema.
    const TfToken collection;
    /// @brief "exclude"
    ///
    /// This is the token used to exclude a path from a collection.  Although it is not a possible value for the
    /// "expansionRule" attribute, it is used as the expansionRule for excluded paths  in
    /// UsdCollectionAPI::MembershipQuery::IsPathIncluded.
    const TfToken exclude;
    /// @brief "excludes"
    ///
    /// UsdCollectionAPI
    const TfToken excludes;
    /// @brief "expandPrims"
    ///
    /// Possible value for UsdCollectionAPI::GetExpansionRuleAttr(), Default value for
    /// UsdCollectionAPI::GetExpansionRuleAttr()
    const TfToken expandPrims;
    /// @brief "expandPrimsAndProperties"
    ///
    /// Possible value for UsdCollectionAPI::GetExpansionRuleAttr()
    const TfToken expandPrimsAndProperties;
    /// @brief "expansionRule"
    ///
    /// UsdCollectionAPI
    const TfToken expansionRule;
    /// @brief "explicitOnly"
    ///
    /// Possible value for UsdCollectionAPI::GetExpansionRuleAttr()
    const TfToken explicitOnly;
    /// @brief "fallbackPrimTypes"
    ///
    /// A dictionary metadata that maps the name of a concrete schema prim type to an ordered list of schema prim types
    /// to use instead if the schema prim type doesn't exist in version of USD being used.
    const TfToken fallbackPrimTypes;
    /// @brief "includeRoot"
    ///
    /// UsdCollectionAPI
    const TfToken includeRoot;
    /// @brief "includes"
    ///
    /// UsdCollectionAPI
    const TfToken includes;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdTokensType::UsdTokensType()
    : apiSchemas("apiSchemas"),
      clips("clips"),
      clipSets("clipSets"),
      collection("collection"),
      exclude("exclude"),
      excludes("excludes"),
      expandPrims("expandPrims"),
      expandPrimsAndProperties("expandPrimsAndProperties"),
      expansionRule("expansionRule"),
      explicitOnly("explicitOnly"),
      fallbackPrimTypes("fallbackPrimTypes"),
      includeRoot("includeRoot"),
      includes("includes")
{
}

struct UsdTokensTypeAccessor
{
    const UsdTokensType* operator->()
    {
        static const UsdTokensType tokens;
        return &tokens;
    }
};


inline UsdTokensTypeAccessor UsdTokens;


} // namespace usdrt
