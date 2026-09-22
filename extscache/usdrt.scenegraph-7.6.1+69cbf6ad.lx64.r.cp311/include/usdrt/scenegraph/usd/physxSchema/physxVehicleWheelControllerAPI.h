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

/// @file physxSchema/physxVehicleWheelControllerAPI.h

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
// PHYSXVEHICLEWHEELCONTROLLERAPI                                              //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleWheelControllerAPI
///
/// PhysX wheel controller that samples user input and allows direct control of the wheel torques and steer angle to
/// drive the vehicle. Has to be applied to a prim with PhysxVehicleWheelAttachmentAPI applied and be a descendant of a
/// prim with a PhysxVehicleAPI applied.

class PhysxSchemaPhysxVehicleWheelControllerAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleWheelControllerAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleWheelControllerAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleWheelControllerAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleWheelControllerAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleWheelControllerAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleWheelControllerAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleWheelControllerAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleWheelControllerAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleWheelControllerAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleWheelControllerAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleWheelControllerAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleWheelControllerAPI>())
        {
            return PhysxSchemaPhysxVehicleWheelControllerAPI(prim);
        }
        return PhysxSchemaPhysxVehicleWheelControllerAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DRIVETORQUE
    // --------------------------------------------------------------------- //
    /// Torque to increase wheel angular rate and speed up (units: mass * distance * distance / seconds / seconds).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheelController:driveTorque = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDriveTorqueAttr() const;

    /// See GetDriveTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDriveTorqueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BRAKETORQUE
    // --------------------------------------------------------------------- //
    /// Torque to decrease wheel angular rate and slow down (units: mass * distance * distance / seconds / seconds).
    /// The value has to be greater or equal zero.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheelController:brakeTorque = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBrakeTorqueAttr() const;

    /// See GetBrakeTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBrakeTorqueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STEERANGLE
    // --------------------------------------------------------------------- //
    /// Steer angle of the wheel in radians.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleWheelController:steerAngle = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSteerAngleAttr() const;

    /// See GetSteerAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSteerAngleAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleWheelControllerAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleWheelControllerAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleWheelControllerAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleWheelControllerAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleWheelControllerAPI::GetDriveTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelControllerDriveTorque));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelControllerAPI::CreateDriveTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelControllerDriveTorque),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelControllerAPI::GetBrakeTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelControllerBrakeTorque));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelControllerAPI::CreateBrakeTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelControllerBrakeTorque),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelControllerAPI::GetSteerAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelControllerSteerAngle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelControllerAPI::CreateSteerAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelControllerSteerAngle),
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
