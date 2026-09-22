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

/// @file usdPhysics/joint.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/imageable.h"
#include "usdrt/scenegraph/usd/usdPhysics/tokens.h"


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
// PHYSICSJOINT                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsJoint
///
/// A joint constrains the movement of rigid bodies. Joint can be
/// created between two rigid bodies or between one rigid body and world.
/// By default joint primitive defines a D6 joint where all degrees of
/// freedom are free. Three linear and three angular degrees of freedom.
/// Note that default behavior is to disable collision between jointed bodies.
///

class UsdPhysicsJoint : public UsdGeomImageable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdPhysicsJoint on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsJoint::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsJoint(const UsdPrim& prim = UsdPrim()) : UsdGeomImageable(prim)
    {
    }

    /// Construct a UsdPhysicsJoint on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsJoint(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsJoint(const UsdSchemaBase& schemaObj) : UsdGeomImageable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsJoint()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdPhysicsJoint Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // LOCALPOS0
    // --------------------------------------------------------------------- //
    /// Relative position of the joint frame to body0's frame.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f physics:localPos0 = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3f |

    UsdAttribute GetLocalPos0Attr() const;

    /// See GetLocalPos0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalPos0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALROT0
    // --------------------------------------------------------------------- //
    /// Relative orientation of the joint frame to body0's frame.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quatf physics:localRot0 = (1, 0, 0, 0)` |
    /// | C++ Type | GfQuatf |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Quatf |

    UsdAttribute GetLocalRot0Attr() const;

    /// See GetLocalRot0Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalRot0Attr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALPOS1
    // --------------------------------------------------------------------- //
    /// Relative position of the joint frame to body1's frame.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f physics:localPos1 = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3f |

    UsdAttribute GetLocalPos1Attr() const;

    /// See GetLocalPos1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalPos1Attr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALROT1
    // --------------------------------------------------------------------- //
    /// Relative orientation of the joint frame to body1's frame.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quatf physics:localRot1 = (1, 0, 0, 0)` |
    /// | C++ Type | GfQuatf |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Quatf |

    UsdAttribute GetLocalRot1Attr() const;

    /// See GetLocalRot1Attr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalRot1Attr() const;

public:
    // --------------------------------------------------------------------- //
    // JOINTENABLED
    // --------------------------------------------------------------------- //
    /// Determines if the joint is enabled.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physics:jointEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetJointEnabledAttr() const;

    /// See GetJointEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateJointEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLISIONENABLED
    // --------------------------------------------------------------------- //
    /// Determines if the jointed subtrees should collide or not.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physics:collisionEnabled = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetCollisionEnabledAttr() const;

    /// See GetCollisionEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollisionEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // EXCLUDEFROMARTICULATION
    // --------------------------------------------------------------------- //
    /// Determines if the joint can be included in an Articulation.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool physics:excludeFromArticulation = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetExcludeFromArticulationAttr() const;

    /// See GetExcludeFromArticulationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateExcludeFromArticulationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BREAKFORCE
    // --------------------------------------------------------------------- //
    /// Joint break force. If set, joint is to break when this force
    /// limit is reached. (Used for linear DOFs.)
    /// Units: mass * distance / second / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:breakForce = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBreakForceAttr() const;

    /// See GetBreakForceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBreakForceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BREAKTORQUE
    // --------------------------------------------------------------------- //
    /// Joint break torque. If set, joint is to break when this torque
    /// limit is reached. (Used for angular DOFs.)
    /// Units: mass * distance * distance / second / second
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:breakTorque = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBreakTorqueAttr() const;

    /// See GetBreakTorqueAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBreakTorqueAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BODY0
    // --------------------------------------------------------------------- //
    /// Relationship to any UsdGeomXformable.
    ///
    UsdRelationship GetBody0Rel() const;

    /// See GetBody0Rel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateBody0Rel() const;

public:
    // --------------------------------------------------------------------- //
    // BODY1
    // --------------------------------------------------------------------- //
    /// Relationship to any UsdGeomXformable.
    ///
    UsdRelationship GetBody1Rel() const;

    /// See GetBody1Rel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateBody1Rel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsJoint::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsJoint");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsJoint::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsJoint");
    return token;
}

/* static */
inline UsdPhysicsJoint UsdPhysicsJoint::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdPhysicsJoint();
    }
    return UsdPhysicsJoint(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdPhysicsJoint::GetLocalPos0Attr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsLocalPos0));
}

inline UsdAttribute UsdPhysicsJoint::CreateLocalPos0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsLocalPos0), SdfValueTypeNames->Point3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetLocalRot0Attr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsLocalRot0));
}

inline UsdAttribute UsdPhysicsJoint::CreateLocalRot0Attr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsLocalRot0), SdfValueTypeNames->Quatf,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetLocalPos1Attr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsLocalPos1));
}

inline UsdAttribute UsdPhysicsJoint::CreateLocalPos1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsLocalPos1), SdfValueTypeNames->Point3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetLocalRot1Attr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsLocalRot1));
}

inline UsdAttribute UsdPhysicsJoint::CreateLocalRot1Attr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsLocalRot1), SdfValueTypeNames->Quatf,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetJointEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsJointEnabled));
}

inline UsdAttribute UsdPhysicsJoint::CreateJointEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsJointEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetCollisionEnabledAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsCollisionEnabled));
}

inline UsdAttribute UsdPhysicsJoint::CreateCollisionEnabledAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsCollisionEnabled), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetExcludeFromArticulationAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsExcludeFromArticulation));
}

inline UsdAttribute UsdPhysicsJoint::CreateExcludeFromArticulationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsExcludeFromArticulation), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetBreakForceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsBreakForce));
}

inline UsdAttribute UsdPhysicsJoint::CreateBreakForceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsBreakForce), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsJoint::GetBreakTorqueAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsBreakTorque));
}

inline UsdAttribute UsdPhysicsJoint::CreateBreakTorqueAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsBreakTorque), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship UsdPhysicsJoint::GetBody0Rel() const
{
    return GetPrim().GetRelationship(UsdPhysicsTokens->physicsBody0);
}

inline UsdRelationship UsdPhysicsJoint::CreateBody0Rel() const
{
    return GetPrim().CreateRelationship(UsdPhysicsTokens->physicsBody0,
                                        /* custom = */ false);
}
inline UsdRelationship UsdPhysicsJoint::GetBody1Rel() const
{
    return GetPrim().GetRelationship(UsdPhysicsTokens->physicsBody1);
}

inline UsdRelationship UsdPhysicsJoint::CreateBody1Rel() const
{
    return GetPrim().CreateRelationship(UsdPhysicsTokens->physicsBody1,
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
