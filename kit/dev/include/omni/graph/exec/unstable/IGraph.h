// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file IGraph.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGraph.
#pragma once

#include <omni/graph/exec/unstable/ConstName.h>
#include <omni/graph/exec/unstable/IBase.h>
#include <omni/graph/exec/unstable/Stamp.h>
#include <omni/graph/exec/unstable/Status.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

// forward declarations needed by interface declaration
class IExecutionContext;
class IGraph_abi;
class IGraph;
class INode;
class INodeGraphDef;
class ITopology;

//! Top-level container for storing the Execution Framework's graph of graphs.
//!
//! @ref omni::graph::exec::unstable::IGraph is the top-level container used to store the graph of graphs.  This
//! top-level container is referred to as the <i>execution graph</i>.
//!
//! @ref omni::graph::exec::unstable::IGraph's responsibilities include:
//!
//! - Tracking if the graph is currently being constructed.  See @ref omni::graph::exec::unstable::IGraph::inBuild().
//!
//! - Tracking gross changes to the topologies of graphs within the execution graph.  This is done with the <i>global
//!   topology stamp</i> (see @ref omni::graph::exec::unstable::IGraph::getGlobalTopologyStamp()).  Each time a topology
//!   is invalidated, the global topology stamp is incremented.  Consumers of the execution graph can use this stamp to
//!   detect changes in the graph.  See @rstref{Graph Invalidation <ef_graph_invalidation>} for details.
//!
//! - Owning and providing access to the top level graph definition (see @ref
//!   omni::graph::exec::unstable::IGraph::getNodeGraphDef()).  The root node of the top-level graph definition is the
//!   root of execution graph.  @ref omni::graph::exec::unstable::IGraph is the only container, other than @ref
//!   omni::graph::exec::unstable::INode, that attaches to definitions.
//!
//! See @rstref{Graph Concepts <ef_graph_concepts>} for more information on how @ref omni::graph::exec::unstable::IGraph
//! fits into the Execution Framework.
//!
//! See @ref omni::graph::exec::unstable::Graph for a concrete implementation of this interface.
class IGraph_abi
    : public omni::core::Inherits<omni::graph::exec::unstable::IBase, OMNI_TYPE_ID("omni.graph.exec.unstable.IGraph")>
{
protected:
    //! Access the top-level node graph definition.
    //!
    //! The returned @ref omni::graph::exec::unstable::INodeGraphDef will *not* have
    //! @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.  The returned pointer will be valid for the lifetime of this @ref
    //! omni::graph::exec::unstable::IGraph.
    virtual OMNI_ATTR("not_null, no_acquire") INodeGraphDef* getNodeGraphDef_abi() noexcept = 0;

    //! Name set on the graph during construction.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.  The returned pointer will be valid for the lifetime of this @ref
    //! omni::graph::exec::unstable::IGraph.
    virtual OMNI_ATTR("ref") const ConstName* getName_abi() noexcept = 0;

    //! Return global topology of the graph. Useful when detecting that graph transformation pipeline needs to run.
    //!
    //! See @rstref{Graph Invalidation <ef_graph_invalidation>} to understand how this stamp is used to detect changes
    //! in the graph.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.  The returned pointer will be valid for the lifetime of this @ref
    //! omni::graph::exec::unstable::IGraph.  It is up to the caller to mutate the stamp in a thread safe manner.
    virtual Stamp* getGlobalTopologyStamp_abi() noexcept = 0;

    //! Return @c true if a @ref omni::graph::exec::unstable::IGraphBuilder is currently building a part of this graph.
    //!
    //! @thread_safety This method is thread safe.
    virtual bool inBuild_abi() noexcept = 0;

    //! Mark that an @ref omni::graph::exec::unstable::IGraphBuilder is currently building a part of this graph.
    //!
    //! Each builder should call @c _setInBuild(true) followed by @c _setInBuild(false) once building is complete. Since
    //! multiple builders can be active at a time, it is safe for this method to be called multiple times.
    //!
    //! This method should only be called by @ref omni::graph::exec::unstable::IGraphBuilder.
    //!
    //! @thread_safety This method is thread safe.
    virtual void _setInBuild_abi(bool inBuild) noexcept = 0;
};

//! Smart pointer managing an instance of @ref IGraph.
using GraphPtr = omni::core::ObjectPtr<IGraph>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// generated API declaration
#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/IGraph.gen.h>

//! @copydoc omni::graph::exec::unstable::IGraph_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::IGraph : public omni::core::Generated<omni::graph::exec::unstable::IGraph_abi>
{
public:
    //! Access topology of the graph.
    //!
    //! The returned @ref ITopology does *not* have @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.  The returned pointer will be valid for the lifetime of this @ref
    //! omni::graph::exec::unstable::IGraph.
    inline ITopology* getTopology() noexcept;

    //! Access root of the graph.
    //!
    //! The returned @ref INode does *not* have @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method always returns a valid pointer.
    //!
    //! @thread_safety This method is thread safe.  The returned pointer will be valid for the lifetime of this @ref
    //! omni::graph::exec::unstable::IGraph.
    inline INode* getRoot() noexcept;
};

#include <omni/graph/exec/unstable/IExecutionContext.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>

inline omni::graph::exec::unstable::ITopology* omni::graph::exec::unstable::IGraph::getTopology() noexcept
{
    return getNodeGraphDef()->getTopology();
}

inline omni::graph::exec::unstable::INode* omni::graph::exec::unstable::IGraph::getRoot() noexcept
{
    return getNodeGraphDef()->getRoot();
}

// generated API implementation
#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/IGraph.gen.h>
