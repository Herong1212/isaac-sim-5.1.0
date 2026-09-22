// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include "../cpp/StringView.h"
#include "Unicode.h"

#include <map>
#include <string>
#include <utility>

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#else
#    ifndef DOXYGEN_BUILD
extern "C"
{
    extern char** environ;
}
#    endif
#endif

namespace carb
{
namespace extras
{

/**
 * Parses environment variables into program options or environment variables
 */
class EnvironmentVariableParser
{
public:
    /**
     * Construct an environment parser looking for variables starting with @p prefix
     */
    EnvironmentVariableParser(const char* prefix) : m_prefix(prefix)
    {
    }

    /**
     * Parse the environment. Variables starting with prefix given to constructor are separated
     * into program options, whereas all others are parsed as normal environment variables
     */
    void parse()
    {
        m_pathwiseOverrides.clear();
#if CARB_PLATFORM_WINDOWS
        parseWindows();
#else
        parsePosix();
#endif
    }

    //! key/value pairs of the parsed environment variables
    using Options = std::map<std::string, std::string>;

    /**
     * The map of program options that matched prefix.
     * @return map of key/value options
     */
    const Options& getOptions()
    {
        return m_pathwiseOverrides;
    }

    /**
     * The map of all environment variables that did not the prefix.
     * @return map of key/value environment variables
     */
    const Options& getEnvVariables()
    {
        return m_envVariables;
    }

private:
#if CARB_PLATFORM_WINDOWS
    void parseWindows()
    {
        class EnvVarsBlockWatchdog
        {
        public:
            EnvVarsBlockWatchdog()
            {
                m_envsBlock = GetEnvironmentStringsW();
            }
            ~EnvVarsBlockWatchdog()
            {
                if (m_envsBlock)
                {
                    FreeEnvironmentStringsW(m_envsBlock);
                }
            }

            const wchar_t* getEnvsBlock()
            {
                return m_envsBlock;
            }

        private:
            wchar_t* m_envsBlock = nullptr;
        };

        EnvVarsBlockWatchdog envVarsBlovkWatchdog;

        const wchar_t* envsBlock = envVarsBlovkWatchdog.getEnvsBlock();
        if (!envsBlock)
        {
            return;
        }

        const wchar_t* var = (LPWSTR)envsBlock;
        while (*var)
        {
            std::string varUtf8 = carb::extras::convertWideToUtf8(var);
            size_t equalSignPos = 0;
            size_t varLen = (size_t)lstrlenW(var);
            while (equalSignPos < varLen && var[equalSignPos] != L'=')
            {
                ++equalSignPos;
            }

            var += varLen + 1;

            if (equalSignPos == 0 || equalSignPos == varLen)
            {
                continue;
            }

            carb::cpp::string_view varNameUtf8(varUtf8.begin(), varUtf8.begin() + equalSignPos);
            carb::cpp::string_view varValueUtf8(varUtf8.begin() + equalSignPos + 1, varUtf8.end());
            _processAndAddOption(varNameUtf8, varValueUtf8);
        }
    }
#else
    void parsePosix()
    {
        char** envsBlock = environ;
        if (!envsBlock || !*envsBlock)
        {
            return;
        }

        while (*envsBlock)
        {
            size_t equalSignPos = 0;
            const char* var = *envsBlock;
            size_t varLen = (size_t)strlen(var);
            while (equalSignPos < varLen && var[equalSignPos] != '=')
            {
                ++equalSignPos;
            }

            ++envsBlock;

            if (equalSignPos == 0 || equalSignPos == varLen)
            {
                continue;
            }

            carb::cpp::string_view varName(var, var + equalSignPos);
            carb::cpp::string_view varValue(var + equalSignPos + 1, varLen - equalSignPos - 1);
            _processAndAddOption(varName, varValue);
        }
    }
#endif

    void _processAndAddOption(carb::cpp::string_view varName, carb::cpp::string_view varValue)
    {
        if (!m_prefix.empty() && varName.starts_with(m_prefix))
        {
            std::string path{ varName.substr(m_prefix.size()) };
            for (char& c : path)
            {
                // TODO: WRONG, must be utf8-aware replacement
                if (c == '_')
                    c = '/';
            }
            m_pathwiseOverrides.emplace(std::move(path), varValue);
        }
        else
        {
            m_envVariables.emplace(varName, varValue);
        }
    }

    // Path-wise overrides
    Options m_pathwiseOverrides;
    // Explicit env variables
    Options m_envVariables;
    std::string m_prefix;
};

} // namespace extras
} // namespace carb
