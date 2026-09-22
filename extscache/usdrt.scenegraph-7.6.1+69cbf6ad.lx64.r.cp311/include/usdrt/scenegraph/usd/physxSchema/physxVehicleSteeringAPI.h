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

/// @file physxSchema/physxVehicleSteeringAPI.h

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
// PHYSXVEHICLESTEERINGAPI                                                     //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleSteeringAPI
///
/// Describes a steering system for a vehicle by specifying which wheels are connected to the
/// steer control and by defining the maximum steer angle for those wheels (see PhysxVehicleControllerAPI
/// for the steer control). This API schema has to be applied to a prim with PhysxVehicleAPI applied.
/// Can only be used for vehicles that have a drive (see PhysxVehicleDriveBasicAPI or
/// PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleSteeringAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleSteeringAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleSteeringAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleSteeringAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleSteeringAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleSteeringAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleSteeringAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleSteeringAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleSteeringAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleSteeringAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleSteeringAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleSteeringAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleSteeringAPI>())
        {
            return PhysxSchemaPhysxVehicleSteeringAPI(prim);
        }
        return PhysxSchemaPhysxVehicleSteeringAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // WHEELS
    // --------------------------------------------------------------------- //
    /// List of indices, referencing the wheels that are going to be steered. The indices
    /// refer to the attribute "index" of PhysxVehicleWheelAttachmentAPI. If not specified,
    /// every wheel will be affected by the steer control using an angle multiplier of 1
    /// (see attribute angleMultipliers).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physxVehicleSteering:wheels` |
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
    // MAXSTEERANGLE
    // --------------------------------------------------------------------- //
    /// The maximum steer angle (in radians) that can be achieved by the wheels.
    /// Has to be in range [-pi, pi] when multiplied by the attribute angleMultipliers.
    /// The steer angle of wheels[i] will be defined by maxSteerAngle * angleMultipliers[i] *
    /// physxVehicleController:steer (see PhysxVehicleControllerAPI).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleSteering:maxSteerAngle = 0` |
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
    // ANGLEMULTIPLIERS
    // --------------------------------------------------------------------- //
    /// Allows to adjust the max steer angle for each wheel that is steered. The values are
    /// unitless multipliers. See maxSteerAngle for how these multipliers affect the steer
    /// angle of a wheel. If the attribute is defined, then the length of the array needs
    /// to match the length of the "wheels" array. If the attribute is not defined,
    /// a multiplier value of 1 will be used for all steered wheels.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxVehicleSteering:angleMultipliers` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetAngleMultipliersAttr() const;

    /// See GetAngleMultipliersAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAngleMultipliersAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleSteeringAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleSteeringAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleSteeringAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleSteeringAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleSteeringAPI::GetWheelsAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSteeringWheels));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSteeringAPI::CreateWheelsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSteeringWheels), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSteeringAPI::GetMaxSteerAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSteeringMaxSteerAngle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSteeringAPI::CreateMaxSteerAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSteeringMaxSteerAngle),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSteeringAPI::GetAngleMultipliersAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSteeringAngleMultipliers));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSteeringAPI::CreateAngleMultipliersAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSteeringAngleMultipliers),
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
