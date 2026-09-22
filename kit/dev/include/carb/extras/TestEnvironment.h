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
 *  @brief Provides helper functions to check the platform a process is running on.
 */
#pragma once

#include "Library.h"
#if CARB_PLATFORM_LINUX
#    include "StringSafe.h"
#endif

#include <carb/extras/EnvironmentVariable.h>


/** Namespace for all low level Carbonite functionality. */
namespace carb
{
/** Common namespace for extra helper functions and classes. */
namespace extras
{

/**
 *  Queries whether the calling process is the Carbonite unit tests.
 *
 *  @note This requires the symbol "g_carbUnitTests" defined
 *  in the unittest module. on linux, if the symbol is declared in
 *  the executable and not in a shared library, the executable must
 *  be linked with -rdynamic or -Wl,--export-dynamic, otherwise
 *  getLibrarySymbol() will fail. typical usage would be to define
 *  g_carbUnitTests near the unittest module's main(), for example:
 *
 *  \code{.cpp}
 *  #include <carb/Defines.h>
 *
 *  CARB_EXPORT int32_t g_carbUnitTests;
 *  int32_t g_carbUnitTests = 1;
 *
 *  int main(int, char**) {
 *      // unittest driver
 *      return 0;
 *  }
 *  \endcode
 *
 *  @returns `true` if the calling process is the Carbonite unit tests.
 *  @returns `false` otherwise.
 */
inline bool isTestEnvironment()
{
    LibraryHandle module;
    void* symbol;


    module = loadLibrary(nullptr);

    if (module == nullptr)
        return false;

    symbol = getLibrarySymbol<void*>(module, "g_carbUnitTests");
    unloadLibrary(module);
    return symbol != nullptr;
}

/** Checks if this process is running under a CI system such as TeamCity or GitLab.
 *
 *  @returns `true` if TeamCity or GitLab have been detected.  Returns `false` otherwise.
 *           This value is cached after the first call and will simply return the cached
 *           value after that.
 */
inline bool isCiEnvironment()
{
    auto checkCiEnvVars = []() -> bool {
        std::string value;

        if (carb::extras::EnvironmentVariable::getValue("TEAMCITY_VERSION", value) ||
            carb::extras::EnvironmentVariable::getValue("GITLAB_CI", value))
        {
            return true;
        }

        return false;
    };

    static bool sResult = checkCiEnvVars();
    return sResult;
}

/** Retrieves the platform distro name.
 *
 *  @returns On Linux, the name of the distro the process is running under as seen in the "ID"
 *           tag in the '/etc/os-release' file if it can be found.
 *           On Windows, this returns the name "Windows".
 *  @returns On Linux, the name "Linux" if the '/etc/os-release' file cannot be accessed or the
 *           "ID" tag cannot be found in it.  On Windows, there is no failure path.
 */
inline const char* getDistroName()
{
#if CARB_POSIX
    static char distroName[64] = { 0 };
    auto searchFileForTag = [](const char* filename, const char* tag, char* out, size_t length, bool atStart) -> bool {
        FILE* fp = fopen(filename, "r");
        char buffer[1024];

        if (fp == nullptr)
            return false;

        out[0] = 0;

        while (!feof(fp) && !ferror(fp))
        {
            char* ptr;
            size_t len;

            ptr = fgets(buffer, CARB_COUNTOF32(buffer), fp);

            if (ptr == nullptr)
                break;

            // clear whitespace from the end of the line.
            len = strlen(buffer);
            while (len > 0 && (buffer[len - 1] == '\r' || buffer[len - 1] == '\n' || buffer[len - 1] == ' ' ||
                               buffer[len - 1] == '\t' || buffer[len - 1] == '\"'))
            {
                len--;
            }

            buffer[len] = 0;

            ptr = strstr(buffer, tag);

            if (ptr == nullptr || (atStart && ptr != buffer))
                continue;

            ptr += strlen(tag);

            if (ptr[0] == '\"')
                ptr++;

            copyStringSafe(out, length, ptr);
            break;
        }

        fclose(fp);
        return out[0] != 0;
    };

    if (distroName[0] == 0)
    {
#    if CARB_PLATFORM_LINUX
        // try to retrieve the distro name from the official OS info file.
        if (!searchFileForTag("/etc/os-release", "ID=", distroName, CARB_COUNTOF(distroName), true))
        {
            copyStringSafe(distroName, CARB_COUNTOF(distroName), "Linux");
        }
#    else
        CARB_UNSUPPORTED_PLATFORM();
#    endif
    }

    return distroName;
#elif CARB_PLATFORM_WINDOWS
    return "Windows";
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}

/** Checks whether the calling process is running on CentOS.
 *
 *  @returns `true` if the current platform is CentOS.
 *  @returns `false` if the current platform is not running CentOS.
 */
inline bool isRunningOnCentos()
{
    return strcmp(getDistroName(), "centos") == 0;
}

/** Checks whether the calling process is running on Ubuntu.
 *
 *  @returns `true` if the current platform is Ubuntu.
 *  @returns `false` if the current platform is not running Ubuntu.
 */
inline bool isRunningOnUbuntu()
{
    return strcmp(getDistroName(), "ubuntu") == 0;
}

} // namespace extras
} // namespace carb
