// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ExecutionContext.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::ExecutionContext.
#pragma once

#include <carb/thread/RecursiveSharedMutex.h>
#include <carb/thread/Spinlock.h>

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/ExecutionPath.h>
#include <omni/graph/exec/unstable/Executor.h>
#include <omni/graph/exec/unstable/IExecutionContext.h>
#include <omni/graph/exec/unstable/IGraph.h>
#include <omni/graph/exec/unstable/INodeGraphDefDebug.h>
#include <omni/graph/exec/unstable/SmallVector.h>
#include <omni/graph/exec/unstable/Traversal.h>

#include <thread>
#include <unordered_map>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Implementation details for omni::graph::exec.  Items in this namespace should not be relied on outside of the API.
namespace detail
{

//! Utility class for discovering all execution paths for a given definition
//!
//! Searches are cached until topology of execution graph changes.
//! Invalidation of the cache happens lazy upon request.
//!
//! This class is thread-safe and can be utilized recurrently.
class ExecutionPathCache
{
public:
    //! Default constructor is removed
    ExecutionPathCache() = delete;

    //! Constructor
    explicit ExecutionPathCache(IGraph& graph) noexcept : m_graph(graph)
    {
    }

    //! Call given function for every execution path that points to given node or node graph definition
    //!
    //! Function should have the signature of `void(const ExecutionPath&)`
    template <typename Key>
    void applyOnEach(const Key& key, IApplyOnEachFunction& applyFn)
    {
        if (m_graph.inBuild())
        {
            // Traversing the entire graph while building it is isn't allowed since multiple threads may be building it.
            OMNI_GRAPH_EXEC_ASSERT(!m_graph.inBuild());
            return;
        }

        if (!m_graph.getTopology()->isValid())
        {
            return;
        }

        // If we're targeting the top-level NodeGraphDef that belongs to the execution graph,
        // simply execute the function here and skip subsequent processing.
        if (_isMatch(key, m_graph.getNodeGraphDef()))
        {
            applyFn.invoke(ExecutionPath::getEmpty());
            return;
        }

        auto discoverAndApplyOnNodesWithDefinitionFn = [this, &key, &applyFn](
                                                           const ExecutionPath& upstreamPath, INodeGraphDef& graph,
                                                           Paths& collectedPaths, auto recursionFn) -> void
        {
            traverseDepthFirst<VisitFirst>(
                graph.getRoot(),
                [this, &upstreamPath, &key, &recursionFn, &applyFn, &collectedPaths](auto info, INode* prev, INode* curr)
                {
                    auto currNodeGraph = curr->getNodeGraphDef();
                    if (currNodeGraph)
                    {
                        ExecutionPath newUpstreamPath(upstreamPath, curr);
                        recursionFn(newUpstreamPath, *currNodeGraph, collectedPaths, recursionFn);
                    }

                    auto def = curr->getDef();
                    if (def && _isMatch(key, def))
                    {
                        collectedPaths.emplace_back(upstreamPath, curr);
                        applyFn.invoke(collectedPaths.back());
                    }

                    info.continueVisit(curr);
                });
        };

        // Check if the this cache is in-sync with the current topology. Since we can run this method in parallel, we
        // need a read lock to m_mutex to safely read m_topologyStamp.
        std::shared_lock<MutexType> readLock(m_mutex);

        auto topologyStamp = *m_graph.getGlobalTopologyStamp();
        if (!m_topologyStamp.inSync(topologyStamp))
        {
            // Cache is out-of-sync; upgrade to a write lock.
            readLock.unlock();
            {
                // Here we once again check to see if the cache is in-sync since another thread may have beat this
                // thread to the write lock and brought the cache into sync.
                std::lock_guard<MutexType> writeLock(m_mutex);
                if (m_topologyStamp.makeSync(topologyStamp))
                {
                    // We're the thread that got to the write lock first, so it's our job to clear the cache.
                    m_defCache.clear();
                    m_nameCache.clear();
                }
            }

            // Grab the read lock again so we can safely read the cache.
            readLock.lock();
        }

        auto& cache = _getCache(key);
        auto findIt = cache.find(key);
        if (findIt != cache.end())
        {
            // We've seen this name before. Make a copy of the paths so we can release the readLock. This is
            // required because an invocation can result in re-entering and taking the writeLock.
            auto pathsCopy = findIt->second;
            readLock.unlock();
            for (ExecutionPath& path : pathsCopy)
            {
                applyFn.invoke(path);
            }
        }
        else
        {
            // Release readLock because apply below can result in re-entry of this function.
            readLock.unlock();
            // Either the key wasn't found or we're building the graph.
            Paths paths;
            discoverAndApplyOnNodesWithDefinitionFn(
                ExecutionPath::getEmpty(), *m_graph.getNodeGraphDef(), paths, discoverAndApplyOnNodesWithDefinitionFn);

            // Insert only once we collected all the paths. Some other thread may be looking for this definition at
            // the same time.
            std::lock_guard<MutexType> writeLock(m_mutex);
            cache.emplace(key, std::move(paths));
        }
    }

private:
    bool _isMatch(const ConstName& desired, IDef* candidate) noexcept
    {
        return (desired == candidate->getName());
    }

    bool _isMatch(IDef* desired, IDef* candidate) noexcept
    {
        return (desired == candidate);
    }

    auto& _getCache(const ConstName&) noexcept
    {
        return m_nameCache;
    }

    auto& _getCache(IDef*) noexcept
    {
        return m_defCache;
    }

    using Paths = SmallVector<ExecutionPath, 2>;
    using DefCache = std::unordered_map<IDef*, Paths>;
    using NameCache = std::unordered_map<ConstName, Paths>;
    using MutexType = carb::thread::recursive_shared_mutex;

    IGraph& m_graph; //!< Execution graph to search for execution paths
    DefCache m_defCache; //!< Storage for already discovered paths (keyed on def ptr)
    NameCache m_nameCache; //!< Storage for already discovered paths (keyed on def name)
    MutexType m_mutex; //!< Mutex to allow concurrent utilization of cache and serialized insertion
    SyncStamp m_topologyStamp; //!< Topology of execution graph this cache is valid for
};

//! Executor implementation that's used to evaluate the associated definitions of single nodes
//! via calls to @ref omni::graph::exec::unstable::ExecutionContext::executeNode_abi. Prevents
//! the executor from attempting to unnecessarily continue graph traversal and task scheduling
//! downstream of the initially-computed node once said node's evaluation has completed.
class ExecutorSingleNode final : public ExecutorFallback
{
public:
    static omni::core::ObjectPtr<ExecutorSingleNode> create(omni::core::ObjectParam<ITopology> toExecute,
                                                            const ExecutionTask& thisTask)
    {
        return omni::core::steal(new ExecutorSingleNode(toExecute.get(), thisTask));
    }

private:
    ExecutorSingleNode(ITopology* toExecute, const ExecutionTask& thisTask) : ExecutorFallback(toExecute, thisTask)
    {
    }

    Status continueExecute_abi(ExecutionTask* currentTask) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(currentTask);

        return currentTask->getExecutionStatus();
    }
};

} // namespace detail

//! @copydoc omni::graph::exec::unstable::IExecutionContext
template <typename StorageType, typename ParentInterface = IExecutionContext>
class ExecutionContext : public Implements<ParentInterface>
{
protected:
    //! Helper RAII object controlling in execution flag. Note that this object will handle
    //! the execution flag differently depending on whether or not recursive execution (i.e.,
    //! invoking execution from a specific context within another task) is allowed. This
    //! recursive execution pattern is only allowed for on-demand definition evaluation
    //! (i.e., calls to executeNode_abi).
    class ScopedInExecute
    {
    public:
        //! Constructor.
        ScopedInExecute(ExecutionContext& context, const bool recursive) noexcept
            : m_context(context), m_recursive(recursive)
        {
            // Note that we skip adding a new thread ID if we're (a) accounting for recursive
            // execution, and (b) we've invoked context evaluation from within some executed
            // task. This helps in preventing deadlocks from occurring when parallel-scheduled
            // tasks directly invoke on-demand execution of other definitions via the context.
            if ((m_recursive && !getCurrentTask()) || !m_recursive)
            {
                std::lock_guard<carb::thread::Spinlock> lock(m_context.m_threadIdSpinlock);
                ++m_context.m_contextThreadIds[std::this_thread::get_id()];
            }
        }
        //! Destructor.
        ~ScopedInExecute() noexcept
        {
            if ((m_recursive && !getCurrentTask()) || !m_recursive)
            {
                std::lock_guard<carb::thread::Spinlock> lock(m_context.m_threadIdSpinlock);
                --m_context.m_contextThreadIds[std::this_thread::get_id()];
                if (m_context.m_contextThreadIds[std::this_thread::get_id()] == 0)
                {
                    m_context.m_contextThreadIds.erase(std::this_thread::get_id());
                }
            }
        }

    private:
        ExecutionContext& m_context; //!< Context in execution.
        const bool m_recursive; //!< Flag for specifying if the ScopedInExecute should alter its
                                //!< execution-flag-handling logic to account for recursive context
                                //!< evaluation.
    };

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::getExecutionStamp_abi
    Stamp getExecutionStamp_abi() noexcept override
    {
        return m_executionStamp;
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::inExecute_abi
    bool inExecute_abi() noexcept override
    {
        std::lock_guard<carb::thread::Spinlock> lock(m_threadIdSpinlock);
        return !m_contextThreadIds.empty();
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::isExecutingThread_abi
    bool isExecutingThread_abi() noexcept override
    {
        std::lock_guard<carb::thread::Spinlock> lock(m_threadIdSpinlock);
        return m_contextThreadIds.find(std::this_thread::get_id()) != m_contextThreadIds.end();
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::execute_abi
    Status execute_abi() noexcept override
    {
        this->initialize();

        m_executionStamp = _getNextGlobalExecutionStamp();

        ScopedInExecute scopedInExecute(*this, false);
        ScopedExecutionDebug scopedDebug{ m_graph->getNodeGraphDef() };

        return getCurrentThread()->executeGraph(m_graph, this);
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::executeNode_abi
    Status executeNode_abi(const ExecutionPath* path, INode* node) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(path);
        OMNI_GRAPH_EXEC_ASSERT(node);

        this->initialize();

        m_executionStamp = _getNextGlobalExecutionStamp();

        ScopedInExecute scopedInExecute(*this, true);
        ScopedExecutionDebug scopedDebug{ m_graph->getNodeGraphDef() };

        auto def = node->getDef();
        if (def)
        {
            // Part of the Executor's (here referring to the templated "default" implementation of IExecutor that
            // comes with EF) top-level execute() method queries its scheduler's status, which pops the current task
            // from the queue, executes it, and automatically tells the executor to continue with its traversal. The
            // subsequent continued executor traversals then keep scheduling work for evaluating all downstream
            // dependent nodes until the scheduler's task list is cleared. On-demand execution of individual definitions
            // (via ExecutionContext::executeNode), however, does not call into this code-path; it instead creates and
            // directly executes a temporary task with a temporary executor for the specified node. As a result, if one
            // were to simply use the ExecutorFallback here, the eventual call to continueExecute after computing the
            // given task would force the executor to take one more unnecessary "step" downstream to try and process a
            // child. This can cause many issues to unfold, some of which will be listed here:
            // - The top-level call to execute the temporary task actually ends up returning the status of this
            // continued
            //   traversal, which won't necessarily line up with the execution status of the temporary task (despite us
            //   only caring about the latter in this situation). For example, if the specified node was successfully
            //   executed, but then the next node in the chain is scheduled for deferred execution, the final returned
            //   status will be a combination of eSuccess and eDeferred.
            // - If the child node that gets processed after the initially-targeted/evaluated node is set to bypass
            // scheduling,
            //   then it will be incorrectly executed on-the-spot, which does not reflect the original query made by
            //   executeNode(). Depending on the definitions, this can be unnecessarily costly.
            // In addition to the above, even if the extra traversal step doesn't cause any issues to immediately arise,
            // there's no need to spend CPU cycles on code-paths that don't need to be run in this specific situation.

            ExecutionTask newTask{ this, node, *path };
            auto tmpExecutor = detail::ExecutorSingleNode::create(node->getTopology(), newTask);
            return newTask.execute(tmpExecutor);
        }
        else
        {
            // There was no work to be done, so we successfully no-op!
            return Status::eSuccess;
        }
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::initialize_abi
    void initialize_abi() noexcept override
    {
        if (!m_initStamp.makeSync(m_graph->getTopology()->getStamp()))
        {
            return; // in sync
        }

        auto traversalFn = [this](INodeGraphDef* nodeGraphDef, const ExecutionPath& path, auto& recursionFn) -> void
        {
            ExecutionTask info(this, nodeGraphDef->getRoot(), path);
            nodeGraphDef->initializeState(info);

            traverseDepthFirst<VisitFirst>(nodeGraphDef->getRoot(),
                                           [&path, &recursionFn, nodeGraphDef](auto info, INode* prev, INode* curr)
                                           {
                                               auto currNodeGraphDef = curr->getNodeGraphDef();
                                               if (currNodeGraphDef)
                                               {
                                                   ExecutionPath newPath{ path, curr }; // may throw
                                                   recursionFn(currNodeGraphDef, newPath, recursionFn);
                                               }

                                               info.continueVisit(curr);
                                           });
        };

        ExecutionPath path;
        traversalFn(m_graph->getNodeGraphDef(), path, traversalFn);
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::getStateInfo_abi
    virtual IExecutionStateInfo* getStateInfo_abi(const ExecutionPath* path, INode* node) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(path);
        return m_storage.getStateInfo(*path, node);
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::getNodeData_abi
    virtual omni::core::Result getNodeData_abi(const ExecutionPath* path,
                                               INode* node,
                                               NodeDataKey key,
                                               omni::core::TypeId* outTypeId,
                                               void** outPtr,
                                               uint64_t* outItemSize,
                                               uint64_t* outBufferSize) noexcept override
    {
        // outTypeId, outItemSize, and outBufferSize should be checked by m_storage
        OMNI_GRAPH_EXEC_ASSERT(path);
        return m_storage.getNodeData(*path, node, key, outTypeId, outPtr, outItemSize, outBufferSize);
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::setNodeData_abi
    virtual void setNodeData_abi(const ExecutionPath* path,
                                 INode* node,
                                 NodeDataKey key,
                                 omni::core::TypeId typeId,
                                 void* data,
                                 uint64_t dataByteCount,
                                 uint64_t dataItemCount,
                                 NodeDataDeleterFn* deleter) noexcept override
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(path);
        m_storage.setNodeData(*path, node, key, typeId, data, dataByteCount, dataItemCount, deleter);
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::applyOnEachDef_abi
    void applyOnEachDef_abi(IDef* def, IApplyOnEachFunction* callback) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(callback);
        m_pathCache.applyOnEach(def, *callback);
    }

    //! @copydoc omni::graph::exec::unstable::IExecutionContext::applyOnEachDefWithName_abi
    void applyOnEachDefWithName_abi(const ConstName* name, IApplyOnEachFunction* callback) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(name);
        OMNI_GRAPH_EXEC_ASSERT(callback);
        m_pathCache.applyOnEach(*name, *callback);
    }

    //! Constructor
    ExecutionContext(IGraph* graph) noexcept
        : m_graph(graph), m_executionStamp(_getNextGlobalExecutionStamp()), m_pathCache(*graph)
    {
    }

    StorageType m_storage; //!< Data store.

private:
    static Stamp _getNextGlobalExecutionStamp() noexcept
    {
        // since this is private, and will only be accessed indirectly via virtual methods, declaring this inline static
        // should be ok
        static Stamp gExecutionStamp;
        gExecutionStamp.next();
        return gExecutionStamp;
    }

    IGraph* m_graph{ nullptr }; //!< Graph associated with this context.
    Stamp m_executionStamp; //!< Execution version incremented with each execution.
    SyncStamp m_initStamp; //!< State initialization version. Synchronized with graph topology.
    detail::ExecutionPathCache m_pathCache; //!< Cache of execution paths for a given definition. Populated lazily and
                                            //!< thread-safe.
    std::unordered_map<std::thread::id, size_t> m_contextThreadIds; //!< Unordered map of thread ids that kickstarted
                                                                    //!< context execution, along with a counter that
                                                                    //!< tracks the number of times that
                                                                    //!< nested/recursive execution has been triggered
                                                                    //!< by those context-starting threads.
    carb::thread::Spinlock m_threadIdSpinlock; //!< Mutex to protect m_contextThreadIds from concurrent write
                                               //!< operations.
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
