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

/// @file physxSchema/physxLimitAPI.h

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
// PHYSXLIMITAPI                                                               //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxLimitAPI
///

class PhysxSchemaPhysxLimitAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxLimitAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxLimitAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxLimit:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxLimitAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxLimitAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxLimitAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxLimitAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxLimitAPI()
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
    /// This information is stored by adding "PhysxLimitAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxLimitAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxLimitAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxLimitAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxLimitAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxLimitAPI>(name))
        {
            return PhysxSchemaPhysxLimitAPI(prim, name);
        }
        return PhysxSchemaPhysxLimitAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RESTITUTION
    // --------------------------------------------------------------------- //
    /// Controls the amount of bounce when the joint hits a limit.
    /// Range: [0, inf)
    /// Units: dimensionless
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float restitution = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRestitutionAttr() const;

    /// See GetRestitutionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestitutionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BOUNCETHRESHOLD
    // --------------------------------------------------------------------- //
    /// Determines the minimum impact velocity which will cause the joint to bounce.
    /// Range: [0, inf)
    /// Units: linear - distance / seconds
    /// angular - degrees / seconds
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float bounceThreshold = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetBounceThresholdAttr() const;

    /// See GetBounceThresholdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBounceThresholdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // STIFFNESS
    // --------------------------------------------------------------------- //
    /// If greater than zero, the limit is soft, i.e. a spring pulls the joint back to the limit.
    /// Range: [0, inf)
    /// Units: linear - force / distance
    /// angular - torque / degrees
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
    /// If spring is greater than zero, this is the damping of the limit spring.
    /// Range: [0, inf)
    /// Units: linear - force / distance * seconds
    /// angular - torque / degrees * seconds
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
    // CONTACTDISTANCE
    // --------------------------------------------------------------------- //
    /// The distance inside the limit value at which the limit will be considered to be active by the solver.
    /// As this value is made larger, the limit becomes active more quickly. It thus becomes less likely to violate
    /// the extents of the limit, but more expensive.
    /// Range: [0, inf)
    /// Units: linear - distance
    /// angular - degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float contactDistance = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetContactDistanceAttr() const;

    /// See GetContactDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateContactDistanceAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxLimitAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxLimitAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxLimitAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxLimitAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxLimitAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("physxLimit"), instanceName, propName };
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

inline UsdAttribute PhysxSchemaPhysxLimitAPI::GetRestitutionAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->restitution));
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::CreateRestitutionAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->restitution),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::GetBounceThresholdAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->bounceThreshold));
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::CreateBounceThresholdAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->bounceThreshold), SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::GetStiffnessAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->stiffness));
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::CreateStiffnessAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->stiffness),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::GetDampingAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->damping));
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::CreateDampingAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->damping),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::GetContactDistanceAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->contactDistance));
}

inline UsdAttribute PhysxSchemaPhysxLimitAPI::CreateContactDistanceAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxLimitAPI(GetName(), PhysxSchemaTokens->contactDistance), SdfValueTypeNames->Float,
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
