// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Helpers for \ref carb::filesystem::IFileSystem
#pragma once

#include "../../carb/InterfaceUtils.h"
#include "../../carb/extras/Path.h"
#include "../../carb/filesystem/IFileSystem.h"
#include "../../carb/tokens/TokensUtils.h"

#include <string>
#include <vector>

namespace omni
{
namespace extras
{

/**
 * Helper function for acquiring and caching the filesystem.
 * @returns \ref carb::filesystem::IFileSystem acquired as by \ref carb::getCachedInterface()
 */
inline carb::filesystem::IFileSystem* getFileSystem()
{
    return carb::getCachedInterface<carb::filesystem::IFileSystem>();
}

/**
 * Returns a list of all files and sub-folders in the given folder.
 * @param folder The folder path to list
 * @returns a `std::vector` of all files and sub-folders in \p folder (non-recursive), or an empty `std::vector` if the
 *   path could not be accessed or was otherwise empty. Each item in the vector will be prefixed with \p folder.
 * @see carb::filesystem::IFileSystem::forEachDirectoryItem(), getDirectoryItemsOfType(), getSubfolders()
 */
inline std::vector<std::string> getDirectoryItems(const std::string& folder)
{
    std::vector<std::string> items;
    getFileSystem()->forEachDirectoryItem(folder.c_str(),
                                          [](const carb::filesystem::DirectoryItemInfo* const info, void* userData) {
                                              decltype(items)* _items = static_cast<decltype(items)*>(userData);
                                              _items->push_back(info->path);
                                              return carb::filesystem::WalkAction::eContinue;
                                          },
                                          &items);
    return items;
}

/**
 * Returns a list of either files or sub-folders in the given folder.
 * @param folder The folder path to list
 * @param type The \ref carb::filesystem::DirectoryItemType to find
 * @returns a `std::vector` of items of \p type in \p folder (non-recursive), or an empty `std::vector` if the path
 *   could not be accessed or was otherwise empty. Each item in the vector will be prefixed with \p folder.
 * @see carb::filesystem::IFileSystem::forEachDirectoryItem(), getDirectoryItems(), getSubfolders()
 */
inline std::vector<std::string> getDirectoryItemsOfType(const std::string& folder,
                                                        carb::filesystem::DirectoryItemType type)
{
    struct UserData
    {
        carb::filesystem::DirectoryItemType type;
        std::vector<std::string> items;
    };
    UserData data{ type, {} };

    getFileSystem()->forEachDirectoryItem(folder.c_str(),
                                          [](const carb::filesystem::DirectoryItemInfo* const info, void* userData) {
                                              decltype(data)* _data = static_cast<decltype(data)*>(userData);
                                              if (info->type == _data->type)
                                                  _data->items.push_back(info->path);
                                              return carb::filesystem::WalkAction::eContinue;
                                          },
                                          &data);
    return data.items;
}

/**
 * Helper function to gather all sub-folders within a given folder.
 *
 * Effectively the same as `getDirectoryItemsOfType(folder, carb::filesystem::DirectoryItemType::eDirectory)`
 * @param folder The folder path to list
 * @returns a `std::vector` of sub-folders in \p folder (non-recursive), or an empty `std::vector` if the path could not
 *   be accessed or was otherwise empty. Each item in the vector will be prefixed with \p folder.
 * @see carb::filesystem::IFileSystem::forEachDirectoryItem(), getDirectoryItems(), getDirectoryItemsOfType()
 */
inline std::vector<std::string> getSubfolders(const std::string& folder)
{
    return getDirectoryItemsOfType(folder, carb::filesystem::DirectoryItemType::eDirectory);
}

/**
 * Helper function to gather all sub-folders within an array of sub-folders.
 *
 * @note This is not recursive; it only goes one level deeper beyond the given collection of \p folders.
 * @param folders a `std::vector` of folders. This vector is walked and \ref getSubfolders() is called on each entry.
 *   Each entry in the vector will be prefixed with the entry from \p folders that contained it.
 * @returns a `std::vector` of sub-folders comprised of all of the sub-folders of the folders given in \p folders
 */
inline std::vector<std::string> getSubfolders(const std::vector<std::string>& folders)
{
    std::vector<std::string> allSubFolders;
    for (const std::string& folder : folders)
    {
        const std::vector<std::string> subFolders = getSubfolders(folder);
        allSubFolders.insert(allSubFolders.end(), subFolders.begin(), subFolders.end());
    }
    return allSubFolders;
}

/**
 * Resolves a given path by resolving all Tokens and optionally prepending the given root path.
 * @param path A path that may contain tokens (see \ref carb::tokens::ITokens)
 * @param root If \p path (after token resolution) is a relative path and this is provided, the returned path is
 *   prepended with this value.
 * @returns \p path with tokens resolved, prepended by \p root (if \p root is provided and the token-resolved path is
 *    relative)
 */
inline std::string resolvePath(const std::string& path, const std::string& root = {})
{
    auto tokens = carb::getCachedInterface<carb::tokens::ITokens>();

    carb::extras::Path resultPath = carb::tokens::resolveString(tokens, path);

    // If relative - relative to the root
    if (!root.empty() && resultPath.isRelative())
    {
        resultPath = carb::extras::Path(root).join(resultPath);
    }
    return resultPath;
}

/**
 * Reads file content into a string.
 * @warning This function reads data in a binary fashion and stores it in a `std::string`. As such, the string may
 *   contain non-printable characters or even `NUL` characters. No conversion of Windows line endings is performed.
 * @param path The path to read
 * @returns a `std::pair`, where the `first` member indicates success if `true` and the `second` member is the contents;
 *   if `first` is `false` then `second` will always be empty. If the file is valid but empty, `first` will be `true`
 *   but `second` will be empty.
 */
inline std::pair<bool, std::string> readFile(const char* path)
{
    auto fs = getFileSystem();
    if (fs->exists(path))
    {
        carb::filesystem::File* file = fs->openFileToRead(path);
        if (file)
        {
            size_t size = fs->getFileSize(file);
            if (size)
            {
                std::string buffer(size, ' ');
                fs->readFileChunk(file, &buffer[0], size);
                fs->closeFile(file);
                return std::make_pair(true, buffer);
            }
            else
            {
                fs->closeFile(file);
                return std::make_pair(true, std::string{});
            }
        }
    }
    return std::make_pair(false, std::string{});
}

} // namespace extras
} // namespace omni
