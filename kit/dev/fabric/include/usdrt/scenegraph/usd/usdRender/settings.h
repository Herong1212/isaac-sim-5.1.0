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

/// @file usdRender/settings.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdRender/settingsBase.h"
#include "usdrt/scenegraph/usd/usdRender/tokens.h"


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
// RENDERSETTINGS                                                              //
// -------------------------------------------------------------------------- //

/// @class UsdRenderSettings
///
/// A UsdRenderSettings prim specifies global settings for
/// a render process, including an enumeration of the RenderProducts
/// that should result, and the UsdGeomImageable purposes that should
/// be rendered.  \ref UsdRenderHowSettingsAffectRendering
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdRenderTokens.
/// So to set an attribute to the value "rightHanded", use UsdRenderTokens->rightHanded
/// as the value.

class UsdRenderSettings : public UsdRenderSettingsBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdRenderSettings on UsdPrim @p prim.
    /// Equivalent to UsdRenderSettings::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdRenderSettings(const UsdPrim& prim = UsdPrim()) : UsdRenderSettingsBase(prim)
    {
    }

    /// Construct a UsdRenderSettings on the prim held by @p schemaObj .
    /// Should be preferred over UsdRenderSettings(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdRenderSettings(const UsdSchemaBase& schemaObj) : UsdRenderSettingsBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdRenderSettings()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdRenderSettings Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // INCLUDEDPURPOSES
    // --------------------------------------------------------------------- //
    /// The list of UsdGeomImageable _purpose_ values that
    /// should be included in the render.  Note this cannot be
    /// specified per-RenderProduct because it is a statement of
    /// which geometry is present.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] includedPurposes = ["default", "render"]` |
    /// | C++ Type | VtArray<TfToken> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TokenArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetIncludedPurposesAttr() const;

    /// See GetIncludedPurposesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIncludedPurposesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MATERIALBINDINGPURPOSES
    // --------------------------------------------------------------------- //
    /// Ordered list of material purposes to consider when
    /// resolving material bindings in the scene.  The empty string
    /// indicates the "allPurpose" binding.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] materialBindingPurposes = ["full", ""]` |
    /// | C++ Type | VtArray<TfToken> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TokenArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdRenderTokens "Allowed Values" | full, preview, "" |

    UsdAttribute GetMaterialBindingPurposesAttr() const;

    /// See GetMaterialBindingPurposesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaterialBindingPurposesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RENDERINGCOLORSPACE
    // --------------------------------------------------------------------- //
    /// Describes a renderer's working (linear) colorSpace where all
    /// the renderer/shader math is expected to happen. When no
    /// renderingColorSpace is provided, renderer should use its own default.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token renderingColorSpace` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetRenderingColorSpaceAttr() const;

    /// See GetRenderingColorSpaceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRenderingColorSpaceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PRODUCTS
    // --------------------------------------------------------------------- //
    /// The set of RenderProducts the render should produce.
    /// This relationship should target UsdRenderProduct prims.
    /// If no _products_ are specified, an application should produce
    /// an rgb image according to the RenderSettings configuration,
    /// to a default display or image name.
    ///
    UsdRelationship GetProductsRel() const;

    /// See GetProductsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateProductsRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdRenderSettings::_GetStaticTfType()
{
    const static TfToken token("UsdRenderSettings");
    return token;
}

/* virtual */
inline const TfToken UsdRenderSettings::_GetTfTypeToken() const
{
    const static TfToken token("UsdRenderSettings");
    return token;
}

/* static */
inline UsdRenderSettings UsdRenderSettings::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdRenderSettings();
    }
    return UsdRenderSettings(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdRenderSettings::GetIncludedPurposesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->includedPurposes));
}

inline UsdAttribute UsdRenderSettings::CreateIncludedPurposesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->includedPurposes), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderSettings::GetMaterialBindingPurposesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->materialBindingPurposes));
}

inline UsdAttribute UsdRenderSettings::CreateMaterialBindingPurposesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->materialBindingPurposes), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderSettings::GetRenderingColorSpaceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->renderingColorSpace));
}

inline UsdAttribute UsdRenderSettings::CreateRenderingColorSpaceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->renderingColorSpace), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}


inline UsdRelationship UsdRenderSettings::GetProductsRel() const
{
    return GetPrim().GetRelationship(UsdRenderTokens->products);
}

inline UsdRelationship UsdRenderSettings::CreateProductsRel() const
{
    return GetPrim().CreateRelationship(UsdRenderTokens->products,
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
