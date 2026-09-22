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

/// @file usdLux/pluginLightFilter.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdLux/lightFilter.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdShade/nodeDefAPI.h" */
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
// PLUGINLIGHTFILTER                                                           //
// -------------------------------------------------------------------------- //

/// @class UsdLuxPluginLightFilter
///
/// Light filter that provides properties that allow it to identify an
/// external SdrShadingNode definition, through UsdShadeNodeDefAPI, that can be
/// provided to render delegates without the need to provide a schema
/// definition for the light filter's type.
///
/// \see \ref usdLux_PluginSchemas
///

class UsdLuxPluginLightFilter : public UsdLuxLightFilter
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxPluginLightFilter on UsdPrim @p prim.
    /// Equivalent to UsdLuxPluginLightFilter::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxPluginLightFilter(const UsdPrim& prim = UsdPrim()) : UsdLuxLightFilter(prim)
    {
    }

    /// Construct a UsdLuxPluginLightFilter on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxPluginLightFilter(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxPluginLightFilter(const UsdSchemaBase& schemaObj) : UsdLuxLightFilter(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxPluginLightFilter()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdLuxPluginLightFilter Define(const UsdStageRefPtr& stage, const SdfPath& path);

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

inline const TfToken UsdLuxPluginLightFilter::_GetStaticTfType()
{
    const static TfToken token("UsdLuxPluginLightFilter");
    return token;
}

/* virtual */
inline const TfToken UsdLuxPluginLightFilter::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxPluginLightFilter");
    return token;
}

/* static */
inline UsdLuxPluginLightFilter UsdLuxPluginLightFilter::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdLuxPluginLightFilter();
    }
    return UsdLuxPluginLightFilter(stage->DefinePrim(path, _GetStaticTfType()));
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
