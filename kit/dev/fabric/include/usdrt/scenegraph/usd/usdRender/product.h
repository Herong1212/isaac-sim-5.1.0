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

/// @file usdRender/product.h

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
// RENDERPRODUCT                                                               //
// -------------------------------------------------------------------------- //

/// @class UsdRenderProduct
///
/// A UsdRenderProduct describes an image or other
/// file-like artifact produced by a render. A RenderProduct
/// combines one or more RenderVars into a file or interactive
/// buffer.  It also provides all the controls established in
/// UsdRenderSettingsBase as optional overrides to whatever the
/// owning UsdRenderSettings prim dictates.
///
/// Specific renderers may support additional settings, such
/// as a way to configure compression settings, filetype metadata,
/// and so forth.  Such settings can be encoded using
/// renderer-specific API schemas applied to the product prim.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdRenderTokens.
/// So to set an attribute to the value "rightHanded", use UsdRenderTokens->rightHanded
/// as the value.

class UsdRenderProduct : public UsdRenderSettingsBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdRenderProduct on UsdPrim @p prim.
    /// Equivalent to UsdRenderProduct::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdRenderProduct(const UsdPrim& prim = UsdPrim()) : UsdRenderSettingsBase(prim)
    {
    }

    /// Construct a UsdRenderProduct on the prim held by @p schemaObj .
    /// Should be preferred over UsdRenderProduct(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdRenderProduct(const UsdSchemaBase& schemaObj) : UsdRenderSettingsBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdRenderProduct()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdRenderProduct Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // PRODUCTTYPE
    // --------------------------------------------------------------------- //
    /// The type of output to produce.
    /// The default, "raster", indicates a 2D image.
    ///
    /// \note In the future, UsdRender may define additional product
    /// types.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token productType = "raster"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetProductTypeAttr() const;

    /// See GetProductTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateProductTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PRODUCTNAME
    // --------------------------------------------------------------------- //
    /// Specifies the name that the output/display driver
    /// should give the product.  This is provided as-authored to the
    /// driver, whose responsibility it is to situate the product on a
    /// filesystem or other storage, in the desired location.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token productName = ""` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |

    UsdAttribute GetProductNameAttr() const;

    /// See GetProductNameAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateProductNameAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ORDEREDVARS
    // --------------------------------------------------------------------- //
    /// Specifies the RenderVars that should be consumed and
    /// combined into the final product.  If ordering is relevant to the
    /// output driver, then the ordering of targets in this relationship
    /// provides the order to use.
    ///
    UsdRelationship GetOrderedVarsRel() const;

    /// See GetOrderedVarsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateOrderedVarsRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdRenderProduct::_GetStaticTfType()
{
    const static TfToken token("UsdRenderProduct");
    return token;
}

/* virtual */
inline const TfToken UsdRenderProduct::_GetTfTypeToken() const
{
    const static TfToken token("UsdRenderProduct");
    return token;
}

/* static */
inline UsdRenderProduct UsdRenderProduct::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdRenderProduct();
    }
    return UsdRenderProduct(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdRenderProduct::GetProductTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->productType));
}

inline UsdAttribute UsdRenderProduct::CreateProductTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->productType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderProduct::GetProductNameAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->productName));
}

inline UsdAttribute UsdRenderProduct::CreateProductNameAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->productName), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}


inline UsdRelationship UsdRenderProduct::GetOrderedVarsRel() const
{
    return GetPrim().GetRelationship(UsdRenderTokens->orderedVars);
}

inline UsdRelationship UsdRenderProduct::CreateOrderedVarsRel() const
{
    return GetPrim().CreateRelationship(UsdRenderTokens->orderedVars,
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
