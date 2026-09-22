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

/// @file forceFieldSchema/physxForceFieldRingAPI.h

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
// PHYSXFORCEFIELDRINGAPI                                                      //
// -------------------------------------------------------------------------- //

/// @class ForceFieldSchemaPhysxForceFieldRingAPI
///
/// A force field that applies forces to rotate rigid bodies around a ring, defined by a
/// normal axis through the center of the ring and radius from that axis. The two sets of coefficients
/// describe the attraction force to the ring and the tangential force that rotated bodies around the ring.
/// The net force on the rigid body is calculated using
/// f_ring = constant + linear * r + inverseSquare / r^2.
/// f_spin = spinConstant + spinLinear * r + spinInverseSquare / r^2.

class ForceFieldSchemaPhysxForceFieldRingAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a ForceFieldSchemaPhysxForceFieldRingAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// ForceFieldSchemaPhysxForceFieldRingAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxForceField:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit ForceFieldSchemaPhysxForceFieldRingAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a ForceFieldSchemaPhysxForceFieldRingAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// ForceFieldSchemaPhysxForceFieldRingAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit ForceFieldSchemaPhysxForceFieldRingAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~ForceFieldSchemaPhysxForceFieldRingAPI()
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
    /// This information is stored by adding "PhysxForceFieldRingAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxForceFieldRingAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid ForceFieldSchemaPhysxForceFieldRingAPI object is returned upon success.
    /// An invalid (or empty) ForceFieldSchemaPhysxForceFieldRingAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static ForceFieldSchemaPhysxForceFieldRingAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<ForceFieldSchemaPhysxForceFieldRingAPI>(name))
        {
            return ForceFieldSchemaPhysxForceFieldRingAPI(prim, name);
        }
        return ForceFieldSchemaPhysxForceFieldRingAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // NORMALAXIS
    // --------------------------------------------------------------------- //
    /// The normal axis through the center of the ring in world coordinates.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f physxForceFieldRing:normalAxis = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3f |

    UsdAttribute GetNormalAxisAttr() const;

    /// See GetNormalAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNormalAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RADIUS
    // --------------------------------------------------------------------- //
    /// The distance from the normal axis to the center of the ring.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldRing:radius = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRadiusAttr() const;

    /// See GetRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRadiusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CONSTANT
    // --------------------------------------------------------------------- //
    /// constant applies a steady force that attracts bodies toward the ring.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldRing:constant = 0` |
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
    /// linear applies a force that attracts bodies toward the ring and varies with distance to the ring.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldRing:linear = 0` |
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
    /// inverseSquare applies a force that attracts bodies toward the ring and varies with the reciprocal of the square
    /// of the distance to the ring.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldRing:inverseSquare = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetInverseSquareAttr() const;

    /// See GetInverseSquareAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInverseSquareAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPINCONSTANT
    // --------------------------------------------------------------------- //
    /// spinConstant applies a steady force that rotates bodies around the ring.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldRing:spinConstant = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpinConstantAttr() const;

    /// See GetSpinConstantAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpinConstantAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPINLINEAR
    // --------------------------------------------------------------------- //
    /// spinLinear applies a force that rotates bodies around the ring and varies with distance to the ring.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldRing:spinLinear = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpinLinearAttr() const;

    /// See GetSpinLinearAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpinLinearAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPININVERSESQUARE
    // --------------------------------------------------------------------- //
    /// inverseSquare sets a force that rotates bodies around the ring and varies with the reciprocal of the square of
    /// the distance to the ring.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physxForceFieldRing:spinInverseSquare = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpinInverseSquareAttr() const;

    /// See GetSpinInverseSquareAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpinInverseSquareAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken ForceFieldSchemaPhysxForceFieldRingAPI::_GetStaticTfType()
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldRingAPI");
    return token;
}

/* virtual */
inline const TfToken ForceFieldSchemaPhysxForceFieldRingAPI::_GetTfTypeToken() const
{
    const static TfToken token("ForceFieldSchemaPhysxForceFieldRingAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxForceFieldRingAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetNormalAxisAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldRingNormalAxis));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateNormalAxisAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldRingNormalAxis),
                                     SdfValueTypeNames->Vector3f,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetRadiusAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldRingAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldRingRadius));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateRadiusAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldRingAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldRingRadius),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetConstantAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldRingConstant));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateConstantAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldRingAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldRingConstant),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetLinearAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldRingAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldRingLinear));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateLinearAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxForceFieldRingAPI(GetName(), ForceFieldSchemaTokens->physxForceFieldRingLinear),
        SdfValueTypeNames->Float,
        /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetInverseSquareAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldRingInverseSquare));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateInverseSquareAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldRingInverseSquare),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetSpinConstantAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldRingSpinConstant));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateSpinConstantAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldRingSpinConstant),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetSpinLinearAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldRingSpinLinear));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateSpinLinearAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldRingSpinLinear),
                                     SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::GetSpinInverseSquareAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
        GetName(), ForceFieldSchemaTokens->physxForceFieldRingSpinInverseSquare));
}

inline UsdAttribute ForceFieldSchemaPhysxForceFieldRingAPI::CreateSpinInverseSquareAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxForceFieldRingAPI(
                                         GetName(), ForceFieldSchemaTokens->physxForceFieldRingSpinInverseSquare),
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
