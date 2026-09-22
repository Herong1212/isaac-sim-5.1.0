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

/// @file usdLux/listAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdLux/tokens.h"


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
// LISTAPI                                                                     //
// -------------------------------------------------------------------------- //

/// @class UsdLuxListAPI
///
/// /// \deprecated
/// Use LightListAPI instead
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxListAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdLuxListAPI on UsdPrim @p prim.
    /// Equivalent to UsdLuxListAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxListAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdLuxListAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxListAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxListAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxListAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "ListAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdLuxListAPI object is returned upon success.
    /// An invalid (or empty) UsdLuxListAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdLuxListAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdLuxListAPI>())
        {
            return UsdLuxListAPI(prim);
        }
        return UsdLuxListAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // LIGHTLISTCACHEBEHAVIOR
    // --------------------------------------------------------------------- //
    /// Controls how the lightList should be interpreted.
    /// Valid values are:
    /// - consumeAndHalt: The lightList should be consulted,
    /// and if it exists, treated as a final authoritative statement
    /// of any lights that exist at or below this prim, halting
    /// recursive discovery of lights.
    /// - consumeAndContinue: The lightList should be consulted,
    /// but recursive traversal over nameChildren should continue
    /// in case additional lights are added by descendants.
    /// - ignore: The lightList should be entirely ignored.  This
    /// provides a simple way to temporarily invalidate an existing
    /// cache.  This is the fallback behavior.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token lightList:cacheBehavior` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdLuxTokens "Allowed Values" | consumeAndHalt, consumeAndContinue, ignore |

    UsdAttribute GetLightListCacheBehaviorAttr() const;

    /// See GetLightListCacheBehaviorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLightListCacheBehaviorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LIGHTLIST
    // --------------------------------------------------------------------- //
    /// Relationship to lights in the scene.
    ///
    UsdRelationship GetLightListRel() const;

    /// See GetLightListRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateLightListRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxListAPI::_GetStaticTfType()
{
    const static TfToken token("UsdLuxListAPI");
    return token;
}

/* virtual */
inline const TfToken UsdLuxListAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxListAPI");
    return token;
}


inline UsdAttribute UsdLuxListAPI::GetLightListCacheBehaviorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightListCacheBehavior));
}

inline UsdAttribute UsdLuxListAPI::CreateLightListCacheBehaviorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightListCacheBehavior), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}


inline UsdRelationship UsdLuxListAPI::GetLightListRel() const
{
    return GetPrim().GetRelationship(UsdLuxTokens->lightList);
}

inline UsdRelationship UsdLuxListAPI::CreateLightListRel() const
{
    return GetPrim().CreateRelationship(UsdLuxTokens->lightList,
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
