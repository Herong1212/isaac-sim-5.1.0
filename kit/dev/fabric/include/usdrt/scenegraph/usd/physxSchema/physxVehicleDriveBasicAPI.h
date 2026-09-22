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

/// @file physxSchema/physxVehicleDriveBasicAPI.h

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
// PHYSXVEHICLEDRIVEBASICAPI                                                   //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleDriveBasicAPI
///
/// Very simple drive model for a PhysX vehicle. A torque will be directly applied to the wheels
/// that are marked as driven (see PhysxVehicleMultiWheelDifferentialAPI or deprecated attribute
/// "driven" in PhysxVehicleWheelAttachmentAPI).
///
/// If the drive setup does not need to be shared among vehicle instances, it can be applied to the
/// prim which has PhysxVehicleAPI applied. If the intent is to share the drive setup, PhysxVehicleDriveBasicAPI
/// can be applied to a separate prim which can be linked to (see PhysxVehicleAPI).

class PhysxSchemaPhysxVehicleDriveBasicAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleDriveBasicAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleDriveBasicAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleDriveBasicAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleDriveBasicAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleDriveBasicAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleDriveBasicAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleDriveBasicAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleDriveBasicAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleDriveBasicAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleDriveBasicAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleDriveBasicAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleDriveBasicAPI>())
        {
            return PhysxSchemaPhysxVehicleDriveBasicAPI(prim);
        }
        return PhysxSchemaPhysxVehicleDriveBasicAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PEAKTORQUE
    // --------------------------------------------------------------------- //
    /// Maximum torque to generate when the accelerator pedal is at maximum
    /// (units: mass * distance * distance / seconds / seconds). The value has to be greater or equal 0.
    ///
    /// Note: PhysxVehicleMultiWheelDifferentialAPI can be used to specify which wheels are connected
    /// to the drive as well as how the torque should be distributed among those wheels. If the
    /// deprecated attribute "driven" of PhysxVehicleWheelAttachmentAPI is used, then each driven
    /// wheel can experience a torque up to the value defined in this attribute.
    ///
    /// Note: the applied torque is the value of the accelerator pedal (in range [0, 1]) multiplied
    /// by peakTorque.
    ///
    /// Note: the default value -1 is not a valid value as such but will result in the value 1000.0
    /// being used (in meter length scale and kilogram mass scale or the equivalent if other units
    /// are used).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleDriveBasic:peakTorque = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPeakTorqueAttr() const;

    /// See GetPeakTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePeakTorqueAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleDriveBasicAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleDriveBasicAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleDriveBasicAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleDriveBasicAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleDriveBasicAPI::GetPeakTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleDriveBasicPeakTorque));
}

inline UsdAttribute PhysxSchemaPhysxVehicleDriveBasicAPI::CreatePeakTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleDriveBasicPeakTorque),
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
