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

/// @file forceFieldSchema/physxForceFieldSpinAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/forceFieldSchema/tokens.h"


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
// PHYSXFORCEFIELDSPINAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class ForceFieldSchemaPhysxForceFieldSpinAPI
///
/// A force field that applies forces to rotate rigid bodies around a line, defined by a
/// spin axis, and varies with the function coefficients. Positive values rotate
/// clockwise around the spin axis when looking along the axis. The net force on the
/// rigid body is calculated using f = constant + linear * r + inverseSquare / r^2.

class ForceFieldSchemaPhysxForceFieldSpinAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a ForceFieldSchemaPhysxForceFieldSpinAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// ForceFieldSchemaPhysxForceFieldSpinAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxForceField:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit ForceFieldSchemaPhysxForceFieldSpinAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a ForceFieldSchemaPhysxForceFieldSpinAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// ForceFieldSchemaPhysxForceFieldSpinAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit ForceFieldSchemaPhysxForceFieldSpinAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~ForceFieldSchemaPhysxForceFieldSpinAPI()
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
    /// This information is stored by adding "PhysxForceFieldSpinAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxForceFieldSpinAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid ForceFieldSchemaPhysxForceFieldSpinAPI object is returned upon success.
    /// An invalid (or empty) ForceFieldSchemaPhysxForceFieldSpinAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static ForceFieldSchemaPhysxForceFieldSpinAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<ForceFieldSchemaPhysxForceFieldSpinAPI>(name))
        {
            return ForceFieldSchemaPhysxForceFieldSpinAPI(prim, name);
        }
        return ForceFieldSchemaPhysxForceFieldSpinAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SPINAXIS
    // --------------------------------------------------------------------- //
    /// The axis around which rigid bodies are rotated in world coordinates.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxForceFieldSpin:spinAxis = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetSpinAxisAttr() const;

    /// See GetSpinAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpinAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONSTANT
    // --------------------------------------------------------------------- //
    /// constant applies a steady force.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldSpin:constant = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetConstantAttr() const;

    /// See GetConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LINEAR
    // --------------------------------------------------------------------- //
    /// linear sets a force that varies with distance to the axis.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldSpin:linear = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLinearAttr() const;

    /// See GetLinearAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLinearAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INVERSESQUARE
    // --------------------------------------------------------------------- //
    /// inverseSquare sets a force that varies with the reciprocal of the square of the distance to the axis.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldSpin:inverseSquare = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetInverseSquareAttr() const;

    /// See GetInverseSquareAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInverseSquareAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken ForceFieldSchemaPhysxForceFieldSpinAPI::_GetStaticTfType()
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldSpinAPI");
    return token;
}

/* virtual */
inline const TfToken ForceFieldSchemaPhysxForceFieldSpinAPI::_GetTfTypeToken() const
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldSpinAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxForceFieldSpinAPI(const TfToken instanceName, const TfToken propName)
{
    std::vector<TfToken> identifiers = { TfToken("physxForceField"), instanceName, propName };
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

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::GetSpinAxisAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldSpinAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldSpinSpinAxis));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::CreateSpinAxisAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldSpinAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldSpinSpinAxis),
        SdfValueTypeNames->Vector3f,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::GetConstantAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldSpinAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldSpinConstant));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::CreateConstantAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldSpinAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldSpinConstant),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::GetLinearAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldSpinAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldSpinLinear));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::CreateLinearAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldSpinAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldSpinLinear),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::GetInverseSquareAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldSpinAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldSpinInverseSquare));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldSpinAPI::CreateInverseSquareAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldSpinAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldSpinInverseSquare),
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
