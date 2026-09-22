// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ITopology.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::ITopology.
#pragma once

#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Stamp.h>
#include <omni/graph/exec/unstable/Types.h>

#include <type_traits>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class IInvalidationForwarder;
class INode;
class ITopology_abi;
class ITopology;

//! Unique owner of the callback. Meaning is up to the caller.  Essentially a void* pointer.
using InvalidationForwarderId = uint64_t;
static_assert(sizeof(uint64_t) >= sizeof(void*), "Target platform's pointer size is larger than expected.");

//! The Topology of a graph is stored in this class.
//!
//! @ref omni::graph::exec::unstable::ITopology is a helper interface used to quickly invalidate the topology, quickly
//! determine if the topology has been invalidated, assign each node in the topology a unique index (suitable for access
//! in contiguous memory), and provide access to the root node.
//!
//! Topologies play a large role in graph invalidation.  See @rstref{Graph Invalidation <ef_graph_invalidation>} for
//! details.
//!
//! To better understand how this object relates to other objects in the Execution Framework, see
//! @rstref{Graph Concepts <ef_graph_concepts>}.
//!
//! See @ref omni::graph::exec::unstable::Topology for a concrete implementation of this interface.
class ITopology_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.ITopology")>
{
protected:
    //! Returns the maximum node index in the topology.
    //!
    //! The returned value may be greater than the current number of nodes associated with the topology.  This may
    //! happen if a node has been deleted.  EF avoid reassigning node indices when a node is deleted, meaning it's
    //! possible for "holes" to show up in the index list.
    //!
    //! The returned value may be greater than the number of nodes that are reachable from the root node.  This may
    //! happen if a node has no parent that is either the root node or a node that has a path to the root node.
    //!
    //! A common use of this method is seen when allocating an array of data that will be indexed by each node's
    //! topology index (see @ref omni::core::exec::unstable::INode::getIndexInTopology()).
    //!
    //! @thread_safety This method is thread safe.
    virtual uint64_t getMaxNodeIndex_abi() noexcept = 0;

    //! Returns the topology's root node that allows reaching all of the valid nodes in the topology.
    //!
    //! The returned @ref omni::graph::exec::unstable::INode will *not* have @ref omni::core::IObject::acquire() called
    //! before being returned.
    //!
    //! The returned pointer will remain valid for the lifetime of this object.
    //!
    //! @thread_safety This method is thread safe.
    // ef-docs i_topology_abi_get_root_abi_begin
    virtual OMNI_ATTR("not_null, no_acquire") INode* getRoot_abi() noexcept = 0;
    // ef-docs i_topology_abi_get_root_abi_end

    //! Returns the topology stamp.  This stamp is updated each time the topology is invalidated.
    //!
    //! See omni::graph::exec::unstable::ITopology::invalidate() to invalidate the topology (and thereby update this
    //! Stamp).
    //!
    //! @thread_safety This method is thread safe.
    virtual Stamp getStamp_abi() noexcept = 0;

    //! Invalidate topology. All edges of the graph will be dropped (lazily), nodes remain valid and can be used to
    //! build new topology.
    //!
    //! See @rstref{Graph Invalidation <ef_graph_invalidation>} for details about how this method is used during
    //! invalidation.
    //!
    //! It is not recommended to call this method during graph execution.  Rather, defer invalidation until after
    //! execution.
    //!
    //! @thread_safety This method is thread safe.
    virtual void invalidate_abi() noexcept = 0;

    //! Returns a unique index for a node in this topology.
    //!
    //! Users should not call this method.  Only the constructors of implementations of @ref
    //! omni::graph::exec::unstable::INode should call this method.
    //!
    //! See @ref omni::graph::exec::unstable::ITopology::releaseNodeIndex().
    //!
    //! @thread_safety This method is not thread safe.
    virtual NodeIndexInTopology acquireNodeIndex_abi() noexcept = 0;

    //! Release unique index of a node in this topology. Shouldn't be used by anything else than a node's destructor.
    //!
    //! See @ref omni::graph::exec::unstable::ITopology::acquireNodeIndex().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void releaseNodeIndex_abi(NodeIndexInTopology index) noexcept = 0;

    //! Add a callback to forward invalidation to other entities.
    //!
    //! At a minimum, the top-level @ref omni::graph::exec::unstable::IGraph will register a invalidation callback with
    //! all topologies created within a pass pipeline. This allows tracking invalidation and triggering minimal graph
    //! rebuild.
    //!
    //! In the future, override passes can generate new graphs and still track authoring invalidation by registering to
    //! the original graph topologies invalidation.
    //!
    //! The given @ref omni::graph::exec::unstable::IInvalidationForwarder will be stored and have @ref
    //! omni::core::IObject::acquire() called.
    //!
    //! If @p owner has a current forwarder, it will be replaced with the given forwarder.
    //!
    //! The given callback must not be @c nullptr.
    //!
    //! See @rstref{Graph Invalidation <ef_graph_invalidation>} for details about how this method is used during
    //! invalidation.
    //!
    //! See @ref omni::graph::exec::unstable::ITopology::removeInvalidationForwarder().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void addInvalidationForwarder_abi(InvalidationForwarderId owner,
                                              OMNI_ATTR("not_null") IInvalidationForwarder* callback) noexcept = 0;

    //! Remove invalidation forwarding for a given owner.
    //!
    //! If the given owner is not known, this method does nothing.
    //!
    //! See @ref omni::graph::exec::unstable::ITopology::addInvalidationForwarder().
    //!
    //! @thread_safety This method is not thread safe.
    virtual void removeInvalidationForwarder_abi(InvalidationForwarderId owner) noexcept = 0;

    //! Get construction version this topology is synchronized with.
    //!
    //! @thread_safety This method is thread safe.
    virtual SyncStamp getConstructionStamp_abi() noexcept = 0;

    //! Private method only for IGraphBuilder, used to tag construction version.
    //!
    //! @thread_safety Calling this method concurrently is not recommended.
    virtual void _setConstructionInSync_abi(Stamp toSync) noexcept = 0;
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/ITopology.gen.h>

//! @copydoc omni::graph::exec::unstable::ITopology_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::ITopology : public omni::core::Generated<omni::graph::exec::unstable::ITopology_abi>
{
public:
    //! Check if the topology is valid.
    //!
    //! A topology is considered valid if the topology's root node stamp is in-sync with the topology (this usually
    //! happens during graph construction).
    //!
    //! See @rstref{Graph Invalidation <ef_graph_invalidation>} for details about how this method is used during
    //! invalidation.
    //!
    //! @thread_safety This method is thread safe.
    inline bool isValid() noexcept;

    //! Add a callback allowing to forward invalidation to other graphs.
    //!
    //! At a minimum, the top-level @ref omni::graph::exec::unstable::IGraph will register a invalidation callback with
    //! all topologies created within a pass pipeline. This allows tracking invalidation and triggering minimal graph
    //! rebuild.
    //!
    //! In the future, override passes can generate new graphs and still track authoring invalidation by registering to
    //! the original graph topologies invalidation.
    //!
    //! If @p owner has a current forwarder, it will be replaced with the given forwarder.
    //!
    //! See @rstref{Graph Invalidation <ef_graph_invalidation>} for details about how this method is used during
    //! invalidation.
    //!
    //! See @ref omni::graph::exec::unstable::ITopology::removeInvalidationForwarder().
    //!
    //! The supplied function should have the signature of `void(ITopology*)`.
    //!
    //! @thread_safety This method is not thread safe.
    template <typename Fn>
    inline void addInvalidationForwarder(InvalidationForwarderId owner, Fn&& fn);
};

#include <omni/graph/exec/unstable/IInvalidationForwarder.h>
#include <omni/graph/exec/unstable/INode.h>

inline bool omni::graph::exec::unstable::ITopology::isValid() noexcept
{
    return getRoot()->isValidTopology();
}

template <typename Fn>
inline void omni::graph::exec::unstable::ITopology::addInvalidationForwarder(InvalidationForwarderId owner, Fn&& fn)
{
    class Forwarder : public Implements<IInvalidationForwarder>
    {
    public:
        Forwarder(Fn&& fn) : m_fn(std::move(fn))
        {
        }

    protected:
        void invoke_abi(ITopology* topology) noexcept override
        {
            m_fn(topology);
        }

        Fn m_fn;
    };

    addInvalidationForwarder_abi(owner, omni::core::steal(new Forwarder(std::forward<Fn>(fn))).get());
}

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/ITopology.gen.h>
