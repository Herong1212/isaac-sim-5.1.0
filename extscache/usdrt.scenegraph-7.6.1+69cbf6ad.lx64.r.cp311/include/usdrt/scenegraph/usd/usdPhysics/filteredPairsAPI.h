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

/// @file usdPhysics/filteredPairsAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdPhysics/tokens.h"


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
// PHYSICSFILTEREDPAIRSAPI                                                     //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsFilteredPairsAPI
///
/// API to describe fine-grained filtering. If a collision between
/// two objects occurs, this pair might be filtered if the pair is defined
/// through this API. This API can be applied either to a body or collision
/// or even articulation. The "filteredPairs" defines what objects it should
/// not collide against. Note that FilteredPairsAPI filtering has precedence
/// over CollisionGroup filtering.

class UsdPhysicsFilteredPairsAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdPhysicsFilteredPairsAPI on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsFilteredPairsAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsFilteredPairsAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdPhysicsFilteredPairsAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsFilteredPairsAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsFilteredPairsAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsFilteredPairsAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysicsFilteredPairsAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdPhysicsFilteredPairsAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsFilteredPairsAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsFilteredPairsAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdPhysicsFilteredPairsAPI>())
        {
            return UsdPhysicsFilteredPairsAPI(prim);
        }
        return UsdPhysicsFilteredPairsAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FILTEREDPAIRS
    // --------------------------------------------------------------------- //
    /// Relationship to objects that should be filtered.
    ///
    UsdRelationship GetFilteredPairsRel() const;

    /// See GetFilteredPairsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateFilteredPairsRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsFilteredPairsAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsFilteredPairsAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsFilteredPairsAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsFilteredPairsAPI");
    return token;
}


inline UsdRelationship UsdPhysicsFilteredPairsAPI::GetFilteredPairsRel() const
{
    return GetPrim().GetRelationship(UsdPhysicsTokens->physicsFilteredPairs);
}

inline UsdRelationship UsdPhysicsFilteredPairsAPI::CreateFilteredPairsRel() const
{
    return GetPrim().CreateRelationship(UsdPhysicsTokens->physicsFilteredPairs,
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
