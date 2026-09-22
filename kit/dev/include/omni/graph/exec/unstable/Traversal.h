// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Traversal.h
//!
//! @brief Defines graph traversal algorithms.
//!
//! See @rstref{Traversing a Graph <ef_graph_traversal_guide>} and
//! @rstref{Graph Traversal In-Depth <ef_graph_traversal_advanced>} for more information how to utilize graph
//! traversals.
#pragma once

#include <concurrentqueue/include_concurrentqueue.h>
#include <omni/graph/exec/unstable/AtomicBackoff.h>
#include <omni/graph/exec/unstable/EnumBitops.h>

#include <atomic>
#include <functional>
#include <memory>
#include <queue>
#include <type_traits>
#include <vector>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Implementation details.
namespace detail
{

//! Information returned to traversal callback indicating visit order
enum class VisitOrder
{
    eUnknown = 0, //!< Visit order is not specified
    eFirst = 1 << 0, //!< This is the first visit to a node during the traversal
    eNext = 1 << 1, //!< This is a next visit to a node, i.e. not a first one and not the last one
    eLast = 1 << 2, //!< This is the last visit to a node during the traversal
    eCycle = 1 << 3 //!< In case of cycles, when traversal enters node at the last visit, more visit can happen with
                    //!< cycle order
};

} // namespace detail

//! Enable bitwise operation on VisitOrder
template <>
struct EnumBitops<detail::VisitOrder> : EnumBitops<>::allow_bitops
{
};

namespace detail
{

//! Traversal information stored per node
struct NodeData
{
    std::atomic<std::size_t> visitCount{ 0 }; //!< How many times this node was visited.
};

// ef-docs visit-first-begin
//! Traversal strategy that enters the node when it was first time discovered
struct VisitFirst
{
    //! Call to traverse the graph with a strategy to visit only when first time discovered
    template <typename Node, typename NodeData>
    static VisitOrder tryVisit(Node* node, NodeData& nodeData)
    {
        auto lastVisit = nodeData.visitCount++; // read+increment only once. other threads can be doing the same.
        return (lastVisit == 0) ? VisitOrder::eFirst : VisitOrder::eUnknown;
    }
};
// ef-docs visit-first-end

// ef-docs visit-last-begin
//! Traversal strategy that enters the node when entire upstream was already visited and this is the last
//! opportunity to enter the node.
//!
//! In case of cycles, this algorithm is relying on knowledge of number of parents that are causing cycles.
struct VisitLast
{
    //! Call to traverse the graph with a strategy to visit only when no more visits are possible
    template <typename Node, typename NodeData>
    static VisitOrder tryVisit(Node& node, NodeData& nodeData)
    {
        auto requiredCount = node->getParents().size() - node->getCycleParentCount();
        auto currentVisit = ++nodeData.visitCount; // increment+read only once. other threads can be doing the same.
        if (requiredCount == 0 && currentVisit == 1)
        {
            return VisitOrder::eLast;
        }
        else if (currentVisit == requiredCount)
        {
            return VisitOrder::eLast;
        }

        return VisitOrder::eUnknown;
    }
};
// ef-docs visit-last-end

// ef-docs visit-all-begin
//! Traversal strategy that allows discovering all the edges in the graph. Traversal continuation is controlled by user
//! code.
struct VisitAll
{
    //! Call to traverse the graph with a strategy to visit all edges of the graph
    template <typename Node, typename NodeData>
    static VisitOrder tryVisit(Node& node, NodeData& nodeData)
    {
        auto parentCount = node->getParents().size();
        auto requiredCount = parentCount - node->getCycleParentCount();

        auto currentVisit = ++nodeData.visitCount; // increment+read only once. other threads can be doing the same.
        if (requiredCount == 0 && currentVisit == 1)
        {
            return (VisitOrder::eFirst | VisitOrder::eLast);
        }

        VisitOrder ret = VisitOrder::eUnknown;
        if (currentVisit > requiredCount)
        {
            ret = VisitOrder::eCycle;
        }
        else if (currentVisit == requiredCount)
        {
            ret = (currentVisit == 1) ? (VisitOrder::eFirst | VisitOrder::eLast) : VisitOrder::eLast;
        }
        else if (currentVisit == 1)
        {
            ret = VisitOrder::eFirst;
        }
        else
        {
            ret = VisitOrder::eNext;
        }

        return ret;
    }
};
// ef-docs visit-all-end

#ifndef DOXYGEN_BUILD

struct FlowDepthFirst
{
};
struct FlowBreadthFirst
{
};

struct SerialQueue
{
};
struct ConcurrentQueue
{
};

template <typename GraphNode, typename Flow, typename Queue, bool ConstNode, typename Enable = void>
struct TraversalBase
{
};

//! Base traversal class when using DepthFirst traversal order.
template <typename GraphNode, typename Flow, typename Queue, bool ConstNode>
struct TraversalBase<GraphNode, Flow, Queue, ConstNode, std::enable_if_t<std::is_same<Flow, FlowDepthFirst>::value>>
{
    void incrementInfo()
    {
    }
    void decrementInfo()
    {
    }
};

//! Base traversal class when using BreadthFirst traversal order and doesn't require thread safe queue.
template <typename GraphNode, typename Flow, typename Queue, bool ConstNode>
struct TraversalBase<GraphNode,
                     Flow,
                     Queue,
                     ConstNode,
                     std::enable_if_t<std::is_same<Flow, FlowBreadthFirst>::value && std::is_same<Queue, SerialQueue>::value>>
{
    // Note that this class is not currently used in EF, so we don't include it in code coverage reports
    // at the moment (can be changed if serial queues for breadth-first search are utilized later on).
    // LCOV_EXCL_START
    using Node = typename std::conditional_t<ConstNode, const GraphNode, GraphNode>;

    std::queue<Node*> m_queue;

    void push(Node* node)
    {
        m_queue.push(&node);
    }
    bool tryPop(Node*& node)
    {
        if (m_queue.empty())
        {
            return false;
        }

        node = m_queue.front();
        m_queue.pop();
        return true;
    }

    void incrementInfo()
    {
    }
    void decrementInfo()
    {
    }
    bool hasInfo() const
    {
        return false;
    }
    // LCOV_EXCL_STOP
};

//! Base traversal class when using BreadthFirst traversal order and DOES require thread safe queue.
template <typename GraphNode, typename Flow, typename Queue, bool ConstNode>
struct TraversalBase<GraphNode,
                     Flow,
                     Queue,
                     ConstNode,
                     std::enable_if_t<std::is_same<Flow, FlowBreadthFirst>::value && std::is_same<Queue, ConcurrentQueue>::value>>
{
    using Node = typename std::conditional_t<ConstNode, const GraphNode, GraphNode>;

    moodycamel::ConcurrentQueue<Node*> m_queue;
    std::atomic<std::size_t> m_infoCount{ 0 };

    TraversalBase() noexcept
    {
    }

    TraversalBase(TraversalBase& src) = delete;

    void push(Node* node)
    {
        m_queue.enqueue(node);
    }
    bool tryPop(Node*& node)
    {
        return m_queue.try_dequeue(node);
    }

    void incrementInfo()
    {
        m_infoCount++;
    }
    void decrementInfo()
    {
        m_infoCount--;
    }
    bool hasInfo() const
    {
        return m_infoCount.load() > 0;
    }
};

struct NoUserData
{
};

template <typename GraphNode, typename NodeUserData, typename Enable = void>
struct UserDataBase
{
    explicit UserDataBase(std::size_t size) noexcept
    {
    }
};

//! User defined data class to be available for each traversed node
template <typename GraphNode, typename NodeUserData>
struct UserDataBase<GraphNode, NodeUserData, std::enable_if_t<!std::is_same<NodeUserData, NoUserData>::value>>
{
    static_assert(std::is_trivially_copyable<NodeUserData>::value, "User data needs to be trivially copyable");

    explicit UserDataBase(std::size_t size) noexcept : m_userData(size)
    {
    }

    NodeUserData& userData(GraphNode* node)
    {
        return m_userData[node->getIndexInTopology()];
    }

    std::vector<NodeUserData> m_userData;
};

using QueueType = ConcurrentQueue; // or SerialQueue (but serial queue will fail with some multithreaded unit tests).

//! Traversal class
//!
//! @tparam GraphNode       Node typename
//! @tparam Graph           Graph typename
//! @tparam Strategy        Traversal visit strategy (first, last, all) typename
//! @tparam Flow            Visit flow (DepthFirst or BreadthFirst) typename
//! @tparam NodeUserData    Custom user data typename allocated for each node
//! @tparam ConstNode       Is this a const traversal
template <typename GraphNode, typename Graph, typename Strategy, typename Flow, typename NodeUserData, bool ConstNode>
class Traversal : private TraversalBase<GraphNode, Flow, QueueType, ConstNode>,
                  private UserDataBase<GraphNode, NodeUserData>
{
public:
    using Node = typename std::conditional_t<ConstNode, const GraphNode, GraphNode>;
    using Base = TraversalBase<GraphNode, Flow, QueueType, ConstNode>;
    using BaseUserData = UserDataBase<GraphNode, NodeUserData>;

    struct Info
    {
        Traversal& traversal;
        VisitOrder order;

        Info(Traversal& t, VisitOrder o) noexcept : traversal(t), order(o)
        {
            traversal.Base::incrementInfo();
        }
        Info(const Info& src) noexcept : traversal(src.traversal), order(src.order)
        {
            traversal.Base::incrementInfo();
        }
        Info(Info&& src) noexcept : traversal(src.traversal), order(src.order)
        {
            traversal.Base::incrementInfo();
        }
        ~Info()
        {
            traversal.Base::decrementInfo();
        }

        Info& operator=(const Info& rhs) = delete;
        Info& operator=(Info&& rhs) = delete;

        bool isFirstVisit() const
        {
            return (order & VisitOrder::eFirst) == VisitOrder::eFirst;
        }
        bool isLastVisit() const
        {
            return (order & VisitOrder::eLast) == VisitOrder::eLast;
        }

        void continueVisit(GraphNode* node)
        {
            return traversal.continueVisit(node);
        }

        NodeUserData& userData(GraphNode* node)
        {
            return traversal.BaseUserData::userData(node);
        }
    };

    using CallbackFn = std::function<void(Info, GraphNode*, GraphNode*)>;

    explicit Traversal(Graph* g, CallbackFn call) noexcept
        : BaseUserData(g->getMaxNodeIndex()), m_callback(call), m_data(g->getMaxNodeIndex())
    {
    }

    Traversal() = delete;
    Traversal(const Traversal& src) = delete;
    Traversal(Traversal&& src) = delete;
    Traversal& operator=(const Traversal& rhs) = delete;
    Traversal& operator=(Traversal&& rhs) = delete;

    void continueVisit(GraphNode* prev)
    {
        continueImpl(Flow(), prev);
    }

    void startVisit(GraphNode* node)
    {
        startImpl(Flow(), node);
    }

    void markVisited(GraphNode* node)
    {
        nodeData(node).visitCount = node->getParents().size();
    }

private:
    // see if our traversal policy allows us to visit this node
    void tryVisit(GraphNode* prev, GraphNode* current)
    {
        VisitOrder visitOrder = Strategy::tryVisit(current, nodeData(current));
        if (visitOrder > VisitOrder::eUnknown)
        {
            m_callback({ *this, visitOrder }, prev, current);
        }
    }

    void tryContinue(GraphNode* current)
    {
        for (auto child : current->getChildren())
        {
            tryVisit(current, child);
        }
    }

    void continueImpl(FlowDepthFirst, Node* prev)
    {
        tryContinue(prev);
    }

    void continueImpl(FlowBreadthFirst, Node* prev)
    {
        Base::push(prev);
    }

    void startImpl(FlowDepthFirst, Node* node)
    {
        markVisited(node);
        tryContinue(node);
    }

    void startImpl(FlowBreadthFirst, Node* node)
    {
        markVisited(node);
        Base::push(node);

        AtomicBackoff backoff;
        Node* stackNode = nullptr;
        while (true)
        {
            if (Base::tryPop(stackNode))
            {
                tryContinue(stackNode);
                backoff.reset();
                continue;
            }

            if (Base::hasInfo())
            {
                backoff.pause();
            }
            else
            {
                break;
            }
        }
    }

    NodeData& nodeData(GraphNode* node)
    {
        return m_data[node->getIndexInTopology()];
    }

    CallbackFn m_callback;
    std::vector<NodeData> m_data;
};

//! Main traversal template for DepthFirst algorithms
template <typename GraphNode, typename Graph, typename Strategy, typename NodeUserData, bool ConstNode>
void runDepthFirstTraversal(
    typename std::conditional_t<ConstNode, const GraphNode, GraphNode>* node,
    typename Traversal<GraphNode, Graph, Strategy, FlowDepthFirst, NodeUserData, ConstNode>::CallbackFn call)
{
    Traversal<GraphNode, Graph, Strategy, FlowDepthFirst, NodeUserData, ConstNode> traversal(node->getTopology(), call);
    traversal.startVisit(node);
}

//! Main traversal template for BreadthFirst algorithms
template <typename GraphNode, typename Graph, typename Strategy, typename NodeUserData, bool ConstNode>
void runBreadthFirstTraversal(
    typename std::conditional_t<ConstNode, const GraphNode, GraphNode>* node,
    typename Traversal<GraphNode, Graph, Strategy, FlowBreadthFirst, NodeUserData, ConstNode>::CallbackFn call)
{
    Traversal<GraphNode, Graph, Strategy, FlowBreadthFirst, NodeUserData, ConstNode> traversal(node->getTopology(), call);
    traversal.startVisit(node);
}

//! Main traversal template for DepthFirst algorithms. Traversal is allocated on the heap and returned.
template <typename GraphNode, typename Graph, typename Strategy, typename NodeUserData, bool ConstNode>
auto allocAndRunDepthFirstTraversal(
    typename std::conditional_t<ConstNode, const GraphNode, GraphNode>* node,
    typename Traversal<GraphNode, Graph, Strategy, FlowDepthFirst, NodeUserData, ConstNode>::CallbackFn call)
{
    using TraversalType = Traversal<GraphNode, Graph, Strategy, FlowDepthFirst, NodeUserData, ConstNode>;
    std::unique_ptr<TraversalType> traversal = std::make_unique<TraversalType>(node->getTopology(), call);
    traversal->startVisit(node);
    return traversal;
}

//! Main traversal template for BreadthFirst algorithms. Traversal is allocated on the heap and returned.
template <typename GraphNode, typename Graph, typename Strategy, typename NodeUserData, bool ConstNode>
auto allocAndRunBreadthFirstTraversal(
    typename std::conditional_t<ConstNode, const GraphNode, GraphNode>* node,
    typename Traversal<GraphNode, Graph, Strategy, FlowBreadthFirst, NodeUserData, ConstNode>::CallbackFn call)
{
    using TraversalType = Traversal<GraphNode, Graph, Strategy, FlowBreadthFirst, NodeUserData, ConstNode>;
    std::unique_ptr<TraversalType> traversal = std::make_unique<TraversalType>(node->getTopology(), call);
    traversal->startVisit(node);
    return traversal;
}

#endif // DOXYGEN_BUILD

} // detail
} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/ITopology.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::detail::VisitFirst
using VisitFirst = detail::VisitFirst;
//! @copydoc omni::graph::exec::unstable::detail::VisitLast
using VisitLast = detail::VisitLast;
//! @copydoc omni::graph::exec::unstable::detail::VisitAll
using VisitAll = detail::VisitAll;

using detail::FlowBreadthFirst;
using detail::FlowDepthFirst;
using detail::NoUserData;
using detail::Traversal;
using detail::VisitOrder;

//! Performs a depth-first (DFS) traversal of a node.
//!
//! EF has several built-in traversal algorithms:
//!
//! - @rstref{Depth-First <depth_first_search>} traversal recursively visits a node's children before visiting its
//!   siblings. This traversal type is implemented by this function.
//!
//! - @rstref{Breadth-First <breadth_first_search>} traversal recursively visits a node's siblings before visiting its
//!   children.  This traversal type is implemented by @ref traverseBreadthFirst.
//!
//! **Visitation Strategy**
//!
//! The template argument @p Strategy defines the "visitation strategy".  When encountering a node during traversal, the
//! visitation strategy is consulted.  If the strategy gives approval to "visit" the node, the given lambda (i.e. @p
//! call) is invoked.  EF ships with the following different strategies, all of which deal with determining if the node
//! should be visited based on the incoming edge (i.e. nodes can have multiple input edges):
//!
//! - @ref VisitFirst. Invoke the given lambda on the first traversed incoming edge.
//!
//! - @ref VisitLast. Invoke the given lambda after all incoming edges have been traversed (i.e. visit on the last
//!   edge).
//!
//! - @ref VisitAll. Invoke the given lambda for each incoming edge.
//!
//! **User Defined Work/Data**
//!
//! The lambda @p call has the following signature `(void)(auto info, INode* prev, INode* curr)`.
//!
//! @p curr is the node that the visitation strategy has approved for visiting.
//!
//! @p prev is the other end of the incoming edge that was traversed to get to @p curr.
//!
//! @p info is a helper object which serves the following purposes:
//!
//! - Traversal can be continued by calling `info.continueVisit(node)`.  Calling `info.continueVisit(curr)` will
//!   continue the depth-first traversal.  However, `continueVisit` can be called on any node (and even multiple times
//!   in the lambda).  This allows for the traversal of @rstref{graph definitions <ef_graph_definition>} attached to
//!   nodes.
//!
//! - The optional template argument @p NodeUserData defines user defined data that will be allocated for each node to
//!   be traversed.  `info.userData(node)` returns the data for the given node.
//!
//! **Concurrency**
//!
//! This function traverses nodes serially.  Any user data (i.e. @p NodeUserData) allocated during traversal will be
//! destroyed upon this function returning.
//!
//! **Learning More**
//!
//! A high-level traversal guide can be found at @rstref{Traversing a Graph <ef_graph_traversal_guide>} while a more
//! in-depth guide can be found at @rstref{Graph Travesal In-Depth <ef_graph_traversal_advanced>}.
//!
//! See also:
//!
//! - @ref traverseBreadthFirst()
//! - @ref traverseDepthFirstAsync()
//! - @ref traverseBreadthFirstAsync()
template <typename Strategy, typename NodeUserData = NoUserData>
void traverseDepthFirst(INode* node,
                        typename Traversal<INode, ITopology, Strategy, FlowDepthFirst, NodeUserData, false>::CallbackFn call)
{
    detail::runDepthFirstTraversal<INode, ITopology, Strategy, NodeUserData, false>(node, call);
}

//! Performs a breadth-first (BFS) traversal of a node.
//!
//! EF has several built-in traversal algorithms:
//!
//! - @rstref{Depth-First <depth_first_search>} traversal recursively visits a node's children before visiting its
//!   siblings.  This traversal type is implemented by @ref traverseDepthFirst.
//!
//! - @rstref{Breadth-First <breadth_first_search>} traversal recursively visits a node's siblings before visiting its
//!   children.  This traversal type is implemented by this function.
//!
//! **Visitation Strategy**
//!
//! The template argument @p Strategy defines the "visitation strategy".  When encountering a node during traversal, the
//! visitation strategy is consulted.  If the strategy gives approval to "visit" the node, the given lambda (i.e. @p
//! call) is invoked.  EF ships with the following different strategies, all of which deal with determining if the node
//! should be visited based on the incoming edge (i.e. nodes can have multiple input edges):
//!
//! - @ref VisitFirst. Invoke the given lambda on the first traversed incoming edge.
//!
//! - @ref VisitLast. Invoke the given lambda after all incoming edges have been traversed (i.e. visit on the last
//!   edge).
//!
//! - @ref VisitAll. Invoke the given lambda for each incoming edge.
//!
//! **User Defined Work/Data**
//!
//! The lambda @p call has the following signature `(void)(auto info, INode* prev, INode* curr)`.
//!
//! @p curr is the node that the visitation strategy has approved for visiting.
//!
//! @p prev is the other end of the incoming edge that was traversed to get to @p curr.
//!
//! @p info is a helper object which serves the following purposes:
//!
//! - Traversal can be continued by calling `info.continueVisit(node)`.  Calling `info.continueVisit(curr)` will
//!   continue the breadth-first traversal.  However, `continueVisit` can be called on any node (and even multiple times
//!   in the lambda).  This allows for the traversal of @rstref{graph definitions <ef_graph_definition>} attached to
//!   nodes.
//!
//! - The optional template argument @p NodeUserData defines user defined data that will be allocated for each node to
//!   be traversed.  `info.userData(node)` returns the data for the given node.
//!
//! **Concurrency**
//!
//! This function traverses nodes serially.  Any user data (i.e. @p NodeUserData) allocated during traversal will be
//! destroyed upon this function returning.
//!
//! **Learning More**
//!
//! A high-level traversal guide can be found at @rstref{Traversing a Graph <ef_graph_traversal_guide>} while a more
//! in-depth guide can be found at @rstref{Graph Travesal In-Depth <ef_graph_traversal_advanced>}.
//!
//! See also:
//!
//! - @ref traverseDepthFirst()
//! - @ref traverseDepthFirstAsync()
//! - @ref traverseBreadthFirstAsync()
template <typename Strategy, typename NodeUserData = NoUserData>
void traverseBreadthFirst(
    INode* node, typename Traversal<INode, ITopology, Strategy, FlowBreadthFirst, NodeUserData, false>::CallbackFn call)
{
    detail::runBreadthFirstTraversal<INode, ITopology, Strategy, NodeUserData, false>(node, call);
}

//! Performs a depth-first (DFS) traversal of a node while allowing for asynchronous work to be performed by the given
//! lambda.
//!
//! EF has several built-in traversal algorithms:
//!
//! - @rstref{Depth-First <depth_first_search>} traversal recursively visits a node's children before visiting its
//!   siblings. This traversal type is implemented by this function.
//!
//! - @rstref{Breadth-First <breadth_first_search>} traversal recursively visits a node's siblings before visiting its
//!   children.  This traversal type is implemented by @ref traverseBreadthFirstAsync.
//!
//! **Visitation Strategy**
//!
//! The template argument @p Strategy defines the "visitation strategy".  When encountering a node during traversal, the
//! visitation strategy is consulted.  If the strategy gives approval to "visit" the node, the given lambda (i.e. @p
//! call) is invoked.  EF ships with the following different strategies, all of which deal with determining if the node
//! should be visited based on the incoming edge (i.e. nodes can have multiple input edges):
//!
//! - @ref VisitFirst. Invoke the given lambda on the first traversed incoming edge.
//!
//! - @ref VisitLast. Invoke the given lambda after all incoming edges have been traversed (i.e. visit on the last
//!   edge).
//!
//! - @ref VisitAll. Invoke the given lambda for each incoming edge.
//!
//! **User Defined Work/Data**
//!
//! The lambda @p call has the following signature `(void)(auto info, INode* prev, INode* curr)`.
//!
//! @p curr is the node that the visitation strategy has approved for visiting.
//!
//! @p prev is the other end of the incoming edge that was traversed to get to @p curr.
//!
//! @p info is a helper object which serves the following purposes:
//!
//! - Traversal can be continued by calling `info.continueVisit(node)`.  Calling `info.continueVisit(curr)` will
//!   continue the depth-first traversal.  However, `continueVisit` can be called on any node (and even multiple times
//!   in the lambda).  This allows for the traversal of @rstref{graph definitions <ef_graph_definition>} attached to
//!   nodes.
//!
//! - The optional template argument @p NodeUserData defines user defined data that will be allocated for each node to
//!   be traversed.  `info.userData(node)` returns the data for the given node.
//!
//! **Concurrency**
//!
//! This function traverses nodes in depth-first order.  However, unlike @ref traverseDepthFirst(), the given lambda can
//! initiate asynchronous work and continue the traversal.  The net effect is that work can be performed on each node's
//! behalf in parallel.
//!
//! The returned object contains the state of the traversal.  It must remain alive for the duration of any asynchronous
//! work initiated by the given lambda.  It is up to the developer to ensure all work has completed before the returned
//! object goes out-of-scope.
//!
//! It is important to note that this function does not initiate any asynchronous work.  It will simply perform a
//! depth-first traversal of the given node.  What this function does do is *allow the given lambda to initiate
//! asynchronous work*.
//!
//! **Learning More**
//!
//! A high-level traversal guide can be found at @rstref{Traversing a Graph <ef_graph_traversal_guide>} while a more
//! in-depth guide can be found at @rstref{Graph Travesal In-Depth <ef_graph_traversal_advanced>}.
//!
//! See also:
//!
//! - @ref traverseDepthFirst()
//! - @ref traverseBreadthFirst()
//! - @ref traverseBreadthFirstAsync()
template <typename Strategy, typename NodeUserData = NoUserData>
auto traverseDepthFirstAsync(
    INode* node, typename Traversal<INode, ITopology, Strategy, FlowDepthFirst, NodeUserData, false>::CallbackFn call)
{
    return detail::allocAndRunDepthFirstTraversal<INode, ITopology, Strategy, NodeUserData, false>(node, call);
}

//! Performs a breadth-first (BFS) traversal of a node while allowing for asynchronous work to be performed by the given
//! lambda.
//!
//! EF has several built-in traversal algorithms:
//!
//! - @rstref{Depth-First <depth_first_search>} traversal recursively visits a node's children before visiting its
//!   siblings.  This traversal type is implemented by @ref traverseDepthFirstAsync.
//!
//! - @rstref{Breadth-First <breadth_first_search>} traversal recursively visits a node's siblings before visiting its
//!   children.  This traversal type is implemented by this function.
//!
//! **Visitation Strategy**
//!
//! The template argument @p Strategy defines the "visitation strategy".  When encountering a node during traversal, the
//! visitation strategy is consulted.  If the strategy gives approval to "visit" the node, the given lambda (i.e. @p
//! call) is invoked.  EF ships with the following different strategies, all of which deal with determining if the node
//! should be visited based on the incoming edge (i.e. nodes can have multiple input edges):
//!
//! - @ref VisitFirst. Invoke the given lambda on the first traversed incoming edge.
//!
//! - @ref VisitLast. Invoke the given lambda after all incoming edges have been traversed (i.e. visit on the last
//!   edge).
//!
//! - @ref VisitAll. Invoke the given lambda for each incoming edge.
//!
//! **User Defined Work/Data**
//!
//! The lambda @p call has the following signature `(void)(auto info, INode* prev, INode* curr)`.
//!
//! @p curr is the node that the visitation strategy has approved for visiting.
//!
//! @p prev is the other end of the incoming edge that was traversed to get to @p curr.
//!
//! @p info is a helper object which serves the following purposes:
//!
//! - Traversal can be continued by calling `info.continueVisit(node)`.  Calling `info.continueVisit(curr)` will
//!   continue the breadth-first traversal.  However, `continueVisit` can be called on any node (and even multiple times
//!   in the lambda).  This allows for the traversal of @rstref{graph definitions <ef_graph_definition>} attached to
//!   nodes.
//!
//! - The optional template argument @p NodeUserData defines user defined data that will be allocated for each node to
//!   be traversed.  `info.userData(node)` returns the data for the given node.
//!
//! **Concurrency**
//!
//! This function traverses nodes in breadth-first order.  However, unlike @ref traverseBreadthFirst(), the given lambda
//! can initiate asynchronous work and continue the traversal.  The net effect is that work can be performed on each
//! node's behalf in parallel.
//!
//! The returned object contains the state of the traversal.  It must remain alive for the duration of any asynchronous
//! work initiated by the given lambda.  It is up to the developer to ensure all work has completed before the returned
//! object goes out-of-scope.
//!
//! It is important to note that this function does not initiate any asynchronous work.  It will simply perform a
//! breadth-first traversal of the given node.  What this function does do is *allow the given lambda to initiate
//! asynchronous work*.
//!
//! **Learning More**
//!
//! A high-level traversal guide can be found at @rstref{Traversing a Graph <ef_graph_traversal_guide>} while a more
//! in-depth guide can be found at @rstref{Graph Travesal In-Depth <ef_graph_traversal_advanced>}.
//!
//! See also:
//!
//! - @ref traverseDepthFirst()
//! - @ref traverseBreadthFirst()
//! - @ref traverseDepthFirstAsync()
template <typename Strategy, typename NodeUserData = NoUserData>
auto traverseBreadthFirstAsync(
    INode* node, typename Traversal<INode, ITopology, Strategy, FlowBreadthFirst, NodeUserData, false>::CallbackFn call)
{
    return detail::allocAndRunBreadthFirstTraversal<INode, ITopology, Strategy, NodeUserData, false>(node, call);
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
