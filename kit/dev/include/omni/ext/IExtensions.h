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
//! @brief omni.ext Extension System interfaces
#pragma once

#include "../../carb/Framework.h"
#include "../../carb/IObject.h"
#include "../../carb/Interface.h"
#include "../../carb/events/IEvents.h"

namespace omni
{
namespace ext
{

/**
 * Extension version struct
 *
 * Follows Semantic Versioning 2.0. https://semver.org/
 */
struct Version
{
    int32_t major; //!< The major version (i.e. the 'x' in x.y.z), incremented for incompatible changes
    int32_t minor; //!< The minor version (i.e. the 'y' in x.y.z), for backwards compatible functionality
    int32_t patch; //!< The patch version (i.e. the 'z' in x.y.z), for backwards compatible bug fixes
    const char* prerelease = nullptr; //!< The pre-release string
    const char* build = nullptr; //!< The build string
};
CARB_ASSERT_INTEROP_SAFE(Version);

//! A struct describing Extension information
struct ExtensionInfo
{
    const char* id; //!< Unique Identifier used for python module name
    const char* name; //!< Extension name
    const char* packageId; //!< A package identifier
    Version version; //!< The version descriptor
    bool enabled; //!< Indicates whether this extension is enabled
    const char* title = nullptr; //!< An optional descriptive title
    const char* path = nullptr; //!< Extension path
};
CARB_ASSERT_INTEROP_SAFE(ExtensionInfo);

//! An enum describing Extensions Path type
enum class ExtensionPathType
{
    eCollection, //!< Folder with extensions
    eDirectPath, //!< Direct path to extension (as single file or a folder)
    eExt1Folder, //!< Deprecated Ext 1.0 Folder
    eCollectionUser, //!< Folder with extensions, read and stored in persistent settings
    eCollectionCache, //!< Folder with extensions, used for caching extensions downloaded from the registry
    eCount //!< Count of items in this enumeration
};

//! A struct for describing Extension Folder information
struct ExtensionFolderInfo
{
    const char* path; //!< Extension path
    ExtensionPathType type; //!< Type of information in `path` member.
};

//! A struct for describing Registry Provider information
struct RegistryProviderInfo
{
    const char* name; //!< The name of the Registry Provider
};

//! A bit type for Extension Summary
//! @see ExtensionSummary
using ExtensionSummaryFlag = uint32_t;

//! Empty flag
constexpr ExtensionSummaryFlag kExtensionSummaryFlagNone = 0;

//! Extension Summary flag meaning that extensions are enabled
constexpr ExtensionSummaryFlag kExtensionSummaryFlagAnyEnabled = (1 << 1);

//! Extension Summary flag meaning that an extension is built-in
constexpr ExtensionSummaryFlag kExtensionSummaryFlagBuiltin = (1 << 2);

//! Extension Summary flag meaning that an extension is installed
constexpr ExtensionSummaryFlag kExtensionSummaryFlagInstalled = (1 << 3);

//! A struct describing an Extension Summary
//! @see ExtensionManager::fetchExtensionSummaries()
struct ExtensionSummary
{
    const char* fullname; //!< The full extension name, typically "ext_name-ext_tag"
    ExtensionSummaryFlag flags; //!< Summary flags about this extension

    //! Information about the enabled version, if any. If not present, \ref ExtensionInfo::id will be an empty string.
    ExtensionInfo enabledVersion;

    //! Information about the latest version.
    ExtensionInfo latestVersion;
};

/**
 * Extension manager change events
 */

//! The event name denoting that a script changed (immediate).
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventScriptChangedImmediate = carb::RString("omni.ext:script_changed:immediate");

//! The event name denoting that a script changed.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventScriptChanged = carb::RString("omni.ext:script_changed");

//! The event name denoting that a folder changed (immediate).
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventFolderChangedImmediate = carb::RString("omni.ext:folder_changed:immediate");

//! The event name denoting that a folder changed.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventFolderChanged = carb::RString("omni.ext:folder_changed");

//! The event name denoting that a script changed (legacy version).
//! @see carb::events::IEvents
const carb::events::EventType kEventScriptChanged = CARB_EVENTS_TYPE_FROM_STR("SCRIPT_CHANGED");

//! An event type denoting a changed folder (legacy version).
//! @see carb::events::IEvents
const carb::events::EventType kEventFolderChanged = CARB_EVENTS_TYPE_FROM_STR("FOLDER_CHANGED");

/**
 * Other global updates issued by the extension manager
 */

//! An event dispatched at the beginning of registry refresh.
//! @par Parameters
//! * None
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventRegistryRefreshBegin = carb::RString("omni.ext:registry_refresh_begin");

//! An event dispatched at the beginning of registry refresh, but deferred until the end of the frame.
//! @par Parameters
//! * None
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventRegistryRefreshBeginDeferred = carb::RString("omni.ext:registry_refresh_begin:deferred");

//! An event dispatched at the end of registry refresh.
//! @par Parameters
//! * "success" (bool) - `true` if the registry was successfully refreshed; `false` otherwise.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventRegistryRefreshEnd = carb::RString("omni.ext:registry_refresh_end");

//! An event dispatched at the beginning of an extension pull.
//! @par Parameters
//! * "packageId" (RString) - The name of the extension package being pulled.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventExtensionPullBegin = carb::RString("omni.ext:extension_pull_begin");

//! An event dispatched at the beginning of an extension pull, but deferred until the end of the frame.
//! @par Parameters
//! * "packageId" (RString) - The name of the extension package being pulled.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventExtensionPullBeginDeferred = carb::RString("omni.ext:extension_pull_begin:deferred");

//! An event dispatched at the end of extension pull.
//! @par Parameters
//! * "packageId" (RString) - The name of the extension package pulled.
//! * "success" (bool) - `true` if the extension was successfully pulled; `false` otherwise.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventExtensionPullEnd = carb::RString("omni.ext:extension_pull_end");

/**
 * Legacy events sent to IApp::getMessageBusEventStream() by extension manager
 */

//! An event type denoting the beginning of registry refresh.
//! @warning this is deprecated in favor of \ref kGlobalEventRegistryRefreshBegin and
//! \ref kGlobalEventRegistryRefreshBeginDeferred
//! @see carb::events::IEvents kGlobalEventRegistryRefreshBegin kGlobalEventRegistryRefreshBeginDeferred
CARB_DEPRECATED("Use IEventDispatcher")
const carb::events::EventType kEventRegistryRefreshBegin = CARB_EVENTS_TYPE_FROM_STR("omni.ext.REGISTRY_REFRESH_BEGIN");

//! An event type denoting the successful end of registry refresh.
//! @warning this is deprecated in favor of \ref kGlobalEventRegistryRefreshEndSuccess and
//! \ref kGlobalEventRegistryRefreshEndSuccessImmediate
//! @see carb::events::IEvents
CARB_DEPRECATED("Use IEventDispatcher")
const carb::events::EventType kEventRegistryRefreshEndSuccess =
    CARB_EVENTS_TYPE_FROM_STR("omni.ext.REGISTRY_REFRESH_END_SUCCESS");

//! An event type denoting end of registry refresh with failure.
//! @warning this is deprecated in favor of \ref kGlobalEventRegistryRefreshEndFailure and
//! \ref kGlobalEventRegistryRefreshEndFailureImmediate
//! @see carb::events::IEvents
CARB_DEPRECATED("Use IEventDispatcher")
const carb::events::EventType kEventRegistryRefreshEndFailure =
    CARB_EVENTS_TYPE_FROM_STR("omni.ext.REGISTRY_REFRESH_END_FAILURE");

//! An event type denoting the beginning of pulling an extension.
//! @warning this is deprecated in favor of \ref kGlobalEventExtensionPullBegin and
//! \ref kGlobalEventExtensionPullBeginDeferred
//! @see carb::events::IEvents
CARB_DEPRECATED("Use IEventDispatcher")
const carb::events::EventType kEventExtensionPullBegin = CARB_EVENTS_TYPE_FROM_STR("omni.ext.EXTENSION_PULL_BEGIN");

//! An event type denoting the successful end of pulling an extension.
//! @warning this is deprecated in favor of \ref kGlobalEventExtensionPullEndSuccess and
//! \ref kGlobalEventExtensionPullEndSuccessImmediate
//! @see carb::events::IEvents
CARB_DEPRECATED("Use IEventDispatcher")
const carb::events::EventType kEventExtensionPullEndSuccess =
    CARB_EVENTS_TYPE_FROM_STR("omni.ext.EXTENSION_PULL_END_SUCCESS");

//! An event type denoting the end of pulling an extension with failure.
//! @warning this is deprecated in favor of \ref kGlobalEventExtensionPullEndFailure and
//! \ref kGlobalEventExtensionPullEndFailureImmediate
//! @see carb::events::IEvents
CARB_DEPRECATED("Use IEventDispatcher")
const carb::events::EventType kEventExtensionPullEndFailure =
    CARB_EVENTS_TYPE_FROM_STR("omni.ext.EXTENSION_PULL_END_FAILURE");

//! A global event type denoting the successful end of registry refresh.
//!
//! This event is deferred until the end of the frame. For notification immediately when the event occurs, see
//! \ref kGlobalEventRegistryRefreshEndSuccessImmediate
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventRegistryRefreshEndSuccess = carb::RString("omni.ext:registry_refresh_end:success");

//! A global event type denoting the successful end of registry refresh.
//!
//! This event is sent immediately when the event occurs. Typical notification should use
//! \ref kGlobalEventRegistryRefreshEndSuccess which comes at the end of the frame.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventRegistryRefreshEndSuccessImmediate =
    carb::RString("omni.ext:registry_refresh_end:success:immediate");

//! A global event type denoting end of registry refresh with failure.
//!
//! This event is deferred until the end of the frame. For notification immediately when the event occurs, see
//! \ref kGlobalEventRegistryRefreshEndFailureImmediate
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventRegistryRefreshEndFailure = carb::RString("omni.ext:registry_refresh_end:failure");

//! A global event type denoting end of registry refresh with failure.
//!
//! This event is sent immediately when the event occurs. Typical notification should use
//! \ref kGlobalEventRegistryRefreshEndSuccess which comes at the end of the frame.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventRegistryRefreshEndFailureImmediate =
    carb::RString("omni.ext:registry_refresh_end:failure:immediate");

//! An event type denoting the successful end of pulling an extension.
//!
//! This event is deferred until the end of the frame. For notification immediately when the event occurs, see
//! \ref kGlobalEventExtensionPullEndSuccessImmediate
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventExtensionPullEndSuccess = carb::RString("omni.ext:extension_pull_end:success");

//! An event type denoting the successful end of pulling an extension.
//!
//! This event is sent immediately when the event occurs. Typical notification should use
//! \ref kGlobalEventExtensionPullEndSuccess which comes at the end of the frame.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventExtensionPullEndSuccessImmediate = carb::RString("omni.ext:extension_pull_end:success:immediate");

//! An event type denoting the end of pulling an extension with failure.
//!
//! This event is deferred until the end of the frame. For notification immediately when the event occurs, see
//! \ref kGlobalEventExtensionPullEndFailureImmediate
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventExtensionPullEndFailure = carb::RString("omni.ext:extension_pull_end:failure");

//! An event type denoting the end of pulling an extension with failure.
//!
//! This event is sent immediately when the event occurs. Typical notification should use
//! \ref kGlobalEventExtensionPullEndFailure which comes at the end of the frame.
//! @see carb::eventdispatcher::IEventDispatcher
const auto kGlobalEventExtensionPullEndFailureImmediate = carb::RString("omni.ext:extension_pull_end:failure:immediate");

/**
 * Version lock generation parameters
 * @see ExtensionManager::generateVersionLock()
 */
struct VersionLockDesc
{
    bool separateFile; //!< Separate file
    bool skipCoreExts; //!< Skip core extensions
    bool overwrite; //!< Overwrite
};

/**
 * The download state communicated by registry provider to extension manager
 *
 * Generally for index refresh or extension pull operations
 */
enum class DownloadState
{
    eDownloading, //!< Currently downloading
    eDownloadSuccess, //!< Downloading finished successfully
    eDownloadFailure //!< Download failed
};

/**
 * Input to running custom extension solver.
 * @see ExtensionManager::solveExtensions()
 */
struct SolverInput
{
    //! List of extension names to enable (and therefore solve)
    //!
    //! Names may include full or partial versions, such as "omni.foo-1.2.3", or "omni.foo-1"
    //! The count of names is specified in `extensionNameCount`.
    const char** extensionNames;

    //! The number of names provided in the `extensionNames` array
    size_t extensionNameCount;

    //! Automatically add already enabled extension to the input (to take into account)
    bool addEnabled;

    //! If `true`, exclude extensions that are currently already enabled from the result.
    bool returnOnlyDisabled;
};


/**
 * Interface to be implemented by registry providers.
 *
 * Extension manager will use it to pull (when resolving dependencies) and publish extensions.
 *
 * This is a sub-interface, with version controlled by \ref IExtensions.
 *
 * @see ExtensionManager, ExtensionManager::addRegistryProvider(), IExtensions
 */
class IRegistryProvider : public carb::IObject
{
public:
    /**
     * Called by ExtensionManager to begin an asynchronous index refresh or check status on an asynchronous refresh
     *
     * This function will be called many times and should return immediately. The returned state should be one of
     * \ref DownloadState. The first call to this function should begin a background index refresh and return
     * \ref DownloadState::eDownloading. Further calls to this function may return the same result while the refresh is
     * in process. When the refresh is finished, the next call should return \ref DownloadState::eDownloadSuccess, at
     * which point the \ref ExtensionManager will call \ref syncIndex().
     *
     * @see ExtensionManager
     * @returns the \ref DownloadState
     */
    virtual DownloadState refreshIndex() = 0;

    /**
     * Called by ExtensionManager to get the index
     *
     * Extension manager will call that function from time to time to get remote index. The structure of this dictionary
     * is a map from extension ids to extension configuration (mostly extension.toml files).
     *
     * @see ExtensionManager, carb::dictionary::IDictionary
     * @returns A \ref carb::dictionary::Item tree representing the remote index.
     */
    virtual carb::dictionary::Item* syncIndex() = 0;

    /**
     * Called by ExtensionManager to trigger extension publishing
     *
     * @see ExtensionManager, unpublishExtension(), carb::dictionary::IDictionary
     * @param extPath The path to the extension to publish
     * @param extDict A \ref carb::dictionary::Item containing data about this extension
     * @returns `true` if publishing was successful; `false` if an error occurs
     */
    virtual bool publishExtension(const char* extPath, carb::dictionary::Item* extDict) = 0;

    /**
     * Called by ExtensionManager to remove an extension
     *
     * @see ExtensionManager, publishExtension()
     * @param extId the extension ID of the extension to remove
     * @returns `true` if removal was successful; `false` if an error occurs
     */
    virtual bool unpublishExtension(const char* extId) = 0;

    /**
     * Called by ExtensionManager to pull an extension, from a remote location to local cache
     *
     * @see ExtensionManager
     * @param extId The extension ID of the extension to pull
     * @param extFolder The folder to store the extension files in
     * @returns `true` if pulling was successful; `false` if an error occurs
     */
    virtual bool pullExtension(const char* extId, const char* extFolder) = 0;

    /**
     * Called by ExtensionManager to asynchronously pull an extension, from a remote location to local cache
     *
     * This function will be called several times. The first time it is called for a given @p extId and @p extFolder, it
     * should start a background download process and return \ref DownloadState::eDownloading. It will be called
     * periodically to check the download state. Once the extension has been downloaded, this function should return
     * @ref DownloadState::eDownloadSuccess, or @ref DownloadState::eDownloadFailure if an error occurs.
     * @see ExtensionManager, DownloadState
     * @param extId The extension ID of the extension to pull
     * @param extFolder The folder to store the extension files in
     * @returns the current \ref DownloadState of the given \p extId
     */
    virtual DownloadState pullExtensionAsync(const char* extId, const char* extFolder) = 0;

    /**
     * Called by ExtensionManager to set the maximum level of index stripping
     *
     * @rst
       .. deprecated::
            This method is deprecated and no longer called.
       @endrst
     */
    CARB_DEPRECATED("Not called. Index stripping was deprecated.") virtual bool setMaxStrippingLevel(int32_t level) = 0;
};

//! Pointer type
using IRegistryProviderPtr = carb::ObjectPtr<IRegistryProvider>;

/**
 * Interface to be implemented to add new extension path protocols.
 */
class IPathProtocolProvider : public carb::IObject
{
public:
    /**
     * Called by ExtensionManager to register a protocol
     *
     * It must return local file system path for the provided url to be registered instead of url. It is a job of
     * protocol provider to update and maintain that local path. Extension manager will treat that path the same as
     * regular local extension search paths.
     * @param url The protocol to register
     * @returns A local filesystem path
     */
    virtual const char* addPath(const char* url) = 0;

    /**
     * Called by ExtensionManager to unregister a protocol
     * @param url The protocol previously passed to \ref addPath().
     */
    virtual void removePath(const char* url) = 0;
};

//! Pointer type
using IPathProtocolProviderPtr = carb::ObjectPtr<IPathProtocolProvider>;

class IExtensionManagerHooks;

/**
 * The manager class that is responsible for all Extensions.
 * @see IExtensions::createExtensionManager
 */
class ExtensionManager : public carb::IObject
{
public:
    /**
     * Process all outstanding extension changes since the previous call to this function.
     *
     * If an extension was changed it will be reloaded. If it was added or removed (including adding new folders)
     * changes will also be applied. Events (@ref kGlobalEventScriptChanged, @ref kGlobalEventFolderChanged) are also
     * dispatched.
     */
    virtual void processAndApplyAllChanges() = 0;

    /**
     * Returns the number of registered local extensions.
     * @returns the number of registered local extensions
     */
    virtual size_t getExtensionCount() const = 0;

    /**
     * Fills an array with information about registered local extensions.
     *
     * @param extensions The array of \ref ExtensionInfo structs to be filled. It must be large enough to hold
     *   @ref getExtensionCount() entries.
     */
    virtual void getExtensions(ExtensionInfo* extensions) const = 0;

    /**
     * Get an extension info dictionary for a single extension.
     * @see carb::dictionary::IDictionary
     * @param extId The extension ID to retrieve info for
     * @returns A \ref carb::dictionary::Item pointer containing the information; `nullptr` if the extension was not
     *   found.
     */
    virtual carb::dictionary::Item* getExtensionDict(const char* extId) const = 0;

    /**
     * Helper function to enable or disable a single extension.
     * @note The operation is deferred until \ref processAndApplyAllChanges() is called. Use
     *   \ref setExtensionEnabledImmediate() to perform the action immediately.
     * @see setExtensionEnabledBatch
     * @param extensionId The extension ID to enable or disable
     * @param enabled `true` to enable the extension; `false` to disable the extension
     */
    void setExtensionEnabled(const char* extensionId, bool enabled)
    {
        setExtensionEnabledBatch(&extensionId, 1, enabled);
    }

    /**
     * Enables or disables several extensions.
     * @note The operation is deferred until \ref processAndApplyAllChanges() is called. Use
     *   \ref setExtensionEnabledBatchImmediate() to perform the action immediately.
     * @param extensionIds An array of extension IDs that should be enabled or disabled
     * @param extensionIdCount The number of items in \p extensionIds
     * @param enabled `true` to enable the extensions; `false` to disable the extensions
     */
    virtual void setExtensionEnabledBatch(const char** extensionIds, size_t extensionIdCount, bool enabled) = 0;

    /**
     * Helper function to enable or disable a single extension, immediately.
     * @see setExtensionEnabledBatchImmediate
     * @param extensionId The extension ID to enable or disable
     * @param enabled `true` to enable the extension; `false` to disable the extension
     * @returns `true` if the operation could be completed; `false` otherwise
     */
    bool setExtensionEnabledImmediate(const char* extensionId, bool enabled)
    {
        return setExtensionEnabledBatchImmediate(&extensionId, 1, enabled);
    }

    /**
     * Enables or disables several extensions immediately.
     * @param extensionIds An array of extension IDs that should be enabled or disabled
     * @param extensionIdCount The number of items in \p extensionIds
     * @param enabled `true` to enable the extensions; `false` to disable the extensions
     * @returns `true` if the operation could be completed; `false` otherwise
     */
    virtual bool setExtensionEnabledBatchImmediate(const char** extensionIds, size_t extensionIdCount, bool enabled) = 0;

    /**
     * Set extensions to exclude on following solver/startup routines.
     *
     * @note The extensions set persist until next call to this function.
     * @param extensionIds An array of extension IDs that should be excluded
     * @param extensionIdCount The number of items in \p extensionIds
     */
    virtual void setExtensionsExcluded(const char** extensionIds, size_t extensionIdCount) = 0;

    /**
     * Gets number of monitored extension folders.
     *
     * @return Extension folder count.
     */
    virtual size_t getFolderCount() const = 0;

    /**
     * Gets monitored extension folders.
     * @param extensionFolderInfos The extension folder info array to be filled. It must be large enough to hold
     *   @ref getFolderCount() entries.
     */
    virtual void getFolders(ExtensionFolderInfo* extensionFolderInfos) const = 0;

    /**
     * Add extension path.
     * @see removePath()
     * @param path The path to add (folder or direct path)
     * @param type An \ref ExtensionPathType describing how \p path should be treated
     */
    virtual void addPath(const char* path, ExtensionPathType type = ExtensionPathType::eCollection) = 0;

    /**
     * Remove extension path.
     * @see addPath()
     * @param path The path previously given to \ref addPath()
     */
    virtual void removePath(const char* path) = 0;

    /**
     * Accesses the IEventStream that is used for change events.
     * @warning This function is deprecated in favor of Events 2.0 using *carb.eventdispatcher.plugin* with named
     *   events (see \ref kGlobalEventScriptChanged, \ref kGlobalEventFolderChanged).
     * @see carb::events::IEventStream
     * @returns The \ref carb::events::IEventStream used for change events
     */
    CARB_DEPRECATED("Use carb::eventdispatcher") virtual carb::events::IEventStream* getChangeEventStream() const = 0;

    /**
     * Interface to install hooks to "extend" extension manager.
     * @returns an \ref IExtensionManagerHooks instance to allow hooking the Extension Manager
     */
    virtual IExtensionManagerHooks* getHooks() const = 0;

    /**
     * Adds a new registry provider.
     * @see IRegistryProvider, removeRegistryProvider()
     * @param providerName unique name for the registry provider
     * @param provider a \ref IRegistryProvider instance that will be retained by `*this`
     * @returns `true` if registration was successful; `false` otherwise (i.e. the provided name was not unique)
     */
    virtual bool addRegistryProvider(const char* providerName, IRegistryProvider* provider) = 0;

    /**
     * Removes a registry provider.
     * @see IRegistryProvider, addRegistryProvider()
     * @param providerName the unique name previously passed to \ref addRegistryProvider()
     */
    virtual void removeRegistryProvider(const char* providerName) = 0;

    /**
     * Gets the number of current registry providers.
     * @returns the number of registry providers
     */
    virtual size_t getRegistryProviderCount() const = 0;

    /**
     * Fills an array with info about current registry providers.
     * @param infos an array of \ref RegistryProviderInfo objects to be filled. It must be large enough to hold
     *   @ref getRegistryProviderCount() entries.
     */
    virtual void getRegistryProviders(RegistryProviderInfo* infos) = 0;

    /**
     * Non blocking call to initiate registry refresh.
     */
    virtual void refreshRegistry() = 0;

    /**
     * Blocking call to synchronize with remote registry.
     * @returns `true` if the synchronization was successful; `false` if an error occurred.
     */
    virtual bool syncRegistry() = 0;

    /**
     * Gets the number of extensions in the registry.
     */
    virtual size_t getRegistryExtensionCount() const = 0;

    /**
     * Fills an array with compatible extensions in the registry.
     *
     * @param extensions an array of \ref ExtensionInfo objects to be filled. It must be large enough to hold
     *   @ref getRegistryExtensionCount() entries.
     */
    virtual void getRegistryExtensions(ExtensionInfo* extensions) const = 0;

    /**
     * Gets the number of extension packages in the registry.
     */
    virtual size_t getRegistryExtensionPackageCount() const = 0;

    /**
     * Fills the array with all extension packages in the registry.
     *
     * @note this function will return all extensions in the registry, including packages for other platforms,
     * incompatible with current runtime.
     *
     * @param extensions an array of \ref ExtensionInfo objects to be filled. It must be large enough to hold
     *   @ref getRegistryExtensionPackageCount() entries.
     */
    virtual void getRegistryExtensionPackages(ExtensionInfo* extensions) const = 0;

    /**
     * Get an extension info dictionary for a single extension from the registry.
     * @see carb::dictionary::IDictionary
     * @param extId The extension ID to retrieve information for
     * @returns A \ref carb::dictionary::Item containing information about the given extension; `nullptr` if the
     *   extension ID was not found.
     */
    virtual carb::dictionary::Item* getRegistryExtensionDict(const char* extId) = 0;

    /**
     * Package and upload extension to the registry.
     *
     * @note If \p providerName is empty and there are multiple providers, the provider specified in the setting key
     *   `/app/extensions/registryPublishDefault` is used.
     * @see unpublishExtension()
     * @param extId The extension ID to publish
     * @param providerName The provider name to use for publish. If an empty string is provided and multiple providers
     *   are registered, the provider specified in the setting key `/app/extensions/registryPublishDefault` is used.
     * @param allowOverwrite If `true`, the extension already specified in the registry maybe overwritten
     */
    virtual bool publishExtension(const char* extId, const char* providerName = "", bool allowOverwrite = false) = 0;

    /**
     * Removes an extension from the registry.
     *
     * @note If \p providerName is empty and there are multiple providers, the provider specified in the setting key
     *   `/app/extensions/registryPublishDefault` is used.
     * @see publishExtension()
     * @param extId The extension ID to unpublish
     * @param providerName The provider name to use. If an empty string is provided and multiple providers
     *   are registered, the provider specified in the setting key `/app/extensions/registryPublishDefault` is used.
     */
    virtual bool unpublishExtension(const char* extId, const char* providerName = "") = 0;

    /**
     * Downloads the specified extension from the registry.
     * @note This is a blocking call. Use @ref pullExtensionAsync() if asynchronous behavior is desired.
     * @see pullExtensionAsync()
     * @param extId The extension ID to download
     * @returns `true` if the extension was downloaded successfully; `false` otherwise.
     */
    virtual bool pullExtension(const char* extId) = 0;

    /**
     * Starts an asynchronous extension download from the registry.
     * @note this function returns immediately
     * @see pullExtension()
     * @param extId The extension ID to download
     */
    virtual void pullExtensionAsync(const char* extId) = 0;

    /**
     * Fetches extension summaries for all extensions.
     *
     * Summary are extensions grouped by version. One summary per fullname(name+tag).
     * @note The array that is received is valid until the next call to this function.
     * @param[out] summaries Receives an array of \ref ExtensionSummary instances
     * @param[out] summaryCount Receives the size of the array passed to \p summaries.
     */
    virtual void fetchExtensionSummaries(ExtensionSummary** summaries, size_t* summaryCount) = 0;

    /**
     * Fetch all matching compatible extensions.
     *
     * A partial version can also be passed. So `omni.foo`, `omni.foo-2`, `omni.foo-1.2.3` all valid values for
     * @p nameAndVersion.
     *
     * @note The returned array is valid until next call of this function.
     * @param nameAndVersion The name (and optional partial or full version) to search
     * @param[out] extensions Receives an array of \ref ExtensionInfo instances
     * @param[out] extensionCount Receives the size of the array passed to \p extensions
     */
    virtual void fetchExtensionVersions(const char* nameAndVersion, ExtensionInfo** extensions, size_t* extensionCount) = 0;

    /**
     * Fetch all matching extension packages.
     *
     * A partial version can also be passed. So `omni.foo`, `omni.foo-2`, `omni.foo-1.2.3` all valid values for
     * @p nameAndVersion.
     *
     * This function will return all extensions in the registry, including packages for other platforms, incompatible
     * with current runtime.
     *
     * @note The returned array is valid until next call of this function.
     * @param nameAndVersion The name (and optional partial or full version) to search
     * @param[out] extensions Receives an array of \ref ExtensionInfo instances
     * @param[out] extensionCount Receives the size of the array passed to \p extensions
     */
    virtual void fetchExtensionPackages(const char* nameAndVersion, ExtensionInfo** extensions, size_t* extensionCount) = 0;

    /**
     * Disables all enabled extensions.
     *
     * @note this is called automatically upon destruction.
     */
    virtual void disableAllExtensions() = 0;

    /**
     * Adds user paths from persistent settings.
     *
     * All of the extension search path from persistent settings are added as \ref ExtensionPathType::eCollectionUser.
     */
    virtual void addUserPaths() = 0;

    /**
     * Add cache paths from settings.
     *
     * All of the cache paths from settings are added as \ref ExtensionPathType::eCollectionCache.
     * This is necessary for registry usage.
     */
    virtual void addCachePath() = 0;

    /**
     * Generate settings that contains versions of started dependencies to lock them (experimental).
     * @param extId The extension ID
     * @param desc A \ref VersionLockDesc descriptor
     * @returns `true` if generation succeeded; `false` otherwise
     */
    virtual bool generateVersionLock(const char* extId, const VersionLockDesc& desc) = 0;

    /**
     * Adds a new path protocol provider.
     * @see removePathProtocolProvider()
     * @param scheme A unique name for this provider
     * @param provider A \ref IPathProtocolProvider instance that will be retained by the Extension Manager
     * @returns `true` if the provider was registered; `false` otherwise (i.e. if \p scheme is not unique)
     */
    virtual bool addPathProtocolProvider(const char* scheme, IPathProtocolProvider* provider) = 0;

    /**
     * Removes a path protocol provider.
     * @see addPathProtocolProvider()
     * @param scheme The unique name previously passed to \ref addPathProtocolProvider()
     */
    virtual void removePathProtocolProvider(const char* scheme) = 0;

    /**
     * Runs the extension dependencies solver on the input.
     *
     * Input is a list of extension, they can be names, full id, partial versions like `ommi.foo-2`.
     *
     * If solver succeeds it returns a list of extensions that satisfy the input and `true`, otherwise `errorMessage`
     * contains explanation of what failed.
     *
     * @note The returned array and error message is valid until next call of this function.
     * @param input The \ref SolverInput containing a list of extensions
     * @param[out] extensions If `true` returned, receives an array of \ref ExtensionInfo instances that satisfy
     *   \p input, otherwise undefined
     * @param[out] extensionCount If `true` returned, receives the count of items passed to \p extensions, otherwise
     *   undefined
     * @param[out] errorMessage If `false` returned, receives an error message, otherwise undefined
     * @returns `true` if the solver succeeds and \p extensions and \p extensionCount contain the array of extensions
     *   that satisfy \p input; `false` otherwise, \p errorMessage contains a description of the error, but
     *   \p extensions and \p extensionCount are undefined and should not be accessed.
     */
    virtual bool solveExtensions(const SolverInput& input,
                                 ExtensionInfo** extensions,
                                 size_t* extensionCount,
                                 const char** errorMessage) = 0;

    /**
     * Gets number of local extension packages.
     * @returns the number of local extension packages
     */
    virtual size_t getExtensionPackageCount() const = 0;

    /**
     * Fills an array with local extension packages.
     *
     * @note This function will return all local extensions, including packages for other platforms, incompatible
     *   with current targets.
     * @param extensions An array of \ref ExtensionInfo instances to be filled. It must be large enough to hold
     *   @ref getExtensionPackageCount() entries.
     */
    virtual void getExtensionPackages(ExtensionInfo* extensions) const = 0;

    /**
     * Removes a downloaded extension.
     * @param extId The extension ID to remove
     * @returns `true` if the extension was removed; `false` otherwise
     */
    virtual bool uninstallExtension(const char* extId) = 0;
};

/**
 * omni.ext plugin interface
 *
 * This interface is used to access the \ref ExtensionManager
 */
struct IExtensions
{
    CARB_PLUGIN_INTERFACE("omni::ext::IExtensions", 1, 1)

    /**
     * Creates a new extension manager.
     * @warning This function should not be used; instead call \ref createExtensionManager() to return a RAII pointer.
     * @param changeEventStream The \ref carb::events::IEventStream to push change events. The stream will not be
     *   pumped by the manager. Optional (may be `nullptr`)
     * @returns A pointer to an \ref ExtensionManager
     */
    ExtensionManager*(CARB_ABI* createExtensionManagerPtr)(carb::events::IEventStream* changeEventStream);

    /**
     * Creates a new extension manager.
     * @param changeEventStream The \ref carb::events::IEventStream to push change events. The stream will not be
     *   pumped by the manager. Optional (may be `nullptr`)
     * @returns An RAII pointer to an \ref ExtensionManager
     */
    carb::ObjectPtr<ExtensionManager> createExtensionManager(carb::events::IEventStream* changeEventStream = nullptr);
};


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                             Extension Manager Hooks                                                //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


/**
 * Different moments in extension state lifetime.
 *
 * Used with \ref IExtensionStateChangeHook::onStateChange() to receive notifications at different points of an
 * extension state change.
 */
enum class ExtensionStateChangeType
{
    eBeforeExtensionEnable, //!< Sent right before extension is enabled.
    eAfterExtensionEnable, //!< Sent right after extension is enabled.
    eBeforeExtensionShutdown, //!< Sent right before extension is disabled.
    eAfterExtensionShutdown, //!< Sent right after extension is disabled.
    eCount, //!< Count of extension state change entries.
};

/**
 * An interface that can be implemented to receive extension state changes.
 */
class IExtensionStateChangeHook : public carb::IObject
{
public:
    /**
     * Called by the ExtensionManager upon extension state changes.
     * @see ExtensionManager
     * @param extId The extension ID that is experiencing a state change
     * @param type The \ref ExtensionStateChangeType that describes the type of state change
     */
    virtual void onStateChange(const char* extId, ExtensionStateChangeType type) = 0;
};

//! RAII pointer type
using IExtensionStateChangeHookPtr = carb::ObjectPtr<IExtensionStateChangeHook>;


/**
 * Hook call order.
 *
 * Lower hook values are called first. Negative values are acceptable.
 * @see kDefaultOrder
 */
using Order = int32_t;

/**
 * Default order.
 */
static constexpr Order kDefaultOrder = 0;


/**
 * Hook holder. Hook is valid while the holder is alive.
 */
class IHookHolder : public carb::IObject
{
};

//! RAII pointer type for \ref IHookHolder.
using IHookHolderPtr = carb::ObjectPtr<IHookHolder>;


/**
 * Extension manager subclass with all the hooks that can be installed into it.
 * @see ExtensionManager::getHooks()
 */
class IExtensionManagerHooks
{
public:
    /**
     * Installs a hook for extension state change.
     *
     * The hook will be called for the states specified by \ref ExtensionStateChangeType.
     *
     * You can filter for extensions with specific config/dict to only be called for those. That allows to implement
     * new configuration parameters handled by your hook.
     *
     * @param hook The instance that will be called. The \ref ExtensionManager will retain this object until the
     *   returned \ref IHookHolderPtr expires
     * @param type Extension state change moment to hook into (see \ref ExtensionStateChangeType)
     * @param extFullName Extension name to look for. Hook is only called for extensions with matching name. Can be
     * empty.
     * @param extDictPath Extension dictionary path to look for. Hook is only called if it is present.
     * @param order Hook call order (if there are multiple).
     * @param hookName Hook name for debugging and logging. Optional (may be `nullptr`)
     * @returns a \ref IHookHolder object. When it expires \p hook will be released and no longer active.
     */
    IHookHolderPtr createExtensionStateChangeHook(IExtensionStateChangeHook* hook,
                                                  ExtensionStateChangeType type,
                                                  const char* extFullName = "",
                                                  const char* extDictPath = "",
                                                  Order order = kDefaultOrder,
                                                  const char* hookName = nullptr);
    //! @copydoc createExtensionStateChangeHook()
    virtual IHookHolder* createExtensionStateChangeHookPtr(IExtensionStateChangeHook* hook,
                                                           ExtensionStateChangeType type,
                                                           const char* extFullName = "",
                                                           const char* extDictPath = "",
                                                           Order order = kDefaultOrder,
                                                           const char* hookName = nullptr) = 0;
};


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                                Inline Functions                                                    //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


////////////// ExtensionManagerHooks //////////////

inline IHookHolderPtr IExtensionManagerHooks::createExtensionStateChangeHook(IExtensionStateChangeHook* hook,
                                                                             ExtensionStateChangeType type,
                                                                             const char* extFullName,
                                                                             const char* extDictPath,
                                                                             Order order,
                                                                             const char* hookName)
{
    return carb::stealObject(
        this->createExtensionStateChangeHookPtr(hook, type, extFullName, extDictPath, order, hookName));
}


////////////// IExtensions //////////////

inline carb::ObjectPtr<ExtensionManager> IExtensions::createExtensionManager(carb::events::IEventStream* changeEventStream)
{
    return carb::stealObject(this->createExtensionManagerPtr(changeEventStream));
}

} // namespace ext
} // namespace omni
