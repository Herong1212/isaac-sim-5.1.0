// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#include "../logging/Log.h"
#include "StringSafe.h"
#include "StringUtils.h"
#include "Unicode.h"

#include <cstddef>
#include <sstream>
#include <map>
#include <regex>
#include <string>

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#elif CARB_PLATFORM_LINUX
#    include <argz.h>
#    include <cstring>
#    include <fstream>
#endif

namespace carb
{
namespace extras
{

class CmdLineParser
{
public:
    using Options = std::map<std::string, std::string>;

    CmdLineParser(const char* prefix) : m_prefix(prefix)
    {
    }

    void parse(char** argv, int argc)
    {
        if (argc > 0)
        {
            parseFromArgs(argv, argc);
        }
        else
        {
            parseFromCLI();
        }
    }

    const Options& getOptions() const
    {
        return m_carbOptions;
    }

private:
    void parseFromCLI()
    {
        m_currentKey.clear();

#if CARB_PLATFORM_WINDOWS
        LPWSTR* argv;
        int argc;

        argv = CommandLineToArgvW(GetCommandLineW(), &argc);
        if (nullptr == argv)
        {
            return;
        }
        parseFromArgs(argv, argc);
        LocalFree(argv);
#elif CARB_PLATFORM_LINUX
        std::string cmdLine;
        std::getline(std::fstream("/proc/self/cmdline", std::ios::in), cmdLine);

        int argc = int(unsigned(argz_count(cmdLine.c_str(), cmdLine.size())));
        char** argv = static_cast<char**>(std::malloc(((size_t)argc + 1) * sizeof(char*)));
        argz_extract(cmdLine.c_str(), cmdLine.size(), argv);
        parseFromArgs(argv, argc);
        std::free(argv);
#endif
    }

    void parseArg(const std::string& arg)
    {
        // Waiting value for a key?
        if (!m_currentKey.empty())
        {
            std::string value = arg;
            preprocessValue(value);
            m_carbOptions[m_currentKey] = value;
            m_currentKey.clear();
            return;
        }

        // Process only keys starting with kCarbPrefix
        if (strncmp(arg.c_str(), m_prefix.c_str(), m_prefix.size()) == 0)
        {
            // Split to key and value
            std::size_t pos = arg.find("=");
            if (pos != std::string::npos)
            {
                const std::string key = carb::extras::trimString(arg.substr(m_prefix.size(), pos - m_prefix.size()));
                if (!key.empty())
                {
                    std::string value = arg.substr(pos + 1, arg.size() - pos - 1);
                    preprocessValue(value);
                    carb::extras::trimStringInplace(value);
                    m_carbOptions[key] = value;
                }
                else
                {
                    CARB_LOG_WARN("Encountered key-value pair with empty key in command line: %s", arg.c_str());
                }
            }
            else
            {
                // Save key and wait for next value
                m_currentKey = arg.substr(m_prefix.size(), arg.size() - m_prefix.size());
                carb::extras::trimStringInplace(m_currentKey);
            }
        }
    }

#if CARB_PLATFORM_WINDOWS
    void parseFromArgs(wchar_t** argv, int argc)
    {
        if (argc < 0 || argv == nullptr)
            return;

        for (int i = 1; i < argc; ++i)
        {
            if (argv[i])
            {
                std::string arg = extras::convertWideToUtf8(argv[i]);
                parseArg(arg);
            }
        }
    }
#endif

    void parseFromArgs(char** argv, int argc)
    {
        if (argc < 0 || argv == nullptr)
            return;

        for (int i = 1; i < argc; ++i)
        {
            if (argv[i])
            {
                std::string arg = argv[i];
                parseArg(arg);
            }
        }
    }

    void preprocessValue(std::string& value)
    {
        // If surrounded by single quotes - replace them with double quotes for json compatibility
        if (!value.empty() && value[0] == '\'' && value[value.size() - 1] == '\'')
        {
            value[0] = '"';
            value[value.size() - 1] = '"';
        }
    }

private:
    Options m_carbOptions;
    std::string m_currentKey;
    std::string m_prefix;
};


/**
 * Converts an array of command-line arguments to a single command-line string.
 *
 * It handles spaces and quotes in the arguments.
 *
 * @param argv The array of command-line arguments.
 * @param argc The number of arguments in the array.
 * @return A string that represents the command-line arguments.
 */
inline std::string argvToCommandLine(const char* const* argv, size_t argc)
{
    std::ostringstream os;
    for (size_t i = 0; i < argc; ++i)
    {
        if (i > 0)
            os << " ";

        // quote this argument if it contains tabs, spaces, quotes, newlines, or carriage returns
        cpp::string_view sv{ cpp::unsafe_length, argv[i] };
        if (sv.find_first_of(" \t\n\r\"", 0, 5) != std::string::npos)
        {
            os << "\"";
            os << sv.data();
            os << "\"";
        }
        else
        {
            os << sv.data();
        }
    }
    return os.str();
}

/** Creates a string version of the command line with specific patterns redacted.
 *
 *  @param[in] argv     A Unix style command line arguments list.  Each entry represents a single
 *                      command line argument.  This list is typically terminated by a `nullptr`
 *                      entry, though that is not required here since an explicit count is also
 *                      given in the @p argc parameter.  This may not be `nullptr`.
 *  @param[in] argc     The total number of argument strings to process in @p argv.  None of the
 *                      entries in @p argv up to but not including this count may be `nullptr`.
 *  @param[in] patterns A semicolon separated list of regular expression patterns to use to redact
 *                      strings in the command line arguments.  Any matching portions of argument
 *                      strings will be replaced with `<redacted>`.  Multiple patterns may be
 *                      provided by separating them with semicolons.  If a semicolon is needed
 *                      within a pattern, it may be escaped with '\\'.  If this is either an empty
 *                      string or `nullptr`, this is the same as calling argvToCommandLine().
 *  @returns The full command line as a single string with any portions that match one or more of
 *           the given patterns replaced with `<redacted>`.  Portions of the command line that do
 *           not match one of the patterns will be added to the command line unmodified.
 *
 *  @note This will throw a `std::regex_error` exception if an invalid regular expression is
 *        included in @p patterns.  If exception handling is enabled for a project that calls
 *        this, that exception will be caught and handled by writing a warning message to the
 *        log.  If exception handling is disabled for the project, this may result in a crash.
 */
inline std::string argvToRedactedCommandLine(const char* const* argv, size_t argc, const char* patterns)
{
    std::string patternsStr;
    std::vector<std::regex> patternsList;
    size_t start;
    size_t end;
    std::ostringstream os;


    if (isNullOrEmpty(patterns))
        return argvToCommandLine(argv, argc);

    // add a semicolon to the end of the string to make it easier to parse.
    patternsStr = patterns;
    patternsStr += ';';

    start = 0;
    do
    {
        end = patternsStr.find_first_of("\\;", start);

        // keep walking the string until we find an unescaped semicolon.
        while (end != std::string::npos && patternsStr[end] == '\\' && end + 1 < patternsStr.length() &&
               patternsStr[end + 1] == ';')
        {
            end = patternsStr.find_first_of("\\;", end + 2);
        }

        if (end == std::string::npos)
            break;

        std::string pattern = patternsStr.substr(start, end - start);

#if CARB_EXCEPTIONS_ENABLED
        try
        {
            patternsList.push_back(std::regex(pattern, std::regex_constants::ECMAScript));
        }

        catch (const std::regex_error& e)
        {
            CARB_LOG_WARN(
                "the pattern '%s' is malformed and will be ignored.  Please use an ECMA script compatible expression.",
                pattern.c_str());
            CARB_LOG_WARN("    %s", e.what());
        }
#else
        patternsList.push_back(std::regex(pattern, std::regex_constants::ECMAScript));
#endif

        start = end + 1;
    } while (1);


    for (size_t i = 0; i < argc; ++i)
    {
        if (i > 0)
            os << " ";

        std::string arg = argv[i];

        // replace the argument string with asterisks if it contains any of the matching filter
        // patterns.
        for (auto& pattern : patternsList)
        {
            arg = std::regex_replace(arg, pattern, "<redacted>");
        }

        // quote this argument if it contains tabs, spaces, quotes, newlines, or carriage returns
        if (arg.find_first_of(" \t\n\r\"", 0, 5) != std::string::npos)
        {
            os << "\"";
            os << arg;
            os << "\"";
        }
        else
        {
            os << arg;
        }
    }

    return os.str();
}

} // namespace extras
} // namespace carb
