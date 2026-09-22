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

/// @file forceFieldSchema/physxForceFieldDragAPI.h

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
// PHYSXFORCEFIELDDRAGAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class ForceFieldSchemaPhysxForceFieldDragAPI
///
/// A force field that slows rigid bodies by generating a force that is opposite to their velocity direction
/// using the forumula f = -linear * v - square * v^2.

class ForceFieldSchemaPhysxForceFieldDragAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a ForceFieldSchemaPhysxForceFieldDragAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// ForceFieldSchemaPhysxForceFieldDragAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxForceField:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit ForceFieldSchemaPhysxForceFieldDragAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a ForceFieldSchemaPhysxForceFieldDragAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// ForceFieldSchemaPhysxForceFieldDragAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit ForceFieldSchemaPhysxForceFieldDragAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~ForceFieldSchemaPhysxForceFieldDragAPI()
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
    /// This information is stored by adding "PhysxForceFieldDragAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxForceFieldDragAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid ForceFieldSchemaPhysxForceFieldDragAPI object is returned upon success.
    /// An invalid (or empty) ForceFieldSchemaPhysxForceFieldDragAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static ForceFieldSchemaPhysxForceFieldDragAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<ForceFieldSchemaPhysxForceFieldDragAPI>(name))
        {
            return ForceFieldSchemaPhysxForceFieldDragAPI(prim, name);
        }
        return ForceFieldSchemaPhysxForceFieldDragAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MINIMUMSPEED
    // --------------------------------------------------------------------- //
    /// Drag forces are not applied below this minimum speed.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldDrag:minimumSpeed = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinimumSpeedAttr() const;

    /// See GetMinimumSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinimumSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LINEAR
    // --------------------------------------------------------------------- //
    /// linear sets a force that varies proportionally with the speed of the rigid body.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldDrag:linear = 0` |
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
    // SQUARE
    // --------------------------------------------------------------------- //
    /// square computes a force the varies with the square of the speed of the rigid body.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldDrag:square = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSquareAttr() const;

    /// See GetSquareAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSquareAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken ForceFieldSchemaPhysxForceFieldDragAPI::_GetStaticTfType()
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldDragAPI");
    return token;
}

/* virtual */
inline const TfToken ForceFieldSchemaPhysxForceFieldDragAPI::_GetTfTypeToken() const
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldDragAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxForceFieldDragAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute ForceFieldSchemaPhysxForceFieldDragAPI::GetMinimumSpeedAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldDragAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldDragMinimumSpeed));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldDragAPI::CreateMinimumSpeedAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldDragAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldDragMinimumSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldDragAPI::GetLinearAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldDragAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldDragLinear));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldDragAPI::CreateLinearAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldDragAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldDragLinear),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldDragAPI::GetSquareAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldDragAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldDragSquare));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldDragAPI::CreateSquareAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldDragAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldDragSquare),
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
