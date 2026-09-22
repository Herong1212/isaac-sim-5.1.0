// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file INodeGraphDef.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::INodeGraphDef.
#pragma once

#include <omni/graph/exec/unstable/IDef.h>
#include <omni/graph/exec/unstable/INodeFactory.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class INode;
class INodeGraphDef_abi;
class INodeGraphDef;
class ITopology;

//! Graph definition.  Defines work to be done as a graph.
//!
//! Nodes within a graph represent work to be done.  The actual work to be performed is described in a
//! @rstref{definition <ef_definition>}.  Each node wanting to perform work points to a defintion.
//!
//! This interface is a subclass of the work definition interface (i.e. @ref omni::graph::exec::unstable::IDef) and
//! extends @ref omni::graph::exec::unstable::IDef with methods to describe work as a graph.
//!
//! Visually:
//!
//! @rst
//!
//! .. image:: /../docs/ef-simple-w-defs.svg
//!     :align: center
//!
//! @endrst
//!
//! Above, you can see the two types of definitions: opaque definitions (described by @ref
//! omni::graph::exec::unstable::INodeDef) and graph definitions (described by this interface).
//!
//! Nodes within a graph definition can point to other graph definitions. This composibility is where EF gets its *graph
//! of graphs* moniker.
//!
//! Multiple node's in the execution graph can point to the same instance of a graph definition. This saves both space
//! and graph construction time.  However, since each graph definition can be shared, its pointer value cannot be used
//! to uniquely identify its location in the graph.  To solve this, when traversing/executing a graph definition, an
//! @ref omni::graph::exec::unstable::ExecutionPath is passed (usually via @ref
//! omni::graph::exec::unstable::ExecutionTask::getUpstreamPath()).
//!
//! When defining new graph types, it is common to create a new implementation of this interface.  See @ref
//! omni::graph::exec:unstable::NodeGraphDef for an implementation of this interface that can be easily inherited from.
//! See @rstref{Definition Creation <ef_definition_creation>} for a guide on creating your own graph definition.
//!
//! How a graph definition's nodes are traversed during execution is defined by the definition's @ref
//! omni::graph::exec::unstable::IExecutor.  See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth
//! guide on how executors and graph definitions work together during execution.
//!
//! See also @ref omni::graph::exec::unstable::INode, @ref omni::graph::exec::unstable::IExecutor, and @ref
//! omni::graph::exec::unstable::ExecutionTask.
//!
//! @thread_safety Since definitions can be shared by multiple nodes, and nodes can be executed in parallel,
//! implementations of this interface should expect its methods to be called in parallel.
class INodeGraphDef_abi : public omni::core::Inherits<IDef, OMNI_TYPE_ID("omni.graph.exec.unstable.INodeGraphDef")>
{
protected:
    //! Return this graph's topology object.
    //!
    //! Each @ref omni::graph::exec::unstable::INodeGraphDef owns a @ref omni::graph::exec::unstable::ITopology.
    //!
    //! The returned @ref omni::graph::exec::unstable::ITopology will *not* have @ref omni::core::IObject::acquire()
    //! called before being returned.
    //!
    //! This method will never return @c nullptr.
    //!
    //! @thread_safety This method is thread safe.
    virtual OMNI_ATTR("not_null, no_acquire") ITopology* getTopology_abi() noexcept = 0;

    //! Initialize the state of the graph.
    //!
    //! It is up to the implementation of the graph type to decide whether this call needs to be propagated over all
    //! nodes within the graph or a single shared state is owned by the graph.
    //!
    //! @param  rootTask    State will be initialized for every instance of this graph. Root task will provide a path to
    //!                     allow discovery of the state.  Must not be @c nullptr.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual void initializeState_abi(OMNI_ATTR("in, out, not_null, ref") ExecutionTask* rootTask) noexcept = 0;

    //! Pre-execution call that can be used to setup the graph state prior to execution or entirely skip the execution.
    //!
    //! The given task must not be @c nullptr.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status
        preExecute_abi(OMNI_ATTR("in, out, not_null, ref") ExecutionTask* info) noexcept = 0;

    //! Post-execution call can be used to finalize the execution, e.g. transfer computation results to consumers.
    //!
    //! The given task must not be @c nullptr.
    //!
    //! See @rstref{Error Handling<ef_error_handling>} to understand the error handling/reporting responsibilities of
    //! implementors of this method.
    //!
    //! @thread_safety See thread safety information in interface description.
    virtual OMNI_ATTR("nodiscard") Status
        postExecute_abi(OMNI_ATTR("in, out, not_null, ref") ExecutionTask* info) noexcept = 0;

    //! Acquire factory object allowing for allocating new node instances for this graph definition.
    //!
    //! The returned factory may be @c nullptr when the graph definition does not allow allocating new nodes outside of
    //! pass that constructed the definition in the first place.
    //!
    //! The returned @ref omni::graph::exec::unstable::INodeFactory will have @ref omni::core::IObject::acquire() called
    //! before being returned.
    //!
    //! @thread_safety Accessing node factory is thread-safe but mutating graphs topology is not. This includes node
    //! creation.
    virtual INodeFactory* getNodeFactory_abi() noexcept = 0;
};

//! Smart pointer managing an instance of @ref INodeGraphDef.
using NodeGraphDefPtr = omni::core::ObjectPtr<INodeGraphDef>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include <omni/graph/exec/unstable/INodeGraphDef.gen.h>

//! @copydoc omni::graph::exec::unstable::INodeGraphDef_abi
//!
//! @ingroup groupOmniGraphExecInterfaces
class omni::graph::exec::unstable::INodeGraphDef
    : public omni::core::Generated<omni::graph::exec::unstable::INodeGraphDef_abi>
{
public:
    //! Access graph's root node.
    //!
    //! The returned @ref INode. will *not* have @ref omni::core::IObject::acquire() called before being returned.
    //!
    //! This method will never return @c nullptr.
    //!
    //! @thread_safety This method is thread safe.
    inline INode* getRoot() noexcept;
};

#include <omni/graph/exec/unstable/ITopology.h>

inline omni::graph::exec::unstable::INode* omni::graph::exec::unstable::INodeGraphDef::getRoot() noexcept
{
    return getTopology()->getRoot();
}

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include <omni/graph/exec/unstable/INodeGraphDef.gen.h>
