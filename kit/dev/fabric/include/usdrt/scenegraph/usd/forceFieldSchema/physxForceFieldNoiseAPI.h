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

/// @file forceFieldSchema/physxForceFieldNoiseAPI.h

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
// PHYSXFORCEFIELDNOISEAPI                                                     //
// -------------------------------------------------------------------------- //

/// @class ForceFieldSchemaPhysxForceFieldNoiseAPI
///
/// A force field that adds randomized motion to a rigid body.

class ForceFieldSchemaPhysxForceFieldNoiseAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a ForceFieldSchemaPhysxForceFieldNoiseAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// ForceFieldSchemaPhysxForceFieldNoiseAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxForceField:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit ForceFieldSchemaPhysxForceFieldNoiseAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a ForceFieldSchemaPhysxForceFieldNoiseAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// ForceFieldSchemaPhysxForceFieldNoiseAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit ForceFieldSchemaPhysxForceFieldNoiseAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~ForceFieldSchemaPhysxForceFieldNoiseAPI()
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
    /// This information is stored by adding "PhysxForceFieldNoiseAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxForceFieldNoiseAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid ForceFieldSchemaPhysxForceFieldNoiseAPI object is returned upon success.
    /// An invalid (or empty) ForceFieldSchemaPhysxForceFieldNoiseAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static ForceFieldSchemaPhysxForceFieldNoiseAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<ForceFieldSchemaPhysxForceFieldNoiseAPI>(name))
        {
            return ForceFieldSchemaPhysxForceFieldNoiseAPI(prim, name);
        }
        return ForceFieldSchemaPhysxForceFieldNoiseAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DRAG
    // --------------------------------------------------------------------- //
    /// The drag coefficient determines how quickly the body moves along with the noise.
    /// Smaller values cause the body to react more slowly.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldNoise:drag = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDragAttr() const;

    /// See GetDragAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDragAttr() const;

public:
    // --------------------------------------------------------------------- //
    // AMPLITUDE
    // --------------------------------------------------------------------- //
    /// The magnitude of the oscillations along each of the three local axes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxForceFieldNoise:amplitude = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetAmplitudeAttr() const;

    /// See GetAmplitudeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAmplitudeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FREQUENCY
    // --------------------------------------------------------------------- //
    /// The frequency of the oscillations for each of the three local axes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxForceFieldNoise:frequency = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetFrequencyAttr() const;

    /// See GetFrequencyAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFrequencyAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken ForceFieldSchemaPhysxForceFieldNoiseAPI::_GetStaticTfType()
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldNoiseAPI");
    return token;
}

/* virtual */
inline const TfToken ForceFieldSchemaPhysxForceFieldNoiseAPI::_GetTfTypeToken() const
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldNoiseAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxForceFieldNoiseAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute ForceFieldSchemaPhysxForceFieldNoiseAPI::GetDragAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldNoiseAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldNoiseDrag));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldNoiseAPI::CreateDragAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldNoiseAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldNoiseDrag),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldNoiseAPI::GetAmplitudeAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldNoiseAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldNoiseAmplitude));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldNoiseAPI::CreateAmplitudeAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldNoiseAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldNoiseAmplitude),
                                     SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldNoiseAPI::GetFrequencyAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldNoiseAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldNoiseFrequency));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldNoiseAPI::CreateFrequencyAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldNoiseAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldNoiseFrequency),
                                     SdfValueTypeNames->Float3,
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
