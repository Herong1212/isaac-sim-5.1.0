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

/// @file physxSchema/jointStateAPI.h

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
// PHYSICSJOINTSTATEAPI                                                        //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaJointStateAPI
///
/// The PhysicsJointStateAPI is applied to a joint primitive
/// (i.e. any PhysicsJoint-derived type) and provides read/write access
/// to the joint position and velocity for a specific joint axis.
/// The PhysicsJointStateAPI is a multipleApply schema, and its instance name
/// TfToken defines the joint axis: The name can be "transX", "transY", "transZ",
/// "rotX", "rotY", "rotZ" or its "linear" for prismatic joint or "angular"
/// for revolute joints, respectively.

class PhysxSchemaJointStateAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaJointStateAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaJointStateAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "state:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaJointStateAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaJointStateAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaJointStateAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaJointStateAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaJointStateAPI()
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
    /// This information is stored by adding "PhysicsJointStateAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysicsJointStateAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaJointStateAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaJointStateAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaJointStateAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaJointStateAPI>(name))
        {
            return PhysxSchemaJointStateAPI(prim, name);
        }
        return PhysxSchemaJointStateAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // POSITION
    // --------------------------------------------------------------------- //
    /// Joint state position defines the relative difference between
    /// joint body0 frame and joint body1 frame in world frame.
    /// Range: (-inf, inf)
    /// Units: linear - distance
    /// angular - degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:position = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetPositionAttr() const;

    /// See GetPositionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePositionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELOCITY
    // --------------------------------------------------------------------- //
    /// Joint state velocity defines the relative velocity between
    /// joint body0 and joint body1.
    /// Range: (-inf, inf)
    /// Units: linear - distance / seconds
    /// angular - degrees / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:velocity = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetVelocityAttr() const;

    /// See GetVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelocityAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaJointStateAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaJointStateAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaJointStateAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaJointStateAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysicsJointStateAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("state"), instanceName, propName };
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

inline UsdAttribute PhysxSchemaJointStateAPI::GetPositionAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysicsJointStateAPI(GetName(), PhysxSchemaTokens->physicsPosition));
}

inline UsdAttribute PhysxSchemaJointStateAPI::CreatePositionAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysicsJointStateAPI(GetName(), PhysxSchemaTokens->physicsPosition),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaJointStateAPI::GetVelocityAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysicsJointStateAPI(GetName(), PhysxSchemaTokens->physicsVelocity));
}

inline UsdAttribute PhysxSchemaJointStateAPI::CreateVelocityAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysicsJointStateAPI(GetName(), PhysxSchemaTokens->physicsVelocity),
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
