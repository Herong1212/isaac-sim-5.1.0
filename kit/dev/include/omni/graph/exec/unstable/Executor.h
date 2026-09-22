// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Executor.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::Executor.
#pragma once

#include <omni/graph/exec/unstable/ExecutionPath.h>
#include <omni/graph/exec/unstable/ExecutionTask.h>
#include <omni/graph/exec/unstable/IExecutionContext.h>
#include <omni/graph/exec/unstable/IExecutor.h>
#include <omni/graph/exec/unstable/INode.h>
#include <omni/graph/exec/unstable/ITopology.h>
#include <omni/graph/exec/unstable/ScheduleFunction.h>
#include <omni/graph/exec/unstable/SchedulingInfo.h>

#include <atomic>
#include <queue>
#include <type_traits>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Basic scheduler which executes the task on calling thread and accumulates the result
struct SerialScheduler
{
    //! Constructor
    SerialScheduler(IExecutionContext* context)
    {
    }

    //! Serial scheduler will emplace the task on serial queue and dispatch one by one after entering process loop
    template <typename Fn>
    Status schedule(Fn&& task, SchedulingInfo)
    {
        m_tasks.emplace(
            [task = captureScheduleFunction(task), this]() mutable
            {
                Status stat = invokeScheduleFunction(task);
                this->m_tasksStatus |= stat;
            });

        return Status::eSuccess;
    }

    //! Enter processing of tasks and return accumulated status
    Status getStatus()
    {
        while (!m_tasks.empty())
        {
            auto& task = m_tasks.front();
            task();
            m_tasks.pop();
        }

        return m_tasksStatus;
    }

private:
    //! Collecting status from all tasks executed by this instance
    Status m_tasksStatus{ Status::eUnknown };

    //! Collect serial tasks in queue to avoid hitting potential stack size limit with the recursive
    //! pattern we had before.
    std::queue<std::function<void()>> m_tasks;
};

//! Data available for executor on every node when traversing the graph.
//!
//! This data does NOT persist from execution to execution. It is written and read by executor during task generation.
//!
//! @note   Can be customized via one of executor template parameters.
struct ExecutionNodeData
{
    std::atomic<std::uint32_t> visitCount{ 0 }; //!< Number of traversal visit to the node.
    std::atomic<bool> hasComputedUpstream{ false }; //!< Propagated value during traversal - has upstream computed.
    std::atomic<bool> hasDeferredUpstream{ false }; //!< Propagated value during traversal - has deferred upstream
                                                    //!< computation.
};

// ef-docs execution-visit-begin
//! Graph traversal visit strategy.
//!
//! Will generate a new task when all upstream nodes have been executed.
struct ExecutionVisit
{
    //! Called when the traversal wants to visit a node.  This method determines what to do with the node (e.g. schedule
    //! it, defer it, etc).
    template <typename ExecutorInfo>
    static Status tryVisit(ExecutorInfo info) noexcept
    {
        auto& nodeData = info.getNodeData();
        if (info.currentTask.getExecutionStatus() == Status::eDeferred)
            nodeData.hasDeferredUpstream = true; // we only set to true...doesn't matter which thread does it first

        std::size_t requiredCount = info.nextNode->getParents().size() - info.nextNode->getCycleParentCount();
        if ((requiredCount == 0) || (++nodeData.visitCount == requiredCount))
        {
            if (!nodeData.hasDeferredUpstream)
            {
                // spawning a task within executor doesn't change the upstream path. just reference the same one.
                ExecutionTask newTask(info.getContext(), info.nextNode, info.getUpstreamPath());
                return info.schedule(std::move(newTask));
            }
            else
                return Status::eDeferred;
        }

        return Status::eUnknown;
    }
};
// ef-docs execution-visit-end

//! Graph traversal visit strategy with dirty cache check.
//!
//! This strategy will generate a new task when all upstream nodes have been visited and:
//!
//! - The node's state requests compute (i.e. the node has been marked as dirty)
//!
//! or:
//!
//! - An upstream node computed
//!
//! If neither of the conditions are true, but all parent nodes have been visited, execution continues (via @ref
//! omni::graph::exec::unstable::IExecutor::continueExecute()).
// ef-docs execution-visit-cache-begin
struct ExecutionVisitWithCacheCheck
{
    //! Called when the traversal wants to visit a node.  This method determines what to do with the node (e.g. schedule
    //! it, defer it, etc).
    template <typename ExecutorInfo>
    static Status tryVisit(ExecutorInfo info) noexcept
    {
        auto& nodeData = info.getNodeData();

        auto triggeringTaskStatus = info.currentTask.getExecutionStatus();
        if (triggeringTaskStatus == Status::eSuccess)
            nodeData.hasComputedUpstream = true; // we only set to true...doesn't matter which thread does it first
        else if (triggeringTaskStatus == Status::eDeferred)
            nodeData.hasDeferredUpstream = true; // we only set to true...doesn't matter which thread does it first

        std::size_t requiredCount = info.nextNode->getParents().size() - info.nextNode->getCycleParentCount();
        if ((requiredCount == 0) || (++nodeData.visitCount == requiredCount))
        {
            if (nodeData.hasDeferredUpstream)
                return Status::eDeferred;
            else
            {
                // spawning a task within executor doesn't change the upstream path. just reference the same one.
                ExecutionTask newTask(info.getContext(), info.nextNode, info.getUpstreamPath());
                if (nodeData.hasComputedUpstream ||
                    info.getContext()->getStateInfo(newTask)->needsCompute(info.getExecutionStamp()))
                    return info.schedule(std::move(newTask));
                else // continue downstream...there may be something dirty. Bypass scheduler to avoid unnecessary
                     // overhead
                    return info.continueExecute(newTask);
            }
        }

        return Status::eUnknown;
    }
};
// ef-docs execution-visit-cache-end

//!   Algorithm to determine how task should be scheduled
struct DefaultSchedulingStrategy
{
    //! Returns the SchedulingInfo (e.g. serial, main thread, etc.) for the given task.
    static SchedulingInfo getSchedulingInfo(const ExecutionTask& task)
    {
        INode* node = task.getNode();
        if (node->getNodeDef())
            return node->getNodeDef()->getSchedulingInfo(task);
        else if (node->getNodeGraphDef())
            return node->getNodeGraphDef()->getSchedulingInfo(task);
        else
            return SchedulingInfo::eSchedulerBypass; // bypass the scheduler since there is nothing to compute
    }
};

//! Easily configurable @ref omni::graph::exec::unstable::IExecutor implementation providing necessary tools for most
//! common executor types.
//!
//! The @ref omni::graph::exec::unstable::Executor class traverses parts of the
//! @rstref{execution graph <ef_execution_graph>}, generating tasks for each node *visited*. One of the core concepts of
//! EF is that *each* @ref omni::graph::exec::unstable::INodeGraphDef *specifies the* @ref
//! omni::graph::exec::unstable::IExecutor *that should be used to execute the subgraph it defines*. This allows each
//! @ref omni::graph::exec::unstable::INodeGraphDef to control a host of strategies for how its subgraph is executed.
//! Some of the strategies are as follows:
//!
//! - *If a node should be scheduled*. For example, the executor may decide to prune parts of the graph based on the
//!   result of a previous execution (i.e. conditional execution). An executor may detect part of the graph does not
//!   need to be computed because a previous execution's results are still valid (i.e. caching). An executor may also
//!   employ strategies such as executing a node once all of its parent have completed or executing the node as soon as
//!   any of the parents have executed.
//!
//! - *How nodes are scheduled*. When an executor visits a node, the executor may choose to execute the computational
//!   logic in the node's definition immediately. Alternatively, it can delegate the execution to a *scheduler*. Working
//!   with the scheduler, an executor is able to provide execution strategies such as:
//!
//!   - Defer execution of the node to a later time.
//!
//!   - Execute the node in parallel with other nodes in the graph.
//!
//!   - Ensure the node is the only node executing at the moment (e.g. "isolated" tasks).
//!
//!   - Execute the node on a specified thread (e.g. the thread that started executing the graph).
//!
//! - *Where nodes are scheduled*. An executor can work with a resource scheduler to determine *where* to execute a
//!   node. This includes deciding the best GPU on a multi-GPU system to execute a GPU node. Likewise, executors can
//!   consult data center aware schedulers to schedule nodes on remote machines.
//!
//! - *The amount of work to be scheduled*. When visiting a node, an executor can create any number of tasks to
//!   accomplish the node's computation. These tasks are able to dynamically create additional work/tasks that the
//!   executor is able to track.
//!
//! Executors and schedulers work together to produce, schedule, and execute tasks on behalf of the node. Executors
//! determine which nodes should be visited and generate appropriate work (i.e. tasks).  Said differently, executor
//! objects "interpret" the graph based on the behavioral logic encapsulated in the executor. Schedulers collect tasks,
//! possibly concurrently from many executor objects, and map the tasks to hardware resources for execution.
//!
//! This @ref omni::graph::exec::unstable::Executor template contains several parameters that allow the user to control
//! the strategies above.
//!
//! <h1><b>Node Type to be Traversed</b></h1>
//!
//! The @p ExecNode parameter defines the interface used to communicate with nodes.  This will usually be @ref
//! omni::graph::exec::unstable::INode or a subclass thereof.
//!
//! <h1><b>Work Generation Strategy</b></h1>
//!
//! @p ExecStrategy defines when/if/what work should be generated when visiting a node.  EF provides several
//! implementations of this strategy:
//!
//! - @ref omni::graph::exec::unstable::ExecutionVisit - Generates work after all parent nodes have been executed.
//!
//! - @ref omni::graph::exec::unstable::ExecutionVisitWithCacheCheck - Generates work after all parents have been
//!   visited *and* either a parent has successfully executed or the node has been explicitly marked for execution (i.e.
//!   dirty).
//!
//! Users are able to define their own execution strategies.  For example OmniGraph defines custom work generation
//! strategies for its various graph types (e.g. pull, push, etc).
//!
//! <h1><b>Transient Execution Data</b></h1>
//!
//! Executing a graph definition may require transient data to implement the executor's work generation strategy. For
//! example, when executing parents in parallel, transient data is needed to atomically count the number of parents that
//! have executed to avoid a node incorrectly executing multiple times.  @p ExecNodeData is a `struct` the user can
//! define to store this transient data.
//!
//! Each node in the graph definition is assigned an @p ExecNodeData.  This transient data type is usually tied to @p
//! ExecStrategy but can also be utilized by the other parameters in this template.
//!
//! EF provides the @ref omni::graph::exec::unstable::ExecutionNodeData struct to work with EF's built-in execution
//! strategies.
//!
//! <h1><b>Scheduler</b></h1>
//!
//! The executors job is to traverse a graph definition, generating appropriate work as nodes are visited.  That work is
//! given to a scheduler, whose job it is to dispatch the work.  The benefit of a scheduler is that it can have a
//! holistic view of the system, across multiple running executors, and efficiently dispatch the work to proper hardware
//! resources.
//!
//! The @p Scheduler parameter defines the scheduler to be used.
//!
//! EF defines the @ref omni::graph::exec::unstable::SerialScheduler which executes task serially.  In practice, more
//! advanced schedulers are available.  For example, *omni.kit.exec.core* defines the @c ParallelSpawner scheduler
//! (based on [Intel's Thread Building Blocks](https://github.com/oneapi-src/oneTBB)) which is able to run tasks in
//! parallel.
//!
//! <h1><b>Scheduling Strategy</b></h1>
//!
//! The @p SchedulingStrategy provides a @ref omni::graph::exec::unstable::SchedulingInfo for each generated task.  @ref
//! omni::graph::exec::unstable::SchedulingInfo is an enum that outlines scheduling constraints for a task (e.g. must be
//! run serially, must run on the thread that started graph execution, etc).
//!
//! EF's @ref omni::graph::exec::unstable::DefaultSchedulingStrategy calls the definitions's @ref
//! omni::graph::exec::unstable::IDef::getSchedulingInfo() to get the definitions's preferred strategy.  However, users
//! may choose to override the definitions's preferred strategy with a custom @c SchedulingStrategy.  For example,
//! forcing all definitions to run serially to ease in debugging the execution graph.
//!
//! <h1><b>Virtual Methods</b></h1>
//!
//! In addition to the template parameters, users may choose to override one of @ref
//! omni::graph::exec::unstable::Executor's virtual methods.  These methods are:
//!
//! - @ref omni::graph::exec::unstable::IExecutor::execute_abi(): This method begins execution of the node provided in
//!   the constructor.  Since this node is usually a root node, this method simply calls @ref
//!   omni::graph::exec::unstable::IExecutor::continueExecute_abi() to execute nodes beyond the root node and calls the
//!   scheduler's @c getStatus() method which is a blocking call that waits for outstanding work to finish.
//!
//! - @ref omni::graph::exec::unstable::IExecutor::continueExecute_abi(): This method is called after each node
//!   executes.  It's job is to continue executing the nodes downstream of the executed node.  By default, this method
//!   uses the work generation strategy (i.e. @c ExecStrategy) on each of the node's children.
//!
//! <h1><b>Miscellaneous</b></h1>
//!
//! The lifetime of an executor is short.  They exist only when executing their owning graph definition.  All transient
//! data stored in @p ExecNodeData is valid only during this lifetime.
//!
//! See @rstref{Execution Concepts <ef_execution_concepts>} for an in-depth guide on how this object is used during
//! execution.
//!
//! See @rstref{Creating an Executor <ef_executor_creation>} for a guide on creating a customize executor for your graph
//! defintion.
template <typename ExecNode,
          typename ExecStrategy,
          typename ExecNodeData,
          typename Scheduler,
          typename SchedulingStrategy,
          typename ExecutorInterface = IExecutor>
class Executor : public Implements<ExecutorInterface>
{
    using Node = const ExecNode;
    using NodeData = ExecNodeData;
    using NodeDataArray = std::vector<NodeData>;
    using ThisExecutor = Executor<ExecNode, ExecStrategy, ExecNodeData, Scheduler, SchedulingStrategy, ExecutorInterface>;
    using ThisExecutorPtr = omni::core::ObjectPtr<ThisExecutor>;

    //! Helper utility to check scheduler dispatch strategy. By default schedulers are not deferred.
    template <typename S, typename Enabled = void>
    struct is_deferred
    {
        static constexpr bool value = false;
    };

    //! Template utility to check scheduler dispatch strategy. Schedulers with scheduleDeferred method are deferred.
    //! Deferred tasks will need to hold a shared pointer to the executor to extend its lifetime past current execution.
    //! This is handled automatically thanks to this helper.
    template <typename S>
    struct is_deferred<
        S,
        std::enable_if_t<std::is_same<Status,
                                      decltype(std::declval<S>().scheduleDeferred(
                                          std::declval<IScheduleFunction*>(), std::declval<SchedulingInfo>()))>::value>>
    {
        static constexpr bool value = true;
    };

public:
    //! Structure passed to the traversal algorithm collecting all necessary data for easy access.
    struct Info
    {
    private:
        Executor* m_executor;

    public:
        const ExecutionTask& currentTask; //!< The node currently being processed.
        INode* nextNode; //!< The node to be visited next.

        //! Constructor.
        Info(Executor* executor, const ExecutionTask& task, INode* next) noexcept
            : m_executor(executor), currentTask(task), nextNode(next)
        {
        }

        //! Returns the @ref Executor defined data for the node.
        NodeData& getNodeData()
        {
            return m_executor->getNodeData(nextNode);
        }

        //! Returns a reference to the owning @ref Executor.
        ThisExecutor* getExecutor()
        {
            return m_executor;
        }

        //! Returns the current context (i.e. @ref IExecutionContext) in which the @ref Executor is executing.
        IExecutionContext* getContext()
        {
            return currentTask.getContext();
        }

        //! Returns the current context's execution stamp/version (i.e. @ref IExecutionContext::getExecutionStamp()).
        Stamp getExecutionStamp()
        {
            return getContext()->getExecutionStamp();
        }

        //! Returns the upstream path of the node that is currently being processed.
        const ExecutionPath& getUpstreamPath() const
        {
            return currentTask.getUpstreamPath();
        }

        //! Schedules the given task.
        Status schedule(ExecutionTask&& newTask)
        {
            return m_executor->scheduleInternal(std::move(newTask));
        }

        //! Returns the given task's SchedulingInfo.
        SchedulingInfo getSchedulingInfo(const ExecutionTask& task) const
        {
            return m_executor->getSchedulingInfo(task);
        }

        //! Returns the @ref Executor's scheduler.
        Scheduler& getScheduler()
        {
            return m_executor->m_scheduler;
        }

        //! Tells the @ref Executor to processes the given task/node's children. This allows it to
        //! generate additional work after the given task has executed.
        Status continueExecute(ExecutionTask& currentTask)
        {
            return m_executor->continueExecute_abi(&currentTask);
        }
    };

    //! Scheduling constraint to use when dispatching given task.
    SchedulingInfo getSchedulingInfo(const ExecutionTask& task) const
    {
        return SchedulingStrategy::getSchedulingInfo(task);
    }

    //! Access custom data associated with each node.
    NodeData& getNodeData(INode* node)
    {
        return m_nodeData[node->getIndexInTopology()];
    }

    //! Execution path to node instantiating graph def associated with this executor.
    const ExecutionPath& getPath() const
    {
        return m_path;
    }

    //! Execution context.
    IExecutionContext* getContext() const
    {
        return m_task.getContext();
    }

    //! Factory method for this executor
    static ThisExecutorPtr create(omni::core::ObjectParam<ITopology> toExecute, const ExecutionTask& thisTask)
    {
        return omni::core::steal(new ThisExecutor(toExecute.get(), thisTask));
    }

protected:
    //! Default constructor is removed
    Executor() = delete;

    //! Constructor used by factory method.
    //!
    //! @param  toExecute   Graph topology used to generate the work.
    //! @param  currentTask Task causing this execution. Used to generate execution path.
    explicit Executor(ITopology* toExecute, const ExecutionTask& currentTask) noexcept
        : m_path((currentTask.getNode() != toExecute->getRoot()) ?
                     ExecutionPath(currentTask.getUpstreamPath(), currentTask.getNode()) :
                     currentTask.getUpstreamPath()),
          m_task(currentTask.getContext(), toExecute->getRoot(), m_path),
          m_nodeData(toExecute->getMaxNodeIndex()),
          m_scheduler(currentTask.getContext())
    {
    }

    // ef-docs executor-execute-begin
    //! Main execution method. Called once by each node instantiating same graph definition.
    Status execute_abi() noexcept override
    {
        // We can bypass all subsequent processing if the node associated with the task starting
        // this execution has no children. Note that we return an eSuccess status because nothing
        // invalid has occurred (e.g., we tried to execute an empty NodeGraphDef); we were asked to
        // compute nothing, and so we computed nothing successfully (no-op)!
        if (m_task.getNode()->getChildren().empty())
        {
            return Status::eSuccess | m_task.getExecutionStatus();
        }

        (void)continueExecute_abi(&m_task);

        // Give a chance for the scheduler to complete the execution of potentially parallel work which should complete
        // within current execution. All background tasks will continue pass this point.

        // Scheduler is responsible for collecting the execution status for everything that this executor generated.
        return m_scheduler.getStatus() | m_schedulerBypass;
    }
    // ef-docs executor-execute-end

    // ef-docs executor-continue-execute-begin
    //! Implementation of the base class method to generate additional work after the given task has executed but
    //! before it has completed.
    Status continueExecute_abi(ExecutionTask* currentTask) noexcept override
    {
        OMNI_GRAPH_EXEC_ASSERT(currentTask);

        if (currentTask->getNode()->getChildren().empty())
        {
            return Status::eSuccess | currentTask->getExecutionStatus();
        }

        Status ret = Status::eUnknown;
        for (auto child : currentTask->getNode()->getChildren())
        {
            ret |= ExecStrategy::tryVisit(Info(this, *currentTask, child));
        }

        return ret | currentTask->getExecutionStatus();
    }
    // ef-docs executor-continue-execute-end

    //! Implementation of base class schedule method available for work generation outside of traversal loop.
    Status schedule_abi(IScheduleFunction* fn, SchedulingInfo schedInfo) noexcept override
    {
        OMNI_GRAPH_EXEC_FATAL_UNLESS_ARG(fn);
        return scheduleExternal(fn, schedInfo);
    }

    //! Scheduling spawner of a task generated by traversal implementation
    template <typename S = Scheduler>
    Status scheduleInternal(ExecutionTask&& newTask, typename std::enable_if_t<!is_deferred<S>::value>* = nullptr)
    {
        // ef-docs executor-schedule-internal-begin
        Status ret = Status::eUnknown;
        SchedulingInfo schedInfo = getSchedulingInfo(newTask);
        if (schedInfo != SchedulingInfo::eSchedulerBypass)
        {
            // this task will finish before we exit executor...just capture as reference to avoid unnecessary cost
            ret = m_scheduler.schedule([executor = this, task = std::move(newTask)]() mutable -> Status
                                       { return task.execute(executor); },
                                       schedInfo);
        }
        else // bypass the scheduler...no need for extra scheduling overhead
        {
            m_schedulerBypass |= newTask.execute(this);
        }

        return ret;
        // ef-docs executor-schedule-internal-end
    }

    //! Deferred scheduling spawner of a task generated by traversal implementation
    template <typename S = Scheduler>
    Status scheduleInternal(ExecutionTask&& newTask, typename std::enable_if_t<is_deferred<S>::value>* = nullptr)
    {
        // ef-docs executor-schedule-deferred-begin
        SchedulingInfo schedInfo = getSchedulingInfo(newTask);
        // for deferred tasks, we capture executor as a shared_ptr (extra cost, but keeps object alive)
        Status ret = m_scheduler.scheduleDeferred(
            [executor = omni::core::borrow(this), task = std::move(newTask)]() mutable -> Status
            { return task.execute(executor); },
            schedInfo);

        return ret;
        // ef-docs executor-schedule-deferred-end
    }

    //! Scheduling spawner of a task generated by currently running task
    template <typename S = Scheduler>
    Status scheduleExternal(IScheduleFunction* fn,
                            SchedulingInfo schedInfo,
                            typename std::enable_if_t<!is_deferred<S>::value>* = nullptr)
    {
        if (schedInfo != SchedulingInfo::eSchedulerBypass)
        {
            return m_scheduler.schedule(fn, schedInfo);
        }
        else // bypass the scheduler...no need for extra scheduling overhead
        {
            return fn->invoke();
        }
    }

    //! Deferred scheduling spawner of a task generated by currently running task
    template <typename S = Scheduler>
    Status scheduleExternal(IScheduleFunction* fn,
                            SchedulingInfo schedInfo,
                            typename std::enable_if_t<is_deferred<S>::value>* = nullptr)
    {
        return m_scheduler.scheduleDeferred(fn, schedInfo);
    }

    ExecutionPath m_path; //!< Execution path helping discover state associated with current instance of the graph.
    ExecutionTask m_task; //!< Task starting the execution
    NodeDataArray m_nodeData; //!< Storage for per node custom data
    Scheduler m_scheduler; //!< An interface for spawning tasks for dispatch by scheduler and waiting for completion.
    Status m_schedulerBypass{ Status::eUnknown }; //!< Execution status for tasks bypassing scheduler.
};

//! Default executor used by all node graph definitions that don't explicitly pass the executor factory method.
using ExecutorFallback = Executor<INode, ExecutionVisit, ExecutionNodeData, SerialScheduler, DefaultSchedulingStrategy>;

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
