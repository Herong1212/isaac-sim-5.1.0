// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file GraphBuilder.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::IGraphBuilder.
#pragma once

#include <carb/Defines.h>
#include <carb/Format.h>

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/IGraphBuilderContext.h>
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/INodeDef.h>
#include <omni/graph/exec/unstable/INodeFactory.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>
#include <omni/graph/exec/unstable/INodeGraphDefDebug.h>
#include <omni/graph/exec/unstable/SmallVector.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::IGraphBuilder
template <typename... Bases>
class GraphBuilderT : public Implements<Bases...>
{
public:
    //! Construct a graph builder for the root @ref INodeGraphDef of the @ref IGraph in the given @ref
    //! IGraphBuilderContext.
    //!
    //! Construction of this graph builder will invalidate the underlying topology.
    //!
    //! @p context must not be @c nullptr.
    //!
    //! This method always returns a valid pointer.
    static omni::core::ObjectPtr<GraphBuilderT> create(omni::core::ObjectParam<IGraphBuilderContext> context)
    {
        OMNI_GRAPH_EXEC_ASSERT(context);
        OMNI_GRAPH_EXEC_ASSERT(
            !omni::graph::exec::unstable::cast<INodeGraphDefDebug>(context->getGraph()->getNodeGraphDef()) ||
            !omni::graph::exec::unstable::cast<INodeGraphDefDebug>(context->getGraph()->getNodeGraphDef())->isExecuting());

        auto builder = omni::core::steal(new GraphBuilderT(context.get(), context->getGraph()->getNodeGraphDef()));
        auto topology = builder->getTopology();
        topology->invalidate();
        builder->_modifiedTopology(topology);

        return builder;
    }

    //! Construct a graph builder for the given @ref INodeGraphDef.
    //!
    //! Construction of this graph builder will invalidate the underlying topology.
    //!
    //! @p context must not be @c nullptr.
    //!
    //! @p nodeGraphDef must not be @c nullptr.
    //!
    //! This method always returns a valid pointer.
    static omni::core::ObjectPtr<GraphBuilderT> create(omni::core::ObjectParam<IGraphBuilder> parentBuilder,
                                                       omni::core::ObjectParam<INodeGraphDef> nodeGraphDef)
    {
        OMNI_GRAPH_EXEC_ASSERT(parentBuilder);
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(nodeGraphDef);
        OMNI_GRAPH_EXEC_ASSERT(!omni::graph::exec::unstable::cast<INodeGraphDefDebug>(nodeGraphDef.get()) ||
                               !omni::graph::exec::unstable::cast<INodeGraphDefDebug>(nodeGraphDef.get())->isExecuting());

        auto builder = omni::core::steal(new GraphBuilderT(parentBuilder->getContext(), nodeGraphDef.get()));
        auto topology = builder->getTopology();
        topology->invalidate();
        builder->_modifiedTopology(topology);

        return builder;
    }

    //! Construct graph builder for a given @ref INodeGraphDef without causing topology invalidation.
    //!
    //! This method creates a builder that can be used by the pass pipeline when operations to the graph will alter
    //! existing topology.
    //!
    //! @p context must not be @c nullptr.
    //!
    //! @p nodeGraphDef must not be @c nullptr.
    //!
    //! This method always returns a valid pointer.
    static omni::core::ObjectPtr<GraphBuilderT> createForPass(omni::core::ObjectParam<IGraphBuilderContext> context,
                                                              omni::core::ObjectParam<INodeGraphDef> nodeGraphDef)
    {
        OMNI_GRAPH_EXEC_ASSERT(context);
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(nodeGraphDef);
        OMNI_GRAPH_EXEC_ASSERT(!omni::graph::exec::unstable::cast<INodeGraphDefDebug>(nodeGraphDef.get()) ||
                               !omni::graph::exec::unstable::cast<INodeGraphDefDebug>(nodeGraphDef.get())->isExecuting());

        auto builder = omni::core::steal(new GraphBuilderT(context.get(), nodeGraphDef.get()));

        // Detect when node graph was constructed outside of the pass pipeline. Tag these defs are created
        // during current construction stamp.
        //
        // This usage pattern we only have in tests currently.
        auto topology = nodeGraphDef->getTopology();
        if (!topology->getConstructionStamp().isValid())
        {
            builder->_modifiedTopology(topology);
        }

        return builder;
    }

protected:
    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::getGraph_abi
    IGraph* getGraph_abi() noexcept override
    {
        return m_context->getGraph();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::getTopology_abi
    ITopology* getTopology_abi() noexcept override
    {
        return m_nodeGraphDef->getTopology();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::getContext_abi
    IGraphBuilderContext* getContext_abi() noexcept override
    {
        return m_context;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::getNodeGraphDef_abi
    INodeGraphDef* getNodeGraphDef_abi() noexcept override
    {
        return m_nodeGraphDef;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::connect_abi
    void connect_abi(INode* upstreamNode, INode* downstreamNode) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(upstreamNode);
        OMNI_GRAPH_EXEC_ASSERT(downstreamNode);

        OMNI_GRAPH_EXEC_FATAL_UNLESS(upstreamNode->getTopology() == m_nodeGraphDef->getTopology());
        OMNI_GRAPH_EXEC_FATAL_UNLESS(downstreamNode->getTopology() == m_nodeGraphDef->getTopology());

        _modifiedTopology(upstreamNode->getTopology());

        IGraphBuilderNode* upstream = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(upstreamNode);
        OMNI_GRAPH_EXEC_ASSERT(upstream);

        IGraphBuilderNode* downstream = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(downstreamNode);
        OMNI_GRAPH_EXEC_ASSERT(downstream);

        _connect(upstream, downstream);
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::disconnect_abi
    void disconnect_abi(INode* upstreamNode, INode* downstreamNode) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(upstreamNode);
        OMNI_GRAPH_EXEC_ASSERT(downstreamNode);

        OMNI_GRAPH_EXEC_FATAL_UNLESS(upstreamNode->getTopology() == m_nodeGraphDef->getTopology());
        OMNI_GRAPH_EXEC_FATAL_UNLESS(downstreamNode->getTopology() == m_nodeGraphDef->getTopology());

        _modifiedTopology(upstreamNode->getTopology());

        IGraphBuilderNode* upstream = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(upstreamNode);
        OMNI_GRAPH_EXEC_ASSERT(upstream);

        IGraphBuilderNode* downstream = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(downstreamNode);
        OMNI_GRAPH_EXEC_ASSERT(downstream);

        _disconnect(upstream, downstream);
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::remove_abi
    void remove_abi(INode* node) noexcept override
    {
        if (!node)
        {
            return;
        }

        OMNI_GRAPH_EXEC_FATAL_UNLESS(node->getTopology() == m_nodeGraphDef->getTopology());

        _modifiedTopology(node->getTopology());

        IGraphBuilderNode* nodeToRemove = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(node);
        OMNI_GRAPH_EXEC_ASSERT(nodeToRemove);
        nodeToRemove->validateOrResetTopology();

        // Nodes don't have an edge back to the root. Check if the removed node is a child of the root.
        auto graphRoot = nodeToRemove->getRoot();
        graphRoot->_removeChild(nodeToRemove); // Silently fails if node is not a root child.

        // Cache these pointers to avoid virtual method overhead.
        auto children = nodeToRemove->getChildren();
        auto parents = nodeToRemove->getParents();

        // Disconnect all parents from the node to be removed.
        for (auto parent : parents)
        {
            parent->_removeChild(nodeToRemove);
        }

        // Disconnect all children from the node to be removed.
        for (auto child : children)
        {
            child->_removeParent(nodeToRemove);
        }

        // Invalidate all remaining connections of the node to be removed.
        nodeToRemove->_invalidateConnections();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::setNodeDef_abi
    void setNodeDef_abi(INode* node, INodeDef* nodeDef) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(node);
        OMNI_GRAPH_EXEC_FATAL_UNLESS(node->getTopology() == m_nodeGraphDef->getTopology());

        _modifiedTopology(node->getTopology());

        auto builderNode = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(node);
        OMNI_GRAPH_EXEC_ASSERT(builderNode);
        builderNode->_setNodeDef(nodeDef);
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::setNodeGraphDef_abi
    void setNodeGraphDef_abi(INode* node, INodeGraphDef* nodeGraphDef) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(node);
        OMNI_GRAPH_EXEC_FATAL_UNLESS(node->getTopology() == m_nodeGraphDef->getTopology());

        _modifiedTopology(node->getTopology());

        auto builderNode = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(node);
        OMNI_GRAPH_EXEC_ASSERT(builderNode);
        builderNode->_setNodeGraphDef(nodeGraphDef);
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::clearDef_abi
    void clearDef_abi(INode* node) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(node);
        OMNI_GRAPH_EXEC_FATAL_UNLESS(node->getTopology() == m_nodeGraphDef->getTopology());

        _modifiedTopology(node->getTopology());

        auto builderNode = exec::unstable::cast<exec::unstable::IGraphBuilderNode>(node);
        OMNI_GRAPH_EXEC_ASSERT(builderNode);
        builderNode->_clearDef();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::replacePartition_abi
    void replacePartition_abi(const NodePartition* partition, IDef* definition) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(partition);

        if (partition->empty())
        {
            return; // nothing to do
        }

        OMNI_GRAPH_EXEC_FATAL_UNLESS(m_nodeGraphDef->getNodeFactory());

        // validate the partition
        for (auto nodeInPartition : *partition)
        {
            OMNI_GRAPH_EXEC_FATAL_UNLESS(nodeInPartition->isValidTopology());
            OMNI_GRAPH_EXEC_FATAL_UNLESS(nodeInPartition->getTopology() == m_nodeGraphDef->getTopology());
        }

        // mutate the graph
        _commitPartition(partition, definition);
        _modifiedTopology(m_nodeGraphDef->getTopology());
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::createNode_abi
    INode* createNode_abi(const char* name, IDef* def) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(name);

        if (auto factory = m_nodeGraphDef->getNodeFactory())
        {
            auto newNode = factory->createNode(name, def); // factory should hold a ref
            OMNI_GRAPH_EXEC_ASSERT(newNode);
            m_createdNodes.push_back(newNode);
            return newNode;
        }
        else
        {
            // the graph definition doesn't support creation of nodes
            return nullptr;
        }
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilder::getCreatedNodes_abi
    Span<INode* const> getCreatedNodes_abi() noexcept override
    {
        return m_createdNodes.size() ? Span<INode* const>{ m_createdNodes.begin(), m_createdNodes.size() } :
                                       Span<INode* const>{ nullptr, 0 };
    }

    //! Constructor
    GraphBuilderT(IGraphBuilderContext* context, INodeGraphDef* nodeGraphDef) noexcept
        : m_context{ context }, m_nodeGraphDef{ nodeGraphDef }
    {
        m_context->getGraph()->_setInBuild(true);
    }

    //! Destructor.
    ~GraphBuilderT() noexcept
    {
        m_context->getGraph()->_setInBuild(false);
    }

private:
    //! This builder modified topology of a graph. Currently it is possible it is not modifying topology belonging to
    //! NodeGraphDef it refers to.
    void _modifiedTopology(ITopology* modifiedTopology) noexcept
    {
        modifiedTopology->_setConstructionInSync(m_context->getConstructionStamp());
    }

    void _connect(IGraphBuilderNode* upstream, IGraphBuilderNode* downstream) noexcept
    {
        upstream->validateOrResetTopology();
        downstream->validateOrResetTopology();

        if (!upstream->hasChild(downstream))
        {
            upstream->_addChild(downstream); // may throw
            if (!upstream->isRoot())
            {
                downstream->_addParent(upstream); // may throw
            }
        }
    }

    void _disconnect(IGraphBuilderNode* upstream, IGraphBuilderNode* downstream) noexcept
    {
        upstream->validateOrResetTopology();
        downstream->validateOrResetTopology();

        if (upstream->hasChild(downstream))
        {
            upstream->_removeChild(downstream);

            if (!upstream->isRoot())
            {
                downstream->_removeParent(upstream);
            }
        }
    }

    //! Make changes to the topology with already validated partition and definition.
    void _commitPartition(const NodePartition* partition, IDef* definition) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(partition->size() > 0);
        OMNI_GRAPH_EXEC_ASSERT(m_nodeGraphDef->getNodeFactory().get()); // graph def must support node creation

        // we affect the topology, but shouldn't require any memory operation
        std::vector<INode*> parents, children; // may throw

        // optimization, let's assume each node has one parent and one child from outside of the partition
        parents.reserve(partition->size() * 2); // may throw
        children.reserve(partition->size() * 2); // may throw

        // we want cost to be linear and for that we are going to avoid searches in the partition
        // we achieve this by collecting all parents/children (some will be in the partition),
        // then invalidating the partition and cleaning up the immediate upstream and downstream
        for (auto nodeInPartition : *partition)
        {
            for (auto parent : nodeInPartition->getParents())
            {
                parents.push_back(parent);
            }

            for (auto child : nodeInPartition->getChildren())
            {
                children.push_back(child);
            }

            // make the node invalid without invalidating the entire topology
            auto builderNode = exec::unstable::cast<IGraphBuilderNode>(nodeInPartition);
            OMNI_GRAPH_EXEC_ASSERT(builderNode);
            builderNode->_invalidateConnections();
        }

        // generate replacement node
        std::string nodeName = carb::fmt::format("Partition_{}", partition->front()->getName()); // may throw

        auto newNode = this->createNode(nodeName, definition);
        OMNI_GRAPH_EXEC_ASSERT(newNode);

        auto newBuilderNode = exec::unstable::cast<IGraphBuilderNode>(newNode);
        OMNI_GRAPH_EXEC_ASSERT(newBuilderNode);

        // in one pass: cleanup the topology and reconnect to the new node
        auto rootBuilderNode = exec::unstable::cast<IGraphBuilderNode>(partition->front()->getRoot());
        OMNI_GRAPH_EXEC_ASSERT(rootBuilderNode);
        rootBuilderNode->_removeInvalidChildren();

        for (auto parent : parents)
        {
            if (parent->isValidTopology())
            {
                auto parentBuilderNode = exec::unstable::cast<IGraphBuilderNode>(parent);
                OMNI_GRAPH_EXEC_ASSERT(parentBuilderNode);

                parentBuilderNode->_removeInvalidChildren();
                _connect(parentBuilderNode, newBuilderNode);
            }
        }

        for (auto child : children)
        {
            if (child->isValidTopology())
            {
                auto childBuilderNode = exec::unstable::cast<IGraphBuilderNode>(child);
                OMNI_GRAPH_EXEC_ASSERT(childBuilderNode);

                childBuilderNode->_removeInvalidParents();
                _connect(newBuilderNode, childBuilderNode);
            }
        }

        // Need to make sure we are connected to the root (indirectly, or directly if this is an entry node)
        if (newNode->getParents().empty())
        {
            _connect(rootBuilderNode, newBuilderNode);
        }
    }

    IGraphBuilderContext* m_context{ nullptr }; //!< All graph builders are operating within a context. We store pointer
                                                //!< to it.
    INodeGraphDef* m_nodeGraphDef{ nullptr }; //!< Graph topology this builder can modify. This is not yet enforced in
                                              //!< code.

    //! Most of the time we won't be needing any space. The size of 2 was chosen arbitrary.
    using NodeArray = SmallVector<INode*, 2>;
    NodeArray m_createdNodes; //!< Collect nodes created dynamically to allow pass pipeline discover them.
};

//! Core GraphBuilder implementation for @ref omni::graph::exec::unstable::IGraphBuilder
using GraphBuilder = GraphBuilderT<IGraphBuilder>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
