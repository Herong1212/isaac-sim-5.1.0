// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/Types.h>

#include <chrono>
#include <iostream>
#include <iomanip>
#include <vector>
#include <unordered_map>
#include <cmath>

#include <omni/utils/BitScan.h>

namespace omni
{

    struct StopWatch
    {
        using Clock = std::chrono::high_resolution_clock;
        using TimePoint = std::chrono::time_point<Clock>;
        TimePoint startTime;

        StopWatch()
        {
            restart();
        }

        void restart()
        {
            startTime = Clock::now();
        }

        uint64_t elapsedMS()
        {
            return elapsedSince<std::milli>(startTime);
        }
        
        uint64_t elapsedNS()
        {
            return elapsedSince<std::nano>(startTime);
        }

        template<typename ValueT>
        void printElapsed(const char* format)
        {
            CARB_LOG_WARN(format, ValueT(elapsedMS()));
        }

        template<typename ValueT>
        void printElapsedNS(const char* format)
        {
            CARB_LOG_WARN(format, ValueT(elapsedNS()));
        }

        template<typename UnitsType>
        static uint64_t elapsedSince(TimePoint start)
        {
            return uint64_t(std::chrono::duration<double, UnitsType>(Clock::now() - start).count());
        }
    };


    struct PerformanceHistogram
    {
        static const uint32_t kBins = 32;
        std::atomic<size_t> bins[kBins];
        std::atomic_uint64_t totalValue{0};
        std::atomic_uint64_t totalCount{0};
        std::atomic_uint64_t totalM2{ 0 };

        PerformanceHistogram()
        {
            clear();
        }

        void addEvent(uint64_t elapsed)
        {
            uint32_t bin = std::min(uint32_t(omni::findMsb(elapsed)), kBins - 1);
            bin = std::min(uint32_t(omni::findMsb(elapsed + (1 << bin) / 2)), kBins - 1);
            bins[bin]++;
            uint64_t lastValue = totalValue.fetch_add(elapsed);
            uint64_t lastCount = totalCount.fetch_add(1);
            double lastMean = lastCount ? double(lastValue / lastCount) : 0;
            double delta = double(elapsed) - lastMean;
            totalM2 += uint64_t(delta * delta);
        }

        double getMean() const
        {
            return totalCount.load() ? double(totalValue.load()) / totalCount.load() : 0.0;
        }

        double getStandardDeviation() const
        {
            return totalCount.load() > 1 ? sqrt(double(totalM2.load()) / (totalCount.load() - 1)) : 0.0;
        }

        void printHistogram(const uint64_t* values, size_t size, std::ostream& os)
        {
            uint64_t maxValue = 0;

            // Count occurrences of each value and find the maximum value
            uint32_t start = kBins;
            uint32_t end = 0;
            uint64_t totalCount = 0;
            for (uint32_t i = 0; i < size; ++i)
            {
                if (values[i])
                {
                    start = std::min(i, start);
                    end = std::max(i + 1, end);
                }
                if (values[i] > maxValue)
                {
                    maxValue = values[i];
                }
                totalCount += values[i];
            }

            const int histogramWidth = 60; // Width of the histogram bars

            os << "us\t\tOccurrences\tHistogram" << std::endl;
            for (size_t i = start; i < end; ++i)
            {
                uint64_t value = uint64_t(1) << i;
                uint64_t count = values[i];

                // Calculate the length of the histogram bar
                int barLength = static_cast<int>(static_cast<double>(count) / maxValue * histogramWidth);

                // Print the value, occurrences, and the histogram bar
                os << std::fixed << std::setprecision(2) << (value / 1000.0f);
                os << "\t\t" << count << "\t\t";
                for (int i = 0; i < barLength; ++i)
                {
                    os << "#";
                }
                os << std::endl;
            }
            os << "mean us:" << std::fixed << std::setprecision(2) << (getMean() / 1000.0f)
               << " stddev:" << (getStandardDeviation() / 1000.0f) << std::endl;
        }

        void print(std::ostream& os)
        {
            printHistogram((const uint64_t*)bins, kBins, os);
        }

        void print()
        {
            printHistogram((const uint64_t*)bins, kBins, std::cout);
        }

        void clear()
        {
            for (uint32_t i = 0; i < kBins; i++)
                bins[i] = 0;
        }
    };
}
