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

/// @file physxSchema/physxMeshMergeCollisionAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/ usd/collectionAPI.h" */
// clang-format on

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
// PHYSXMESHMERGECOLLISIONAPI                                                  //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxMeshMergeCollisionAPI
///
/// PhysxMeshMergeCollisionAPI enables implicit mesh merging of given meshes with respect to physics collision geometry
/// representation. It is expected that this API extends the UsdPhysics.CollisionAPI definition, the
/// UsdPhysics.CollisionAPI is still required to be present together with this API to define the collision properties.
/// All meshes that belong to the prim (with this API) subtree will be merged into one mesh that will
/// be used for collision representation. Additionally all meshes that belong to the
/// collisionmeshes collection will be merged too. Note that the collection can also define what meshes should be
/// excluded from the selection.
///
/// This means that for example all meshes that belong to the hierarchy will be represented
/// as one convexHull rather than dozens of convexHulls per mesh.
///
///
/// Note that any changes to the meshes during runtime will get ignored.
///

class PhysxSchemaPhysxMeshMergeCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxMeshMergeCollisionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxMeshMergeCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxMeshMergeCollisionAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxMeshMergeCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxMeshMergeCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxMeshMergeCollisionAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxMeshMergeCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxMeshMergeCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxMeshMergeCollisionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxMeshMergeCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxMeshMergeCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxMeshMergeCollisionAPI>())
        {
            return PhysxSchemaPhysxMeshMergeCollisionAPI(prim);
        }
        return PhysxSchemaPhysxMeshMergeCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxMeshMergeCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxMeshMergeCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxMeshMergeCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxMeshMergeCollisionAPI");
    return token;
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
