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

/// @file physxSchema/physxTendonAttachmentAPI.h

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
// PHYSXTENDONATTACHMENTAPI                                                    //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxTendonAttachmentAPI
///
/// WARNING: Draft API, this design is not fixed and may change in the future.
///
/// Applied to an articulation-link rigid-body Xformable.
///
/// A tendon attachment is part of a spatial tendon and is attached to an articulation link. The distance between the
/// attachment and its parent attachment contributes to the length of the tendon, after scaling by the gearing
/// attribute.
///
/// The localPos attribute defines the translational offset of the attachment in the link's local frame; in particular,
/// this means that the offset is scaled together with any scaling applied to the link.
///
/// An articulation link may have multiple distinct attachments that belong to the same or distinct spatial tendons;
/// therefore, the spatial tendon APIs are multi-apply and each attachment must have a unique instance name that is
/// used in parent-child relationships of the attachments.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref PhysxSchemaTokens.
/// So to set an attribute to the value "rightHanded", use PhysxSchemaTokens->rightHanded
/// as the value.

class PhysxSchemaPhysxTendonAttachmentAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxTendonAttachmentAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxTendonAttachmentAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxTendon:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxTendonAttachmentAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxTendonAttachmentAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxTendonAttachmentAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxTendonAttachmentAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxTendonAttachmentAPI()
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
    /// This information is stored by adding "PhysxTendonAttachmentAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxTendonAttachmentAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxTendonAttachmentAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxTendonAttachmentAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxTendonAttachmentAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxTendonAttachmentAPI>(name))
        {
            return PhysxSchemaPhysxTendonAttachmentAPI(prim, name);
        }
        return PhysxSchemaPhysxTendonAttachmentAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // GEARING
    // --------------------------------------------------------------------- //
    /// Attachment distance scaling factor.
    /// Range: (-inf, inf)
    /// Units: unitless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float gearing = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGearingAttr() const;

    /// See GetGearingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGearingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOCALPOS
    // --------------------------------------------------------------------- //
    /// Location of the attachment. Only considered if API is applied to an articulation link (i.e. with a
    /// PhysicsRigidBodyAPI). Units: (local-frame) distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f localPos = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3f |

    UsdAttribute GetLocalPosAttr() const;

    /// See GetLocalPosAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLocalPosAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARENTATTACHMENT
    // --------------------------------------------------------------------- //
    /// API instance name of parent attachment at parentLink.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token parentAttachment` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetParentAttachmentAttr() const;

    /// See GetParentAttachmentAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateParentAttachmentAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PARENTLINK
    // --------------------------------------------------------------------- //
    /// Relationship to parent link that has a PhysxTendonAttachmentAPI or PhysxTendonAttachmentRootAPI with instance
    /// name parentAttachment applied.
    ///
    UsdRelationship GetParentLinkRel() const;

    /// See GetParentLinkRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateParentLinkRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxTendonAttachmentAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxTendonAttachmentAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxTendonAttachmentAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxTendonAttachmentAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentAPI::GetGearingAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->gearing));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentAPI::CreateGearingAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->gearing),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentAPI::GetLocalPosAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->localPos));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentAPI::CreateLocalPosAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->localPos),
        SdfValueTypeNames->Point3f,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentAPI::GetParentAttachmentAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->parentAttachment));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentAPI::CreateParentAttachmentAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->parentAttachment),
        SdfValueTypeNames->Token,
        /* custom = */ false);
}


inline UsdRelationship PhysxSchemaPhysxTendonAttachmentAPI::GetParentLinkRel() const
{
    return GetPrim().GetRelationship(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->parentLink));
}

inline UsdRelationship PhysxSchemaPhysxTendonAttachmentAPI::CreateParentLinkRel() const
{
    return GetPrim().CreateRelationship(
        _GetNamespacedPropertyNamePhysxTendonAttachmentAPI(GetName(), PhysxSchemaTokens->parentLink),
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
