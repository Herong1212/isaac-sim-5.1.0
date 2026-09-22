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

/// @file physxSchema/physxVehicleGearsAPI.h

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
// PHYSXVEHICLEGEARSAPI                                                        //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleGearsAPI
///
/// Properties of PhysX vehicle gears. If the gears setup does not need to be shared among vehicle
/// instances, it can be applied to the prim which has PhysxVehicleDriveStandardAPI applied.
/// If the intent is to share the gears setup, PhysxVehicleGearsAPI can be applied to a separate
/// prim which can be linked to (see PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleGearsAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleGearsAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleGearsAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleGearsAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleGearsAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleGearsAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleGearsAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleGearsAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleGearsAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleGearsAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleGearsAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleGearsAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleGearsAPI>())
        {
            return PhysxSchemaPhysxVehicleGearsAPI(prim);
        }
        return PhysxSchemaPhysxVehicleGearsAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RATIOS
    // --------------------------------------------------------------------- //
    /// The gear ratios. First entry is for reverse, then there is support for up to 30 gears
    /// (neutral has a fixed value of 0 and is not represented in this array). The value for
    /// reverse has to be negative, else a positive value is expected and the ratios have to
    /// form a descending sequence.
    ///
    /// Note: if not defined, the following values will be used: [-4.0, 4.0, 2.0, 1.5, 1.1, 1.0].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] physxVehicleGears:ratios` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetRatiosAttr() const;

    /// See GetRatiosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRatiosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RATIOSCALE
    // --------------------------------------------------------------------- //
    /// Multiplier for gear ratio values. Final gear ratio is computed as ratios[currentGear] * ratioScale.
    /// The value has to be positive.
    ///
    /// Note: if not defined, the value 4.0 will be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleGears:ratioScale` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRatioScaleAttr() const;

    /// See GetRatioScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRatioScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SWITCHTIME
    // --------------------------------------------------------------------- //
    /// Time it takes to switch gear (units: seconds).
    ///
    /// Note: if not defined, the value 0.5 will be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleGears:switchTime` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSwitchTimeAttr() const;

    /// See GetSwitchTimeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSwitchTimeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleGearsAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleGearsAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleGearsAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleGearsAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleGearsAPI::GetRatiosAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleGearsRatios));
}

inline UsdAttribute PhysxSchemaPhysxVehicleGearsAPI::CreateRatiosAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleGearsRatios), SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleGearsAPI::GetRatioScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleGearsRatioScale));
}

inline UsdAttribute PhysxSchemaPhysxVehicleGearsAPI::CreateRatioScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleGearsRatioScale), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleGearsAPI::GetSwitchTimeAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleGearsSwitchTime));
}

inline UsdAttribute PhysxSchemaPhysxVehicleGearsAPI::CreateSwitchTimeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleGearsSwitchTime), SdfValueTypeNames->Float,
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
