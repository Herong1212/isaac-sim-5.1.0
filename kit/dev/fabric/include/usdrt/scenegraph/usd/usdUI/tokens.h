// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usdUI/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdUITokensType

/// Provides standard set of public tokens for UsdUI schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdUITokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdUITokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdUITokensType
{
    UsdUITokensType();
    /// @brief "closed"
    ///
    /// Possible value for UsdUINodeGraphNodeAPI::GetUiNodegraphNodeExpansionStateAttr()
    const TfToken closed;
    /// @brief "minimized"
    ///
    /// Possible value for UsdUINodeGraphNodeAPI::GetUiNodegraphNodeExpansionStateAttr()
    const TfToken minimized;
    /// @brief "open"
    ///
    /// Possible value for UsdUINodeGraphNodeAPI::GetUiNodegraphNodeExpansionStateAttr()
    const TfToken open;
    /// @brief "ui:description"
    ///
    /// UsdUIBackdrop
    const TfToken uiDescription;
    /// @brief "ui:displayGroup"
    ///
    /// UsdUISceneGraphPrimAPI
    const TfToken uiDisplayGroup;
    /// @brief "ui:displayName"
    ///
    /// UsdUISceneGraphPrimAPI
    const TfToken uiDisplayName;
    /// @brief "ui:nodegraph:node:displayColor"
    ///
    /// UsdUINodeGraphNodeAPI
    const TfToken uiNodegraphNodeDisplayColor;
    /// @brief "ui:nodegraph:node:expansionState"
    ///
    /// UsdUINodeGraphNodeAPI
    const TfToken uiNodegraphNodeExpansionState;
    /// @brief "ui:nodegraph:node:icon"
    ///
    /// UsdUINodeGraphNodeAPI
    const TfToken uiNodegraphNodeIcon;
    /// @brief "ui:nodegraph:node:pos"
    ///
    /// UsdUINodeGraphNodeAPI
    const TfToken uiNodegraphNodePos;
    /// @brief "ui:nodegraph:node:size"
    ///
    /// UsdUINodeGraphNodeAPI
    const TfToken uiNodegraphNodeSize;
    /// @brief "ui:nodegraph:node:stackingOrder"
    ///
    /// UsdUINodeGraphNodeAPI
    const TfToken uiNodegraphNodeStackingOrder;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdUITokensType::UsdUITokensType()
    : closed("closed"),
      minimized("minimized"),
      open("open"),
      uiDescription("ui:description"),
      uiDisplayGroup("ui:displayGroup"),
      uiDisplayName("ui:displayName"),
      uiNodegraphNodeDisplayColor("ui:nodegraph:node:displayColor"),
      uiNodegraphNodeExpansionState("ui:nodegraph:node:expansionState"),
      uiNodegraphNodeIcon("ui:nodegraph:node:icon"),
      uiNodegraphNodePos("ui:nodegraph:node:pos"),
      uiNodegraphNodeSize("ui:nodegraph:node:size"),
      uiNodegraphNodeStackingOrder("ui:nodegraph:node:stackingOrder")
{
}

struct UsdUITokensTypeAccessor
{
    const UsdUITokensType* operator->()
    {
        static const UsdUITokensType tokens;
        return &tokens;
    }
};


inline UsdUITokensTypeAccessor UsdUITokens;


} // namespace usdrt
