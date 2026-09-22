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

/// @file physxSchema/physxPhysicsRackAndPinionJoint.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdPhysics/joint.h"
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
// PHYSXPHYSICSRACKANDPINIONJOINT                                              //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxPhysicsRackAndPinionJoint
///
/// Predefined rack & pinion joint type

class PhysxSchemaPhysxPhysicsRackAndPinionJoint : public UsdPhysicsJoint
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPhysxPhysicsRackAndPinionJoint on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxPhysicsRackAndPinionJoint::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxPhysicsRackAndPinionJoint(const UsdPrim& prim = UsdPrim()) : UsdPhysicsJoint(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxPhysicsRackAndPinionJoint on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxPhysicsRackAndPinionJoint(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxPhysicsRackAndPinionJoint(const UsdSchemaBase& schemaObj) : UsdPhysicsJoint(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxPhysicsRackAndPinionJoint()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaPhysxPhysicsRackAndPinionJoint Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RATIO
    // --------------------------------------------------------------------- //
    /// Ratio between angular and linear motion.
    /// Range: (-inf, inf)
    /// Units: degrees / distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:ratio = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRatioAttr() const;

    /// See GetRatioAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRatioAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HINGE
    // --------------------------------------------------------------------- //
    /// Relationship to revolute joint.
    ///
    UsdRelationship GetHingeRel() const;

    /// See GetHingeRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateHingeRel() const;

public:
    // --------------------------------------------------------------------- //
    // PRISMATIC
    // --------------------------------------------------------------------- //
    /// Relationship to prismatic joint.
    ///
    UsdRelationship GetPrismaticRel() const;

    /// See GetPrismaticRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreatePrismaticRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxPhysicsRackAndPinionJoint::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxPhysicsRackAndPinionJoint");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxPhysicsRackAndPinionJoint::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxPhysicsRackAndPinionJoint");
    return token;
}

/* static */
inline PhysxSchemaPhysxPhysicsRackAndPinionJoint PhysxSchemaPhysxPhysicsRackAndPinionJoint::Define(
    const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaPhysxPhysicsRackAndPinionJoint();
    }
    return PhysxSchemaPhysxPhysicsRackAndPinionJoint(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaPhysxPhysicsRackAndPinionJoint::GetRatioAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsRatio));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsRackAndPinionJoint::CreateRatioAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsRatio), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxPhysicsRackAndPinionJoint::GetHingeRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physicsHinge);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsRackAndPinionJoint::CreateHingeRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physicsHinge,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxPhysicsRackAndPinionJoint::GetPrismaticRel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physicsPrismatic);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsRackAndPinionJoint::CreatePrismaticRel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physicsPrismatic,
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
