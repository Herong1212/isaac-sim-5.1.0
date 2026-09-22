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

/// @file physxSchema/physxTriangleMeshSimplificationCollisionAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/physxSchema/tokens.h"


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
// PHYSXTRIANGLEMESHSIMPLIFICATIONCOLLISIONAPI                                 //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI
///
/// PhysX triangle mesh simplification extended parameters

class PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI(const UsdPrim& prim = UsdPrim())
        : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI(const UsdSchemaBase& schemaObj)
        : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxTriangleMeshSimplificationCollisionAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI>())
        {
            return PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI(prim);
        }
        return PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SIMPLIFICATIONMETRIC
    // --------------------------------------------------------------------- //
    /// Mesh simplification accuracy.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxTriangleMeshSimplificationCollision:metric = 0.55` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSimplificationMetricAttr() const;

    /// See GetSimplificationMetricAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSimplificationMetricAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WELDTOLERANCE
    // --------------------------------------------------------------------- //
    /// Mesh weld tolerance, controls the distance at which vertices are welded.
    /// Default -inf will autocompute the welding tolerance based on the mesh size. Zero value will disable welding.
    /// Range: [0, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxTriangleMeshSimplificationCollision:weldTolerance = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetWeldToleranceAttr() const;

    /// See GetWeldToleranceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWeldToleranceAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI::GetSimplificationMetricAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxTriangleMeshSimplificationCollisionMetric));
}

inline UsdAttribute PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI::CreateSimplificationMetricAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxTriangleMeshSimplificationCollisionMetric),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI::GetWeldToleranceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxTriangleMeshSimplificationCollisionWeldTolerance));
}

inline UsdAttribute PhysxSchemaPhysxTriangleMeshSimplificationCollisionAPI::CreateWeldToleranceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxTriangleMeshSimplificationCollisionWeldTolerance),
                                     SdfValueTypeNames->Float,
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
