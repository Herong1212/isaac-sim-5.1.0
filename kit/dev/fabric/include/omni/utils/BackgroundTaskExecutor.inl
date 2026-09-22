// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <future>
#include <queue>
#include <mutex>

namespace omni
{

// Helper to execute tasks in a another thread and synchronize back to the caller with a future.
// - If useConditionVariable is true it will block waiting in pollTaskExecution() to be notified of tasks with Submit(),
// otherwise it polls and returns immediately if no tasks are queued.
// - Note that the intended use of this wrapper is for non performance critical codepaths as it relies on fairly heavy handed memory 
// allocation for the task entries and a plain std::queue and mutex.
class BackgroundTaskExecutor
{
public:
    BackgroundTaskExecutor(bool useConditionVariable)
    : m_useConditionVariable(useConditionVariable),
      m_stop(false)
    {}

    ~BackgroundTaskExecutor()
    {
        terminate();
    }

    // submit a function to be executed on by another thread that calls pollTaskExecution()
    // and return a future we can wait for
    template <typename Func>
    auto submit(Func&& func) -> std::future<decltype(func())>
    {
        using ReturnType = decltype(func());
        auto task = std::make_shared<std::packaged_task<ReturnType()>>(std::forward<Func>(func));
        std::future<ReturnType> result = task->get_future();

        {
            std::unique_lock<std::mutex> lock(m_mutex);
            m_tasks.emplace([task]() { (*task)(); });
        }

        if (m_useConditionVariable)
        {
            m_cv.notify_one();
        }

        return result;
    }

    // Should be called in the execution thread to pickup and execute the next pending task.
    // Returns true if a task was executed, false otherwise.
    bool pollTaskExecution()
    {
        std::function<void()> task;

        {
            std::unique_lock<std::mutex> lock(m_mutex);

            if (m_useConditionVariable)
            {
                m_cv.wait(lock, [this] { return !m_tasks.empty() || m_stop; });
            }

            if (m_stop || m_tasks.empty())
            {
                return false;
            }

            task = std::move(m_tasks.front());
            m_tasks.pop();
        }

        task();
        return true;
    }

    void terminate()
    {
        m_stop = true;
        if (m_useConditionVariable)
        {
            m_cv.notify_all();
        }
    }

private:
    std::queue<std::function<void()>> m_tasks;
    std::mutex m_mutex;
    std::condition_variable m_cv;
    bool m_useConditionVariable = true;
    bool m_stop = false;
};

} //namespace omni
