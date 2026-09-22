// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file TbbSchedulerState.h
//!
//! @brief Defines @ref omni::kit::exec::core::unstable::TbbSchedulerState.
#pragma once

#include <carb/container/LocklessStack.h>

#include <tbb/enumerable_thread_specific.h>
#include <tbb/recursive_mutex.h>
CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wattributes")
#include <tbb/task.h>
CARB_IGNOREWARNING_GNUC_POP

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

//! Implementation details for the TBB based task scheduler state singleton.
//!
//! Will be replaced.
struct TbbSchedulerState
{
    //! A base struct from which all scheduled tasks need to derive from in order to be compatible with
    //! TbbSchedulerState, which uses an intrusive concurrent stack data container for storing said tasks.
    struct TaskStackEntry : public tbb::task
    {
        carb::container::LocklessStackLink<TaskStackEntry> m_link;
    };

    carb::container::LocklessStack<TaskStackEntry, &TaskStackEntry::m_link> stackParallel; //!< Stack of parallel tasks.
                                                                                           //!< Allows concurrent
                                                                                           //!< insertion.
    carb::container::LocklessStack<TaskStackEntry, &TaskStackEntry::m_link> stackSerial; //!< Stack of serial tasks.
                                                                                         //!< Allows concurrent
                                                                                         //!< insertion.
    carb::container::LocklessStack<TaskStackEntry, &TaskStackEntry::m_link> stackIsolate; //!< Stack of isolate tasks.
                                                                                          //!< Allows concurrent
                                                                                          //!< insertion.

    std::atomic<int> totalTasksInFlight{ 0 }; //!< Track total number of serial and parallel tasks. Used for isolation.
    tbb::enumerable_thread_specific<int> tasksExecutingPerThread{ 0 }; //!< Track execution per thread to know if
                                                                       //!< waiting on a task contributed to a total
                                                                       //!< tasks in flight.

    std::atomic<std::thread::id> serialThreadId; //!< Thread currently processing serial tasks.
    std::atomic<std::thread::id> isolateThreadId; //!< Thread currently processing isolate tasks.

    tbb::recursive_mutex executingThreadMutex; //!< Mutex used to serialize the processing of all context-kickstarting
                                               //!< threads (i.e., all threads which kickstarted execution from any
                                               //!< given ExecutionContexts). This ensures that up to a single
                                               //!< kickstarter thread is computing at any given moment, regardless of
                                               //!< the number of threads that triggered execution from a given context
                                               //!< OR the number of different ExecutionContexts that began executing
                                               //!< concurrently (assuming that the user is utilizing the provided
                                               //!< ParallelScheduler for those contexts, otherwise they will need to
                                               //!< manage the synchronization on their own), which is important because
                                               //!< serial and isolate tasks are scheduled to run on a
                                               //!< context-kickstarter thread, so allowing multiple such threads to
                                               //!< evaluate concurrently would break the promise that serial and
                                               //!< isolate tasks cannot be executed in multiple threads simultaneously.
};

} // namespace unstable
} // namespace core
} // namespace exec
} // namespace kit
} // namespace omni
