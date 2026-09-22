// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#pragma once

#include <carb/tasking/ITasking.h>
#include <carb/tasking/TaskingUtils.h>
#include <carb/profiler/Profile.h>

namespace omni
{

///! Helper to add a max concurrent task limiter.
// - It defaults to allowing the same amount of workers as carb worker threads.
struct TaskSchedulerWithWorkerLimiter
{
    TaskSchedulerWithWorkerLimiter()
    {
        m_tasking = carb::getCachedInterface<carb::tasking::ITasking>();
        const uint32_t taskingThreadCount = m_tasking->getDesc().threadCount;
        m_currentWorkerThreadCount =
            taskingThreadCount > 0 ? taskingThreadCount : carb::thread::hardware_concurrency();

        setMaxWorkerCount(m_currentWorkerThreadCount);
    }
    
    void setMaxWorkerCount(uint32_t maxWorkers)
    {
        setMaxWorkerCountInternal(maxWorkers);
    }

    void setMaxWorkerFactor(float factorOfWorkerThreadCount)
    {
        CARB_ASSERT(factorOfWorkerThreadCount > 0.0f);
        const uint32_t workerCount = uint32_t(m_currentWorkerThreadCount * factorOfWorkerThreadCount);
        setMaxWorkerCountInternal(workerCount);
    }

    carb::tasking::CounterWrapper& getOngoingTaskCounter()
    {
        return m_ongoingTaskCounter;
    }

    template <class Callable, class... Args>
    auto addTask(carb::tasking::Priority priority, Callable&& f, Args&&... args)
    {
        return m_tasking->addThrottledTask(m_activeWorkersSemaphore, priority, m_ongoingTaskCounter,
                                           std::forward<Callable>(f), std::forward<Args>(args)...);
    }

private:
    void setMaxWorkerCountInternal(uint32_t maxWorkerCount)
    {
        CARB_PROFILE_FUNCTION(carb::profiler::kCaptureMaskDefault);

        maxWorkerCount = std::max(uint32_t(1), maxWorkerCount);
        while (m_workerCount > maxWorkerCount)
        {
            m_activeWorkersSemaphore.acquire();
            --m_workerCount;
        }
        while (m_workerCount < maxWorkerCount)
        {
            m_activeWorkersSemaphore.release();
            ++m_workerCount;
        }
    }

    unsigned int m_workerCount = 0;
    carb::tasking::SemaphoreWrapper m_activeWorkersSemaphore{ 0 };

    carb::tasking::CounterWrapper m_ongoingTaskCounter;

    carb::tasking::ITasking* m_tasking = nullptr;
    
    uint32_t m_currentWorkerThreadCount = 0;
};

} // namespace omni
