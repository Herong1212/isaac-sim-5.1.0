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

/// @file usdUI/sceneGraphPrimAPI.h

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
// SCENEGRAPHPRIMAPI                                                           //
// -------------------------------------------------------------------------- //

/// @class UsdUISceneGraphPrimAPI
///
/// /// Utility schema for display properties of a prim
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdUITokens.
/// So to set an attribute to the value "rightHanded", use UsdUITokens->rightHanded
/// as the value.

class UsdUISceneGraphPrimAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdUISceneGraphPrimAPI on UsdPrim @p prim.
    /// Equivalent to UsdUISceneGraphPrimAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdUISceneGraphPrimAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdUISceneGraphPrimAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdUISceneGraphPrimAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdUISceneGraphPrimAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdUISceneGraphPrimAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "SceneGraphPrimAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdUISceneGraphPrimAPI object is returned upon success.
    /// An invalid (or empty) UsdUISceneGraphPrimAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdUISceneGraphPrimAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdUISceneGraphPrimAPI>())
        {
            return UsdUISceneGraphPrimAPI(prim);
        }
        return UsdUISceneGraphPrimAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DISPLAYNAME
    // --------------------------------------------------------------------- //
    /// When publishing a nodegraph or a material, it can be useful to
    /// provide an optional display name, for readability.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token ui:displayName` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDisplayNameAttr() const;

    /// See GetDisplayNameAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisplayNameAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DISPLAYGROUP
    // --------------------------------------------------------------------- //
    /// When publishing a nodegraph or a material, it can be useful to
    /// provide an optional display group, for organizational purposes and
    /// readability. This is because often the usd shading hierarchy is rather
    /// flat while we want to display it in organized groups.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token ui:displayGroup` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDisplayGroupAttr() const;

    /// See GetDisplayGroupAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisplayGroupAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdUISceneGraphPrimAPI::_GetStaticTfType()
{
    const static TfToken token("UsdUISceneGraphPrimAPI");
    return token;
}

/* virtual */
inline const TfToken UsdUISceneGraphPrimAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdUISceneGraphPrimAPI");
    return token;
}


inline UsdAttribute UsdUISceneGraphPrimAPI::GetDisplayNameAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiDisplayName));
}

inline UsdAttribute UsdUISceneGraphPrimAPI::CreateDisplayNameAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiDisplayName), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdUISceneGraphPrimAPI::GetDisplayGroupAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdUITokens->uiDisplayGroup));
}

inline UsdAttribute UsdUISceneGraphPrimAPI::CreateDisplayGroupAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdUITokens->uiDisplayGroup), SdfValueTypeNames->Token,
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
