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

/// @file physxSchema/physxVehicleWheelAPI.h

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
// PHYSXVEHICLEWHEELAPI                                                        //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleWheelAPI
///
/// Properties of a PhysX vehicle wheel. If the wheel setup does not need to be shared among vehicle
/// instances, it can be applied to the prim which has PhysxVehicleWheelAttachmentAPI applied.
/// If the intent is to share the wheel setup, PhysxVehicleWheelAPI can be applied to a separate
/// prim which can be linked to (see PhysxVehicleWheelAttachmentAPI).

class PhysxSchemaPhysxVehicleWheelAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleWheelAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleWheelAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleWheelAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleWheelAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleWheelAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleWheelAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleWheelAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleWheelAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleWheelAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleWheelAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleWheelAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleWheelAPI>())
        {
            return PhysxSchemaPhysxVehicleWheelAPI(prim);
        }
        return PhysxSchemaPhysxVehicleWheelAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RADIUS
    // --------------------------------------------------------------------- //
    /// The radius of the wheel (metal wheel plus tire).
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:radius` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRadiusAttr() const;

    /// See GetRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRadiusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WIDTH
    // --------------------------------------------------------------------- //
    /// The width of the wheel (metal wheel plus tire).
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:width` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetWidthAttr() const;

    /// See GetWidthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWidthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MASS
    // --------------------------------------------------------------------- //
    /// The mass of the wheel (metal wheel plus tire).
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:mass` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMassAttr() const;

    /// See GetMassAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMassAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MOI
    // --------------------------------------------------------------------- //
    /// The moment of inertia (metal wheel plus tire) about the rolling axis (units:
    /// mass * distance * distance).
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:moi` |
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
    // DAMPINGRATE
    // --------------------------------------------------------------------- //
    /// The damping rate applied to the wheel (units: torque * seconds = mass * distance * distance / seconds).
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:dampingRate` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDampingRateAttr() const;

    /// See GetDampingRateAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDampingRateAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXBRAKETORQUE
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleBrakesAPI instead.
    ///
    /// The maximum brake torque that can be applied to the wheel
    /// (units: mass * distance * distance / seconds / seconds).
    ///
    /// Note: will be ignored if PhysxVehicleBrakesAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:maxBrakeTorque` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxBrakeTorqueAttr() const;

    /// See GetMaxBrakeTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxBrakeTorqueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXHANDBRAKETORQUE
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleBrakesAPI instead.
    ///
    /// The maximum hand brake torque that can be applied to the wheel
    /// (units: mass * distance * distance / seconds / seconds).
    ///
    /// Note: will be ignored if PhysxVehicleBrakesAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:maxHandBrakeTorque` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxHandBrakeTorqueAttr() const;

    /// See GetMaxHandBrakeTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxHandBrakeTorqueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXSTEERANGLE
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleSteeringAPI instead.
    ///
    /// The maximum steer angle (in radians) that can be achieved by the wheel.
    ///
    /// Note: will be ignored if PhysxVehicleSteeringAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:maxSteerAngle` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxSteerAngleAttr() const;

    /// See GetMaxSteerAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxSteerAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TOEANGLE
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleSuspensionComplianceAPI instead.
    ///
    /// The wheel toe angle (in radians).
    ///
    /// Note: currently, this attribute is only considered for vehicles using the
    /// PhysxVehicleDriveStandard drive type.
    ///
    /// Note: will be ignored if PhysxVehicleSuspensionComplianceAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheel:toeAngle` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetToeAngleAttr() const;

    /// See GetToeAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateToeAngleAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleWheelAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleWheelAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleWheelAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleWheelAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelRadius));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelRadius), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetWidthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelWidth));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateWidthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelWidth), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetMassAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMass));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateMassAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMass), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetMoiAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMoi));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateMoiAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMoi), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetDampingRateAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelDampingRate));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateDampingRateAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelDampingRate), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetMaxBrakeTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMaxBrakeTorque));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateMaxBrakeTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMaxBrakeTorque),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetMaxHandBrakeTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMaxHandBrakeTorque));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateMaxHandBrakeTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMaxHandBrakeTorque),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetMaxSteerAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMaxSteerAngle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateMaxSteerAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelMaxSteerAngle), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::GetToeAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelToeAngle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAPI::CreateToeAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelToeAngle), SdfValueTypeNames->Float,
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
