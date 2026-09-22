// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IGraphBuilder.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGraphBuilder.
#pragma once

#include <omni/core/ResultError.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/NodePartition.h>
#include <omni/graph/exec/unstable/Span.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IGraph;
class IGraphBuilder_abi;
class IGraphBuilder;
class IGraphBuilderContext;
class IGraphBuilderNode;
class INode;
class IDef;
class INodeDef;
class INodeGraphDef;
class ITopology;

//! Graph builder is the only class that has the ability to modify topology of a graph.
//!
//! Topological edits of the graph are only allowed during graph transformation and should never be performed during
//! execution of the graph. Construction of the builder will automatically drop all the connections between nodes.
//!
//! @thread_safety Methods on this class mutating a graph topology are not thread-safe (unless documented otherwise)
class IGraphBuilder_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.IGraphBuilder")>
{
protected:
    //! Return the top-level execution graph who owns the graph definition this builder is modifying.
    //!
    //! The returned @ref omni::graph::exec::unstable::IGraph will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") IGraph* getGraph_abi() noexcept = 0;

    //! Returns the topology this builder can modify.
    //!
    //! The returned @ref omni::graph::exec::unstable::ITopology will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") ITopology* getTopology_abi() noexcept = 0;

    //! Returns the context in which this builder works.
    //!
    //! The returned @ref omni::graph::exec::unstable::IGraphBuilderContext will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") IGraphBuilderContext* getContext_abi() noexcept = 0;

    //! Returns @ref omni::graph::exec::unstable::INodeGraphDef this builder is modifying.
    //!
    //! The returned @ref omni::graph::exec::unstable::INodeGraphDef will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") INodeGraphDef* getNodeGraphDef_abi() noexcept = 0;

    //! Connects two given nodes in the graph definition.
    //!
    //! The given nodes must be in the builder's graph definition topology.
    //!
    //! The given nodes must not be @c nullptr.
    //!
    //! The upstream and downstream nodes can be the same node, essentially forming a connection between a node and
    //! itself.
    //!
    //! Neither @ref omni::graph::exec::unstable::INode have @ref omni::core::IObject::acquire() called during the
    //! connection process.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void connect_abi(OMNI_ATTR("not_null") INode* upstreamNode,
                             OMNI_ATTR("not_null") INode* downstreamNode) noexcept = 0;

    //! Disconnect two given nodes.
    //!
    //! The given nodes must be in the builder's graph definition topology.
    //!
    //! The given nodes must not be @c nullptr.
    //!
    //! It is not an error if the two nodes are not connected.
    //!
    //! Neither @ref omni::graph::exec::unstable::INode have @ref omni::core::IObject::acquire() called
    //! during the disconnection process.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void disconnect_abi(OMNI_ATTR("not_null") INode* upstreamNode,
                                OMNI_ATTR("not_null") INode* downstreamNode) noexcept = 0;

    //! Remove a node from topology.
    //!
    //! The given node must be in the builder's graph definition topology.
    //!
    //! The given node can be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void remove_abi(INode* node) noexcept = 0;

    //! Sets the definition for the given node.
    //!
    //! If a definition is already set, it will be replaced by the given definition.
    //!
    //! The given node must be in the builder's graph definition topology.
    //!
    //! The given node must not be @c nullptr.
    //!
    //! The given definition may be @c nullptr.
    //!
    //! @ref omni::core::IObject::acquire() is called on the given definition pointer.
    //!
    //! See also @ref omni::graph::exec::unstable::IGraphBuilder::setNodeGraphDef().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void setNodeDef_abi(OMNI_ATTR("not_null") INode* node, INodeDef* nodeDef) noexcept = 0;

    //! Sets the graph definition for give node.
    //!
    //! If a definition is already set, it will be replaced by the given definition.
    //!
    //! The given node must be in the builder's graph definition topology.
    //!
    //! The given node must not be @c nullptr.
    //!
    //! The given definition may be @c nullptr.
    //!
    //! @ref omni::core::IObject::acquire() is called on the given definition pointer.
    //!
    //! See also @ref omni::graph::exec::unstable::IGraphBuilder::setNodeDef().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void setNodeGraphDef_abi(OMNI_ATTR("not_null") INode* node, INodeGraphDef* nodeGraphDef) noexcept = 0;

    //! Removes the given node's definition.
    //!
    //! The given node must be in the builder's graph definition topology.
    //!
    //! The given node must not be @c nullptr.
    //!
    //! If the definition is already @c nullptr, this method does nothing.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void clearDef_abi(OMNI_ATTR("not_null") INode* node) noexcept = 0;

    //! Replace a well formed cluster of nodes with a single node and the given definition.
    //!
    //! All nodes in the partition must by in the builder's graph definition topology.
    //!
    //! All nodes in the partition must not be @c nullptr.
    //!
    //! The given partition pointer must not be @c nullptr.
    //!
    //! The given definition may be @c nullptr.
    //!
    //! If the given partition is empty, this method does nothing.
    //!
    //! The node graph definition this builder is modifying must support node creation (e.g. @ref
    //! omni::graph::exec::unstable::INodeGraphDef::getNodeFactory() must return a valid factory).
    //!
    //! @ref omni::core::IObject::acquire() is called on the given definition pointer.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void replacePartition_abi(OMNI_ATTR("in, not_null, ref") const NodePartition* partition,
                                      IDef* definition) noexcept = 0;

    //! Create a new node in the builder's node graph definition.
    //!
    //! The given node name must not be @c nullptr.
    //!
    //! The given definition can be @c nullptr.
    //!
    //! Node creation can return @c nullptr when the builder's node graph definition doesn't allow node construction
    //! outside of the pass that created it (i.e. @ref omni::graph::exec::unstable::INodeGraphDef::getNodeFactory()
    //! returns `nullptr`).
    //!
    //! The returned @ref omni::graph::exec::unstable::INode will not have @ref omni::core::IObject::acquire() called on
    //! it.  It is assumed the returned node will be owned by the builder's graph definition.
    //!
    //! @thread_safety This method is not thread safe.
    virtual OMNI_ATTR("no_acquire") INode* createNode_abi(OMNI_ATTR("in, not_null, c_str") const char* name,
                                                          IDef* def) noexcept = 0;

    //! Access nodes created by this builder.
    //!
    //! The returned span is no longer valid when the topology of the builder's graph changes.
    //!
    //! Nodes returned in this list may not be valid in the builder's graph definition topology.  This can happen if a
    //! previously created node was removed by a subsequent pass. Users can check if a returned node is valid within the
    //! topology with @ref omni::graph::exec::unstable::INode::isValidTopology().
    //!
    //! The pointers in the span are non-owning, i.e. each @ref omni::graph::exec::unstable::INode will not have
    //! @ref omni::core::IObject::acquire() called on it before returning.
    //!
    //! @thread_safety This method is not thread safe.
    virtual Span<INode* const> getCreatedNodes_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref IGraphBuilder.
using GraphBuilderPtr = omni::core::ObjectPtr<IGraphBuilder>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IGraphBuilder.gen.h>

//! @copydoc omni::graph::exec::unstable::IGraphBuilder_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IGraphBuilder
    : public omni::core::Generated<omni::graph::exec::unstable::IGraphBuilder_abi>
{
public:
    //! Return the root node of the graph definition this builder is modifying.
    //!
    //! The returned @ref INode. will *not* have @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.
    inline INode* getRoot() noexcept;

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::createNode_abi
    INode* createNode(const std::string& name, omni::core::ObjectParam<IDef> def) noexcept
    {
        return createNode_abi(name.c_str(), def.get());
    }

    using omni::core::Generated<omni::graph::exec::unstable::IGraphBuilder_abi>::createNode;
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/IGraphBuilderNode.h>
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/INodeDef.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>

inline omni::graph::exec::unstable::INode* omni::graph::exec::unstable::IGraphBuilder::getRoot() noexcept
{
    return getNodeGraphDef()->getRoot();
}

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IGraphBuilder.gen.h>
