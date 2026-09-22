// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IGraphBuilderNode.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGraphBuilderNode.
#pragma once

#include <omni/core/ResultError.h>
#include <omni/graph/exec/unstable/ConstName.h>
#include <omni/graph/exec/unstable/ElementAt.h>
#include <omni/graph/exec/unstable/IBase.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IGraphBuilderNode;
class IGraphBuilderNode_abi;
class INode;
class INodeDef;
class INodeGraphDef;
class ITopology;

//! Describes a node @ref omni::graph::exec::unstable::IGraphBuilder can manipulate.
//!
//! Only @ref omni::graph::exec::unstable::IGraphBuilder should use @ref omni::graph::exec::unstable::IGraphBuilderNode.
//! One way to think about this interface is that it is a private interface used by
//! @ref omni::graph::exec::unstable::IGraphBuilder to connect instances of @ref omni::graph::exec::unstable::INode.
class IGraphBuilderNode_abi : public omni::core::Inherits<omni::graph::exec::unstable::IBase,
                                                          OMNI_TYPE_ID("omni.graph.exec.unstable.IGraphBuilderNode")>
{
protected:
    //! Adds the given node as a parent (i.e. upstream) of this node.
    //!
    //! @ref omni::core::IObject::acquire() is not called on the given node.  It is up to the calling code to ensure the
    //! node persists while in use by this interface.
    //!
    //! @p parent must not be @c nullptr.
    //!
    //! It is undefined behavior to add a parent multiple times to a node.
    //!
    //! Do not directly call this method.  Instead, call @ref omni::graph::exec::unstable::IGraphBuilder::connect().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _addParent_abi(OMNI_ATTR("not_null") IGraphBuilderNode* parent) noexcept = 0;

    //! Removes the given node as a parent.
    //!
    //! It is not an error if the given node is not a parent.
    //!
    //! The given node may be @c nullptr.
    //!
    //! Do not directly call this method.  Instead, call @ref omni::graph::exec::unstable::IGraphBuilder::disconnect().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _removeParent_abi(IGraphBuilderNode* parent) noexcept = 0;

    //! Adds the given node as a child (i.e. downstream) of this node.
    //!
    //! @ref omni::core::IObject::acquire() is not called on the given node.  It is up to the calling code to ensure the
    //! node persists while in use by this interface.
    //!
    //! @p child must not be @c nullptr.
    //!
    //! It is undefined behavior to add a child multiple times to a node.
    //!
    //! Do not directly call this method.  Instead, call @ref omni::graph::exec::unstable::IGraphBuilder::connect().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _addChild_abi(OMNI_ATTR("not_null") IGraphBuilderNode* child) noexcept = 0;

    //! Removes the given node as a child.
    //!
    //! It is not an error if the given node is not a parent.
    //!
    //! The given node may not be @c nullptr.
    //!
    //! Do not directly call this method.  Instead, call @ref omni::graph::exec::unstable::IGraphBuilder::disconnect().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _removeChild_abi(IGraphBuilderNode* child) noexcept = 0;

    //! Remove from this node's parent list any nodes that no longer exist in current topology, i.e are invalid.
    //!
    //! @ref omni::core::IObject::release() is not called on the invalid nodes.
    //!
    //! Do not directly call this method.  It is used internally by @ref omni::graph::exec::unstable::IGraphBuilder.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _removeInvalidParents_abi() noexcept = 0;

    //! Remove from this node's children list any nodes that no longer exist in current topology, i.e are invalid.
    //!
    //! @ref omni::core::IObject::release() is not called on the invalid nodes.
    //!
    //! Do not directly call this method.  It is used internally by @ref omni::graph::exec::unstable::IGraphBuilder.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _removeInvalidChildren_abi() noexcept = 0;

    //! Invalidate all children and parents connections by invalidating the topology stamp this node is synchronized
    //! with.
    //!
    //! @warning This only removes connections on a single node. The topology has bi-directional connections
    //! for every node with the exception of the connection with the root node.
    //!
    //! Do not directly call this method.  It is used internally by @ref omni::graph::exec::unstable::IGraphBuilder.
    //!
    //! @thread_safety This method is thread safe.
    virtual void _invalidateConnections_abi() noexcept = 0;

    //! Sets the number of parents who are a part of cycle.
    //!
    //! @thread_safety This method is not thread safe.
    virtual void setCycleParentCount_abi(uint32_t count) noexcept = 0;

    //! Sets the definition for this node.
    //!
    //! If a definition is already set, it will be replaced by the given definition.
    //!
    //! The given definition may be @c nullptr.
    //!
    //! @ref omni::core::IObject::acquire() is called on the given pointer.
    //!
    //! See also  @ref omni::graph::exec::unstable::IGraphBuilderNode::_setNodeGraphDef().
    //!
    //! Do not directly call this method.  Instead, call @ref omni::graph::exec::unstable::IGraphBuilder::setNodeDef().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _setNodeDef_abi(INodeDef* nodeDef) noexcept = 0;

    //! Sets the definition for this node.
    //!
    //! If a definition is already set, it will be replaced by the given definition.
    //!
    //! The given definition may be @c nullptr.
    //!
    //! @ref omni::core::IObject::acquire() is called on the given pointer.
    //!
    //! See also  @ref omni::graph::exec::unstable::IGraphBuilderNode::_setNodeDef().
    //!
    //! Do not directly call this method.  Instead, call @ref
    //! omni::graph::exec::unstable::IGraphBuilder::setNodeGraphDef().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void _setNodeGraphDef_abi(INodeGraphDef* nodeGraphDef) noexcept = 0;

    //! Unsets this node's definition.
    //!
    //! If the definition is already @c nullptr, this method does nothing.
    //!
    //! Do not directly call this method.  Instead, call @ref omni::graph::exec::unstable::IGraphBuilder::clearDef().

    //! @thread_safety This method is not thread safe.
    virtual void _clearDef_abi() noexcept = 0;

    //! Access the topology owning this node.
    //!
    //! The returned @ref omni::graph::exec::unstable::ITopology will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! The returned pointer is always valid.
    //!
    //! @thread_safety This method is not thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") ITopology* getTopology_abi() noexcept = 0;

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

    //! Access the parent at the given index.
    //!
    //! It is an error if the the given index is greater than the parent count.
    //!
    //! See @ref omni::graph::exec::unstable::IGraphBuilderNode::getParentCount().
    //!
    //! Consider using @ref omni::graph::exec::unstable::IGraphBuilderNode::getParents() for a modern C++ wrapper to
    //! this method.
    //!
    //! The returned @ref omni::graph::exec::unstable::IGraphBuilderNode will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! The returned pointer will not be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") IGraphBuilderNode* getParentAt_abi(uint64_t index) noexcept = 0;

    //! Returns the number of parents.
    //!
    //! @thread_safety This method is not thread safe.
    virtual uint64_t getParentCount_abi() noexcept = 0;

    //! Access the child at the given index.
    //!
    //! It is an error if the the given index is greater than the child count.
    //!
    //! See @ref omni::graph::exec::unstable::IGraphBuilderNode::getChildCount().
    //!
    //! Consider using @ref omni::graph::exec::unstable::IGraphBuilderNode::getChildren()
    //! for a modern C++ wrapper to this method.
    //!
    //! The returned @ref omni::graph::exec::unstable::IGraphBuilderNode will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! The returned pointer will not be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") IGraphBuilderNode* getChildAt_abi(uint64_t index) noexcept = 0;

    //! Returns the number of children.
    //!
    //! @thread_safety This method is not thread safe.
    virtual uint64_t getChildCount_abi() noexcept = 0;

    //! Returns @c true if the given node is an immediate child of this node.
    //!
    //! @p node may be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual bool hasChild_abi(IGraphBuilderNode* node) noexcept = 0;

    //! Returns @c true if this node is the root of the topology.
    //!
    //! @thread_safety This method is not thread safe.
    virtual bool isRoot_abi() noexcept = 0;

    //! Returns the root node of the topology of which this node is a part.
    //!
    //! The returned @ref omni::graph::exec::unstable::IGraphBuilderNode will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! The returned pointer will not be @c nullptr.
    //!
    //! @thread_safety This method is not thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") IGraphBuilderNode* getRoot_abi() noexcept = 0;

    //! Access node's unique identifier name.
    //!
    //! The lifetime of the returned object is tied to this node.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("ref") const ConstName* getName_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref IGraphBuilderNode.
using GraphBuilderNodePtr = omni::core::ObjectPtr<IGraphBuilderNode>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IGraphBuilderNode.gen.h>

//! @copydoc omni::graph::exec::unstable::IGraphBuilderNode_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IGraphBuilderNode
    : public omni::core::Generated<omni::graph::exec::unstable::IGraphBuilderNode_abi>
{
public:
#ifndef DOXYGEN_BUILD
    //! Implementation detail to access parent ABI.
    struct GetParent
    {
        //! Access element at a given index
        static void getAt(IGraphBuilderNode* owner, uint64_t index, IGraphBuilderNode** out) noexcept
        {
            *out = owner->getParentAt(index);
        }

        //! Returns element count
        static uint64_t getCount(IGraphBuilderNode* owner) noexcept
        {
            return owner->getParentCount();
        }
    };

    //! Implementation detail to access children ABI.
    struct GetChild
    {
        //! Access element at a given index
        static void getAt(IGraphBuilderNode* owner, uint64_t index, IGraphBuilderNode** out) noexcept
        {
            *out = owner->getChildAt(index);
        }

        //! Returns element count
        static uint64_t getCount(IGraphBuilderNode* owner) noexcept
        {
            return owner->getChildCount();
        }
    };
#endif // DOXYGEN_BUILD

    //! Iterable wrapper providing access to the node's parent.
    using Parents = detail::ElementAt<IGraphBuilderNode, IGraphBuilderNode*, GetParent>;

    //! Iterable wrapper providing access to the node's parent.
    using Children = detail::ElementAt<IGraphBuilderNode, IGraphBuilderNode*, GetChild>;

    //! Returns an object that allows the list of parents to be iterated over (i.e. using range-based for loops).
    //!
    //! @thread_safety This method is not thread safe.
    Parents getParents() noexcept
    {
        return Parents(this);
    }

    //! Returns an object that allows the list of children to be iterated over (i.e. using range-based for loops).
    //!
    //! @thread_safety This method is not thread safe.
    Children getChildren() noexcept
    {
        return Children(this);
    }
};

// additional headers needed for API implementation
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/INodeDef.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>
#include <omni/graph/exec/unstable/ITopology.h>

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IGraphBuilderNode.gen.h>
