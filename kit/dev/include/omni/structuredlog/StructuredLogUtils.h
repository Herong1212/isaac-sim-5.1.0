// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
/** @file
 *  @brief Utilities for structured log functionality.
 */
#pragma once
#include "../extras/UniqueApp.h"
#include "IStructuredLogSettings.h"
#include "../../carb/extras/StringSafe.h"

#if CARB_PLATFORM_WINDOWS
#    include "../../carb/CarbWindows.h"
#elif CARB_POSIX
#    include <time.h>
#else
CARB_UNSUPPORTED_PLATFORM();
#endif


namespace omni
{
namespace structuredlog
{

/** Base type for a CloudEvents timestamp.  This will always be a value in nanoseconds. */
using TimestampNs = uint64_t;


/** Generate the 'dataschema' field for events of a schema.
 *  @param[in] clientName    The client name specified in the schema's metadata.
 *  @param[in] schemaVersion The version specified in the schema's metadata.
 *  @returns The 'dataschema' field that will be emitted with the event.
 */
inline std::string generateDataSchema(const char* clientName, const char* schemaVersion)
{
    return std::string(clientName) + '-' + schemaVersion;
}

/** retrieves a UTC timestamp relative to the system epoch in nanoseconds.
 *
 *  @returns the number of system specific ticks that have elapsed since the system epoch.
 *           The specifc epoch depends on the platform.  On Windows, this is midnight Jan
 *           1, 1601.  On Linux, this is midnight Jan 1, 1970.
 *
 *  @thread_safety This is thread safe and only operates on local values.
 */
inline TimestampNs getUtcTimestamp()
{
#if CARB_PLATFORM_WINDOWS
    CARBWIN_FILETIME ft;

    // use GetSystemTimeAsFileTime() since that gives higher than millisecond resolution
    // (number of 100 nanosecond ticks since January 1, 1601).  Other time functions
    // either do not have a reliable granularity, unknown epoch, or have a resolution
    // lower than milliseconds.  This value has ~29247 years of space on it so overflow
    // should not be a concern.  This then needs to be converted to nanoseconds for
    // return.
    GetSystemTimeAsFileTime(reinterpret_cast<FILETIME*>(&ft));
    return ((((uint64_t)ft.dwHighDateTime) << 32) | ft.dwLowDateTime) * 100;
#elif CARB_POSIX
    struct timespec ts;

    // use clock_gettime() since that gives higher than millisecond resolution (number
    // of nanoseconds since January 1, 1970).  Other time functions either have an
    // unknown epoch, have a resolution lower than milliseconds, or are just built on
    // top of this function (ie: gettimeofday()).  Storing this as a 64-bit integer
    // should give approximately 292 years worth of space.  That is significantly more
    // than the 136 years of space that clock_gettime() gives in the first place.
    // Overflow of the value should not be an concern.
    clock_gettime(CLOCK_REALTIME, &ts);
    return (TimestampNs)((ts.tv_sec * 1'000'000'000ll) + ts.tv_nsec);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/** Prints a UTC timestamp as an RfC3339 formatted string.
 *
 *  @param[in]  time    The UTC timestamp to print.  This should have been retrieved from a
 *                      previous call to getUtcTimestamp().
 *  @param[out] buffer  Receives the printed timestamp string.  This buffer must be large
 *                      enough to hold at least @p len characters.  This buffer will always
 *                      be null terminated.  This may not be nullptr.
 *  @param[in]  len     The maximum number of characters that will fit in @p buffer including
 *                      the null terminator.
 *  @returns The number of characters written to the output buffer.
 *           This will truncate the timestamp if there was not enough buffer space.
 *
 *  @thread_safety This is thread safe and only operates on local buffers.
 */
inline size_t printUtcTimestamp(TimestampNs time, char* buffer, size_t len)
{
    size_t count;
    int32_t year;
    int32_t month;
    int32_t day;
    int32_t hour;
    int32_t minute;
    int32_t second;
    int32_t microseconds;


#if CARB_PLATFORM_WINDOWS
    CARBWIN_FILETIME ft;
    CARBWIN_SYSTEMTIME st;
    TimestampNs t;

    // convert the given time index from nanoseconds back to NT ticks (100ns units).
    t = time / 100;

    // convert this back to a FILETIME object (a split 64-bit value representing the number
    // of 100 nanosecond ticks since January 1, 1601) so we can convert it to an adjusted
    // date/time stamp.  The native call already provides milliseconds so we don't need to
    // calculate that separately.
    ft.dwLowDateTime = t & 0xffffffffull;
    ft.dwHighDateTime = t >> 32;
    FileTimeToSystemTime(reinterpret_cast<FILETIME*>(&ft), reinterpret_cast<SYSTEMTIME*>(&st));
    year = st.wYear;
    month = st.wMonth;
    day = st.wDay;
    hour = st.wHour;
    minute = st.wMinute;
    second = st.wSecond;
#elif CARB_POSIX
    struct tm tm;
    time_t t;


    // convert this back to a time_t and a count of remaining milliseconds.  The input time
    // value will be the number of nanoseconds since January 1, 1970.  This will convert it
    // to an adjusted date/time stamp.  Since time_t values only hold times in seconds and
    // gmtime*() are the only functions that provide an adjusted date/time stamp, we'll
    // extract the microseconds count from the original value manually.  Microseconds are
    // not affected by leaps (days or seconds), so they can be safely extracted from the
    // original time without having to adjust the date/time further.
    t = time / 1'000'000'000ull;
    gmtime_r(&t, &tm);
    year = tm.tm_year + 1900;
    month = tm.tm_mon + 1;
    day = tm.tm_mday;
    hour = tm.tm_hour;
    minute = tm.tm_min;
    second = tm.tm_sec;
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif

    microseconds = static_cast<int32_t>((time / 1'000ull) % 1'000'000ull);

    count = carb::extras::formatString(
        buffer, len, "%04d-%02d-%02dT%02d:%02d:%02d.%06dZ", year, month, day, hour, minute, second, microseconds);

    return count;
}

} // namespace structuredlog
} // namespace omni
