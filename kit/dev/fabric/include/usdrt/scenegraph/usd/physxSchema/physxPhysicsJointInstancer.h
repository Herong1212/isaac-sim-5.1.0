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

/// @file physxSchema/physxPhysicsJointInstancer.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/physxSchema/physxPhysicsInstancer.h"
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
// PHYSXPHYSICSJOINTINSTANCER                                                  //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxPhysicsJointInstancer
///
/// Physics joint instancer, the prototypes are expected to be UsdPhysicsJoint prim types.

class PhysxSchemaPhysxPhysicsJointInstancer : public PhysxSchemaPhysxPhysicsInstancer
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPhysxPhysicsJointInstancer on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxPhysicsJointInstancer::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxPhysicsJointInstancer(const UsdPrim& prim = UsdPrim())
        : PhysxSchemaPhysxPhysicsInstancer(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxPhysicsJointInstancer on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxPhysicsJointInstancer(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxPhysicsJointInstancer(const UsdSchemaBase& schemaObj)
        : PhysxSchemaPhysxPhysicsInstancer(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxPhysicsJointInstancer()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaPhysxPhysicsJointInstancer Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSBODY0INDICES
    // --------------------------------------------------------------------- //
    /// <b>Optional property</b>. Only applicable if body0s is a point instancer.
    /// An index specifies the per-instance body0 rel as the rigid body at the body0s-instancer's protoIndices[index].
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physics:body0Indices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetPhysicsBody0IndicesAttr() const;

    /// See GetPhysicsBody0IndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePhysicsBody0IndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSBODY1INDICES
    // --------------------------------------------------------------------- //
    /// <b>Optional property</b>. Only applicable if body0s is a point instancer.
    /// An index specifies the per-instance body0 rel as the rigid body at the body0s-instancer's protoIndices[index].
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] physics:body1Indices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetPhysicsBody1IndicesAttr() const;

    /// See GetPhysicsBody1IndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePhysicsBody1IndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSLOCALPOS0S
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. Per-instance localPos0. This transformation
    /// is added on top of the joint localPos0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physics:localPos0s` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetPhysicsLocalPos0sAttr() const;

    /// See GetPhysicsLocalPos0sAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePhysicsLocalPos0sAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSLOCALROT0S
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. Per-instance localRot0. This transformation
    /// is added on top of the joint localPos0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quath[] physics:localRot0s` |
    /// | C++ Type | VtArray<GfQuath> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->QuathArray |

    UsdAttribute GetPhysicsLocalRot0sAttr() const;

    /// See GetPhysicsLocalRot0sAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePhysicsLocalRot0sAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSLOCALPOS1S
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. Per-instance localPos1. This transformation
    /// is added on top of the joint localPos1.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] physics:localPos1s` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetPhysicsLocalPos1sAttr() const;

    /// See GetPhysicsLocalPos1sAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePhysicsLocalPos1sAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSLOCALROT1S
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. Per-instance localRot1. This transformation
    /// is added on top of the joint localPos0.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quath[] physics:localRot1s` |
    /// | C++ Type | VtArray<GfQuath> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->QuathArray |

    UsdAttribute GetPhysicsLocalRot1sAttr() const;

    /// See GetPhysicsLocalRot1sAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePhysicsLocalRot1sAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSBODY0S
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. The rel must contain either exactly one
    /// UsdGeomPointInstancer that instances rigid bodies; or one or more rigid-body prims in the stage.
    /// If the rel is to a point instancer, the body0Indices must be specified.
    ///
    ///
    UsdRelationship GetPhysicsBody0sRel() const;

    /// See GetPhysicsBody0sRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreatePhysicsBody0sRel() const;

public:
    // --------------------------------------------------------------------- //
    // PHYSICSBODY1S
    // --------------------------------------------------------------------- //
    /// <b>Required property</b>. The rel must contain either exactly one
    /// UsdGeomPointInstancer that instances rigid bodies; or one or more rigid-body prims in the stage.
    /// If the rel is to a point instancer, the body0Indices must be specified.
    ///
    ///
    UsdRelationship GetPhysicsBody1sRel() const;

    /// See GetPhysicsBody1sRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreatePhysicsBody1sRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxPhysicsJointInstancer::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxPhysicsJointInstancer");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxPhysicsJointInstancer::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxPhysicsJointInstancer");
    return token;
}

/* static */
inline PhysxSchemaPhysxPhysicsJointInstancer PhysxSchemaPhysxPhysicsJointInstancer::Define(const UsdStageRefPtr& stage,
                                                                                           const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaPhysxPhysicsJointInstancer();
    }
    return PhysxSchemaPhysxPhysicsJointInstancer(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsBody0IndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsBody0Indices));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsBody0IndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsBody0Indices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsBody1IndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsBody1Indices));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsBody1IndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsBody1Indices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsLocalPos0sAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsLocalPos0s));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsLocalPos0sAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsLocalPos0s), SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsLocalRot0sAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsLocalRot0s));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsLocalRot0sAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsLocalRot0s), SdfValueTypeNames->QuathArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsLocalPos1sAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsLocalPos1s));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsLocalPos1sAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsLocalPos1s), SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsLocalRot1sAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsLocalRot1s));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsLocalRot1sAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsLocalRot1s), SdfValueTypeNames->QuathArray,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsBody0sRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physicsBody0s);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsBody0sRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physicsBody0s,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxPhysicsJointInstancer::GetPhysicsBody1sRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physicsBody1s);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsJointInstancer::CreatePhysicsBody1sRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physicsBody1s,
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
