// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief Utilities for Carbonite clients
#pragma once

#include "Framework.h"
#include "assert/AssertUtils.h"
#include "crashreporter/CrashReporterUtils.h"
#include "l10n/L10nUtils.h"
#include "logging/Log.h"
#include "profiler/Profile.h"

#include "../omni/core/Omni.h"

namespace carb
{

#ifndef DOXYGEN_SHOULD_SKIP_THIS
namespace detail
{
inline void registerBuiltinFileSystem(Framework* f)
{
    f->registerPlugin(g_carbClientName, f->getBuiltinFileSystemDesc());
}

inline void registerBuiltinLogging(Framework* f)
{
    f->registerPlugin(g_carbClientName, f->getBuiltinLoggingDesc());
}

inline void registerBuiltinAssert(Framework* f)
{
    f->registerPlugin(g_carbClientName, f->getBuiltinAssertDesc());
}

inline void registerBuiltinThreadUtil(Framework* f)
{
    f->registerPlugin(g_carbClientName, f->getBuiltinThreadUtilDesc());
}

inline void registerAtexitHandler()
{
#    if CARB_PLATFORM_WINDOWS && !defined _DLL
    // Since we're not using the dynamic runtime, we need to notify carb.dll if the executable's atexit() functions run.
    // We only do this if this is compiled into the executable here, so check that
    auto exeHandle = GetModuleHandleW(NULL);
    HMODULE myHandle;
    if (GetModuleHandleExW(
            CARBWIN_GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | CARBWIN_GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
            (LPCWSTR)&registerAtexitHandler, &myHandle) &&
        myHandle == exeHandle)
    {
        // Verified that this function is compiled into the executable and without dynamic runtime.
        auto carbHandle = GetModuleHandleW(L"carb.dll");
        auto proc = (void (*)(void*))(carbHandle ? GetProcAddress(carbHandle, "carbControlAtexit") : nullptr);
        if (proc)
        {
            // Call our undocumented function and pass our atexit() function so that carb.dll can register a callback
            // to know when the first-chance (executable) atexit happens.
            proc((void*)&atexit);
        }
    }
#    endif
}
} // namespace detail
#endif

/**
 * Main acquisition of the Carbonite Framework for Clients (applications and plugins).
 *
 * \warning It is typically not necessary to call this, since macros such as \ref OMNI_CORE_INIT already ensure that
 * this function is called properly.
 *
 * At a high level, this function:
 *
 *  - Calls \ref carb::acquireFramework() and assigns it to a global variable within this module: \ref g_carbFramework.
 *  - Calls \ref logging::registerLoggingForClient(), \ref assert::registerAssertForClient(), and
 *    \ref l10n::registerLocalizationForClient().
 *  - Calls \ref OMNI_CORE_START().
 *
 * @param args Arguments passed to \ref OMNI_CORE_START
 * @returns A pointer to the Carbonite Framework, if initialization was successful; `nullptr` otherwise.
 */
inline Framework* acquireFrameworkAndRegisterBuiltins(const OmniCoreStartArgs* args = nullptr)
{
    // Acquire framework and set into global variable
    Framework* framework = acquireFramework(g_carbClientName);
    if (framework)
    {
        g_carbFramework = framework;

        static_assert(
            kFrameworkVersion.major == 0,
            "The framework automatically registers builtins now; the registerXXX functions can be removed once the framework version changes.");

        detail::registerAtexitHandler();

        // Starting up logging
        detail::registerBuiltinLogging(framework);
        logging::registerLoggingForClient();

        // Starting up filesystem
        detail::registerBuiltinFileSystem(framework);
        detail::registerBuiltinAssert(framework);
        detail::registerBuiltinThreadUtil(framework);

        // grab the assertion helper interface.
        assert::registerAssertForClient();

        // grab the l10n interface.
        l10n::registerLocalizationForClient();

        // start up ONI
        OMNI_CORE_START(args);
    }
    return framework;
}

/**
 * This function releases the Carbonite Framework.
 *
 * The options performed are essentially the teardown operations for \ref acquireFrameworkAndRegisterBuiltins().
 *
 * At a high-level, this function:
 *  - Calls \ref logging::deregisterLoggingForClient(), \ref assert::deregisterAssertForClient(), and
 *    \ref l10n::deregisterLocalizationForClient().
 *  - Calls \ref omniReleaseStructuredLog().
 *  - Unloads all Carbonite plugins
 *  - Calls \ref OMNI_CORE_STOP
 *  - Calls \ref releaseFramework()
 *  - Sets \ref g_carbFramework to `nullptr`.
 *
 * \note It is not necessary to manually call this function if \ref OMNI_CORE_INIT is used, since that macro will ensure
 * that the Framework is released.
 */
inline void releaseFrameworkAndDeregisterBuiltins()
{
    if (isFrameworkValid())
    {
        logging::deregisterLoggingForClient();
        assert::deregisterAssertForClient();
        l10n::deregisterLocalizationForClient();
        // Release structured log before unloading plugins
        omniReleaseStructuredLog();
        g_carbFramework->unloadAllPlugins();
        OMNI_CORE_STOP();
        releaseFramework();
    }
    g_carbFramework = nullptr;
}

} // namespace carb

/**
 * Defines global variables of the framework and built-in plugins.
 *
 * \note Either this macro, or \ref CARB_GLOBALS_EX or \ref OMNI_APP_GLOBALS must be specified in the global namespace
 * in exactly one compilation unit for a Carbonite Application.
 *
 * @param clientName The name of the client application. Must be unique with respect to any plugins loaded. Also is the
 * name of the default log channel.
 */
#define CARB_GLOBALS(clientName) CARB_GLOBALS_EX(clientName, nullptr)

/**
 * Defines global variables of the framework and built-in plugins.
 *
 * \note Either this macro, or \ref CARB_GLOBALS or \ref OMNI_APP_GLOBALS must be specified in the global namespace in
 * exactly one compilation unit for a Carbonite Application.
 *
 * @param clientName The name of the client application. Must be unique with respect to any plugins loaded. Also is the
 * name of the default log channel.
 * @param clientDescription A description to use for the default log channel.
 */
#define CARB_GLOBALS_EX(clientName, clientDescription)                                                                 \
    CARB_FRAMEWORK_GLOBALS(clientName)                                                                                 \
    CARB_LOG_GLOBALS()                                                                                                 \
    CARB_PROFILER_GLOBALS()                                                                                            \
    CARB_ASSERT_GLOBALS()                                                                                              \
    CARB_LOCALIZATION_GLOBALS()                                                                                        \
    CARB_CRASH_REPORTER_GLOBALS()                                                                                      \
    OMNI_GLOBALS_ADD_DEFAULT_CHANNEL(clientName, clientDescription)
