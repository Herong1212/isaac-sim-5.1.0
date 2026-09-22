// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file RaceConditionFinder.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::RaceConditionFinder.
#pragma once

#include <carb/Defines.h>

#include <atomic>
#include <thread>

#if CARB_PLATFORM_WINDOWS
#else
#    include <signal.h>
#endif

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Helper class for detecting race conditions.
//!
//! This type of a "fake lock" has been known under many names. The goal is to create a "critical section"
//! without enforcing synchronization. If more than one thread falls into this "critical section" it means
//! we haven't managed (at the orchestration level) guarantee sequential execution of particular code.
//!
//! The RC finder is used very similar to a lock, i.e. you allocate a shared RC finder and enter
//! the "critical section" using Scope RAII object. When more than one thread enters this section,
//! we will make them spin forever and issue a debug break from the first thread that started the section.
//! This allows to catch all the threads and easily debug by seeing all the callstacks and states.
//!
//! RC finder supports recursive execution.
//!
//! This is a debugging object and shouldn't be used in released product. Without debugged attached, application will
//! simply crash. As a result, we don't include it as part of any .cpp code coverage reports.
class RaceConditionFinder
{
public:
    //! Create scope around the fake "critical section".
    class Scope
    {
    public:
        //! Construct the scope with a valid shared finder.
        Scope(RaceConditionFinder& finder)
            : m_sharedFinder(finder),
              m_thisThreadId(std::this_thread::get_id()),
              m_originalThreadId(m_sharedFinder.m_currentThread)
        {
            // handle recursive code paths
            bool acquiredSuccessfully = (m_originalThreadId == m_thisThreadId);
            if (!acquiredSuccessfully)
            {
                std::thread::id emptyId;
                acquiredSuccessfully = m_sharedFinder.m_currentThread.compare_exchange_strong(emptyId, m_thisThreadId);
            }

            // infinite loop in here and let the other thread complete and issue debugger break in the destructor
            if (!acquiredSuccessfully)
            {
                m_sharedFinder.m_raceDetected = true;
                while (true)
                {
                    std::this_thread::yield();
                }
            }
        }
        //! Issue a breakpoint if race condition is detected, otherwise release the section.
        ~Scope()
        {
            if (m_sharedFinder.m_raceDetected)
            {
#if CARB_PLATFORM_WINDOWS
                __debugbreak();
#else
                raise(SIGTRAP);
#endif
            }
            else
            {
                bool resetSuccessfully =
                    m_sharedFinder.m_currentThread.compare_exchange_strong(m_thisThreadId, m_originalThreadId);
                // this shouldn't be possible
                if (!resetSuccessfully)
                {
                    m_sharedFinder.m_raceDetected = true;
                    while (true)
                    {
                        std::this_thread::yield();
                    }
                }
            }
        }

    private:
        RaceConditionFinder& m_sharedFinder; //!< Shared finder object used to communicate state across threads
        std::thread::id m_thisThreadId; //!< Captured thread ID at the construction of the object
        std::thread::id m_originalThreadId; //!< Captured thread ID at the construction time from shared finder
    };

private:
    std::atomic<std::thread::id> m_currentThread; //!< Thread ID currently holding critical section, or empty ID
    std::atomic<bool> m_raceDetected{ false }; //!< Was race condition detected
};

}
}
}
}
