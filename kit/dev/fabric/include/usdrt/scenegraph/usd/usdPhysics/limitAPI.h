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

/// @file usdPhysics/limitAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
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
// PHYSICSLIMITAPI                                                             //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsLimitAPI
///
/// The PhysicsLimitAPI can be applied to a PhysicsJoint and will
/// restrict the movement along an axis. PhysicsLimitAPI is a multipleApply
/// schema: The PhysicsJoint can be restricted along "transX", "transY",
/// "transZ", "rotX", "rotY", "rotZ", "distance". Setting these as a
/// multipleApply schema TfToken name will define the degree of freedom the
/// PhysicsLimitAPI is applied to. Note that if the low limit is higher than
/// the high limit, motion along this axis is considered locked.

class UsdPhysicsLimitAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a UsdPhysicsLimitAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// UsdPhysicsLimitAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "limit:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsLimitAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a UsdPhysicsLimitAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// UsdPhysicsLimitAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit UsdPhysicsLimitAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsLimitAPI()
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
    /// This information is stored by adding "PhysicsLimitAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysicsLimitAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid UsdPhysicsLimitAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsLimitAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsLimitAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<UsdPhysicsLimitAPI>(name))
        {
            return UsdPhysicsLimitAPI(prim, name);
        }
        return UsdPhysicsLimitAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // LOW
    // --------------------------------------------------------------------- //
    /// Lower limit. Units: degrees or distance depending on trans or
    /// rot axis applied to. -inf means not limited in negative direction.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:low = -inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLowAttr() const;

    /// See GetLowAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLowAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HIGH
    // --------------------------------------------------------------------- //
    /// Upper limit. Units: degrees or distance depending on trans or
    /// rot axis applied to. inf means not limited in positive direction.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:high = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetHighAttr() const;

    /// See GetHighAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHighAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsLimitAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsLimitAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsLimitAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsLimitAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysicsLimitAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("limit"), instanceName, propName };
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

inline UsdAttribute UsdPhysicsLimitAPI::GetLowAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysicsLimitAPI(GetName(), UsdPhysicsTokens->physicsLow));
}

inline UsdAttribute UsdPhysicsLimitAPI::CreateLowAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysicsLimitAPI(GetName(), UsdPhysicsTokens->physicsLow),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsLimitAPI::GetHighAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysicsLimitAPI(GetName(), UsdPhysicsTokens->physicsHigh));
}

inline UsdAttribute UsdPhysicsLimitAPI::CreateHighAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysicsLimitAPI(GetName(), UsdPhysicsTokens->physicsHigh),
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
