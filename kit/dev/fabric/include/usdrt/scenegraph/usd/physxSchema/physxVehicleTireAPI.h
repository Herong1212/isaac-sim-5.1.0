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

/// @file physxSchema/physxVehicleTireAPI.h

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
// PHYSXVEHICLETIREAPI                                                         //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleTireAPI
///
/// Properties of a PhysX vehicle tire. If the tire setup does not need to be shared among vehicle
/// instances, it can be applied to the prim which has PhysxVehicleWheelAttachmentAPI applied.
/// If the intent is to share the tire setup, PhysxVehicleTireAPI can be applied to a separate
/// prim which can be linked to (see PhysxVehicleWheelAttachmentAPI).

class PhysxSchemaPhysxVehicleTireAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleTireAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleTireAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleTireAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleTireAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleTireAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleTireAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleTireAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleTireAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleTireAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleTireAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleTireAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleTireAPI>())
        {
            return PhysxSchemaPhysxVehicleTireAPI(prim);
        }
        return PhysxSchemaPhysxVehicleTireAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // LATSTIFFX
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use lateralStiffnessGraph instead.
    ///
    /// Tire lateral stiffness is a graph of tire load that has linear behavior near zero load and
    /// flattens at large loads. The parameter describes the minimum normalized load (load/restLoad)
    /// that gives a flat lateral stiffness response to load.
    ///
    /// Note: will be ignored if lateralStiffnessGraph is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTire:latStiffX = 2` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLatStiffXAttr() const;

    /// See GetLatStiffXAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLatStiffXAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LATSTIFFY
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use lateralStiffnessGraph instead.
    ///
    /// Tire lateral stiffness is a graph of tire load that has linear behavior near zero load and
    /// flattens at large loads. The parameter describes the maximum possible value of lateralStiffness/restLoad
    /// that occurs when (load/restLoad) >= latStiffX. If load/restLoad is greater than latStiffX then
    /// the lateral stiffness is latStiffY*restLoad, else the lateral stiffness is latStiffY*(load/latStiffX).
    ///
    /// Note: will be ignored if lateralStiffnessGraph is used.
    ///
    /// Note: if not defined, the value 17.095 will be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTire:latStiffY` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLatStiffYAttr() const;

    /// See GetLatStiffYAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLatStiffYAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LATERALSTIFFNESSGRAPH
    // --------------------------------------------------------------------- //
    /// Tire lateral stiffness is represented as a graph of tire load that has linear behavior
    /// near zero load and flattens at large loads. The first value of the parameter describes the
    /// minimum normalized load (load/restLoad) that gives a flat lateral stiffness response to load.
    /// This value has to be greater or equal 0. The second value of the parameter defines the lateral
    /// stiffness when the response is flat (the max lateral stiffness, units: mass * distance / seconds / seconds).
    /// This value has to be positive.
    ///
    /// Note: the default value (0, 0) is not a valid value as such but indicates that the
    /// deprecated attributes latStiffX and latStiffY should be used instead.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2 physxVehicleTire:lateralStiffnessGraph = (0, 0)` |
    /// | C++ Type | GfVec2f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2 |

    UsdAttribute GetLateralStiffnessGraphAttr() const;

    /// See GetLateralStiffnessGraphAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLateralStiffnessGraphAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LONGITUDINALSTIFFNESSPERUNITGRAVITY
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use longitudinalStiffness instead.
    ///
    /// Tire longitudinal stiffness per unit gravitational acceleration. Longitudinal stiffness of
    /// the tire is calculated as gravitationalAcceleration*longitudinalStiffnessPerUnitGravity.
    ///
    /// Note: will be ignored if longitudinalStiffness is used.
    ///
    /// Note: if not defined, the value 500 will be used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTire:longitudinalStiffnessPerUnitGravity` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLongitudinalStiffnessPerUnitGravityAttr() const;

    /// See GetLongitudinalStiffnessPerUnitGravityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLongitudinalStiffnessPerUnitGravityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LONGITUDINALSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Tire longitudinal stiffness (units: mass * distance / seconds / seconds).
    /// The value has to be positive. The resulting longitudinal force can be approximated as:
    /// longitudinalStiffness*longitudinalSlip.
    ///
    /// Note: the default value 0 is not a valid value as such but indicates that the deprecated
    /// attribute longitudinalStiffnessPerUnitGravity should be used instead.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTire:longitudinalStiffness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLongitudinalStiffnessAttr() const;

    /// See GetLongitudinalStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLongitudinalStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CAMBERSTIFFNESSPERUNITGRAVITY
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use camberStiffness instead.
    ///
    /// Tire camber stiffness per unit gravitational acceleration. Camber stiffness of the tire is
    /// calculated as gravitationalAcceleration*camberStiffnessPerUnitGravity.
    ///
    /// Note: will be ignored if camberStiffness is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTire:camberStiffnessPerUnitGravity = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCamberStiffnessPerUnitGravityAttr() const;

    /// See GetCamberStiffnessPerUnitGravityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCamberStiffnessPerUnitGravityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CAMBERSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Tire camber stiffness (units: mass * distance / seconds / seconds / radians).
    /// The value has to be greater or equal 0. Camber force can be approximated as:
    /// camberStiffness*camberAngle.
    ///
    /// Note: the default value -1 is not a valid value as such but indicates that the
    /// deprecated attribute camberStiffnessPerUnitGravity should be used instead.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTire:camberStiffness = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetCamberStiffnessAttr() const;

    /// See GetCamberStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCamberStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FRICTIONVSSLIPGRAPH
    // --------------------------------------------------------------------- //
    /// Graph of friction vs longitudinal slip with 3 points. The friction value extracted from this
    /// graph will be multiplied with the friction value of the combination of ground material and tire
    /// type. The array is expected to have 3 entries/points. For the first point, the first value is
    /// always zero and the second value is the friction available at zero longitudinal slip. For the
    /// second point, the first value is the longitudinal slip with maximum friction and the second
    /// value is the maximum friction. For the third point, the first value is the end point of the graph
    /// and the second value is the friction for slips greater than the end point of the graph. Note that
    /// the friction value of the first point is typically smaller than the friction value of the second
    /// point and the friction value of the second point is typically larger than the friction value of
    /// the third point.
    ///
    /// Note: if not defined, the following values will be used: [(0.0, 1.0), (0.1, 1.0), (1.0, 1.0)].
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float2[] physxVehicleTire:frictionVsSlipGraph` |
    /// | C++ Type | VtArray<GfVec2f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float2Array |

    UsdAttribute GetFrictionVsSlipGraphAttr() const;

    /// See GetFrictionVsSlipGraphAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrictionVsSlipGraphAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RESTLOAD
    // --------------------------------------------------------------------- //
    /// The load that develops on the tire when the vehicle is at rest on a flat plane
    /// (units: force = mass * distance / seconds / seconds). The value has to be greater or equal 0.
    /// If set to 0, the rest load will get computed automatically using the approximation of:
    /// gravitational acceleration * sprungMass.
    ///
    /// Note: it is not possible for a vehicle to have some rest load values being user-defined
    /// and some being computed automatically. Either all values have to be user-defined or all
    /// have to be set to 0 for auto-computation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxVehicleTire:restLoad = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRestLoadAttr() const;

    /// See GetRestLoadAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestLoadAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FRICTIONTABLE
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleTireFrictionTable instance.
    ///
    /// Note: if not defined, a default friction table will be used.
    ///
    UsdRelationship GetFrictionTableRel() const;

    /// See GetFrictionTableRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateFrictionTableRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleTireAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleTireAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleTireAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleTireAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetLatStiffXAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLatStiffX));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateLatStiffXAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLatStiffX), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetLatStiffYAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLatStiffY));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateLatStiffYAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLatStiffY), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetLateralStiffnessGraphAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLateralStiffnessGraph));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateLateralStiffnessGraphAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLateralStiffnessGraph),
                                     SdfValueTypeNames->Float2,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetLongitudinalStiffnessPerUnitGravityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLongitudinalStiffnessPerUnitGravity));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateLongitudinalStiffnessPerUnitGravityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLongitudinalStiffnessPerUnitGravity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetLongitudinalStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLongitudinalStiffness));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateLongitudinalStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireLongitudinalStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetCamberStiffnessPerUnitGravityAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireCamberStiffnessPerUnitGravity));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateCamberStiffnessPerUnitGravityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireCamberStiffnessPerUnitGravity),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetCamberStiffnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireCamberStiffness));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateCamberStiffnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireCamberStiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetFrictionVsSlipGraphAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireFrictionVsSlipGraph));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateFrictionVsSlipGraphAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireFrictionVsSlipGraph),
                                     SdfValueTypeNames->Float2Array,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::GetRestLoadAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireRestLoad));
}

inline UsdAttribute PhysxSchemaPhysxVehicleTireAPI::CreateRestLoadAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleTireRestLoad), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxVehicleTireAPI::GetFrictionTableRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleTireFrictionTable);
}

inline UsdRelationship PhysxSchemaPhysxVehicleTireAPI::CreateFrictionTableRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleTireFrictionTable,
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
