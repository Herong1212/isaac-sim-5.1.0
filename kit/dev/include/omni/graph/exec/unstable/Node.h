// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Node.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::Node.
#pragma once

#include <omni/core/ResultError.h>
#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/IGraphBuilderNode.h>
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/INodeDef.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>
#include <omni/graph/exec/unstable/ITopology.h>
#include <omni/graph/exec/unstable/SmallVector.h>
#include <omni/graph/exec/unstable/Types.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Concrete implementation of @ref omni::graph::exec::unstable::INode.
//!
//! This template is a concrete implementation of @ref omni::graph::exec::unstable::INode.  In most cases, instantiating
//! @ref omni::graph::exec::unstable::Node (which is instance of this template) will suffice.
//!
//! See @ref omni::graph::exec::unstable::INode for documentation on the purpose of nodes in the Execution Framework.
//!
//! This class can be seen as a way to provide a reasonable, default implementation of both @ref
//! omni::graph::exec::unstable::INode and @ref omni::graph::exec::unstable::IGraphBuilderNode.  The template arguments
//! allow the developer to further customize the interfaces this class implements.  A common pattern seen in the
//! Execution Framework is to define a private interface to attach authoring data to a node.
//! See @rstref{Private Interfaces <ef_private_interfaces>} for details.
//!
//! During graph construction, authoring data can be stored in @ref omni::graph::exec::unstable::NodeT.  When storing
//! data in @ref omni::graph::exec::unstable::NodeT, the user must be mindful that a node may be a part of a definition
//! that is shared.
//!
//! Storing authoring data in @ref omni::graph::exec::unstable::NodeGraphDefT during graph construction is another way
//! to link authoring data and the Execution Framework.  Again, the user must be mindful that definitions can be shared
//! across multiple nodes in the execution graph.
//!
//! @ref omni::graph::exec::unstable::IExecutionContext is another place to store data.  Rather than storing authoring
//! data, @ref omni::graph::exec::unstable::IExecutionContext is designed to store execution/evaluation data keyed on
//! each node's unique @ref omni::graph::exec::unstable::ExecutionPath.  Since definitions can be shared between nodes,
//! each node's @ref omni::graph::exec::unstable::ExecutionPath is necessary to uniquely identify the "instance" of any
//! given node.
template <typename... Bases>
class NodeT : public Implements<Bases...>
{
public:
    //! Constructor of a node with an empty definition.
    //!
    //! The given graph or topology must not be @c nullptr.
    //!
    //! The given name must not be @c nullptr.
    //!
    //! A valid pointer is always returned.
    template <typename T>
    static omni::core::ObjectPtr<NodeT> create(T&& graphOrTopology, const carb::cpp::string_view& idName)
    {
        OMNI_GRAPH_EXEC_ASSERT(graphOrTopology);
        OMNI_GRAPH_EXEC_ASSERT(idName.data());

        // Get the topology in which the node should reside in.
        ITopology* topology = GetTopology::get(std::forward<T>(graphOrTopology));

        return omni::core::steal(new NodeT(topology, idName));
    }

    //! Constructor of a node with a definition (can be a base definition @c IDef, an
    //! opaque node definition @c INodeDef, or a node graph definition @c INodeGraphDef).
    //!
    //! The given graph or topology must not be @c nullptr.
    //!
    //! The given name must not be @c nullptr.
    //!
    //! A valid pointer is always returned.
    template <typename T, typename D>
    static omni::core::ObjectPtr<NodeT> create(T&& graphOrTopology, D&& def, const carb::cpp::string_view& idName)
    {
        OMNI_GRAPH_EXEC_ASSERT(graphOrTopology);
        OMNI_GRAPH_EXEC_ASSERT(idName.data());

        // Get the definition type (IDef, INodeDef, or INodeGraphDef).
        using DefType = typename GetDefType<typename std::remove_reference<D>::type>::type;

        // Get the topology in which the node should reside in.
        ITopology* topology = GetTopology::get(std::forward<T>(graphOrTopology));

        return _create(topology, omni::core::ObjectParam<DefType>(std::forward<D>(def)).get(), idName);
    }

    //! Destructor
    virtual ~NodeT()
    {
        // in case we decide to implement move constructor
        if (m_indexInTopology != kInvalidNodeIndexInTopology)
        {
            m_topology->releaseNodeIndex(m_indexInTopology);

            if (isValidTopology_abi())
            {
                m_topology->invalidate();
            }
        }
    }

    // disambiguate between INode and IGraphBuilderNode
    using INode::getChildren;
    using INode::getName;
    using INode::getParents;
    using INode::getTopology;
    using INode::hasChild;

protected:
    //! @copydoc omni::graph::exec::unstable::INode::getTopology_abi
    ITopology* getTopology_abi() noexcept override
    {
        return m_topology;
    }

    //! @copydoc omni::graph::exec::unstable::INode::getName_abi
    const ConstName* getName_abi() noexcept override
    {
        return &m_name;
    }

    //! @copydoc omni::graph::exec::unstable::INode::getIndexInTopology_abi
    NodeIndexInTopology getIndexInTopology_abi() noexcept override
    {
        return m_indexInTopology;
    }

    //! @copydoc omni::graph::exec::unstable::INode::getParents_abi
    Span<INode* const> getParents_abi() noexcept override
    {
        return isValidTopology_abi() ? Span<INode* const>{ m_parents.begin(), m_parents.size() } :
                                       Span<INode* const>{ nullptr, 0 };
    }

    //! @copydoc omni::graph::exec::unstable::INode::getChildren_abi
    Span<INode* const> getChildren_abi() noexcept override
    {
        return isValidTopology_abi() ? Span<INode* const>{ m_children.begin(), m_children.size() } :
                                       Span<INode* const>{ nullptr, 0 };
    }

    //! @copydoc omni::graph::exec::unstable::INode::getCycleParentCount_abi
    uint32_t getCycleParentCount_abi() noexcept override
    {
        return isValidTopology_abi() ? m_cycleParentCount : 0;
    }

    //! @copydoc omni::graph::exec::unstable::INode::isValidTopology_abi
    //!
    //! @note This method is called in the destructor and therefore must be marked as final
    bool isValidTopology_abi() noexcept final override
    {
        return m_topologyStamp.inSync(m_topology->getStamp());
    }

    //! @copydoc omni::graph::exec::unstable::INode::validateOrResetTopology_abi
    virtual void validateOrResetTopology_abi() noexcept
    {
        if (m_topologyStamp.makeSync(m_topology->getStamp()))
        {
            // topology changed, let's clear the old one
            m_parents.clear();
            m_children.clear();
            m_cycleParentCount = 0;
        }
    }

    //! @copydoc omni::graph::exec::unstable::INode::getDef_abi
    IDef* getDef_abi() noexcept override
    {
        if (m_nodeDef.get())
        {
            return m_nodeDef.get();
        }
        else
        {
            return m_nodeGraphDef.get();
        }
    }

    //! @copydoc omni::graph::exec::unstable::INode::getNodeDef_abi
    INodeDef* getNodeDef_abi() noexcept override
    {
        return m_nodeDef.get();
    }

    //! @copydoc omni::graph::exec::unstable::INode::getNodeGraphDef_abi
    INodeGraphDef* getNodeGraphDef_abi() noexcept override
    {
        return m_nodeGraphDef.get();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_addParent_abi
    void _addParent_abi(IGraphBuilderNode* parent) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(parent);
        OMNI_GRAPH_EXEC_CAST_OR_FATAL(asNode, INode, parent);
        OMNI_GRAPH_EXEC_ASSERT(isValidTopology_abi());
        m_parents.push_back(asNode); // may throw
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_removeParent_abi
    void _removeParent_abi(IGraphBuilderNode* parent) noexcept override
    {
        if (!parent)
        {
            return; // LCOV_EXCL_LINE
        }
        OMNI_GRAPH_EXEC_CAST_OR_FATAL(asNode, INode, parent);
        _eraseRemove(m_parents, asNode);
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_addChild_abi
    void _addChild_abi(IGraphBuilderNode* child) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(child);
        OMNI_GRAPH_EXEC_CAST_OR_FATAL(asNode, INode, child);
        OMNI_GRAPH_EXEC_ASSERT(isValidTopology_abi());
        m_children.push_back(asNode);
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_removeChild_abi
    void _removeChild_abi(IGraphBuilderNode* child) noexcept override
    {
        if (!child)
        {
            return; // LCOV_EXCL_LINE
        }
        OMNI_GRAPH_EXEC_CAST_OR_FATAL(asNode, INode, child);
        _eraseRemove(m_children, asNode);
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_removeInvalidParents_abi
    void _removeInvalidParents_abi() noexcept override
    {
        if (isValidTopology_abi())
        {
            m_parents.erase(
                std::remove_if(m_parents.begin(), m_parents.end(), [](INode* n) { return !n->isValidTopology(); }),
                m_parents.end());
        }
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_removeInvalidChildren_abi
    void _removeInvalidChildren_abi() noexcept override
    {
        if (isValidTopology_abi())
        {
            m_children.erase(
                std::remove_if(m_children.begin(), m_children.end(), [](INode* n) { return !n->isValidTopology(); }),
                m_children.end());
        }
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_invalidateConnections_abi
    void _invalidateConnections_abi() noexcept override
    {
        m_topologyStamp.invalidate();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::setCycleParentCount_abi
    void setCycleParentCount_abi(uint32_t count) noexcept override
    {
        m_cycleParentCount = count;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_setNodeDef_abi
    void _setNodeDef_abi(INodeDef* nodeDef) noexcept override
    {
        m_nodeDef.borrow(nodeDef);
        m_nodeGraphDef.release();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_setNodeGraphDef_abi
    void _setNodeGraphDef_abi(INodeGraphDef* nodeGraphDef) noexcept override
    {
        m_nodeGraphDef.borrow(nodeGraphDef);
        m_nodeDef.release();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::_clearDef_abi
    void _clearDef_abi() noexcept override
    {
        m_nodeDef.release();
        m_nodeGraphDef.release();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::getParentAt_abi
    IGraphBuilderNode* getParentAt_abi(uint64_t index) noexcept override
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS(isValidTopology_abi());
        OMNI_GRAPH_EXEC_FATAL_UNLESS(index < m_parents.size());
        OMNI_GRAPH_EXEC_CAST_OR_FATAL(asGraphBuilderNode, IGraphBuilderNode, m_parents[static_cast<uint32_t>(index)]);
        return asGraphBuilderNode;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::getParentCount_abi
    uint64_t getParentCount_abi() noexcept override
    {
        return isValidTopology_abi() ? m_parents.size() : 0;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::getChildAt_abi
    IGraphBuilderNode* getChildAt_abi(uint64_t index) noexcept override
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS(isValidTopology_abi());
        OMNI_GRAPH_EXEC_FATAL_UNLESS(index < m_children.size());
        OMNI_GRAPH_EXEC_CAST_OR_FATAL(asGraphBuilderNode, IGraphBuilderNode, m_children[static_cast<uint32_t>(index)]);
        return asGraphBuilderNode;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::getChildCount_abi
    uint64_t getChildCount_abi() noexcept override
    {
        return isValidTopology_abi() ? m_children.size() : 0;
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::hasChild_abi
    bool hasChild_abi(IGraphBuilderNode* node) noexcept override
    {
        if (!isValidTopology_abi())
        {
            return false; // LCOV_EXCL_LINE
        }

        auto asNode = omni::graph::exec::unstable::cast<INode>(node);
        if (!asNode)
        {
            return false; // LCOV_EXCL_LINE
        }

        return std::find(m_children.begin(), m_children.end(), asNode) != m_children.end();
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::isRoot_abi
    bool isRoot_abi() noexcept override
    {
        return (m_topology->getRoot() == static_cast<INode*>(this));
    }

    //! @copydoc omni::graph::exec::unstable::IGraphBuilderNode::getRoot_abi
    IGraphBuilderNode* getRoot_abi() noexcept override
    {
        OMNI_GRAPH_EXEC_CAST_OR_FATAL(asGraphBuilderNode, IGraphBuilderNode, m_topology->getRoot());
        return asGraphBuilderNode;
    }

    //! Constructor
    NodeT(ITopology* topology, const carb::cpp::string_view& idName) noexcept
        : m_topology{ topology }, m_indexInTopology{ m_topology->acquireNodeIndex() }, m_name{ idName }
    {
    }

    //! Constructor
    NodeT(ITopology* topology, INodeGraphDef* nodeGraphDef, const carb::cpp::string_view& idName) noexcept
        : m_topology{ topology },
          m_indexInTopology{ m_topology->acquireNodeIndex() },
          m_nodeGraphDef{ nodeGraphDef, omni::core::kBorrow },
          m_name{ idName }
    {
    }

    //! Constructor
    NodeT(ITopology* topology, INodeDef* nodeDef, const carb::cpp::string_view& idName) noexcept
        : m_topology{ topology },
          m_indexInTopology{ m_topology->acquireNodeIndex() },
          m_nodeDef{ nodeDef, omni::core::kBorrow },
          m_name{ idName }
    {
    }

private:
    //! Container for connections.
    //!
    //! Using @ref omni::graph::exec::unstable::SmallVector with local storage space for two nodes.
    //! The local space storage was hand picked, following the experience that most of graph nodes
    //! have very few downstream nodes.
    using NodeArray = SmallVector<INode*, 2>;

    //! Helper erase-remove idiom to remove and eliminate a node from the container
    template <typename T>
    void _eraseRemove(T& v, INode* n) noexcept
    {
        v.erase(std::remove(v.begin(), v.end(), n), v.end());
    };

    ITopology* m_topology; //!< Topology owning this node

    //! Acquired local index
    NodeIndexInTopology m_indexInTopology{ kInvalidNodeIndexInTopology };

    NodeArray m_parents; //!< Edges to parents
    NodeArray m_children; //!< Edges to children

    uint32_t m_cycleParentCount{ 0 }; //!< Cycling parents (used by the graph traversal)
    SyncStamp m_topologyStamp; //!< Validity check for edges

    omni::core::ObjectPtr<INodeDef> m_nodeDef; //!< Node definition
    omni::core::ObjectPtr<INodeGraphDef> m_nodeGraphDef; //!< Node graph definition

    ConstName m_name; //!< Identifier name

    // Helper struct for getting a topology pointer from one of the following:
    // - IGraph*
    // - omni::core::ObjectPtr<IGraph>
    // - omni::core::ObjectParam<IGraph>
    // - ITopology*
    // - omni::core::ObjectPtr<ITopology>
    // - omni::core::ObjectParam<ITopology>
    struct GetTopology
    {
        static ITopology* get(omni::core::ObjectParam<IGraph> graph)
        {
            return graph->getTopology();
        }
        static ITopology* get(omni::core::ObjectParam<ITopology> topology)
        {
            return topology.get();
        }
    };

    // Helper structs for obtaining a definition type.
    // LCOV_EXCL_START
    template <typename T>
    struct GetDefType
    {
        using type = std::remove_pointer_t<T>;
    };
    template <typename T>
    struct GetDefType<omni::core::ObjectPtr<T>>
    {
        using type = T;
    };
    template <typename T>
    struct GetDefType<omni::core::ObjectParam<T>>
    {
        using type = T;
    };
    // LCOV_EXCL_STOP

    // Internal implementations for node creation that intake a topology
    // and various definitions. We have separate overloads for the various
    // definition interfaces (IDef, INodeDef, and INodeGraphDef) to reduce
    // some overhead from having to explicitly deduce typing at runtime for
    // the latter two; instead, the correct overload to utilize in a given
    // context can be decided at compile time, saving us runtime checks
    // if we are attempting to create a node using either INodeDef- or
    // INodeGraphDef-derived definitions. Said checks still need to be
    // performed if IDefs are directly passed in, however.
    template <typename T>
    static omni::core::ObjectPtr<NodeT> _create(T topology, INodeGraphDef* def, const carb::cpp::string_view& idName)
    {
        return omni::core::steal(new NodeT(topology, def, idName));
    }

    template <typename T>
    static omni::core::ObjectPtr<NodeT> _create(T topology, INodeDef* def, const carb::cpp::string_view& idName)
    {
        return omni::core::steal(new NodeT(topology, def, idName));
    }

    template <typename T, typename D>
    static omni::core::ObjectPtr<NodeT> _create(T topology, D* def, const carb::cpp::string_view& idName)
    {
        // We don't know if def is an INodeDef or INodeGraphDef at compile time, so
        // we have to perform this runtime check.
        if (!def)
        {
            return omni::core::steal(new NodeT(topology, idName));
        }
        else if (auto* nodeDef = omni::graph::exec::unstable::cast<INodeDef>(def))
        {
            return omni::core::steal(new NodeT(topology, nodeDef, idName));
        }
        else if (auto* nodeGraphDef = omni::graph::exec::unstable::cast<INodeGraphDef>(def))
        {
            return omni::core::steal(new NodeT(topology, nodeGraphDef, idName));
        }
        // LCOV_EXCL_START
        else
        {
            return nullptr; // Should not happen.
        }
        // LCOV_EXCL_STOP
    }
};

//! Core node implementation for @ref omni::graph::exec::unstable::INode
//!
//! See @ref omni::graph::exec::unstable::NodeT to understand how nodes can be customized.
using Node = NodeT<INode, IGraphBuilderNode>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
