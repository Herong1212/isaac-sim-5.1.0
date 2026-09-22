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

/// @file physxSchema/physxRigidBodyAPI.h

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
// PHYSXRIGIDBODYAPI                                                           //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxRigidBodyAPI
///
/// PhysX rigid body extended parameters

class PhysxSchemaPhysxRigidBodyAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxRigidBodyAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxRigidBodyAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxRigidBodyAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxRigidBodyAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxRigidBodyAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxRigidBodyAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxRigidBodyAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxRigidBodyAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxRigidBodyAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxRigidBodyAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxRigidBodyAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxRigidBodyAPI>())
        {
            return PhysxSchemaPhysxRigidBodyAPI(prim);
        }
        return PhysxSchemaPhysxRigidBodyAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // LINEARDAMPING
    // --------------------------------------------------------------------- //
    /// Linear damping coefficient.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:linearDamping = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLinearDampingAttr() const;

    /// See GetLinearDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLinearDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ANGULARDAMPING
    // --------------------------------------------------------------------- //
    /// Angular damping coefficient.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:angularDamping = 0.05` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetAngularDampingAttr() const;

    /// See GetAngularDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAngularDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXLINEARVELOCITY
    // --------------------------------------------------------------------- //
    /// Maximum allowable linear velocity for the rigid body.
    /// Range: [0, inf)
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:maxLinearVelocity = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxLinearVelocityAttr() const;

    /// See GetMaxLinearVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxLinearVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXANGULARVELOCITY
    // --------------------------------------------------------------------- //
    /// Maximum allowable angular velocity for rigid body.
    /// Range: [0, inf)
    /// Units: degrees / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:maxAngularVelocity = 5729.58` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxAngularVelocityAttr() const;

    /// See GetMaxAngularVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxAngularVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SLEEPTHRESHOLD
    // --------------------------------------------------------------------- //
    /// Mass-normalized kinetic energy threshold below which an actor may go to sleep.
    /// Range: [0, inf)
    /// Default: 0.00005 * tolerancesSpeed * tolerancesSpeed
    /// Units: distance * distance / seconds / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:sleepThreshold = 0.00005` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSleepThresholdAttr() const;

    /// See GetSleepThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSleepThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STABILIZATIONTHRESHOLD
    // --------------------------------------------------------------------- //
    /// Mass-normalized kinetic energy threshold below which an actor may participate in stabilization.
    /// Range: [0, inf)
    /// Default: 0.00001 * tolerancesSpeed * tolerancesSpeed
    /// Units: distance * distance / seconds / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:stabilizationThreshold = 0.00001` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStabilizationThresholdAttr() const;

    /// See GetStabilizationThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStabilizationThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXDEPENETRATIONVELOCITY
    // --------------------------------------------------------------------- //
    /// The maximum depenetration velocity permitted to be introduced by the solver.
    /// Range: [0, inf)
    /// Default: 5.0 * tolerancesLength
    /// Units: distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:maxDepenetrationVelocity = 3` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxDepenetrationVelocityAttr() const;

    /// See GetMaxDepenetrationVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxDepenetrationVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXCONTACTIMPULSE
    // --------------------------------------------------------------------- //
    /// Sets a limit on the impulse that may be applied at a contact. The maximum impulse at a contact between two
    /// dynamic or kinematic bodies will be the minimum of the two limit values. For a collision between a static and a
    /// dynamic body, the impulse is limited by the value for the dynamic body. Range: [0, inf) Units: force * seconds =
    /// mass * distance / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:maxContactImpulse = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxContactImpulseAttr() const;

    /// See GetMaxContactImpulseAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxContactImpulseAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLVERPOSITIONITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Solver position iteration counts for the body. Allowed range [1, 255].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxRigidBody:solverPositionIterationCount = 16` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetSolverPositionIterationCountAttr() const;

    /// See GetSolverPositionIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolverPositionIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOLVERVELOCITYITERATIONCOUNT
    // --------------------------------------------------------------------- //
    /// Solver velocity iteration counts for the body. Allowed range [0, 255].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxRigidBody:solverVelocityIterationCount = 1` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetSolverVelocityIterationCountAttr() const;

    /// See GetSolverVelocityIterationCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolverVelocityIterationCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLECCD
    // --------------------------------------------------------------------- //
    /// Enables swept integration for the actor.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxRigidBody:enableCCD = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableCCDAttr() const;

    /// See GetEnableCCDAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableCCDAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLESPECULATIVECCD
    // --------------------------------------------------------------------- //
    /// Register a rigid body to dynamically adjust contact offset based on velocity. This can be used to achieve a CCD
    /// effect.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxRigidBody:enableSpeculativeCCD = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableSpeculativeCCDAttr() const;

    /// See GetEnableSpeculativeCCDAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableSpeculativeCCDAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RETAINACCELERATIONS
    // --------------------------------------------------------------------- //
    /// Carries over forces/accelerations between frames, rather than clearing them.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxRigidBody:retainAccelerations = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetRetainAccelerationsAttr() const;

    /// See GetRetainAccelerationsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRetainAccelerationsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLEGYROSCOPICFORCES
    // --------------------------------------------------------------------- //
    /// Enables computation of gyroscopic forces on the rigid body.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxRigidBody:enableGyroscopicForces = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableGyroscopicForcesAttr() const;

    /// See GetEnableGyroscopicForcesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableGyroscopicForcesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DISABLEGRAVITY
    // --------------------------------------------------------------------- //
    /// Disable gravity for the actor.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxRigidBody:disableGravity = 0` |
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
    // SOLVECONTACT
    // --------------------------------------------------------------------- //
    /// Process the contacts of this rigid body in the dynamics solver.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxRigidBody:solveContact = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetSolveContactAttr() const;

    /// See GetSolveContactAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSolveContactAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCKEDPOSAXIS
    // --------------------------------------------------------------------- //
    /// Collection of flags providing a mechanism to lock motion along/around a specific axis (1 << 0, 1 << 1, 1 << 2).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxRigidBody:lockedPosAxis = 0` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetLockedPosAxisAttr() const;

    /// See GetLockedPosAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLockedPosAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCKEDROTAXIS
    // --------------------------------------------------------------------- //
    /// Collection of flags providing a mechanism to lock motion along/around a specific axis (1 << 0, 1 << 1, 1 << 2).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxRigidBody:lockedRotAxis = 0` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetLockedRotAxisAttr() const;

    /// See GetLockedRotAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLockedRotAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONTACTSLOPCOEFFICIENT
    // --------------------------------------------------------------------- //
    /// Tolerance on the angular influence of a contact that can help improve the behavior of rolling approximate
    /// collision shapes. Specifically, the angular component of a normal constraint in a contact is zeroed if
    /// normal.cross(offset) falls below this tolerance. The tolerance is scaled such that the behavior improvement
    /// persists through a range of angular velocities of a rolling shape. Range: [0, inf) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:contactSlopCoefficient = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetContactSlopCoefficientAttr() const;

    /// See GetContactSlopCoefficientAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateContactSlopCoefficientAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CFMSCALE
    // --------------------------------------------------------------------- //
    /// The cfm scale term can help stabilize an articulation by weakening the constraint's response.
    /// Use small values close to the default and typically in the range [0, 0.1] for best results.
    /// Note that this parameter is currently used only if rigid body is part of an articulation.
    /// Range: [0, 1]
    /// Units: unitless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxRigidBody:cfmScale = 0.025` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCfmScaleAttr() const;

    /// See GetCfmScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCfmScaleAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxRigidBodyAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxRigidBodyAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxRigidBodyAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxRigidBodyAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetLinearDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyLinearDamping));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateLinearDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyLinearDamping), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetAngularDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyAngularDamping));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateAngularDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyAngularDamping), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetMaxLinearVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxLinearVelocity));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateMaxLinearVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxLinearVelocity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetMaxAngularVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxAngularVelocity));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateMaxAngularVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxAngularVelocity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetSleepThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySleepThreshold));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateSleepThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySleepThreshold), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetStabilizationThresholdAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyStabilizationThreshold));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateStabilizationThresholdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyStabilizationThreshold),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetMaxDepenetrationVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxDepenetrationVelocity));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateMaxDepenetrationVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxDepenetrationVelocity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetMaxContactImpulseAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxContactImpulse));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateMaxContactImpulseAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyMaxContactImpulse),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetSolverPositionIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySolverPositionIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateSolverPositionIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySolverPositionIterationCount),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetSolverVelocityIterationCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySolverVelocityIterationCount));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateSolverVelocityIterationCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySolverVelocityIterationCount),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetEnableCCDAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyEnableCCD));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateEnableCCDAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyEnableCCD), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetEnableSpeculativeCCDAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyEnableSpeculativeCCD));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateEnableSpeculativeCCDAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyEnableSpeculativeCCD),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetRetainAccelerationsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyRetainAccelerations));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateRetainAccelerationsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyRetainAccelerations),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetEnableGyroscopicForcesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyEnableGyroscopicForces));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateEnableGyroscopicForcesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyEnableGyroscopicForces),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetDisableGravityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyDisableGravity));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateDisableGravityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyDisableGravity), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetSolveContactAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySolveContact));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateSolveContactAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodySolveContact), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetLockedPosAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyLockedPosAxis));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateLockedPosAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyLockedPosAxis), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetLockedRotAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyLockedRotAxis));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateLockedRotAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyLockedRotAxis), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetContactSlopCoefficientAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyContactSlopCoefficient));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateContactSlopCoefficientAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyContactSlopCoefficient),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::GetCfmScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyCfmScale));
}

inline UsdAttribute PhysxSchemaPhysxRigidBodyAPI::CreateCfmScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxRigidBodyCfmScale), SdfValueTypeNames->Float,
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
