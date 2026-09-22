// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Graph.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGraph.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/ExecutorFactory.h>
#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/NodeGraphDef.h>

#include <atomic>
#include <utility>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::IGraph
template <typename... Bases>
class GraphT : public Implements<Bases...>
{
public:
    //! Construct a graph with default executor attached to an empty node graph.
    //!
    //! @p name is the name of the graph and must not be @c nullptr.
    //!
    //! A valid pointer is always returned.
    static omni::core::ObjectPtr<GraphT> create(const carb::cpp::string_view& name) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(name.data());
        return omni::core::steal(new GraphT(name));
    }

    //! Construct a graph with a given executor and an empty node graph.
    //!
    //! @p executorFactory is a factory to create a user defined executor to execute the graph.
    //!
    //! @p name is the name of the graph and must not be @c nullptr.
    //!
    //! A valid pointer is always returned.
    static omni::core::ObjectPtr<GraphT> create(const ExecutorFactory& executorFactory,
                                                const carb::cpp::string_view& name) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(name.data());
        return omni::core::steal(new GraphT(executorFactory, name));
    }

    //! Construct a graph with the given node graph.
    //!
    //! @p nodeGraphDefFactory will be used to create the graph's top-level graph definition.
    //!
    //! The signature of @p nodeGraphDefFactory must be equivalent to `NodeGraphDefPtr(IGraph*)`.
    //!
    //! A valid pointer is always returned.
    template <typename Fn>
    static omni::core::ObjectPtr<GraphT> create(const carb::cpp::string_view& name, Fn&& nodeGraphDefFactory) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(name.data());
        return omni::core::steal(new GraphT(name, std::forward<Fn>(nodeGraphDefFactory)));
    }

protected:
    //! @copydoc omni::graph::exec::unstable::IGraph::getNodeGraphDef_abi
    INodeGraphDef* getNodeGraphDef_abi() noexcept override
    {
        return m_nodeGraphDef.get();
    }

    //! @copydoc omni::graph::exec::unstable::IGraph::getName_abi
    const ConstName* getName_abi() noexcept override
    {
        return &m_name;
    }

    //! @copydoc omni::graph::exec::unstable::IGraph::getGlobalTopologyStamp_abi
    Stamp* getGlobalTopologyStamp_abi() noexcept override
    {
        return &m_globalTopologyStamp;
    }

    //! @copydoc omni::graph::exec::unstable::IGraph::inBuild_abi
    virtual bool inBuild_abi() noexcept override
    {
        return (m_inBuild > 0);
    }

    //! @copydoc omni::graph::exec::unstable::IGraph::_setInBuild_abi
    virtual void _setInBuild_abi(bool inBuild) noexcept override
    {
        if (inBuild)
        {
            ++m_inBuild;
        }
        else
        {
            --m_inBuild;
            OMNI_GRAPH_EXEC_ASSERT(m_inBuild > -1);
        }
    }

    //! Construct with a default top level graph definition.
    GraphT(const carb::cpp::string_view& name) noexcept : m_name(name)
    {
        m_globalTopologyStamp.next();
        m_nodeGraphDef = NodeGraphDef::create(this, "NODE-ROOT");
    }

    //! Construct with a custom executor for a top level graph definition.
    GraphT(const ExecutorFactory& executorFactory, const carb::cpp::string_view& name) noexcept : m_name(name)
    {
        m_globalTopologyStamp.next();
        m_nodeGraphDef = NodeGraphDef::create(this, executorFactory, "NODE-ROOT");
    }

    //! Construct with a custom top level graph factory.
    template <typename Fn>
    GraphT(const carb::cpp::string_view& name, Fn&& nodeGraphDefFactory) noexcept : m_name(name)
    {
        m_globalTopologyStamp.next();
        m_nodeGraphDef = nodeGraphDefFactory(this); // may throw
    }

private:
    Stamp m_globalTopologyStamp; //!< Global graph topology. Incremented every time any nested topologies changes
    omni::core::ObjectPtr<INodeGraphDef> m_nodeGraphDef; //!< Top level node graph definition
    ConstName m_name; //!< Name of the execution graph

    //! How many builders are active.  Atomic since multiple builders may be running in parallel.
    std::atomic<int> m_inBuild{ 0 };
};

//! Core Graph implementation for @ref omni::graph::exec::unstable::IGraph
//!
//! See @ref omni::graph::exec::unstable::GraphT to understand how the top-level execution graph can be customized.
using Graph = GraphT<IGraph>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
