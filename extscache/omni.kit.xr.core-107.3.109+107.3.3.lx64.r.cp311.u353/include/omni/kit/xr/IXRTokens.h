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

// Predefined shared tokens/"string interning"

#include <carb/Defines.h>
#include <carb/Interface.h>
#include <carb/settings/ISettings.h>
#include <carb/settings/SettingsUtils.h>

namespace omni
{
namespace kit
{
namespace xr
{

using XRToken = const char*;

/**
 * @brief A fast "string interning" system for XR
 *
 * Similar to omni::usd::TokenH and pxr::TfToken, but with a few XRCore-specific design decisions in mind
 */
class IXRTokens_v1
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::xr::IXRTokens_v1", 1, 0)

    /**
     * @brief Create a new XRToken. Tokens are based on strings
     * and if you supply the same string the token will be the
     * same, making it easy to compare tokens.
     *
     * @param tokenStr    name of the token
     * @return token
     */
    XRToken(CARB_ABI* createXRToken_abi)(const char* tokenStr);
};

using IXRTokens = IXRTokens_v1;

/**
 * @brief Convenience function to get string from token
 *
 * @param token token to resolve
 * @return string representation of token
 */
inline const char* getStringFromXRToken(XRToken token)
{
    if (token == 0)
    {
        return "";
    }
    return reinterpret_cast<const char*>(token);
}

/**
 * @brief Convenience function to get uint64_t from token
 *
 * @param token token to resolve
 * @return uint64_t representation of token
 */
inline uint64_t getUnit64FromXRToken(XRToken token)
{
    return reinterpret_cast<uint64_t>(token);
}

/**
 * @brief Convenience function to get uint64_t from token
 *
 * @param token token to resolve
 * @return uint64_t representation of token
 */
inline XRToken getXRTokenFromUnit64(uint64_t token)
{
    return reinterpret_cast<XRToken>(token);
}

/**
 * @brief Convenience function for creating token from string
 *
 * @param tokenStr name of the token to resolve
 * @return token value
 */
inline XRToken getXRTokenFromString(const char* tokenStr)
{
    auto tokens = carb::getCachedInterface<IXRTokens>();
    return tokens->createXRToken_abi(tokenStr);
}

/**
 * @brief Convenience function for creating token from string
 *
 * @param tokenStr name of the token to resolve
 * @return token value
 */
inline XRToken getXRTokenFromString(const std::string& tokenStr)
{
    auto tokens = carb::getCachedInterface<IXRTokens>();
    return tokens->createXRToken_abi(tokenStr.c_str());
}

inline XRToken getXRTokenFromPath(const std::string& path, const std::string& defaultValue)
{
    auto settings = carb::getCachedInterface<carb::settings::ISettings>();
    auto tokens = carb::getCachedInterface<IXRTokens>();

    std::string value = carb::settings::getString(settings, path.c_str(), defaultValue);
    return tokens->createXRToken_abi(value.c_str());
}


/**
 * @brief Convenience class for quickly defining a token.
 */
class XRTokenDefinition
{
public:
    // Constructor
    XRTokenDefinition(const char* tokenString) : m_tokenString(tokenString)
    {
    }

    operator XRToken()
    {
        if (m_token == 0)
        {
            m_token = getXRTokenFromString(m_tokenString);
        }

        return m_token;
    }

private:
    const char* m_tokenString;
    XRToken m_token = 0;
};

} // namespace xr
} // namespace kit
} // namespace omni
