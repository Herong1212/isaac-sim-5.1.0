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
//! @brief Implementation of utilities for \ref carb::tokens::ITokens.
#pragma once

#include "../InterfaceUtils.h"
#include "../logging/Log.h"
#include "../cpp/StringView.h"
#include "ITokens.h"

#include <string>
#include <algorithm>

namespace carb
{
namespace tokens
{

/**
 * Helper for resolving a token string. The resolve result (resolve code) is placed in the optional parameter.
 *
 * @param tokens tokens interface (passing a null pointer will result in an error)
 * @param str string for token resolution
 * @param resolveFlags flags that modify token resolution process
 * @param resolveResult optional parameter for receiving resulting resolve code
 *
 * @return true if the operation was successful false otherwise
 */
inline std::string resolveString(const ITokens* tokens,
                                 carb::cpp::string_view str,
                                 ResolveFlags resolveFlags = kResolveFlagNone,
                                 ResolveResult* resolveResult = nullptr)
{
    // Defaulting to an error result thus it's possible to just log an error message and return an empty string if
    // anything goes wrong
    if (resolveResult)
    {
        *resolveResult = ResolveResult::eFailure;
    }

    if (!tokens)
    {
        CARB_LOG_ERROR("Couldn't acquire ITokens interface.");
        return std::string();
    }

    ResolveResult resResult;
    size_t resolvedStringSize = tokens->calculateDestinationBufferSize(
        str.data(), str.size(), StringEndingMode::eNoNullTerminator, resolveFlags, &resResult);

    if (resResult == ResolveResult::eFailure)
    {
        CARB_LOG_ERROR("Couldn't calculate required buffer size for token resolution of string: %.*s",
                       unsigned(str.size()), str.data());
        return std::string();
    }

    // Successful resolution to an empty string
    if (resolvedStringSize == 0)
    {
        if (resolveResult)
        {
            *resolveResult = ResolveResult::eSuccess;
        }
        return std::string();
    }

    // C++11 guarantees that strings are continuous in memory
    std::string resolvedString;
    resolvedString.resize(resolvedStringSize);

    const ResolveResult resolveResultLocal =
        tokens->resolveString(str.data(), str.size(), &resolvedString.front(), resolvedString.size(),
                              StringEndingMode::eNoNullTerminator, resolveFlags, nullptr);

    if (resolveResultLocal != ResolveResult::eSuccess)
    {
        CARB_LOG_ERROR("Couldn't successfully resolve provided string: %.*s", unsigned(str.size()), str.data());
        return std::string();
    }

    if (resolveResult)
    {
        *resolveResult = ResolveResult::eSuccess;
    }

    return resolvedString;
}

/**
 * A helper function that escapes necessary symbols in the provided string so that they won't be recognized as related
 * to token parsing
 * @param str a string that requires preprocessing to evade the token resolution (a string provided by a user or some
 * other data that must not be a part of token resolution)
 * @return a string with necessary modification so it won't participate in token resolution
 */
inline std::string escapeString(const std::string& str)
{
    constexpr char kSpecialChar = '$';
    const size_t countSpecials = (size_t)std::count(str.begin(), str.end(), kSpecialChar);
    if (!countSpecials)
    {
        return str;
    }

    std::string result;
    result.reserve(str.length() + countSpecials);

    for (char curChar : str)
    {
        result.push_back(curChar);
        if (curChar == kSpecialChar)
        {
            result.push_back(kSpecialChar);
        }
    }
    return result;
}

} // namespace tokens
} // namespace carb
