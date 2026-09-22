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

/// @file physxSchema/physxTendonAttachmentRootAPI.h

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
// PHYSXTENDONATTACHMENTROOTAPI                                                //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxTendonAttachmentRootAPI
///
/// WARNING: Draft API, this design is not fixed and may change in the future.
///
/// Applied to an articulation-link rigid-body Xformable.
///
/// The root API creates a new spatial tendon tree. The root tendon attachment is the only attachment in a tendon tree
/// that does not have a parent, so the parentLink, parentAttachment, and gearing attributes inherited from
/// PhysxTendonAttachmentAPI are ignored for a root.
///
/// Spatial tendons create line-of-sight distance constraints between links of a single articulation. In particular,
/// spatial tendons run through attachments that are positioned relative to a rigid-body link, and their length is
/// defined as a weighted sum of the distance between the attachments in the tendon.
///
/// Spatial tendons may branch, in which case the tendon splits up into multiple conceptual sub-tendons, one for each
/// root-to-leaf path in the tendon tree. The tendon tree starts at the root, and its topology is defined by the
/// attachments' parentLink rel and parentAttachment token.
///
/// It is possible to create multiple attachments per link, see PhysxTendonAttachmentAPI.
///
/// Details on dynamics:
///
/// The length of a sub-tendon in the tree is
///
/// subTendonLength = sum(gearing[i] * |p[i] - p_parent[i]|)
///
/// where the sum is evaluated along the unique tree path between root and leaf. The gearing[i] is the i-th attachment's
/// gearing, and |p[i] - p_parent[i]| is the distance between the positions of the i-th attachment and its parent
/// attachment.
///
/// Each subtendon has spring-damper dynamics acting on the length constraint
///
/// constraint = 0 = offset + subTendonLength - restLength
///
/// where the offset is a common summand for all sub-tendons of a spatial tendon, and the restLength is specific to a
/// sub-tendon, see the PhysxTendonAttachmentLeafAPI.
///
/// If limits are not active, the sub-tendon force that acts on the leaf is
///
/// F = stiffness * constraint + damping * tendonVelocity
///
/// where tendonVelocity is the sum of the time derivatives of the line-of-sight distances between
/// 1) the leaf and its parent attachment and
/// 2) the tendon root and its first child attachment on the path to the leaf.
/// Stiffness and damping are common parameters for all sub-tendons.
///
/// The 3D force applied at the leaf attachment is equal to
///
/// F * (p_parent - p_leaf).
///
/// where p_leaf and p_parent are the leaf's position and its parent's position, respectively. The reaction force acting
/// on the root attachment is
///
/// F * (p_child_leaf - p_root)
///
/// where p_child_leaf is the position of the root's child attachment that leads to the leaf that produces F,
/// and p_root is the root attachment position. The tendon force is not further propagated through the tendon, so at
/// intermediate attachments (i.e. created by PhysxTendonAttachmentAPI) no forces are applied.
///
/// Note that a spatial tendon may both pull and push on the leaf and root attachments. A string-like, one-sided
/// constraint can be implemented using the sub-tendon's length limits.
///
/// Sub-tendon length limits constrain the offset length
///
/// lowerLimit <= subTendonLength + offset<= upperLimit
///
/// and, when active, add a restoring spring force parametrized by limitStiffness to the tendon force, analogous to the
/// length constraint force above. Limit dynamics are damped by the tendon-length damping that is applied regardless of
/// a limit being active. Limit parameters are attributes of the PhysxTendonAttachmentLeafAPI.

class PhysxSchemaPhysxTendonAttachmentRootAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxTendonAttachmentRootAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxTendonAttachmentRootAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxTendon:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxTendonAttachmentRootAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxTendonAttachmentRootAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxTendonAttachmentRootAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxTendonAttachmentRootAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxTendonAttachmentRootAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

    /// Returns the name of this multiple-apply schema instance
    TfToken GetName() const
    {
        return _GetInstanceName();
    }

    /// Applies this <b>multiple-apply</b> API schema to the given @p prim
    /// along with the given instance name, @p name.
    ///
    /// This information is stored by adding "PhysxTendonAttachmentRootAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxTendonAttachmentRootAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxTendonAttachmentRootAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxTendonAttachmentRootAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxTendonAttachmentRootAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxTendonAttachmentRootAPI>(name))
        {
            return PhysxSchemaPhysxTendonAttachmentRootAPI(prim, name);
        }
        return PhysxSchemaPhysxTendonAttachmentRootAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // TENDONENABLED
    // --------------------------------------------------------------------- //
    /// Enables/disables the tendon from contributing to the articulation dynamics.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool tendonEnabled = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetTendonEnabledAttr() const;

    /// See GetTendonEnabledAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTendonEnabledAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STIFFNESS
    // --------------------------------------------------------------------- //
    /// Common sub-tendon length spring stiffness.
    /// Range: [0, inf)
    /// Units: force / distance = mass / time / time
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float stiffness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStiffnessAttr() const;

    /// See GetStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DAMPING
    // --------------------------------------------------------------------- //
    /// Common sub-tendon length damping.
    /// Range: [0, inf)
    /// Units: force / distance * time = mass / time
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float damping = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDampingAttr() const;

    /// See GetDampingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDampingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LIMITSTIFFNESS
    // --------------------------------------------------------------------- //
    /// Common sub-tendon length-limit spring stiffness.
    /// Range: [0, inf)
    /// Units: force / distance = mass / time / time
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float limitStiffness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLimitStiffnessAttr() const;

    /// See GetLimitStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLimitStiffnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // OFFSET
    // --------------------------------------------------------------------- //
    /// Common sub-tendon length offset.
    /// Range: (-inf, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float offset = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetOffsetAttr() const;

    /// See GetOffsetAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateOffsetAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxTendonAttachmentRootAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxTendonAttachmentRootAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxTendonAttachmentRootAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxTendonAttachmentRootAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("physxTendon"), instanceName, propName };
    // join (TODO this was SdfPath::JoinIdentifier(identifiers))
    std::string namespaceDelimeter = ":";
    std::string namespacedName = "";
    for (auto& token : identifiers)
    {
        namespacedName += token.GetString();
        if (!(token == *(identifiers.end() - 1)))
        {
            namespacedName += namespaceDelimeter;
        }
    }

    return TfToken(namespacedName);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::GetTendonEnabledAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->tendonEnabled));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::CreateTendonEnabledAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->tendonEnabled),
        SdfValueTypeNames->Bool,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::GetStiffnessAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->stiffness));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::CreateStiffnessAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->stiffness),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::GetDampingAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->damping));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::CreateDampingAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->damping),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::GetLimitStiffnessAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->limitStiffness));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::CreateLimitStiffnessAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->limitStiffness),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::GetOffsetAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->offset));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentRootAPI::CreateOffsetAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentRootAPI(GetName(), PhysxSchemaTokens->offset),
        SdfValueTypeNames->Float,
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
