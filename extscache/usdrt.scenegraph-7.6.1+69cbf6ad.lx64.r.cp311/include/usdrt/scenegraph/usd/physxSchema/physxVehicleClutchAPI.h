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

/// @file physxSchema/physxVehicleClutchAPI.h

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
// PHYSXVEHICLECLUTCHAPI                                                       //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleClutchAPI
///
/// Properties of the PhysX vehicle clutch. If the clutch setup does not need to be shared among vehicle
/// instances, it can be applied to the prim which has PhysxVehicleDriveStandardAPI applied.
/// If the intent is to share the clutch setup, PhysxVehicleClutchAPI can be applied to a separate
/// prim which can be linked to (see PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleClutchAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleClutchAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleClutchAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleClutchAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleClutchAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleClutchAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleClutchAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleClutchAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleClutchAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleClutchAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleClutchAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleClutchAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleClutchAPI>())
        {
            return PhysxSchemaPhysxVehicleClutchAPI(prim);
        }
        return PhysxSchemaPhysxVehicleClutchAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // STRENGTH
    // --------------------------------------------------------------------- //
    /// Strength of clutch (units: torque * seconds = mass * distance * distance / seconds).
    /// The value has to be positive.
    /// The clutch is the mechanism that couples the engine to the wheels. A stronger clutch more
    /// strongly couples the engine to the wheels, while a clutch of strength zero completely
    /// decouples the engine from the wheels. Stronger clutches more quickly bring the wheels and
    /// engine into equilibrium, while weaker clutches take longer, resulting in periods of clutch
    /// slip and delays in power transmission from the engine to the wheels. The torque generated
    /// by the clutch is proportional to the clutch strength and the velocity difference between
    /// the engine's rotational speed and the rotational speed of the driven wheels after accounting
    /// for the gear ratio. The torque at the clutch is applied negatively to the engine and
    /// positively to the driven wheels.
    ///
    /// Note: if not defined, the value 10.0 will be used. This default value is in meter length scale
    /// and kilograms and will get adjusted if other units are used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleClutch:strength` |
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

inline const TfToken PhysxSchemaPhysxVehicleClutchAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleClutchAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleClutchAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleClutchAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleClutchAPI::GetStrengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleClutchStrength));
}

inline UsdAttribute PhysxSchemaPhysxVehicleClutchAPI::CreateStrengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleClutchStrength), SdfValueTypeNames->Float,
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
