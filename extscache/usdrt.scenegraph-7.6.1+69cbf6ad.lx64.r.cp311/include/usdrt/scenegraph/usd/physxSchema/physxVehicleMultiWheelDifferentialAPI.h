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

/// @file physxSchema/physxVehicleMultiWheelDifferentialAPI.h

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
// PHYSXVEHICLEMULTIWHEELDIFFERENTIALAPI                                       //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI
///
/// Describes which wheels of a vehicle are driven as well as the distribution of the
/// drive torque among those wheels. Has to be applied to a prim with PhysxVehicleAPI applied.
/// Can only be used for vehicles that have a drive (see PhysxVehicleDriveBasicAPI or
/// PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI(const UsdSchemaBase& schemaObj)
        : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleMultiWheelDifferentialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI>())
        {
            return PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI(prim);
        }
        return PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // WHEELS
    // --------------------------------------------------------------------- //
    /// List of indices, referencing the wheels that are driven (receiving torque from the engine). The
    /// indices refer to the attribute "index" of PhysxVehicleWheelAttachmentAPI.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physxVehicleMultiWheelDifferential:wheels` |
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
    // TORQUERATIOS
    // --------------------------------------------------------------------- //
    /// Defines how the drive torque should get distributed among the wheels specified in the "wheels"
    /// attribute. The provided ratios must be in range [-1, 1] and under normal circumstances the absolute
    /// values should sum up to 1. If the attribute is defined, then the length of the array needs to match
    /// the length of the "wheels" array. If the attribute is not defined, the torque will get split equally
    /// among all driven wheels.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxVehicleMultiWheelDifferential:torqueRatios` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetTorqueRatiosAttr() const;

    /// See GetTorqueRatiosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTorqueRatiosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // AVERAGEWHEELSPEEDRATIOS
    // --------------------------------------------------------------------- //
    /// Defines how the speeds of the driven wheels get weighted when computing the average wheel
    /// speed at the clutch (for computing clutch slip). The provided ratios must be in range [0, 1]
    /// and under normal circumstances sum up to 1. If the attribute is defined, then the length of
    /// the array needs to match the length of the "wheels" array. If the attribute is not defined,
    /// the wheel speeds of all driven wheels will get weighted equally.
    ///
    /// Note: if a vehicle is using a PhysxVehicleDriveBasicAPI drive, then this attribute should not
    /// be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxVehicleMultiWheelDifferential:averageWheelSpeedRatios` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetAverageWheelSpeedRatiosAttr() const;

    /// See GetAverageWheelSpeedRatiosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAverageWheelSpeedRatiosAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::GetWheelsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleMultiWheelDifferentialWheels));
}

inline UsdAttribute PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::CreateWheelsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleMultiWheelDifferentialWheels),
                                     SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::GetTorqueRatiosAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleMultiWheelDifferentialTorqueRatios));
}

inline UsdAttribute PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::CreateTorqueRatiosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleMultiWheelDifferentialTorqueRatios),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::GetAverageWheelSpeedRatiosAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleMultiWheelDifferentialAverageWheelSpeedRatios));
}

inline UsdAttribute PhysxSchemaPhysxVehicleMultiWheelDifferentialAPI::CreateAverageWheelSpeedRatiosAttr() const
{
    return GetPrim().CreateAttribute(
        TfToken(PhysxSchemaTokens->physxVehicleMultiWheelDifferentialAverageWheelSpeedRatios),
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
