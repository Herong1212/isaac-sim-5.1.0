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

/// @file physxSchema/physxTendonAxisAPI.h

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
// PHYSXTENDONAXISAPI                                                          //
// -------------------------------------------------------------------------- //

/// @class PhysxSchemaPhysxTendonAxisAPI
///
/// WARNING: Draft API, this design is not fixed and may change in the future. At this point, we don't support
/// multi-axis joints (e.g. spherical, D6).
///
/// Applied to a Physics Joint that must be part of an articulation, e.g. PhysicsRevoluteJoint or PhysicsPrismaticJoint.
///
/// A tendon axis is part of a fixed tendon and contributes to the tendon length via the position of its associated
/// articulation joint axis and the gearing attribute. The tendon applies spring-damper forces to the articulation
/// links, scaled by the force coefficient, that aim to maintain constraints on the tendon lengths.
///
/// A joint may have multiple tendon axes that belong to distinct fixed tendons; therefore, the fixed-tendon APIs are
/// multi-apply and are grouped into tendons by their instance names.
///
/// Fixed tendons do not allow linking arbitrary joint axes of the articulation: The respective joints must all be
/// directly connected to each other in the articulation structure, i.e. each of the joints in the tendon must be
/// connected by a single articulation link to another joint in the same tendon. This implies that fixed tendons can
/// branch along with a branching articulation as well. In addition, the root tendon axis created by applying the
/// PhysxTendonAxisRootAPI must be applied to the articulation joint that is the common ancestor of all joint
/// axes in the fixed tendon.
///
/// In a future version, it will be possible to include multiple axes of a multi-axis joint (e.g. a spherical joint)
/// in the fixed tendon by adding them to the axis token array, and setting their gearing and forceCoefficient
/// accordingly in the respective float arrays (in the same order). Until then, the jointAxis token array is ignored,
/// and only the first element of the gearing array is considered.
///

class PhysxSchemaPhysxTendonAxisAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::MultipleApplyAPI;

    /// Construct a PhysxSchemaPhysxTendonAxisAPI on UsdPrim @p prim with
    /// name @p name . Equivalent to
    /// PhysxSchemaPhysxTendonAxisAPI::Get(
    ///    prim.GetStage(),
    ///    prim.GetPath().AppendProperty(
    ///        "physxTendon:name"));
    ///
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit PhysxSchemaPhysxTendonAxisAPI(const UsdPrim& prim = UsdPrim(), const TfToken& name = TfToken())
        : UsdAPISchemaBase(prim, /*instanceName*/ name)
    {
    }

    /// Construct a PhysxSchemaPhysxTendonAxisAPI on the prim held by @p schemaObj with
    /// name @p name .  Should be preferred over
    /// PhysxSchemaPhysxTendonAxisAPI(schemaObj.GetPrim(), name), as it preserves
    /// SchemaBase state.
    explicit PhysxSchemaPhysxTendonAxisAPI(const UsdSchemaBase& schemaObj, const TfToken& name)
        : UsdAPISchemaBase(schemaObj, /*instanceName*/ name)
    {
    }

    /// Destructor.
    virtual ~PhysxSchemaPhysxTendonAxisAPI()
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
    /// This information is stored by adding "PhysxTendonAxisAPI:<i>name</i>"
    /// to the token-valued, listOp metadata \em apiSchemas on the prim.
    /// For example, if @p name is 'instance1', the token
    /// 'PhysxTendonAxisAPI:instance1' is added to 'apiSchemas'.
    ///
    /// @return A valid PhysxSchemaPhysxTendonAxisAPI object is returned upon success.
    /// An invalid (or empty) PhysxSchemaPhysxTendonAxisAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for
    /// conditions resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static PhysxSchemaPhysxTendonAxisAPI Apply(const UsdPrim& prim, const TfToken& name)
    {
        if (prim.ApplyAPI<PhysxSchemaPhysxTendonAxisAPI>(name))
        {
            return PhysxSchemaPhysxTendonAxisAPI(prim, name);
        }
        return PhysxSchemaPhysxTendonAxisAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // GEARING
    // --------------------------------------------------------------------- //
    /// Joint gearing(s) per joint axis in axis token array, in the same order.
    /// Range: (-inf, inf)
    /// Units: translational axis: unitless
    /// rotational axis:    distance/degrees
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] gearing = [1]` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetGearingAttr() const;

    /// See GetGearingAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGearingAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FORCECOEFFICIENT
    // --------------------------------------------------------------------- //
    /// Joint force coefficient(s) per joint axis in axis token array, in the same order.
    /// Range: (-inf, inf)
    /// Units: translational axis: unitless
    /// rotational axis:    distance
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] forceCoefficient = [1]` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetForceCoefficientAttr() const;

    /// See GetForceCoefficientAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateForceCoefficientAttr() const;

public:
    // --------------------------------------------------------------------- //
    // JOINTAXIS
    // --------------------------------------------------------------------- //
    /// Specifies target joint axis/axes. Ignored when the joint only has a single axis, e.g. a revolute joint.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] jointAxis` |
    /// | C++ Type | VtArray<TfToken> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TokenArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref PhysxSchemaTokens "Allowed Values" | transX, transY, transZ, rotX, rotY, rotZ |

    UsdAttribute GetJointAxisAttr() const;

    /// See GetJointAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateJointAxisAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken PhysxSchemaPhysxTendonAxisAPI::_GetStaticTfType()
{
    const static TfToken token("PhysxSchemaPhysxTendonAxisAPI");
    return token;
}

/* virtual */
inline const TfToken PhysxSchemaPhysxTendonAxisAPI::_GetTfTypeToken() const
{
    const static TfToken token("PhysxSchemaPhysxTendonAxisAPI");
    return token;
}


/// @private
/// Returns the property name prefixed with the correct namespace prefix, which
/// is composed of the the API's propertyNamespacePrefix metadata and the
/// instance name of the API.
inline TfToken _GetNamespacedPropertyNamePhysxTendonAxisAPI(const TfToken instanceName, const TfToken propName)
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

inline UsdAttribute PhysxSchemaPhysxTendonAxisAPI::GetGearingAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxTendonAxisAPI(GetName(), PhysxSchemaTokens->gearing));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisAPI::CreateGearingAttr() const
{
    return GetPrim().CreateAttribute(_GetNamespacedPropertyNamePhysxTendonAxisAPI(GetName(), PhysxSchemaTokens->gearing),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisAPI::GetForceCoefficientAttr() const
{

    return GetPrim().GetAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisAPI(GetName(), PhysxSchemaTokens->forceCoefficient));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisAPI::CreateForceCoefficientAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisAPI(GetName(), PhysxSchemaTokens->forceCoefficient),
        SdfValueTypeNames->FloatArray,
        /* custom = */ false);
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisAPI::GetJointAxisAttr() const
{

    return GetPrim().GetAttribute(_GetNamespacedPropertyNamePhysxTendonAxisAPI(GetName(), PhysxSchemaTokens->jointAxis));
}

inline UsdAttribute PhysxSchemaPhysxTendonAxisAPI::CreateJointAxisAttr() const
{
    return GetPrim().CreateAttribute(
        _GetNamespacedPropertyNamePhysxTendonAxisAPI(GetName(), PhysxSchemaTokens->jointAxis),
        SdfValueTypeNames->TokenArray,
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
