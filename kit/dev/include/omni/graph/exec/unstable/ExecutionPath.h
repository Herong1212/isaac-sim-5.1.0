// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ExecutionPath.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::ExecutionPath.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/SmallStack.h>
#include <omni/graph/exec/unstable/Span.h>
#include <omni/graph/exec/unstable/Types.h>

#include <atomic>
#include <initializer_list>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

class INode;

//! Path representing a unique location of an instantiated node during execution.
//!
//! The @ref omni::graph::exec::unstable::ExecutionPath class is an efficient utility class used to store the *execution
//! path* of an @ref omni::graph::exec::unstable::INode. There's subtlety to what an execution path is. That subtlety is
//! best explained with a diagram:
//!
//! @rst
//!
//! .. image:: /../docs/ef-execution-path-point-k.svg
//!     :align: center
//!
//! @endrst
//!
//! Above, nodes are labelled with lower-case letters (e.g. *a*, *b*, etc.). Node can point to either an
//! @ref omni::graph::exec::unstable::INodeDef (which defines opaque computation) or an @ref
//! omni::graph::exec::unstable::INodeGraphDef (which defines its computation with a subgraph). In the diagram above,
//! @ref omni::graph::exec::unstable::INodeGraphDef objects are labelled with upper-case letters (e.g. *X*, *Y*).
//!
//! Observe that @ref omni::graph::exec::unstable::INodeGraphDef *X* is used by both nodes *e* and *f*. This illustrates
//! that @ref omni::graph::exec::unstable::INodeGraphDef objects can be reused within the graph. This makes sense
//! because @ref omni::graph::exec::unstable::INodeGraphDef is defining computational logic and that logic may be needed
//! in multiple places in the graph (e.g. instancing). Likewise, though not illustrated above, @ref
//! omni::graph::exec::unstable::INodeDef objects can be reused.
//!
//! Consider node *k* above (pointed to by the yellow arrow). When *k* is executing, what is its execution path?  One
//! way to describe the path is to store the nodes traversed to get to the node. For instance, */a/c/m/n/h/i/k* could be
//! a likely path. Lets call this representation of a path the *traversal path*.
//!
//! EF (via @ref omni::graph::exec::unstable::ExecutionPath) does not store *traversal paths*. Rather, it uses a much
//! more compact representation called the *execution path*. In the diagram above, the execution path for *k* is
//! */f/p/k*.
//!
//! @ref omni::graph::exec::unstable::ExecutionPath stores enough information to **uniquely identify the node**. That's
//! important, since *k* is being shared in the diagram above. The execution path */e/k* points to the same *k* node's
//! memory but logically */e/k* and */f/p/k* are different nodes.  This illustrates the main purpose of this object:
//! @ref omni::graph::exec::unstable::INode, @ref omni::graph::exec::unstable::INodeDef, *and* @ref
//! omni::graph::exec::unstable::INodeGraphDef *objects can not be uniquely identified by their raw pointer value.*
//! @ref omni::graph::exec::unstable::ExecutionPath *must be used to uniquely identify a node.*
//!
//! @ref omni::graph::exec::unstable::ExecutionPath is often used as a key in a key/value store to access a node's state
//! data.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! Unless otherwise noted, methods in this class are not thread-safe.
//!
//! To reduce the amount of new paths we create, we only create a new path when entering a node graph definition
//! execution. All tasks generated for computing nodes withing the same node graph will point to the same path.
//!
//! This class can safely be passed by pointer across the ABI.  However, since it is not a trivial type, it cannot be
//! passed by value across the ABI. See @ref OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI for details.
class ExecutionPath
{
    enum : ExecutionPathHash
    {
        kEmptyPathHash = 0
    };

public:
    //! Default constructor for an empty path. Consider using sEmpty if you need one.
    ExecutionPath() noexcept
    {
    }

    //! Copy constructor.
    ExecutionPath(const ExecutionPath& src) noexcept : m_path{ src.m_path }, m_cachedHash(src.m_cachedHash.load())
    {
    }

    //! Assignment operator.
    ExecutionPath& operator=(const ExecutionPath& rhs) noexcept
    {
        m_path = rhs.m_path;
        m_cachedHash.store(rhs.m_cachedHash.load());
        return *this;
    }

    //! Construct a path for a node (used only at the beginning of the execution).
    //!
    //! @p node must not be @c nullptr.
    //!
    //! The given node will not have @ref omni::core::IObject::acquire() called on it.
    explicit ExecutionPath(omni::core::ObjectParam<INode> node) noexcept : m_path{ node.get() }
    {
        OMNI_GRAPH_EXEC_ASSERT(node.get());
    }

    //! Construct a path from an upstream path and a node. Mostly used when entering a node graph definition.
    //!
    //! @p node must not be @c nullptr.
    //!
    //! The given node will not have @ref omni::core::IObject::acquire() called on it.
    ExecutionPath(const ExecutionPath& upPath, omni::core::ObjectParam<INode> node) noexcept
        : m_path{ upPath.m_path, node.get() }
    {
        OMNI_GRAPH_EXEC_ASSERT(node.get());
    }

    //! Convenience method for constructing paths from initializer list.
    //!
    //! The given nodes must not be @c nullptr.
    //!
    //! The given node will not have @ref omni::core::IObject::acquire() called on it.
    explicit ExecutionPath(std::initializer_list<omni::core::ObjectParam<INode>> path) noexcept
        : m_path{ const_cast<INode**>(reinterpret_cast<INode* const*>(path.begin())),
                  const_cast<INode**>(reinterpret_cast<const INode* const*>(path.end())) }
    {
        static_assert(sizeof(INode*) == sizeof(omni::core::ObjectParam<INode>), "unexpected ObjectParam size");
    }

    //! Constructs a path from a list of nodes.
    //!
    //! The given nodes must not be @c nullptr.
    //!
    //! The given nodes will not have @ref omni::core::IObject::acquire() called on them.
    //!
    //! @param path The list of nodes to be considered as a path.
    explicit ExecutionPath(Span<INode* const> path)
        : m_path{ const_cast<INode**>(path.begin()), const_cast<INode**>(path.end()) }
    {
    }

private:
    ExecutionPath(INode** begin, INode** end) noexcept : m_path{ begin, end }
    {
    }

public:
    //! Append a node to the path.
    //!
    //! The given node is not internally acquired and it is up to the calling code to ensure the node remains alive
    //! while in use by this object.
    //!
    //! @thread_safety This method is not thread safe.
    void push(INode* node) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(node);
        m_path.push(node);

        m_cachedHash = kEmptyPathHash;
    }

    //! Return a new path with a last node removed
    //!
    //! @thread_safety This method is not thread safe.
    ExecutionPath copyWithoutTop() const noexcept
    {
        int delta = (m_path.empty() ? 0 : -1);
        return ExecutionPath{ const_cast<INode**>(m_path.begin()), const_cast<INode**>(m_path.end() + delta) };
    }

    //! Compute unique index using pairing function and unique indexes of nodes (within owning topology)
    //!
    //! This is one strategy to generate a hash for a path. Other hashing strategies can be built outside of the class
    //! and used for example when retrieving state from execution context.
    //!
    //! The computed hash is internally cached.
    //!
    //! @thread_safety This method is thread safe.
    inline ExecutionPathHash getHash() const noexcept;

    //! Compute unique index using pairing function and unique indexes of nodes (within owning topology)
    //!
    //! @param  node    Include given node as the last node in the path. This allows us to avoid creating a new path
    //!                 when fetching a state for an execution task.
    //!
    //! @thread_safety This method is thread safe.
    inline ExecutionPathHash getHashWith(omni::core::ObjectParam<INode> node) const noexcept;

    //! Check if path is empty.
    //!
    //! @thread_safety This method is thread safe.
    bool isEmpty() const noexcept
    {
        return m_path.empty();
    }

    //! Access to underlying path container
    //!
    //! @thread_safety This method is not thread safe.
    Span<INode* const> getData() const noexcept
    {
        return Span<INode* const>{ m_path.begin(), m_path.size() };
    }

    //! Return the node at the top of the stack.
    //!
    //! Undefined behavior if the stack is empty.
    //!
    //! @thread_safety This method is not thread safe.
    INode* getTop() const noexcept
    {
        return m_path.top();
    }

    //! An instance of an empty path.
    //!
    //! @warning A different empty path may be returned over multiple calls of this method. Do not rely on using a
    //!          pointer to the returned object to check if another path is the empty path.  Rather, use the @ref
    //!          isEmpty() method to check if a path is empty.
    //!
    //! @thread_safety This method is thread safe.
    static const ExecutionPath& getEmpty() noexcept
    {
        static ExecutionPath sPath; // unique per DLL
        return sPath;
    }

    //! Pairing function used by the hashing algorithm
    //!
    //! @thread_safety This method is thread safe.
    static ExecutionPathHash pairingFunction(ExecutionPathHash a, ExecutionPathHash b)
    {
        return static_cast<ExecutionPathHash>(((a + b) * (a + b + 1) * 0.5) + b);
    }

private:
    // Container for nodes forming the path
    //
    // We use a small stack to reduce the need of heap allocations.
    using PathStorage = detail::SmallStack<INode*>;

    PathStorage m_path; //!< Path is defined by a series of nodes that we visit during task generation

    //! Cache used to accelerate getHash method. We decided to go with mutable version, since we want to preserve
    //! the const correctness in places that receive the path, i.e. we don't want anyone to attempt mutating the
    //! path from these places. The alternative would be to not provide caching which means we give up performance
    //! and that is not acceptable.
    mutable std::atomic<ExecutionPathHash> m_cachedHash{ kEmptyPathHash };
};

#ifndef DOXYGEN_BUILD // macros called in namespaces seem to upset doxygen
OMNI_STATIC_ASSERT_MUST_BE_PASSED_BY_POINTER_IN_ABI(ExecutionPath);
static_assert(72 == sizeof(ExecutionPath), "ExecutionPath is an unexpected size");
#endif

//! Comparison operator.
inline bool operator==(const ExecutionPath& lhs, const ExecutionPath& rhs) noexcept
{
    return lhs.getHash() == rhs.getHash();
}

//! Comparison operator.
inline bool operator!=(const ExecutionPath& lhs, const ExecutionPath& rhs) noexcept
{
    return lhs.getHash() != rhs.getHash();
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

// includes needed for method implementations
#include <omni/graph/exec/unstable/INode.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

inline ExecutionPathHash ExecutionPath::getHash() const noexcept
{
    if (m_path.empty())
    {
        return kEmptyPathHash;
    }

    if (m_cachedHash != kEmptyPathHash)
        return m_cachedHash;

    ExecutionPathHash result = kEmptyPathHash;
    for (INode* node : m_path)
    {
        result = pairingFunction(result, node->getIndexInTopology());
    }

    // no need for compare and exchange...all threads that potentially computed this cache will generate the same result
    // and since write is atomic, all reads will see correct value
    m_cachedHash = result;

    return result;
}

inline ExecutionPathHash ExecutionPath::getHashWith(omni::core::ObjectParam<INode> node) const noexcept
{
    OMNI_GRAPH_EXEC_ASSERT(node.get());
    ExecutionPathHash result = getHash();
    return pairingFunction(result, node->getIndexInTopology());
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
