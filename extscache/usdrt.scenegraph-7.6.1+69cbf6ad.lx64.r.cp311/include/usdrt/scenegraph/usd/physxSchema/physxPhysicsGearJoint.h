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

/// @file physxSchema/physxPhysicsGearJoint.h

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
// PHYSXPHYSICSGEARJOINT                                                       //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxPhysicsGearJoint
///
/// Predefined gear joint type

class PhysxSchemaPhysxPhysicsGearJoint : public UsdPhysicsJoint
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a PhysxSchemaPhysxPhysicsGearJoint on UsdPrim @p prim.
    /// Equivalent to PhysxSchemaPhysxPhysicsGearJoint::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxPhysicsGearJoint(const UsdPrim& prim = UsdPrim()) : UsdPhysicsJoint(prim)
    {
    }

    /// Construct a PhysxSchemaPhysxPhysicsGearJoint on the prim held by @p schemaObj .
    /// Should be preferred over PhysxSchemaPhysxPhysicsGearJoint(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit PhysxSchemaPhysxPhysicsGearJoint(const UsdSchemaBase& schemaObj) : UsdPhysicsJoint(schemaObj)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxPhysicsGearJoint()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static PhysxSchemaPhysxPhysicsGearJoint Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // GEARRATIO
    // --------------------------------------------------------------------- //
    /// Gear ratio
    /// Range: (-inf, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:gearRatio = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGearRatioAttr() const;

    /// See GetGearRatioAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGearRatioAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HINGE0
    // --------------------------------------------------------------------- //
    /// Relationship to first revolute joint.
    ///
    UsdRelationship GetHinge0Rel() const;

    /// See GetHinge0Rel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateHinge0Rel() const;

public:
    // --------------------------------------------------------------------- //
    // HINGE1
    // --------------------------------------------------------------------- //
    /// Relationship to second revolute joint.
    ///
    UsdRelationship GetHinge1Rel() const;

    /// See GetHinge1Rel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateHinge1Rel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxPhysicsGearJoint::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxPhysicsGearJoint");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxPhysicsGearJoint::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxPhysicsGearJoint");
    return token;
}

/* static */
inline PhysxSchemaPhysxPhysicsGearJoint PhysxSchemaPhysxPhysicsGearJoint::Define(const UsdStageRefPtr& stage,
                                                                                 const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return PhysxSchemaPhysxPhysicsGearJoint();
    }
    return PhysxSchemaPhysxPhysicsGearJoint(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute PhysxSchemaPhysxPhysicsGearJoint::GetGearRatioAttr() const
{

    return GetPrim().GetAttribute(TfToken(PhysxSchemaTokens->physicsGearRatio));
}

inline UsdAttribute PhysxSchemaPhysxPhysicsGearJoint::CreateGearRatioAttr() const
{
    return GetPrim().CreateAttribute(TfToken(PhysxSchemaTokens->physicsGearRatio), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxPhysicsGearJoint::GetHinge0Rel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physicsHinge0);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsGearJoint::CreateHinge0Rel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physicsHinge0,
                                        /* custom = */ false);
}
inline UsdRelationship PhysxSchemaPhysxPhysicsGearJoint::GetHinge1Rel() const
{
    return GetPrim().GetRelationship(PhysxSchemaTokens->physicsHinge1);
}

inline UsdRelationship PhysxSchemaPhysxPhysicsGearJoint::CreateHinge1Rel() const
{
    return GetPrim().CreateRelationship(PhysxSchemaTokens->physicsHinge1,
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
