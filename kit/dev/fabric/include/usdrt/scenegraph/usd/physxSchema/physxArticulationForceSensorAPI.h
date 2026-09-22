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

/// @file physxSchema/physxArticulationForceSensorAPI.h

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
// PHYSXARTICULATIONFORCESENSORAPI                                             //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxArticulationForceSensorAPI
///
/// WARNING: THIS API IS DEPRECATED AND WILL BE REMOVED IN A FUTURE RELEASE.
/// PhysX articulation sensor to measure spatial force.
/// Articulation sensor API must be applied to a UsdGeom.Xformable in order to get
/// a transformation information. The UsdGeom.Xformable must be created under the
/// articulated rigid body in order to compute a relative transformation between the
/// body and the sensor.

class PhysxSchemaPhysxArticulationForceSensorAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxArticulationForceSensorAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxArticulationForceSensorAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxArticulationForceSensorAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxArticulationForceSensorAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxArticulationForceSensorAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxArticulationForceSensorAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxArticulationForceSensorAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxArticulationForceSensorAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxArticulationForceSensorAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxArticulationForceSensorAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxArticulationForceSensorAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxArticulationForceSensorAPI>())
        {
            return PhysxSchemaPhysxArticulationForceSensorAPI(prim);
        }
        return PhysxSchemaPhysxArticulationForceSensorAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FORCE
    // --------------------------------------------------------------------- //
    /// Spatial force in the local frame of the sensor computed by the simulation.
    /// Units: force
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxArticulationForceSensor:force = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetForceAttr() const;

    /// See GetForceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateForceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TORQUE
    // --------------------------------------------------------------------- //
    /// Spatial torque in the local frame of the sensor computed by the simulation.
    /// Units: torque
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxArticulationForceSensor:torque = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetTorqueAttr() const;

    /// See GetTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTorqueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SENSORENABLED
    // --------------------------------------------------------------------- //
    /// Boolean defining whether sensor is enabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxArticulationForceSensor:sensorEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSensorEnabledAttr() const;

    /// See GetSensorEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSensorEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WORLDFRAMEENABLED
    // --------------------------------------------------------------------- //
    /// Boolean defining whether reported force is in world frame.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxArticulationForceSensor:worldFrameEnabled = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetWorldFrameEnabledAttr() const;

    /// See GetWorldFrameEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWorldFrameEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FORWARDDYNAMICSFORCESENABLED
    // --------------------------------------------------------------------- //
    /// Boolean defining whether to receive forces from forward dynamics.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxArticulationForceSensor:forwardDynamicsForcesEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetForwardDynamicsForcesEnabledAttr() const;

    /// See GetForwardDynamicsForcesEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateForwardDynamicsForcesEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONSTRAINTSOLVERFORCESENABLED
    // --------------------------------------------------------------------- //
    /// Boolean defining whether to receive forces from constraint solver.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxArticulationForceSensor:constraintSolverForcesEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetConstraintSolverForcesEnabledAttr() const;

    /// See GetConstraintSolverForcesEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateConstraintSolverForcesEnabledAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxArticulationForceSensorAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxArticulationForceSensorAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxArticulationForceSensorAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxArticulationForceSensorAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::GetForceAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorForce));
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::CreateForceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorForce),
                                     SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::GetTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorTorque));
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::CreateTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorTorque),
                                     SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::GetSensorEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorSensorEnabled));
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::CreateSensorEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorSensorEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::GetWorldFrameEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorWorldFrameEnabled));
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::CreateWorldFrameEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorWorldFrameEnabled),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::GetForwardDynamicsForcesEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorForwardDynamicsForcesEnabled));
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::CreateForwardDynamicsForcesEnabledAttr() const
{
    return GetPrim().CreateAttribute(
        TfToken(PhysxSchemaTokens->physxArticulationForceSensorForwardDynamicsForcesEnabled), SdfValueTypeNames->Bool,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::GetConstraintSolverForcesEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxArticulationForceSensorConstraintSolverForcesEnabled));
}

inline UsdAttribute PhysxSchemaPhysxArticulationForceSensorAPI::CreateConstraintSolverForcesEnabledAttr() const
{
    return GetPrim().CreateAttribute(
        TfToken(PhysxSchemaTokens->physxArticulationForceSensorConstraintSolverForcesEnabled), SdfValueTypeNames->Bool,
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
