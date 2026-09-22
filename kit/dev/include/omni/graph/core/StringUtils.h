// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// This file contains helpful string utilities that can be implemented entirely as inlines, preventing the
// need for a bunch of tiny little extensions.

#include <carb/logging/Log.h>
#include <omni/graph/core/Type.h>

// clang-format off
#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/base/tf/token.h>
#include <omni/graph/core/PostUsdInclude.h>
// clang-format on

#include <string>
#include <vector>

// snprintf becomes _snprintf on Windows, but we want to use std::snprintf
#ifdef HAVE_SNPRINTF
#    undef snprintf
#endif

// The namespace is merely to ensure uniqueness. There's nothing inherently associated with OmniGraph in here
namespace omni {
namespace graph {
namespace core {

// ==============================================================================================================
inline void tokenizeString(const char* input, const std::string& separator, std::vector<pxr::TfToken> & output)
{
    std::string remainder = input;
    size_t separatorLocation = remainder.find(separator);
    while (separatorLocation != std::string::npos)
    {
        std::string tokenStr = remainder.substr(0, separatorLocation);
        output.emplace_back(tokenStr);

        remainder = remainder.substr(separatorLocation + separator.size());
        separatorLocation = remainder.find(separator);
    }
    if (!remainder.empty())
    {
        output.emplace_back(remainder);
    }
}

// ==============================================================================================================
// This is like tokenizeString, except returns a vector of strings, not tokens
inline std::vector<std::string> splitString(const char* string, char delimiter)
{
    std::vector<std::string> strings;
    const char* prev_pos = string;

    while (*string++)
    {
        char ch = *string;
        if (ch == delimiter)
        {
            strings.push_back(std::string(prev_pos, string));
            prev_pos = string + 1;
        }
    }

    if (prev_pos != string)
        strings.push_back(std::string(prev_pos, string - 1));

    return strings;
}

// ==============================================================================================================
// Return a formatted string.
// On error will return an empty string.
template <typename... Args>
std::string formatString(const char* format, Args&&... args)
{
    int fmtSize = std::snprintf(nullptr, 0, format, args...) + 1; // Extra space for '\0'
    if (fmtSize <= 0)
    {
        CARB_LOG_ERROR("Error formating string %s", format);
        return {};
    }
    auto size = static_cast<size_t>(fmtSize);
    auto buf = std::make_unique<char[]>(size);
    std::snprintf(buf.get(), size, format, args...);
    return std::string(buf.get(), buf.get() + size - 1); // We don't want the '\0' inside
}

//early version of GCC emit a warning if the "format" string passed to "std::snprintf" does not contain any formatting character
// Specialize the function for this use case and prevent that warning
inline std::string formatString(const char* format)
{
    return std::string(format);
}

} // namespace core
} // namespace graph
} // namespace omni
