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

/// @file usdPhysics/rigidBodyAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdPhysics/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/pxr/base/gf/matrix3f.h"
#include "usdrt/scenegraph/usd/pxr/base/gf/quatf.h" */
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
// PHYSICSRIGIDBODYAPI                                                         //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsRigidBodyAPI
///
/// Applies physics body attributes to any UsdGeomXformable prim and
/// marks that prim to be driven by a simulation. If a simulation is running
/// it will update this prim's pose. All prims in the hierarchy below this
/// prim should move accordingly.

class UsdPhysicsRigidBodyAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdPhysicsRigidBodyAPI on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsRigidBodyAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsRigidBodyAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdPhysicsRigidBodyAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsRigidBodyAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsRigidBodyAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsRigidBodyAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysicsRigidBodyAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdPhysicsRigidBodyAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsRigidBodyAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsRigidBodyAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdPhysicsRigidBodyAPI>())
        {
            return UsdPhysicsRigidBodyAPI(prim);
        }
        return UsdPhysicsRigidBodyAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RIGIDBODYENABLED
    // --------------------------------------------------------------------- //
    /// Determines if this PhysicsRigidBodyAPI is enabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physics:rigidBodyEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetRigidBodyEnabledAttr() const;

    /// See GetRigidBodyEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRigidBodyEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // KINEMATICENABLED
    // --------------------------------------------------------------------- //
    /// Determines whether the body is kinematic or not. A kinematic
    /// body is a body that is moved through animated poses or through
    /// user defined poses. The simulation derives velocities for the
    /// kinematic body based on the external motion. When a continuous motion
    /// is not desired, this kinematic flag should be set to false.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physics:kinematicEnabled = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetKinematicEnabledAttr() const;

    /// See GetKinematicEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateKinematicEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STARTSASLEEP
    // --------------------------------------------------------------------- //
    /// Determines if the body is asleep when the simulation starts.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool physics:startsAsleep = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetStartsAsleepAttr() const;

    /// See GetStartsAsleepAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStartsAsleepAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELOCITY
    // --------------------------------------------------------------------- //
    /// Linear velocity in the same space as the node's xform.
    /// Units: distance/second.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physics:velocity = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetVelocityAttr() const;

    /// See GetVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ANGULARVELOCITY
    // --------------------------------------------------------------------- //
    /// Angular velocity in the same space as the node's xform.
    /// Units: degrees/second.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physics:angularVelocity = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetAngularVelocityAttr() const;

    /// See GetAngularVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAngularVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SIMULATIONOWNER
    // --------------------------------------------------------------------- //
    /// Single PhysicsScene that will simulate this body. By
    /// default this is the first PhysicsScene found in the stage using
    /// UsdStage::Traverse().
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

inline const TfToken UsdPhysicsRigidBodyAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsRigidBodyAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsRigidBodyAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsRigidBodyAPI");
    return token;
}


inline UsdAttribute UsdPhysicsRigidBodyAPI::GetRigidBodyEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsRigidBodyEnabled));
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::CreateRigidBodyEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsRigidBodyEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::GetKinematicEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsKinematicEnabled));
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::CreateKinematicEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsKinematicEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::GetStartsAsleepAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsStartsAsleep));
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::CreateStartsAsleepAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsStartsAsleep), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::GetVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsVelocity));
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::CreateVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsVelocity), SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::GetAngularVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsAngularVelocity));
}

inline UsdAttribute UsdPhysicsRigidBodyAPI::CreateAngularVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsAngularVelocity), SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}


inline UsdRelationship UsdPhysicsRigidBodyAPI::GetSimulationOwnerRel() const
{
    return GetPrim().GetRelationship(UsdPhysicsTokens->physicsSimulationOwner);
}

inline UsdRelationship UsdPhysicsRigidBodyAPI::CreateSimulationOwnerRel() const
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
