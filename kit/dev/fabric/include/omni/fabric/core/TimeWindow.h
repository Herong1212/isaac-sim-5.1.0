// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/fabric/core/Macros.h>
#include <omni/fabric/core/FabricTime.h>
#include <omni/fabric/core/RationalTime.h>

#include <cstddef>
#include <cstdint>

namespace omni
{
namespace fabric
{

enum class TimeUnits
{
    NANOSECONDS,
    MICROSECONDS,
    MILLISECONDS,
    SECONDS,
    MINUTES,
    HOURS
};


struct Instant
{
    double time;
    TimeUnits timeUnits;
    double error;
    TimeUnits errorUnits;
};
constexpr Instant kInvalidInstant{ (double)~0, (TimeUnits)~0, (double)~0, (TimeUnits)~0 };
constexpr Instant kLiveInstant = kInvalidInstant;
FABRIC_DEFINE_COMPARATORS(Instant);
FABRIC_ENFORCE_STANDARD_LAYOUT(Instant);


struct Duration
{
    double time;
    TimeUnits timeUnits;
    double error;
    TimeUnits errorUnits;
};
FABRIC_ENFORCE_STANDARD_LAYOUT(Duration);


struct TimeWindow
{
    Instant begin;
    Duration duration;
};
FABRIC_ENFORCE_STANDARD_LAYOUT(TimeWindow);

/**
 * These options are used for controlling how time windows boundary behaviors
 *
 * eExclusive -> time range is (start, end)
 * eIncludeStart -> time range is [start, end)
 * eIncludeEnd -> time range is (start, end]
 * eIncludeBoth -> time range is [start, end]
 *
 */
enum class EndPointOptions : uint8_t
{
    eExclusive = 0,
    eIncludeStart = 1,
    eIncludeEnd = 2,
    eIncludeBoth = 3
};

template<typename T>
struct TimeWindowOf
{
    T start;
    T end;
    EndPointOptions opt;
};

typedef TimeWindowOf<RationalTime> RationalTimeWindow;
FABRIC_ENFORCE_STANDARD_LAYOUT(RationalTimeWindow);

typedef TimeWindowOf<double> DoubleTimeWindow;
FABRIC_ENFORCE_STANDARD_LAYOUT(DoubleTimeWindow);

typedef TimeWindowOf<FabricTime> FabricTimeWindow;
FABRIC_ENFORCE_STANDARD_LAYOUT(FabricTimeWindow);

} // namespace fabric
} // namespace omni
