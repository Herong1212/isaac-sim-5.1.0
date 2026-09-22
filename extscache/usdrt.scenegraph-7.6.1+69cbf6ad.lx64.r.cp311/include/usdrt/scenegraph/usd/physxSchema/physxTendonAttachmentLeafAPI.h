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

/// @file physxSchema/physxTendonAttachmentLeafAPI.h

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
// PHYSXTENDONATTACHMENTLEAFAPI                                                //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxTendonAttachmentLeafAPI
///
/// WARNING: Draft API, this design is not fixed and may change in the future.
///
/// Applied to an articulation-link rigid-body Xformable.
///
/// The leaf API creates a new sub-tendon between the leaf and the root attachment. A leaf cannot have any children,
/// i.e. there cannot be another attachment API that refers to a leaf as parent.

class PhysxSchemaPhysxTendonAttachmentLeafAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxTendonAttachmentLeafAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxTendonAttachmentLeafAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxTendon:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxTendonAttachmentLeafAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxTendonAttachmentLeafAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxTendonAttachmentLeafAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxTendonAttachmentLeafAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxTendonAttachmentLeafAPI()
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
    /// This information is stored by adding "PhysxTendonAttachmentLeafAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxTendonAttachmentLeafAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxTendonAttachmentLeafAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxTendonAttachmentLeafAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxTendonAttachmentLeafAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxTendonAttachmentLeafAPI>(name))
        {
            return PhysxSchemaPhysxTendonAttachmentLeafAPI(prim, name);
        }
        return PhysxSchemaPhysxTendonAttachmentLeafAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RESTLENGTH
    // --------------------------------------------------------------------- //
    /// Sub-tendon rest length. If set to a negative value, the rest length is computed internally from the articulation
    /// pose and the attachment positions at simulation start. Range: [0, inf) Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float restLength = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRestLengthAttr() const;

    /// See GetRestLengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestLengthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOWERLIMIT
    // --------------------------------------------------------------------- //
    /// Sub-tendon length lower limit.
    /// Range: (-inf, upperLimit]
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float lowerLimit = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLowerLimitAttr() const;

    /// See GetLowerLimitAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLowerLimitAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UPPERLIMIT
    // --------------------------------------------------------------------- //
    /// Sub-tendon length upper limit.
    /// Range: [lowerLimit, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float upperLimit = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetUpperLimitAttr() const;

    /// See GetUpperLimitAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpperLimitAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxTendonAttachmentLeafAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxTendonAttachmentLeafAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxTendonAttachmentLeafAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxTendonAttachmentLeafAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxTendonAttachmentLeafAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentLeafAPI::GetRestLengthAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentLeafAPI(GetName(), PhysxSchemaTokens->restLength));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentLeafAPI::CreateRestLengthAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentLeafAPI(GetName(), PhysxSchemaTokens->restLength),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentLeafAPI::GetLowerLimitAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentLeafAPI(GetName(), PhysxSchemaTokens->lowerLimit));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentLeafAPI::CreateLowerLimitAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentLeafAPI(GetName(), PhysxSchemaTokens->lowerLimit),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentLeafAPI::GetUpperLimitAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentLeafAPI(GetName(), PhysxSchemaTokens->upperLimit));
}

inline UsdAttribute PhysxSchemaPhysxTendonAttachmentLeafAPI::CreateUpperLimitAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAttachmentLeafAPI(GetName(), PhysxSchemaTokens->upperLimit),
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
