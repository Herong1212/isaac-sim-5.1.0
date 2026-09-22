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

/// @file physxSchema/physxVehicleSuspensionComplianceAPI.h

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
// PHYSXVEHICLESUSPENSIONCOMPLIANCEAPI                                         //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleSuspensionComplianceAPI
///
/// Compliance describes how toe and camber angle and force application points are
/// affected by suspension compression. Each compliance term is in the form of a graph
/// with up to 3 points. The points in the graph consist of a normalized jounce value
/// (with 0 meaning fully elongated and 1 fully compressed suspension) and a corresponding
/// compliance value (which can be an angle or point etc. depending on the specific
/// compliance term). The sequence of points must respresent monotonically increasing
/// values of normalized jounce. The actual compliance value will be computed by linear
/// interpolation based on the current normalized jounce. If any graph has zero points
/// in it, a value of 0.0 is used for the compliance value. If any graph has 1 point
/// in it, the compliance value of that point is used directly. This API schema has to
/// be applied to a prim with PhysxVehicleWheelAttachmentAPI applied. If defined, then
/// this setup takes precedence over the deprecated attributes suspensionForceAppPointOffset
/// and tireForceAppPointOffset of the PhysxVehicleWheelAttachmentAPI API schema, the
/// deprecated attributes camberAtRest, camberAtMaxCompression, camberAtMaxDroop of the
/// PhysxVehicleSuspensionAPI API schema as well as the deprecated attribute toeAngle
/// of the PhysxVehicleWheelAPI API schema.

class PhysxSchemaPhysxVehicleSuspensionComplianceAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleSuspensionComplianceAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleSuspensionComplianceAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleSuspensionComplianceAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleSuspensionComplianceAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleSuspensionComplianceAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleSuspensionComplianceAPI(const UsdSchemaBase& schemaObj)
        : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleSuspensionComplianceAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleSuspensionComplianceAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleSuspensionComplianceAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleSuspensionComplianceAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleSuspensionComplianceAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleSuspensionComplianceAPI>())
        {
            return PhysxSchemaPhysxVehicleSuspensionComplianceAPI(prim);
        }
        return PhysxSchemaPhysxVehicleSuspensionComplianceAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // WHEELTOEANGLE
    // --------------------------------------------------------------------- //
    /// A graph of toe angle against normalized jounce with the toe angle expressed
    /// in radians in the range [-pi, pi]. See the class documentation for general info
    /// about the nature of these graphs and the data requirements.
    ///
    /// Note: the toe angle is applied in the suspension frame (see PhysxVehicleWheelAttachmentAPI).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2[] physxVehicleSuspensionCompliance:wheelToeAngle` |
    /// | C++ Type | VtArray<GfVec2f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2Array |

    UsdAttribute GetWheelToeAngleAttr() const;

    /// See GetWheelToeAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelToeAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WHEELCAMBERANGLE
    // --------------------------------------------------------------------- //
    /// A graph of camber angle against normalized jounce with the camber angle expressed
    /// in radians in the range [-pi, pi]. See the class documentation for general info
    /// about the nature of these graphs and the data requirements.
    ///
    /// Note: the camber angle is applied in the suspension frame (see PhysxVehicleWheelAttachmentAPI).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2[] physxVehicleSuspensionCompliance:wheelCamberAngle` |
    /// | C++ Type | VtArray<GfVec2f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2Array |

    UsdAttribute GetWheelCamberAngleAttr() const;

    /// See GetWheelCamberAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelCamberAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUSPENSIONFORCEAPPPOINT
    // --------------------------------------------------------------------- //
    /// Suspension forces are applied at an offset from the suspension frame (see
    /// PhysxVehicleWheelAttachmentAPI). An entry in this array defines this offset for a
    /// given normalized jounce value (which is the first element in the float4 while
    /// the other 3 elements are used to store the x, y, z coordinates of the offset).
    /// See the class documentation for general info about the nature of these compliance
    /// terms and the data requirements.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float4[] physxVehicleSuspensionCompliance:suspensionForceAppPoint` |
    /// | C++ Type | VtArray<GfVec4f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float4Array |

    UsdAttribute GetSuspensionForceAppPointAttr() const;

    /// See GetSuspensionForceAppPointAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSuspensionForceAppPointAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TIREFORCEAPPPOINT
    // --------------------------------------------------------------------- //
    /// Tire forces are applied at an offset from the suspension frame (see
    /// PhysxVehicleWheelAttachmentAPI). An entry in this array defines this offset for a
    /// given normalized jounce value (which is the first element in the float4 while
    /// the other 3 elements are used to store the x, y, z coordinates of the offset).
    /// See the class documentation for general info about the nature of these compliance
    /// terms and the data requirements.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float4[] physxVehicleSuspensionCompliance:tireForceAppPoint` |
    /// | C++ Type | VtArray<GfVec4f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float4Array |

    UsdAttribute GetTireForceAppPointAttr() const;

    /// See GetTireForceAppPointAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTireForceAppPointAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleSuspensionComplianceAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleSuspensionComplianceAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleSuspensionComplianceAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleSuspensionComplianceAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::GetWheelToeAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceWheelToeAngle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::CreateWheelToeAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceWheelToeAngle),
                                     SdfValueTypeNames->Float2Array,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::GetWheelCamberAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceWheelCamberAngle));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::CreateWheelCamberAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceWheelCamberAngle),
                                     SdfValueTypeNames->Float2Array,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::GetSuspensionForceAppPointAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceSuspensionForceAppPoint));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::CreateSuspensionForceAppPointAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceSuspensionForceAppPoint),
                                     SdfValueTypeNames->Float4Array,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::GetTireForceAppPointAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceTireForceAppPoint));
}

inline UsdAttribute PhysxSchemaPhysxVehicleSuspensionComplianceAPI::CreateTireForceAppPointAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleSuspensionComplianceTireForceAppPoint),
                                     SdfValueTypeNames->Float4Array,
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
