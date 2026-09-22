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

/// @file physxSchema/physxDeformableBodyAPI.h

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
// PHYSXDEFORMABLEBODYAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxDeformableBodyAPI
///
/// Applied to a UsdGeomMesh that is to be driven by a deformable body simulation.
/// See PhysxDeformableAPI for information on how to define the deformable body's material properties.

class PhysxSchemaPhysxDeformableBodyAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxDeformableBodyAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxDeformableBodyAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxDeformableBodyAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxDeformableBodyAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxDeformableBodyAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxDeformableBodyAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxDeformableBodyAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxDeformableBodyAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxDeformableBodyAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxDeformableBodyAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxDeformableBodyAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxDeformableBodyAPI>())
        {
            return PhysxSchemaPhysxDeformableBodyAPI(prim);
        }
        return PhysxSchemaPhysxDeformableBodyAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DISABLEGRAVITY
    // --------------------------------------------------------------------- //
    /// Disable gravity for the actor.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxDeformable:disableGravity = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetDisableGravityAttr() const;

    /// See GetDisableGravityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisableGravityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONINDICES
    // --------------------------------------------------------------------- //
    /// Mesh indices that define the collision tetrahedral mesh together with the collisionPoints attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int[] physxDeformable:collisionIndices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetCollisionIndicesAttr() const;

    /// See GetCollisionIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONPOINTS
    // --------------------------------------------------------------------- //
    /// Mesh points in local coordinates that define the collision tetrahedral mesh together with the collisionIndices
    /// attribute. This attribute is read-only and may be updated from simulation data to reflect the current simulation
    /// state.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxDeformable:collisionPoints` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetCollisionPointsAttr() const;

    /// See GetCollisionPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionPointsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONRESTPOINTS
    // --------------------------------------------------------------------- //
    /// Mesh rest points in local coordinates that define the rest pose of the collision tetrahedral mesh together with
    /// the collisionIndices attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxDeformable:collisionRestPoints` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetCollisionRestPointsAttr() const;

    /// See GetCollisionRestPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionRestPointsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONPOINTS
    // --------------------------------------------------------------------- //
    /// Simulation mesh points in local coordinates that define the simulation tetrahedral mesh together with the
    /// simulationIndices attribute. This attribute may be updated from simulation data to reflect the current
    /// simulation state.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxDeformable:simulationPoints` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetSimulationPointsAttr() const;

    /// See GetSimulationPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSimulationPointsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONRESTPOINTS
    // --------------------------------------------------------------------- //
    /// Mesh rest points in local coordinates that define the rest pose of the simulation tetrahedral mesh together with
    /// the simulationIndices attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physxDeformable:simulationRestPoints` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetSimulationRestPointsAttr() const;

    /// See GetSimulationRestPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSimulationRestPointsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxDeformableBodyAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxDeformableBodyAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxDeformableBodyAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxDeformableBodyAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::GetDisableGravityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableDisableGravity));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::CreateDisableGravityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableDisableGravity), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::GetCollisionIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableCollisionIndices));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::CreateCollisionIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableCollisionIndices),
                                     SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::GetCollisionPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableCollisionPoints));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::CreateCollisionPointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableCollisionPoints),
                                     SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::GetCollisionRestPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableCollisionRestPoints));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::CreateCollisionRestPointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableCollisionRestPoints),
                                     SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::GetSimulationPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationPoints));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::CreateSimulationPointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationPoints),
                                     SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::GetSimulationRestPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationRestPoints));
}

inline UsdAttribute PhysxSchemaPhysxDeformableBodyAPI::CreateSimulationRestPointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxDeformableSimulationRestPoints),
                                     SdfValueTypeNames->Point3fArray,
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
