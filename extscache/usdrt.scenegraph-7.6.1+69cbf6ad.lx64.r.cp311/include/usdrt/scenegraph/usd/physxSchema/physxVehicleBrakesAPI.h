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

/// @file physxSchema/physxVehicleBrakesAPI.h

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
// PHYSXVEHICLEBRAKESAPI                                                       //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleBrakesAPI
///
/// Describes a braking system for a vehicle by specifying which wheels are connected to the
/// brake control and by defining the brake torque that gets applied to those wheels. Currently,
/// up to two braking systems are supported. Use the instance name TfToken "brakes0" and "brakes1"
/// of this multipleApply schema to distinguish between the two braking systems. Note that system
/// "brakes0" will be coupled to the brake control brake0 while system "brakes1" will be coupled
/// to the brake control brake1 (see PhysxVehicleControllerAPI for the brake controls). An example
/// for using two systems is to provide brake and handbrake control (the former applying brake
/// torque to all wheels and the latter applying brake torque to the rear wheels only). This API
/// schema has to be applied to a prim with PhysxVehicleAPI applied. Can only be used for vehicles
/// that have a drive (see PhysxVehicleDriveBasicAPI or PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleBrakesAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxVehicleBrakesAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxVehicleBrakesAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxVehicleBrakes:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleBrakesAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleBrakesAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxVehicleBrakesAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxVehicleBrakesAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleBrakesAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

    /// Returns the name of this multiple-apply schema instance
    TfToken GetName() const
    {
        return _GetInstanceName();
    }

    /// Applies this <b>multiple-apply</b> API schema to the given @p prim
    /// along with the given instance name, @p name.
    ///
    /// This information is stored by adding "PhysxVehicleBrakesAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxVehicleBrakesAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleBrakesAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleBrakesAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleBrakesAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleBrakesAPI>(name))
        {
            return PhysxSchemaPhysxVehicleBrakesAPI(prim, name);
        }
        return PhysxSchemaPhysxVehicleBrakesAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // WHEELS
    // --------------------------------------------------------------------- //
    /// List of indices, referencing the wheels that receive brake torque. The indices
    /// refer to the attribute "index" of PhysxVehicleWheelAttachmentAPI. If not specified,
    /// each wheel will receive a brake torque using a torque multiplier of 1 (see attribute
    /// torqueMultipliers).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] wheels` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetWheelsAttr() const;

    /// See GetWheelsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXBRAKETORQUE
    // --------------------------------------------------------------------- //
    /// The maximum brake torque that can be generated by the braking system
    /// (units: mass * distance * distance / seconds / seconds). Has to be greater or equal
    /// zero. For braking system "brakes0", the brake torque applied to wheels[i] will be
    /// defined by maxBrakeTorque * torqueMultipliers[i] * physxVehicleController:brake0
    /// (see PhysxVehicleControllerAPI).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float maxBrakeTorque = 0` |
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
    // TORQUEMULTIPLIERS
    // --------------------------------------------------------------------- //
    /// Defines how much of the max brake torque can be delivered to the wheels that are
    /// connected to the braking system. The values are unitless multipliers and have to be
    /// greater or equal to zero. See maxBrakeTorque for how these multipliers affect the
    /// brake torque applied to a wheel. If the attribute is defined, then the length of the
    /// array needs to match the length of the "wheels" array. If the attribute is not defined,
    /// a multiplier value of 1 will be used for all connected wheels.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] torqueMultipliers` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetTorqueMultipliersAttr() const;

    /// See GetTorqueMultipliersAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTorqueMultipliersAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleBrakesAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleBrakesAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleBrakesAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleBrakesAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxVehicleBrakesAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("physxVehicleBrakes"), instanceName, propName };
    // join (TODO this was SdfPath::JoinIdentifier(identifiers))
    std::string namespaceDelimeter = ":";
    std::string namespacedName = "";
    for (auto& token : identifiers)
    {
        namespacedName += token.GetString();
        if (!(token == *(identifiers.end() - 1)))
        {
            namespacedName += namespaceDelimeter;
        }
    }

    return TfToken(namespacedName);
}

inline UsdAttribute PhysxSchemaPhysxVehicleBrakesAPI::GetWheelsAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxVehicleBrakesAPI(GetName(), PhysxSchemaTokens->wheels));
}

inline UsdAttribute PhysxSchemaPhysxVehicleBrakesAPI::CreateWheelsAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxVehicleBrakesAPI(GetName(), PhysxSchemaTokens->wheels),
        SdfValueTypeNames->IntArray,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleBrakesAPI::GetMaxBrakeTorqueAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxVehicleBrakesAPI(GetName(), PhysxSchemaTokens->maxBrakeTorque));
}

inline UsdAttribute PhysxSchemaPhysxVehicleBrakesAPI::CreateMaxBrakeTorqueAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxVehicleBrakesAPI(GetName(), PhysxSchemaTokens->maxBrakeTorque),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleBrakesAPI::GetTorqueMultipliersAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxVehicleBrakesAPI(GetName(), PhysxSchemaTokens->torqueMultipliers));
}

inline UsdAttribute PhysxSchemaPhysxVehicleBrakesAPI::CreateTorqueMultipliersAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxVehicleBrakesAPI(GetName(), PhysxSchemaTokens->torqueMultipliers),
        SdfValueTypeNames->FloatArray,
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
