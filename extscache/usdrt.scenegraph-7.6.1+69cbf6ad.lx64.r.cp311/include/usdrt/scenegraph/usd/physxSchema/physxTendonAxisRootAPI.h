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

/// @file physxSchema/physxTendonAxisRootAPI.h

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
// PHYSXTENDONAXISROOTAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxTendonAxisRootAPI
///
/// WARNING: Draft API, this design is not fixed and may change in the future. At this point, we don't support
/// multi-axis joints (e.g. spherical, D6) yet.
///
/// Applied to a Physics Joint that must be part of an articulation, e.g. PhysicsRevoluteJoint or PhysicsPrismaticJoint.
///
/// In addition to creating a regular axis of the fixed tendon, the root API provides attributes that apply to the
/// entire tendon. The root API must be applied to the joint that is the common ancestor of all joint axes in the
/// tendon.
///
/// For restrictions on tendon structure and grouping of axes into tendons, see PhysxTendonAxisAPI.
///

class PhysxSchemaPhysxTendonAxisRootAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxTendonAxisRootAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxTendonAxisRootAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxTendon:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxTendonAxisRootAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxTendonAxisRootAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxTendonAxisRootAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxTendonAxisRootAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxTendonAxisRootAPI()
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
    /// This information is stored by adding "PhysxTendonAxisRootAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxTendonAxisRootAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxTendonAxisRootAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxTendonAxisRootAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxTendonAxisRootAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxTendonAxisRootAPI>(name))
        {
            return PhysxSchemaPhysxTendonAxisRootAPI(prim, name);
        }
        return PhysxSchemaPhysxTendonAxisRootAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // STIFFNESS
    // --------------------------------------------------------------------- //
    /// Tendon length spring stiffness.
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
    /// Tendon length damping.
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
    /// Tendon length-limit spring stiffness.
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
    /// Tendon length offset.
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

public:
    // --------------------------------------------------------------------- //
    // RESTLENGTH
    // --------------------------------------------------------------------- //
    /// Tendon rest length.
    /// Range: (-inf, inf)
    /// Units: distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float restLength = 0` |
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
    /// Tendon length lower limit.
    /// Range: (-inf, upperLimit].
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
    /// Tendon length upper limit.
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

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxTendonAxisRootAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxTendonAxisRootAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxTendonAxisRootAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxTendonAxisRootAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetStiffnessAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->stiffness));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateStiffnessAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->stiffness),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetDampingAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->damping));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateDampingAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->damping), SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetLimitStiffnessAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->limitStiffness));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateLimitStiffnessAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->limitStiffness),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetOffsetAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->offset));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateOffsetAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->offset), SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetRestLengthAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->restLength));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateRestLengthAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->restLength),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetLowerLimitAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->lowerLimit));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateLowerLimitAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->lowerLimit),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetUpperLimitAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->upperLimit));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateUpperLimitAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->upperLimit),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::GetTendonEnabledAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->tendonEnabled));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisRootAPI::CreateTendonEnabledAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisRootAPI(GetName(), PhysxSchemaTokens->tendonEnabled),
        SdfValueTypeNames->Bool,
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
