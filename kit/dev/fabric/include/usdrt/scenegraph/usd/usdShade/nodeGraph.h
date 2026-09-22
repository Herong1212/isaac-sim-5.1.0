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

/// @file usdShade/nodeGraph.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include <utility>
#include "usdrt/scenegraph/usd/usd/editTarget.h"
#include "usdrt/scenegraph/usd/usd/relationship.h"
#include "usdrt/scenegraph/usd/usdShade/input.h"
#include "usdrt/scenegraph/usd/usdShade/output.h"
#include "usdrt/scenegraph/usd/usdShade/shader.h"
#include "usdrt/scenegraph/usd/usdShade/connectableAPIBehavior.h"*/
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
#include <usdrt/scenegraph/usd/usdShade/input.h>
#include <usdrt/scenegraph/usd/usdShade/output.h>
#include <usdrt/scenegraph/usd/usdShade/shader.h>
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
// NODEGRAPH                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdShadeNodeGraph
///
/// A node-graph is a container for shading nodes, as well as other
/// node-graphs. It has a public input interface and provides a list of public
/// outputs.
///
/// <b>Node Graph Interfaces</b>
///
/// One of the most important functions of a node-graph is to host the "interface"
/// with which clients of already-built shading networks will interact.  Please
/// see \ref UsdShadeNodeGraph_Interfaces "Interface Inputs" for a detailed
/// explanation of what the interface provides, and how to construct and
/// use it, to effectively share/instance shader networks.
///
/// <b>Node Graph Outputs</b>
///
/// These behave like outputs on a shader and are typically connected to an
/// output on a shader inside the node-graph.
///

class UsdShadeNodeGraph : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdShadeNodeGraph on UsdPrim @p prim.
    /// Equivalent to UsdShadeNodeGraph::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdShadeNodeGraph(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdShadeNodeGraph on the prim held by @p schemaObj .
    /// Should be preferred over UsdShadeNodeGraph(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdShadeNodeGraph(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdShadeNodeGraph()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdShadeNodeGraph Define(const UsdStageRefPtr& stage, const SdfPath& path);

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
    /// Constructor that takes a ConnectableAPI object.  Allow implicit
    /// (auto) conversion of UsdShadeConnectableAPI to UsdShadeNodeGraph, so
    /// that a ConnectableAPI can be passed into any function that accepts a
    /// NodeGraph.
    ///
    /// \note that the conversion may produce an invalid NodeGraph object,
    /// because not all UsdShadeConnectableAPI%s are UsdShadeNodeGraph%s
    UsdShadeNodeGraph(const UsdShadeConnectableAPI& connectable);

    /// Contructs and returns a UsdShadeConnectableAPI object with this
    /// node-graph.
    ///
    /// Note that most tasks can be accomplished without explicitly constructing
    /// a UsdShadeConnectable API, since connection-related API such as
    /// UsdShadeConnectableAPI::ConnectToSource() are static methods, and
    /// UsdShadeNodeGraph will auto-convert to a UsdShadeConnectableAPI when
    /// passed to functions that want to act generically on a connectable
    /// UsdShadeConnectableAPI object.
    UsdShadeConnectableAPI ConnectableAPI() const;

    /// \anchor UsdShadeNodeGraph_Output
    /// \name Outputs of a node-graph. These typically connect to outputs of
    /// shaders or nested node-graphs within the node-graph.
    ///
    /// @{

    /// Create an output which can either have a value or can be connected.
    /// The attribute representing the output is created in the "outputs:"
    /// namespace.
    ///
    UsdShadeOutput CreateOutput(const TfToken& name, const SdfValueTypeName& typeName) const;

    /// Return the requested output if it exists.
    ///
    UsdShadeOutput GetOutput(const TfToken& name) const;

    /// Outputs are represented by attributes in the "outputs:" namespace.
    /// If \p onlyAuthored is true (the default), then only return authored
    /// attributes; otherwise, this also returns un-authored builtins.
    ///
    std::vector<UsdShadeOutput> GetOutputs(bool onlyAuthored = true) const;

    /// \deprecated in favor of GetValueProducingAttributes on UsdShadeOutput
    /// Resolves the connection source of the requested output, identified by
    /// \p outputName to a shader output.
    ///
    /// \p sourceName is an output parameter that is set to the name of the
    /// resolved output, if the node-graph output is connected to a valid
    /// shader source.
    ///
    /// \p sourceType is an output parameter that is set to the type of the
    /// resolved output, if the node-graph output is connected to a valid
    /// shader source.
    ///
    /// \return Returns a valid shader object if the specified output exists and
    /// is connected to one. Return an empty shader object otherwise.
    /// The python version of this method returns a tuple containing three
    /// elements (the source shader, sourceName, sourceType).
    UsdShadeShader ComputeOutputSource(const TfToken& outputName,
                                       TfToken* sourceName,
                                       UsdShadeAttributeType* sourceType) const;

    /// @}

    /// \anchor UsdShadeNodeGraph_Interfaces
    /// \name Interface inputs of a node-graph.
    ///
    /// In addition to serving as the "head" for all of the shading networks
    /// that describe each render target's particular node-graph, the node-graph
    /// prim provides a unified "interface" that allows node-graphs to share
    /// shading networks while retaining the ability for each to specify its own
    /// set of unique values for the interface inputs that users may need to
    /// modify.
    ///
    /// A "Node-graph Interface" is a combination of:
    /// \li a flat collection of attributes, of arbitrary names
    /// \li for each such attribute, a list of UsdShaderInput targets
    /// whose attributes on Shader prims should be driven by the interface
    /// input.
    ///
    /// A single interface input can drive multiple shader inputs and be
    /// consumed by multiple render targets. The set of interface inputs itself
    /// is intentionally flat, to encourage sharing of the interface between
    /// render targets.  Clients are always free to create interface inputs with
    /// namespacing to segregate "private" attributes exclusive to the render
    /// target, but we hope this will be an exception.
    ///
    /// To facilitate connecting, qualifying, and interrogating interface
    /// attributes, we use the attribute schema UsdShadeInput, which also
    /// serves as an abstraction for shader inputs.
    ///
    /// <b>Scoped Interfaces</b>
    ///
    /// \todo describe scoped interfaces and fix bug/108940 to account for them.
    ///
    /// @{

    /// Create an Input which can either have a value or can be connected.
    /// The attribute representing the input is created in the "inputs:"
    /// namespace.
    ///
    /// \todo clarify error behavior if typeName does not match existing,
    /// defined attribute - should match UsdPrim::CreateAttribute - bug/108970
    ///
    UsdShadeInput CreateInput(const TfToken& name, const SdfValueTypeName& typeName) const;

    /// Return the requested input if it exists.
    ///
    UsdShadeInput GetInput(const TfToken& name) const;

    /// Returns all inputs present on the node-graph. These are represented by
    /// attributes in the "inputs:" namespace.
    /// If \p onlyAuthored is true (the default), then only return authored
    /// attributes; otherwise, this also returns un-authored builtins.
    ///
    std::vector<UsdShadeInput> GetInputs(bool onlyAuthored = true) const;

    /// @}
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdShadeNodeGraph::_GetStaticTfType()
{
    const static TfToken token("UsdShadeNodeGraph");
    return token;
}

/* virtual */
inline const TfToken UsdShadeNodeGraph::_GetTfTypeToken() const
{
    const static TfToken token("UsdShadeNodeGraph");
    return token;
}

/* static */
inline UsdShadeNodeGraph UsdShadeNodeGraph::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdShadeNodeGraph();
    }
    return UsdShadeNodeGraph(stage->DefinePrim(path, _GetStaticTfType()));
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

namespace usdrt
{

inline UsdShadeNodeGraph::UsdShadeNodeGraph(const UsdShadeConnectableAPI& connectable)
    : UsdShadeNodeGraph(connectable.GetPrim())
{
}

inline UsdShadeConnectableAPI UsdShadeNodeGraph::ConnectableAPI() const
{
    return UsdShadeConnectableAPI(GetPrim());
}

inline UsdShadeOutput UsdShadeNodeGraph::CreateOutput(const TfToken& name, const SdfValueTypeName& typeName) const
{
    return UsdShadeConnectableAPI(GetPrim()).CreateOutput(name, typeName);
}

inline UsdShadeOutput UsdShadeNodeGraph::GetOutput(const TfToken& name) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetOutput(name);
}

inline std::vector<UsdShadeOutput> UsdShadeNodeGraph::GetOutputs(bool onlyAuthored) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetOutputs(onlyAuthored);
}

inline UsdShadeShader UsdShadeNodeGraph::ComputeOutputSource(const TfToken& outputName,
                                                             TfToken* sourceName,
                                                             UsdShadeAttributeType* sourceType) const
{
    return UsdShadeShader();
}

inline UsdShadeInput UsdShadeNodeGraph::CreateInput(const TfToken& name, const SdfValueTypeName& typeName) const
{
    return UsdShadeConnectableAPI(GetPrim()).CreateInput(name, typeName);
}

inline UsdShadeInput UsdShadeNodeGraph::GetInput(const TfToken& name) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetInput(name);
}

inline std::vector<UsdShadeInput> UsdShadeNodeGraph::GetInputs(bool onlyAuthored) const
{
    return UsdShadeConnectableAPI(GetPrim()).GetInputs(onlyAuthored);
}

} // namespace usdrt
