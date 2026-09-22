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
//! @brief Helpers for carb.settings
#pragma once

#include "../../carb/settings/SettingsUtils.h"

#include <string>
#include <vector>

namespace carb
{
namespace settings
{

/**
 * Access a setting key if present, otherwise returning a default value.
 * \details This function does not use the \ref carb::settings::ISettings API to set the value as a default if \p path
 *   does not exist. In order to do that, use \ref setDefaultAndGetSetting().
 * @tparam T the type of the return value and default value
 * @param path The setting key path to check
 * @param defaultValue The default value to return if the setting key does not exist
 * @returns The value read from \p path, or \p defaultValue if the setting key does not exist
 */
template <typename T>
T getSettingOrDefault(const char* path, T defaultValue = {})
{
    ISettings* s = getCachedInterface<ISettings>();
    if (s->getItemType(path) == dictionary::ItemType::eCount)
        return defaultValue;
    return s->get<T>(path);
}

/**
 * Sets a default value for a setting key and returns the current value.
 * \details Setting a default value will only have an effect if the setting key is not already present. The distinction
 *   between this function and \ref getSettingOrDefault() is that this function will set the default value with the
 *   \ref carb::settings::ISettings API. Any attempts to query the key directly will return the default value if it has
 *   not been modified.
 * @tparam T the type of the return value and default value
 * @param path The setting key path
 * @param defaultValue The default value to set for the setting key if it does not exist
 * @return The current value read from \p path, which will be \p defaultValue if the setting key did not exist before
 *   this function was called.
 */
template <typename T>
T setDefaultAndGetSetting(const char* path, T defaultValue = {})
{
    ISettings* s = getCachedInterface<ISettings>();
    s->setDefault<T>(path, defaultValue);
    return s->get<T>(path);
}

/**
 * Appends a set of string values to the end of a setting key.
 * @see carb::settings::ISettings
 * @param path The setting key path containing a string array. If the key does not exist it will be created. If the key
 *   is already present as a different type it will be changed to a string array.
 * @param values A `std::vector` of string values to add to the end of the string array at the setting key
 */
inline void appendToStringArray(const char* path, const std::vector<std::string>& values)
{
    if (values.empty())
        return;
    ISettings* s = getCachedInterface<ISettings>();
    carb::settings::ScopedWrite writeLock; // Hold a write lock while the modification takes place
    // TODO: This could be implemented a lot more efficiently than fully copying everything twice
    std::vector<std::string> v = settings::getStringArray(s, path);
    v.insert(v.end(), values.begin(), values.end());
    settings::setStringArray(s, path, v);
}

} // namespace settings
} // namespace carb
