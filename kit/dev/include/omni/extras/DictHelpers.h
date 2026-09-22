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
//! @brief Helpers for \ref carb::dictionary::Item and \ref carb::dictionary::IDictionary
#pragma once

#include "../../carb/dictionary/DictionaryUtils.h"

#include <string>
#include <vector>

namespace carb
{
namespace dictionary
{

/**
 * Gets a child value from a given Item if present, otherwise returns the given default value.
 * @tparam T the type of the return value and default value
 * @param baseItem The \ref carb::dictionary::Item to use as a base (required)
 * @param path The path of children from \p baseItem using `/` as a separator
 * @param defaultValue The default value to return if no item is present at the given location
 * @returns The \ref carb::dictionary::Item converted to `T` with \ref carb::dictionary::IDictionary::get(), or
 *   \p defaultValue if the given \p baseItem and \p path did not resolve to an Item
 */
template <typename T>
T getValueOrDefault(const Item* baseItem, const char* path, T defaultValue)
{
    IDictionary* d = getCachedDictionaryInterface();
    auto item = d->getItem(baseItem, path);
    if (!item)
        return defaultValue;
    return d->get<T>(item);
}

/**
 * Set a string array at the given path with the given array (creating it if it doesn't yet exist).
 * @param baseItem The \ref carb::dictionary::Item to use as a base (required)
 * @param path The path of children from \p baseItem using `/` as a separator
 * @param arr The array of string data to set at the given path
 * @returns The \ref carb::dictionary::Item that was either created or found at the given \p path
 */
inline Item* makeStringArrayAtPath(Item* baseItem, const char* path, const std::vector<std::string>& arr)
{
    IDictionary* dict = getCachedDictionaryInterface();
    ScopedWrite g(*dict, baseItem);
    Item* item = dict->getItemMutable(baseItem, path);
    if (!item)
    {
        item = dict->createItem(baseItem, path, ItemType::eDictionary);
    }

    for (size_t i = 0, count = arr.size(); i < count; ++i)
    {
        dict->setStringAt(item, i, arr[i].c_str());
    }
    return item;
}

} // namespace dictionary

} // namespace carb
