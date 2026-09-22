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

/// @file physxSchema/physxVehicleEngineAPI.h

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
// PHYSXVEHICLEENGINEAPI                                                       //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleEngineAPI
///
/// Properties of a PhysX vehicle engine. If the engine setup does not need to be shared among vehicle
/// instances, it can be applied to the prim which has PhysxVehicleDriveStandardAPI applied.
/// If the intent is to share the engine setup, PhysxVehicleEngineAPI can be applied to a separate
/// prim which can be linked to (see PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleEngineAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleEngineAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleEngineAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleEngineAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleEngineAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleEngineAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleEngineAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleEngineAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleEngineAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleEngineAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleEngineAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleEngineAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleEngineAPI>())
        {
            return PhysxSchemaPhysxVehicleEngineAPI(prim);
        }
        return PhysxSchemaPhysxVehicleEngineAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MOI
    // --------------------------------------------------------------------- //
    /// The moment of inertia of the engine around the axis of rotation (units:
    /// mass * distance * distance). The value has to be positive.
    ///
    /// Note: if not defined, the value 1.0 will be used. This default value is in meter length scale
    /// and kilograms and will get adjusted if other units are used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleEngine:moi` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMoiAttr() const;

    /// See GetMoiAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMoiAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PEAKTORQUE
    // --------------------------------------------------------------------- //
    /// Maximum torque available to apply to the engine when the accelerator pedal is at maximum
    /// (units: mass * distance * distance / seconds / seconds). The value has to be greater or
    /// equal 0.
    ///
    /// Note: the torque available is the value of the accelerator pedal (in range [0, 1]) multiplied
    /// by the normalized torque as computed from torqueCurve (see corresponding attribute)
    /// multiplied by peakTorque.
    ///
    /// Note: the default value -1 is not a valid value as such but will result in the value 500.0
    /// being used (in meter length scale and kilogram mass scale or the equivalent if other units
    /// are used).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleEngine:peakTorque = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPeakTorqueAttr() const;

    /// See GetPeakTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePeakTorqueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXROTATIONSPEED
    // --------------------------------------------------------------------- //
    /// Maximum rotation speed of the engine (units: radians / seconds). The value has to be greater
    /// or equal 0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleEngine:maxRotationSpeed = 600` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxRotationSpeedAttr() const;

    /// See GetMaxRotationSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxRotationSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // IDLEROTATIONSPEED
    // --------------------------------------------------------------------- //
    /// Rotation speed of the engine when idling (units: radians / seconds). The value has to be greater or equal 0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleEngine:idleRotationSpeed = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetIdleRotationSpeedAttr() const;

    /// See GetIdleRotationSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIdleRotationSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TORQUECURVE
    // --------------------------------------------------------------------- //
    /// Graph of normalized torque (torque / peakTorque) against normalized engine speed (engineRotationSpeed /
    /// maxRotationSpeed).
    ///
    /// Note: the normalized engine speed is the x-axis of the graph, while the normalized torque is the y-axis of the
    /// graph. No more than 8 data points are supported.
    ///
    /// Note: if not defined, the following values will be used: [(0.0, 0.8), (0.33, 1.0), (1.0, 0.8)].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2[] physxVehicleEngine:torqueCurve` |
    /// | C++ Type | VtArray<GfVec2f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2Array |

    UsdAttribute GetTorqueCurveAttr() const;

    /// See GetTorqueCurveAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTorqueCurveAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DAMPINGRATEFULLTHROTTLE
    // --------------------------------------------------------------------- //
    /// Damping rate of engine when full throttle is applied (units:
    /// torque * seconds = mass * distance * distance / seconds). The value has to be greater
    /// or equal 0.
    ///
    /// Note: if the clutch is engaged (any gear except neutral) then the damping rate applied
    /// at run-time is an interpolation between dampingRateZeroThrottleClutchEngaged (see
    /// corresponding attribute) and dampingRateFullThrottle:
    /// dampingRateZeroThrottleClutchEngaged +
    /// ((dampingRateFullThrottle-dampingRateZeroThrottleClutchEngaged) * acceleratorPedal).
    ///
    /// Note: if the clutch is disengaged (in neutral gear) the damping rate applied at run-time
    /// is an interpolation between dampingRateZeroThrottleClutchDisengaged (see corresponding
    /// attribute) and dampingRateFullThrottle:
    /// dampingRateZeroThrottleClutchDisengaged +
    /// ((dampingRateFullThrottle-dampingRateZeroThrottleClutchDisengaged) * acceleratorPedal).
    ///
    /// Note: the default value -1 is not a valid value as such but will result in the value 0.15
    /// being used (in meter length scale and kilogram mass scale or the equivalent if other units
    /// are used).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleEngine:dampingRateFullThrottle = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDampingRateFullThrottleAttr() const;

    /// See GetDampingRateFullThrottleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDampingRateFullThrottleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DAMPINGRATEZEROTHROTTLECLUTCHENGAGED
    // --------------------------------------------------------------------- //
    /// Damping rate of engine when no throttle is applied and the clutch is engaged (units:
    /// torque * seconds = mass * distance * distance / seconds). See attribute "dampingRateFullThrottle"
    /// for information about the effect of the value. The value has to be greater or equal 0.
    ///
    /// Note: the default value -1 is not a valid value as such but will result in the value 2.0
    /// being used (in meter length scale and kilogram mass scale or the equivalent if other units
    /// are used).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleEngine:dampingRateZeroThrottleClutchEngaged = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDampingRateZeroThrottleClutchEngagedAttr() const;

    /// See GetDampingRateZeroThrottleClutchEngagedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDampingRateZeroThrottleClutchEngagedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DAMPINGRATEZEROTHROTTLECLUTCHDISENGAGED
    // --------------------------------------------------------------------- //
    /// Damping rate of engine when no throttle is applied and the clutch is disengaged (units:
    /// torque * seconds = mass * distance * distance / seconds). See attribute "dampingRateFullThrottle"
    /// for information about the effect of the value. The value has to be greater or equal 0.
    ///
    /// Note: the default value -1 is not a valid value as such but will result in the value 0.35
    /// being used (in meter length scale and kilogram mass scale or the equivalent if other units
    /// are used).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleEngine:dampingRateZeroThrottleClutchDisengaged = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDampingRateZeroThrottleClutchDisengagedAttr() const;

    /// See GetDampingRateZeroThrottleClutchDisengagedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDampingRateZeroThrottleClutchDisengagedAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleEngineAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleEngineAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleEngineAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleEngineAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetMoiAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineMoi));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreateMoiAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineMoi), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetPeakTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEnginePeakTorque));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreatePeakTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleEnginePeakTorque), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetMaxRotationSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineMaxRotationSpeed));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreateMaxRotationSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineMaxRotationSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetIdleRotationSpeedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineIdleRotationSpeed));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreateIdleRotationSpeedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineIdleRotationSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetTorqueCurveAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineTorqueCurve));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreateTorqueCurveAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineTorqueCurve),
                                     SdfValueTypeNames->Float2Array,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetDampingRateFullThrottleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineDampingRateFullThrottle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreateDampingRateFullThrottleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineDampingRateFullThrottle),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetDampingRateZeroThrottleClutchEngagedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineDampingRateZeroThrottleClutchEngaged));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreateDampingRateZeroThrottleClutchEngagedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineDampingRateZeroThrottleClutchEngaged),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::GetDampingRateZeroThrottleClutchDisengagedAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleEngineDampingRateZeroThrottleClutchDisengaged));
}

inline UsdAttribute PhysxSchemaPhysxVehicleEngineAPI::CreateDampingRateZeroThrottleClutchDisengagedAttr() const
{
    return GetPrim().CreateAttribute(
        TfToken(PhysxSchemaTokens->physxVehicleEngineDampingRateZeroThrottleClutchDisengaged), SdfValueTypeNames->Float,
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
