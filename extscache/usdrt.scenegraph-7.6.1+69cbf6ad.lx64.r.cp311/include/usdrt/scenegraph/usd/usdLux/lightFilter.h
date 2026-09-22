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

/// @file usdLux/lightFilter.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/xformable.h"
#include "usdrt/scenegraph/usd/usdLux/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/collectionAPI.h"
#include "usdrt/scenegraph/usd/usdShade/input.h"
#include "usdrt/scenegraph/usd/usdShade/output.h" */
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
// LIGHTFILTER                                                                 //
// -------------------------------------------------------------------------- //

/// @class UsdLuxLightFilter
///
/// A light filter modifies the effect of a light.
/// Lights refer to filters via relationships so that filters may be
/// shared.
///
/// <b>Linking</b>
///
/// Filters can be linked to geometry.  Linking controls which geometry
/// a light-filter affects, when considering the light filters attached
/// to a light illuminating the geometry.
///
/// Linking is specified as a collection (UsdCollectionAPI) which can
/// be accessed via GetFilterLinkCollection().
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxLightFilter : public UsdGeomXformable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxLightFilter on UsdPrim @p prim.
    /// Equivalent to UsdLuxLightFilter::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxLightFilter(const UsdPrim& prim = UsdPrim()) : UsdGeomXformable(prim)
    {
    }

    /// Construct a UsdLuxLightFilter on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxLightFilter(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxLightFilter(const UsdSchemaBase& schemaObj) : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxLightFilter()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdLuxLightFilter Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // COLLECTIONFILTERLINKINCLUDEROOT
    // --------------------------------------------------------------------- //
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool collection:filterLink:includeRoot = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetCollectionFilterLinkIncludeRootAttr() const;

    /// See GetCollectionFilterLinkIncludeRootAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollectionFilterLinkIncludeRootAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHADERID
    // --------------------------------------------------------------------- //
    /// Default ID for the light filter's shader.
    /// This defines the shader ID for this light filter when a render context
    /// specific shader ID is not available.
    ///
    /// \see GetShaderId
    /// \see GetShaderIdAttrForRenderContext
    /// \see SdrRegistry::GetShaderNodeByIdentifier
    /// \see SdrRegistry::GetShaderNodeByIdentifierAndType
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token lightFilter:shaderId = ""` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetShaderIdAttr() const;

    /// See GetShaderIdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShaderIdAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxLightFilter::_GetStaticTfType()
{
    const static TfToken token("UsdLuxLightFilter");
    return token;
}

/* virtual */
inline const TfToken UsdLuxLightFilter::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxLightFilter");
    return token;
}

/* static */
inline UsdLuxLightFilter UsdLuxLightFilter::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdLuxLightFilter();
    }
    return UsdLuxLightFilter(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdLuxLightFilter::GetCollectionFilterLinkIncludeRootAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->collectionFilterLinkIncludeRoot));
}

inline UsdAttribute UsdLuxLightFilter::CreateCollectionFilterLinkIncludeRootAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->collectionFilterLinkIncludeRoot), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightFilter::GetShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightFilterShaderId));
}

inline UsdAttribute UsdLuxLightFilter::CreateShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightFilterShaderId), SdfValueTypeNames->Token,
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
