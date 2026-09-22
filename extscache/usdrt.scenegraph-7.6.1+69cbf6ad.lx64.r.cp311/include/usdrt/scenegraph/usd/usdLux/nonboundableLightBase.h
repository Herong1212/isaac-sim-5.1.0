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

/// @file usdLux/nonboundableLightBase.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/xformable.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdLux/lightAPI.h" */
// clang-format on

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
// NONBOUNDABLELIGHTBASE                                                       //
// -------------------------------------------------------------------------- //

/// @class UsdLuxNonboundableLightBase
///
/// Base class for intrinsic lights that are not boundable.
///
/// The primary purpose of this class is to provide a direct API to the
/// functions provided by LightAPI for concrete derived light types.
///

class UsdLuxNonboundableLightBase : public UsdGeomXformable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdLuxNonboundableLightBase on UsdPrim @p prim.
    /// Equivalent to UsdLuxNonboundableLightBase::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxNonboundableLightBase(const UsdPrim& prim = UsdPrim()) : UsdGeomXformable(prim)
    {
    }

    /// Construct a UsdLuxNonboundableLightBase on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxNonboundableLightBase(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxNonboundableLightBase(const UsdSchemaBase& schemaObj) : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxNonboundableLightBase()
    {
    }

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

inline const TfToken UsdLuxNonboundableLightBase::_GetStaticTfType()
{
    const static TfToken token("UsdLuxNonboundableLightBase");
    return token;
}

/* virtual */
inline const TfToken UsdLuxNonboundableLightBase::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxNonboundableLightBase");
    return token;
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
