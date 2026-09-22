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

/// @file physxSchema/physxVehicleAutoGearBoxAPI.h

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
// PHYSXVEHICLEAUTOGEARBOXAPI                                                  //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleAutoGearBoxAPI
///
/// Properties of the PhysX vehicle automatic gear shift box. If the automatic gear shift box setup
/// does not need to be shared among vehicle instances, it can be applied to the prim which has
/// PhysxVehicleDriveStandardAPI applied. If the intent is to share the automatic gear shift box
/// setup, PhysxVehicleAutoGearBoxAPI can be applied to a separate prim which can be linked to
/// (see PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleAutoGearBoxAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleAutoGearBoxAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleAutoGearBoxAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleAutoGearBoxAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleAutoGearBoxAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleAutoGearBoxAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleAutoGearBoxAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleAutoGearBoxAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleAutoGearBoxAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleAutoGearBoxAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleAutoGearBoxAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleAutoGearBoxAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleAutoGearBoxAPI>())
        {
            return PhysxSchemaPhysxVehicleAutoGearBoxAPI(prim);
        }
        return PhysxSchemaPhysxVehicleAutoGearBoxAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // UPRATIOS
    // --------------------------------------------------------------------- //
    /// Value of normalized engine speed (engineRotationSpeed / maxRotationSpeed) that is high
    /// enough to increment gear. The first entry is for first gear and then up to the
    /// second highest gear. When (engineRotationSpeed / maxRotationSpeed) > upRatios[currentGear]
    /// the autobox will begin a transition to currentGear+1 unless currentGear is the highest
    /// possible gear or neutral or reverse.
    ///
    /// Note: if not defined, the following values will be used: [0.65, 0.65, 0.65, 0.65].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxVehicleAutoGearBox:upRatios` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetUpRatiosAttr() const;

    /// See GetUpRatiosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpRatiosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DOWNRATIOS
    // --------------------------------------------------------------------- //
    /// Value of normalized engine speed (engineRotationSpeed / maxRotationSpeed) that is low
    /// enough to decrement gear. The first entry is for second gear then up to the highest gear.
    /// When (engineRotationSpeed / maxRotationSpeed) < downRatios[currentGear] the autobox will
    /// begin a transition to currentGear-1 unless currentGear is first gear or neutral or reverse.
    ///
    /// Note: if not defined, the following values will be used: [0.5, 0.5, 0.5, 0.5].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxVehicleAutoGearBox:downRatios` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetDownRatiosAttr() const;

    /// See GetDownRatiosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDownRatiosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LATENCY
    // --------------------------------------------------------------------- //
    /// The latency time of the automatic gear shift box (units: seconds). This is the minimum
    /// time that must pass between each gear change that is initiated by the automatic gear shift
    /// box.
    ///
    /// Note: if not defined, the value 2.0 will be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleAutoGearBox:latency` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLatencyAttr() const;

    /// See GetLatencyAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLatencyAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleAutoGearBoxAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleAutoGearBoxAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleAutoGearBoxAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleAutoGearBoxAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleAutoGearBoxAPI::GetUpRatiosAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAutoGearBoxUpRatios));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAutoGearBoxAPI::CreateUpRatiosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAutoGearBoxUpRatios),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAutoGearBoxAPI::GetDownRatiosAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAutoGearBoxDownRatios));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAutoGearBoxAPI::CreateDownRatiosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAutoGearBoxDownRatios),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleAutoGearBoxAPI::GetLatencyAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleAutoGearBoxLatency));
}

inline UsdAttribute PhysxSchemaPhysxVehicleAutoGearBoxAPI::CreateLatencyAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleAutoGearBoxLatency), SdfValueTypeNames->Float,
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
