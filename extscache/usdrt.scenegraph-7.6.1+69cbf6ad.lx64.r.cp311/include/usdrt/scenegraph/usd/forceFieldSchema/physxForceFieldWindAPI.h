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

/// @file forceFieldSchema/physxForceFieldWindAPI.h

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
// PHYSXFORCEFIELDWINDAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class ForceFieldSchemaPhysxForceFieldWindAPI
///
/// A force field that simulates an unsteady wind that pushes rigid bodies.

class ForceFieldSchemaPhysxForceFieldWindAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a ForceFieldSchemaPhysxForceFieldWindAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// ForceFieldSchemaPhysxForceFieldWindAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxForceField:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit ForceFieldSchemaPhysxForceFieldWindAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a ForceFieldSchemaPhysxForceFieldWindAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// ForceFieldSchemaPhysxForceFieldWindAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit ForceFieldSchemaPhysxForceFieldWindAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~ForceFieldSchemaPhysxForceFieldWindAPI()
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
    /// This information is stored by adding "PhysxForceFieldWindAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxForceFieldWindAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid ForceFieldSchemaPhysxForceFieldWindAPI object is returned upon success.
    /// An invalid (or empty) ForceFieldSchemaPhysxForceFieldWindAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static ForceFieldSchemaPhysxForceFieldWindAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<ForceFieldSchemaPhysxForceFieldWindAPI>(name))
        {
            return ForceFieldSchemaPhysxForceFieldWindAPI(prim, name);
        }
        return ForceFieldSchemaPhysxForceFieldWindAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DRAG
    // --------------------------------------------------------------------- //
    /// The drag coefficient determines how quickly the body moves along with the wind.
    /// Smaller values cause the body to react more slowly.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldWind:drag = 0` |
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
    // AVERAGESPEED
    // --------------------------------------------------------------------- //
    /// The average speed of the wind. Speed changes are added to this base speed, but
    /// the net speed can never drop below zero.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldWind:averageSpeed = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetAverageSpeedAttr() const;

    /// See GetAverageSpeedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAverageSpeedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // AVERAGEDIRECTION
    // --------------------------------------------------------------------- //
    /// The initial direction of the wind in the world coordinate system. Wind direction
    /// changes are added to this base direciton.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxForceFieldWind:averageDirection = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetAverageDirectionAttr() const;

    /// See GetAverageDirectionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAverageDirectionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPEEDVARIATION
    // --------------------------------------------------------------------- //
    /// The magnitude of the random changes of the wind speed.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldWind:speedVariation = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpeedVariationAttr() const;

    /// See GetSpeedVariationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpeedVariationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPEEDVARIATIONFREQUENCY
    // --------------------------------------------------------------------- //
    /// The frequency of the random changes of the wind speed.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldWind:speedVariationFrequency = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpeedVariationFrequencyAttr() const;

    /// See GetSpeedVariationFrequencyAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpeedVariationFrequencyAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DIRECTIONVARIATION
    // --------------------------------------------------------------------- //
    /// The magnitude of the random changes of the wind direction in the world coordinate system.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxForceFieldWind:directionVariation = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetDirectionVariationAttr() const;

    /// See GetDirectionVariationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDirectionVariationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DIRECTIONVARIATIONFREQUENCY
    // --------------------------------------------------------------------- //
    /// The frequency of the random variations of the wind direction in the world coordinate system.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3 physxForceFieldWind:directionVariationFrequency = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3 |

    UsdAttribute GetDirectionVariationFrequencyAttr() const;

    /// See GetDirectionVariationFrequencyAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDirectionVariationFrequencyAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken ForceFieldSchemaPhysxForceFieldWindAPI::_GetStaticTfType()
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldWindAPI");
    return token;
}

/* virtual */
inline const TfToken ForceFieldSchemaPhysxForceFieldWindAPI::_GetTfTypeToken() const
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldWindAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxForceFieldWindAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::GetDragAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldWindAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldWindDrag));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::CreateDragAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldWindAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldWindDrag),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::GetAverageSpeedAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldWindAverageSpeed));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::CreateAverageSpeedAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldWindAverageSpeed),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::GetAverageDirectionAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldWindAverageDirection));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::CreateAverageDirectionAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldWindAverageDirection),
                                     SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::GetSpeedVariationAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldWindSpeedVariation));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::CreateSpeedVariationAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldWindSpeedVariation),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::GetSpeedVariationFrequencyAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldWindSpeedVariationFrequency));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::CreateSpeedVariationFrequencyAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldWindSpeedVariationFrequency),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::GetDirectionVariationAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldWindDirectionVariation));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::CreateDirectionVariationAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldWindDirectionVariation),
                                     SdfValueTypeNames->Float3,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::GetDirectionVariationFrequencyAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldWindAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldWindDirectionVariationFrequency));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldWindAPI::CreateDirectionVariationFrequencyAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldWindAPI(
            GetName(), ForceFieldSchemaTokens->physxForceFieldWindDirectionVariationFrequency),
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
