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

/// @file usdPhysics/meshCollisionAPI.h

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
// PHYSICSMESHCOLLISIONAPI                                                     //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsMeshCollisionAPI
///
/// Attributes to control how a Mesh is made into a collider.
/// Can be applied to only a USDGeomMesh in addition to its
/// PhysicsCollisionAPI.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdPhysicsTokens.
/// So to set an attribute to the value "rightHanded", use UsdPhysicsTokens->rightHanded
/// as the value.

class UsdPhysicsMeshCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdPhysicsMeshCollisionAPI on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsMeshCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsMeshCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdPhysicsMeshCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsMeshCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsMeshCollisionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsMeshCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysicsMeshCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdPhysicsMeshCollisionAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsMeshCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsMeshCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdPhysicsMeshCollisionAPI>())
        {
            return UsdPhysicsMeshCollisionAPI(prim);
        }
        return UsdPhysicsMeshCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // APPROXIMATION
    // --------------------------------------------------------------------- //
    /// Determines the mesh's collision approximation:
    /// "none" - The mesh geometry is used directly as a collider without any
    /// approximation.
    /// "convexDecomposition" - A convex mesh decomposition is performed. This
    /// results in a set of convex mesh colliders.
    /// "convexHull" - A convex hull of the mesh is generated and used as the
    /// collider.
    /// "boundingSphere" - A bounding sphere is computed around the mesh and used
    /// as a collider.
    /// "boundingCube" - An optimally fitting box collider is computed around the
    /// mesh.
    /// "meshSimplification" - A mesh simplification step is performed, resulting
    /// in a simplified triangle mesh collider.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physics:approximation = "none"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdPhysicsTokens "Allowed Values" | none, convexDecomposition, convexHull, boundingSphere, boundingCube,
    /// meshSimplification |

    UsdAttribute GetApproximationAttr() const;

    /// See GetApproximationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateApproximationAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsMeshCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsMeshCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsMeshCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsMeshCollisionAPI");
    return token;
}


inline UsdAttribute UsdPhysicsMeshCollisionAPI::GetApproximationAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsApproximation));
}

inline UsdAttribute UsdPhysicsMeshCollisionAPI::CreateApproximationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsApproximation), SdfValueTypeNames->Token,
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
