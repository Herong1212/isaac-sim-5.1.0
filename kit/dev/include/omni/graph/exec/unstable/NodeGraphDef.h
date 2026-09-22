// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file NodeGraphDef.h
//!
//! @brief Declares @ref omni::graph::exec::unstable::NodeGraphDef
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/Executor.h>
#include <omni/graph/exec/unstable/ExecutorFactory.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>
#include <omni/graph/exec/unstable/INodeGraphDefDebug.h>
#include <omni/graph/exec/unstable/Topology.h>

#include <atomic>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Concrete implementation of @ref omni::graph::exec::unstable::INodeGraphDef.
//!
//! This template is a concrete implementation of @ref omni::graph::exec::unstable::INodeGraphDef.  In many cases,
//! instantiating @ref omni::graph::exec::unstable::NodeGraphDef (which is instance of this template) will suffice.
//!
//! See @ref omni::graph::exec::unstable::INodeGraphDef for documentation on the purpose of graph definitions in the
//! Execution Framework.
//!
//! This class can be seen as a way to provide a reasonable, default implementation of both @ref
//! omni::graph::exec::unstable::INodeGraphDef and omni::graph::exec::unstable::INodeGraphDefDebug. The template
//! arguments allow the developer to further customize the interfaces this class implements.  A common pattern seen in
//! the Execution Framework is to define a private interface to attach authoring data to a definition. See
//! @rstref{Private Interfaces <ef_private_interfaces>} for details.
//!
//! Storing authoring data in the graph definition during graph construction is one way to link authoring data and the
//! Execution Framework.  However, the user must be mindful that definitions can be shared across multiple nodes in the
//! execution graph.
//!
//! During graph construction, authoring data can also be stored in @ref omni::graph::exec::unstable::NodeT.  When
//! storing data in @ref omni::graph::exec::unstable::NodeT, the user must again be mindful that a node may be a part of
//! a definition that is shared.
//!
//! @ref omni::graph::exec::unstable::IExecutionContext is another place to store data.  Rather than storing authoring
//! data, @ref omni::graph::exec::unstable::IExecutionContext is designed to store execution/evaluation data keyed on
//! each node's unique @ref omni::graph::exec::unstable::ExecutionPath.  Since definitions can be shared between nodes,
//! each node's @ref omni::graph::exec::unstable::ExecutionPath is necessary to uniquely identify the "instance" of any
//! given node.
template <typename... Bases>
class NodeGraphDefT : public Implements<Bases...>
{
public:
    //! Construct graph node definition with default executor.
    //!
    //! This method never returns @c nullptr.
    //!
    //! @param owner Execution graph having this graph as part of the global topology. Must not be @c nullptr.
    //!
    //! @param definitionName Definition name is considered as a token that transformation passes can register
    //!                       against. Must not be @c nullptr.
    static omni::core::ObjectPtr<NodeGraphDefT> create(omni::core::ObjectParam<IGraph> owner,
                                                       const carb::cpp::string_view& definitionName) noexcept
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(owner);
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(definitionName.data());
        return omni::core::steal(new NodeGraphDefT(owner, definitionName));
    }

    //! Construct graph node definition with the given executor factory.
    //!
    //! This method never returns @c nullptr.
    //!
    //! @param owner Execution graph having this graph as part of the global topology.  Must not be @c nullptr.
    //! @param executorFactory Factory returning executor for this graph.
    //! @param definitionName Definition name is considered as a token that transformation passes can register
    //!                       against.  Must not be @c nullptr.
    static omni::core::ObjectPtr<NodeGraphDefT> create(omni::core::ObjectParam<IGraph> owner,
                                                       ExecutorFactory executorFactory,
                                                       const carb::cpp::string_view& definitionName) noexcept
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(owner);
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(definitionName.data());
        return omni::core::steal(new NodeGraphDefT(owner, std::move(executorFactory), definitionName));
    }

protected:
    //! @copydoc omni::graph::exec::unstable::IDef::execute_abi
    //!
    //! This implementation delegates execution @ref omni::graph::exec::unstable::IExecutor. The lifetime of an executor
    //! is only for a single execution and any state that needs to persist longer than a single execution must be
    //! written with @ref omni::graph::exec::unstable::IExecutionContext::setNodeData_abi().
    Status execute_abi(ExecutionTask* info) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(info);

        // ef-docs nodegraphdef-execute-begin
        omni::core::ObjectPtr<IExecutor> executor;
        if (m_executorFactory)
        {
            executor = m_executorFactory(m_topology, *info);
        }
        else
        {
            executor = ExecutorFallback::create(m_topology, *info);
        }
        return executor->execute(); // execute the node specified by info->getNode()
        // ef-docs nodegraphdef-execute-end
    }

    //! @copydoc omni::graph::exec::unstable::IDef::getSchedulingInfo_abi
    SchedulingInfo getSchedulingInfo_abi(const ExecutionTask* info) noexcept override
    {
        return SchedulingInfo::eSerial;
    }

    //! @copydoc omni::graph::exec::unstable::IDef::getName_abi
    const ConstName* getName_abi() noexcept override
    {
        return &m_name;
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDef::getTopology_abi
    ITopology* getTopology_abi() noexcept override
    {
        return m_topology.get();
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDef::initializeState_abi
    void initializeState_abi(ExecutionTask* rootTask) noexcept override
    {
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDef::preExecute_abi
    Status preExecute_abi(ExecutionTask* info) noexcept override
    {
        return Status::eSuccess;
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDef::postExecute_abi
    Status postExecute_abi(ExecutionTask* info) noexcept override
    {
        return Status::eSuccess;
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDef::getNodeFactory_abi
    INodeFactory* getNodeFactory_abi() noexcept override
    {
        return nullptr;
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDefDebug::getExecutionCount_abi
    uint64_t getExecutionCount_abi() noexcept override
    {
        return m_executionCount;
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDefDebug::incrementExecutionCount_abi
    void incrementExecutionCount_abi() noexcept override
    {
        ++m_executionCount;
    }

    //! @copydoc omni::graph::exec::unstable::INodeGraphDefDebug::decrementExecutionCount_abi
    void decrementExecutionCount_abi() noexcept override
    {
        --m_executionCount;
    }

    //! Constructor with a default executor.
    NodeGraphDefT(omni::core::ObjectParam<IGraph> owner, const carb::cpp::string_view& definitionName) noexcept
        : m_topology{ Topology::create(definitionName) }, m_name{ definitionName }
    {
        _addInvalidationForwarder(owner);
    }

    //! Constructor with a custom executor.
    NodeGraphDefT(omni::core::ObjectParam<IGraph> owner,
                  ExecutorFactory&& executorFactory,
                  const carb::cpp::string_view& definitionName) noexcept
        : m_topology{ Topology::create(definitionName) },
          m_executorFactory(std::move(executorFactory)),
          m_name{ definitionName }
    {
        _addInvalidationForwarder(owner);
    }

private:
    //! Private method that will allow forwarding of topology invalidation to the execution graph.
    //! Invalid global topology will allow pass pipeline to execute and discover invalidated definitions.
    void _addInvalidationForwarder(omni::core::ObjectParam<IGraph> owner) noexcept
    {
        m_topology->addInvalidationForwarder(reinterpret_cast<InvalidationForwarderId>(owner.get()),
                                             [global = owner->getGlobalTopologyStamp()](ITopology*) -> void
                                             { global->next(); });
    }

    omni::core::ObjectPtr<ITopology> m_topology; //!< Graphs topology
    ExecutorFactory m_executorFactory; //!< Executor factory (if empty, default executor will be used)

    std::atomic<std::size_t> m_executionCount{ 0 }; //!< Debugging counter to detect illegal executions.

    ConstName m_name; //!< Definition name
};

//! Core NodeGraphDef implementation for @ref omni::graph::exec::unstable::INodeGraphDef
//!
//! See @ref omni::graph::exec::unstable::NodeGraphDefT for documentation on this type.
using NodeGraphDef = NodeGraphDefT<INodeGraphDef, INodeGraphDefDebug>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
