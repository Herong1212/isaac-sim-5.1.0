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

/// @file usdUI/backdrop.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
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
// BACKDROP                                                                    //
// -------------------------------------------------------------------------- //

/// @class UsdUIBackdrop
///
/// Provides a 'group-box' for the purpose of node graph organization.
///
/// Unlike containers, backdrops do not store the Shader nodes inside of them.
/// Backdrops are an organizational tool that allows Shader nodes to be visually
/// grouped together in a node-graph UI, but there is no direct relationship
/// between a Shader node and a Backdrop.
///
/// The guideline for a node-graph UI is that a Shader node is considered part
/// of a Backdrop when the Backdrop is the smallest Backdrop a Shader node's
/// bounding-box fits inside.
///
/// Backdrop objects are contained inside a NodeGraph, similar to how Shader
/// objects are contained inside a NodeGraph.
///
/// Backdrops have no shading inputs or outputs that influence the rendered
/// results of a NodeGraph. Therefore they can be safely ignored during import.
///
/// Like Shaders and NodeGraphs, Backdrops subscribe to the NodeGraphNodeAPI to
/// specify position and size.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdUITokens.
/// So to set an attribute to the value "rightHanded", use UsdUITokens->rightHanded
/// as the value.

class UsdUIBackdrop : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdUIBackdrop on UsdPrim @p prim.
    /// Equivalent to UsdUIBackdrop::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdUIBackdrop(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdUIBackdrop on the prim held by @p schemaObj .
    /// Should be preferred over UsdUIBackdrop(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdUIBackdrop(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdUIBackdrop()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdUIBackdrop Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DESCRIPTION
    // --------------------------------------------------------------------- //
    /// The text label that is displayed on the backdrop in the node
    /// graph. This help-description explains what the nodes in a backdrop do.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token ui:description` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDescriptionAttr() const;

    /// See GetDescriptionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDescriptionAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdUIBackdrop::_GetStaticTfType()
{
    const static TfToken token("UsdUIBackdrop");
    return token;
}

/* virtual */
inline const TfToken UsdUIBackdrop::_GetTfTypeToken() const
{
    const static TfToken token("UsdUIBackdrop");
    return token;
}

/* static */
inline UsdUIBackdrop UsdUIBackdrop::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdUIBackdrop();
    }
    return UsdUIBackdrop(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdUIBackdrop::GetDescriptionAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiDescription));
}

inline UsdAttribute UsdUIBackdrop::CreateDescriptionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiDescription), SdfValueTypeNames->Token,
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
