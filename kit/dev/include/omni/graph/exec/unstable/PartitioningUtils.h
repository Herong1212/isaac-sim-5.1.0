// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file PartitioningUtils.h
//!
//! @brief Defines classes and algorithms to use with @ref omni::graph::exec::unstable::IPartitionPass.
#pragma once

#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/ITopology.h>
#include <omni/graph/exec/unstable/Span.h>
#include <omni/graph/exec/unstable/Traversal.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Specialized container to enable partitioning algorithm via disjoint set like data structure
//!
//! Modifications to typically known algorithm (https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
//! - index set "0" is a special one and matching the root of the graph, i.e. root node will always have index 0
//! - only "selected" nodes are inserted into sets and only these nodes are merged to form groups of nodes based
//!   on partitioning algorithm
//!
//! This object is *not* ABI-safe.
class PartitionSet
{
    //! Deleted default constructor
    PartitionSet() = delete;

    //! Reserved index for root nodes. We leverage that to distinguish between selected and not selected nodes.
    enum : uint64_t
    {
        kReservedRootIndex = 0
    };

public:
    //! Construct a set for a static topology of a given @p topologyNodeCount nodes.
    PartitionSet(std::size_t topologyNodeCount) noexcept : m_parent(topologyNodeCount), m_rank(topologyNodeCount)
    {
    }

    //! Initialize selected nodes
    template <typename V>
    void makeSelectedSets(V& selected)
    {
        for (INode* node : selected)
        {
            auto index = node->getIndexInTopology();
            m_parent[index] = index;
        }
    }

    //! Return true is give node is selected for partitioning and has a set allocated.
    bool isMarked(INode* node) const
    {
        auto index = node->getIndexInTopology();
        return m_parent[index] != kReservedRootIndex;
    }

    //! Find the set this node belongs to. Forwards the call to underlying implementation.
    uint64_t find(INode* node)
    {
        return find(node->getIndexInTopology());
    }

    //! Merge two sets. Forwards the call to underlying implementation.
    void merge(INode* nodeA, INode* nodeB)
    {
        merge(nodeA->getIndexInTopology(), nodeB->getIndexInTopology());
    }

    //! Find set that this index belongs to.
    //!
    //! Search has a side effect, i.e. it flattens the set links directly to the last link in the chain.
    //! This allows for faster search next time same find is performed.
    uint64_t find(uint64_t index)
    {
        if (m_parent[index] != index)
        {
            m_parent[index] = find(m_parent[index]);
        }

        return m_parent[index];
    }

    //! Merge two sets.
    //!
    //! Implementation uses rank to prioritize merging into sets that received more merges.
    //! This improves the search time.
    void merge(uint64_t a, uint64_t b)
    {
        auto aSet = find(a);
        auto bSet = find(b);

        if (aSet == bSet)
            return;

        // Shouldn't happen. Make sure we only merge marked nodes
        OMNI_GRAPH_EXEC_ASSERT(a != kReservedRootIndex && b != kReservedRootIndex);

        if (m_rank[aSet] < m_rank[bSet])
        {
            m_parent[aSet] = bSet;
        }
        else if (m_rank[aSet] > m_rank[bSet])
        {
            m_parent[bSet] = aSet;
        }
        else
        {
            m_parent[bSet] = aSet;
            m_rank[aSet] += 1;
        }
    }

    std::vector<uint64_t> m_parent; //!< We have as many elements as nodes in the topology. Each element represents
                                    //!< a unique set (if it points to its own index), or a link to another set (if
                                    //!< merged)
    std::vector<uint64_t> m_rank; //!< Rank per element used to prevent growing the tree to high and optimizes searches
};

//! Algorithm to group selected nodes into valid partitions based on node ordering.
//!
//! Partition is only valid when there is no path that leaves and comes back to the same group.
//! Such partition would introduce cycles in the graph.
//!
//! Quick algorithm uses a single traversal over the entire graph to determine unique partition index for group of
//! nodes. During traversal, the partition index is based on the node the traversal comes from and:
//! - the partition index is incremented by 1 if edge crosses selected and unselected nodes
//! - the partition index is assigned to the currently visited node only if it is higher than currently set
//!
//! The traversal algorithm visits all the edges in the graph and does continuation on the last visit to the node.
template <typename VerifyAndCreateFn>
void quickPartitioning(ITopology* topology, Span<INode*> selectedNodes, VerifyAndCreateFn&& verifyAndCommitPartitionFn)
{
    if (selectedNodes.size() == 0)
    {
        return; // LCOV_EXCL_LINE
    }

    std::vector<INode*> nodes(selectedNodes.begin(), selectedNodes.end());

    PartitionSet partitions(topology->getMaxNodeIndex());
    partitions.makeSelectedSets(nodes);

    struct QuickPartitioningNodeData
    {
        uint64_t partition{ 0 };
        bool marked{ false };
    };

    traverseDepthFirst<VisitAll, QuickPartitioningNodeData>(
        topology->getRoot(),
        [&partitions](auto info, INode* prev, INode* curr)
        {
            auto& currUserData = info.userData(curr);
            if (info.isFirstVisit())
            {
                currUserData.marked = partitions.isMarked(curr);
            }

            auto& prevUserData = info.userData(prev);
            uint64_t edgePartition = prevUserData.partition;
            if (currUserData.marked != prevUserData.marked)
            {
                edgePartition += 1;
            }

            if (currUserData.partition < edgePartition)
            {
                currUserData.partition = edgePartition;
            }

            if (info.isLastVisit())
            {
                if (currUserData.marked)
                {
                    for (INode* parent : curr->getParents())
                    {
                        auto& parentUserData = info.userData(parent);
                        if (parentUserData.partition == currUserData.partition)
                        {
                            partitions.merge(parent, curr);
                        }
                    }
                }

                info.continueVisit(curr);
            }
        });

    // sort vector by partitions
    std::sort(nodes.begin(), nodes.end(),
              [&partitions](INode* a, INode* b) { return partitions.find(a) < partitions.find(b); });

    // verify and create partitions in the graph
    auto partitionSetBegin = nodes.begin();
    auto partitionSet = partitions.find(*partitionSetBegin);
    auto partitionSetNext = partitionSetBegin;
    do
    {
        partitionSetNext++;

        if (partitionSetNext == nodes.end())
        {
            verifyAndCommitPartitionFn(&(*partitionSetBegin), partitionSetNext - partitionSetBegin);
        }
        else if (partitions.find(*partitionSetNext) != partitionSet)
        {
            verifyAndCommitPartitionFn(&(*partitionSetBegin), partitionSetNext - partitionSetBegin);

            // switch to next partition
            partitionSetBegin = partitionSetNext;
            partitionSet = partitions.find(*partitionSetNext);
        }

    } while (partitionSetNext != nodes.end());
}


} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
