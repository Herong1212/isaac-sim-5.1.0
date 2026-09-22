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

/// @file physxSchema/physxVehicleTankDifferentialAPI.h

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
// PHYSXVEHICLETANKDIFFERENTIALAPI                                             //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleTankDifferentialAPI
///
/// Differential to set up a wheeled tank vehicle. Describes which wheels of a vehicle are part of
/// the tank tracks. The wheels in each tank track have a constraint applied to them to enforce the
/// rule that they all have the same longitudinal speed at the contact point between the wheel and the
/// tank track. Driven wheels that are not part of a tank track receive the torque split specified in
/// physxVehicleMultiWheelDifferential:torqueRatios. Has to be applied to a prim with PhysxVehicleAPI
/// applied. Can only be used for vehicles that have a standard drive (see PhysxVehicleDriveStandardAPI).

class PhysxSchemaPhysxVehicleTankDifferentialAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleTankDifferentialAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleTankDifferentialAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleTankDifferentialAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleTankDifferentialAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleTankDifferentialAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleTankDifferentialAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleTankDifferentialAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleTankDifferentialAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleTankDifferentialAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleTankDifferentialAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleTankDifferentialAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleTankDifferentialAPI>())
        {
            return PhysxSchemaPhysxVehicleTankDifferentialAPI(prim);
        }
        return PhysxSchemaPhysxVehicleTankDifferentialAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // NUMBEROFWHEELSPERTRACK
    // --------------------------------------------------------------------- //
    /// For each track, this array holds the number of wheels assigned to that track.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physxVehicleTankDifferential:numberOfWheelsPerTrack` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetNumberOfWheelsPerTrackAttr() const;

    /// See GetNumberOfWheelsPerTrackAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNumberOfWheelsPerTrackAttr() const;

public:
    // --------------------------------------------------------------------- //
    // THRUSTINDEXPERTRACK
    // --------------------------------------------------------------------- //
    /// For each track, this array holds the index of the thrust control (0 or 1, see PhysxVehicleTankControllerAPI)
    /// that drives the track. The length of the array needs to match the length of the
    /// "numberOfWheelsPerTrack" array.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physxVehicleTankDifferential:thrustIndexPerTrack` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetThrustIndexPerTrackAttr() const;

    /// See GetThrustIndexPerTrackAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateThrustIndexPerTrackAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRACKTOWHEELINDICES
    // --------------------------------------------------------------------- //
    /// For each track, this array holds the start index of the list describing the wheels that
    /// are assigned to that track (e.g., the list of wheel indices assigned to the track with index
    /// 2 starts at: wheelIndicesInTrackOrder[trackToWheelIndices[2]]). The length of the array needs
    /// to match the length of the "numberOfWheelsPerTrack" array.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physxVehicleTankDifferential:trackToWheelIndices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetTrackToWheelIndicesAttr() const;

    /// See GetTrackToWheelIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrackToWheelIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WHEELINDICESINTRACKORDER
    // --------------------------------------------------------------------- //
    /// The wheels (identified by wheel attachment indices, see attribtue "index" of
    /// PhysxVehicleWheelAttachmentAPI) assigned to track 0, followed by the wheels assigned to
    /// track 1 and so on. The length of the array is expected to be equal (or larger than) the number
    /// of wheels that are assigned to tracks.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physxVehicleTankDifferential:wheelIndicesInTrackOrder` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetWheelIndicesInTrackOrderAttr() const;

    /// See GetWheelIndicesInTrackOrderAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelIndicesInTrackOrderAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleTankDifferentialAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleTankDifferentialAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleTankDifferentialAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleTankDifferentialAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::GetNumberOfWheelsPerTrackAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialNumberOfWheelsPerTrack));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::CreateNumberOfWheelsPerTrackAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialNumberOfWheelsPerTrack),
                                     SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::GetThrustIndexPerTrackAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialThrustIndexPerTrack));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::CreateThrustIndexPerTrackAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialThrustIndexPerTrack),
                                     SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::GetTrackToWheelIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialTrackToWheelIndices));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::CreateTrackToWheelIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialTrackToWheelIndices),
                                     SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::GetWheelIndicesInTrackOrderAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialWheelIndicesInTrackOrder));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTankDifferentialAPI::CreateWheelIndicesInTrackOrderAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTankDifferentialWheelIndicesInTrackOrder),
                                     SdfValueTypeNames->IntArray,
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
