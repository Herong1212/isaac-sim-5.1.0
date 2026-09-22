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

/// @file physxSchema/physxVehicleAckermannSteeringAPI.h

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
// PHYSXVEHICLEACKERMANNSTEERINGAPI                                            //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleAckermannSteeringAPI
///
/// Describes a steering system with Ackermann correction for two wheels. This system will
/// result in asymmetric steer angles such that the line defined by the non-steered wheel axle
/// and the lateral lines of the steered wheels meet at the same point. As a consequence, when
/// following the path around a curve, the inner wheel will turn more than the outer one. This
/// avoids that some wheels need to slip sideways to stay on the path. The specified wheels
/// will be connected to the steer control (see PhysxVehicleControllerAPI). This API schema
/// has to be applied to a prim with PhysxVehicleAPI applied. Can only be used for vehicles that
/// have a drive (see PhysxVehicleDriveBasicAPI or PhysxVehicleDriveStandardAPI). This API
/// schema can not be combined with PhysxVehicleSteeringAPI, only one or the other is allowed.

class PhysxSchemaPhysxVehicleAckermannSteeringAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleAckermannSteeringAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleAckermannSteeringAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleAckermannSteeringAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleAckermannSteeringAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleAckermannSteeringAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleAckermannSteeringAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleAckermannSteeringAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleAckermannSteeringAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleAckermannSteeringAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleAckermannSteeringAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleAckermannSteeringAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleAckermannSteeringAPI>())
        {
            return PhysxSchemaPhysxVehicleAckermannSteeringAPI(prim);
        }
        return PhysxSchemaPhysxVehicleAckermannSteeringAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // WHEEL0
    // --------------------------------------------------------------------- //
    /// The index of the wheel that is negative along the lateral axis and should get
    /// connected to the steering system. The index refers to the attribute "index" of
    /// PhysxVehicleWheelAttachmentAPI.
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxVehicleAckermannSteering:wheel0` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetWheel0Attr() const;

    /// See GetWheel0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheel0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // WHEEL1
    // --------------------------------------------------------------------- //
    /// The index of the wheel that is positive along the lateral axis and should get
    /// connected to the steering system. The index refers to the attribute "index" of
    /// PhysxVehicleWheelAttachmentAPI.
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxVehicleAckermannSteering:wheel1` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetWheel1Attr() const;

    /// See GetWheel1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheel1Attr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXSTEERANGLE
    // --------------------------------------------------------------------- //
    /// The maximum steer angle (in radians) that can be achieved by the wheels.
    /// Has to be in range [-pi, pi]. The steer angle of wheel0 will be defined by
    /// maxSteerAngle * ackermann_correction(0) * physxVehicleController:steer (see PhysxVehicleControllerAPI).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleAckermannSteering:maxSteerAngle = 0` |
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
    // WHEELBASE
    // --------------------------------------------------------------------- //
    /// The longitudinal distance between the axle that is affected by Ackermann
    /// correction and a reference axle (units: distance). The value has to be greater
    /// than zero.
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleAckermannSteering:wheelBase` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetWheelBaseAttr() const;

    /// See GetWheelBaseAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelBaseAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRACKWIDTH
    // --------------------------------------------------------------------- //
    /// The width of the axle defined by wheel0 and wheel1 (units: distance).
    /// The value has to be greater than zero.
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleAckermannSteering:trackWidth` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetTrackWidthAttr() const;

    /// See GetTrackWidthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrackWidthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STRENGTH
    // --------------------------------------------------------------------- //
    /// The strength of the Ackermann correction with 0 denoting no correction and
    /// 1 denoting perfect correction. The value has to be in range [0, 1].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleAckermannSteering:strength = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStrengthAttr() const;

    /// See GetStrengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStrengthAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleAckermannSteeringAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleAckermannSteeringAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleAckermannSteeringAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleAckermannSteeringAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::GetWheel0Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringWheel0));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::CreateWheel0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringWheel0),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::GetWheel1Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringWheel1));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::CreateWheel1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringWheel1),
                                     SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::GetMaxSteerAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringMaxSteerAngle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::CreateMaxSteerAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringMaxSteerAngle),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::GetWheelBaseAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringWheelBase));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::CreateWheelBaseAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringWheelBase),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::GetTrackWidthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringTrackWidth));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::CreateTrackWidthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringTrackWidth),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::GetStrengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringStrength));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAckermannSteeringAPI::CreateStrengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAckermannSteeringStrength),
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
