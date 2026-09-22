// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Provides an interface to allow for more detailed assertion failure dialogues.
#pragma once

#include "../Interface.h"

#include <cstdarg>

//! The latest possible version of \ref carb::assert::IAssert
#define carb_assert_IAssert_latest CARB_HEXVERSION(1, 1)
#ifndef carb_assert_IAssert
//! The default version of \ref carb::assert::IAssert
#    define carb_assert_IAssert CARB_HEXVERSION(1, 0)
#endif

// NOTE: this interface is included and used in a very low level header.  No more headers than are
//       absolutely necessary should be included from here.
#include "../Interface.h"

#include <stdarg.h>

namespace carb::assert
{
struct IAssert;
}

/** Defines the global variable that holds the pointer to the IAssert implementation.  This will
 *  be `nullptr` if the IAssert interface is unavailable, disabled, or has not been initialized
 *  yet.  This variable is specific to each module.
 */
CARB_WEAKLINK CARB_HIDDEN carb::assert::IAssert* g_carbAssert;

/** Namespace for all low level Carbonite functionality. */
namespace carb
{
/** Namespace for all assertion checking helpers and interfaces. */
namespace assert
{

//! Assertion types
enum class Type : uint16_t
{
    eAssert, //!< A debug assert, such as \ref CARB_ASSERT.
    eCheck, //!< A checked-build assert, such as \ref CARB_CHECK.
    eReleaseAssert, //!< A release assert, such as \ref CARB_RELEASE_ASSERT.
    eFatal //!< A fatal assert, such as \ref CARB_FATAL_UNLESS.
};

//! The return value of a vectored assertion handler.
enum class Result
{
    //! The next vectored assertion handler should be called.
    eCallNext,

    //! Stop calling assertion handlers. Execution should continue from the assertion point without triggering any
    //! software breakpoint.
    //! @note For \ref Type::eFatal this return value is treated the same as \ref eHalt.
    eContinueExecution,

    //! Stop calling assertion handlers. Stop execution typically via a software breakpoint, or in the case of
    //! \ref Type::eFatal, by calling `std::terminate()`.
    eHalt,
};

//! Information about an assertion.
//! @note This structure is not intended to be instantiated directly but by assertion macros such as \ref CARB_ASSERT.
struct AssertEntry
{
    //! Must always match `sizeof(AssertEntry)`. Used as versioning.
    uint16_t sizeOf{ uint16_t(sizeof(AssertEntry)) };

    //! The assertion \ref Type.
    Type type;

    //! The source code line number where the assertion is located.
    int32_t line;

    //! A string representation of the assertion that failed.
    const char* condition;

    //! The source code file name where the assertion is located.
    const char* file;

    //! The source code function name where the assertion is located.
    const char* func;

    //! Constructor.
    constexpr AssertEntry(Type type, const char* condition, const char* func, const char* file, int32_t line) noexcept
        : type(type), line(line), condition(condition), file(file), func(func)
    {
    }
};

/**
 * Definition of a vectored assertion handler function.
 *
 * Called in sequence when an assertion fails.
 * @param entry Information about the failed assertion.
 * @param extraInfo May be `nullptr`. If the assertion failure provided additional information it is provided here. If
 *   the assertion failure did not provide additional information, this will be `nullptr`.
 * @param userData The opaque pointer passed when the assertion handler was registered.
 * @retval Result::eCallNext Call the next vectored assertion handler in sequence.
 * @retval Result::eContinueException Stop calling vectored assertion handlers and continue execution at the point where
 *   the assertion failed.
 * @retval Result::eHalt Stop calling vectored assertion handlers and halt (typically via a software breakpoint) at the
 *   point where the assertion failed.
 */
using VectoredAssertionHandler = Result (*)(const AssertEntry& entry, const char* extraInfo, void* userData);

//! A handle type representing a registered vectored assertion handler.
enum class [[nodiscard]] Handle : uintptr_t{
    kInvalid = 0 //!< Represents an invalid handle type.
};

/** Base type for the flags that control the behavior of CARB_ASSERT() and CARB_CHECK() failure reporting. */
using AssertFlags = uint32_t;

/** Flag to indicate that the assertion confirmation dialog should always be skipped for this
 *  process.  When set, the dialog will be assumed to always behave as though the button to
 *  break into the debugger had been pressed.  When clear, the dialog will show based on
 *  platform defaults.
 */
constexpr AssertFlags fAssertSkipDialog = 0x00000001;

/** Flag to indicate that the software breakpoint that is triggered on a failing assertion
 *  is to be ignored.  When set, the breakpoint will never be executed and execution will
 *  simply continue after reporting the failed assertion to the logs.  When clear, the
 *  breakpoint will be executed normally.
 */
constexpr AssertFlags fAssertSkipBreakpoint = 0x00000002;

/** Flag to indicate that the assertion should not produce any console output. When set, an
 *  assertion will not print anything to the console, but the failure count will increase.
 */
constexpr AssertFlags fAssertNoConsole = 0x00000004;

/** Flag to indicate that the assertion should not store any crash metadata. This is not
 *  recommended except for tests only.
 */
constexpr AssertFlags fAssertNoMetadata = 0x00000008;

/** Interface to provide functionality to display assertion failures in greater detail.  This
 *  provides a way to encapsulate OS specific functionality for gathering additional information,
 *  displaying dialogues, and providing additional debugging functionality.  Without this interface,
 *  assertion failure reports are only really limited to log messages and software breakpoints.
 */
struct IAssert
{
    CARB_PLUGIN_INTERFACE_EX("carb::assert::IAssert", carb_assert_IAssert_latest, carb_assert_IAssert)

    /** Sets, clears, or retrieves the default assertion handler behavioral flags.
     *
     *  @param[in] set      A mask of zero or more flags to enable.  This may be 0 to indicate
     *                      that no new flags should be set.  This is a combination of the
     *                      fAssert* flags.
     *  @param[in] clear    A mask of zero or more flags to disable.  This may be 0 to indicate
     *                      that no new flags should be cleared.  This is a combination of the
     *                      fAssert* flags.
     *  @returns The flags immediately before set/clear changes were applied.
     *
     *  @note This is always thread safe; changes are applied atomically. Also, set and clear can be 0
     *        to retrieve the current set of flags.
     */
    AssertFlags(CARB_ABI* setAssertionFlags)(AssertFlags set, AssertFlags clear);

    /** Retrieves the count of how many assertions have failed.
     *
     *  @returns The number of assertions that have failed in the calling process.
     *
     *  @remarks This retrieves the current number of assertion failures that have occurred in the
     *           calling process.  This may be combined with using the @ref fAssertSkipBreakpoint
     *           and @ref fAssertSkipDialog flags to allow certain assertions to continue in a
     *           'headless' mode whose behavior can then be monitored externally.
     */
    uint64_t(CARB_ABI* getAssertionFailureCount)();

    /** Report that an assertion failed and calls vectored assertion handlers.
     *
     *  @details See the article about @rstref{default assertion behavior <default_assertion_behavior>}.
     *  If no vectored assertion handlers are registered, the default assertion behavior occurs.
     *  @param[in] condition    The text describing the failed assertion condition.  This may not be
     *                          `nullptr`.
     *  @param[in] file         The name of the file that the assertion is in.  This may not be
     *                          `nullptr`.
     *  @param[in] func         The name of the function that the assertion is in.  This may not be
     *                          `nullptr`.
     *  @param[in] line         The line number that the assertion failed in.
     *  @param[in] fmt          A printf() style format string providing more information for the
     *                          failed assertion.  This may be `nullptr` if no additional information
     *                          is necessary or provided.
     *  @param[in] ...          Additional arguments required to fulfill the format string's needs.
     *                          Note that this is expected to be a single va_list object containing
     *                          the arguments.  For this reason, the @ref reportFailedAssertion()
     *                          variant is expected to be the one that is called instead of the 'V'
     *                          one being called directly.
     *  @returns `true` if a software breakpoint should be triggered.
     *  @returns `false` if the assertion should attempt to be ignored.
     *
     *  @remarks This handles displaying an assertion failure message to the user.  The failure
     *           message will be unconditionally written to the attached console and the debugger
     *           output window (if running on Windows under a debugger).  If no debugger is
     *           attached to the process, a simple message box will be shown to the user indicating
     *           that an assertion failure occurred and allowing them to choose how to proceed.
     *           If a debugger is attached, the default behavior is to break into the debugger
     *           unconditionally.
     *
     *  @note If running under the MSVC debugger, double clicking on the assertion failure text
     *        in the MSVC output window will jump to the source file and line containing the
     *        failed assertion.
     */
    bool(CARB_ABI* reportFailedAssertionV)(
        const char* condition, const char* file, const char* func, int32_t line, const char* fmt, ...);

#if CARB_VERSION_ATLEAST(carb_assert_IAssert, 1, 1)
    /**
     * Report that an assertion failed and calls vectored assertion handlers.
     * @details See the article about @rstref{default assertion behavior <default_assertion_behavior>}.
     * @param entry The \ref AssertEntry with information about the assertion failure.
     * @param fmt May be `nullptr`. If non-`nullptr`, a printf-style format string with additional information about the
     *   assertion failure.
     * @param ... Printf-style arguments matching format specifiers in \p fmt.
     * @retval true An assertion handler returned \ref Result::eHalt indicating that execution should be stopped.
     * @retval false An assertion handler returned \ref Result::eContinueExecution indicating that execution should be
     *   continued.
     */
    bool(CARB_ABI* reportFailedAssertion2)(const AssertEntry& entry, const char* fmt, std::va_list* ap);

    /**
     * Adds a new assertion handler.
     * @details If an assertion handler is added from an assertion handler (i.e. while handling an assertion failure)
     *   and \p first is `false`, the new assertion handler will be added to the list of handlers to be called during
     *   the current assertion handler traversal.
     * @note When assertion failure occurs, assertion handlers are called in a first-to-last order until an assertion
     *   handler returns a value other than \ref Result::eCallNext. Therefore it is possible that an assertion handler
     *   is never called.
     * @thread_safety This function is safe to call at any point by any thread, including to add assertion
     *   handlers while assertion handlers are being called.
     * @param first If `true`, the new assertion handler is pushed to the front of the list of vectored assertion
     *   handlers. Otherwise, the new assertion handler is pushed to the back of the list. When an assertion failure
     *   occurs, assertion handlers are called in first-to-last order.
     * @param handler The handler function that will be called when an assertion failure occurs.
     * @param userData An opaque information pointer that is passed to \p handler when it is called.
     * @returns A \ref Handle representing the registered assertion handler. To unregister, this can be passed to
     *   \ref unregisterAssertionHandler.
     */
    Handle(CARB_ABI* registerAssertionHandler)(bool first, VectoredAssertionHandler handler, void* userData);

    /**
     * Removes a previously-registered assertion handler.
     * @details If assertion handlers are currently being called by another thread due to an assertion failure, this
     *   function will not return until it can be guaranteed that the handler to be removed has finished being called or
     *   will not be called.
     * @thread_safety This function is safe to call at any point by any thread, including to remove either the current
     *   assertion handler (during assertion failure processing) or an upcoming assertion handler.
     * @param h The handle from a previous call to \ref registerAssertionHandler.
     * @returns `true` if the assertion handler was found and unregistered; `false` otherwise.
     */
    bool(CARB_ABI* unregisterAssertionHandler)(Handle h);
#endif

    // ^^^ API functions
    // vvv Inline helper functions

    /** Report that an assertion failed and calls vectored assertion handlers.
     *  @details See the article about @rstref{default assertion behavior <default_assertion_behavior>}.
     *  @param[in] condition    The text describing the failed assertion condition.  This may not be
     *                          `nullptr`.
     *  @param[in] file         The name of the file that the assertion is in.  This may not be
     *                          `nullptr`.
     *  @param[in] func         The name of the function that the assertion is in.  This may not be
     *                          `nullptr`.
     *  @param[in] line         The line number that the assertion failed in.
     *  @param[in] fmt          A printf() style format string providing more information for the
     *                          failed assertion.  This may be `nullptr` if no additional information
     *                          is necessary or provided.
     *  @param[in] ...          Additional arguments required to fulfill the format string's needs.
     *  @returns `true` if a software breakpoint should be triggered.
     *  @returns `false` if the assertion should attempt to be ignored.
     *
     *  @remarks This handles displaying an assertion failure message to the user.  The failure
     *           message will be unconditionally written to the attached console and the debugger
     *           output window (if running on Windows under a debugger).  If no debugger is
     *           attached to the process, a simple message box will be shown to the user indicating
     *           that an assertion failure occurred and allowing them to choose how to proceed.
     *           If a debugger is attached, the default behavior is to break into the debugger
     *           unconditionally.
     *
     *  @note If running under the MSVC debugger, double clicking on the assertion failure text
     *        in the MSVC output window will jump to the source file and line containing the
     *        failed assertion.
     *
     *  @note This variant of the function is present to allow the @p fmt parameter to default
     *        to `nullptr` so that it can be used with a version of the CARB_ASSERT() macro that
     *        doesn't pass any message.
     */
    bool reportFailedAssertion(
        const char* condition, const char* file, const char* func, int32_t line, const char* fmt = nullptr, ...)
    {
        std::va_list args;
        bool result;

        va_start(args, fmt);
        result = reportFailedAssertionV(condition, file, func, line, fmt, &args);
        va_end(args);
        return result;
    }
};

//! \cond DEV
namespace detail
{
/**
 * Assertion helper function. Do not call directly. Used by CARB_CHECK, CARB_ASSERT, etc. to dispatch assert calls.
 *
 * If \ref carb::assert::IAssert is available through \ref g_carbAssert, the
 * \ref carb::assert::IAssert::reportFailedAssertion2() function is called for assertion failures. Otherwise, the
 * assertion message is printed to stdout.
 * @param entry The \ref carb::assert::AssertEntry containing information about the assertion that failed.
 * @param fmt May be `nullptr`. If non-`nullptr`, must be a printf-style format string further describing the failed
 *   assertion.
 * @param ... Arguments corresponding to format specifiers in \p fmt.
 * @returns `true` if the result of calling vectored assertion handlers was \ref carb::assert::Result::eHalt, or `false`
 *   if the result of calling vectored assertion handlers was \ref carb::assert::Result::eContinueExecution. If no
 *   vectored assertion handlers are present, the default is to return `true`.
 */
inline CARB_NOINLINE bool dispatchAssert(const ::carb::assert::AssertEntry& entry, const char* fmt = nullptr, ...) noexcept
{
    std::va_list ap;
    va_start(ap, fmt);

    bool breakpoint = true;
    if (g_carbAssert)
    {
#if CARB_VERSION_ATLEAST(carb_assert_IAssert, 1, 1)
        breakpoint = g_carbAssert->reportFailedAssertion2(entry, fmt, &ap);
#else
        breakpoint = g_carbAssert->reportFailedAssertionV(entry.condition, entry.file, entry.func, entry.line, fmt, &ap);
#endif
    }
    else
    {
        char* buf = nullptr;
        if (fmt)
        {
            // measure string
            std::va_list ap2;
            va_copy(ap2, ap);
            auto icount = ptrdiff_t(std::vsnprintf(nullptr, 0, fmt, ap2));
            va_end(ap2);

            if (icount >= 0)
            {
                size_t count = size_t(icount);
                buf = CARB_STACK_ALLOC(char, count + 1);
                if (std::vsnprintf(buf, count + 1, fmt, ap) < 0)
                    buf = nullptr; // an error occurred, so ignore the buffer
            }
        }

        fprintf(stderr, "%s:%" PRId32 " (%s):: Assertion (%s) failed%c %s\n", entry.file, entry.line, entry.func,
                entry.condition, buf ? ':' : '.', buf ? buf : "");
    }

    va_end(ap);

    return breakpoint;
}
} // namespace detail
//! \endcond

} // namespace assert
} // namespace carb
