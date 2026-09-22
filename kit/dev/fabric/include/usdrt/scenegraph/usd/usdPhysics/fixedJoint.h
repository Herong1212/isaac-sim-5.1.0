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

/// @file usdPhysics/fixedJoint.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdPhysics/joint.h"


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
// PHYSICSFIXEDJOINT                                                           //
// -------------------------------------------------------------------------- //

/// @class UsdPhysicsFixedJoint
///
/// Predefined fixed joint type (All degrees of freedom are
/// removed.)

class UsdPhysicsFixedJoint : public UsdPhysicsJoint
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdPhysicsFixedJoint on UsdPrim @p prim.
    /// Equivalent to UsdPhysicsFixedJoint::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdPhysicsFixedJoint(const UsdPrim& prim = UsdPrim()) : UsdPhysicsJoint(prim)
    {
    }

    /// Construct a UsdPhysicsFixedJoint on the prim held by @p schemaObj .
    /// Should be preferred over UsdPhysicsFixedJoint(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdPhysicsFixedJoint(const UsdSchemaBase& schemaObj) : UsdPhysicsJoint(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdPhysicsFixedJoint()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdPhysicsFixedJoint Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdPhysicsFixedJoint::_GetStaticTfType()
{
    const static TfToken token("UsdPhysicsFixedJoint");
    return token;
}

/* virtual */
inline const TfToken UsdPhysicsFixedJoint::_GetTfTypeToken() const
{
    const static TfToken token("UsdPhysicsFixedJoint");
    return token;
}

/* static */
inline UsdPhysicsFixedJoint UsdPhysicsFixedJoint::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdPhysicsFixedJoint();
    }
    return UsdPhysicsFixedJoint(stage->DefinePrim(path, _GetStaticTfType()));
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
