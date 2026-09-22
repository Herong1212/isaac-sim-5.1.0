// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file PassPipeline.h
//!
//! @brief Declares @ref omni::graph::exec::unstable::PassPipeline.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/IGlobalPass.h>
#include <omni/graph/exec/unstable/IGraphBuilder.h>
#include <omni/graph/exec/unstable/INodeGraphDef.h>
#include <omni/graph/exec/unstable/IPartitionPass.h>
#include <omni/graph/exec/unstable/IPassPipeline.h>
#include <omni/graph/exec/unstable/IPassRegistry.h>
#include <omni/graph/exec/unstable/IPassTypeRegistry.h>
#include <omni/graph/exec/unstable/IPopulatePass.h>
#include <omni/graph/exec/unstable/Traversal.h>
#include <omni/graph/exec/unstable/Types.h>

#include <algorithm>
#include <tuple>
#include <unordered_map>
#include <vector>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! @copydoc omni::graph::exec::unstable::IPassPipeline
template <typename GraphBuilderT, typename... Bases>
class PassPipelineT : public Implements<Bases...>
{
public:
    //! Creates and returns a @ref IPassPipeline.
    //!
    //! This method always returns a valid object.
    static omni::core::ObjectPtr<PassPipelineT> create() noexcept
    {
        return omni::core::steal(new PassPipelineT);
    }

protected:
    //! @copydoc omni::graph::exec::unstable::IPassPipeline::needsConstruction_abi
    bool needsConstruction_abi() noexcept override
    {
        return !m_registryCache.inSync(getPassRegistry()->getStamp());
    }

    //! @copydoc omni::graph::exec::unstable::IPassPipeline::construct_abi
    void construct_abi() noexcept override
    {
        auto registry = getPassRegistry();
        if (m_registryCache.makeSync(registry->getStamp()))
        {
            m_populatePasses.clear();
            auto populatePasses = registry->getPassTypeRegistry(PassType::ePopulate);
            OMNI_GRAPH_EXEC_ASSERT(populatePasses);
            if (populatePasses)
            {
                for (auto& record : populatePasses->getPasses())
                {
                    m_populatePasses.emplace(record.nameToMatch->getHash(), record); // may throw
                }
            }

            m_partitionPasses.clear();
            auto partitionPasses = registry->getPassTypeRegistry(PassType::ePartitioning);
            OMNI_GRAPH_EXEC_ASSERT(partitionPasses);
            if (partitionPasses)
            {
                for (auto& record : partitionPasses->getPasses())
                {
                    _insert_sorted(m_partitionPasses, record,
                                   [](const PassTypeRegistryEntry& a, const PassTypeRegistryEntry& b) -> bool
                                   { return a.priority > b.priority; }); // may throw
                }
            }
        }
    }

    //! @copydoc omni::graph::exec::unstable::IPassPipeline::needsRun_abi
    bool needsRun_abi(Stamp globalTopology) noexcept override
    {
        return !m_globalTopology.inSync(globalTopology);
    }

    //! @copydoc omni::graph::exec::unstable::IPassPipeline::run_abi
    //!
    //! Acceleration structure is generated on changes to @ref omni::graph::exec::unstable::IPassRegistry
    //! to organize passes for this pipeline.
    //!
    //! @note Passes are run single-threaded in core implementation because we have no access to rich
    //! threading library in OV. We have parallel version available in *omni.kit.exec.core*.
    void run_abi(IGraphBuilderContext* builderContext, INodeGraphDef* nodeGraphDef) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(builderContext);
        OMNI_GRAPH_EXEC_ASSERT(nodeGraphDef);

        auto globalTopologyStamp = builderContext->getGraph()->getGlobalTopologyStamp();
        if (!m_globalTopology.inSync(*globalTopologyStamp))
        {
            if (this->needsConstruction())
            {
                this->construct(); // may throw
            }

            _runPopulatePass(builderContext, nodeGraphDef);
            _runGlobalPass(builderContext, nodeGraphDef);

            m_globalTopology.sync(*globalTopologyStamp);
        }
    }

    //! Run populate passes
    //!
    //! The algorithm will traverse the graph with DFS order serially. For each visited node,
    //! it will give a chance to registered population passes to populate the definition
    //! of discovered @ref omni::graph::exec::unstable::INode or @ref omni::graph::exec::unstable::INodeGraphDef.
    //!
    //! To preserve instancing within a single NodeGraphDef, algorithm will keep a track of discovered
    //! NodeGraphDefs and populate/continue traversal of only first visited node that instantiates it.
    //! Later when internal state goes out of scope, all instances are updated to point to same definition.
    //!
    //! This algorithm is wrote in a way to follow the multithreaded version from omni.kit.exec.core and
    //! the goal is to replace it with multithreaded version once OM-70769 is closed.
    void _runPopulatePass(IGraphBuilderContext* builderContext, INodeGraphDef* nodeGraphDef)
    {
        class PassState
        {
            struct Record
            {
                INode* orgNode{ nullptr };
                // This definition might have been released if it is only single instance
                // and it was changed during graph transformation. That's ok, since we will
                // only use the address of the pointer, and only if other instances exist
                // (if so, they will own a reference to this pointer making it still valid)
                INodeGraphDef* orgNodeGraphDef{ nullptr };
                // definitions are referenced by nodes in the graph, but can as well be hold
                // by the authoring side for fast access. We will allocate a small space
                // for these cases to avoid dynamic allocation cost when reserving space upfront for all instances
                // based on use count.
                SmallVector<INode*, 2> accumulatedInstances;

                static_assert(
                    sizeof(accumulatedInstances) == 24,
                    "Expecting sizeof(SmallVector<INode*, 2>) to be 24 bytes and match sizeof an empty std::vector");

                Record(INode* instance, INodeGraphDef* nodeGraphDef) : orgNode(instance), orgNodeGraphDef(nodeGraphDef)
                {
                    accumulatedInstances.reserve(useCount(nodeGraphDef));
                }

                void addInstance(INode* instance)
                {
                    accumulatedInstances.emplace_back(instance);
                }

                void processInstances()
                {
                    if (accumulatedInstances.size() == 0)
                        return;

                    auto newNodeGraphDef = orgNode->getNodeGraphDef();
                    OMNI_GRAPH_EXEC_ASSERT(newNodeGraphDef);
                    if (newNodeGraphDef != orgNodeGraphDef)
                    {
                        for (auto node : accumulatedInstances)
                        {
                            exec::unstable::cast<IGraphBuilderNode>(node)->_setNodeGraphDef(newNodeGraphDef);
                        }
                    }
                }
            };

        public:
            PassState(PassPipelineT* owner, IGraphBuilderContext* builderContext, INodeGraphDef* nodeGraphDef)
                : m_passPipeline(owner)
            {
                m_builder = GraphBuilder::createForPass(builderContext, nodeGraphDef);
            }

            ~PassState()
            {
                // Update instances
                for (auto& pair : m_registry)
                {
                    pair.second.processInstances();
                }

                // If this NodeGraphDef changed in this population pass, run the partitioning pass on it
                auto* nodeGraphDef = m_builder->getNodeGraphDef();
                auto* builderContext = m_builder->getContext();
                auto constructionStamp = nodeGraphDef->getTopology()->getConstructionStamp();
                if (constructionStamp.inSync(builderContext->getConstructionStamp()))
                    m_passPipeline->_runPartitionPass(builderContext, nodeGraphDef);
            }

            IGraphBuilder* getBuilder()
            {
                return m_builder.get();
            }

            //! Store record of a node graph if it has multiple instances referencing it.
            //!
            //! Returns true if a new record was generated for this NodeGraphDef.
            //! It also returns true when nodeGraphDef has only single instance referencing it. For performance
            //! reasons we don't store such record in the container which reduces cost in updateInstances method.
            bool addRecord(INode* instance, INodeGraphDef* nodeGraphDef)
            {
                auto fountIt = m_registry.find(nodeGraphDef);
                if (fountIt == m_registry.end())
                {
                    m_registry.emplace(std::piecewise_construct, std::forward_as_tuple(nodeGraphDef),
                                       std::forward_as_tuple(instance, nodeGraphDef));
                    return true;
                }
                else
                {
                    fountIt->second.addInstance(instance);
                    return false;
                }
            }

        private:
            PassPipelineT* m_passPipeline;
            GraphBuilderPtr m_builder;

            using Container = std::unordered_map<INodeGraphDef*, Record>;
            Container m_registry;
        };

        auto traversalFnImp = [this, builderContext](INodeGraphDef* nodeGraphDef, auto& fn) -> void
        {
            PassState nodeGraphDefPassState(this, builderContext, nodeGraphDef);

            traverseDepthFirst<VisitFirst>(
                nodeGraphDef->getTopology()->getRoot(),
                [this, &nodeGraphDefPassState, &fn](auto info, INode* prev, INode* curr)
                {
                    bool processNodeGraphDef = true;

                    auto builder = nodeGraphDefPassState.getBuilder();
                    auto foundIt = this->m_populatePasses.find(curr->getName().getHash());
                    if (foundIt != this->m_populatePasses.end())
                    {
                        auto newPass = foundIt->second.factory->createPass(builder);
                        auto newPopulatePass = exec::unstable::cast<IPopulatePass>(newPass);
                        newPopulatePass->run(builder, curr);
                    }
                    else if (auto currNodeGraphDef = curr->getNodeGraphDef())
                    {
                        auto foundIt = this->m_populatePasses.find(currNodeGraphDef->getName().getHash());
                        if (foundIt != this->m_populatePasses.end())
                        {
                            processNodeGraphDef = nodeGraphDefPassState.addRecord(curr, currNodeGraphDef);
                            if (processNodeGraphDef)
                            {
                                auto newPass = foundIt->second.factory->createPass(builder);
                                auto newPopulatePass = exec::unstable::cast<IPopulatePass>(newPass);
                                newPopulatePass->run(builder, curr);
                            }
                        }
                    }

                    if (processNodeGraphDef)
                    {
                        // re-acquire the graph node def (because there might have been pass
                        // that expanded it) and traverse inside
                        if (auto nodeGraphDef = curr->getNodeGraphDef())
                        {
                            fn(nodeGraphDef, fn);
                        }
                    }
                    info.continueVisit(curr);
                });

            // nodeGraphDefPassState is going out of scope and will trigger additional work
            // the code is structure this way to make it easier for multithreaded execution
            // where partitioning pass should run when the last reference of the state is removed.
        };

        traversalFnImp(nodeGraphDef, traversalFnImp);
    }

    //! Run partition passes
    void _runPartitionPass(IGraphBuilderContext* builderContext, INodeGraphDef* nodeGraphDef)
    {
        // Partition passes require NodeGraphDef's to provide node factory. Skip ones that doesn't
        // implement it.
        if (!nodeGraphDef->getNodeFactory())
        {
            return;
        }

        auto builder{ GraphBuilderT::createForPass(builderContext, nodeGraphDef) };

        INode* root = nodeGraphDef->getTopology()->getRoot();

        std::vector<PartitionPassPtr> passInstances;
        passInstances.reserve(m_partitionPasses.size());

        // Initialize partitioning passes
        for (auto& record : m_partitionPasses)
        {
            auto newPass = record.factory->createPass(builder);
            auto newPartitionPass = exec::unstable::cast<IPartitionPass>(newPass);
            if (newPartitionPass->initialize(nodeGraphDef->getTopology()))
            {
                passInstances.emplace_back(newPartitionPass, omni::core::kBorrow);
            }
        }

        // No need to do the traversal if nothing initialized for this node graph def
        if (passInstances.size() == 0)
            return;

        // Select nodes for partitioning
        traverseDepthFirst<VisitFirst>(root,
                                       [this, &passInstances](auto info, INode* prev, INode* curr)
                                       {
                                           for (auto& pass : passInstances)
                                           {
                                               pass->run(curr);
                                           }
                                           info.continueVisit(curr);
                                       });

        // commit changes to the definition
        for (auto& pass : passInstances)
        {
            pass->commit(builder);
        }
    }

    //! Run global passes
    void _runGlobalPass(IGraphBuilderContext* builderContext, INodeGraphDef* nodeGraphDef)
    {
        auto builder{ GraphBuilderT::createForPass(builderContext, nodeGraphDef) };

        auto registry = getPassRegistry();
        auto globalPasses = registry->getPassTypeRegistry(PassType::eGlobal);
        for (auto& record : globalPasses->getPasses())
        {
            auto newPass = record.factory->createPass(builder); // may throw
            auto newGlobalPass = exec::unstable::cast<IGlobalPass>(newPass);
            newGlobalPass->run(builder);
        }
    }

    //! Helper function to insert an item into a vector in sorted order.
    template <typename T, typename Compare>
    typename std::vector<T>::iterator _insert_sorted(std::vector<T>& vec, T const& item, Compare comp)
    {
        return vec.insert(std::upper_bound(vec.begin(), vec.end(), item, comp), item);
    }

    //! Type of acceleration structure holding population passes
    using PopulatePassCache = std::unordered_map<NameHash, PassTypeRegistryEntry>;

    SyncStamp m_registryCache; //!< Synchronized with cache registry version allows us to detect changes
    SyncStamp m_globalTopology; //!< Synchronized with execution graph allows us to detect changes to run the
                                //!< pipeline
    PopulatePassCache m_populatePasses; //!< Acceleration structure for this pipeline to speed up the searches
    std::vector<PassTypeRegistryEntry> m_partitionPasses; //!< Acceleration structure to keep passes ordered for this
                                                          //!< pipeline. We order from the highest priority to the
                                                          //!< lowest.
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

#include <omni/graph/exec/unstable/GraphBuilder.h>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{
//! Core PassPipeline implementation for @ref omni::graph::exec::unstable::IPassPipeline
using PassPipeline = PassPipelineT<GraphBuilder, IPassPipeline>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
