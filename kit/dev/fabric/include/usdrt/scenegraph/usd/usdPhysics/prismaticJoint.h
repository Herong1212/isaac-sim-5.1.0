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

/// @file usdPhysics/prismaticJoint.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdPhysics/joint.h"
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
// PHYSICSPRISMATICJOINT                                                       //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsPrismaticJoint
///
/// Predefined prismatic joint type (translation along prismatic
/// joint axis is permitted.)
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdPhysicsTokens.
/// So to set an attribute to the value "rightHanded", use UsdPhysicsTokens->rightHanded
/// as the value.

class UsdPhysicsPrismaticJoint : public UsdPhysicsJoint
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdPhysicsPrismaticJoint on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsPrismaticJoint::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsPrismaticJoint(const UsdPrim& prim = UsdPrim()) : UsdPhysicsJoint(prim)
    {
    }

    /// Construct a UsdPhysicsPrismaticJoint on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsPrismaticJoint(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsPrismaticJoint(const UsdSchemaBase& schemaObj) : UsdPhysicsJoint(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsPrismaticJoint()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdPhysicsPrismaticJoint Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // AXIS
    // --------------------------------------------------------------------- //
    /// Joint axis.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token physics:axis = "X"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdPhysicsTokens "Allowed Values" | X, Y, Z |

    UsdAttribute GetAxisAttr() const;

    /// See GetAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LOWERLIMIT
    // --------------------------------------------------------------------- //
    /// Lower limit. Units: distance. -inf means not limited in
    /// negative direction.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:lowerLimit = -inf` |
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
    /// Upper limit. Units: distance. inf means not limited in
    /// positive direction.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:upperLimit = inf` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetUpperLimitAttr() const;

    /// See GetUpperLimitAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUpperLimitAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsPrismaticJoint::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsPrismaticJoint");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsPrismaticJoint::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsPrismaticJoint");
    return token;
}

/* static */
inline UsdPhysicsPrismaticJoint UsdPhysicsPrismaticJoint::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdPhysicsPrismaticJoint();
    }
    return UsdPhysicsPrismaticJoint(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdPhysicsPrismaticJoint::GetAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsAxis));
}

inline UsdAttribute UsdPhysicsPrismaticJoint::CreateAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsAxis), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsPrismaticJoint::GetLowerLimitAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsLowerLimit));
}

inline UsdAttribute UsdPhysicsPrismaticJoint::CreateLowerLimitAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsLowerLimit), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsPrismaticJoint::GetUpperLimitAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsUpperLimit));
}

inline UsdAttribute UsdPhysicsPrismaticJoint::CreateUpperLimitAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsUpperLimit), SdfValueTypeNames->Float,
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
