// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ParallelScheduler.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::ParallelSpawner.
#pragma once

#include <omni/graph/exec/unstable/AtomicBackoff.h>
#include <omni/kit/exec/core/unstable/ITbbSchedulerState.h>
#include <omni/kit/exec/core/unstable/TbbSchedulerState.h>

#include <atomic>
#include <cstddef>
#include <mutex>
#include <thread>
#include <type_traits>

#ifndef __TBB_ALLOW_MUTABLE_FUNCTORS
//! Allow task functors to mutate captured by value state
#    define __TBB_ALLOW_MUTABLE_FUNCTORS 1
#endif

#include <tbb/task.h>
#include <tbb/task_group.h>

#include <atomic>
#include <thread>

namespace omni
{
namespace kit
{
namespace exec
{
namespace core
{
namespace unstable
{
namespace detail
{

class ParallelSchedulerDebugger;

} // namespace detail

#ifndef DOXYGEN_BUILD

//! Parallel scheduler for task dispatch.
//!
//! Currently only needs to handle special requests, actual parallel work is enqueue directly to TBB
class ParallelScheduler
{
public:
    //! Access static per-DLL singleton.
    static ParallelScheduler& getSingleton()
    {
        // this static is per-DLL, but the actual private data (s_state) is shared across DLLs
        static ParallelScheduler sScheduler;
        return sScheduler;
    }

    //! Class wrapping lambda into serial and parallel tasks. Additionally, this class keeps a track of all
    //! created tasks to allow activating isolation pass when all serial and parallel work is completed.
    template <typename Fn>
    class TaskBody : public TbbSchedulerState::TaskStackEntry
    {
    public:
        //! Expected function signature is void(). Increments total task count.
        TaskBody(Fn&& f) : m_fn(std::forward<Fn>(f)), m_sharedState(ParallelScheduler::getSingleton().s_state)
        {
            ++m_sharedState->totalTasksInFlight;
        }
        //! Decrements total task count and starts processing isolate tasks if no more tasks are running.
        ~TaskBody()
        {
            --m_sharedState->totalTasksInFlight;
        }

        //! TBB task execute method calling into lambda. To track nested executions, we increment and decrement
        //! tasks per thread atomic counter.
        task* execute() override
        {
            struct ExecutingCountedTaskScope
            {
                ExecutingCountedTaskScope(tbb::enumerable_thread_specific<int>& executingPerThread)
                    : _executingPerThread(executingPerThread)
                {
                    _executingPerThread.local()++;
                }
                ~ExecutingCountedTaskScope()
                {
                    _executingPerThread.local()--;
                    OMNI_KIT_EXEC_RECORD_TASK_EXECUTED();
                }

                tbb::enumerable_thread_specific<int>& _executingPerThread;
            } executingScope(m_sharedState->tasksExecutingPerThread);

            return m_fn(); // Allow for potential continuation.
        };

    private:
        Fn m_fn; //!< Lambda function to call from the execute() function.
        TbbSchedulerState* m_sharedState{ nullptr }; //!< Scheduler shared state used to track total task count.
    };

    //! Class wrapping lambda into an isolated TBB task. No other tasks will be running when this task executes.
    template <typename Fn>
    class IsolateTaskBody : public TbbSchedulerState::TaskStackEntry
    {
    public:
        //! Constructor capturing the lambda function
        //!
        //! Expected function signature is void()
        IsolateTaskBody(Fn&& f) : m_fn(std::forward<Fn>(f))
        {
        }

        //! TBB task execute method calling into lambda.
        task* execute() override
        {
            // Isolate tasks are not counted in total in flight tasks to allow us detect when
            // all other work is finished. Once we are entering scope of isolate task, we make sure
            // PauseTaskScope doesn't consider this task as taking part in totalTasksInFlight.
            struct ExecutingNotCountedTaskScope
            {
                ExecutingNotCountedTaskScope(tbb::enumerable_thread_specific<int>& executingPerThread)
                    : _executingPerThread(executingPerThread)
                {
                    auto& perThreadCount = _executingPerThread.local();
                    _originalPerThread = perThreadCount;
                    perThreadCount = 0;
                }
                ~ExecutingNotCountedTaskScope()
                {
                    _executingPerThread.local() = _originalPerThread;
                    OMNI_KIT_EXEC_RECORD_TASK_EXECUTED();
                }

                tbb::enumerable_thread_specific<int>& _executingPerThread;
                int _originalPerThread;
            } executingScope(ParallelScheduler::getSingleton().s_state->tasksExecutingPerThread);

            return m_fn(); // Allow for potential continuation.
        };

    private:
        Fn m_fn; //!< Lambda function to call from the execute() function.
    };

    //! RAII class used to pause and resume total tasks in flight when thread is about to pick up new tasks to work on.
    class PauseTaskScope
    {
    public:
        PauseTaskScope()
            : m_scheduler(ParallelScheduler::getSingleton()),
              m_isCountedTask(m_scheduler.s_state->tasksExecutingPerThread.local() > 0)
        {
            if (m_isCountedTask)
            {
                --m_scheduler.s_state->totalTasksInFlight;
            }
        }
        ~PauseTaskScope()
        {
            if (m_isCountedTask)
            {
                ++m_scheduler.s_state->totalTasksInFlight;
            }
        }

    private:
        ParallelScheduler& m_scheduler; //!< To avoid calling into getSingleton multiple times.
        const bool m_isCountedTask; //!< Know if we are pausing task that was scheduled by us or someone else.
    };

    //! Typically parallel tasks are spawned right away, but when executed from isolation tasks, we defer spawning
    //! until all isolation work is completed.
    void pushParallelTask(TbbSchedulerState::TaskStackEntry& t, bool isExecutingThread)
    {
        if (!isProcessingIsolate())
        {
            if (isExecutingThread && (s_state->totalTasksInFlight < 2))
            {
                // Record that a task has been enqueued
                OMNI_KIT_EXEC_RECORD_TASK_ENQUEUED();

                // Context execution-invoking threads never joins the arena, so won't process its local queue. Add the
                // task to the global queue. We only do this if there aren't already tasks in flight that can pick up
                // task if we spawn() it.
                tbb::task::enqueue(t);
            }
            else
            {
                // Record that a task has been spawned
                OMNI_KIT_EXEC_RECORD_TASK_SPAWNED();
                tbb::task::spawn(t); // add to local queue
            }
        }
        else
        {
            // Record that a parallel task has been pushed to queue
            OMNI_KIT_EXEC_RECORD_PUSHED_PARALLEL_TASK();
            s_state->stackParallel.push(&t);
        }
    }

    //! Add task /p t for serial dispatch. These tasks are guaranteed to be run one after another, but other thread-safe
    //! tasks are allowed to run together with them.
    void pushSerialTask(TbbSchedulerState::TaskStackEntry& t)
    {
        // Record that a serial task has been pushed to queue
        OMNI_KIT_EXEC_RECORD_PUSHED_SERIAL_TASK();
        s_state->stackSerial.push(&t);
    }

    //! Store isolate task for execution when no other tasks are running.
    void pushIsolateTask(TbbSchedulerState::TaskStackEntry& t)
    {
        // Record that an isolate task has been pushed to queue
        OMNI_KIT_EXEC_RECORD_PUSHED_ISOLATE_TASK();
        s_state->stackIsolate.push(&t);
    }

    //! Returns true if calling thread has been tagged as the one processing serial task. If so, this thread
    //! is in the middle of processing a serial task.
    bool isWithinSerialTask() const
    {
        return (s_state->serialThreadId.load() == std::this_thread::get_id());
    }

    //! Returns true if calling thread has been tagged as the one processing isolate task. If so, this thread
    //! is in the middle of processing an isolate task.
    bool isWithinIsolateTask() const
    {
        return (s_state->isolateThreadId.load() == std::this_thread::get_id());
    }

    //! Returns true if processing of isolate tasks is in progress.
    bool isProcessingIsolate() const
    {
        return (s_state->isolateThreadId.load() != std::thread::id());
    }

    void processContextThread(tbb::empty_task* const rootTask)
    {
        // See the note in TbbSchedulerState.h as to why we need this
        // mutex lock here.
        std::unique_lock<tbb::recursive_mutex> uniqueLock(s_state->executingThreadMutex);

        graph::exec::unstable::AtomicBackoff backoff;

        if (isWithinIsolateTask())
        {
            while (rootTask->ref_count() > 1)
            {
                if (processQueuedTasks(rootTask))
                    backoff.reset();
                else
                    backoff.pause();

                // Check and log metrics periodically
                OMNI_KIT_EXEC_CHECK_AND_LOG_METRICS();
            }
        }
        else
        {
            while (rootTask->ref_count() > 1)
            {
                if (processSerialTasks() || processIsolateTasks())
                    backoff.reset();
                else
                    backoff.pause();

                // Check and log metrics periodically
                OMNI_KIT_EXEC_CHECK_AND_LOG_METRICS();
            }
        }
    }

private:
    //! Explicit call to execute the serial task stackSerial until empty.
    //!
    bool processSerialTasks()
    {
        tbb::task* task = s_state->stackSerial.pop();

        // No work.
        if (!task)
        {
            return false;
        }

        {
            // Acquire the thread that's supposed to be handling serial task evaluation. Note
            // that this thread can be derived from many different execution contexts kickstarted
            // by multiple different threads.
            std::thread::id currentThreadId = std::this_thread::get_id();
            std::thread::id originalThreadId;
            if (!s_state->serialThreadId.compare_exchange_strong(originalThreadId, currentThreadId) &&
                originalThreadId != currentThreadId)
            {
                return false;
            }

            // Once serial tasks evaluation is complete, we will want to restore the serial thread ID
            // back to its default value; employ an RAII helper to do so.
            struct ScopeRelease
            {
                std::thread::id _originalThreadId;
                std::atomic<std::thread::id>& _serialThreadId;
                ~ScopeRelease()
                {
                    _serialThreadId = _originalThreadId;
                }
            } threadScope = { originalThreadId, s_state->serialThreadId };

            // Run the loop over tasks. We are responsible here to delete the task since it is consumed outside of TBB.
            do
            {
                (void)task->execute();
                tbb::task::destroy(*task);
            } while ((task = s_state->stackSerial.pop()));
        }

        // Let the caller know that we had something to do
        return true;
    }

    //! When no more work is available execute isolated tasks.
    bool processIsolateTasks()
    {
        if (s_state->totalTasksInFlight > 0 || s_state->stackIsolate.isEmpty())
        {
            return false;
        }

        // Try to acquire the right to process isolated tasks. Need to support nested executions.
        {
            std::thread::id currentThreadId = std::this_thread::get_id();
            std::thread::id originalThreadId;
            if (!s_state->isolateThreadId.compare_exchange_strong(originalThreadId, currentThreadId) &&
                originalThreadId != currentThreadId)
            {
                return false;
            }

            // We acquired the thread, nothing else will be running until the end of this scope.
            struct ScopeRelease
            {
                std::thread::id _originalThreadId;
                std::atomic<std::thread::id>& _isolateThreadId;
                ~ScopeRelease()
                {
                    _isolateThreadId = _originalThreadId;
                }
            } threadScope = { originalThreadId, s_state->isolateThreadId };

            // Run the loop over tasks. We are responsible here to delete the task since it is consumed outside of TBB.
            while (tbb::task* task = s_state->stackIsolate.pop())
            {
                (void)task->execute();
                tbb::task::destroy(*task);
            }

            // Here we will release this thread from processing isolate tasks.
            // We don't worry about synchronization between push tasks and this operation because
            // all push call can only happen from within above loop (indirectly via execute). There is no
            // other concurrent execution happening when we are in here.
        }

        // Do NOT start parallel work in nested isolate task; it has to be all consumed on this thread until we can
        // exit isolation.
        if (!isWithinIsolateTask())
        {
            // Restart parallel task execution.
            while (tbb::task* dispatchTask = s_state->stackParallel.pop())
            {
                if (s_state->totalTasksInFlight < 2)
                {
                    tbb::task::enqueue(*dispatchTask);
                }
                else
                {
                    tbb::task::spawn(*dispatchTask);
                }
            }
        }

        return true;
    }

    //! This processing should be avoided as much as possible but is necessary when work is generated and executed
    //! from within isolate task. Note that we prevent task execute continuation if a given task was originally
    //! enqueued by a different ParallelSpawner instance (determined by comparing root tasks, which are different
    //! across ParallelSpawner objects), since such behavior tends to produces deep recursive callstacks that can
    //! easily lead to stack overflows if too many tasks are present in the execution graph. Instead, processQueuedTasks
    //! will only execute tasks that are directly associated with the current NodeGraphDef that's being evaluated - all
    //! other tasks will eventually have their execution triggered by their corresponding ParallelSpawner instances that
    //! originally scheduled them; this avoids the aforementioned recursive call pattern that could lead to stack
    //! overflows, even if the number of enqueued tasks is quite large.
    bool processQueuedTasks(tbb::empty_task* const rootTask)
    {
        OMNI_ASSERT(isWithinIsolateTask());

        // First attempt to only process the first task in each scheduling-type stack. In most cases this is enough to
        // allow for subsequent execution to occur.
        bool ret = processTaskStackTop(s_state->stackIsolate, rootTask) ||
                   processTaskStackTop(s_state->stackParallel, rootTask) ||
                   processTaskStackTop(s_state->stackSerial, rootTask);

        // If no tasks have been processed yet because the top task in each stack belongs to a different ParallelSpawner
        // instance than the one currently running (i.e., not because all of the task stacks are empty), perform more
        // intensive task processing by looping through each stack to find at least one task that's been enqueued by
        // the current ParallelSpanwer/Executor. This situation has not been observed thus far in any cases where only
        // a single ExecutionGraph is present in the runtime (as is the case in kit at the moment, and even if there are
        // multiple contexts associated with it for evaluation, which is exercised in the unit tests), and only seems to
        // happen occasionally (~5% of the time) in a couple of unit tests (specifically ones that either contain very
        // large execution graphs or multiple different execution graphs that are evaluated across multiple threads
        // simultaneously, and even those cases seem to only manifest in Linux, or at least have not been observed in
        // Windows so far). The relative rarity with which this scenario is encountered, combined with the fact that the
        // aforementioned looping logic does add some extra overhead to potentially hot code-paths, is why we've broken
        // the below section out into its own scope.
        if (!ret &&
            (!s_state->stackIsolate.isEmpty() || !s_state->stackParallel.isEmpty() || !s_state->stackSerial.isEmpty()))
        {
            ret = processTaskStack(s_state->stackIsolate, rootTask) ||
                  processTaskStack(s_state->stackParallel, rootTask) || processTaskStack(s_state->stackSerial, rootTask);
        }

        return ret;
    }

    // Helper method that will execute and clean up the top task in the specified stack if said task was originally
    // inserted by the current ParallelSpawner instance.
    const bool processTaskStackTop(carb::container::LocklessStack<TbbSchedulerState::TaskStackEntry,
                                                                  &TbbSchedulerState::TaskStackEntry::m_link>& taskStack,
                                   tbb::empty_task* const rootTask) noexcept
    {
        if (TbbSchedulerState::TaskStackEntry* const task = taskStack.pop())
        {
            if (task->parent() == rootTask) // Prevent task execute continuation if the current task
                                            // belongs to a different ParallelSpawner instance.
            {
                (void)task->execute();
                tbb::task::destroy(*task); // We are responsible here to delete the task since it is consumed manually.
                return true;
            }
            else
            {
                taskStack.push(task); // Add the task back to the stack without processing it.
            }
        }

        return false;
    }

    // Helper method that will execute and clean up the first task it finds in the specified stack that was originally
    // inserted by the current ParallelSpawner instance.
    const bool processTaskStack(carb::container::LocklessStack<TbbSchedulerState::TaskStackEntry,
                                                               &TbbSchedulerState::TaskStackEntry::m_link>& taskStack,
                                tbb::empty_task* const rootTask) noexcept
    {
        if (!taskStack.isEmpty())
        {
            TbbSchedulerState::TaskStackEntry* taskToExecute = nullptr;
            carb::container::LocklessStack<TbbSchedulerState::TaskStackEntry, &TbbSchedulerState::TaskStackEntry::m_link> tempStack;
            while (TbbSchedulerState::TaskStackEntry* const task = taskStack.pop())
            {
                if (task->parent() == rootTask)
                {
                    taskToExecute = task;
                    break;
                }
                tempStack.push(task);
            }

            while (TbbSchedulerState::TaskStackEntry* const task = tempStack.pop())
            {
                taskStack.push(task);
            }

            if (taskToExecute)
            {
                (void)taskToExecute->execute();
                tbb::task::destroy(*taskToExecute); // We are responsible here to delete the task since it is consumed
                                                    // manually.
                return true;
            }
        }

        return false;
    }

    //! Constructor.
    explicit ParallelScheduler() noexcept
    {
        omni::core::ObjectPtr<ITbbSchedulerState> sInterface = omni::core::createType<ITbbSchedulerState>();
        OMNI_ASSERT(sInterface);
        s_state = sInterface->getState();
        OMNI_ASSERT(s_state);
    }

    TbbSchedulerState* s_state; //!< One scheduler state shared by all DLLs.
    friend class detail::ParallelSchedulerDebugger; //!< Friend class that exposes some of ParallelScheduler's internals
                                                    //!< for debugging and testing purposes.
};

namespace detail
{

//! Utility class that exposes some of ParallelScheduler's internals for debugging and testing purposes.
class ParallelSchedulerDebugger
{
public:
    //! Returns the total number of enqueued isolate tasks. Not threadsafe.
    static const size_t enqueuedIsolateTasksUnsafeCount()
    {
        ParallelScheduler& scheduler = ParallelScheduler::getSingleton();

        // First obtain the total number of enqueued isolate tasks by emptying the stack and counting all
        // popped tasks; store said tasks in a temporary container.
        std::size_t count = 0;
        carb::container::LocklessStack<TbbSchedulerState::TaskStackEntry, &TbbSchedulerState::TaskStackEntry::m_link> tempStack;
        while (auto task = scheduler.s_state->stackIsolate.pop())
        {
            ++count;
            tempStack.push(task);
        }

        // Refill the isolate tasks stack.
        while (auto task = tempStack.pop())
        {
            scheduler.s_state->stackIsolate.push(task);
        }

        return count;
    }

    //! Returns the total number of enqueued parallel tasks. Not threadsafe.
    static const size_t enqueuedParallelTasksUnsafeCount()
    {
        ParallelScheduler& scheduler = ParallelScheduler::getSingleton();

        // First obtain the total number of enqueued parallel tasks by emptying the stack and counting all
        // popped tasks; store said tasks in a temporary container.
        std::size_t count = 0;
        carb::container::LocklessStack<TbbSchedulerState::TaskStackEntry, &TbbSchedulerState::TaskStackEntry::m_link> tempStack;
        while (auto task = scheduler.s_state->stackParallel.pop())
        {
            ++count;
            tempStack.push(task);
        }

        // Refill the parallel tasks stack.
        while (auto task = tempStack.pop())
        {
            scheduler.s_state->stackParallel.push(task);
        }

        return count;
    }

    //! Returns the total number of enqueued serial tasks. Not threadsafe.
    static const size_t enqueuedSerialTasksUnsafeCount()
    {
        ParallelScheduler& scheduler = ParallelScheduler::getSingleton();

        // First obtain the total number of enqueued serial tasks by emptying the stack and counting all
        // popped tasks; store said tasks in a temporary container.
        std::size_t count = 0;
        carb::container::LocklessStack<TbbSchedulerState::TaskStackEntry, &TbbSchedulerState::TaskStackEntry::m_link> tempStack;
        while (auto task = scheduler.s_state->stackSerial.pop())
        {
            ++count;
            tempStack.push(task);
        }

        // Refill the serial tasks stack.
        while (auto task = tempStack.pop())
        {
            scheduler.s_state->stackSerial.push(task);
        }

        return count;
    }
};

//! Utility to construct in-place /p allocTask a task /p TaskT wrapping given lambda /p f
template <template <class...> typename TaskT, typename A, typename Fn>
TaskT<Fn>* makeTask(A&& allocTask, Fn&& f)
{
    return new (allocTask) TaskT<Fn>(std::forward<Fn>(f));
}

} // namespace detail

#endif // DOXYGEN_BUILD

//! Interface executors use to talk to the scheduler. Every executor object that wishes to use the ParallelScheduler
//! (which is a singleton) will have its own associated instance of ParallelSpawner.
struct ParallelSpawner
{
    //! Constructor.
    ParallelSpawner(graph::exec::unstable::IExecutionContext* context)
        : m_context(context), m_scheduler(ParallelScheduler::getSingleton())
    {
        m_root = new (tbb::task::allocate_root()) tbb::empty_task;
        m_root->set_ref_count(1);
    }

    //! Destructor.
    ~ParallelSpawner()
    {
        tbb::task::destroy(*m_root);
    }

    //! Thread-safe schedule method called by executor to enqueue generated work.
    //! Supports parallel, serial and isolate scheduling constraints.
    template <typename Fn>
    graph::exec::unstable::Status schedule(Fn&& task, graph::exec::unstable::SchedulingInfo schedInfo)
    {
        using namespace detail;

        if (schedInfo == graph::exec::unstable::SchedulingInfo::eParallel)
        {
            auto* dispatchTask = detail::makeTask<ParallelScheduler::TaskBody>(
                tbb::task::allocate_additional_child_of(*m_root),
                [task = graph::exec::unstable::captureScheduleFunction(task), this]() mutable
                {
                    graph::exec::unstable::Status ret = graph::exec::unstable::invokeScheduleFunction(task);
                    this->accumulateStatus(ret);

                    return nullptr;
                });

            m_scheduler.pushParallelTask(*dispatchTask, m_context->isExecutingThread());
        }
        else if (schedInfo == graph::exec::unstable::SchedulingInfo::eIsolate)
        {
            auto* dispatchTask = detail::makeTask<ParallelScheduler::IsolateTaskBody>(
                tbb::task::allocate_additional_child_of(*m_root),
                [task = graph::exec::unstable::captureScheduleFunction(task), this]() mutable
                {
                    graph::exec::unstable::Status ret = graph::exec::unstable::invokeScheduleFunction(task);
                    this->accumulateStatus(ret);

                    return nullptr;
                });

            m_scheduler.pushIsolateTask(*dispatchTask);
        }
        else
        {
            auto* dispatchTask = detail::makeTask<ParallelScheduler::TaskBody>(
                tbb::task::allocate_additional_child_of(*m_root),
                [task = graph::exec::unstable::captureScheduleFunction(task), this]() mutable -> tbb::task*
                {
                    graph::exec::unstable::Status ret = graph::exec::unstable::invokeScheduleFunction(task);
                    this->accumulateStatus(ret);

                    return nullptr;
                });

            m_scheduler.pushSerialTask(*dispatchTask);
        }

        return graph::exec::unstable::Status::eSuccess;
    }

    //! Thread-safe accumulation of status returned by all spawned tasks.
    void accumulateStatus(graph::exec::unstable::Status ret)
    {
        graph::exec::unstable::Status current, newValue = graph::exec::unstable::Status::eUnknown;
        do
        {
            current = m_status.load();
            newValue = ret | current;
        } while (!m_status.compare_exchange_weak(current, newValue));
    }

    //! Blocking call to acquire accumulated status.
    //! When more work is still available, this thread will join the arena and pickup some work OR
    //! will be reserved to process serial tasks if we end up here from a serial task (nested scenario).
    graph::exec::unstable::Status getStatus()
    {
        // We are about to enter nested execution. This has an effect on total tasks in flight, i.e.
        // we will suspend the current task by reducing the counters. All that is done by RAII class below.
        ParallelScheduler::PauseTaskScope pauseTask;

        // Note that in situations where multiple different contexts are running from multiple different
        // threads, just having the first check (m_context->isExecutingThread()) won't be enough because
        // we may be attempting to get the status of a serial/isolate task that was originally created in
        // context A running on thread 1 while context B running on thread 2 is being processed in the
        // below check; this can occur if context A/thread 1 was temporarily suspended in the past after
        // context B/thread 2 beat it to acquiring the s_state->executingThreadMutex, meaning that we
        // are currently processing nested tasks (which can be of any scheduling type) that are derived
        // from some top-level set of serial/isolate tasks in context B. In such situations, we need to
        // additionally check if we are currently within a serial or isolate task scope, since otherwise
        // the task originally created in context A/thread 1 will incorrectly skip processing on context B's
        // running kickstarter thread, despite thread 2 being the only such evaluating kickstarter thread at
        // the moment, and take a different code-path that leads to hangs. Serial/isolate tasks don't need to
        // be run exclusively on the context-kickstarting thread from which they were eventually scheduled -
        // they can be run on any such thread type as long as that thread is the only one running/processing
        // serial/isolate tasks.
        if (m_context->isExecutingThread() || m_scheduler.isWithinSerialTask() || m_scheduler.isWithinIsolateTask())
        {
            m_scheduler.processContextThread(m_root);
        }
        else
        {
            if (m_root->ref_count() > 1)
            {
                m_root->wait_for_all();
                m_root->set_ref_count(1);
            }
        }

        return m_status;
    }

protected:
    graph::exec::unstable::IExecutionContext* m_context; //!< Execution context used to identify kickstarting threads
                                                         //!< for the scheduling of serial and isolate tasks.
    tbb::empty_task* m_root{ nullptr }; //!< Root task for all spawned tasks.
    std::atomic<graph::exec::unstable::Status> m_status{ graph::exec::unstable::Status::eUnknown }; //!< Accumulated
                                                                                                    //!< status.
    ParallelScheduler& m_scheduler; //!< To avoid calling into getSingleton multiple times.
};

} // namespace unable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni
