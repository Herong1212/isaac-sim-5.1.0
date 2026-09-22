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

/// @file usdShade/nodeDefAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdShade/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/ndr/declare.h"
#include "usdrt/scenegraph/usd/sdr/shaderNode.h"
    */
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
// NODEDEFAPI                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdShadeNodeDefAPI
///
/// UsdShadeNodeDefAPI is an API schema that provides attributes
/// for a prim to select a corresponding Shader Node Definition ("Sdr Node"),
/// as well as to look up a runtime entry for that shader node in the
/// form of an SdrShaderNode.
///
/// UsdShadeNodeDefAPI is intended to be a pre-applied API schema for any
/// prim type that wants to refer to the SdrRegistry for further implementation
/// details about the behavior of that prim.  The primary use in UsdShade
/// itself is as UsdShadeShader, which is a basis for material shading networks
/// (UsdShadeMaterial), but this is intended to be used in other domains
/// that also use the Sdr node mechanism.
///
/// This schema provides properties that allow a prim to identify an external
/// node definition, either by a direct identifier key into the SdrRegistry
/// (info:id), an asset to be parsed by a suitable NdrParserPlugin
/// (info:sourceAsset), or an inline source code that must also be parsed
/// (info:sourceCode); as well as a selector attribute to determine which
/// specifier is active (info:implementationSource).
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdShadeTokens.
/// So to set an attribute to the value "rightHanded", use UsdShadeTokens->rightHanded
/// as the value.

class UsdShadeNodeDefAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdShadeNodeDefAPI on UsdPrim @p prim.
    /// Equivalent to UsdShadeNodeDefAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdShadeNodeDefAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdShadeNodeDefAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdShadeNodeDefAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdShadeNodeDefAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdShadeNodeDefAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "NodeDefAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdShadeNodeDefAPI object is returned upon success.
    /// An invalid (or empty) UsdShadeNodeDefAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdShadeNodeDefAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdShadeNodeDefAPI>())
        {
            return UsdShadeNodeDefAPI(prim);
        }
        return UsdShadeNodeDefAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // IMPLEMENTATIONSOURCE
    // --------------------------------------------------------------------- //
    /// Specifies the attribute that should be consulted to get the
    /// shader's implementation or its source code.
    ///
    /// * If set to "id", the "info:id" attribute's value is used to
    /// determine the shader source from the shader registry.
    /// * If set to "sourceAsset", the resolved value of the "info:sourceAsset"
    /// attribute corresponding to the desired implementation (or source-type)
    /// is used to locate the shader source.  A source asset file may also
    /// specify multiple shader definitions, so there is an optional attribute
    /// "info:sourceAsset:subIdentifier" whose value should be used to indicate
    /// a particular shader definition from a source asset file.
    /// * If set to "sourceCode", the value of "info:sourceCode" attribute
    /// corresponding to the desired implementation (or source type) is used as
    /// the shader source.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token info:implementationSource = "id"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdShadeTokens "Allowed Values" | id, sourceAsset, sourceCode |

    UsdAttribute GetImplementationSourceAttr() const;

    /// See GetImplementationSourceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateImplementationSourceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ID
    // --------------------------------------------------------------------- //
    /// The id is an identifier for the type or purpose of the
    /// shader. E.g.: Texture or FractalFloat.
    /// The use of this id will depend on the render target: some will turn it
    /// into an actual shader path, some will use it to generate shader source
    /// code dynamically.
    ///
    /// \sa SetShaderId()
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token info:id` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetIdAttr() const;

    /// See GetIdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIdAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--

    /// Reads the value of info:implementationSource attribute and returns a
    /// token identifying the attribute that must be consulted to identify the
    /// shader's source program.
    ///
    /// This returns
    /// * <b>id</b>, to indicate that the "info:id" attribute must be
    /// consulted.
    /// * <b>sourceAsset</b> to indicate that the asset-valued
    /// "info:{sourceType}:sourceAsset" attribute associated with the desired
    /// <b>sourceType</b> should be consulted to locate the asset with the
    /// shader's source.
    /// * <b>sourceCode</b> to indicate that the string-valued
    /// "info:{sourceType}:sourceCode" attribute associated with the desired
    /// <b>sourceType</b> should be read to get shader's source.
    ///
    /// This issues a warning and returns <b>id</b> if the
    /// <i>info:implementationSource</i> attribute has an invalid value.
    ///
    /// <i>{sourceType}</i> above is a place holder for a token that identifies
    /// the type of shader source or its implementation. For example: osl,
    /// glslfx, riCpp etc. This allows a shader to specify different sourceAsset
    /// (or sourceCode) values for different sourceTypes. The sourceType tokens
    /// usually correspond to the sourceType value of the NdrParserPlugin that's
    /// used to parse the shader source (\ref NdrParserPlugin::SourceType).
    ///
    /// When sourceType is empty, the corresponding sourceAsset or sourceCode is
    /// considered to be "universal" (or fallback), which is represented by the
    /// empty-valued token UsdShadeTokens->universalSourceType. When the
    /// sourceAsset (or sourceCode) corresponding to a specific, requested
    /// sourceType is unavailable, the universal sourceAsset (or sourceCode) is
    /// returned by GetSourceAsset (and GetSourceCode} API, if present.
    ///
    /// \sa GetShaderId()
    /// \sa GetSourceAsset()
    /// \sa GetSourceCode()
    TfToken GetImplementationSource() const;

    /// Sets the shader's ID value. This also sets the
    /// <i>info:implementationSource</i> attribute on the shader to
    /// <b>UsdShadeTokens->id</b>, if the existing value is different.
    bool SetShaderId(const TfToken& id) const;

    /// Fetches the shader's ID value from the <i>info:id</i> attribute, if the
    /// shader's <i>info:implementationSource</i> is <b>id</b>.
    ///
    /// Returns <b>true</b> if the shader's implementation source is <b>id</b>
    /// and the value was fetched properly into \p id. Returns false otherwise.
    ///
    /// \sa GetImplementationSource()
    bool GetShaderId(TfToken* id) const;

    /// Sets the shader's source-asset path value to \p sourceAsset for the
    /// given source type, \p sourceType.
    ///
    /// This also sets the <i>info:implementationSource</i> attribute on the
    /// shader to <b>UsdShadeTokens->sourceAsset</b>.
    bool SetSourceAsset(const SdfAssetPath& sourceAsset,
                        const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Fetches the shader's source asset value for the specified
    /// \p sourceType value from the <b>info:<i>sourceType:</i>sourceAsset</b>
    /// attribute, if the shader's <i>info:implementationSource</i> is
    /// <b>sourceAsset</b>.
    ///
    /// If the <i>sourceAsset</i> attribute corresponding to the requested
    /// <i>sourceType</i> isn't present on the shader, then the <i>universal</i>
    /// <i>fallback</i> sourceAsset attribute, i.e. <i>info:sourceAsset</i> is
    /// consulted, if present, to get the source asset path.
    ///
    /// Returns <b>true</b> if the shader's implementation source is
    /// <b>sourceAsset</b> and the source asset path value was fetched
    /// successfully into \p sourceAsset. Returns false otherwise.
    ///
    /// \sa GetImplementationSource()
    bool GetSourceAsset(SdfAssetPath* sourceAsset, const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Set a sub-identifier to be used with a source asset of the given source
    /// type.  This sets the <b>info:<i>sourceType:</i>sourceAsset:subIdentifier
    /// </b>.
    ///
    /// This also sets the <i>info:implementationSource</i> attribute on the
    /// shader to <b>UsdShadeTokens->sourceAsset</b>
    bool SetSourceAssetSubIdentifier(const TfToken& subIdentifier,
                                     const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Fetches the shader's sub-identifier for the source asset with the
    /// specified \p sourceType value from the <b>info:<i>sourceType:</i>
    /// sourceAsset:subIdentifier</b> attribute, if the shader's <i>info:
    /// implementationSource</i> is <b>sourceAsset</b>.
    ///
    /// If the <i>subIdentifier</i> attribute corresponding to the requested
    /// <i>sourceType</i> isn't present on the shader, then the <i>universal</i>
    /// <i>fallback</i> sub-identifier attribute, i.e. <i>info:sourceAsset:
    /// subIdentifier</i> is consulted, if present, to get the sub-identifier
    /// name.
    ///
    /// Returns <b>true</b> if the shader's implementation source is
    /// <b>sourceAsset</b> and the sub-identifier for the given source type was
    /// fetched successfully into \p subIdentifier. Returns false otherwise.
    bool GetSourceAssetSubIdentifier(TfToken* subIdentifier,
                                     const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Sets the shader's source-code value to \p sourceCode for the given
    /// source type, \p sourceType.
    ///
    /// This also sets the <i>info:implementationSource</i> attribute on the
    /// shader to <b>UsdShadeTokens->sourceCode</b>.
    bool SetSourceCode(const std::string& sourceCode,
                       const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Fetches the shader's source code for the specified \p sourceType value
    /// by reading the <b>info:<i>sourceType:</i>sourceCode</b> attribute, if
    /// the shader's <i>info:implementationSource</i> is <b>sourceCode</b>.
    ///
    /// If the <i>sourceCode</i> attribute corresponding to the
    /// requested <i>sourceType</i> isn't present on the shader, then the
    /// <i>universal</i> or <i>fallback</i> sourceCode attribute (i.e.
    /// <i>info:sourceCode</i>) is consulted, if present, to get the source
    /// code.
    ///
    /// Returns <b>true</b> if the shader's implementation source is
    /// <b>sourceCode</b> and the source code string was fetched successfully
    /// into \p sourceCode. Returns false otherwise.
    ///
    /// \sa GetImplementationSource()
    bool GetSourceCode(std::string* sourceCode, const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

private:
    static TfToken _GetSourceAssetAttrName(const TfToken& sourceType);

    static TfToken _GetSourceAssetSubIdentifierAttrName(const TfToken& sourceType);

    static TfToken _GetSourceCodeAttrName(const TfToken& sourceType);

    struct NodeDefAPITokensType
    {
        const TfToken info = "info";
        const TfToken infoSourceAsset = "info:sourceAsset";
        const TfToken infoSubIdentifier = "info:sourceAsset:subIdentifier";
        const TfToken infoSourceCode = "info:sourceCode";
    };

    struct NodeDefAPITokensTypeAcessor
    {
        const NodeDefAPITokensType* operator->()
        {
            static const NodeDefAPITokensType tokens;
            return &tokens;
        }
    };

    inline static NodeDefAPITokensTypeAcessor _tokens;
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdShadeNodeDefAPI::_GetStaticTfType()
{
    const static TfToken token("UsdShadeNodeDefAPI");
    return token;
}

/* virtual */
inline const TfToken UsdShadeNodeDefAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdShadeNodeDefAPI");
    return token;
}


inline UsdAttribute UsdShadeNodeDefAPI::GetImplementationSourceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdShadeTokens->infoImplementationSource));
}

inline UsdAttribute UsdShadeNodeDefAPI::CreateImplementationSourceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdShadeTokens->infoImplementationSource), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdShadeNodeDefAPI::GetIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdShadeTokens->infoId));
}

inline UsdAttribute UsdShadeNodeDefAPI::CreateIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdShadeTokens->infoId), SdfValueTypeNames->Token,
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

namespace usdrt
{

inline TfToken UsdShadeNodeDefAPI::GetImplementationSource() const
{
    TfToken implSource;
    GetImplementationSourceAttr().Get(&implSource);

    if (implSource == UsdShadeTokens->id || implSource == UsdShadeTokens->sourceAsset ||
        implSource == UsdShadeTokens->sourceCode)
    {
        return implSource;
    }
    else
    {
        return UsdShadeTokens->id;
    }
}

inline bool UsdShadeNodeDefAPI::SetShaderId(const TfToken& id) const
{
    return CreateImplementationSourceAttr().Set(UsdShadeTokens->id) && CreateIdAttr().Set(id);
}

inline bool UsdShadeNodeDefAPI::GetShaderId(TfToken* id) const
{
    auto implSource = GetImplementationSource();
    if (implSource == UsdShadeTokens->id)
    {
        return GetIdAttr().Get(id);
    }
    return false;
}

inline bool UsdShadeNodeDefAPI::SetSourceAsset(const SdfAssetPath& sourceAsset, const TfToken& sourceType) const
{
    return CreateImplementationSourceAttr().Set(UsdShadeTokens->sourceAsset) &&
           GetPrim()
               .CreateAttribute(_GetSourceAssetAttrName(sourceType), SdfValueTypeNames->Asset, /* custom = */ false)
               .Set(sourceAsset);
}

inline bool UsdShadeNodeDefAPI::GetSourceAsset(SdfAssetPath* sourceAsset, const TfToken& sourceType) const
{
    auto implSource = GetImplementationSource();
    if (implSource != UsdShadeTokens->sourceAsset)
    {
        return false;
    }

    auto sourceAssetAttrName = _GetSourceAssetAttrName(sourceType);
    auto sourceAssetAttr = GetPrim().GetAttribute(sourceAssetAttrName);
    if (sourceAssetAttr)
    {
        return sourceAssetAttr.Get(sourceAsset);
    }

    if (sourceType != UsdShadeTokens->universalSourceType)
    {
        auto univSourceAssetAttr = GetPrim().GetAttribute(_GetSourceAssetAttrName(UsdShadeTokens->universalSourceType));
        if (univSourceAssetAttr)
        {
            return univSourceAssetAttr.Get(sourceAsset);
        }
    }

    return false;
}

inline bool UsdShadeNodeDefAPI::SetSourceAssetSubIdentifier(const TfToken& subIdentifier, const TfToken& sourceType) const
{
    return CreateImplementationSourceAttr().Set(UsdShadeTokens->sourceAsset) &&
           GetPrim()
               .CreateAttribute(_GetSourceAssetSubIdentifierAttrName(sourceType), SdfValueTypeNames->Token,
                                /* custom = */ false)
               .Set(subIdentifier);
}


inline bool UsdShadeNodeDefAPI::GetSourceAssetSubIdentifier(TfToken* subIdentifier, const TfToken& sourceType) const
{
    auto implSource = GetImplementationSource();
    if (implSource != UsdShadeTokens->sourceAsset)
    {
        return false;
    }

    auto subIdentifierAttrName = _GetSourceAssetSubIdentifierAttrName(sourceType);
    auto subIdentifierAttr = GetPrim().GetAttribute(subIdentifierAttrName);
    if (subIdentifierAttr)
    {
        return subIdentifierAttr.Get(subIdentifier);
    }

    if (sourceType != UsdShadeTokens->universalSourceType)
    {
        auto univSubIdentifierAttr =
            GetPrim().GetAttribute(_GetSourceAssetSubIdentifierAttrName(UsdShadeTokens->universalSourceType));
        if (univSubIdentifierAttr)
        {
            return univSubIdentifierAttr.Get(subIdentifier);
        }
    }

    return false;
}

inline bool UsdShadeNodeDefAPI::SetSourceCode(const std::string& sourceCode, const TfToken& sourceType) const
{
    return CreateImplementationSourceAttr().Set(UsdShadeTokens->sourceCode) &&
           GetPrim()
               .CreateAttribute(_GetSourceCodeAttrName(sourceType), SdfValueTypeNames->String,
                                /* custom = */ false)
               .Set(sourceCode);
}

inline bool UsdShadeNodeDefAPI::GetSourceCode(std::string* sourceCode, const TfToken& sourceType) const
{
    auto implSource = GetImplementationSource();
    if (implSource != UsdShadeTokens->sourceCode)
    {
        return false;
    }

    auto sourceCodeAttrName = _GetSourceCodeAttrName(sourceType);
    auto sourceCodeAttr = GetPrim().GetAttribute(sourceCodeAttrName);
    if (sourceCodeAttr)
    {
        return sourceCodeAttr.Get(sourceCode);
    }

    if (sourceType != UsdShadeTokens->universalSourceType)
    {
        auto univSourceCodeAttr = GetPrim().GetAttribute(_GetSourceCodeAttrName(UsdShadeTokens->universalSourceType));
        if (univSourceCodeAttr)
        {
            return univSourceCodeAttr.Get(sourceCode);
        }
    }

    return false;
}

inline TfToken UsdShadeNodeDefAPI::_GetSourceAssetAttrName(const TfToken& sourceType)
{
    if (sourceType == UsdShadeTokens->universalSourceType)
    {
        return _tokens->infoSourceAsset;
    }
    return TfToken(SdfPath::JoinIdentifier(TfTokenVector{ _tokens->info, sourceType, UsdShadeTokens->sourceAsset }));
}

inline TfToken UsdShadeNodeDefAPI::_GetSourceAssetSubIdentifierAttrName(const TfToken& sourceType)
{
    if (sourceType == UsdShadeTokens->universalSourceType)
    {
        return _tokens->infoSubIdentifier;
    }
    return TfToken(SdfPath::JoinIdentifier(
        TfTokenVector{ _tokens->info, sourceType, UsdShadeTokens->sourceAsset, UsdShadeTokens->subIdentifier }));
}

inline TfToken UsdShadeNodeDefAPI::_GetSourceCodeAttrName(const TfToken& sourceType)
{
    if (sourceType == UsdShadeTokens->universalSourceType)
    {
        return _tokens->infoSourceCode;
    }
    return TfToken(SdfPath::JoinIdentifier(TfTokenVector{ _tokens->info, sourceType, UsdShadeTokens->sourceCode }));
}

} // namespace usdrt
