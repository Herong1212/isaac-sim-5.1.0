// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "../Defines.h"

#include <time.h>

namespace carb
{
namespace time
{

/**
 * Platform independent version of asctime_r: convert a `struct tm` into a null-terminated string.
 * @tparam N The size of \p buf; must be at least 26 characters.
 * @param tm The time component representation.
 * @param buf The character buffer to render the string into. Must be at least 26 characters.
 * @returns \p buf, or `nullptr` if an error occurs.
 */
template <size_t N>
inline char* asctime_r(const struct tm* tm, char (&buf)[N]) noexcept
{
    // Buffer requirements as specified:
    // https://linux.die.net/man/3/gmtime_r
    // https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/asctime-s-wasctime-s?view=msvc-170
    static_assert(N >= 26, "Insufficient buffer size");
#if CARB_PLATFORM_WINDOWS
    return asctime_s(buf, N, tm) == 0 ? buf : nullptr;
#elif CARB_POSIX
    return ::asctime_r(tm, buf);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Platform independent version of ctime_r; convert a `time_t` into a null-terminated string in the user's local time
 * zone.
 *
 * Equivalent to:
 * ```
 * struct tm tmBuf;
 * return asctime_r(localtime_r(timep, &tmBuf), buf);
 * ```
 * @tparam N The size of \p buf; must be at least 26 characters.
 * @param timep A pointer to a `time_t`.
 * @param buf The character buffer to render the string into. Must be at least 26 characters.
 * @returns \p buf, or `nullptr` if an error occurs.
 */
template <size_t N>
inline char* ctime_r(const time_t* timep, char (&buf)[N]) noexcept
{
    // Buffer requirements as specified:
    // https://linux.die.net/man/3/gmtime_r
    // https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/ctime-s-ctime32-s-ctime64-s-wctime-s-wctime32-s-wctime64-s?view=msvc-170
    static_assert(N >= 26, "Insufficient buffer size");
#if CARB_PLATFORM_WINDOWS
    auto err = ctime_s(buf, N, timep);
    return err == 0 ? buf : nullptr;
#elif CARB_POSIX
    return ::ctime_r(timep, buf);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Platform independent version of gmtime_r: convert a `time_t` to UTC component representation.
 * @param timep A pointer to a `time_t`.
 * @param result A pointer to a `struct tm` that will receive the result.
 * @returns \p result if conversion succeeded; `nullptr` if the year does not fit into an integer or an error occurs.
 */
inline struct tm* gmtime_r(const time_t* timep, struct tm* result) noexcept
{
#if CARB_PLATFORM_WINDOWS
    auto err = ::gmtime_s(result, timep);
    return err == 0 ? result : nullptr;
#elif CARB_POSIX
    return ::gmtime_r(timep, result);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/**
 * Platform independent version of localtime_r: convert a `time_t` to local timezone component representation.
 * @param timep A pointer to a `time_t`.
 * @param result A pointer to a `struct tm` that will receive the result.
 * @returns \p result if conversion succeeded; `nullptr` if the year does not fit into an integer or an error occurs.
 */
inline struct tm* localtime_r(const time_t* timep, struct tm* result) noexcept
{
#if CARB_PLATFORM_WINDOWS
    auto err = ::localtime_s(result, timep);
    return err == 0 ? result : nullptr;
#elif CARB_POSIX
    return ::localtime_r(timep, result);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

} // namespace time
} // namespace carb
