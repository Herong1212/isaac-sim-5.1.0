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

/// @file physxSchema/physxVehicleWheelAttachmentAPI.h

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
// PHYSXVEHICLEWHEELATTACHMENTAPI                                              //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxVehicleWheelAttachmentAPI
///
/// For every wheel of a vehicle, this class defines the attachment properties. Has to
/// be applied to a prim that is a descendant of a prim with PhysxVehicleAPI applied. If the wheel
/// attachment prim (the prim with PhysxVehicleWheelAttachmentAPI applied) is a UsdGeomXformable,
/// then the position and orientation of the prim will be set by the vehicle simulation. If the
/// wheel attachment prim has PhysicsCollisionAPI applied, then none of its descendants are allowed
/// to have PhysicsCollisionAPI applied. If the wheel attachment prim is a UsdGeomXformable but does
/// not have PhysicsCollisionAPI applied, then exactly one direct child prim among all descendants
/// is allowed to have PhysicsCollisionAPI applied. That prim will be interpreted as the collision
/// geometry of the wheel and its position and orientation will be set by the vehicle simulation
/// too. Note that the relative transform between the collision geometry prim and the wheel attachment
/// prim at the start of the simulation will be maintained (the relative transform with respect to
/// the center of mass frame of the vehicle rigid body that is). If there is no desire to have the
/// vehicle simulation control the transform of the wheel attachment prim, then a prim type that is
/// not a UsdGeomXformable should be chosen.

class PhysxSchemaPhysxVehicleWheelAttachmentAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a PhysxSchemaPhysxVehicleWheelAttachmentAPI on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxVehicleWheelAttachmentAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxVehicleWheelAttachmentAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxVehicleWheelAttachmentAPI on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxVehicleWheelAttachmentAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxVehicleWheelAttachmentAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxVehicleWheelAttachmentAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "PhysxVehicleWheelAttachmentAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid PhysxSchemaPhysxVehicleWheelAttachmentAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxVehicleWheelAttachmentAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxVehicleWheelAttachmentAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxVehicleWheelAttachmentAPI>())
        {
            return PhysxSchemaPhysxVehicleWheelAttachmentAPI(prim);
        }
        return PhysxSchemaPhysxVehicleWheelAttachmentAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // INDEX
    // --------------------------------------------------------------------- //
    /// The index of the wheel attachment. Some other components will reference the wheel attachments
    /// based on this index. Either all indices of a vehicle's wheel attachments need to be -1 or they
    /// need to cover all entries in the group {0, .., (numberOfWheels-1)}. All indices being -1 covers
    /// the case where wheels are controlled directly through PhysxVehicleWheelControllerAPI, for example,
    /// or when deprecated APIs are used still.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int physxVehicleWheelAttachment:index = -1` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetIndexAttr() const;

    /// See GetIndexAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIndexAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUSPENSIONTRAVELDIRECTION
    // --------------------------------------------------------------------- //
    /// The direction of the suspension travel (towards the wheel). The custom metadata
    /// physxVehicle:referenceFrameIsCenterOfMass (on the vehicle prim) defines in what frame
    /// the direction is specified. If set to true, the direction is assumed to be relative
    /// to the vehicle center of mass frame, else relative to the frame of the vehicle prim.
    /// Note that using the center of mass frame as reference is deprecated and will not be
    /// supported for much longer.
    ///
    /// Note: this attribute has to be specified (there is no default).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxVehicleWheelAttachment:suspensionTravelDirection` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetSuspensionTravelDirectionAttr() const;

    /// See GetSuspensionTravelDirectionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSuspensionTravelDirectionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUSPENSIONFRAMEPOSITION
    // --------------------------------------------------------------------- //
    /// The point of the suspension at max compression. The custom metadata
    /// physxVehicle:referenceFrameIsCenterOfMass (on the vehicle prim) defines in what frame
    /// the position is specified. If set to true, the position is assumed to be relative
    /// to the vehicle center of mass frame, else relative to the frame of the vehicle prim.
    /// Note that using the center of mass frame as reference is deprecated and will not be
    /// supported for much longer. Camber, steer and toe angles are all applied in the suspension
    /// frame. The vehicle frame transform of the wheel will be defined by: centerOfMassFrame *
    /// suspensionFrame * wheelFrame (if physxVehicle:referenceFrameIsCenterOfMass is true,
    /// else centerOfMassFrame has to be omitted).
    ///
    /// Note: either this attribute or the deprecated wheelCenterOfMassOffset have to
    /// to be specified (with the former taking precedence).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f physxVehicleWheelAttachment:suspensionFramePosition` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3f |

    UsdAttribute GetSuspensionFramePositionAttr() const;

    /// See GetSuspensionFramePositionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSuspensionFramePositionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUSPENSIONFRAMEORIENTATION
    // --------------------------------------------------------------------- //
    /// The orientation of the suspension frame. The custom metadata
    /// physxVehicle:referenceFrameIsCenterOfMass (on the vehicle prim) defines in what frame
    /// the orientation is specified. If set to true, the orientation is assumed to be relative
    /// to the vehicle center of mass frame, else relative to the frame of the vehicle prim.
    /// Note that using the center of mass frame as reference is deprecated and will not be
    /// supported for much longer. Camber, steer and toe angles are all applied in the suspension
    /// frame. The vehicle frame transform of the wheel will be defined by: centerOfMassFrame *
    /// suspensionFrame * wheelFrame (if physxVehicle:referenceFrameIsCenterOfMass is true,
    /// else centerOfMassFrame has to be omitted).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quatf physxVehicleWheelAttachment:suspensionFrameOrientation = (1, 0, 0, 0)` |
    /// | C++ Type | GfQuatf |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Quatf |

    UsdAttribute GetSuspensionFrameOrientationAttr() const;

    /// See GetSuspensionFrameOrientationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSuspensionFrameOrientationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUSPENSIONFORCEAPPPOINTOFFSET
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleSuspensionComplianceAPI instead.
    ///
    /// The location where the suspension force gets applied. The custom metadata
    /// physxVehicle:referenceFrameIsCenterOfMass (on the vehicle prim) defines in what frame
    /// the offset is specified. If set to true, the offset is assumed to be relative
    /// to the vehicle center of mass frame, else relative to the frame of the vehicle prim.
    /// Note that using the center of mass frame as reference is deprecated and will not be
    /// supported for much longer.
    ///
    /// Note: will be ignored if PhysxVehicleSuspensionComplianceAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxVehicleWheelAttachment:suspensionForceAppPointOffset` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetSuspensionForceAppPointOffsetAttr() const;

    /// See GetSuspensionForceAppPointOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSuspensionForceAppPointOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WHEELCENTEROFMASSOFFSET
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use suspensionFramePosition instead.
    ///
    /// The location of the wheel centre when at rest. The custom metadata
    /// physxVehicle:referenceFrameIsCenterOfMass (on the vehicle prim) defines in what frame
    /// the offset is specified. If set to true, the offset is assumed to be relative
    /// to the vehicle center of mass frame, else relative to the frame of the vehicle prim.
    /// Note that using the center of mass frame as reference is deprecated and will not be
    /// supported for much longer.
    ///
    /// Note: will be ignored if suspensionFramePosition is authored.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxVehicleWheelAttachment:wheelCenterOfMassOffset` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetWheelCenterOfMassOffsetAttr() const;

    /// See GetWheelCenterOfMassOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelCenterOfMassOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TIREFORCEAPPPOINTOFFSET
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleSuspensionComplianceAPI instead.
    ///
    /// The location where the tire force gets applied. The custom metadata
    /// physxVehicle:referenceFrameIsCenterOfMass (on the vehicle prim) defines in what frame
    /// the offset is specified. If set to true, the offset is assumed to be relative
    /// to the vehicle center of mass frame, else relative to the frame of the vehicle prim.
    /// Note that using the center of mass frame as reference is deprecated and will not be
    /// supported for much longer.
    ///
    /// Note: will be ignored if PhysxVehicleSuspensionComplianceAPI is used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxVehicleWheelAttachment:tireForceAppPointOffset` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetTireForceAppPointOffsetAttr() const;

    /// See GetTireForceAppPointOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTireForceAppPointOffsetAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WHEELFRAMEPOSITION
    // --------------------------------------------------------------------- //
    /// A position offset of the wheel center relative to the suspension frame.
    /// Non-zero values might be used, for example, if the steer axis should not go
    /// through the wheel center.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f physxVehicleWheelAttachment:wheelFramePosition = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3f |

    UsdAttribute GetWheelFramePositionAttr() const;

    /// See GetWheelFramePositionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelFramePositionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WHEELFRAMEORIENTATION
    // --------------------------------------------------------------------- //
    /// An orientation adjustment of the wheel relative to the suspension frame.
    /// The rotation angle around the wheel's lateral axis is applied in this frame.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quatf physxVehicleWheelAttachment:wheelFrameOrientation = (1, 0, 0, 0)` |
    /// | C++ Type | GfQuatf |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Quatf |

    UsdAttribute GetWheelFrameOrientationAttr() const;

    /// See GetWheelFrameOrientationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWheelFrameOrientationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DRIVEN
    // --------------------------------------------------------------------- //
    /// Deprecated. Please use PhysxVehicleMultiWheelDifferentialAPI instead.
    ///
    /// True if the tire is driven by the engine through the transmission. Will be ignored if the vehicle
    /// has no drive specified (see PhysxVehicleAPI:drive) or if PhysxVehicleMultiWheelDifferentialAPI
    /// is used instead.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physxVehicleWheelAttachment:driven` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetDrivenAttr() const;

    /// See GetDrivenAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDrivenAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WHEEL
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleWheelAPI prim.
    ///
    /// Note: either this relationship has to be specified or the prim must have PhysxVehicleWheelAPI
    /// applied (none or both of the two is invalid).
    ///
    UsdRelationship GetWheelRel() const;

    /// See GetWheelRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateWheelRel() const;

public:
    // --------------------------------------------------------------------- //
    // TIRE
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleTireAPI prim.
    ///
    /// Note: either this relationship has to be specified or the prim must have PhysxVehicleTireAPI
    /// applied (none or both of the two is invalid).
    ///
    UsdRelationship GetTireRel() const;

    /// See GetTireRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateTireRel() const;

public:
    // --------------------------------------------------------------------- //
    // SUSPENSION
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysxVehicleSuspensionAPI prim.
    ///
    /// Note: either this relationship has to be specified or the prim must have PhysxVehicleSuspensionAPI
    /// applied (none or both of the two is invalid).
    ///
    UsdRelationship GetSuspensionRel() const;

    /// See GetSuspensionRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateSuspensionRel() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONGROUP
    // --------------------------------------------------------------------- //
    /// A relationship to a PhysicsCollisionGroup instance that defines what the wheel/suspension scene queries should
    /// treat as a ground surface to collide against. If not specified, no specific filtering will be applied.
    ///
    UsdRelationship GetCollisionGroupRel() const;

    /// See GetCollisionGroupRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateCollisionGroupRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxVehicleWheelAttachmentAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxVehicleWheelAttachmentAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxVehicleWheelAttachmentAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxVehicleWheelAttachmentAPI");
    return token;
}


inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetIndexAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentIndex));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateIndexAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentIndex), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetSuspensionTravelDirectionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionTravelDirection));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateSuspensionTravelDirectionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionTravelDirection),
                                     SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetSuspensionFramePositionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionFramePosition));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateSuspensionFramePositionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionFramePosition),
                                     SdfValueTypeNames->Point3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetSuspensionFrameOrientationAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionFrameOrientation));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateSuspensionFrameOrientationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionFrameOrientation),
                                     SdfValueTypeNames->Quatf,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetSuspensionForceAppPointOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionForceAppPointOffset));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateSuspensionForceAppPointOffsetAttr() const
{
    return GetPrim().CreateAttribute(
        TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspensionForceAppPointOffset), SdfValueTypeNames->Float3,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetWheelCenterOfMassOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentWheelCenterOfMassOffset));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateWheelCenterOfMassOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentWheelCenterOfMassOffset),
                                     SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetTireForceAppPointOffsetAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentTireForceAppPointOffset));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateTireForceAppPointOffsetAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentTireForceAppPointOffset),
                                     SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetWheelFramePositionAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentWheelFramePosition));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateWheelFramePositionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentWheelFramePosition),
                                     SdfValueTypeNames->Point3f,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetWheelFrameOrientationAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentWheelFrameOrientation));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateWheelFrameOrientationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentWheelFrameOrientation),
                                     SdfValueTypeNames->Quatf,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetDrivenAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentDriven));
}

inline UsdAttribute PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateDrivenAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physxVehicleWheelAttachmentDriven),
                                     SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetWheelRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentWheel);
}

inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateWheelRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentWheel,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetTireRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentTire);
}

inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateTireRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentTire,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetSuspensionRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspension);
}

inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateSuspensionRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentSuspension,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::GetCollisionGroupRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentCollisionGroup);
}

inline UsdRelationship PhysxSchemaPhysxVehicleWheelAttachmentAPI::CreateCollisionGroupRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physxVehicleWheelAttachmentCollisionGroup,
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
