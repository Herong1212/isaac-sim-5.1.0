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

/// @file usdPhysics/distanceJoint.h

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
// PHYSICSDISTANCEJOINT                                                        //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsDistanceJoint
///
/// Predefined distance joint type (Distance between rigid bodies
/// may be limited to given minimum or maximum distance.)

class UsdPhysicsDistanceJoint : public UsdPhysicsJoint
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdPhysicsDistanceJoint on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsDistanceJoint::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsDistanceJoint(const UsdPrim& prim = UsdPrim()) : UsdPhysicsJoint(prim)
    {
    }

    /// Construct a UsdPhysicsDistanceJoint on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsDistanceJoint(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsDistanceJoint(const UsdSchemaBase& schemaObj) : UsdPhysicsJoint(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsDistanceJoint()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdPhysicsDistanceJoint Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // MINDISTANCE
    // --------------------------------------------------------------------- //
    /// Minimum distance. If attribute is negative, the joint is not
    /// limited. Units: distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:minDistance = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMinDistanceAttr() const;

    /// See GetMinDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMinDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MAXDISTANCE
    // --------------------------------------------------------------------- //
    /// Maximum distance. If attribute is negative, the joint is not
    /// limited. Units: distance.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float physics:maxDistance = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetMaxDistanceAttr() const;

    /// See GetMaxDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaxDistanceAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsDistanceJoint::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsDistanceJoint");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsDistanceJoint::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsDistanceJoint");
    return token;
}

/* static */
inline UsdPhysicsDistanceJoint UsdPhysicsDistanceJoint::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdPhysicsDistanceJoint();
    }
    return UsdPhysicsDistanceJoint(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdPhysicsDistanceJoint::GetMinDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsMinDistance));
}

inline UsdAttribute UsdPhysicsDistanceJoint::CreateMinDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsMinDistance), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdPhysicsDistanceJoint::GetMaxDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdPhysicsTokens->physicsMaxDistance));
}

inline UsdAttribute UsdPhysicsDistanceJoint::CreateMaxDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdPhysicsTokens->physicsMaxDistance), SdfValueTypeNames->Float,
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
