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

/// @file usdPhysics/collisionGroup.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
#include "usdrt/scenegraph/usd/usdPhysics/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/collectionAPI.h" */
// clang-format on

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
// PHYSICSCOLLISIONGROUP                                                       //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsCollisionGroup
///
/// Defines a collision group for coarse filtering. When a collision
/// occurs between two objects that have a PhysicsCollisionGroup assigned,
/// they will collide with each other unless this PhysicsCollisionGroup pair
/// is filtered. See filteredGroups attribute.
///
/// A CollectionAPI:colliders maintains a list of PhysicsCollisionAPI rel-s that
/// defines the members of this Collisiongroup.
///

class UsdPhysicsCollisionGroup : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdPhysicsCollisionGroup on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsCollisionGroup::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsCollisionGroup(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdPhysicsCollisionGroup on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsCollisionGroup(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsCollisionGroup(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsCollisionGroup()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdPhysicsCollisionGroup Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MERGEGROUPNAME
    // --------------------------------------------------------------------- //
    /// If non-empty, any collision groups in a stage with a matching
    /// mergeGroup should be considered to refer to the same collection. Matching
    /// collision groups should behave as if there were a single group containing
    /// referenced colliders and filter groups from both collections.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `string physics:mergeGroup` |
    /// | C++ Type | std::string |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->String |

    UsdAttribute GetMergeGroupNameAttr() const;

    /// See GetMergeGroupNameAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMergeGroupNameAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INVERTFILTEREDGROUPS
    // --------------------------------------------------------------------- //
    /// Normally, the filter will disable collisions against the selected
    /// filter groups. However, if this option is set, the filter will disable
    /// collisions against all colliders except for those in the selected filter
    /// groups.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool physics:invertFilteredGroups` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetInvertFilteredGroupsAttr() const;

    /// See GetInvertFilteredGroupsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInvertFilteredGroupsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FILTEREDGROUPS
    // --------------------------------------------------------------------- //
    /// References a list of PhysicsCollisionGroups with which
    /// collisions should be ignored.
    ///
    UsdRelationship GetFilteredGroupsRel() const;

    /// See GetFilteredGroupsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateFilteredGroupsRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsCollisionGroup::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsCollisionGroup");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsCollisionGroup::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsCollisionGroup");
    return token;
}

/* static */
inline UsdPhysicsCollisionGroup UsdPhysicsCollisionGroup::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdPhysicsCollisionGroup();
    }
    return UsdPhysicsCollisionGroup(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdPhysicsCollisionGroup::GetMergeGroupNameAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsMergeGroup));
}

inline UsdAttribute UsdPhysicsCollisionGroup::CreateMergeGroupNameAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsMergeGroup), SdfValueTypeNames->String,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsCollisionGroup::GetInvertFilteredGroupsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsInvertFilteredGroups));
}

inline UsdAttribute UsdPhysicsCollisionGroup::CreateInvertFilteredGroupsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsInvertFilteredGroups), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship UsdPhysicsCollisionGroup::GetFilteredGroupsRel() const
{
    return GetPrim().GetRelationship(UsdPhysicsTokens->physicsFilteredGroups);
}

inline UsdRelationship UsdPhysicsCollisionGroup::CreateFilteredGroupsRel() const
{
    return GetPrim().CreateRelationship(UsdPhysicsTokens->physicsFilteredGroups,
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
