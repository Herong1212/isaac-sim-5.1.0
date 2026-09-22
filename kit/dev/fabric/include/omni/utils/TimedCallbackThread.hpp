// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <chrono>

namespace omni
{

// TimedCallbackThread:
// - implements a helper thread that will attempt to call the given callback at the given interval
class TimedCallbackThread
{
public:
    using Clock = std::chrono::high_resolution_clock;
    using TimeStamp = std::chrono::time_point<Clock>;
    using Callback = std::function<void()>;

    TimedCallbackThread(const char* name, uint32_t callIntervalInMs, Callback callback)
        : m_threadName(name), m_callIntervalInMs(callIntervalInMs), m_callback(callback)
    {
        m_thread = std::thread([this]() { this->threadBody(); });
    }

    void stop()
    {
        if (m_thread.joinable())
        {
            m_terminate = true;
            m_thread.join();
        }
    }

    ~TimedCallbackThread()
    {
        stop();
    }

private:
    void threadBody()
    {
        carb::this_thread::setName(m_threadName.c_str());

        Clock::time_point lastUpdateTime = Clock::now();

        while (!m_terminate)
        {
            auto timeNow = Clock::now();
            auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(timeNow - lastUpdateTime).count();
            if (elapsedMs < m_callIntervalInMs)
            {
                uint32_t msToSleep = m_callIntervalInMs - uint32_t(elapsedMs);
                carb::cpp::this_thread::sleep_for(std::chrono::milliseconds(msToSleep));
            }
            lastUpdateTime = std::chrono::high_resolution_clock::now();

            if (m_callback)
            {
                m_callback();
            }
        }
    }

    std::string m_threadName;
    uint32_t m_callIntervalInMs;
    Callback m_callback;
    std::atomic_bool m_terminate = false;
    std::thread m_thread;
};

} //namespace omni
