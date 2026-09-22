// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Topology.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::Topology.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/CompactUniqueIndex.h>
#include <omni/graph/exec/unstable/ITopology.h>
#include <omni/graph/exec/unstable/Node.h>

#include <tuple>
#include <unordered_map>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::ITopology
class Topology : public Implements<ITopology>
{
public:
    //! Creates a new topology.
    //!
    //! The given name must not be @c nullptr.
    //!
    //! This method always returns a valid object.
    static omni::core::ObjectPtr<Topology> create(const carb::cpp::string_view& rootDebugName) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(rootDebugName.data());
        return omni::core::steal(new Topology(rootDebugName));
    }

protected:
    //! @copydoc omni::graph::exec::unstable::ITopology::getMaxNodeIndex_abi
    uint64_t getMaxNodeIndex_abi() noexcept override
    {
        return m_nodeIndexes.size();
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::getRoot_abi
    INode* getRoot_abi() noexcept override
    {
        return m_root.get();
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::getStamp_abi
    Stamp getStamp_abi() noexcept override
    {
        return m_version;
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::invalidate_abi
    void invalidate_abi() noexcept override
    {
        if (isValid())
        {
            m_version.next();
            _forwardInvalidation();
        }
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::acquireNodeIndex_abi
    NodeIndexInTopology acquireNodeIndex_abi() noexcept override
    {
        return m_nodeIndexes.acquireUniqueIndex();
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::releaseNodeIndex_abi
    void releaseNodeIndex_abi(NodeIndexInTopology index) noexcept override
    {
        m_nodeIndexes.releaseUniqueIndex(index);
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::addInvalidationForwarder_abi
    virtual void addInvalidationForwarder_abi(InvalidationForwarderId owner,
                                              IInvalidationForwarder* callback) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(callback);
        m_invalidationForwarders.emplace( // may throw
            std::piecewise_construct, std::forward_as_tuple(owner), std::forward_as_tuple(callback, omni::core::kBorrow));
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::removeInvalidationForwarder_abi
    void removeInvalidationForwarder_abi(InvalidationForwarderId owner) noexcept override
    {
        auto foundIt = m_invalidationForwarders.find(owner);
        if (foundIt != m_invalidationForwarders.end())
        {
            m_invalidationForwarders.erase(foundIt);
        }
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::getConstructionStamp_abi
    SyncStamp getConstructionStamp_abi() noexcept override
    {
        return m_constructionStamp;
    }

    //! @copydoc omni::graph::exec::unstable::ITopology::_setConstructionInSync_abi
    void _setConstructionInSync_abi(Stamp toSync) noexcept override
    {
        m_constructionStamp.sync(toSync);
    }

    //! Constructor
    explicit Topology(const carb::cpp::string_view& rootDebugName) noexcept
        : m_root{ Node::create(this, rootDebugName) }
    {
        static Stamp sTopologyVersion;
        sTopologyVersion.next();
        m_version = sTopologyVersion;
    }

    //! Destructor
    virtual ~Topology() noexcept
    {
        // prevent the root node's ~Node() trying to invalidate the topology
        m_version.next();
    }

private:
    //! Invoke invalidation forwarders
    void _forwardInvalidation() noexcept
    {
        for (auto& pair : m_invalidationForwarders)
        {
            pair.second->invoke(this);
        }
    }

    CompactUniqueIndex m_nodeIndexes; //!< Compact registry of nodes unique indexes
    omni::core::ObjectPtr<INode> m_root; //!< Root node allowing to discover all nodes within the current topology
    Stamp m_version; //!< Topology version used by nodes to detect if they belong to current topology version
    SyncStamp m_constructionStamp; //!< Synchronized with @ref omni::graph::exec::unstable::IGraphBuilderContext.
                                   //!< Allows detecting in which construction pass this topology was altered.

    //! Array of functions to call on topology invalidation
    std::unordered_map<InvalidationForwarderId, omni::core::ObjectPtr<IInvalidationForwarder>> m_invalidationForwarders;
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
