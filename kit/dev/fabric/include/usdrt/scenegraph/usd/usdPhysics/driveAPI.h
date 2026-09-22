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

/// @file usdPhysics/driveAPI.h

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
// PHYSICSDRIVEAPI                                                             //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsDriveAPI
///
/// The PhysicsDriveAPI when applied to any joint primitive will drive
/// the joint towards a given target. The PhysicsDriveAPI is a multipleApply
/// schema: drive can be set per axis "transX", "transY", "transZ", "rotX",
/// "rotY", "rotZ" or its "linear" for prismatic joint or "angular" for revolute
/// joints. Setting these as a multipleApply schema TfToken name will
/// define the degree of freedom the DriveAPI is applied to. Each drive is an
/// implicit force-limited damped spring:
/// Force or acceleration = stiffness * (targetPosition - position)
/// + damping * (targetVelocity - velocity)
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdPhysicsTokens.
/// So to set an attribute to the value "rightHanded", use UsdPhysicsTokens->rightHanded
/// as the value.

class UsdPhysicsDriveAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a UsdPhysicsDriveAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// UsdPhysicsDriveAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "drive:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsDriveAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a UsdPhysicsDriveAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// UsdPhysicsDriveAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit UsdPhysicsDriveAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsDriveAPI()
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
    /// This information is stored by adding "PhysicsDriveAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysicsDriveAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid UsdPhysicsDriveAPI object is returned upon success.
    /// An invalid (or empty) UsdPhysicsDriveAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdPhysicsDriveAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<UsdPhysicsDriveAPI>(name))
        {
            return UsdPhysicsDriveAPI(prim, name);
        }
        return UsdPhysicsDriveAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // TYPE
    // --------------------------------------------------------------------- //
    /// Drive spring is for the acceleration at the joint (rather
    /// than the force).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physics:type = "force"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdPhysicsTokens "Allowed Values" | force, acceleration |

    UsdAttribute GetTypeAttr() const;

    /// See GetTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXFORCE
    // --------------------------------------------------------------------- //
    /// Maximum force that can be applied to drive. Units:
    /// if linear drive: mass*DIST_UNITS/second/second
    /// if angular drive: mass*DIST_UNITS*DIST_UNITS/second/second
    /// inf means not limited. Must be non-negative.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:maxForce = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxForceAttr() const;

    /// See GetMaxForceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxForceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TARGETPOSITION
    // --------------------------------------------------------------------- //
    /// Target value for position. Units:
    /// if linear drive: distance
    /// if angular drive: degrees.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:targetPosition = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetTargetPositionAttr() const;

    /// See GetTargetPositionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTargetPositionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TARGETVELOCITY
    // --------------------------------------------------------------------- //
    /// Target value for velocity. Units:
    /// if linear drive: distance/second
    /// if angular drive: degrees/second.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:targetVelocity = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetTargetVelocityAttr() const;

    /// See GetTargetVelocityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTargetVelocityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DAMPING
    // --------------------------------------------------------------------- //
    /// Damping of the drive. Units:
    /// if linear drive: mass/second
    /// If angular drive: mass*DIST_UNITS*DIST_UNITS/second/second/degrees.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:damping = 0` |
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
    // STIFFNESS
    // --------------------------------------------------------------------- //
    /// Stiffness of the drive. Units:
    /// if linear drive: mass/second/second
    /// if angular drive: mass*DIST_UNITS*DIST_UNITS/degree/second/second.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:stiffness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetStiffnessAttr() const;

    /// See GetStiffnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateStiffnessAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsDriveAPI::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsDriveAPI");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsDriveAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsDriveAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysicsDriveAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("drive"), instanceName, propName };
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

inline UsdAttribute UsdPhysicsDriveAPI::GetTypeAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsType));
}

inline UsdAttribute UsdPhysicsDriveAPI::CreateTypeAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsType),
                                     SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsDriveAPI::GetMaxForceAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsMaxForce));
}

inline UsdAttribute UsdPhysicsDriveAPI::CreateMaxForceAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsMaxForce), SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute UsdPhysicsDriveAPI::GetTargetPositionAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsTargetPosition));
}

inline UsdAttribute UsdPhysicsDriveAPI::CreateTargetPositionAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsTargetPosition),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute UsdPhysicsDriveAPI::GetTargetVelocityAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsTargetVelocity));
}

inline UsdAttribute UsdPhysicsDriveAPI::CreateTargetVelocityAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsTargetVelocity),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute UsdPhysicsDriveAPI::GetDampingAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsDamping));
}

inline UsdAttribute UsdPhysicsDriveAPI::CreateDampingAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsDamping), SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute UsdPhysicsDriveAPI::GetStiffnessAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsStiffness));
}

inline UsdAttribute UsdPhysicsDriveAPI::CreateStiffnessAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysicsDriveAPI(GetName(), UsdPhysicsTokens->physicsStiffness),
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
