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

/// @file usdShade/shader.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdShade/input.h"
#include "usdrt/scenegraph/usd/usdShade/output.h"
#include "usdrt/scenegraph/usd/usdShade/tokens.h"
#include "usdrt/scenegraph/usd/ndr/declare.h"
#include "usdrt/scenegraph/usd/sdr/shaderNode.h"*/
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
#include <usdrt/scenegraph/usd/usdShade/connectableAPI.h>
#include <usdrt/scenegraph/usd/usdShade/input.h>
#include <usdrt/scenegraph/usd/usdShade/output.h>
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
// SHADER                                                                      //
// -------------------------------------------------------------------------- //

/// @class UsdShadeShader
///
/// Base class for all USD shaders. Shaders are the building blocks
/// of shading networks. While UsdShadeShader objects are not target specific,
/// each renderer or application target may derive its own renderer-specific
/// shader object types from this base, if needed.
///
/// Objects of this class generally represent a single shading object, whether
/// it exists in the target renderer or not. For example, a texture, a fractal,
/// or a mix node.
///
/// The UsdShadeNodeDefAPI provides attributes to uniquely identify the
/// type of this node.  The id resolution into a renderable shader target
/// type of this node.  The id resolution into a renderable shader target
/// is deferred to the consuming application.
///
/// The purpose of representing them in Usd is two-fold:
/// \li To represent, via "connections" the topology of the shading network
/// that must be reconstructed in the renderer. Facilities for authoring and
/// manipulating connections are encapsulated in the API schema
/// UsdShadeConnectableAPI.
/// \li To present a (partial or full) interface of typed input parameters
/// whose values can be set and overridden in Usd, to be provided later at
/// render-time as parameter values to the actual render shader objects. Shader
/// input parameters are encapsulated in the property schema UsdShadeInput.
///

class UsdShadeShader : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdShadeShader on UsdPrim @p prim.
    /// Equivalent to UsdShadeShader::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdShadeShader(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdShadeShader on the prim held by @p schemaObj .
    /// Should be preferred over UsdShadeShader(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdShadeShader(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdShadeShader()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdShadeShader Define(const UsdStageRefPtr& stage, const SdfPath& path);

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

public:
    // -------------------------------------------------------------------------
    /// \name Conversion to and from UsdShadeConnectableAPI
    ///
    /// @{

    /// Constructor that takes a ConnectableAPI object.
    /// Allow implicit (auto) conversion of UsdShadeConnectableAPI to
    /// UsdShadeShader, so that a ConnectableAPI can be passed into any function
    /// that accepts a Shader.
    ///
    /// \note that the conversion may produce an invalid Shader object, because
    /// not all UsdShadeConnectableAPI%s are Shader%s
    UsdShadeShader(const UsdShadeConnectableAPI& connectable);

    /// Contructs and returns a UsdShadeConnectableAPI object with this shader.
    ///
    /// Note that most tasks can be accomplished without explicitly constructing
    /// a UsdShadeConnectable API, since connection-related API such as
    /// UsdShadeConnectableAPI::ConnectToSource() are static methods, and
    /// UsdShadeShader will auto-convert to a UsdShadeConnectableAPI when
    /// passed to functions that want to act generically on a connectable
    /// UsdShadeConnectableAPI object.
    UsdShadeConnectableAPI ConnectableAPI() const;

    /// @}

    // -------------------------------------------------------------------------
    /// \name Outputs API
    ///
    /// Outputs represent a typed attribute on a shader or node-graph whose value
    /// is computed externally.
    ///
    /// When they exist on a node-graph, they are connectable and are typically
    /// connected to the output of a shader within the node-graph.
    ///
    /// @{

    /// Create an output which can either have a value or can be connected.
    /// The attribute representing the output is created in the "outputs:"
    /// namespace. Outputs on a shader cannot be connected, as their
    /// value is assumed to be computed externally.
    ///
    UsdShadeOutput CreateOutput(const TfToken& name, const SdfValueTypeName& typeName);

    /// Return the requested output if it exists.
    ///
    UsdShadeOutput GetOutput(const TfToken& name) const;

    /// Outputs are represented by attributes in the "outputs:" namespace.
    /// If \p onlyAuthored is true (the default), then only return authored
    /// attributes; otherwise, this also returns un-authored builtins.
    ///
    std::vector<UsdShadeOutput> GetOutputs(bool onlyAuthored = true) const;

    /// \name Inputs API
    ///
    /// Inputs are connectable attribute with a typed value.
    ///
    /// On shaders, the shader parameters are encoded as inputs. On node-graphs,
    /// interface attributes are represented as inputs.
    ///
    /// @{

    /// Create an input which can either have a value or can be connected.
    /// The attribute representing the input is created in the "inputs:"
    /// namespace. Inputs on both shaders and node-graphs are connectable.
    ///
    UsdShadeInput CreateInput(const TfToken& name, const SdfValueTypeName& typeName);

    /// Return the requested input if it exists.
    ///
    UsdShadeInput GetInput(const TfToken& name) const;

    /// Inputs are represented by attributes in the "inputs:" namespace.
    /// If \p onlyAuthored is true (the default), then only return authored
    /// attributes; otherwise, this also returns un-authored builtins.
    ///
    std::vector<UsdShadeInput> GetInputs(bool onlyAuthored = true) const;

    /// @}

    // -------------------------------------------------------------------------
    /// \name UsdShadeNodeDefAPI forwarding
    ///
    /// @{

    /// Forwards to UsdShadeNodeDefAPI(prim).
    UsdAttribute GetImplementationSourceAttr() const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    UsdAttribute CreateImplementationSourceAttr() const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    UsdAttribute GetIdAttr() const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    UsdAttribute CreateIdAttr() const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    TfToken GetImplementationSource() const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool SetShaderId(const TfToken& id) const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool GetShaderId(TfToken* id) const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool SetSourceAsset(const SdfAssetPath& sourceAsset,
                        const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool GetSourceAsset(SdfAssetPath* sourceAsset, const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool SetSourceAssetSubIdentifier(const TfToken& subIdentifier,
                                     const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool GetSourceAssetSubIdentifier(TfToken* subIdentifier,
                                     const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool SetSourceCode(const std::string& sourceCode,
                       const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// Forwards to UsdShadeNodeDefAPI(prim).
    bool GetSourceCode(std::string* sourceCode, const TfToken& sourceType = UsdShadeTokens->universalSourceType) const;

    /// @}
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdShadeShader::_GetStaticTfType()
{
    const static TfToken token("UsdShadeShader");
    return token;
}

/* virtual */
inline const TfToken UsdShadeShader::_GetTfTypeToken() const
{
    const static TfToken token("UsdShadeShader");
    return token;
}

/* static */
inline UsdShadeShader UsdShadeShader::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdShadeShader();
    }
    return UsdShadeShader(stage->DefinePrim(path, _GetStaticTfType()));
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

#include <usdrt/scenegraph/usd/usdShade/connectableAPI.h>
#include <usdrt/scenegraph/usd/usdShade/nodeDefAPI.h>

namespace usdrt
{

inline UsdShadeShader::UsdShadeShader(const UsdShadeConnectableAPI& connectable) : UsdShadeShader(connectable.GetPrim())
{
}

inline UsdShadeConnectableAPI UsdShadeShader::ConnectableAPI() const
{
    return UsdShadeConnectableAPI(GetPrim());
}

inline UsdShadeOutput UsdShadeShader::CreateOutput(const TfToken& name, const SdfValueTypeName& typeName)
{
    return UsdShadeConnectableAPI(GetPrim()).CreateOutput(name, typeName);
}

inline UsdShadeOutput UsdShadeShader::GetOutput(const TfToken& name) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetOutput(name);
}

inline std::vector<UsdShadeOutput> UsdShadeShader::GetOutputs(bool onlyAuthored) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetOutputs(onlyAuthored);
}

inline UsdShadeInput UsdShadeShader::CreateInput(const TfToken& name, const SdfValueTypeName& typeName)
{
    return UsdShadeConnectableAPI(GetPrim()).CreateInput(name, typeName);
}

inline UsdShadeInput UsdShadeShader::GetInput(const TfToken& name) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetInput(name);
}

inline std::vector<UsdShadeInput> UsdShadeShader::GetInputs(bool onlyAuthored) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetInputs(onlyAuthored);
}

inline UsdAttribute UsdShadeShader::GetImplementationSourceAttr() const
{
    return UsdShadeNodeDefAPI(GetPrim()).GetImplementationSourceAttr();
}

inline UsdAttribute UsdShadeShader::CreateImplementationSourceAttr() const
{
    return UsdShadeNodeDefAPI(GetPrim()).CreateImplementationSourceAttr();
}

inline UsdAttribute UsdShadeShader::GetIdAttr() const
{
    return UsdShadeNodeDefAPI(GetPrim()).GetIdAttr();
}

inline UsdAttribute UsdShadeShader::CreateIdAttr() const
{
    return UsdShadeNodeDefAPI(GetPrim()).CreateIdAttr();
}

inline TfToken UsdShadeShader::GetImplementationSource() const
{
    return UsdShadeNodeDefAPI(GetPrim()).GetImplementationSource();
}

inline bool UsdShadeShader::SetShaderId(const TfToken& id) const
{
    return UsdShadeNodeDefAPI(GetPrim()).SetShaderId(id);
}

inline bool UsdShadeShader::GetShaderId(TfToken* id) const
{
    return UsdShadeNodeDefAPI(GetPrim()).GetShaderId(id);
}

inline bool UsdShadeShader::SetSourceAsset(const SdfAssetPath& sourceAsset, const TfToken& sourceType) const
{
    return UsdShadeNodeDefAPI(GetPrim()).SetSourceAsset(sourceAsset, sourceType);
}

inline bool UsdShadeShader::GetSourceAsset(SdfAssetPath* sourceAsset, const TfToken& sourceType) const
{
    return UsdShadeNodeDefAPI(GetPrim()).GetSourceAsset(sourceAsset, sourceType);
}

inline bool UsdShadeShader::SetSourceAssetSubIdentifier(const TfToken& subIdentifier, const TfToken& sourceType) const
{
    return UsdShadeNodeDefAPI(GetPrim()).SetSourceAssetSubIdentifier(subIdentifier, sourceType);
}

inline bool UsdShadeShader::GetSourceAssetSubIdentifier(TfToken* subIdentifier, const TfToken& sourceType) const
{
    return UsdShadeNodeDefAPI(GetPrim()).GetSourceAssetSubIdentifier(subIdentifier, sourceType);
}

inline bool UsdShadeShader::SetSourceCode(const std::string& sourceCode, const TfToken& sourceType) const
{
    return UsdShadeNodeDefAPI(GetPrim()).SetSourceCode(sourceCode, sourceType);
}

inline bool UsdShadeShader::GetSourceCode(std::string* sourceCode, const TfToken& sourceType) const
{
    return UsdShadeNodeDefAPI(GetPrim()).GetSourceCode(sourceCode, sourceType);
}

} // namespace usdrt
