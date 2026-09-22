// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

/// @file usdUI/nodeGraphNodeAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdUI/tokens.h"


// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
// --(END CUSTOM INCLUDES)--

#include <omni/core/IObject.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/base/vt/array.h>
#include <usdrt/scenegraph/interface/IRtAttribute.h>
#include <usdrt/scenegraph/interface/IRtPrim.h>
#include <usdrt/scenegraph/interface/IRtPrimRange.h>
#include <usdrt/scenegraph/interface/IRtRelationship.h>
#include <usdrt/scenegraph/interface/IRtStage.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usd/common.h>
#include <usdrt/scenegraph/usd/usd/prim.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>

namespace usdrt
{

// -------------------------------------------------------------------------- //
// NODEGRAPHNODEAPI                                                            //
// -------------------------------------------------------------------------- //

/// @class UsdUINodeGraphNodeAPI
///
/// /// This api helps storing information about nodes in node graphs.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdUITokens.
/// So to set an attribute to the value "rightHanded", use UsdUITokens->rightHanded
/// as the value.

class UsdUINodeGraphNodeAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdUINodeGraphNodeAPI on UsdPrim @p prim.
    /// Equivalent to UsdUINodeGraphNodeAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdUINodeGraphNodeAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdUINodeGraphNodeAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdUINodeGraphNodeAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdUINodeGraphNodeAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdUINodeGraphNodeAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "NodeGraphNodeAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdUINodeGraphNodeAPI object is returned upon success.
    /// An invalid (or empty) UsdUINodeGraphNodeAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdUINodeGraphNodeAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdUINodeGraphNodeAPI>())
        {
            return UsdUINodeGraphNodeAPI(prim);
        }
        return UsdUINodeGraphNodeAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // POS
    // --------------------------------------------------------------------- //
    /// /// Declared relative position to the parent in a node graph.
    /// X is the horizontal position.
    /// Y is the vertical position. Higher numbers correspond to lower positions
    /// (coordinates are Qt style, not cartesian).
    ///
    /// These positions are not explicitly meant in pixel space, but rather
    /// assume that the size of a node is approximately 1.0x1.0. Where size-x is
    /// the node width and size-y height of the node. Depending on
    /// graph UI implementation, the size of a node may vary in each direction.
    ///
    /// Example: If a node's width is 300 and it is position is at 1000, we
    /// store for x-position: 1000 * (1.0/300)
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float2 ui:nodegraph:node:pos` |
    /// | C++ Type | GfVec2f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2 |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetPosAttr() const;

    /// See GetPosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STACKINGORDER
    // --------------------------------------------------------------------- //
    /// /// This optional value is a useful hint when an application cares about
    /// the visibility of a node and whether each node overlaps another.
    ///
    /// Nodes with lower stacking order values are meant to be drawn below
    /// higher ones. Negative values are meant as background. Positive values
    /// are meant as foreground.
    /// Undefined values should be treated as 0.
    ///
    /// There are no set limits in these values.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int ui:nodegraph:node:stackingOrder` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetStackingOrderAttr() const;

    /// See GetStackingOrderAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStackingOrderAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DISPLAYCOLOR
    // --------------------------------------------------------------------- //
    /// /// This hint defines what tint the node should have in the node graph.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform color3f ui:nodegraph:node:displayColor` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Color3f |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDisplayColorAttr() const;

    /// See GetDisplayColorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisplayColorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ICON
    // --------------------------------------------------------------------- //
    /// /// This points to an image that should be displayed on the node.  It is
    /// intended to be useful for summary visual classification of nodes, rather
    /// than a thumbnail preview of the computed result of the node in some
    /// computational system.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform asset ui:nodegraph:node:icon` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetIconAttr() const;

    /// See GetIconAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIconAttr() const;

public:
    // --------------------------------------------------------------------- //
    // EXPANSIONSTATE
    // --------------------------------------------------------------------- //
    /// /// The current expansionState of the node in the ui.
    /// 'open' = fully expanded
    /// 'closed' = fully collapsed
    /// 'minimized' = should take the least space possible
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token ui:nodegraph:node:expansionState` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdUITokens "Allowed Values" | open, closed, minimized |

    UsdAttribute GetExpansionStateAttr() const;

    /// See GetExpansionStateAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateExpansionStateAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIZE
    // --------------------------------------------------------------------- //
    /// /// Optional size hint for a node in a node graph.
    /// X is the width.
    /// Y is the height.
    ///
    /// This value is optional, because node size is often determined
    /// based on the number of in- and outputs of a node.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float2 ui:nodegraph:node:size` |
    /// | C++ Type | GfVec2f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2 |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSizeAttr() const;

    /// See GetSizeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSizeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdUINodeGraphNodeAPI::_GetStaticTfType()
{
    const static TfToken token("UsdUINodeGraphNodeAPI");
    return token;
}

/* virtual */
inline const TfToken UsdUINodeGraphNodeAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdUINodeGraphNodeAPI");
    return token;
}


inline UsdAttribute UsdUINodeGraphNodeAPI::GetPosAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiNodegraphNodePos));
}

inline UsdAttribute UsdUINodeGraphNodeAPI::CreatePosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiNodegraphNodePos), SdfValueTypeNames->Float2,
                                     /* custom = */ false);
}

inline UsdAttribute UsdUINodeGraphNodeAPI::GetStackingOrderAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiNodegraphNodeStackingOrder));
}

inline UsdAttribute UsdUINodeGraphNodeAPI::CreateStackingOrderAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiNodegraphNodeStackingOrder), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute UsdUINodeGraphNodeAPI::GetDisplayColorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiNodegraphNodeDisplayColor));
}

inline UsdAttribute UsdUINodeGraphNodeAPI::CreateDisplayColorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiNodegraphNodeDisplayColor), SdfValueTypeNames->Color3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdUINodeGraphNodeAPI::GetIconAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiNodegraphNodeIcon));
}

inline UsdAttribute UsdUINodeGraphNodeAPI::CreateIconAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiNodegraphNodeIcon), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdUINodeGraphNodeAPI::GetExpansionStateAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiNodegraphNodeExpansionState));
}

inline UsdAttribute UsdUINodeGraphNodeAPI::CreateExpansionStateAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiNodegraphNodeExpansionState), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdUINodeGraphNodeAPI::GetSizeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiNodegraphNodeSize));
}

inline UsdAttribute UsdUINodeGraphNodeAPI::CreateSizeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiNodegraphNodeSize), SdfValueTypeNames->Float2,
                                     /* custom = */ false);
}


} // namespace usdrt
// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
