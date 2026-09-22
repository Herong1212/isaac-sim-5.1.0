// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file INode.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::INode.
#pragma once

#include <omni/graph/exec/unstable/ConstName.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Span.h>
#include <omni/graph/exec/unstable/Types.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class IDef;
class INode_abi;
class INode;
class INodeDef;
class INodeGraphDef;
class ITopology;

//! Represents work in a graph.  Nodes point to a shared execution definition to state the actual work.
//!
//! @ref omni::graph::exec::unstable::INode is the main structural component used to build a graph's topology.  @ref
//! omni::graph::exec::unstable::INode stores edges to *parents* (i.e. predecessors) and *children* (i.e. successors).
//! These edges set an ordering between nodes.  See @ref omni::graph::exec::unstable::INode::getParents() and @ref
//! omni::graph::exec::unstable::INode::getChildren() respectively.
//!
//! A node represents work to be performed.  The description of the work to be performed is stored in a *definition*
//! (i.e. @ref omni::graph::exec::unstable::IDef).  Each node wishing to perform work points to a definition (see @ref
//! omni::graph::exec::unstable::INode::getDef()).
//!
//! The definition to which a node points can be one of two types.  The first type, @ref
//! omni::graph::exec::unstable::INodeDef, defines work opaquely (i.e. EF is unable to view the work definition and
//! potentially optimize it). The second type, @ref omni::graph::exec::unstable::INodeGraphDef, defines work with a
//! graph. This last representation is the most power as it allows for both *extensibilty* and *composibility* in EF.
//!
//! @rst
//!
//! .. image:: /../docs/ef-simple-w-defs.svg
//!     :align: center
//!
//! @endrst
//!
//! Above, we see that nodes point to graph definitions, which contain other nodes that point to other graph
//! definitions.  This structure of graphs pointing to other graphs is where EF gets its *graph of graphs* name.
//!
//! Not all nodes will point to a definition.  For example, the @rstref{root node <ef_root_node>} in each graph
//! definition will not point to a definition.
//!
//! A node is always part of a graph definition and the graph definition's executor is responsible for orchestrating and
//! generating work to the scheduler.
//!
//! Node's within a graph definition are assigned a unique index, between zero and the number of nodes in the
//! definition. This index is often used as a lookup into transient arrays used to store state during graph traversals.
//! See @ref omni::graph::exec::unstable::INode::getIndexInTopology().
//!
//! Nodes have a notion of validity.  See @rstref{Graph Invalidation <ef_graph_invalidation>} for details.
//!
//! @ref omni::graph::exec::unstable::INode does not contain methods for either settings the node's definition or
//! connecting nodes to each other.  This functionality is reserved for @ref omni::graph::exec::unstable::IGraphBuilder.
//! See @rstref{Graph Construction <ef_pass_concepts>} for details.
//!
//! See @rstref{Graph Concepts <ef_graph_concepts>} for a guide on how this object relates to other objects in the
//! Execution Framework.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! Users may wish to implement this interface to store meaningful authoring level data in EF.  For example, OmniGraph
//! uses an implementation of this node to store graph instancing information.  See @ref
//! omni::graph::exec::unstable::Node for a concrete implementation of this interface suitable for inheriting.
class INode_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.INode")>
{
public:
    using NodeArray = Span<INode* const>; //!< Stores the list of parents and children.

protected:
    //! Access topology owning this node.
    //!
    //! The returned pointer will not be @c nullptr.
    //!
    //! The returned @ref omni::graph::exec::unstable::ITopology will *not* have @ref omni::core::IObject::acquire()
    //! called before being returned.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") ITopology* getTopology_abi() noexcept = 0;

    //! Access node's unique identifier name.
    //!
    //! The lifetime of the returned object is tied to this node.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("ref") const ConstName* getName_abi() noexcept = 0;

    //! Access nodes unique index withing owning topology. Index will be always smaller than topology size.
    //!
    //! @thread_safety This method is thread safe.
    virtual NodeIndexInTopology getIndexInTopology_abi() noexcept = 0;

    //! Access parents.
    //!
    //! The returned @ref omni::graph::exec::unstable::INode objects will *not* have @ref omni::core::IObject::acquire()
    //! called before being returned.
    //!
    //! @thread_safety This method makes no guarantees on thread safety.  However, in practice, accessing the parents
    //! during execution is safe as the list of parents is not expected to change during execution.  Accessing the
    //! parents during graph construction requires coordination with the passes building the graph.
    virtual Span<INode* const> getParents_abi() noexcept = 0;

    //! Access children.
    //!
    //! The returned @ref omni::graph::exec::unstable::INode objects will *not* have @ref omni::core::IObject::acquire()
    //! called before being returned.
    //!
    //! @thread_safety This method makes no guarantees on thread safety.  However, in practice, accessing the children
    //! during execution is safe as the list of children is not expected to change during execution.  Accessing the
    //! children during graph construction requires coordination with the passes building the graph.
    virtual Span<INode* const> getChildren_abi() noexcept = 0;

    //! Return number of parents that cause cycles within the graph during traversal over this node.
    //!
    //! @thread_safety This method makes no guarantees on thread safety.  However, in practice, accessing this count
    //! during execution is safe as the cycle count is expected to be computed during graph construction.  Accessing the
    //! count during graph construction requires coordination with the passes building the graph.
    virtual uint32_t getCycleParentCount_abi() noexcept = 0;

    //! Check if topology/connectivity of nodes is valid within current topology version.
    //!
    //! See @rstref{Graph Invalidation <ef_graph_invalidation>} for details on invalidation.
    //!
    //! @thread_safety This method is not thread safe.
    virtual bool isValidTopology_abi() noexcept = 0;

    //! Check if this node is valid in the topology, dropping all connections if it is not.
    //!
    //! This method checks if the node is valid in the topology (i.e. checks the node's topology stamp with the
    //! topology).  If it is not valid, all parent and child connections are removed and the cycle count is set back to
    //! zero.
    //!
    //! If the node is valid in the topology, this method does nothing.
    //!
    //! See @rstref{Graph Invalidation <ef_graph_invalidation>} to better understand stamps, topologies, and
    //! invalidation.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void validateOrResetTopology_abi() noexcept = 0;

    //! Access the node's definition (can be empty).
    //!
    //! When you wish to determine if the attached definition is either opaque or a graph, consider calling @ref
    //! omni::graph::exec::unstable::INode::getNodeDef() or @ref omni::graph::exec::unstable::INode::getNodeGraphDef()
    //! rather than this method.
    //!
    //! The returned @ref omni::graph::exec::unstable::IDef will *not* have @ref omni::core::IObject::acquire() called
    //! before being returned.
    //!
    //! @thread_safety This method is thread safe during execution since the definition is not expected to change during
    //! execution.  During construction, access to this method must be coordinated between the passes building the
    //! graph.
    virtual OMNI_ATTR("no_acquire") IDef* getDef_abi() noexcept = 0;

    //! Access node definition (can be empty).
    //!
    //! If the returned pointer is @c nullptr, either the definition does not implement @ref
    //! omni::graph::exec::unstable::INodeDef or there is no definition attached to the node.
    //!
    //! The returned @ref omni::graph::exec::unstable::INodeDef will *not* have @ref omni::core::IObject::acquire()
    //! called before being returned.
    //!
    //! Also see @ref omni::graph::exec::unstable::INode::getDef() and @ref
    //! omni::graph::exec::unstable::INode::getNodeGraphDef().
    //!
    //! @thread_safety This method is thread safe during execution since the definition is not expected to change during
    //! execution.  During construction, access to this method must be coordinated between the passes building the
    //! graph.
    virtual OMNI_ATTR("no_acquire") INodeDef* getNodeDef_abi() noexcept = 0;

    //! Access node's graph definition (can be empty)
    //!
    //! The returned graph definition pointer is the graph definition which defines the work this node represents.  The
    //! returned pointer **is not** the graph definition that contains this node.
    //!
    //! If the returned pointer is @c nullptr, either the definition does not implement @ref
    //! omni::graph::exec::unstable::INodeGraphDef or there is no definition attached to the node.
    //!
    //! The returned @ref omni::graph::exec::unstable::INodeGraphDef will *not* have @ref omni::core::IObject::acquire()
    //! called before being returned.
    //!
    //! Also see @ref omni::graph::exec::unstable::INode::getDef() and @ref
    //! omni::graph::exec::unstable::INode::getNodeDef().
    //!
    //! @thread_safety This method is thread safe during execution since the definition is not expected to change during
    //! execution.  During construction, access to this method must be coordinated between the passes building the
    //! graph.
    virtual OMNI_ATTR("no_acquire") INodeGraphDef* getNodeGraphDef_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref INode.
using NodePtr = omni::core::ObjectPtr<INode>;

//! Converts an contiguous array of @ref NodePtr to a @ref Span.  This is useful when returning the array via the ABI.
//!
//! No data is copied during this conversion.  This method simply extracts a pointer to the node array and places it in
//! a span.
//!
//! The returned @ref omni::graph::exec::unstable::INode objects will *not* have @ref omni::core::IObject::acquire()
//! called before being returned.
inline Span<INode* const> toSpan(const std::vector<omni::core::ObjectPtr<INode>>& nodes) noexcept;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/INode.gen.h>

//! @copydoc omni::graph::exec::unstable::INode_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::INode : public omni::core::Generated<omni::graph::exec::unstable::INode_abi>
{
public:
    //! Returns the root of the graph definition of which this node is a part.
    //!
    //! @thread_safety This method is thread safe.
    inline INode* getRoot() noexcept;

    //! Check if this node is the root of the graph/topology.
    //!
    //! @thread_safety This method is thread safe.
    inline bool isRoot() noexcept;

    //! Check if a given node is a parent of this node.
    //!
    //! The given node may be @c nullptr.
    //!
    //! @thread_safety This method makes no guarantees on thread safety.  However, in practice, accessing the parents
    //! during execution is safe as the list of parents is not expected to change during execution.  Accessing the
    //! parents during graph construction requires coordination with the passes building the graph.
    inline bool hasParent(omni::core::ObjectParam<INode> parent) noexcept;

    //! Check if a given node is a child of this node.
    //!
    //! The given node may be @c nullptr.
    //!
    //! @thread_safety This method makes no guarantees on thread safety.  However, in practice, accessing the children
    //! during execution is safe as the list of children is not expected to change during execution.  Accessing the
    //! children during graph construction requires coordination with the passes building the graph.
    inline bool hasChild(omni::core::ObjectParam<INode> child) noexcept;
};

#include <omni/graph/exec/unstable/INodeDef.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>
#include <omni/graph/exec/unstable/ITopology.h>

inline omni::graph::exec::unstable::INode* omni::graph::exec::unstable::INode::getRoot() noexcept
{
    return getTopology()->getRoot();
}

inline bool omni::graph::exec::unstable::INode::isRoot() noexcept
{
    return (getRoot() == this);
}

inline bool omni::graph::exec::unstable::INode::hasParent(omni::core::ObjectParam<INode> parent) noexcept
{
    auto parents = getParents();
    return std::find(parents.begin(), parents.end(), parent.get()) != parents.end();
}

inline bool omni::graph::exec::unstable::INode::hasChild(omni::core::ObjectParam<INode> child) noexcept
{
    auto children = getChildren();
    return std::find(children.begin(), children.end(), child.get()) != children.end();
}

#ifndef DOXYGEN_BUILD

inline omni::graph::exec::unstable::Span<omni::graph::exec::unstable::INode* const> omni::graph::exec::unstable::toSpan(
    const std::vector<omni::graph::exec::unstable::NodePtr>& nodes) noexcept
{
    static_assert(sizeof(NodePtr) == sizeof(INode*), "NodePtr should be the same size as INode*"); // LCOV_EXCL_LINE

    // ObjectPtr is really just a raw pointer (we kinda prove that above with the static_assert). std::vector<NodePtr>
    // is a contiguous array of ObjectPtr, making it a contiguous array of raw pointers. so, if we grab a pointer to the
    // start of std::vector's buffer, we're really grabbing a pointer to a raw pointer (i.e. INode**). the
    // reinterpret_cast below exploits this.
    return !nodes.empty() ? Span<INode* const>{ reinterpret_cast<INode* const*>(&(nodes[0])), nodes.size() } :
                            Span<INode* const>{ nullptr, 0 };
}

#endif

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/INode.gen.h>
