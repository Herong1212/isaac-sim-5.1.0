// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#pragma once

#include <atomic>
#include <thread>
#include "Defines.h"
#include <carb/tasking/ITasking.h>
#include "IPtr.h"

namespace omni
{

struct JoinableThread
{
    std::atomic<bool> m_terminate = false;
    std::thread m_thread;

    template<typename ThreadFn>
    void start(ThreadFn fn)
    {
        m_terminate = false;
        m_thread = std::thread([this, fn]()
            {
                while (!m_terminate)
                {
                    fn();
                }
            });
    }

    ~JoinableThread()
    {
        terminate();
    }

    void terminate()
    {
        if (!m_terminate)
        {
            m_terminate = true;
            if (m_thread.joinable())
            {
                m_thread.join();
            }
        }
    }
};

struct JoinableSleepThread
{
    std::atomic<bool> m_terminate = false;
    std::thread m_thread;
    uint32_t m_sleepMS;
    CachedIPtr<carb::tasking::ITasking> m_tasking;

    JoinableSleepThread(uint32_t sleepMS)
        : m_sleepMS(sleepMS)
    {
    }

    template<typename ThreadFn>
    void start(ThreadFn fn)
    {
        m_terminate = false;
        m_thread = std::thread([this, fn]()
            {
                while (!m_terminate)
                {
                    fn();
                    m_tasking->futexWaitFor(m_terminate, false, std::chrono::milliseconds(m_sleepMS));
                }
            });
    }

    ~JoinableSleepThread()
    {
        terminate();
    }

    void terminate()
    {
        if (!m_terminate)
        {
            m_terminate = true;
            m_tasking->futexWakeup(m_terminate, UINT_MAX);
            if (m_thread.joinable())
            {
                m_thread.join();
            }
        }
    }
};

#if CARB_ENABLE_FAIL

// only enable multi thread detection if TEST failing is enabled, otherwise it is not going to report anything anyways

struct MultiThreadDetector
{
    std::atomic_uint32_t threadId;
    MultiThreadDetector()
    {
        threadId = 0;
    }
};

struct MultiThreadDetectorInstance
{
    MultiThreadDetector& m_detector;
    uint32_t m_threadId;

    MultiThreadDetectorInstance(MultiThreadDetector& detector)
        : m_detector(detector)
    {
        uint32_t newValue = carb::this_thread::getId();
        uint32_t expected = 0;
        if (!m_detector.threadId.compare_exchange_strong(expected, newValue))
        {
            CARB_FAIL_UNLESS(false, "MultiThreadDetector failure : Executing on 0x%x already executed on thread: 0x%x (not aware of fiber switches)", newValue, expected);
            m_threadId = 0;
        }
        else
        {
            m_threadId = newValue;
        }
    }
    ~MultiThreadDetectorInstance()
    {
        uint32_t expected = m_threadId;
        if (!m_detector.threadId.compare_exchange_strong(expected, 0))
        {
            CARB_FAIL_UNLESS(false, "MultiThreadDetector failure at cleanup: was 0x%x, expected: 0x%x", expected, m_threadId);
        }
    }
};

#else // #if CARB_ENABLE_FAIL

// empty implementation
struct MultiThreadDetector {};
struct MultiThreadDetectorInstance
{
    MultiThreadDetectorInstance(MultiThreadDetector& detector) {};
};

#endif // #if !CARB_ENABLE_FAIL

} // namespace omni
