// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//!
//! @brief Carbonite basic defines and helper functions.
#pragma once

#include "detail/PushBadMacros.h"

#include <cinttypes>
#include <climits>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#ifndef CARB_NO_MALLOC_FREE
#    include <cstring>
#else
#    include <cstddef> // for size_t
#endif
#include <new> // for std::hardware_destructive_interference_size
#include <exception> // for std::terminate
#include <type_traits>

#include "detail/PopBadMacros.h"

/** A macro to put into `#else` branches when writing platform-specific code. */
#define CARB_UNSUPPORTED_PLATFORM() static_assert(false, "Unsupported platform!")

/** A macro to put into the `#else` branches when writing CPU architecture specific code. */
#define CARB_UNSUPPORTED_ARCHITECTURE() static_assert(false, "Unsupported architecture!")

/** A macro to put into the `#else` branches when writing compiler specific code. */
#define CARB_UNSUPPORTED_COMPILER() static_assert(false, "Unsupported compiler!")

#ifndef CARB_DEBUG
#    if defined(NDEBUG) || defined(DOXYGEN_BUILD)
//! A macro indicating whether the current compilation unit is built in debug mode. Always defined as either 0 or 1. Can
//! be overridden by defining before this file is included or by passing on the compiler command line. Defined as `0`
//! if `NDEBUG` is defined; `1` otherwise.
#        define CARB_DEBUG 0
#    else
#        define CARB_DEBUG 1
#    endif
#endif

//! A macro that can be used to indicate classes and members that participate in visualizers, such as \a carb.natvis.
//! This is a reminder that these classes, members and types will require visualizer fixup if changes are made.
#define CARB_VIZ

#ifdef DOXYGEN_BUILD
//! A macro defined as `1` if compilation is targeting Windows; `0` otherwise. Exactly one of the `CARB_PLATFORM_*`
//! macros will be set to `1`. May be overridden by defining before this file is included or by passing on the compiler
//! command line. By default, set to `1` if `_WIN32` is defined.
#    define CARB_PLATFORM_WINDOWS 0
//! A macro defined as `1` if compilation is targeting Linux; `0` otherwise. Exactly one of the `CARB_PLATFORM_*`
//! macros will be set to `1`. May be overridden by defining before this file is included or by passing on the compiler
//! command line. By default, set to `1` if `_WIN32` is not defined and `__linux__` is defined.
#    define CARB_PLATFORM_LINUX 1
//! A macro defined as `1` if compilation is targeting Mac OS; `0` otherwise. Exactly one of the `CARB_PLATFORM_*`
//! macros will be set to `1`. May be overridden by defining before this file is included or by passing on the compiler
//! command line. By default, set to `1` if `_WIN32` and `__linux__` are not defined and `__APPLE__` is defined.
#    define CARB_PLATFORM_MACOS 0
//! The name of the current platform as a string.
#    define CARB_PLATFORM_NAME
#elif defined(CARB_PLATFORM_WINDOWS) && defined(CARB_PLATFORM_LINUX) && defined(CARB_PLATFORM_MACOS)
#    if (!!CARB_PLATFORM_WINDOWS) + (!!CARB_PLATFORM_LINUX) + (!!CARB_PLATFORM_MACOS) != 1
#        define CARB_PLATFORM_WINDOWS // show previous definition
#        define CARB_PLATFORM_LINUX // show previous definition
#        define CARB_PLATFORM_MACOS // show previous definition
#        error Exactly one of CARB_PLATFORM_WINDOWS, CARB_PLATFORM_LINUX or CARB_PLATFORM_MACOS must be non-zero.
#    endif
#elif !defined(CARB_PLATFORM_WINDOWS) && !defined(CARB_PLATFORM_LINUX)
#    ifdef _WIN32
#        define CARB_PLATFORM_WINDOWS 1
#        define CARB_PLATFORM_LINUX 0
#        define CARB_PLATFORM_MACOS 0
#        define CARB_PLATFORM_NAME "windows"
#    elif defined(__linux__)
#        define CARB_PLATFORM_WINDOWS 0
#        define CARB_PLATFORM_LINUX 1
#        define CARB_PLATFORM_MACOS 0
#        define CARB_PLATFORM_NAME "linux"
#    else
CARB_UNSUPPORTED_PLATFORM();
#    endif
#else
#    error "Must define all of CARB_PLATFORM_WINDOWS, CARB_PLATFORM_LINUX and CARB_PLATFORM_MACOS or none."
#endif

#if CARB_PLATFORM_LINUX || defined(DOXYGEN_BUILD)
#    include <unistd.h> // _POSIX_VERSION comes from unistd.h

/** This is set to `_POSIX_VERSION` platforms that are mostly-compliant with POSIX.
 *  This is set to 0 on other platforms (e.g. no GNU extensions).
 */
#    define CARB_POSIX _POSIX_VERSION
#else
#    define CARB_POSIX 0
#endif

#ifndef DOXYGEN_BUILD
#    if CARB_PLATFORM_WINDOWS
#        ifndef CARB_NO_MALLOC_FREE
#            include "malloc.h"
#        endif
#        include <intrin.h>
#    elif CARB_PLATFORM_LINUX
#        include <alloca.h>
#        include <signal.h>
#        define _alloca alloca
#    endif
#endif

#ifdef CARB_POSIX
#    include <cerrno>
#endif

// Architecture defines
#ifdef DOXYGEN_BUILD
//! A macro defined as `1` if compilation is targeting the AArch64 platform; `0` otherwise. May not be overridden on the
//! command line or by defining before including this file. Set to `1` if `__aarch64__` is defined, `0` if `__x86_64__`
//! or `_M_X64` are defined, and left undefined otherwise.
#    define CARB_AARCH64 0
//! A macro defined as `1` if compilation is targeting the x86-64 platform; `0` otherwise. May not be overridden on the
//! command line or by defining before including this file. Set to `0` if `__aarch64__` is defined, `1` if `__x86_64__`
//! or `_M_X64` are defined, and left undefined otherwise.
#    define CARB_X86_64 1
//! The name of the current architecture as a string.
#    define CARB_ARCH_NAME
#elif defined(__aarch64__) /*GCC*/ || defined(_M_ARM64) /*MSVC*/
#    define CARB_AARCH64 1
#    define CARB_X86_64 0
#elif defined(__x86_64__) /*GCC*/ || defined(_M_X64) /*MSVC*/
#    define CARB_X86_64 1
#    define CARB_AARCH64 0
#endif

#if CARB_X86_64
#    define CARB_ARCH_NAME "x86_64"
#elif CARB_AARCH64
#    define CARB_ARCH_NAME "aarch64"
#endif


#ifndef CARB_PROFILING
//! When set to a non-zero value, profiling macros in \a include/carb/profiler/Profile.h will report to the profiler;
//! otherwise the profiling macros have no effect. Always set to `1` by default, but may be overridden by defining a
//! different value before including this file or by specifying a different value on the compiler command line.
#    define CARB_PROFILING 1
#endif

#ifdef DOXYGEN_BUILD
//! A macro defined as `1` if compilation is targeting the Tegra platform. By default set to `1` only if `__aarch64__`
//! and `__LINARO_RELEASE__` are defined; `0` otherwise. May be overridden by defining a different value before
//! including this file or by specifying a different value on the compiler command line.
#    define CARB_TEGRA 0
#elif !defined(CARB_TEGRA)
#    if defined(__aarch64__) && defined(__LINARO_RELEASE__)
#        define CARB_TEGRA 1
#    else
#        define CARB_TEGRA 0
#    endif
#endif

#ifdef DOXYGEN_BUILD
//! A macro defined as `1` if compilation is using Microsoft Visual C++, that is, if `_MSC_VER` is defined. May be
//! overridden by defining a different value before including this file or by specifying a different value on the
//! compiler command line, however, only one of `CARB_COMPILER_MSC` and `CARB_COMPILER_GNUC` must be set to `1`; the
//! other macro(s) must be set to `0`.
#    define CARB_COMPILER_MSC 0
//! A macro defined as `1` if compilation is using GNU C Compiler (GCC), that is, if `_MSC_VER` is not defined but
//! `__GNUC__` is defined. May be overridden by defining a different value before including this file or by specifying a
//! different value on the compiler command line, however, only one of `CARB_COMPILER_MSC` and `CARB_COMPILER_GNUC` must
//! be set to `1`; the other macro(s) must be set to `0`.
#    define CARB_COMPILER_GNUC 1
#elif defined(CARB_COMPILER_MSC) && defined(CARB_COMPILER_GNUC)
#    if (!!CARB_COMPILER_MSC) + (!!CARB_COMPILER_GNUC) != 1
#        define CARB_COMPILER_MSC // Show previous definition
#        define CARB_COMPILER_GNUC // Show previous definition
#        error Exactly one of CARB_COMPILER_MSC or CARB_COMPILER_GNUC must be non-zero.
#    endif
#elif !defined(CARB_COMPILER_MSC) && !defined(CARB_COMPILER_GNUC)
#    ifndef CARB_COMPILER_MSC
#        if defined(_MSC_VER)
#            define CARB_COMPILER_MSC 1
#            define CARB_COMPILER_GNUC 0
#        elif defined(__GNUC__)
#            define CARB_COMPILER_MSC 0
#            define CARB_COMPILER_GNUC 1
#        else
#            error "Unsupported compiler."
#        endif
#    endif
#else
#    error "Must define CARB_COMPILER_MSC and CARB_COMPILER_GNUC or neither."
#endif

#ifdef DOXYGEN_BUILD
//! A macro defined as `1` if a Clang-infrastructure toolchain is building the current file, that is, if `__clang__` is
//! defined; `0` if not. May be overridden by defining a different value before including this file or by specifying a
//! different value on the compiler command line.
//! @note It is legal to have \ref CARB_COMPILER_MSC and \ref CARB_TOOLCHAIN_CLANG both as `1` simultaneously, which
//! represents a Clang-infrastructure toolchain running in Microsoft compatibility mode.
#    define CARB_TOOLCHAIN_CLANG 0
#elif !defined(CARB_TOOLCHAIN_CLANG)
#    if defined(__clang__)
#        define CARB_TOOLCHAIN_CLANG 1
#    else
#        define CARB_TOOLCHAIN_CLANG 0
#    endif
#endif

#ifdef DOXYGEN_BUILD
//! A macro defined as `1` if the toolchain is building the current file with `-fsanitize=address`, that is, if
//! `__SANITIZE_ADDRESS__` is defined; `0` otherwise. May be overridden by defining a different value before including
//! this file or by specifying a different value on the compiler command line. Microsoft Visual Studio supports address
//! sanitizer starting with 2019 (v16.9) by specifying `/fsanitize=address` on the compiler command line.
//! See https://learn.microsoft.com/en-us/cpp/sanitizers/asan?view=msvc-160
#    define CARB_ASAN_ENABLED 0
#elif !defined(CARB_ASAN_ENABLED)
#    if defined(__has_feature)
#        define CARB_ASAN_ENABLED __has_feature(address_sanitizer)
#    elif defined(__SANITIZE_ADDRESS__)
#        define CARB_ASAN_ENABLED __SANITIZE_ADDRESS__
#    else
#        define CARB_ASAN_ENABLED 0
#    endif
#endif

#ifdef DOXYGEN_BUILD
//! A macro defined as `1` if the toolchain is building the current file with `-fsanitize=thread`, that is, if
//! `__SANITIZE_THREAD__` is defined; `0` otherwise. May be overridden by defining a different value before including
//! this file or by specifying a different value on the compiler command line. Microsoft Visual Studio does not support
//! thread sanitizer.
#    define CARB_TSAN_ENABLED 0
#elif !defined(CARB_TSAN_ENABLED)
#    if defined(__has_feature)
#        define CARB_TSAN_ENABLED __has_feature(thread_sanitizer)
#    elif defined(__SANITIZE_THREAD__)
#        define CARB_TSAN_ENABLED __SANITIZE_THREAD__
#    else
#        define CARB_TSAN_ENABLED 0
#    endif
#endif

//! De-parenthesize the contents of \c pack_. `CARB_DEPAREN((x, y))` becomes `x, y`. An unparenthesized pack will cause
//! cause a compilation failure; e.g.: `CARB_DEPAREN(foo)` will not work, but `CARB_DEPAREN((foo))` will.
#define CARB_DEPAREN(pack_) CARB_IDENTITY pack_

//! Return exactly the arguments. This is useful for expansion of the tokens.
#define CARB_IDENTITY(...) __VA_ARGS__

// Compiler specific defines. Exist for all supported compilers but may be a no-op for certain compilers.
#ifdef DOXYGEN_BUILD
//! Acts as a `char[]` with the current full function signature.
#    define CARB_PRETTY_FUNCTION "<function signature here>"
//! GCC only, defined as `__attribute__((__VA_ARGS__))`; ignored on non-GCC compilers.
#    define CARB_ATTRIBUTE(...)
//! MSVC only, defined as `__declspec(__VA_ARGS__)`; ignored on non-MSVC compilers.
#    define CARB_DECLSPEC(...)
//! MSVC only, defined as `__VA_ARGS__`; ignored on non-MSVC compilers.
#    define CARB_MSC_ONLY(...)
//! Only non-MSVC compilers, defined as `__VA_ARGS__`; ignored on MSVC.
#    define CARB_NOT_MSC(...)
//! GCC only, defined as `gnuc_only_block`; ignored on non-GCC compilers including Clang.
#    define CARB_GNUC_ONLY(...)
//! Only non-GCC compilers including Clang, defined as `__VA_ARGS__`; ignored on GCC.
#    define CARB_NOT_GNUC(...)
//! Clang only, defined as `__VA_ARGS__`; ignored on non-Clang compilers including GCC.
#    define CARB_CLANG_ONLY(...)
//! Only non-Clang compilers including GCC, defined as `__VA_ARGS__`; ignored on Clang.
#    define CARB_NOT_CLANG(...)
//! Generic pragma, only to be used for pragmas that are the same on all supported compilers.
//! @see CARB_PRAGMA_MSC
//! @see CARB_PRAGMA_GNUC
#    define CARB_PRAGMA(...)
//! MSVC only, defined as `__pragma(__VA_ARGS__)`; ignored on non-MSVC compilers.
#    define CARB_PRAGMA_MSC(...)
//! GCC only, defined as `_Pragma(__VA_ARGS__)`; ignored on non-GCC compilers.
#    define CARB_PRAGMA_GNUC(...)

//! Macro to work around Exhale tripping over `constexpr` sometimes and reporting things like:
//! `Invalid C++ declaration: Expected identifier in nested name, got keyword: static`
#    define CARB_DOC_CONSTEXPR const

//! Indicates whether exceptions are enabled for the current compilation unit. Value depends on parameters passed to the
//! compiler.
#    define CARB_EXCEPTIONS_ENABLED 1

//! Conditionally includes text only when documenting (i.e. when `DOXYGEN_BUILD` is defined).
//! @param ... The text to include if documenting
#    define CARB_DOC_ONLY(...) __VA_ARGS__

//! Declares a value or statement in a way that prevents Doxygen and Sphinx from getting confused
//! about matching symbols.  There seems to be a bug in Sphinx that prevents at least templated
//! symbols from being matched to the ones generated by Doxygen when keywords such as `decltype`
//! are used.  This is effectively the opposite operation as CARB_DOC_ONLY().
#    define CARB_NO_DOC(...)
#else
#    define CARB_DOC_CONSTEXPR constexpr
#    define CARB_DOC_ONLY(...)
#    define CARB_NO_DOC(...) __VA_ARGS__
#    if CARB_TOOLCHAIN_CLANG
#        define CARB_MSC_ONLY(...)
#        define CARB_NOT_MSC(...) __VA_ARGS__
#        define CARB_GNUC_ONLY(...)
#        define CARB_NOT_GNUC(...) __VA_ARGS__
#        define CARB_CLANG_ONLY(...) __VA_ARGS__
#        define CARB_NOT_CLANG(...)
#    elif CARB_COMPILER_MSC
#        define CARB_MSC_ONLY(...) __VA_ARGS__
#        define CARB_NOT_MSC(...)
#        define CARB_GNUC_ONLY(...)
#        define CARB_NOT_GNUC(...) __VA_ARGS__
#        define CARB_CLANG_ONLY(...)
#        define CARB_NOT_CLANG(...) __VA_ARGS__
#    elif CARB_COMPILER_GNUC
#        define CARB_MSC_ONLY(...)
#        define CARB_NOT_MSC(...) __VA_ARGS__
#        define CARB_GNUC_ONLY(...) __VA_ARGS__
#        define CARB_NOT_GNUC(...)
#        define CARB_CLANG_ONLY(...)
#        define CARB_NOT_CLANG(...) __VA_ARGS__
#    else
#        error Unsupported compiler.
#    endif
#    if CARB_COMPILER_MSC
#        define CARB_PRETTY_FUNCTION __FUNCSIG__
#        if CARB_TOOLCHAIN_CLANG
#            define CARB_ATTRIBUTE(...) __attribute__((__VA_ARGS__))
#        else
#            define CARB_ATTRIBUTE(...)
#        endif
#        define CARB_PRAGMA(...) __pragma(__VA_ARGS__)
#        define CARB_DECLSPEC(...) __declspec(__VA_ARGS__)
#        define CARB_PRAGMA_MSC(...) CARB_PRAGMA(__VA_ARGS__)
#        define CARB_PRAGMA_GNUC(...)
#        ifdef __cpp_exceptions
#            define CARB_EXCEPTIONS_ENABLED 1
#        else
#            define CARB_EXCEPTIONS_ENABLED 0
#        endif
// Other MSC-specific definitions that must exist outside of the carb namespace
extern "C" void _mm_prefetch(char const* _A, int _Sel); // From winnt.h/intrin.h

#        if defined(__INTELLISENSE__) && _MSC_VER < 1920
// See: https://stackoverflow.com/questions/61485127/including-windows-h-causes-unknown-attributeno-init-all-error
#            define no_init_all deprecated
#        endif

#    elif CARB_COMPILER_GNUC
#        define CARB_PRETTY_FUNCTION __PRETTY_FUNCTION__
#        define CARB_ATTRIBUTE(...) __attribute__((__VA_ARGS__))
#        define CARB_DECLSPEC(...)
#        define CARB_PRAGMA(...) _Pragma(__VA_ARGS__)
#        define CARB_PRAGMA_MSC(...)
#        define CARB_PRAGMA_GNUC(...) CARB_PRAGMA(__VA_ARGS__)

#        ifdef __EXCEPTIONS
#            define CARB_EXCEPTIONS_ENABLED 1
#        else
#            define CARB_EXCEPTIONS_ENABLED 0
#        endif
#    else
#        error Unsupported compiler
#    endif
#endif

//! Toolchain-independent way to check the C++ standard / version.
//! On windows, the value of __cplusplus is unreliable - it is defined if using C++, but is set to 199711L, regardless
//! of what /std:c++XX is used (unless you enable a special option, /Zc:__cplusplus):
//!     https://learn.microsoft.com/en-us/cpp/build/reference/zc-cplusplus
//! It is not a drop-in replacement for __cplusplus, as it is always defined (but may be 0)
//! ie,
//!
//!     #if defined(__cplusplus) && __cplusplus >= 201700
//!
//! becomes
//!
//!     #if CARB_CPLUSPLUS > 201700
//!
//! and
//!
//!     #ifdef __cplusplus
//!
//! becomes
//!
//!     #if CARB_CPLUSPLUS
//!
//! ...though replacing __cplusplus when it is ONLY being checked for ifdef / defined is optional, as
//! whether __cplusplus is defined at all is still reliable - it is only comparing against specific numbers that is
//! unreliable across platforms.
#ifndef CARB_CPLUSPLUS
#    if defined(__cplusplus)
#        if CARB_COMPILER_MSC && defined(_MSVC_LANG)
#            define CARB_CPLUSPLUS _MSVC_LANG
#        else
#            define CARB_CPLUSPLUS __cplusplus
#        endif
#    else
#        define CARB_CPLUSPLUS 0L
#    endif
#endif


#if defined(DOXYGEN_BUILD)
//! Indicates whether RTTI is enabled
#    define CARB_HAS_RTTI 1
#elif CARB_TOOLCHAIN_CLANG
#    if __has_feature(cxx_rtti)
#        define CARB_HAS_RTTI 1
#    endif
#elif CARB_COMPILER_MSC
#    ifdef _CPPRTTI
#        define CARB_HAS_RTTI 1
#    endif
#elif CARB_COMPILER_GNUC
#    ifdef __GXX_RTTI
#        define CARB_HAS_RTTI 1
#    endif
#endif

#ifndef CARB_HAS_RTTI
#    define CARB_HAS_RTTI 0
#endif

#if defined(DOXYGEN_BUILD) || defined(OMNI_BIND)
//! Turns optimizations off at the function level until a CARB_OPTIMIZE_ON_MSC() call is seen.
//! This must be called outside of the body of any function and will remain in effect until
//! either a CARB_OPTIMIZE_ON_MSC() call is seen or the end of the translation unit.  This
//! unfortunately needs to be a separate set of macros versus the one for GCC and Clang due
//! to the different style of disabling and enabling optimizations under the MSC compiler.
#    define CARB_OPTIMIZE_OFF_MSC()
//! Restores previous optimizations that were temporarily disable due to an earlier call to
//! CARB_OPTIMIZE_OFF_MSC().  This must be called outside the body of any function.  If this
//! call is not made, the previous optimization state will remain until the end of the current
//! translation unit.
#    define CARB_OPTIMIZE_ON_MSC()
//! Disables optimizations for the function that is tagged with this attribute.  This only
//! affects the single function that it tags.  Optimizations will be restored to the previous
//! settings for the translation unit outside of the tagged function.
#    define CARB_NO_OPTIMIZE_GNUC_CLANG()
#else
#    if CARB_COMPILER_MSC
#        define CARB_OPTIMIZE_OFF_MSC() CARB_PRAGMA_MSC(optimize("", off))
#        define CARB_OPTIMIZE_ON_MSC() CARB_PRAGMA_MSC(optimize("", on))
#        if CARB_TOOLCHAIN_CLANG
#            define CARB_NO_OPTIMIZE_GNUC_CLANG() CARB_ATTRIBUTE(optnone)
#        else
#            define CARB_NO_OPTIMIZE_GNUC_CLANG()
#        endif
#    elif CARB_TOOLCHAIN_CLANG
#        define CARB_NO_OPTIMIZE_GNUC_CLANG() CARB_ATTRIBUTE(optnone)
#        define CARB_OPTIMIZE_OFF_MSC()
#        define CARB_OPTIMIZE_ON_MSC()
#    elif CARB_COMPILER_GNUC
#        define CARB_NO_OPTIMIZE_GNUC_CLANG() CARB_ATTRIBUTE(optimize("-O0"))
#        define CARB_OPTIMIZE_OFF_MSC()
#        define CARB_OPTIMIZE_ON_MSC()
#    else
#        error Unsupported compiler
#    endif
#endif

// MSC-specific warning macros are defined only for MSC
// CARB_IGNOREWARNING_MSC_PUSH: MSVC only; pushes the warning state
// CARB_IGNOREWARNING_MSC_POP: MSVC only; pops the warning state
// CARB_IGNOREWARNING_MSC(w): MSVC only; disables the given warning number (ex: CARB_IGNOREWARNING_MSC(4505))
// CARB_IGNOREWARNING_MSC_WITH_PUSH(w): MSVC only; combines CARB_IGNOREWARNING_MSC_PUSH and CARB_IGNOREWARNING_MSC()
#if !defined(DOXYGEN_BUILD) && CARB_COMPILER_MSC
#    define CARB_IGNOREWARNING_MSC_PUSH __pragma(warning(push))
#    define CARB_IGNOREWARNING_MSC_POP __pragma(warning(pop))
#    define CARB_IGNOREWARNING_MSC(w) __pragma(warning(disable : w))
#    define CARB_IGNOREWARNING_MSC_WITH_PUSH(w)                                                                        \
        CARB_IGNOREWARNING_MSC_PUSH                                                                                    \
        CARB_IGNOREWARNING_MSC(w)
#else
//! For MSVC only, pushes the current compilation warning configuration. Defined as `__pragma(warning(push))` for MSVC
//! only; ignored by other compilers.
#    define CARB_IGNOREWARNING_MSC_PUSH
//! For MSVC only, pops the compilation warning configuration previously pushed with \ref CARB_IGNOREWARNING_MSC_PUSH,
//! overwriting the current state. Defined as `__pragma(warning(pop))` for MSVC only; ignored by other compilers.
#    define CARB_IGNOREWARNING_MSC_POP
//! For MSVC only, disables a specific compiler warning for the current compilation warning configuration. Defined as
//! `__pragma(warning(disable : <w>))` for MSVC only; ignored by other compilers.
//! @param w The warning number to disable.
#    define CARB_IGNOREWARNING_MSC(w)
//! Syntactic sugar for \ref CARB_IGNOREWARNING_MSC_PUSH followed by \ref CARB_IGNOREWARNING_MSC.
//! @param w The warning number to disable.
#    define CARB_IGNOREWARNING_MSC_WITH_PUSH(w)
#endif

// GNUC-specific helper macros are defined for GCC and Clang-infrastructure
// CARB_IGNOREWARNING_GNUC_PUSH: GCC only; pushes the warning state
// CARB_IGNOREWARNING_GNUC_POP: GCC only; pops the warning state
// CARB_IGNOREWARNING_CLANG_PUSH: Clang only; pushes the warning state
// CARB_IGNOREWARNING_CLANG_POP: Clang only; pops the warning state
// CARB_IGNOREWARNING_GNUC(w): GCC only; disables the given warning (ex: CARB_IGNOREWARNING_GNUC("-Wattributes"))
// CARB_IGNOREWARNING_GNUC_WITH_PUSH(w): GCC only; combines CARB_IGNOREWARNING_GNUC_PUSH and CARB_IGNOREWARNING_GNUC()
// CARB_IGNOREWARNING_CLANG(w): Clang only; disables the given warning (ex: CARB_IGNOREWARNING_CLANG("-Wattributes"))
// CARB_IGNOREWARNING_CLANG_WITH_PUSH(w): Clang only; combines CARB_IGNOREWARNING_CLANG_PUSH and
// CARB_IGNOREWARNING_CLANG()
#if !defined(DOXYGEN_BUILD) && (CARB_COMPILER_GNUC || CARB_TOOLCHAIN_CLANG)
#    define CARB_IGNOREWARNING_GNUC_PUSH _Pragma("GCC diagnostic push")
#    define CARB_IGNOREWARNING_GNUC_POP _Pragma("GCC diagnostic pop")
#    define INTERNAL_CARB_IGNOREWARNING_GNUC(str) _Pragma(#    str)
#    define CARB_IGNOREWARNING_GNUC(w) INTERNAL_CARB_IGNOREWARNING_GNUC(GCC diagnostic ignored w)
#    define CARB_IGNOREWARNING_GNUC_WITH_PUSH(w) CARB_IGNOREWARNING_GNUC_PUSH CARB_IGNOREWARNING_GNUC(w)
#    if CARB_TOOLCHAIN_CLANG
#        define CARB_IGNOREWARNING_CLANG_PUSH _Pragma("clang diagnostic push")
#        define CARB_IGNOREWARNING_CLANG_POP _Pragma("clang diagnostic pop")
#        define INTERNAL_CARB_IGNOREWARNING_CLANG(str) _Pragma(#        str)
#        define CARB_IGNOREWARNING_CLANG(w) INTERNAL_CARB_IGNOREWARNING_CLANG(clang diagnostic ignored w)
#        define CARB_IGNOREWARNING_CLANG_WITH_PUSH(w) CARB_IGNOREWARNING_CLANG_PUSH CARB_IGNOREWARNING_CLANG(w)
#    else
#        define CARB_IGNOREWARNING_CLANG_PUSH
#        define CARB_IGNOREWARNING_CLANG_POP
#        define CARB_IGNOREWARNING_CLANG(w)
#        define CARB_IGNOREWARNING_CLANG_WITH_PUSH(w)
#    endif
#else
//! For GCC only, pushes the current compilation warning configuration. Defined as `_Pragma("GCC diagnostic push")` for
//! GCC only; ignored by other compilers.
#    define CARB_IGNOREWARNING_GNUC_PUSH
//! For GCC only, pops the compilation warning configuration previously pushed with \ref CARB_IGNOREWARNING_GNUC_PUSH,
//! overwriting the current state. Defined as `_Pragma("GCC diagnostic pop")` for GCC only; ignored by other compilers.
#    define CARB_IGNOREWARNING_GNUC_POP
//! For Clang only, pushes the current compilation warning configuration. Defined as `_Pragma("GCC diagnostic push")`
//! for Clang only; ignored by other compilers.
#    define CARB_IGNOREWARNING_CLANG_PUSH
//! For Clang only, pops the compilation warning configuration previously pushed with \ref
//! CARB_IGNOREWARNING_CLANG_PUSH, overwriting the current state. Defined as `_Pragma("GCC diagnostic pop")` for Clang
//! only; ignored by other compilers.
#    define CARB_IGNOREWARNING_CLANG_POP
//! For GCC only, disables a specific compiler warning for the current compilation warning configuration. Defined as
//! `_Pragma("GCC diagnostic ignored <warning>")` for GCC only; ignored by other compilers.
//! @param w The warning to disable, example: `"-Wattributes"` (note that quotes must be specified)
#    define CARB_IGNOREWARNING_GNUC(w)
//! Syntactic sugar for \ref CARB_IGNOREWARNING_GNUC_PUSH followed by \ref CARB_IGNOREWARNING_GNUC.
//! @param w The warning to disable, example: `"-Wattributes"` (note that quotes must be specified)
#    define CARB_IGNOREWARNING_GNUC_WITH_PUSH(w)
//! For Clang only, disables a specific compiler warning for the current compilation warning configuration. Defined as
//! `_Pragma("GCC diagnostic ignored <warning>")` for Clang only; ignored by other compilers.
//! @param w The warning to disable, example: `"-Wattributes"` (note that quotes must be specified)
#    define CARB_IGNOREWARNING_CLANG(w)
//! Syntactic sugar for \ref CARB_IGNOREWARNING_CLANG_PUSH followed by \ref CARB_IGNOREWARNING_CLANG.
//! @param w The warning to disable, example: `"-Wattributes"` (note that quotes must be specified)
#    define CARB_IGNOREWARNING_CLANG_WITH_PUSH(w)
#endif

#if defined(__cplusplus) || defined(DOXYGEN_BUILD)
//! Defined as `extern "C"` for C++ compilation, that is, when `__cplusplus` is defined; empty define otherwise.
#    define CARB_EXTERN_C extern "C"
#else
#    define CARB_EXTERN_C
#endif

//! Grants a function external linkage in a dynamic library or executable.
//!
//! On MSVC, `extern "C" __declspec(dllexport)`. On GCC/Clang: `extern "C" __attribute__((visibility("default")))`.
//!
//! This macro is always defined as such. If conditional import/export is desired, use \ref CARB_DYNAMICLINK.
#define CARB_EXPORT CARB_EXTERN_C CARB_DECLSPEC(dllexport) CARB_ATTRIBUTE(visibility("default"))

//! Imports a function with external linkage from a shared object or DLL.
//!
//! On all compilers: `extern "C"`
//!
//! \note on Windows platforms we do not use `__declspec(dllimport)` as it is <a
//! href="https://learn.microsoft.com/en-us/cpp/build/importing-into-an-application-using-declspec-dllimport?view=msvc-160">optional</a>
//! and can lead to linker warning <a
//! href="https://learn.microsoft.com/en-us/cpp/error-messages/tool-errors/linker-tools-warning-lnk4217?view=msvc-160">LNK4217</a>.
#define CARB_IMPORT CARB_EXTERN_C

// For documentation only
#ifdef DOXYGEN_BUILD
//! Instructs CARB_DYNAMICLINK to export instead of import
//!
//! \warning This symbol is not defined anywhere; it is up to the user of \ref CARB_DYNAMICLINK to define this in the
//! compilation unit that exports the symbols. **This must be defined before carb/Defines.h is included.**
//!
//! \see CARB_DYNAMICLINK
#    define CARB_EXPORTS
#endif

#if defined(CARB_EXPORTS) || defined(DOXYGEN_BUILD)
//! Conditional (import/export) dynamic linking.
//!
//! If and only if \ref CARB_EXPORTS is defined before including this file, this will match \ref CARB_EXPORT and
//! function as granting a function external linkage. If `CARB_EXPORTS` is not defined, this functions as merely
//! declaring the function as `extern "C"` so that it can be imported.
#    define CARB_DYNAMICLINK CARB_EXPORT
#else
#    define CARB_DYNAMICLINK CARB_IMPORT
#endif

//! Defined as `__cdecl` on Windows and an empty define on Linux. Used to explicitly state ABI calling convention for
//! API functions. Update: Deprecated. Define left for compatibility.
#define CARB_ABI

#if CARB_CPLUSPLUS < 201700L && !defined(DOXYGEN_BUILD)
#    error "Carbonite requires C++17 or later."
#endif

//! Always defined as `1` because the current compiler supports C++14
#define CARB_HAS_CPP14 1

//! Always defined as `1` because the current compiler supports C++17
#define CARB_HAS_CPP17 1

//! Defined as `constexpr` because the current compiler supports C++17
#define CARB_CPP17_CONSTEXPR constexpr

#if CARB_CPLUSPLUS >= 202000L || defined(DOXYGEN_BUILD)
//! Defined as `1` if the current compiler supports C++20; `0` otherwise.
#    define CARB_HAS_CPP20 1
#else
#    define CARB_HAS_CPP20 0
#endif

#ifndef DOXYGEN_BUILD
#    if defined(__has_cpp_attribute) // C++20
#        define CARBLOCAL_HAS_NODISCARD_MSG (__has_cpp_attribute(nodiscard) >= 201907L)
#        define CARBLOCAL_HAS_LIKELY (__has_cpp_attribute(likely) >= 201803L)
#        define CARBLOCAL_HAS_UNLIKELY (__has_cpp_attribute(unlikely) >= 201803L)
#        define CARBLOCAL_HAS_NO_UNIQUE_ADDRESS (__has_cpp_attribute(no_unique_address) >= 201803L)
#    else
#        define CARBLOCAL_HAS_NODISCARD_MSG 0
#        define CARBLOCAL_HAS_LIKELY 0
#        define CARBLOCAL_HAS_UNLIKELY 0
#        define CARBLOCAL_HAS_NO_UNIQUE_ADDRESS 0
#    endif
#    if defined(__has_builtin)
#        define CARBLOCAL_HAS_BUILTIN_DEBUGTRAP (__has_builtin(__builtin_debugtrap))
#    else
#        define CARBLOCAL_HAS_BUILTIN_DEBUGTRAP 0
#    endif
#endif

// [[nodiscard]]
//! Defined as `[[nodiscard]]` because the current compiler supports C++17
#define CARB_NODISCARD [[nodiscard]]

//! Defined as `[[nodiscard]]` because the current compiler supports C++17
#define CARB_NODISCARD_TYPE [[nodiscard]]

// [[nodiscard(msg)]]
#if (CARB_HAS_CPP20 && CARBLOCAL_HAS_NODISCARD_MSG) || defined(DOXYGEN_BUILD)
//! Defined as `[[nodiscard(msg)]]` if the current compiler supports C++20; falls back to `[[nodiscard]]` without the
//! message pre-C++20.
#    define CARB_NODISCARD_MSG(msg) [[nodiscard(msg)]]
//! Defined as `[[nodiscard(msg)]]` if the current compiler supports C++20; falls back to \c CARB_NODISCARD_TYPE without
//! the message pre-C++20.
#    define CARB_NODISCARD_TYPE_MSG(msg) [[nodiscard(msg)]]
#else
#    define CARB_NODISCARD_MSG(msg) [[nodiscard]]
#    define CARB_NODISCARD_TYPE_MSG(msg) CARB_NODISCARD_TYPE
#endif

// [[fallthrough]]
//! Defined as `[[fallthrough]]` because the current compiler supports C++17
#define CARB_FALLTHROUGH [[fallthrough]]

// [[maybe_unused]]
//! Defined as `[[maybe_unused]]` because the current compiler supports C++17
#define CARB_MAYBE_UNUSED [[maybe_unused]]

// [[likely]] / [[unlikely]]
#if (CARB_HAS_CPP20 && CARBLOCAL_HAS_LIKELY) || defined(DOXYGEN_BUILD)
//! Defined as `[[likely]]` if the current compiler supports C++20 (that is, \ref CARB_HAS_CPP20 is non-zero) and the
//! compiler reports the presence of the `likely` attributes.
#    define CARB_CPP20_LIKELY [[likely]]
#else
#    define CARB_CPP20_LIKELY
#endif

#if (CARB_HAS_CPP20 && CARBLOCAL_HAS_UNLIKELY) || defined(DOXYGEN_BUILD)
//! Defined as `[[unlikely]]` if the current compiler supports C++20 (that is, \ref CARB_HAS_CPP20 is non-zero) and the
//! compiler reports the presence of the `unlikely` attributes.
#    define CARB_CPP20_UNLIKELY [[unlikely]]
#else
#    define CARB_CPP20_UNLIKELY
#endif

#if CARB_COMPILER_GNUC || defined(DOXYGEN_BUILD)
//! If the current compiler is GCC, defined as `__builtin_expect(!!(<expr>), 1)`. Otherwise, defined as `(!!(<expr>))`.
//! @param expr The expression to evaluate, optimized with a `true` outcome likely and expected.
//! @returns The boolean result of \p expr.
#    define CARB_LIKELY(expr) __builtin_expect(!!(expr), 1)
//! If the current compiler is GCC, defined as `__builtin_expect(!!(<expr>), 0)`. Otherwise, defined as `(!!(<expr>))`.
//! @param expr The expression to evaluate, optimized with a `false` outcome likely and expected.
//! @returns The boolean result of \p expr.
#    define CARB_UNLIKELY(expr) __builtin_expect(!!(expr), 0)
#else // not supported
#    define CARB_LIKELY(expr) (!!(expr))
#    define CARB_UNLIKELY(expr) (!!(expr))
#endif

//! A helper for using both the \ref CARB_LIKELY macro as well as the \ref CARB_CPP20_LIKELY macro.
#define CARB_LIKELY_IF(...)                                                                                            \
    if (CARB_LIKELY(__VA_ARGS__))                                                                                      \
    CARB_CPP20_LIKELY

//! A helper for using both the \ref CARB_UNLIKELY macro as well as the \ref CARB_CPP20_UNLIKELY macro.
#define CARB_UNLIKELY_IF(...)                                                                                          \
    if (CARB_UNLIKELY(__VA_ARGS__))                                                                                    \
    CARB_CPP20_UNLIKELY

// [[no_unique_address]]
#if (CARB_HAS_CPP20 && CARBLOCAL_HAS_NO_UNIQUE_ADDRESS) || defined(DOXYGEN_BUILD)
//! Defined as `[[no_unique_address]]` if the current compiler supports C++20; empty otherwise.
#    define CARB_NO_UNIQUE_ADDRESS [[no_unique_address]]
#else // not supported
#    define CARB_NO_UNIQUE_ADDRESS
#endif

//! Syntactic sugar for `CARB_ATTRIBUTE(visibility("hidden"))`; ignored on compilers other than GCC.
#define CARB_HIDDEN CARB_ATTRIBUTE(visibility("hidden"))

//! Syntactic sugar for `CARB_DECLSPEC(selectany) CARB_ATTRIBUTE(weak)`, used to enable weak linking.
#define CARB_WEAKLINK CARB_DECLSPEC(selectany) CARB_ATTRIBUTE(weak)

// constexpr in CPP20, but not before
#if (CARB_HAS_CPP20 && __cpp_constexpr >= 201907L) || defined(DOXYGEN_BUILD)
//! Defined as `constexpr` if the current compiler supports C++20; empty otherwise.
#    define CARB_CPP20_CONSTEXPR constexpr
#else
#    define CARB_CPP20_CONSTEXPR
#endif

#ifdef DOXYGEN_BUILD
//! \brief Used to break into the debugger.
//! \details When compiled with Microsoft Visual C++, this is `__debugbreak()`.
//! If a compiler has `__builtin_debugtrap()` (i.e. Clang), then that is used.
//! On GCC with x86-64 architecture, the `int3` assembly instruction is used.
//! Otherwise, POSIX platforms will use `raise(SIGTRAP)`.
#    define CARB_BREAK_POINT()
#elif CARB_COMPILER_MSC && !CARB_TOOLCHAIN_CLANG
#    define CARB_BREAK_POINT() ::__debugbreak()
#elif CARBLOCAL_HAS_BUILTIN_DEBUGTRAP
#    define CARB_BREAK_POINT() __builtin_debugtrap()
#elif CARB_COMPILER_GNUC && CARB_X86_64
// clang-format off
#    define CARB_BREAK_POINT() []{ __asm__ __volatile__ ("int3"); }()
// clang-format on
#elif CARB_POSIX
#    include <csignal>
#    define CARB_BREAK_POINT() ::raise(SIGTRAP)
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

//! \cond DEV
namespace carb::detail
{
// clang-format off
#define C(a) (unsigned char)(0x##a)
constexpr unsigned char lowerTable[256] = {
    C(00), C(01), C(02), C(03), C(04), C(05), C(06), C(07), C(08), C(09), C(0A), C(0B), C(0C), C(0D), C(0E), C(0F),
    C(10), C(11), C(12), C(13), C(14), C(15), C(16), C(17), C(18), C(19), C(1A), C(1B), C(1C), C(1D), C(1E), C(1F),
    C(20), C(21), C(22), C(23), C(24), C(25), C(26), C(27), C(28), C(29), C(2A), C(2B), C(2C), C(2D), C(2E), C(2F),
    C(30), C(31), C(32), C(33), C(34), C(35), C(36), C(37), C(38), C(39), C(3A), C(3B), C(3C), C(3D), C(3E), C(3F),
    C(40),

           // [0x41, 0x5A] -> [0x61, 0x7A]
           C(61), C(62), C(63), C(64), C(65), C(66), C(67), C(68), C(69), C(6A), C(6B), C(6C), C(6D), C(6E), C(6F),
    C(70), C(71), C(72), C(73), C(74), C(75), C(76), C(77), C(78), C(79), C(7A),

                                                                                 C(5B), C(5C), C(5D), C(5E), C(5F),
    C(60), C(61), C(62), C(63), C(64), C(65), C(66), C(67), C(68), C(69), C(6A), C(6B), C(6C), C(6D), C(6E), C(6F),
    C(70), C(71), C(72), C(73), C(74), C(75), C(76), C(77), C(78), C(79), C(7A), C(7B), C(7C), C(7D), C(7E), C(7F),
    C(80), C(81), C(82), C(83), C(84), C(85), C(86), C(87), C(88), C(89), C(8A), C(8B), C(8C), C(8D), C(8E), C(8F),
    C(90), C(91), C(92), C(93), C(94), C(95), C(96), C(97), C(98), C(99), C(9A), C(9B), C(9C), C(9D), C(9E), C(9F),
    C(A0), C(A1), C(A2), C(A3), C(A4), C(A5), C(A6), C(A7), C(A8), C(A9), C(AA), C(AB), C(AC), C(AD), C(AE), C(AF),
    C(B0), C(B1), C(B2), C(B3), C(B4), C(B5), C(B6), C(B7), C(B8), C(B9), C(BA), C(BB), C(BC), C(BD), C(BE), C(BF),
    C(C0), C(C1), C(C2), C(C3), C(C4), C(C5), C(C6), C(C7), C(C8), C(C9), C(CA), C(CB), C(CC), C(CD), C(CE), C(CF),
    C(D0), C(D1), C(D2), C(D3), C(D4), C(D5), C(D6), C(D7), C(D8), C(D9), C(DA), C(DB), C(DC), C(DD), C(DE), C(DF),
    C(E0), C(E1), C(E2), C(E3), C(E4), C(E5), C(E6), C(E7), C(E8), C(E9), C(EA), C(EB), C(EC), C(ED), C(EE), C(EF),
    C(F0), C(F1), C(F2), C(F3), C(F4), C(F5), C(F6), C(F7), C(F8), C(F9), C(FA), C(FB), C(FC), C(FD), C(FE), C(FF),
};
constexpr unsigned char upperTable[256] = {
    C(00), C(01), C(02), C(03), C(04), C(05), C(06), C(07), C(08), C(09), C(0A), C(0B), C(0C), C(0D), C(0E), C(0F),
    C(10), C(11), C(12), C(13), C(14), C(15), C(16), C(17), C(18), C(19), C(1A), C(1B), C(1C), C(1D), C(1E), C(1F),
    C(20), C(21), C(22), C(23), C(24), C(25), C(26), C(27), C(28), C(29), C(2A), C(2B), C(2C), C(2D), C(2E), C(2F),
    C(30), C(31), C(32), C(33), C(34), C(35), C(36), C(37), C(38), C(39), C(3A), C(3B), C(3C), C(3D), C(3E), C(3F),
    C(40), C(41), C(42), C(43), C(44), C(45), C(46), C(47), C(48), C(49), C(4A), C(4B), C(4C), C(4D), C(4E), C(4F),
    C(50), C(51), C(52), C(53), C(54), C(55), C(56), C(57), C(58), C(59), C(5A), C(5B), C(5C), C(5D), C(5E), C(5F),
    C(60),

           // [0x61, 0x7A] -> [0x41, 0x5A]
           C(41), C(42), C(43), C(44), C(45), C(46), C(47), C(48), C(49), C(4A), C(4B), C(4C), C(4D), C(4E), C(4F),
    C(50), C(51), C(52), C(53), C(54), C(55), C(56), C(57), C(58), C(59), C(5A),

                                                                                 C(7B), C(7C), C(7D), C(7E), C(7F),
    C(80), C(81), C(82), C(83), C(84), C(85), C(86), C(87), C(88), C(89), C(8A), C(8B), C(8C), C(8D), C(8E), C(8F),
    C(90), C(91), C(92), C(93), C(94), C(95), C(96), C(97), C(98), C(99), C(9A), C(9B), C(9C), C(9D), C(9E), C(9F),
    C(A0), C(A1), C(A2), C(A3), C(A4), C(A5), C(A6), C(A7), C(A8), C(A9), C(AA), C(AB), C(AC), C(AD), C(AE), C(AF),
    C(B0), C(B1), C(B2), C(B3), C(B4), C(B5), C(B6), C(B7), C(B8), C(B9), C(BA), C(BB), C(BC), C(BD), C(BE), C(BF),
    C(C0), C(C1), C(C2), C(C3), C(C4), C(C5), C(C6), C(C7), C(C8), C(C9), C(CA), C(CB), C(CC), C(CD), C(CE), C(CF),
    C(D0), C(D1), C(D2), C(D3), C(D4), C(D5), C(D6), C(D7), C(D8), C(D9), C(DA), C(DB), C(DC), C(DD), C(DE), C(DF),
    C(E0), C(E1), C(E2), C(E3), C(E4), C(E5), C(E6), C(E7), C(E8), C(E9), C(EA), C(EB), C(EC), C(ED), C(EE), C(EF),
    C(F0), C(F1), C(F2), C(F3), C(F4), C(F5), C(F6), C(F7), C(F8), C(F9), C(FA), C(FB), C(FC), C(FD), C(FE), C(FF),
};
#undef C
// clang-format on
} // namespace carb::detail
//! \endcond

#ifdef DOXYGEN_BUILD
//! Indicates whether asserts are enabled. May be overridden by defining this before including this file. By default, is
//! set to `CARB_DEBUG`. If this is overridden to a non-zero value and `CARB_ASSERT` is not defined,
//! `CARB_ASSERT` will receive the default implementation.
//! See @rstref{the main assert article <carb_asserts>}.
#    define CARB_ASSERT_ENABLED CARB_DEBUG
//! Indicates whether runtime checking is enabled. May be overridden by defining this before including this file. If not
//! overridden, this is set to `1` always. If this is a non-zero value and `CARB_CHECK` is not defined,
//! `CARB_CHECK` will receive the default implementation.
//! See @rstref{the main assert article <carb_asserts>}.
#    define CARB_CHECK_ENABLED 1
//! Indicates whether release asserts are enabled. May be overridden by defining this before including this file. If not
//! overridden, this is set to `1` always. If this is a non-zero value and `CARB_RELEASE_ASSERT` is not defined,
//! `CARB_RELEASE_ASSERT` will receive the default implementation.
//! See @rstref{the main assert article <carb_asserts>}.
#    define CARB_RELEASE_ASSERT_ENABLED 1
//! Indicates whether fatal condition checks are enabled. Always `1` since fatal condition checks are always enabled.
//! See @rstref{the main assert article <carb_asserts>}.
#    define CARB_FATAL_UNLESS_ENABLED 1
//! Performs an assertion check, by default for debug builds only.
//! @warning The \p cond should have no side effects! Asserts can be disabled which will cause \p cond to not be
//! evaluated.
//! @note The \ref CARB_ASSERT_ENABLED define can be used to determine if asserts are enabled, or to cause them to be
//! enabled or disabled by defining it before including this file.
//!
//! The implementation can be overridden on the command line, or by defining to a different implementation before
//! including this file.
//!
//! When \p cond is evaluated as `false`, the assertion is dispatched. If \ref g_carbAssert is non-`nullptr`, the
//! \ref carb::assert::IAssert::reportFailedAssertion2 function is called with \ref carb::assert::Type::eAssert. This
//! causes vectored assertion handlers to run and, depending on their result, execution may continue or a software
//! breakpoint is triggered. If \ref g_carbAssert is `nullptr`, the assertion information is printed to `stderr` and a
//! software breakpoint is triggered.
//!
//! See @rstref{the main assert article <carb_asserts>}.
//! @param cond A condition that is evaluated for a boolean result. If the condition produces \c false, the assert
//! handler is notified.
//! @param ... An optional printf-style format string and variadic parameters.
#    define CARB_ASSERT(cond, ...) ((void)0)
//! Performs a runtime check assertion, by default for both debug and release builds.
//! @warning The \p cond should have no side effects! Asserts can be disabled which will cause \p cond to not be
//! evaluated.
//! @note The \ref CARB_CHECK_ENABLED define can be used to determine if runtime check asserts are enabled, or to cause
//! them to be enabled or disabled by defining it before including this file.
//!
//! The implementation can be overridden on the command line, or by defining to a different implementation before
//! including this file.
//!
//! When \p cond is evaluated as `false`, the assertion is dispatched. If \ref g_carbAssert is non-`nullptr`, the
//! \ref carb::assert::IAssert::reportFailedAssertion2 function is called with \ref carb::assert::Type::eCheck. This
//! causes vectored assertion handlers to run and, depending on their result, execution may continue or a software
//! breakpoint is triggered. If \ref g_carbAssert is `nullptr`, the assertion information is printed to `stderr` and a
//! software breakpoint is triggered.
//!
//! See @rstref{the main assert article <carb_asserts>}.
//! @param cond A condition that is evaluated for a boolean result. If the condition produces \c false, the assert
//! handler is notified.
//! @param ... An optional printf-style format string and variadic parameters.
#    define CARB_CHECK(cond, ...) ((void)0)
//! Performs a runtime assertion, by default for both debug and release builds.
//! @warning The \p cond should have no side effects! Asserts can be disabled which will cause \p cond to not be
//! evaluated.
//! @note The \ref CARB_RELEASE_ASSERT_ENABLED define can be used to determine if runtime check asserts are enabled, or
//! to cause them to be enabled or disabled by defining it before including this file.
//!
//! The implementation can be overridden on the command line, or by defining to a different implementation before
//! including this file.
//!
//! When \p cond is evaluated as `false`, the assertion is dispatched. If \ref g_carbAssert is non-`nullptr`, the
//! \ref carb::assert::IAssert::reportFailedAssertion2 function is called with \ref carb::assert::Type::eReleaseAssert.
//! This causes vectored assertion handlers to run and, depending on their result, execution may continue or a software
//! breakpoint is triggered. If \ref g_carbAssert is `nullptr`, the assertion information is printed to `stderr` and a
//! software breakpoint is triggered.
//!
//! See @rstref{the main assert article <carb_asserts>}.
//! @param cond A condition that is evaluated for a boolean result. If the condition produces \c false, the assert
//! handler is notified.
//! @param ... An optional printf-style format string and variadic parameters.
#    define CARB_RELEASE_ASSERT(cond, ...) ((void)0)
//! Terminates the application if a check fails.
//!
//! The implementation can be overridden on the command line, or by defining to a different implementation before
//! including this file.
//!
//! When \p cond is evaluated as `false`, the assertion is dispatched. If \ref g_carbAssert is non-`nullptr`, the
//! \ref carb::assert::IAssert::reportFailedAssertion2 function is called with \ref carb::assert::Type::eFatal. This
//! causes vectored assertion handlers to run. If \ref g_carbAssert is `nullptr`, the assertion information is printed
//! to `stderr`. **If the assert handler returns, `std::terminate()` is called**.
//!
//! See @rstref{the main assert article <carb_asserts>}.
//! @warning Undefined behavior occurs if an overriding implementation of `CARB_FATAL_UNLESS` allows continued execution
//!   when \p cond returns false.
//! @param cond A condition that is evaluated for a boolean result. If the condition produces \c false, the assert
//! handler is notified. If the assert handler returns, `std::terminate()` is called.
//! @param fmt An explanation of the failure is required. This is a printf-style format string.
//! @param ... printf-style variadic parameters
#    define CARB_FATAL_UNLESS(cond, fmt, ...) (!(cond) ? (std::terminate(), false) : true)
#else
/* main assertion test entry point.  This is implemented as a single conditional statement to
 * ensure that the assertion failure breakpoint occurs on the same line of code as the assertion
 * test itself. CARB_CHECK() exists in release and debug, and CARB_ASSERT() is debug-only.
 */
// example-begin CARB_IMPL_ASSERT
#    define CARB_IMPL_ASSERT(cond, type, ...)                                                                          \
        (CARB_LIKELY(cond) ||                                                                                          \
         ![&](const char* funcname__, ...) CARB_NOINLINE {                                                             \
             return ::carb::assert::detail::dispatchAssert(                                                            \
                 ::carb::assert::AssertEntry{ (type), #cond, funcname__, __FILE__, __LINE__ }, ##__VA_ARGS__);         \
         }(CARB_PRETTY_FUNCTION) ||                                                                                    \
         (CARB_BREAK_POINT(), false))

// Use as:
// #define CARB_ASSERT(cond, ...) CARB_IMPL_ASSERT(cond, ::carb::assert::Type::eAssert, ##__VA_ARGS__)
// #define CARB_CHECK(cond, ...) CARB_IMPL_ASSERT(cond, ::carb::assert::Type::eCheck, ##__VA_ARGS__)
// #define CARB_RELEASE_ASSERT(cond, ...) CARB_IMPL_ASSERT(cond, ::carb::assert::Type::eReleaseAssert, ##__VA_ARGS__)

// NOTE: Ideal implementation is below, but this requires C++23 for static in constexpr functions where it might be used
#    if 0
#        define CARB_IMPL_ASSERT(cond, type, ...)                                                                      \
            do                                                                                                         \
            {                                                                                                          \
                CARB_LIKELY_IF(cond) break;                                                                            \
                constexpr static ::carb::assert::AssertEntry implAssertEntry{ (type), #cond, CARB_PRETTY_FUNCTION,     \
                                                                              __FILE__, __LINE__ };                    \
                if (::carb::assert::detail::dispatchAssert(&implAssertEntry, ##__VA_ARGS__))                           \
                    CARB_BREAK_POINT();                                                                                \
            } while (false)
#    endif
// example-end CARB_IMPL_ASSERT


#    ifndef CARB_ASSERT
#        ifndef CARB_ASSERT_ENABLED
#            define CARB_ASSERT_ENABLED CARB_DEBUG
#        endif
#        if CARB_ASSERT_ENABLED
#            define CARB_ASSERT(cond, ...) CARB_IMPL_ASSERT(cond, ::carb::assert::Type::eAssert, ##__VA_ARGS__)
#        else
#            define CARB_ASSERT(cond, ...) ((void)0)
#        endif
#    else
// CARB_ASSERT was already defined
#        ifndef CARB_ASSERT_ENABLED
#            define CARB_ASSERT /* cause an error showing where it was already defined */
#            error CARB_ASSERT_ENABLED must also be defined if CARB_ASSERT is pre-defined!
#        endif
#    endif
#endif

#ifndef CARB_CHECK
#    ifndef CARB_CHECK_ENABLED
#        define CARB_CHECK_ENABLED 1
#    endif
#    if CARB_CHECK_ENABLED
#        define CARB_CHECK(cond, ...) CARB_IMPL_ASSERT(cond, ::carb::assert::Type::eCheck, ##__VA_ARGS__)
#    else
#        define CARB_CHECK(...) ((void)0)
#    endif
#else
// CARB_CHECK was already defined
#    ifndef CARB_CHECK_ENABLED
#        define CARB_CHECK /* cause an error showing where it was already defined */
#        error CARB_CHECK_ENABLED must also be defined if CARB_CHECK is pre-defined!
#    endif
#endif

#ifndef CARB_RELEASE_ASSERT
#    ifndef CARB_RELEASE_ASSERT_ENABLED
#        define CARB_RELEASE_ASSERT_ENABLED 1
#    endif
#    if CARB_RELEASE_ASSERT_ENABLED
#        define CARB_RELEASE_ASSERT(cond, ...)                                                                         \
            CARB_IMPL_ASSERT(cond, ::carb::assert::Type::eReleaseAssert, ##__VA_ARGS__)
#    else
#        define CARB_RELEASE_ASSERT(...) ((void)0)
#    endif
#else
// CARB_RELEASE_ASSERT was already defined
#    ifndef CARB_RELEASE_ASSERT_ENABLED
#        define CARB_RELEASE_ASSERT /* cause an error showing where it was already defined */
#        error CARB_RELEASE_ASSERT_ENABLED must also be defined if CARB_RELEASE_ASSERT is pre-defined!
#    endif
#endif

#define CARB_FATAL_UNLESS_ENABLED 1
#ifndef CARB_FATAL_UNLESS
// example-begin CARB_FATAL_UNLESS
#    define CARB_FATAL_UNLESS(cond, fmt, ...)                                                                          \
        (CARB_LIKELY(cond) ||                                                                                          \
            ([&](const char* funcname__, ...) CARB_NOINLINE {                                                          \
                if (false)                                                                                             \
                    ::printf(fmt, ##__VA_ARGS__);                                                                      \
                ::carb::assert::detail::dispatchAssert(::carb::assert::AssertEntry{ ::carb::assert::Type::eFatal,      \
                    #cond, funcname__, __FILE__, __LINE__ }, fmt, ##__VA_ARGS__);                                      \
             }(CARB_PRETTY_FUNCTION), std::terminate(), false))
// example-end CARB_FATAL_UNLESS
#endif

//! A helper to determine if the size and alignment of two given structures match, causing a static assert if unmatched.
//! @param A One type to compare.
//! @param B Another type to compare.
#define CARB_ASSERT_STRUCTS_MATCH(A, B)                                                                                \
    static_assert(                                                                                                     \
        sizeof(A) == sizeof(B) && alignof(A) == alignof(B), "Size or alignment mismatch between " #A " and " #B ".")

//! A helper to determine if member `A.a` matches the offset and size of `B.b`, causing a static assert if unmatched.
//! @param A The struct containing public member \p a.
//! @param a A public member of \p A.
//! @param B The struct containing public member \p b.
//! @param b A public member of \p B.
#define CARB_ASSERT_MEMBERS_MATCH(A, a, B, b)                                                                          \
    static_assert(offsetof(A, a) == offsetof(B, b) && sizeof(A::a) == sizeof(B::b),                                    \
                  "Offset or size mismatch between members " #a " of " #A " and " #b " of " #B ".")

//! The maximum value that can be represented by `uint16_t`.
#define CARB_UINT16_MAX UINT16_MAX
//! The maximum value that can be represented by `uint32_t`.
#define CARB_UINT32_MAX UINT32_MAX
//! The maximum value that can be represented by `uint64_t`.
#define CARB_UINT64_MAX UINT64_MAX
//! The maximum value that can be represented by `unsigned long long`.
#define CARB_ULLONG_MAX ULLONG_MAX
//! The maximum value that can be represented by `unsigned short`.
#define CARB_USHRT_MAX USHRT_MAX
//! The maximum value that can be represented by `float`.
#define CARB_FLOAT_MAX 3.402823466e+38F

//! A macro that returns the least of two values.
//! @warning This macro will evaluate parameters more than once! Consider using carb_min() or `std::min`.
//! @param a The first value.
//! @param b The second value.
//! @returns The least of \p a or \p b. If the values are equal \p b will be returned.
#define CARB_MIN(a, b) (((a) < (b)) ? (a) : (b))

//! A macro the returns the largest of two values.
//! @warning This macro will evaluate parameters more than once! Consider using carb_max() or `std::max`.
//! @param a The first value.
//! @param b The second value.
//! @returns The largest of \p a or \p b. If the values are equal \p b will be returned.
#define CARB_MAX(a, b) (((a) > (b)) ? (a) : (b))

//! A macro the returns the largest of two values.
//! @warning This macro will evaluate parameters more than once! Consider using `std::clamp` or an inline function
//! instead.
//! @param x The value to clamp.
//! @param lo The lowest acceptable value. This will be returned if `x < lo`.
//! @param hi The highest acceptable value. This will be returned if `x > hi`.
//! @return \p lo if \p x is less than \p lo; \p hi if \p x is greater than \p hi; \p x otherwise.
#define CARB_CLAMP(x, lo, hi) (((x) < (lo)) ? (lo) : (((x) > (hi)) ? (hi) : (x)))

//! Rounds a given value to the next highest multiple of another given value.
//! @warning This macro will evaluate the \p to parameter more than once! Consider using an inline function instead.
//! @param value The value to round.
//! @param to The multiple to round to.
//! @returns \p value rounded up to the next multiple of \p to.
#define CARB_ROUNDUP(value, to) ((((value) + (to)-1) / (to)) * (to))

//! \cond DEV
// CARB_JOIN will join together `a` and `b` and also work properly if either parameter is another macro like __LINE__.
// This requires two macros since the preprocessor will only recurse macro expansion if # and ## are not present.
#define __CARB_JOIN(a, b) a##b
//! \endcond

//! A macro that joins two parts to create one symbol allowing one or more parameters to be a macro, as if by the `##`
//! preprocessor operator.
//! Example: `CARB_JOIN(test, __LINE__)` on line 579 produces `test579`.
//! @param a The first name to join.
//! @param b The second name to join.
#define CARB_JOIN(a, b) __CARB_JOIN(a, b)

//! A macro that deletes the copy-construct and copy-assign functions for the given classname.
//! @param classname The class to delete copy functions for.
#define CARB_PREVENT_COPY(classname)                                                                                   \
    classname(const classname&) = delete; /**< @private */                                                             \
    classname& operator=(const classname&) = delete /**< @private */

//! A macro that deletes the move-construct and move-assign functions for the given classname.
//! @param classname The class to delete move functions for.
#define CARB_PREVENT_MOVE(classname)                                                                                   \
    classname(classname&&) = delete; /**< @private */                                                                  \
    classname& operator=(classname&&) = delete /**< @private */

//! Syntactic sugar for both \ref CARB_PREVENT_COPY and \ref CARB_PREVENT_MOVE.
//! @param classname The class to delete copy and move functions for.
#define CARB_PREVENT_COPY_AND_MOVE(classname)                                                                          \
    CARB_PREVENT_COPY(classname);                                                                                      \
    CARB_PREVENT_MOVE(classname)

#if defined(__COUNTER__) || defined(DOXYGEN_BUILD)
//! A helper macro that appends a number to the given name to create a unique name.
//! @param str The name to decorate.
#    define CARB_ANONYMOUS_VAR(str) CARB_JOIN(str, __COUNTER__)
#else
#    define CARB_ANONYMOUS_VAR(str) CARB_JOIN(str, __LINE__)
#endif

namespace carb
{

//! \cond DEV
template <typename T, size_t N>
constexpr size_t countOf(T const (&)[N])
{
    return N;
}

template <typename T, typename U>
constexpr uint32_t offsetOf(U T::*member)
{
    CARB_IGNOREWARNING_GNUC_PUSH
#if CARB_TOOLCHAIN_CLANG && __clang_major__ >= 13 // this error is issued on clang 13
    CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wnull-pointer-subtraction")
#endif
    return (uint32_t)((char*)&((T*)nullptr->*member) - (char*)nullptr);
    CARB_IGNOREWARNING_GNUC_POP
}

template <typename T, typename U>
constexpr uint32_t includesMember(size_t sizeOfStruct, U T::*member)
{
    CARB_IGNOREWARNING_GNUC_PUSH
#if CARB_TOOLCHAIN_CLANG && __clang_major__ >= 13 // this error is issued on clang 13
    CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wnull-pointer-subtraction")
#endif
    return sizeOfStruct >= offsetOf(member) + sizeof(U);
    CARB_IGNOREWARNING_GNUC_POP
}

template <typename T>
constexpr T align(T x, size_t alignment)
{
    return (T)(((size_t)x + alignment - 1) / alignment * alignment);
}

template <typename T>
T* align(T* x, size_t alignment)
{
    return (T*)(((size_t)x + alignment - 1) / alignment * alignment);
}

template <typename T>
constexpr T alignedSize(const T& size, uint32_t alignment)
{
    return ((size + alignment - 1) / alignment) * alignment;
}

template <typename T>
constexpr T divideCeil(T size, uint32_t divisor)
{
    static_assert(std::is_integral<T>::value, "Integral required.");
    return (size + divisor - 1) / divisor;
}
//! \endcond

//! Returns the count of an array as a `size_t` at compile time.
//! @param a The array to count.
//! @returns The number of elements in \p a.
#define CARB_COUNTOF(a) carb::countOf(a)

//! Returns the count of an array as a `uint32_t` at compile time.
//! @param a The array to count.
//! @returns The number of elements in \p a.
#define CARB_COUNTOF32(a) uint32_t(carb::countOf(a))

//! Returns the offset of a member of a class at compile time.
//! @param a The member of a class. The member must have visibility to the call of `CARB_OFFSETOF`. The class is
//! inferred.
//! @returns The offset of \p a from its containing class, in bytes, as a `uint32_t`.
#define CARB_OFFSETOF(a) carb::offsetOf(&a)

//! Returns whether it is safe to access a member of a versioned struct.
//! @param[in] sizeOfStruct The size of the versioned struct in bytes.  This is usually
//!                         provided as the first member of the struct.  Note that this
//!                         should not be passed as `sizeof(<struct_name>)` since that
//!                         would be hard coded at build time instead of considering the
//!                         actual versioned struct's runtime size.
//! @param[in] member       The member to test is safe to access in the struct.  This
//!                         should be given as the fully qualified name of the requested
//!                         member.
//! @returns `true` if the requested member is safe to access.  Returns `false` otherwise.
#define CARB_INCLUDES_MEMBER(sizeOfStruct, member) carb::includesMember(sizeOfStruct, &member)

#if !CARB_TOOLCHAIN_CLANG || defined(DOXYGEN_BUILD)
//! Returns the offset of a member `m` of a class `t` at compile time.
//! @param t The type on which to compute the offset.
//! @param m The member - the current location must have visibility to the call of `CARB_OFFSETOF2`.
//! @returns The offset of \p `m` in `t` from its containing class, in bytes, as a `size_t`.
#    define CARB_OFFSETOF2(t, m) (offsetof(t, m))
#else
// Workaround for CLANG+MSC Library issue (https://github.com/microsoft/STL/issues/3311)
#    define CARB_OFFSETOF2(t, m) (__builtin_offsetof(t, m))
#endif

#if CARB_COMPILER_MSC || defined(DOXYGEN_BUILD)
//! Returns the required alignment of a type.
//! @param T The type to determine alignment of.
//! @returns The required alignment of \p T, in bytes.
#    define CARB_ALIGN_OF(T) __alignof(T)
#elif CARB_COMPILER_GNUC
#    define CARB_ALIGN_OF(T) __alignof__(T)
#else
#    error "Align of cannot be determined - compiler not known"
#endif

// Implement CARB_HARDWARE_PAUSE; a way of idling the pipelines and reducing the penalty
// from memory order violations. See
// https://software.intel.com/en-us/articles/long-duration-spin-wait-loops-on-hyper-threading-technology-enabled-intel-processors
#ifdef DOXYGEN_BUILD
//! Instructs the underlying hardware to idle the CPU pipelines and reduce the penalty from memory order violations.
#    define CARB_HARDWARE_PAUSE()
#elif CARB_X86_64
// avoid including immintrin.h
#    if CARB_COMPILER_MSC
#        pragma intrinsic(_mm_pause)
#        define CARB_HARDWARE_PAUSE() _mm_pause()
#    else
#        define CARB_HARDWARE_PAUSE() __builtin_ia32_pause()
#    endif
#elif defined(__aarch64__)
#    define CARB_HARDWARE_PAUSE() __asm__ __volatile__("yield" ::: "memory")
#elif defined(_M_ARM64)
#    define CARB_HARDWARE_PAUSE() __yield()
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

#if CARB_COMPILER_MSC || defined(DOXYGEN_BUILD)
#    if defined(DOXYGEN_BUILD)
//! Attempts to prefetch from memory using a compiler intrinsic.
//! @param addr The address to prefetch
//! @param write Pass `true` if writing to the address is intended; `false` otherwise.
//! @param level The `carb::PrefetchLevel` hint.
#        define CARB_PREFETCH(addr, write, level)
#    elif CARB_X86_64
#        pragma intrinsic(_mm_prefetch)
#        define CARB_PREFETCH(addr, write, level) _mm_prefetch(reinterpret_cast<char*>(addr), int(level))
#    elif CARB_AARCH64
#        pragma intrinsic(__prefetch)
#        define CARB_PREFETCH(addr, write, level) __prefetch(reinterpret_cast<void*>(addr))
#    endif
//! Instructs the compiler to force inline of the decorated function
#    define CARB_ALWAYS_INLINE __forceinline
//! A prefetch level hint to pass to \ref CARB_PREFETCH()
enum class PrefetchLevel
{
    kHintNonTemporal = 0, //!< prefetch data into non-temporal cache structure and into a location close to the
                          //!< processor, minimizing cache pollution.
    kHintL1 = 1, //!< prefetch data into all levels of the cache hierarchy.
    kHintL2 = 2, //!< prefetch data into level 2 cache and higher.
    kHintL3 = 3, //!< prefetch data into level 3 cache and higher, or an implementation specific choice.
};
#elif CARB_COMPILER_GNUC
#    define CARB_ALWAYS_INLINE CARB_ATTRIBUTE(always_inline)
#    define CARB_PREFETCH(addr, write, level) __builtin_prefetch((addr), (write), int(level))
enum class PrefetchLevel
{
    kHintNonTemporal = 0,
    kHintL1 = 3,
    kHintL2 = 2,
    kHintL3 = 1,
};
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

//! A macro that declares that a function may not be inlined.
#define CARB_NOINLINE CARB_ATTRIBUTE(noinline) CARB_DECLSPEC(noinline)

#ifdef DOXYGEN_BUILD
//! Declares a function as deprecated.
#    define CARB_DEPRECATED(msg)
//! Declares a file as deprecated.
#    define CARB_FILE_DEPRECATED
//! Declares that a function will not throw any exceptions
#    define CARB_NOEXCEPT throw()
//! Used when declaring opaque types to prevent Doxygen from getting confused about not finding any implementation.
#    define DOXYGEN_EMPTY_CLASS                                                                                        \
        {                                                                                                              \
        }
#else
#    define CARB_DEPRECATED(msg) CARB_ATTRIBUTE(deprecated(msg)) CARB_DECLSPEC(deprecated(msg))
#    ifdef CARB_IGNORE_REMOVEFILE_WARNINGS
#        define CARB_FILE_DEPRECATED
#        define CARB_FILE_DEPRECATED_MSG(...)
#    else
#        define CARB_FILE_DEPRECATED_MSG(msg)                                                                          \
            CARB_PRAGMA(message("\x1b[33m" __FILE__ ":" CARB_STRINGIFY(                                                \
                __LINE__) ": " msg " (#define CARB_IGNORE_REMOVEFILE_WARNINGS to ignore these warnings)\x1b[0m"))      \
            CARB_PRAGMA(warning_see_message)
#        define CARB_FILE_DEPRECATED CARB_FILE_DEPRECATED_MSG("This file is no longer needed and will be removed soon")
#    endif
#    define CARB_NOEXCEPT noexcept
#    define DOXYGEN_EMPTY_CLASS
#endif

//! Aligns a number or pointer to the next multiple of a provided alignment.
//! @note The alignment need not be a power-of-two.
//! @param x The pointer or value to align
//! @param alignment The alignment value in bytes.
//! @returns If \p x is already aligned to \p alignment, returns \p x; otherwise returns \p x rounded up to the next
//! multiple of \p alignment.
#define CARB_ALIGN(x, alignment) carb::align(x, alignment)

//! Aligns a size to the given alignment.
//! @note The alignment need not be a power-of-two.
//! @param size The size to align.
//! @param alignment The alignment value in bytes.
//! @returns If \p size is already aligned to \p alignment, returns \p size; otherwise returns \p size rounded up to the
//! next multiple of \p alignment.
#define CARB_ALIGNED_SIZE(size, alignment) carb::alignedSize(size, alignment)

//! Defined as `alignas(T)`.
#define CARB_ALIGN_AS(T) alignas(T)

/**
 * Divides size by divisor and returns the closest integer greater than or equal to the division result.
 * For uses such as calculating a number of thread groups that cover all threads in a compute dispatch.
 * @param size An integer value.
 * @param divisor The divisor value.
 * @returns `size / divisor`, rounded up to the nearest whole integer. The type is based on \p size.
 */
#define CARB_DIVIDE_CEIL(size, divisor) carb::divideCeil(size, divisor)

#ifdef __cpp_lib_hardware_interference_size
CARB_GNUC_ONLY(CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Winterference-size"))
static_assert(std::hardware_destructive_interference_size == 64);
CARB_GNUC_ONLY(CARB_IGNOREWARNING_GNUC_POP)
#endif
//! Minimum offset between two objects to avoid false sharing, i.e. cache line size. If C++17 is not supported, falls
//! back to the default value of 64 bytes.
#define CARB_CACHELINE_SIZE (64)

//! Defined as `CARB_ALIGN_AS(CARB_CACHELINE_SIZE)`.
#define CARB_CACHELINE_ALIGN CARB_ALIGN_AS(CARB_CACHELINE_SIZE)

/** This is a wrapper for the platform-specific call to the non-standard but almost universal alloca() function. */
#if CARB_PLATFORM_WINDOWS
#    define CARB_ALLOCA(size) _alloca(size)
#elif CARB_PLATFORM_LINUX
#    define CARB_ALLOCA(size) alloca(size)
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

//! Attempts to allocate an array of the given type on the stack.
//! @warning On Windows, the underlying call to `_alloca()` may throw a SEH stack overflow exception if the stack does
//! not have sufficient space to perform the allocation. However, on Linux, there is no error handling for the
//! underlying `alloca()` call. The caller is advised to use caution.
//! @note The memory allocated is within the stack frame of the current function and is automatically freed when the
//! function returns or `longjmp()` or `siglongjmp()` is called. The memory is \a not freed when leaving the scope that
//! allocates it, except by the methods mentioned.
//! @param T The type of the object(s) to allocate.
//! @param number The number of objects to allocate. If `0`, a `nullptr` is returned.
//! @returns A properly-aligned pointer that will fit \p number quantity of type \p T on the stack. This memory will be
//! freed automatically when the function returns or `longjmp()` or `siglongjmp()` is called.
#define CARB_STACK_ALLOC(T, number)                                                                                    \
    carb::align<T>((((number) != 0) ? (T*)CARB_ALLOCA((number) * sizeof(T) + alignof(T)) : nullptr), alignof(T))

//! Allocates memory from the heap.
//! @rst
//! .. deprecated:: 126.0
//!     Please use `carb::allocate()` instead.
//! @endrst
//! @warning Memory allocated from this method must be freed within the same module that allocated it.
//! @param size The number of bytes to allocate.
//! @returns A valid pointer to a memory region of \p size bytes. If an error occurs, `nullptr` is returned.
#define CARB_MALLOC(size) std::malloc(size)

//! Frees memory previously allocated using CARB_MALLOC().
//! @rst
//! .. deprecated:: 126.0
//!     Please use `carb::deallocate()` instead.
//! @endrst
//! @param ptr The pointer previously returned from \c CARB_MALLOC.
#define CARB_FREE(ptr) std::free(ptr)

//! \cond DEV
// clang-format off
#define __CARB_STRINGIFY(x) #x
// clang-format on
//! \endcond

//! Turns a name into a string, resolving macros (i.e. `CARB_STRINGIFY(__LINE__)` on line 815 will produce `"815"`).
//! @param x The name to turn into a string.
//! @returns \p x as a string.
#define CARB_STRINGIFY(x) __CARB_STRINGIFY(x)

//! FNV-1a 64-bit hash basis.
//! @see http://www.isthe.com/chongo/tech/comp/fnv/#FNV-param
constexpr uint64_t kFnvBasis = 14695981039346656037ull;

//! FNV-1a 64-bit hash prime.
//! @see http://www.isthe.com/chongo/tech/comp/fnv/#FNV-param
constexpr uint64_t kFnvPrime = 1099511628211ull;

//! Compile-time FNV-1a 64-bit hash, use with CARB_HASH_STRING macro
//! @param str The string to hash.
//! @param n The number of characters in \p str, not including the NUL terminator.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
constexpr uint64_t fnv1aHash(const char* str, std::size_t n, uint64_t hash = kFnvBasis)
{
    return n > 0 ? fnv1aHash(str + 1, n - 1, (hash ^ (uint64_t)(*str)) * kFnvPrime) : hash;
}

//! \cond DEV
//! Compile-time FNV-1a 64-bit hash for a static string (char array).
//! @param array The static string to hash.
//! @returns A hash computed from the given parameters.
template <std::size_t N>
constexpr uint64_t fnv1aHash(const char (&array)[N])
{
    return fnv1aHash(&array[0], N - 1);
}
//! \endcond

//! Runtime FNV-1a 64-bit string hash
//! @param str The C-style (NUL terminated) string to hash.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
inline uint64_t hashString(const char* str, uint64_t hash = kFnvBasis)
{
    while (*str != '\0')
    {
        hash ^= static_cast<unsigned char>(*(str++));
        hash *= kFnvPrime;
    }
    return hash;
}

//! A fast table-based implementation of std::tolower for ASCII characters only.
//! @warning This function does not work on Unicode characters and is not locale-aware; it is ASCII only.
//! @param c The character to change to lower case.
//! @return The lower-case letter of \p c if \p c is an upper-case letter; \p c otherwise.
constexpr unsigned char tolower(unsigned char c)
{
    return detail::lowerTable[c];
};

//! A fast table-based implementation of std::toupper for ASCII characters only.
//! @warning This function does not work on Unicode characters and is not locale-aware; it is ASCII only.
//! @param c The character to change to upper case.
//! @return The upper-case letter of \p c if \p c is a lower-case letter; \p c otherwise.
constexpr unsigned char toupper(unsigned char c)
{
    return detail::upperTable[c];
}

//! Runtime FNV-1a 64-bit lower-case string hash (as if the string had been converted using \ref tolower()).
//! @param str The C-style (NUL terminated) string to hash.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
inline uint64_t hashLowercaseString(const char* str, uint64_t hash = kFnvBasis)
{
    while (*str != '\0')
    {
        hash ^= tolower(static_cast<unsigned char>(*(str++)));
        hash *= kFnvPrime;
    }
    return hash;
}

//! Runtime FNV-1a 64-bit lower-case byte hash (as if the bytes had been converted using \ref tolower()).
//! @param buffer The byte buffer to hash.
//! @param len The number of bytes in \p buffer.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
inline uint64_t hashLowercaseBuffer(const void* buffer, size_t len, uint64_t hash = kFnvBasis)
{
    const unsigned char* data = static_cast<const unsigned char*>(buffer);
    const unsigned char* const end = data + len;
    while (data != end)
    {
        hash ^= tolower(*(data++));
        hash *= kFnvPrime;
    }
    return hash;
}

//! Runtime FNV-1a 64-bit upper-case string hash (as if the string had been converted using \ref toupper()).
//! @param str The C-style (NUL terminated) string to hash.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
inline uint64_t hashUppercaseString(const char* str, uint64_t hash = kFnvBasis)
{
    while (*str != '\0')
    {
        hash ^= toupper(static_cast<unsigned char>(*(str++)));
        hash *= kFnvPrime;
    }
    return hash;
}

//! Runtime FNV-1a 64-bit upper-case byte hash (as if the bytes had been converted using \ref toupper()).
//! @param buffer The byte buffer to hash.
//! @param len The number of bytes in \p buffer.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
inline uint64_t hashUppercaseBuffer(const void* buffer, size_t len, uint64_t hash = kFnvBasis)
{
    const unsigned char* data = static_cast<const unsigned char*>(buffer);
    const unsigned char* const end = data + len;
    while (data != end)
    {
        hash ^= toupper(*(data++));
        hash *= kFnvPrime;
    }
    return hash;
}

//! Runtime FNV-1a 64-bit byte hash.
//! @param buffer The byte buffer to hash.
//! @param length The number of bytes in \p buffer.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
inline uint64_t hashBuffer(const void* buffer, size_t length, uint64_t hash = kFnvBasis)
{
    const char* ptr = static_cast<const char*>(buffer);


    for (size_t i = 0; i < length; ++i)
    {
        hash ^= static_cast<unsigned char>(ptr[i]);
        hash *= kFnvPrime;
    }
    return hash;
}

//! Runtime FNV-1a 64-bit hash of a scalar type.
//! @param type An scalar to hash.
//! @param hash The previous hash value or starting hash basis.
//! @returns A hash computed from the given parameters.
template <class T>
constexpr uint64_t hashScalar(const T& type, uint64_t hash = kFnvBasis)
{
    static_assert(std::is_scalar<T>::value, "Unsupported type for hashing");
    return hashBuffer(reinterpret_cast<const char*>(std::addressof(type)), sizeof(type), hash);
}

/**
 * Combines two hashes producing better collision avoidance than XOR.
 *
 * @param hash1 The initial hash
 * @param hash2 The hash to combine with @p hash1
 * @returns A combined hash of @p hash1 and @p hash2
 */
inline constexpr uint64_t hashCombine(uint64_t hash1, uint64_t hash2) noexcept
{
    constexpr uint64_t kConstant{ 14313749767032793493ull };
    constexpr int kRotate = 47;

    hash2 *= kConstant;
    hash2 ^= (hash2 >> kRotate);
    hash2 *= kConstant;

    hash1 ^= hash2;
    hash1 *= kConstant;

    // Add an arbitrary value to prevent 0 hashing to 0
    hash1 += 0x42524143; // CARB
    return hash1;
}

// The string hash macro is guaranteed to evaluate at compile time. MSVC raises a warning for this, which we disable.
#if defined(__CUDACC__) || defined(DOXYGEN_BUILD)
//! Computes a literal string hash at compile time.
//! @param str The string literal to hash
//! @returns A hash computed from the given string literal as if by \ref carb::fnv1aHash().
#    define CARB_HASH_STRING(str) std::integral_constant<uint64_t, carb::fnv1aHash(str)>::value
#else
#    define CARB_HASH_STRING(str)                                                                                      \
        CARB_IGNOREWARNING_MSC_WITH_PUSH(4307) /* 'operator': integral constant overflow */                            \
        std::integral_constant<uint64_t, carb::fnv1aHash(str)>::value CARB_IGNOREWARNING_MSC_POP
#endif

//! Syntactic sugar for `CARB_HASH_STRING(CARB_STRINGIFY(T))`.
#define CARB_HASH_TYPE(T) CARB_HASH_STRING(CARB_STRINGIFY(T))

// printf-like functions attributes
#if CARB_COMPILER_GNUC || defined(DOXYGEN_BUILD)
//! Requests that the compiler validate any variadic arguments as printf-style format specifiers, if supported by the
//! compiler. Causes a compilation error if the printf-style format specifier doesn't match the given variadic types.
//! @note The current implementation is effective only when `CARB_COMPILER_GNUC` is non-zero. The Windows implementation
//! does not work properly for custom printf-like function pointers. It is recommended where possible to use a "fake
//! printf" trick to force the compiler to evaluate the arguments:
//! ```cpp
//! if (0) printf(fmt, arg1, arg2); // Compiler will check but never execute.
//! ```
//! @param fmt_ordinal The 1-based function parameter receiving the printf-style format string.
//! @param args_ordinal The 1-based function parameter receiving the first variadic argument.
#    define CARB_PRINTF_FUNCTION(fmt_ordinal, args_ordinal) CARB_ATTRIBUTE(format(printf, fmt_ordinal, args_ordinal))
#elif CARB_COMPILER_MSC
// Microsoft suggest to use SAL annotations _Printf_format_string_ and _Printf_format_string_params_ for
// printf-like functions. Unfortunately it does not work properly for custom printf-like function pointers.
// So, instead of defining marker attribute for format string, we use the "fake printf" trick to force compiler
// checks and keep function attribute empty.
#    define CARB_PRINTF_FUNCTION(fmt_ordinal, args_ordinal)
#else
#    define CARB_PRINTF_FUNCTION(fmt_ordinal, args_ordinal)
#endif

//! An empty class tag type used with \ref EmptyMemberPair constructors.
struct ValueInitFirst
{
    //! Default constructor.
    constexpr explicit ValueInitFirst() = default;
};

//! An empty class tag type used with \ref EmptyMemberPair constructors.
struct InitBoth
{
    //! Default constructor.
    constexpr explicit InitBoth() = default;
};

//! Attempts to invoke the Empty Member Optimization by inheriting from the First element if possible, which, if empty
//! will eliminate the storage necessary for an empty class; the Second element is always stored as a separate member.
//! The First element is inherited from if it is an empty `class`/`struct` and is not declared `final`.
//! @tparam First The first element of the pair that the pair will inherit from if empty and not `final`.
//! @tparam Second The second element of the pair that will always be a member.
template <class First, class Second, bool = std::is_empty<First>::value && !std::is_final<First>::value>
class EmptyMemberPair : private First
{
public:
    //! Type of the First element
    using FirstType = First;
    //! Type of the Second element
    using SecondType = Second;

    //! Constructor that default-initializes the `First` member and passes all arguments to the constructor of `Second`.
    //! @param args arguments passed to the constructor of `second`.
    template <class... Args2>
    constexpr explicit EmptyMemberPair(ValueInitFirst, Args2&&... args)
        : First{}, second{ std::forward<Args2>(args)... }
    {
    }

    //! Constructor that initializes both members.
    //! @param arg1 the argument that is forwarded to the `First` constructor.
    //! @param args2 arguments passed to the constructor of `second`.
    template <class Arg1, class... Args2>
    constexpr explicit EmptyMemberPair(InitBoth, Arg1&& arg1, Args2&&... args2)
        : First(std::forward<Arg1>(arg1)), second(std::forward<Args2>(args2)...)
    {
    }

    //! Non-const access to `First`.
    //! @returns a non-const reference to `First`.
    constexpr FirstType& first() noexcept
    {
        return *this;
    }

    //! Const access to `First`.
    //! @returns a const reference to `First`.
    constexpr const FirstType& first() const noexcept
    {
        return *this;
    }

    //! Direct access to the `Second` member.
    SecondType second;
};

//! \cond DEV
template <class First, class Second>
class EmptyMemberPair<First, Second, false>
{
public:
    using FirstType = First;
    using SecondType = Second;

    template <class... Args2>
    constexpr explicit EmptyMemberPair(ValueInitFirst, Args2&&... args)
        : m_first(), second(std::forward<Args2>(args)...)
    {
    }

    template <class Arg1, class... Args2>
    constexpr explicit EmptyMemberPair(InitBoth, Arg1&& arg1, Args2&&... args2)
        : m_first(std::forward<Arg1>(arg1)), second(std::forward<Args2>(args2)...)
    {
    }

    constexpr FirstType& first() noexcept
    {
        return m_first;
    }
    constexpr const FirstType& first() const noexcept
    {
        return m_first;
    }

private:
    FirstType m_first;

public:
    SecondType second;
};
//! \endcond

} // namespace carb

/**
 * Picks the minimum of two values.
 *
 * Same as `std::min` but implemented without using the `min` keyword as Windows.h can sometimes `#define` it.
 *
 * @param left The first value to compare.
 * @param right The second value to compare.
 * @returns \p left if \p left is less than \p right, otherwise \p right, even if the values are equal.
 */
template <class T>
[[nodiscard]] constexpr const T& carb_min(const T& left, const T& right) noexcept(noexcept(left < right))
{
    return left < right ? left : right;
}

/**
 * Picks the maximum of two values.
 *
 * Same as `std::max` but implemented without using the `max` keyword as Windows.h can sometimes `\#define` it.
 *
 * @param left The first value to compare.
 * @param right The second value to compare.
 * @returns \p right if \p left is less than \p right, otherwise \p left, even if the values are equal.
 */
template <class T>
[[nodiscard]] constexpr const T& carb_max(const T& left, const T& right) noexcept(noexcept(left < right))
{
    return left < right ? right : left;
}

#if CARB_POSIX || defined(DOXYGEN_BUILD)
/**
 * A macro to retry operations if they return -1 and errno is set to EINTR.
 * @warning The `op` expression is potentially evaluated multiple times.
 * @param op The operation to retry
 * @returns The return value of \p op while guaranteeing that `errno` is not `EINTR`.
 */
#    define CARB_RETRY_EINTR(op)                                                                                       \
        [&] {                                                                                                          \
            decltype(op) ret_;                                                                                         \
            while ((ret_ = (op)) < 0 && errno == EINTR)                                                                \
            {                                                                                                          \
            }                                                                                                          \
            return ret_;                                                                                               \
        }()
#else
#    define CARB_RETRY_EINTR(op) (op)
#endif

/**
 * Portable way to mark unused variables as used.
 *
 * This tricks the compiler into thinking that the variables are used, eliminating warnings about unused variables.
 *
 * @param args Any variables or arguments that should be marked as unused.
 */
template <class... Args>
void CARB_UNUSED(Args&&... CARB_DOC_ONLY(args))
{
}

/** A macro to mark functionality that has not been implemented yet.
 *  @remarks This will abort the process with a message.
 *           The macro is [[noreturn]].
 */
#define CARB_UNIMPLEMENTED(msg, ...)                                                                                   \
    do                                                                                                                 \
    {                                                                                                                  \
        CARB_FATAL_UNLESS(false, (msg), ##__VA_ARGS__);                                                                \
        std::terminate();                                                                                              \
    } while (0)

/** A macro to mark placeholder functions on MacOS while the porting effort is in progress. */
#define CARB_MACOS_UNIMPLEMENTED() CARB_UNIMPLEMENTED("Unimplemented on Mac OS")

#if defined(CARB_INCLUDE_PURIFY_NAME) && !defined(DOXYGEN_BUILD)
#    ifdef __COUNTER__
#        define CARB_INCLUDE_PURIFY_TEST(...)                                                                          \
            inline void CARB_JOIN(CARB_INCLUDE_PURIFY_NAME, __COUNTER__)()                                             \
                __VA_ARGS__ static_assert(true, "Semicolon required")
#    else
#        define CARB_INCLUDE_PURIFY_TEST(...)                                                                          \
            inline void CARB_JOIN(CARB_INCLUDE_PURIFY_NAME, __LINE__)()                                                \
                __VA_ARGS__ static_assert(true, "Semicolon required")
#    endif
#else
/**
 * A macro that is used only for public includes to define a function which will instantiate templates.
 *
 * The templates are instantiated to make sure that all of the required symbols are available for compilation.
 * Example usage:
 * @code{.cpp}
 *  CARB_INCLUDE_PURIFY_TEST({
 *      carb::Delegate<void()> del;
 *  });
 * @endcode
 * @note The braces must be specified inside the macro parentheses.
 * @note This function is never executed, merely compiled to test include purification. Unit tests are responsible for
 *    full testing.
 * @note This macro only produces a function if `CARB_INCLUDE_PURIFY_NAME` is set to a function name. This happens in
 *    Carbonite's premake5.lua file when the include purification projects are generated.
 */
#    define CARB_INCLUDE_PURIFY_TEST(...)
#endif

#if CARB_COMPILER_MSC || defined(DOXYGEN_BUILD)
/**
 * A macro used to help the compiler optimize the code better, by assuming that the condition `b` is true.
 * Executing CARB_ASSUME(b) with `b == false` results in undefined behavior.
 */
#    define CARB_ASSUME(b) __assume(b)
#else
#    define CARB_ASSUME(b)                                                                                             \
        do                                                                                                             \
        {                                                                                                              \
            if (!(b))                                                                                                  \
                __builtin_unreachable();                                                                               \
        } while (false)
#endif

/**
 * A macro used to express that the current code position is unreachable.
 * Executing CARB_UNREACHABLE() results in undefined behavior.
 */
#define CARB_UNREACHABLE() CARB_ASSUME(false)

#if (CARB_HAS_CPP20 && defined(__cpp_consteval)) || defined(DOXYGEN_BUILD)
/**
 * A macro to mark a function as compile-time-only function.
 */
#    define CARB_CONSTEVAL consteval
#else
#    define CARB_CONSTEVAL constexpr
#endif

#if CARB_COMPILER_MSC || defined(DOXYGEN_BUILD)
/**
 * A placeholder for DWORD type
 */
#    define PRIdword "lu"

/**
 * A placeholder for DWORD type, in hexadecimal format
 */
#    define PRIxdword "lx"
#else
#    define PRIdword "u"
#    define PRIxdword "x"
#endif

// Undefine locals
#undef CARBLOCAL_HAS_NODISCARD_MSG
#undef CARBLOCAL_HAS_LIKELY
#undef CARBLOCAL_HAS_UNLIKELY
#undef CARBLOCAL_HAS_NO_UNIQUE_ADDRESS
#undef CARBLOCAL_HAS_BUILTIN_DEBUGTRAP

// Include the IAssert interface here so that Defines.h can be self-contained since CARB_ASSERT is defined here.
#include "assert/IAssert.h"
