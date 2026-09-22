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

/// @file usdPhysics/collisionAPI.h

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
// PHYSICSCOLLISIONAPI                                                         //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsCollisionAPI
///
/// Applies collision attributes to a UsdGeomXformable prim. If a
/// simulation is running, this geometry will collide with other geometries that
/// have PhysicsCollisionAPI applied. If a prim in the parent hierarchy has the
/// RigidBodyAPI applied, this collider is a part of that body. If there is
/// no body in the parent hierarchy, this collider is considered to be static.

class UsdPhysicsCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdPhysicsCollisionAPI on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdPhysicsCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsCollisionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysicsCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdPhysicsCollisionAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdPhysicsCollisionAPI>())
        {
            return UsdPhysicsCollisionAPI(prim);
        }
        return UsdPhysicsCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONENABLED
    // --------------------------------------------------------------------- //
    /// Determines if the PhysicsCollisionAPI is enabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physics:collisionEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetCollisionEnabledAttr() const;

    /// See GetCollisionEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONOWNER
    // --------------------------------------------------------------------- //
    /// Single PhysicsScene that will simulate this collider.
    /// By default this object belongs to the first PhysicsScene.
    /// Note that if a RigidBodyAPI in the hierarchy above has a different
    /// simulationOwner then it has a precedence over this relationship.
    ///
    UsdRelationship GetSimulationOwnerRel() const;

    /// See GetSimulationOwnerRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateSimulationOwnerRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsCollisionAPI");
    return token;
}


inline UsdAttribute UsdPhysicsCollisionAPI::GetCollisionEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsCollisionEnabled));
}

inline UsdAttribute UsdPhysicsCollisionAPI::CreateCollisionEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsCollisionEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship UsdPhysicsCollisionAPI::GetSimulationOwnerRel() const
{
    return GetPrim().GetRelationship(UsdPhysicsTokens->physicsSimulationOwner);
}

inline UsdRelationship UsdPhysicsCollisionAPI::CreateSimulationOwnerRel() const
{
    return GetPrim().CreateRelationship(UsdPhysicsTokens->physicsSimulationOwner,
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
