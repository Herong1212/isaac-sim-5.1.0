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

/// @file physxSchema/physxVehicleTankControllerAPI.h

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
// PHYSXVEHICLETANKCONTROLLERAPI                                               //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleTankControllerAPI
///
/// PhysX vehicle tank controller to divert torque from the engine to the wheels of the tracks
/// of a wheel based tank vehicle (see PhysxVehicleTankDifferentialAPI). Note that the "accelerator"
/// attribute of PhysxVehicleControllerAPI still drives the engine torque whereas the thrust controls
/// introduced here define how that torque gets diverted to the wheels, so both controls need to
/// be used to drive a wheel based tank vehicle usually. This API schema has to be applied to a prim
/// with PhysxVehicleAPI applied. Can only be used for vehicles that have a standard drive and a
/// tank differential defined (see PhysxVehicleDriveStandardAPI, PhysxVehicleTankDifferentialAPI).

class PhysxSchemaPhysxVehicleTankControllerAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleTankControllerAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleTankControllerAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleTankControllerAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleTankControllerAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleTankControllerAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleTankControllerAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleTankControllerAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleTankControllerAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleTankControllerAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleTankControllerAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleTankControllerAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleTankControllerAPI>())
        {
            return PhysxSchemaPhysxVehicleTankControllerAPI(prim);
        }
        return PhysxSchemaPhysxVehicleTankControllerAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // THRUST0
    // --------------------------------------------------------------------- //
    /// Magnitude of thrust to apply to the tracks that are assigned to thrust control 0.
    /// Values have to be in [-1.0, 1.0] with the sign dictating whether the thrust will be
    /// applied positively or negatively with respect to the gearing ratio.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTankController:thrust0 = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetThrust0Attr() const;

    /// See GetThrust0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateThrust0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // THRUST1
    // --------------------------------------------------------------------- //
    /// Magnitude of thrust to apply to the tracks that are assigned to thrust control 1.
    /// Values have to be in [-1.0, 1.0] with the sign dictating whether the thrust will be
    /// applied positively or negatively with respect to the gearing ratio.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTankController:thrust1 = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetThrust1Attr() const;

    /// See GetThrust1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateThrust1Attr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleTankControllerAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleTankControllerAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleTankControllerAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleTankControllerAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleTankControllerAPI::GetThrust0Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankControllerThrust0));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankControllerAPI::CreateThrust0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankControllerThrust0),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankControllerAPI::GetThrust1Attr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankControllerThrust1));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankControllerAPI::CreateThrust1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankControllerThrust1),
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
