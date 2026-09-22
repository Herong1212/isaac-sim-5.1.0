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

/// @file physxSchema/physxVehicleAPI.h

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
// PHYSXVEHICLEAPI                                                             //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleAPI
///
/// PhysX vehicle. Has to be applied to a prim with PhysicsRigidBodyAPI applied. Wheels can be added by applying
/// PhysxVehicleWheelAttachmentAPI to a prim that is a descendant of the "vehicle" prim.
///
/// Note: if the prim has PhysxRigidBodyAPI applied, it should be configured such that disableGravity is set to true
/// since the vehicle simulation will take gravity into account already. For any described attribute @em Fallback @em
/// Value or @em Allowed @em Values below that are text/tokens, the actual token is published and defined in @ref
/// PhysxSchemaTokens. So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded as the
/// value.

class PhysxSchemaPhysxVehicleAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleAPI>())
        {
            return PhysxSchemaPhysxVehicleAPI(prim);
        }
        return PhysxSchemaPhysxVehicleAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // VEHICLEENABLED
    // --------------------------------------------------------------------- //
    /// Defines whether the vehicle simulation update loop will run for the vehicle or not.
    ///
    /// Note: if set to false, the prim's rigid body will still get simulated (the PhysicsRigidBodyAPI API schema
    /// can be used to turn the body into a kinematic or set velocities to zero at that point).
    ///
    /// Note: it is an illegal setup to have a vehicle enabled, while the prim's rigid body is disabled or kinematic.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxVehicle:vehicleEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetVehicleEnabledAttr() const;

    /// See GetVehicleEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVehicleEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUSPENSIONLINEQUERYTYPE
    // --------------------------------------------------------------------- //
    /// Collision of the wheels with the ground surface is detected through scene queries along the suspension
    /// direction. This attribute defines whether a raycast or a sweep should be used as the query type. Raycasts are
    /// faster while sweeps can represent the wheel shape better and thus react earlier to ground surface changes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physxVehicle:suspensionLineQueryType = "raycast"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | raycast, sweep |

    UsdAttribute GetSuspensionLineQueryTypeAttr() const;

    /// See GetSuspensionLineQueryTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSuspensionLineQueryTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LIMITSUSPENSIONEXPANSIONVELOCITY
    // --------------------------------------------------------------------- //
    /// Limit the suspension expansion dynamics.
    ///
    /// When a hit with the ground is detected, the suspension jounce will be set such that the wheel
    /// is placed on the ground. This can result in large changes to jounce within a single simulation
    /// frame, if the ground surface has high frequency or if the simulation time step is large. As a
    /// result, large damping forces can evolve and cause undesired behavior. If this parameter is set
    /// to true, the suspension expansion speed will be limited to what can be achieved given the time
    /// step, suspension stiffness etc. As a consequence, handling of the vehicle will be affected as
    /// the wheel might loose contact with the ground more easily.
    ///
    /// Note: this will apply to the suspensions of all wheels.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxVehicle:limitSuspensionExpansionVelocity = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetLimitSuspensionExpansionVelocityAttr() const;

    /// See GetLimitSuspensionExpansionVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLimitSuspensionExpansionVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUBSTEPTHRESHOLDLONGITUDINALSPEED
    // --------------------------------------------------------------------- //
    /// Threshold speed that is used to categorize vehicle speed as low speed or high speed for
    /// choosing the sub-step count (units: distance / seconds).
    ///
    /// Note: if not defined, the value 5.0 will be used. This default value is in meter length scale
    /// and will get adjusted if another unit is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:subStepThresholdLongitudinalSpeed` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSubStepThresholdLongitudinalSpeedAttr() const;

    /// See GetSubStepThresholdLongitudinalSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSubStepThresholdLongitudinalSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOWFORWARDSPEEDSUBSTEPCOUNT
    // --------------------------------------------------------------------- //
    /// Number of sub-steps performed in the vehicle dynamics update for vehicles that have
    /// longitudinal speed lower than subStepThresholdLongitudinalSpeed.
    ///
    /// Note: if not defined, the value 3 will be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxVehicle:lowForwardSpeedSubStepCount` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetLowForwardSpeedSubStepCountAttr() const;

    /// See GetLowForwardSpeedSubStepCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLowForwardSpeedSubStepCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HIGHFORWARDSPEEDSUBSTEPCOUNT
    // --------------------------------------------------------------------- //
    /// Number of sub-steps performed in the vehicle dynamics update for vehicles that have
    /// longitudinal speed greater than subStepThresholdLongitudinalSpeed.
    ///
    /// Note: if not defined, the value 1 will be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxVehicle:highForwardSpeedSubStepCount` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetHighForwardSpeedSubStepCountAttr() const;

    /// See GetHighForwardSpeedSubStepCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHighForwardSpeedSubStepCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINLONGITUDINALSLIPDENOMINATOR
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use minPassiveLongitudinalSlipDenominator instead.
    ///
    /// The minimum denominator used in the longitudinal slip calculation (units: distance / seconds).
    /// For low longitudinal velocities, the computation of the longitudinal slip can become
    /// unstable. This value defines the minimum velocity to use when computing the longitudinal slip.
    ///
    /// Note: will be ignored if minPassiveLongitudinalSlipDenominator is used.
    ///
    /// Note: if not defined, the value 4.0 will be used. This default value is in meter length scale
    /// and will get adjusted if another unit is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:minLongitudinalSlipDenominator` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinLongitudinalSlipDenominatorAttr() const;

    /// See GetMinLongitudinalSlipDenominatorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinLongitudinalSlipDenominatorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINPASSIVELONGITUDINALSLIPDENOMINATOR
    // --------------------------------------------------------------------- //
    /// The minimum denominator used in the longitudinal slip calculation when a wheel experiences no
    /// drive and no brake torque (units: distance / seconds). For low longitudinal velocities, the
    /// computation of the longitudinal slip can become unstable. This value defines the minimum velocity
    /// to use when computing the longitudinal slip. The value has to be positive.
    ///
    /// Note: the default value 0 is not a valid value as such but indicates that the deprecated
    /// attribute minLongitudinalSlipDenominator should be used instead.
    ///
    /// Note: it is recommended to have minActiveLongitudinalSlipDenominator < minPassiveLongitudinalSlipDenominator.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:minPassiveLongitudinalSlipDenominator = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinPassiveLongitudinalSlipDenominatorAttr() const;

    /// See GetMinPassiveLongitudinalSlipDenominatorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinPassiveLongitudinalSlipDenominatorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINACTIVELONGITUDINALSLIPDENOMINATOR
    // --------------------------------------------------------------------- //
    /// The minimum denominator used in the longitudinal slip calculation when a wheel experiences
    /// drive or brake torque (units: distance / seconds). For low longitudinal velocities, the
    /// computation of the longitudinal slip can become unstable. This value defines the minimum velocity
    /// to use when computing the longitudinal slip. The value has to be positive.
    ///
    /// Note: the default value 0 is not a valid value as such but will result in the value 0.1 being
    /// used (in meter length scale or the equivalent if another unit is used).
    ///
    /// Note: it is recommended to have minActiveLongitudinalSlipDenominator < minPassiveLongitudinalSlipDenominator.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:minActiveLongitudinalSlipDenominator = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinActiveLongitudinalSlipDenominatorAttr() const;

    /// See GetMinActiveLongitudinalSlipDenominatorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinActiveLongitudinalSlipDenominatorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MINLATERALSLIPDENOMINATOR
    // --------------------------------------------------------------------- //
    /// The minimum denominator used in the lateral slip calculation (units: distance / seconds).
    /// For low longitudinal velocities, the computation of the lateral slip can become unstable.
    /// This value defines the minimum longitudinal velocity to use when computing the lateral slip.
    /// The value has to be positive.
    ///
    /// Note: the default value 0 is not a valid value as such but will result in the value 1.0 being
    /// used (in meter length scale or the equivalent if another unit is used).
    ///
    /// Note: larger simulation timesteps typically require larger values of minLateralSlipDenominator.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:minLateralSlipDenominator = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinLateralSlipDenominatorAttr() const;

    /// See GetMinLateralSlipDenominatorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinLateralSlipDenominatorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LONGITUDINALSTICKYTIRETHRESHOLDSPEED
    // --------------------------------------------------------------------- //
    /// The longitudinal sticky tire threshold speed (units: distance / seconds). Has to be greater
    /// or equal 0. A tire enters the "sticky tire" regime when its longitudinal speed has been below
    /// this threshold for a continuous time specified by longitudinalStickyTireThresholdTime. At low
    /// speeds with no significant brake or drive torque, numerical error begins to dominate and it
    /// can be difficult to bring the vehicle to rest. A solution to this problem is to recognise that
    /// the vehicle is close to rest and to replace the tire forces with velocity constraints that will
    /// bring the vehicle to rest. For the purpose of this documentation, this regime is referred to as
    /// the "sticky tire" regime.
    ///
    /// Note: the default value -1 is not a valid value as such but will result in the value 0.2 being
    /// used (in meter length scale or the equivalent if another unit is used).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:longitudinalStickyTireThresholdSpeed = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLongitudinalStickyTireThresholdSpeedAttr() const;

    /// See GetLongitudinalStickyTireThresholdSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLongitudinalStickyTireThresholdSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LONGITUDINALSTICKYTIRETHRESHOLDTIME
    // --------------------------------------------------------------------- //
    /// The longitudinal sticky tire threshold time (in seconds). Has to be greater or equal 0.
    /// A tire enters the "sticky tire" regime when it has been below the speed specified by
    /// longitudinalStickyTireThresholdSpeed for this continuous time. More details on the
    /// "sticky tire" regime can be found in the documentation of the longitudinalStickyTireThresholdSpeed
    /// attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:longitudinalStickyTireThresholdTime = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLongitudinalStickyTireThresholdTimeAttr() const;

    /// See GetLongitudinalStickyTireThresholdTimeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLongitudinalStickyTireThresholdTimeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LONGITUDINALSTICKYTIREDAMPING
    // --------------------------------------------------------------------- //
    /// The longitudinal sticky tire damping (per seconds). Has to be greater or equal 0.
    /// Describes the rate at which the velocity constraint approaches zero when entering the "sticky tire"
    /// regime. More details on the "sticky tire" regime can be found in the documentation of the
    /// longitudinalStickyTireThresholdSpeed attribute.
    ///
    /// Note: larger values of damping lead to faster approaches to zero. Since the damping behaves
    /// like a stiffness with respect to the velocity, too large a value can lead to instabilities.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:longitudinalStickyTireDamping = 200` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLongitudinalStickyTireDampingAttr() const;

    /// See GetLongitudinalStickyTireDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLongitudinalStickyTireDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LATERALSTICKYTIRETHRESHOLDSPEED
    // --------------------------------------------------------------------- //
    /// The lateral sticky tire threshold speed (units: distance / seconds). See documentation about
    /// longitudinalStickyTireThresholdSpeed as it is the same concept. Note that the lateral part
    /// can only enter the "sticky tire" regime if the longitudinal speed is below longitudinalStickyTireThresholdSpeed.
    ///
    /// Note: the default value -1 is not a valid value as such but will result in the value 0.2 being
    /// used (in meter length scale or the equivalent if another unit is used).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:lateralStickyTireThresholdSpeed = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLateralStickyTireThresholdSpeedAttr() const;

    /// See GetLateralStickyTireThresholdSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLateralStickyTireThresholdSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LATERALSTICKYTIRETHRESHOLDTIME
    // --------------------------------------------------------------------- //
    /// The lateral sticky tire threshold time (in seconds). See documentation about
    /// longitudinalStickyTireThresholdTime as it is the same concept.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:lateralStickyTireThresholdTime = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLateralStickyTireThresholdTimeAttr() const;

    /// See GetLateralStickyTireThresholdTimeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLateralStickyTireThresholdTimeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LATERALSTICKYTIREDAMPING
    // --------------------------------------------------------------------- //
    /// The lateral sticky tire damping (per seconds). See documentation about
    /// longitudinalStickyTireDamping as it is the same concept.
    ///
    /// Note: larger values of damping lead to faster approaches to zero. Since the damping behaves
    /// like a stiffness with respect to the velocity, too large a value can lead to instabilities.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicle:lateralStickyTireDamping = 20` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLateralStickyTireDampingAttr() const;

    /// See GetLateralStickyTireDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLateralStickyTireDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DRIVE
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleDriveBasicAPI or PhysxVehicleDriveStandardAPI prim that describes the
    /// drive model. If none is specified, it is up to the user to apply torque to the wheels. It is also
    /// possible to apply PhysxVehicleDriveBasicAPI or PhysxVehicleDriveStandardAPI to the prim directly. In
    /// that case the relationship must not be defined.
    ///
    UsdRelationship GetDriveRel() const;

    /// See GetDriveRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateDriveRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetVehicleEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleVehicleEnabled));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateVehicleEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleVehicleEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetSuspensionLineQueryTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionLineQueryType));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateSuspensionLineQueryTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionLineQueryType),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLimitSuspensionExpansionVelocityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLimitSuspensionExpansionVelocity));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLimitSuspensionExpansionVelocityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLimitSuspensionExpansionVelocity),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetSubStepThresholdLongitudinalSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSubStepThresholdLongitudinalSpeed));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateSubStepThresholdLongitudinalSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSubStepThresholdLongitudinalSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLowForwardSpeedSubStepCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLowForwardSpeedSubStepCount));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLowForwardSpeedSubStepCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLowForwardSpeedSubStepCount),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetHighForwardSpeedSubStepCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleHighForwardSpeedSubStepCount));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateHighForwardSpeedSubStepCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleHighForwardSpeedSubStepCount),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetMinLongitudinalSlipDenominatorAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinLongitudinalSlipDenominator));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateMinLongitudinalSlipDenominatorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinLongitudinalSlipDenominator),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetMinPassiveLongitudinalSlipDenominatorAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinPassiveLongitudinalSlipDenominator));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateMinPassiveLongitudinalSlipDenominatorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinPassiveLongitudinalSlipDenominator),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetMinActiveLongitudinalSlipDenominatorAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinActiveLongitudinalSlipDenominator));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateMinActiveLongitudinalSlipDenominatorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinActiveLongitudinalSlipDenominator),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetMinLateralSlipDenominatorAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinLateralSlipDenominator));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateMinLateralSlipDenominatorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleMinLateralSlipDenominator),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLongitudinalStickyTireThresholdSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLongitudinalStickyTireThresholdSpeed));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLongitudinalStickyTireThresholdSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLongitudinalStickyTireThresholdSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLongitudinalStickyTireThresholdTimeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLongitudinalStickyTireThresholdTime));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLongitudinalStickyTireThresholdTimeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLongitudinalStickyTireThresholdTime),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLongitudinalStickyTireDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLongitudinalStickyTireDamping));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLongitudinalStickyTireDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLongitudinalStickyTireDamping),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLateralStickyTireThresholdSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLateralStickyTireThresholdSpeed));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLateralStickyTireThresholdSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLateralStickyTireThresholdSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLateralStickyTireThresholdTimeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLateralStickyTireThresholdTime));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLateralStickyTireThresholdTimeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLateralStickyTireThresholdTime),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::GetLateralStickyTireDampingAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleLateralStickyTireDamping));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAPI::CreateLateralStickyTireDampingAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleLateralStickyTireDamping),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxVehicleAPI::GetDriveRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleDrive);
}

inline UsdRelationship PhysxSchemaPhysxVehicleAPI::CreateDriveRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleDrive,
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
