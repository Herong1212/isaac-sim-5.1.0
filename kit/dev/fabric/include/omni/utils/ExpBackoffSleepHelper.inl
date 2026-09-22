// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#pragma once

#include <chrono>
#include <random>

namespace omni
{

// Helper to manage an exponential backoff sleep
template <typename SleepUnits = std::chrono::milliseconds>
struct ExpBackoffSleepHelper
{
    using Clock = std::chrono::high_resolution_clock;
    using Timepoint = Clock::time_point;

    ExpBackoffSleepHelper(SleepUnits initialSleep = std::chrono::milliseconds(1000),
                          size_t initialJitterMax = 250,
                          SleepUnits sleepMax = std::chrono::milliseconds(32000))
        : m_sleepMax(sleepMax), m_iterationIndex(0)
    {
        size_t jitter = std::rand() % (initialJitterMax + 1);
        m_currentBackoffSleep = initialSleep + SleepUnits(jitter);
        m_startTime = Clock::now();
    }
    SleepUnits updateAndGetPreviousSleep()
    {
        SleepUnits backOffSleep = m_currentBackoffSleep;
        if (m_currentBackoffSleep <= m_sleepMax)
        {
            m_currentBackoffSleep *= 2;
        }
        ++m_iterationIndex;
        return backOffSleep;
    }
    SleepUnits getBackoff() const
    {
        return m_currentBackoffSleep;
    }
    size_t getIterationIndex() const
    {
        return m_iterationIndex;
    }
    SleepUnits getElapsedTime() const
    {
        return std::chrono::duration_cast<SleepUnits>(Clock::now() - m_startTime);
    }

private:
    SleepUnits m_currentBackoffSleep;
    SleepUnits m_sleepMax;
    size_t m_iterationIndex;
    Timepoint m_startTime;
};

} // namespace omni
