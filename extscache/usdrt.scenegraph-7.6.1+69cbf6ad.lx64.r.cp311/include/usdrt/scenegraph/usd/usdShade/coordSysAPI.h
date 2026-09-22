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

/// @file usdShade/coordSysAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdShade/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdGeom/xformable.h"*/
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
// COORDSYSAPI                                                                 //
// -------------------------------------------------------------------------- //

/// @class UsdShadeCoordSysAPI
///
/// UsdShadeCoordSysAPI provides a way to designate, name,
/// and discover coordinate systems.
///
/// Coordinate systems are implicitly established by UsdGeomXformable
/// prims, using their local space.  That coordinate system may be
/// bound (i.e., named) from another prim.  The binding is encoded
/// as a single-target relationship in the "coordSys:" namespace.
/// Coordinate system bindings apply to descendants of the prim
/// where the binding is expressed, but names may be re-bound by
/// descendant prims.
///
/// Named coordinate systems are useful in shading workflows.
/// An example is projection paint, which projects a texture
/// from a certain view (the paint coordinate system).  Using
/// the paint coordinate frame avoids the need to assign a UV
/// set to the object, and can be a concise way to project
/// paint across a collection of objects with a single shared
/// paint coordinate system.
///
/// This is a non-applied API schema.
///

class UsdShadeCoordSysAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::NonAppliedAPI;


    /// Construct a UsdShadeCoordSysAPI on UsdPrim @p prim.
    /// Equivalent to UsdShadeCoordSysAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdShadeCoordSysAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdShadeCoordSysAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdShadeCoordSysAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdShadeCoordSysAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdShadeCoordSysAPI()
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

inline const TfToken UsdShadeCoordSysAPI::_GetStaticTfType()
{
    const static TfToken token("UsdShadeCoordSysAPI");
    return token;
}

/* virtual */
inline const TfToken UsdShadeCoordSysAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdShadeCoordSysAPI");
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
