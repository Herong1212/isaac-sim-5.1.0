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
//! @brief Utilities for omni.ext
#pragma once

#include "IExtensions.h"

#include "../../carb/ObjectUtils.h"
#include "../../carb/dictionary/DictionaryUtils.h"
#include "../../carb/settings/SettingsUtils.h"

#include <functional>
#include <string>
#include <utility>
#include <vector>


namespace omni
{
namespace ext
{

/**
 * Helper function to look up the path from an extension dictionary.
 * @warning Undefined behavior results if `extId` is not a valid Extension ID. Check for the existence of the extension
 *   before calling this function.
 * @param manager A pointer to the \ref ExtensionManager
 * @param extId The Extension ID as required by \ref ExtensionManager::getExtensionDict()
 * @returns a `std::string` representing the `path` member of the extension info dictionary
 * @see ExtensionManager, ExtensionManager::getExtensionDict()
 */
inline std::string getExtensionPath(ExtensionManager* manager, const char* extId)
{
    auto dict = carb::dictionary::getCachedDictionaryInterface();
    carb::dictionary::Item* infoDict = manager->getExtensionDict(extId);
    return infoDict ? dict->get<const char*>(infoDict, "path") : "";
}

/**
 * Helper function to find the Extension ID of a given Extension.
 * @param manager A pointer to the \ref ExtensionManager
 * @param extFullName The full extension name as required by \ref ExtensionManager::fetchExtensionVersions()
 * @returns The Extension ID of the enabled extension, or "" if the extension was not found or not enabled
 */
inline const char* getEnabledExtensionId(ExtensionManager* manager, const char* extFullName)
{
    size_t count;
    ExtensionInfo* extensions;
    manager->fetchExtensionVersions(extFullName, &extensions, &count);
    for (size_t i = 0; i < count; i++)
    {
        if (extensions[i].enabled)
            return extensions[i].id;
    }
    return nullptr;
}


/**
 * Helper function to check if an extension is enabled by name.
 * @param manager A pointer to the \ref ExtensionManager
 * @param extFullName The full extension name as required by \ref ExtensionManager::fetchExtensionVersions()
 * @returns `true` if the extension is enabled (that is if \ref getEnabledExtensionId() would return a non-`nullptr`
 *   value); `false` if the extension is not found or not enabled
 */
inline bool isExtensionEnabled(ExtensionManager* manager, const char* extFullName)
{
    return getEnabledExtensionId(manager, extFullName) != nullptr;
}

/**
 * Helper function to fetch all extension packages and load them into the memory.
 *
 * @warning This function is extemely slow, can take seconds, depending on the size of registry.
 *
 * After calling this function extension manager will have all registry extensions loaded into memory. Functions like
 * \ref ExtensionManager::getRegistryExtensions() will be returning a full list of all extensions after.
 *
 * @param manager A pointer to the \ref ExtensionManager
 * @returns A vector of of \ref ExtensionInfo objects
 */
inline std::vector<ExtensionInfo> fetchAllExtensionPackages(ExtensionManager* manager)
{
    std::vector<ExtensionInfo> packages;
    ExtensionSummary* summaries;
    size_t summaryCount;
    manager->fetchExtensionSummaries(&summaries, &summaryCount);
    for (size_t i = 0; i < summaryCount; i++)
    {
        const ExtensionSummary& summary = summaries[i];
        ExtensionInfo* extensions;
        size_t extensionCount;
        manager->fetchExtensionPackages(summary.fullname, &extensions, &extensionCount);
        packages.insert(packages.end(), extensions, extensions + extensionCount);
    }

    return packages;
}

/**
 * A wrapper object to allow passing an invocable type (i.e. lambda) as an extension hook.
 */
class ExtensionStateChangeHookLambda : public IExtensionStateChangeHook
{
public:
    /**
     * Constructor.
     * @note Typically this is not constructed directly. Instead use \ref createExtensionStateChangeHook().
     * @param fn a `std::function` that will be called on extension state change. May be empty.
     */
    ExtensionStateChangeHookLambda(const std::function<void(const char*, ExtensionStateChangeType)>& fn) : m_fn(fn)
    {
    }

    /**
     * State change handler function.
     * @note Typically this is not called directly; it is called by \ref ExtensionManager.
     * @param extId The Extension ID that is changing
     * @param type The \ref ExtensionStateChangeType describing the state change
     */
    void onStateChange(const char* extId, ExtensionStateChangeType type) override
    {
        if (m_fn)
            m_fn(extId, type);
    }

private:
    std::function<void(const char*, ExtensionStateChangeType)> m_fn;

    CARB_IOBJECT_IMPL
};

/**
 * Wrapper to pass an invocable object to Extension Manager Hooks.
 * @param hooks The \ref IExtensionManagerHooks instance
 * @param onStateChange The `std::function` that captures the invocable type (may be empty)
 * @param type The type to monitor for (see \ref IExtensionManagerHooks::createExtensionStateChangeHook())
 * @param extFullName See \ref IExtensionManagerHooks::createExtensionStateChangeHook()
 * @param extDictPath See \ref IExtensionManagerHooks::createExtensionStateChangeHook()
 * @param order See \ref IExtensionManagerHooks::createExtensionStateChangeHook()
 * @param hookName See \ref IExtensionManagerHooks::createExtensionStateChangeHook()
 * @returns see \ref IExtensionManagerHooks::createExtensionStateChangeHook()
 */
inline IHookHolderPtr createExtensionStateChangeHook(
    IExtensionManagerHooks* hooks,
    const std::function<void(const char* extId, ExtensionStateChangeType type)>& onStateChange,
    ExtensionStateChangeType type,
    const char* extFullName = "",
    const char* extDictPath = "",
    Order order = kDefaultOrder,
    const char* hookName = nullptr)
{
    return hooks->createExtensionStateChangeHook(
        carb::stealObject(new ExtensionStateChangeHookLambda(onStateChange)).get(), type, extFullName, extDictPath,
        order, hookName);
}

/**
 * A wrapper function to subscribe to extension enable (and optionally disable) events.
 * @param manager The \ref ExtensionManager instance
 * @param onEnable The `std::function` that captures the invocable to call on enable (may be empty). If the extension is
 *   already enabled, this is invoked immediately
 * @param onDisable The `std::function` that captures the invocable to call on disable (may be empty)
 * @param extFullName See \ref IExtensionManagerHooks::createExtensionStateChangeHook()
 * @param hookName See \ref IExtensionManagerHooks::createExtensionStateChangeHook()
 * @returns a `std::pair` of \ref IHookHolderPtr objects (`first` represents the enable holder and `second` represents
 *   the disable holder)
 */
inline std::pair<IHookHolderPtr, IHookHolderPtr> subscribeToExtensionEnable(
    ExtensionManager* manager,
    const std::function<void(const char* extId)>& onEnable,
    const std::function<void(const char* extId)>& onDisable = nullptr,
    const char* extFullName = "",
    const char* hookName = nullptr)
{
    // Already enabled?
    if (extFullName && extFullName[0] != '\0')
    {
        const char* enabledExtId = getEnabledExtensionId(manager, extFullName);
        if (enabledExtId)
            onEnable(enabledExtId);
    }

    // Subscribe for enabling:
    IHookHolderPtr holder0 = createExtensionStateChangeHook(
        manager->getHooks(), [onEnable = onEnable](const char* extId, ExtensionStateChangeType) { onEnable(extId); },
        ExtensionStateChangeType::eAfterExtensionEnable, extFullName, "", kDefaultOrder, hookName);

    // Optionally subscribe for disabling
    IHookHolderPtr holder1;
    if (onDisable)
        holder1 = createExtensionStateChangeHook(
            manager->getHooks(),
            [onDisable = onDisable](const char* extId, ExtensionStateChangeType) { onDisable(extId); },
            ExtensionStateChangeType::eBeforeExtensionShutdown, extFullName, "", kDefaultOrder, hookName);
    return std::make_pair(holder0, holder1);
}

//! The result of parsing an extension URL.
//!
//! Given "omniverse://path/to/object", `scheme` would contain "omniverse" and `path` would contain "path/to/object"
struct ExtPathUrl
{
    std::string scheme; //!< The extension URL scheme
    std::string path; //!< The extension URL path
};

/**
 * Simple helper function to parse a given URL into a scheme and a path.
 * @note If a path is given such as "f:/path/to/ext", this will return as \ref ExtPathUrl::scheme empty and everything
 *   in \ref ExtPathUrl::path.
 * @param url The extension URL to parse
 * @returns a \ref ExtPathUrl containing the separate parts
 */
inline ExtPathUrl parseExtUrl(const std::string& url)
{
    const std::string kSchemeDelimiter = ":";
    auto pos = url.find(kSchemeDelimiter);
    if (pos == std::string::npos || pos == 1)
        return { "", url };

    ExtPathUrl res = {};
    res.scheme = url.substr(0, pos);
    res.path = url.substr(pos + kSchemeDelimiter.size() + 1);
    res.path = res.path.erase(0, res.path.find_first_not_of("/"));
    return res;
}

} // namespace ext
} // namespace omni
