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

/// @file physxSchema/physxVehicleDriveStandardAPI.h

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
// PHYSXVEHICLEDRIVESTANDARDAPI                                                //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleDriveStandardAPI
///
/// Standard drive model for a PhysX vehicle. The available drive torque will be split equally
/// between all the wheels that are marked as driven (see PhysxVehicleMultiWheelDifferentialAPI
/// or deprecated attribute "driven" in PhysxVehicleWheelAttachmentAPI) unless the torque
/// distributon is configured explicitly (see PhysxVehicleMultiWheelDifferentialAPI for details).
///
/// If the drive setup does not need to be shared among vehicle instances, it can be applied to the
/// prim which has PhysxVehicleAPI applied. If the intent is to share the drive setup, PhysxVehicleDriveStandardAPI
/// can be applied to a separate prim which can be linked to (see PhysxVehicleAPI).

class PhysxSchemaPhysxVehicleDriveStandardAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleDriveStandardAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleDriveStandardAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleDriveStandardAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleDriveStandardAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleDriveStandardAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleDriveStandardAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleDriveStandardAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleDriveStandardAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleDriveStandardAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleDriveStandardAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleDriveStandardAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleDriveStandardAPI>())
        {
            return PhysxSchemaPhysxVehicleDriveStandardAPI(prim);
        }
        return PhysxSchemaPhysxVehicleDriveStandardAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ENGINE
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleEngineAPI prim that describes the engine.
    ///
    /// Note: either this relationship has to be specified or the prim must have PhysxVehicleEngineAPI
    /// applied (none or both of the two is invalid).
    ///
    UsdRelationship GetEngineRel() const;

    /// See GetEngineRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateEngineRel() const;

public:
    // --------------------------------------------------------------------- //
    // GEARS
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleGearsAPI prim that describes the gears.
    ///
    /// Note: either this relationship has to be specified or the prim must have PhysxVehicleGearsAPI
    /// applied (none or both of the two is invalid).
    ///
    UsdRelationship GetGearsRel() const;

    /// See GetGearsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateGearsRel() const;

public:
    // --------------------------------------------------------------------- //
    // AUTOGEARBOX
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleAutoGearBoxAPI prim that describes the automatic gear shift box.
    /// This relationship is optional and should be omitted if no automatic gear shift is desired. It is
    /// also possible to apply PhysxVehicleAutoGearBoxAPI to the prim directly. In that case the relationship
    /// must not be defined.
    ///
    UsdRelationship GetAutoGearBoxRel() const;

    /// See GetAutoGearBoxRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateAutoGearBoxRel() const;

public:
    // --------------------------------------------------------------------- //
    // CLUTCH
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleClutchAPI prim that describes the clutch.
    ///
    /// Note: either this relationship has to be specified or the prim must have PhysxVehicleClutchAPI
    /// applied (none or both of the two is invalid).
    ///
    UsdRelationship GetClutchRel() const;

    /// See GetClutchRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateClutchRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleDriveStandardAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleDriveStandardAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleDriveStandardAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleDriveStandardAPI");
    return token;
}


inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::GetEngineRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleDriveStandardEngine);
}

inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::CreateEngineRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleDriveStandardEngine,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::GetGearsRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleDriveStandardGears);
}

inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::CreateGearsRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleDriveStandardGears,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::GetAutoGearBoxRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleDriveStandardAutoGearBox);
}

inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::CreateAutoGearBoxRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleDriveStandardAutoGearBox,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::GetClutchRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleDriveStandardClutch);
}

inline UsdRelationship PhysxSchemaPhysxVehicleDriveStandardAPI::CreateClutchRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleDriveStandardClutch,
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
