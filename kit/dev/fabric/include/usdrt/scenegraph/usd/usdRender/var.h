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

/// @file usdRender/var.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
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
// RENDERVAR                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdRenderVar
///
/// A UsdRenderVar describes a custom data variable for
/// a render to produce.  The prim describes the source of the data, which
/// can be a shader output or an LPE (Light Path Expression), and also
/// allows encoding of (generally renderer-specific) parameters that
/// configure the renderer for computing the variable.
///
/// \note The name of the RenderVar prim drives the name of the data
/// variable that the renderer will produce.
///
/// \note In the future, UsdRender may standardize RenderVar representation
/// for well-known variables under the sourceType `intrinsic`,
/// such as _r_, _g_, _b_, _a_, _z_, or _id_.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdRenderTokens.
/// So to set an attribute to the value "rightHanded", use UsdRenderTokens->rightHanded
/// as the value.

class UsdRenderVar : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdRenderVar on UsdPrim @p prim.
    /// Equivalent to UsdRenderVar::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdRenderVar(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdRenderVar on the prim held by @p schemaObj .
    /// Should be preferred over UsdRenderVar(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdRenderVar(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdRenderVar()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdRenderVar Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DATATYPE
    // --------------------------------------------------------------------- //
    /// The type of this channel, as a USD attribute type.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token dataType = "color3f"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDataTypeAttr() const;

    /// See GetDataTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDataTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOURCENAME
    // --------------------------------------------------------------------- //
    /// The renderer should look for an output of this name
    /// as the computed value for the RenderVar.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform string sourceName = ""` |
    /// | C++ Type | std::string |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->String |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSourceNameAttr() const;

    /// See GetSourceNameAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSourceNameAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SOURCETYPE
    // --------------------------------------------------------------------- //
    /// Indicates the type of the source.
    ///
    /// - "raw": The name should be passed directly to the
    /// renderer.  This is the default behavior.
    /// - "primvar":  This source represents the name of a primvar.
    /// Some renderers may use this to ensure that the primvar
    /// is provided; other renderers may require that a suitable
    /// material network be provided, in which case this is simply
    /// an advisory setting.
    /// - "lpe":  Specifies a Light Path Expression in the
    /// [OSL Light Path Expressions
    /// language](https://github.com/imageworks/OpenShadingLanguage/wiki/OSL-Light-Path-Expressions) as the source for
    /// this RenderVar.  Some renderers may use extensions to
    /// that syntax, which will necessarily be non-portable.
    /// - "intrinsic":  This setting is currently unimplemented,
    /// but represents a future namespace for UsdRender to provide
    /// portable baseline RenderVars, such as camera depth, that
    /// may have varying implementations for each renderer.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token sourceType = "raw"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdRenderTokens "Allowed Values" | raw, primvar, lpe, intrinsic |

    UsdAttribute GetSourceTypeAttr() const;

    /// See GetSourceTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSourceTypeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdRenderVar::_GetStaticTfType()
{
    const static TfToken token("UsdRenderVar");
    return token;
}

/* virtual */
inline const TfToken UsdRenderVar::_GetTfTypeToken() const
{
    const static TfToken token("UsdRenderVar");
    return token;
}

/* static */
inline UsdRenderVar UsdRenderVar::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdRenderVar();
    }
    return UsdRenderVar(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdRenderVar::GetDataTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->dataType));
}

inline UsdAttribute UsdRenderVar::CreateDataTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->dataType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderVar::GetSourceNameAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->sourceName));
}

inline UsdAttribute UsdRenderVar::CreateSourceNameAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->sourceName), SdfValueTypeNames->String,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderVar::GetSourceTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->sourceType));
}

inline UsdAttribute UsdRenderVar::CreateSourceTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->sourceType), SdfValueTypeNames->Token,
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
