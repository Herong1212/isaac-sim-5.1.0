// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
/** @file
 *  @brief Wrappers for libc string functions to avoid dangerous edge cases.
 */
#pragma once

// for vsnprintf() on windows
#if !defined(_CRT_SECURE_NO_WARNINGS) && !defined(DOXYGEN_BUILD)
#    define _CRT_SECURE_NO_WARNINGS
#endif

#include "../detail/PushBadMacros.h"

#include "../Defines.h"
#include "ScopeExit.h"

#include <cstdarg>
#include <cstdio>
#include <cstring>

namespace carb
{
namespace extras
{

/**
 * Verify if a string is null or empty.
 *
 * @param str The string to check.
 * @returns true if the string is null or empty, false otherwise.
 */
inline bool isNullOrEmpty(const char* str)
{
    return str == nullptr || str[0] == '\0';
}

/** Compare two strings in a case sensitive manner.
 *
 *  @param[in] str1             The first string to compare.  This may not be `nullptr`.
 *  @param[in] str2             The second string to compare.  This may not be `nullptr`.
 *  @returns `0` if the two strings match.
 *  @returns A negative value if `str1` should be ordered before `str2`.
 *  @returns A positive value if `str1` should be ordered after `str2`.
 */
inline int32_t compareStrings(const char* str1, const char* str2)
{
    return strcmp(str1, str2);
}

/** Compare two strings in a case insensitive manner.
 *
 *  @param[in] str1             The first string to compare.  This may not be `nullptr`.
 *  @param[in] str2             The second string to compare.  This may not be `nullptr`.
 *  @returns `0` if the two strings match.
 *  @returns A negative value if `str1` should be ordered before `str2`.
 *  @returns A positive value if `str1` should be ordered after `str2`.
 */
inline int32_t compareStringsNoCase(const char* str1, const char* str2)
{
#if CARB_PLATFORM_WINDOWS
    return _stricmp(str1, str2);
#else
    return strcasecmp(str1, str2);
#endif
}

/**
 * Check if two memory regions overlaps.
 *
 * @param[in] ptr1 pointer to a first memory region.
 * @param[in] size1 size in bytes of the first memory region.
 * @param[in] ptr2 pointer to a second memory region.
 * @param[in] size2 size in bytes of the second memory region.
 *
 * @return true if memory regions overlaps or false if they are not.
 */
inline bool isMemoryOverlap(const void* ptr1, size_t size1, const void* ptr2, size_t size2)
{
    // We assume flat memory model.
    uintptr_t addr1 = uintptr_t(ptr1);
    uintptr_t addr2 = uintptr_t(ptr2);

    if (addr1 < addr2)
    {
        if (addr2 - addr1 >= size1)
        {
            return false;
        }
    }
    else if (addr1 > addr2)
    {
        if (addr1 - addr2 >= size2)
        {
            return false;
        }
    }

    return true;
}

/**
 * Copy a string with optional truncation.
 *
 * @param[out] dstBuf pointer to a destination buffer (can be nullptr in the case if dstBufSize is zero).
 * @param[in] dstBufSize size in characters of the destination buffer.
 * @param[in] srcString pointer to a source string.
 *
 * @return a number of copied characters to the destination buffer (not including the trailing \0).
 *
 * @remark This function copies up to dstBufSize - 1 characters from the 0-terminated string srcString
 * to the buffer dstBuf and appends trailing \0 to the result. This function is guarantee that the result
 * has trailing \0 as long as dstBufSize is larger than 0.
 */
inline size_t copyStringSafe(char* dstBuf, size_t dstBufSize, const char* srcString)
{
    CARB_ASSERT(dstBuf || dstBufSize == 0);
    CARB_ASSERT(srcString);

    if (dstBufSize > 0)
    {
        // Compute length of the source string to be copied.
        size_t copyLength = strlen(srcString);

        // Check the source and destination are not overlapped.
        CARB_ASSERT(!isMemoryOverlap(dstBuf, dstBufSize, srcString, copyLength + 1));

        if (copyLength >= dstBufSize)
        {
            copyLength = dstBufSize - 1;
            memcpy(dstBuf, srcString, copyLength);
        }
        else if (copyLength > 0)
        {
            memcpy(dstBuf, srcString, copyLength);
        }
        dstBuf[copyLength] = '\0';

        return copyLength;
    }

    return 0;
}

/**
 * Copy slice of string with optional truncation.
 *
 * @param[out] dstBuf pointer to a destination buffer (can be nullptr in the case if dstBufSize is zero).
 * @param[in] dstBufSize size in characters of the destination buffer.
 * @param[in] srcString pointer to a source string (can be nullptr in the case if maxCharacterCount is zero).
 * @param[in] maxCharacterCount maximum number of characters to be copied from the source string.
 *
 * @return a number of copied characters to the destination buffer (not including the trailing \0).
 *
 * @remarks This function copies up to min(dstBufSize - 1, maxCharacterCount) characters from the source string
 * srcString to the buffer dstBuf and appends trailing \0 to the result. This function is guarantee that the result has
 * trailing \0 as long as dstBufSize is larger than 0.
 */
inline size_t copyStringSafe(char* dstBuf, size_t dstBufSize, const char* srcString, size_t maxCharacterCount)
{
    CARB_ASSERT(dstBuf || dstBufSize == 0);
    CARB_ASSERT(srcString || maxCharacterCount == 0);

    // NOTE: We don't use strncpy_s in implementation even if it's available in the system because it places empty
    // string to the destination buffer in case of truncation of source string (see the detailed description at
    // https://en.cppreference.com/w/c/string/byte/strncpy).

    // Instead, we use always our own implementation which is tolerate to any case of truncation.

    if (dstBufSize > 0)
    {
        // Compute length of the source string slice to be copied.
        size_t copyLength = (maxCharacterCount > 0) ? strnlen(srcString, CARB_MIN(dstBufSize - 1, maxCharacterCount)) : 0;

        // Check the source and destination are not overlapped.
        CARB_ASSERT(!isMemoryOverlap(dstBuf, dstBufSize, srcString, copyLength));

        if (copyLength > 0)
        {
            memcpy(dstBuf, srcString, copyLength);
        }
        dstBuf[copyLength] = '\0';

        return copyLength;
    }

    return 0;
}

/**
 * A vsnprintf wrapper that clamps the return value.
 *
 * @param[out] dstBuf pointer to a destination buffer (can be nullptr in the case if dstBufSize is zero).
 * @param[in] dstBufSize size in characters of the destination buffer.
 * @param[in] fmtString pointer to a format string (passed to the vsnprintf call).
 * @param[in] argsList arguments list
 *
 * @return a number of characters written to the destination buffer (not including the trailing \0).
 *
 * @remarks This function is intended to be used in code where an index is incremented by snprintf.
 * In the following example, if vsnprintf() were used, idx can become larger than
 * len, causing wraparound errors, but with formatStringV(), idx will never
 * become larger than len.
 *
 *               idx += formatStringV(buf, len - idx, ...);
 *               idx += formatStringV(buf, len - idx, ...);
 *
 */
inline size_t formatStringV(char* dstBuf, size_t dstBufSize, const char* fmtString, va_list argsList)
{
    CARB_ASSERT(dstBuf || dstBufSize == 0);
    CARB_ASSERT(fmtString);

    if (dstBufSize > 0)
    {
        int rc = std::vsnprintf(dstBuf, dstBufSize, fmtString, argsList);
        size_t count = size_t(rc);
        if (rc < 0)
        {
            // We assume no output in a case of I/O error.
            dstBuf[0] = '\0';
            count = 0;
        }
        else if (count >= dstBufSize)
        {
            // ANSI C always adds the null terminator, older MSVCRT versions do not.
            dstBuf[dstBufSize - 1] = '\0';
            count = (dstBufSize - 1);
        }

        return count;
    }

    return 0;
}

/**
 * A snprintf wrapper that clamps the return value.
 *
 * @param[out] dstBuf pointer to a destination buffer (can be nullptr in the case if dstBufSize is zero).
 * @param[in] dstBufSize size in characters of the destination buffer.
 * @param[in] fmtString pointer to a format string (passed to the snprintf call).
 *
 * @return a number of characters written to the destination buffer (not including the trailing \0).
 *
 * @remarks This function is intended to be used in code where an index is incremented by snprintf.
 * In the following example, if snprintf() were used, idx can become larger than
 * len, causing wraparound errors, but with formatString(), idx will never
 * become larger than len.
 *
 *               idx += formatString(buf, len - idx, ...);
 *               idx += formatString(buf, len - idx, ...);
 *
 */
inline size_t formatString(char* dstBuf, size_t dstBufSize, const char* fmtString, ...) CARB_PRINTF_FUNCTION(3, 4);

inline size_t formatString(char* dstBuf, size_t dstBufSize, const char* fmtString, ...)
{
    size_t count;
    va_list argsList;

    va_start(argsList, fmtString);
    count = formatStringV(dstBuf, dstBufSize, fmtString, argsList);
    va_end(argsList);

    return count;
}

/** Test if one string is a prefix of the other.
 *  @param[in] str    The string to test.
 *  @param[in] prefix The prefix to test on @p str.
 *  @returns `true` if @p str begins with @p prefix.
 *  @returns `false` otherwise.
 */
inline bool isStringPrefix(const char* str, const char* prefix)
{
    for (size_t i = 0; prefix[i] != '\0'; i++)
    {
        if (str[i] != prefix[i])
        {
            return false;
        }
    }
    return true;
}

/**
 * Formats as with vsnprintf() and calls a Callable with the result and the size. The memory for the string is managed
 * for the caller.
 * \details This function attempts to use the stack first but will fall back to the heap if the given \p fmt and
 * arguments do not fit on the stack.
 * \tparam StackSize The size of the stack buffer to reserve. The default is 256 characters. This amount includes the
 *   NUL terminator.
 * \tparam Callable The type of callable that will be invoked with the formatted string and its size. The type should be
 *   `void(const char*, size_t)`; any return type will be ignored. The size given will not include the NUL terminator.
 * \param fmt The `printf`-style format string.
 * \param ap The collection of variadic arguments as initialized by `va_start` or `va_copy`.
 * \param c The \c Callable that will be invoked after the string format. Any return value is ignored. It is undefined
 *   behavior to use the pointer value passed to \p c after \p c returns.
 */
template <size_t StackSize = 256, class Callable>
void withFormatNV(const char* fmt, va_list ap, Callable&& c) noexcept
{
    char* heap = nullptr;
    char buffer[StackSize];

    va_list ap2;
    va_copy(ap2, ap);
    CARB_SCOPE_EXIT
    {
        va_end(ap2);
        delete[] heap;
    };

    constexpr static char kErrorFormat[] = "<vsnprintf failed>";
    constexpr static char kErrorAlloc[] = "<failed to allocate>";

    // Optimistically try to format
    char* pbuf = buffer;
    int isize = std::vsnprintf(pbuf, StackSize, fmt, ap);
    if (CARB_UNLIKELY(isize < 0))
    {
        c(kErrorFormat, CARB_COUNTOF(kErrorFormat) - 1);
        return;
    }

    auto size = size_t(isize);
    if (size >= StackSize)
    {
        // Need the heap
        pbuf = heap = new (std::nothrow) char[size + 1];
        if (CARB_UNLIKELY(!heap))
        {
            c(kErrorAlloc, CARB_COUNTOF(kErrorAlloc) - 1);
            return;
        }

        isize = std::vsnprintf(pbuf, size + 1, fmt, ap2);
        if (CARB_UNLIKELY(isize < 0))
        {
            c(kErrorFormat, CARB_COUNTOF(kErrorFormat) - 1);
            return;
        }
        size = size_t(isize);
    }

    c(const_cast<const char*>(pbuf), size);
}

/**
 * Formats as with vsnprintf() and calls a Callable with the result. The memory for the string is managed for the
 * caller.
 * \details This function attempts to use the stack first but will fall back to the heap if the given \p fmt and
 * arguments do not fit on the stack.
 * \tparam StackSize The size of the stack buffer to reserve. The default is 256 characters. This amount includes the
 *   NUL terminator.
 * \tparam Callable The type of callable that will be invoked with the formatted string. The type should be
 *   `void(const char*)`; any return type will be ignored.
 * \param fmt The `printf`-style format string.
 * \param ap The collection of variadic arguments as initialized by `va_start` or `va_copy`.
 * \param c The \c Callable that will be invoked after the string format. Any return value is ignored. It is undefined
 *   behavior to use the pointer value passed to \p c after \p c returns.
 */
template <size_t StackSize = 256, class Callable>
void withFormatV(const char* fmt, va_list ap, Callable&& c)
{
    // Adapt to drop the size
    withFormatNV<StackSize>(fmt, ap, [&](const char* p, size_t) { c(p); });
}

/**
 * @copydoc CARB_FORMATTED
 * \param size The size of the stack buffer to reserve. If the formatted string will be larger than this size, a buffer
 *   will be created on the heap instead, and destroyed once the callable returns.
 */
#define CARB_FORMATTED_SIZE(size, fmt, ...)                                                                            \
    do                                                                                                                 \
    {                                                                                                                  \
        va_list CARB_JOIN(ap, __LINE__);                                                                               \
        va_start(CARB_JOIN(ap, __LINE__), fmt);                                                                        \
        CARB_SCOPE_EXIT                                                                                                \
        {                                                                                                              \
            va_end(CARB_JOIN(ap, __LINE__));                                                                           \
        };                                                                                                             \
        ::carb::extras::withFormatV<size>((fmt), CARB_JOIN(ap, __LINE__), __VA_ARGS__);                                \
    } while (0)

/**
 * Formats a string as if by vsnprintf and invokes a callable with the result.
 * \details This macro constructs a `va_list`, gathers the variadic parameters with `va_start`, formats the string with
 * `std::vsnprintf`, and calls a Callable with the formatted string. This function reserves a stack buffer of the size
 * requested by \c size for \ref CARB_FORMATTED_SIZE or a default size for \ref CARB_FORMATTED, but if the formatted
 * string will not fit into that buffer, will use the heap to create a larger buffer.
 * \param fmt The `printf`-style format string.
 * \param ... A Callable that may be invoked as via `...(p)` where `p` is a `const char*`, such as a lambda, functor or
 *   function pointer. Retaining and reading `p` after the Callable returns is undefined behavior. If an error occurs
 *   with `std::vsnprintf` then `p` will be `<vsnprintf failed>`, or if a heap buffer was required and allocation
 *   failed, then `p` will be `<failed to allocate>`. If you wish the callback to receive the length of the formatted
 *   string as well, use \ref CARB_FORMATTED_N() or \ref CARB_FORMATTED_N_SIZE().
 * \note This macro is intended to be used in variadic functions as a simple means of replacing uses of
 *   `std::vsnprintf`.
 * ```cpp
 * void myLogFunction(const char* fmt, ...) {
 *     CARB_FORMATTED([&](const char* p) {
 *         log(p);
 *     });
 * }
 * ```
 * \see CARB_FORMATTED(), CARB_FORMATTED_SIZE(), CARB_FORMATTED_N(), CARB_FORMATTED_N_SIZE(),
 *   carb::extras::withFormatNV(), carb::extras::withFormatV()
 */
#define CARB_FORMATTED(fmt, ...) CARB_FORMATTED_SIZE(256, fmt, __VA_ARGS__)

/**
 * @copydoc CARB_FORMATTED_N
 * \param size The size of the stack buffer to reserve. If the formatted string will be larger than this size, a buffer
 *   will be created on the heap instead, and destroyed once the callable returns.
 */
#define CARB_FORMATTED_N_SIZE(size, fmt, ...)                                                                          \
    do                                                                                                                 \
    {                                                                                                                  \
        va_list CARB_JOIN(ap, __LINE__);                                                                               \
        va_start(CARB_JOIN(ap, __LINE__), fmt);                                                                        \
        CARB_SCOPE_EXIT                                                                                                \
        {                                                                                                              \
            va_end(CARB_JOIN(ap, __LINE__));                                                                           \
        };                                                                                                             \
        ::carb::extras::withFormatNV<size>((fmt), CARB_JOIN(ap, __LINE__), __VA_ARGS__);                               \
    } while (0)

/**
 * Formats a string as if by vsnprintf and invokes a callable with the result and the length.
 * \details This macro constructs a `va_list`, gathers the variadic parameters with `va_start`, formats the string with
 * `std::vsnprintf`, and calls a Callable with the formatted string and length. This function reserves a stack buffer of
 * the size requested by \c size for \ref CARB_FORMATTED_N_SIZE or a default size for \ref CARB_FORMATTED_N, but if the
 * formatted string will not fit into the stack buffer, will use the heap to create a larger buffer.
 * \param fmt The `printf`-style format string.
 * \param ... A Callable that may be invoked as via `...(p, n)` (where `p` is a `const char*` and `n` is a `size_t`),
 *   such as a lambda, functor or function pointer. Retaining and reading `p` after the Callable returns is undefined
 *   behavior. If an error occurs with `std::vsnprintf` then `p` will be `<vsnprintf failed>`, or if a heap buffer was
 *   required and allocation failed, then `p` will be `<failed to allocate>`. If you do not need the length provided to
 *   the Callable, use \ref CARB_FORMATTED() or \ref CARB_FORMATTED_SIZE() instead.
 * \note This macro is intended to be used in variadic functions as a simple means of replacing uses of
 *   `std::vsnprintf`.
 * ```cpp
 * void myLogFunction(const char* fmt, ...) {
 *     CARB_FORMATTED_N([&](const char* p, size_t len) {
 *         log(p, len);
 *     });
 * }
 * ```
 */
#define CARB_FORMATTED_N(fmt, ...) CARB_FORMATTED_N_SIZE(256, fmt, __VA_ARGS__)

} // namespace extras
} // namespace carb

#include "../detail/PopBadMacros.h"
