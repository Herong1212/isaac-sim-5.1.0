// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief Carbonite error handling utilities
#pragma once

#include "../Defines.h"

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#    include "Unicode.h"

#    include <memory>
#elif CARB_POSIX
// Nothing needed for now
#else
CARB_UNSUPPORTED_PLATFORM();
#endif
#include <cerrno>
#include <string.h>
#include <string>

namespace carb
{
namespace extras
{

//! The decayed type of `errno`
//!
//! Defined as `std::decay_t<decltype(errno)>`
using ErrnoType = std::decay_t<decltype(errno)>;

#if defined(DOXYGEN_BUILD) || CARB_PLATFORM_WINDOWS
//! (Windows only) The type of value returned from `GetLastError()`
using WinApiErrorType = unsigned long;
#endif

/**
 * Returns the last value of errno.
 *
 * @return the last value of errno.
 */
inline ErrnoType getLastErrno() noexcept
{
    return errno;
}

/**
 * Returns a human-readable string for a given errno value
 *
 * On Windows, this value is created from <a
 * href="https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/strerror-s-strerror-s-wcserror-s-wcserror-s?view=msvc-170">strerror_s()</a>.
 * On other platforms, <a href="https://linux.die.net/man/3/strerror_r">strerror_r()</a> is used instead. If the GNU
 * version is available it is used, otherwise the XSI-compliant version is used.
 *
 * @warning This function does not make any guarantees about the current value of `errno` or attempts to keep `errno`
 * set at the same value; `errno` may be modified by this function.
 *
 * @param errorCode the error code read from `errno`
 * @return text message corresponding to the error code; an \p errorCode of 0 returns an empty string
 */
inline std::string convertErrnoToMessage(ErrnoType errorCode)
{
    if (errorCode == 0)
        return {};

    char buffer[1024];
    constexpr size_t bufferSize = carb::countOf(buffer);

#if CARB_PLATFORM_WINDOWS
    if (CARB_LIKELY(strerror_s(buffer, bufferSize, errorCode) == 0))
        return buffer;

    return ("Error code " + std::to_string(errorCode)) + " failed to format";
#elif CARB_PLATFORM_LINUX

    // strerror_r implementation switch
#    if ((_POSIX_C_SOURCE >= 200112L || _XOPEN_SOURCE >= 600) && !_GNU_SOURCE)
    // XSI-compliant strerror_r
    if (CARB_LIKELY(strerror_r(errorCode, buffer, bufferSize) == 0))
        return buffer;

    return ("Error code " + std::to_string(errorCode)) + " failed to format";
#    else
    // GNU-specific strerror_r
    // We always get some result in this implementation for a valid buffer
    return strerror_r(errorCode, buffer, bufferSize);

#    endif // end of strerror_r implementation switch
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif // end of platform switch
}

/**
 * Reads the current value of `errno` and returns a human-readable string for the errno value.
 *
 * @note Unlike \ref convertErrnoToMessage(), this function ensures that `errno` remains consistent by setting `errno`
 *     to the same value after creating the string.
 * @see getLastErrno() convertErrnoToMessage()
 * @param[out] out If not `nullptr`, receives the value of `errno`.
 * @return string value from \ref convertErrnoToMessage()
 */
inline std::string getLastErrnoMessage(ErrnoType* out = nullptr)
{
    const ErrnoType errorCode = getLastErrno();
    if (out)
        *out = errorCode;
    auto str = convertErrnoToMessage(errorCode);
    errno = errorCode;
    return str;
}

///////////////////////////////////
/// Platform specific functions ///
///////////////////////////////////

#if CARB_PLATFORM_WINDOWS || defined(DOXYGEN_BUILD)

/**
 * (Windows only) Returns the value of the GetLastError() Win32 API function
 *
 * @return the value of the GetLastError Win API function.
 */
inline WinApiErrorType getLastWinApiErrorCode() noexcept
{
    return ::GetLastError();
}

/**
 * (Windows only) Converts a Win32 API error code into a human-readable string.
 *
 * This function translates a Win32 API error code into a human-readable string using the `FormatMessageA` function.
 *
 * @note In some cases, the returned string may have UTF-8 encoding or format specifiers. Use caution when printing
 *    this string. For instance, `ERROR_BAD_EXE_FORMAT` contains `"%1"`.
 *
 * @warning This function does not make any guarantees about the current value of `GetLastError()` or attempts to keep
 * `GetLastError()` set at the same value; `GetLastError()` may be modified by this function.
 *
 * @param errorCode the code of the Win API error
 * @return a human-readable message based on the error code; an \p errorCode of 0 produces an empty string
 */
inline std::string convertWinApiErrorCodeToMessage(WinApiErrorType errorCode)
{
    if (errorCode == CARBWIN_ERROR_SUCCESS)
    {
        return {};
    }

    LPWSTR resultMessageBuffer = nullptr;
    const DWORD kFormatFlags = CARBWIN_FORMAT_MESSAGE_ALLOCATE_BUFFER | CARBWIN_FORMAT_MESSAGE_FROM_SYSTEM |
                               CARBWIN_FORMAT_MESSAGE_IGNORE_INSERTS;

    const DWORD dwFormatResultCode = FormatMessageW(kFormatFlags, nullptr, errorCode,
                                                    CARBWIN_MAKELANGID(CARBWIN_LANG_NEUTRAL, CARBWIN_SUBLANG_DEFAULT),
                                                    reinterpret_cast<LPWSTR>(&resultMessageBuffer), 0, nullptr);
    if (dwFormatResultCode == 0 || !resultMessageBuffer)
    {
        return ("Error code " + std::to_string(errorCode)) + " failed to format";
    }

    struct Deleter
    {
        void operator()(LPWSTR str)
        {
            ::LocalFree(str);
        }
    };
    std::unique_ptr<WCHAR, Deleter> systemBuffKeeper(resultMessageBuffer);
    return carb::extras::convertWideToUtf8(resultMessageBuffer);
}

/**
 * (Windows only) Reads the value of `GetLastError()` and converts it to a human-readable string.
 *
 * @note Unlike \ref convertWinApiErrorCodeToMessage(), this function will keep the same error code consistent. A call
 *     to `GetLastError()` after calling this function will return the same value as prior to calling this function.
 *
 * @return the string from \ref convertWinApiErrorCodeToMessage()
 */
inline std::string getLastWinApiErrorMessage()
{
    const WinApiErrorType errorCode = getLastWinApiErrorCode();
    auto str = convertWinApiErrorCodeToMessage(errorCode);
    SetLastError(errorCode);
    return str;
}

#endif // #if CARB_PLATFORM_WINDOWS

} // namespace extras
} // namespace carb
