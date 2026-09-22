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
//! @brief RTX Settings utilities
//! \todo This should probably not be in Carbonite.
#pragma once

#include "../../carb/dictionary/IDictionary.h"
#include "../../carb/logging/Log.h"
#include "../../carb/settings/ISettings.h"
#include "../../carb/settings/SettingsUtils.h"
#include "../../carb/tasking/TaskingUtils.h"
#include "StringHelpers.h"

#include <algorithm>
#include <sstream>
#include <string>
#include <unordered_map>
#include "md5.h"

namespace rtx
{

/*

Usage:

// init
globalOverrides = Settings::createContext();
vp0Context = Settings::createContext();

// update loop
{
    // Frame begin
    // clone global settings
    Settings::cloneToContext(vp0Context, nullptr);
    Settings::getIDictionary()->makeIntAtPath(vp0Context, "path/to/int", 10);
    // ...
    Settings::applyOverridesToContext(vp0Context, globalOverrides);

    // ...

    // will have all the overrides
    Settings::getIDictionary()->getAsInt(vp0Context, "path/to/int");
}

*/

//! Settings path for RTX default settings.
constexpr char kDefaultSettingsPath[] = "/rtx-defaults";
//! Settings path for RTX settings.
constexpr char kSettingsPath[] = "/rtx";

//! Settings path for persistent default settings.
constexpr char kDefaultPersistentSettingsPath[] = "/persistent-defaults";
//! Settings path for persistent settings.
constexpr char kPersistentSettingsPath[] = "/persistent";

//! Settings path for transient RTX settings.
constexpr char kTransientSettingsPath[] = "/rtx-transient";
//! Settings path for RTX flag settings.
constexpr char kFlagsSettingsPath[] = "/rtx-flags";

// A note on internal setting handling.
// Settings in /rtx-transient/internal and /rtx/internal are automatically mapped to entries in /rtx-transient/hashed
// and /rtx/hashed, respectively. We use the MD5 hash of the full internal setting string as the key inside the "hashed"
// scope. See the comments in InternalSettings.h for more details.

//! Internal setting key.
constexpr char kInternalSettingKey[] = "internal";
//! Hashed setting key
constexpr char kHashedSettingKey[] = "hashed";
//! Settings root keys
constexpr const char* kInternalSettingRoots[] = {
    kSettingsPath,
    kTransientSettingsPath,
};

//! \defgroup rtxsettingflags RTX Settings Flags
//! @{

//! Setting Flags type definition
typedef uint32_t SettingFlags;

//! Value indicating no settings flags.
constexpr SettingFlags kSettingFlagNone = 0;
//! Indicates that a setting flag is transient.
//! \details Do not read or store in USD. Transient settings automatically disables reset feature. Note that settings
//!   under /rtx-transient are transient irrespective of this setting.
constexpr SettingFlags kSettingFlagTransient = 1 << 0;
//! Flag to indicate that resetting of the setting under /rtx-defaults is not allowed.
constexpr SettingFlags kSettingFlagResetDisabled = 1 << 1;
//! Default Setting Flag
constexpr SettingFlags kSettingFlagDefault = kSettingFlagNone;

//! @}

//! Worst case hashed setting root path length.
constexpr size_t kHashedSettingPrefixMaxSize =
    carb_max(carb::countOf(kSettingsPath), carb::countOf(kTransientSettingsPath)) + 1 + carb::countOf(kHashedSettingKey);
//! Worst case hashed setting string length.
constexpr size_t kHashedSettingCStringMaxLength = kHashedSettingPrefixMaxSize + MD5::kDigestStringSize + 1;

/**
 * A class encapsulating render settings.
 */
class RenderSettings
{
public:
    /**
     * Statically-sized container for hashed setting strings.
     * \details We use MD5 hashes which have constant size, so we can compute the worst case hashed setting string size
     * and pass them around on the stack instead of on the heap. In the future this may also help with hashing at build
     * time.
     */
    struct HashedSettingCString
    {
        //! String data
        char data[kHashedSettingCStringMaxLength];
    };

    /**
     * Checks a path to see if it matches the RTX setting root.
     * @param path The path to check
     * @returns `true` if \p path compares equal (case sensitive) to \ref kSettingsPath; `false` otherwise
     */
    static bool isPathRenderSettingsRoot(const char* path)
    {
        size_t rtxSettingsPathLen = CARB_COUNTOF(kSettingsPath) - 1;
        size_t pathLen = strlen(path);
        if (pathLen == rtxSettingsPathLen && strcmp(path, kSettingsPath) == 0)
        {
            return true;
        }

        return false;
    }

    /**
     * Translates the given path to the defaults path.
     * \details For instance if \p cPath is `"/rtx/foo"`, `"/rtx-defaults/foo"` would be returned.
     * @param cPath The path to translate
     * @returns The path key in the defaults tree. See details above.
     */
    static std::string getAssociatedDefaultsPath(const char* cPath)
    {
        carb::cpp::string_view path(carb::cpp::unsafe_length, cPath);

        size_t pos = path.find_first_of("/", 1);

        carb::cpp::string_view parentPath;
        carb::cpp::string_view childPath;

        if (pos == carb::cpp::string_view::npos)
        {
            parentPath = path;
        }
        else
        {
            parentPath = path.substr(0, pos);
            childPath = path.substr(pos);
        }

        return carb::extras::join(parentPath, "-defaults", childPath);
    }

    /**
     * Translates a string into a key-value mapping.
     * \details Only two types of `<KeyType, ValueType>` are allowed: `<uint32_t, std::vector<uint32_t>>`, or
     *   `<std::string, uint32_t>`. A colon (`:`) is the key/value separator and a semicolon (`;`) is the map separator.
     *   This function first splits \p keyToValueDictStr by (`;`) and then each substring is split by (`:`). If exactly
     *   two values are found by this second split, the value is added to \p outputDict. When `ValueType` is a
     *   `std::vector`, the values are found by splitting the value substring by a comma (`,`).
     * @tparam KeyType The type of the key. See above for details.
     * @tparam ValueType The type of the value. See above for details.
     * @param keyToValueDictStr A string that is processed according to the details above
     * @param[out] outputDict The `std::unordered_map` that receives processed key/value pairs. This map is not cleared;
     *   any values that exist in it before this function is called remain, but existing keys that are encountered in
     *   \p keyToValueDictStr will overwrite existing values (however, if `ValueType` is `std::vector` the values are
     *   appended to existing values).
     * @param debugStr (required) a string that will be used in logging if parse errors occur
     */
    template <typename KeyType, typename ValueType>
    static void stringToKeyTypeToValueTypeDictionary(const std::string& keyToValueDictStr,
                                                     std::unordered_map<KeyType, ValueType>& outputDict,
                                                     const char* debugStr)
    {
        // Convert from string to a dictionary mapping KeyType values to ValueType values
        //
        // Example syntax: 0:0; 1:1,2; 2:3,4; 3:5; 4:6; 5:6; 6:6; 7;6"
        // Example syntax: "AsphaltStandard:0; AsphaltWeathered:1; ConcreteRough:2"
        // I.e.: use semicolon (';') to separate dictionary entries from each other,
        //       use colon (':') to separate key from value and
        //       use comma (',') to separate entries in a list of values
        std::stringstream ss(keyToValueDictStr);
        static constexpr char kMappingSep = ';';
        static constexpr char kKeyValueSep = ':';

        // Split by ';' into key:value mappings
        std::vector<std::string> keyToValueStrVec = omni::extras::split(keyToValueDictStr, kMappingSep);
        for (auto& keyToValue : keyToValueStrVec)
        {
            // Split a mapping into its key and value
            std::vector<std::string> keyToValueStrVec = omni::extras::split(keyToValue, kKeyValueSep);

            if (keyToValueStrVec.size() == 2) // this is a key,value pair
            {
                // find an appropriate overloaded function to add a key:value pair to the dictionary
                addValueAtKey(keyToValueStrVec[0], keyToValueStrVec[1], outputDict, debugStr);
            }
        }
    }

    /**
     * A helper function to determine if a setting flag path exists.
     * @param settings \ref carb::settings::ISettings as if by \ref carb::getCachedInterface()
     * @param settingPath The path to check for. \ref kFlagsSettingsPath will be prepended to this value
     * @returns `true` if the settings flag exists; `false` otherwise
     */
    static inline bool hasSettingFlags(carb::settings::ISettings& settings, const char* settingPath)
    {
        std::string settingPathStr(kFlagsSettingsPath);
        settingPathStr += settingPath;
        return settings.getItemType(settingPathStr.c_str()) != carb::dictionary::ItemType::eCount;
    }

    /**
     * A helper function for reading settings flags.
     * @param settings \ref carb::settings::ISettings as if by \ref carb::getCachedInterface()
     * @param settingPath The path to read. \ref kFlagsSettingsPath will be prepended to this value
     * @returns the \ref rtxsettingflags read as an integer from the given \p settingsPath
     */
    static inline SettingFlags getSettingFlags(carb::settings::ISettings& settings, const char* settingPath)
    {
        std::string settingPathStr(kFlagsSettingsPath);
        settingPathStr += settingPath;
        return SettingFlags(settings.getAsInt(settingPathStr.c_str()));
    }

    /**
     * A helper function for writing settings flags.
     * @param settings \ref carb::settings::ISettings as if by \ref carb::getCachedInterface()
     * @param settingPath The path to write. \ref kFlagsSettingsPath will be prepended to this value
     * @param flags The flags to write. These values will overwrite any existing flags
     */
    static inline void setSettingFlags(carb::settings::ISettings& settings, const char* settingPath, SettingFlags flags)
    {
        std::string settingPathStr(kFlagsSettingsPath);
        settingPathStr += settingPath;
        settings.setInt64(settingPathStr.c_str(), flags);
    }

    /**
     * A helper function for deleting a settings flags key.
     * \post The settings path at \ref kFlagsSettingsPath + \p settingPath is destroyed.
     * @param settings \ref carb::settings::ISettings as if by \ref carb::getCachedInterface()
     * @param settingPath The path to delete. \ref kFlagsSettingsPath will be prepended to this value
     */
    static inline void removeSettingFlags(carb::settings::ISettings& settings, const char* settingPath)
    {
        std::string settingPathStr(kFlagsSettingsPath);
        settingPathStr += settingPath;
        settings.destroyItem(settingPathStr.c_str());
    }

    /**
     * Sets the default value for a RTX setting value and backs up the value.
     * \details The \ref carb::settings::ISettings API is used to set the default value at \p settingPath if the setting
     *   key does not exist. If \p flags has neither \ref kSettingFlagTransient and \ref kSettingFlagResetDisabled set,
     *   then the default path is constructed by \ref getAssociatedDefaultsPath(). If the default path is under the
     *   `/persistent` root, the default path setting is updated with \p value, otherwise the default path setting is
     *   updated with the current value read from \p settingPath. Finally, \ref setSettingFlags() is called with
     *   \p settingPath and \p flags.
     * @param settingPath the setting path to set default for and to back up
     * @param value the default value to set at \p settingPath
     * @param flags \ref rtxsettingflags to apply to \p settingPath
     */
    template <typename SettingType>
    static void setAndBackupDefaultSetting(const char* settingPath,
                                           SettingType value,
                                           SettingFlags flags = kSettingFlagDefault)
    {
        carb::settings::ISettings* settings = getISettings();
        settings->setDefault<SettingType>(settingPath, value);

        bool allowReset = (flags & (kSettingFlagTransient | kSettingFlagResetDisabled)) == 0;
        if (allowReset)
        {
            std::string defaultSettingPath = getAssociatedDefaultsPath(settingPath);
            if (!defaultSettingPath.empty())
            {
                static constexpr carb::cpp::string_view persistentSettingsPath(kPersistentSettingsPath);
                std::string path(defaultSettingPath);
                if (path.substr(0, persistentSettingsPath.size()) == persistentSettingsPath.data())
                {
                    settings->set<SettingType>(defaultSettingPath.c_str(), value);
                }
                else
                {
                    settings->setDefault<SettingType>(
                        defaultSettingPath.c_str(), settings->get<SettingType>(settingPath));
                }
            }
        }
        // Set per setting flag (persistent, etc.)
        setSettingFlags(*settings, settingPath, flags);
    }

    /**
     * Returns a hashed setting string based on the given setting path.
     * @param s The setting path
     * @returns A hashed setting string based on \p s
     */
    static inline std::string getInternalSettingString(const char* s)
    {
        return std::string(getHashedSettingString(s).data);
    }

    // TODO: Make private? It looks like this function is just subscribed for change events in
    // setAndBackupPersistentDefaultSetting.
    //! @private
    static void updateSetting(const carb::dictionary::Item* changedItem,
                              carb::dictionary::ChangeEventType eventType,
                              void* userData)
    {
        CARB_UNUSED(eventType);
        if (!changedItem)
        {
            CARB_LOG_ERROR("Unexpected setting deletion");
        }

        const char* path = reinterpret_cast<const char*>(userData);
        carb::dictionary::IDictionary* dictionary = getIDictionary();
        carb::settings::ISettings* settings = getISettings();

        carb::dictionary::ItemType itemType = dictionary->getItemType(changedItem);
        if (itemType == carb::dictionary::ItemType::eString)
        {
            settings->setString(path, dictionary->getStringBuffer(changedItem));
        }
        else if (itemType == carb::dictionary::ItemType::eFloat)
        {
            settings->setFloat(path, dictionary->getAsFloat(changedItem));
        }
        else if (itemType == carb::dictionary::ItemType::eInt)
        {
            settings->setInt(path, dictionary->getAsInt(changedItem));
        }
        else if (itemType == carb::dictionary::ItemType::eBool)
        {
            settings->setBool(path, dictionary->getAsBool(changedItem));
        }
    }

    /**
     * Sets a setting value to a given default value and back up the previous value.
     * \warning The \p settingPath pointer value is captured by this function. Its lifetime must be for the rest of the
     *   application, or undefined behavior will occur.
     * @tparam SettingType the type of the value
     * @param settingPath the setting path to set default for and to back up. **NOTE** see warning above
     * @param value The default value to assign
     */
    template <typename SettingType>
    static void setAndBackupPersistentDefaultSetting(const char* settingPath, SettingType value)
    {
        carb::settings::ISettings* settings = getISettings();

        std::string persistentPath = std::string("/persistent") + settingPath;
        settings->setDefault<SettingType>(persistentPath.c_str(), value);

        std::string defaultSettingPath = getAssociatedDefaultsPath(persistentPath.c_str());
        if (!defaultSettingPath.empty())
        {
            static constexpr carb::cpp::string_view persistentSettingsPath(kPersistentSettingsPath);
            std::string path(defaultSettingPath);
            if (path.substr(0, persistentSettingsPath.size()) == persistentSettingsPath.data())
            {
                settings->set<SettingType>(defaultSettingPath.c_str(), value);
            }
            else
            {
                settings->set<SettingType>(
                    defaultSettingPath.c_str(), settings->get<SettingType>(persistentPath.c_str()));
            }
        }

        settings->subscribeToNodeChangeEvents(
            persistentPath.c_str(), RenderSettings::updateSetting, (void*)(settingPath));

        settings->set<SettingType>(settingPath, settings->get<SettingType>(persistentPath.c_str()));
    }

    /**
     * Sets a setting value to a given array value and backs up the previous value.
     * @tparam SettingArrayType the type of the elements of the array
     * @param settingPath the setting path to set default for and to back up
     * @param array The array of values to assign as the default for \p settingPath
     * @param arrayLength The number of items in \p array
     * @param flags \ref rtxsettingflags to apply to \p settingPath
     */
    template <typename SettingArrayType>
    static void setAndBackupDefaultSettingArray(const char* settingPath,
                                                const SettingArrayType* array,
                                                size_t arrayLength,
                                                SettingFlags flags = kSettingFlagDefault)
    {
        carb::settings::ISettings* settings = getISettings();
        settings->setDefaultArray<SettingArrayType>(settingPath, array, arrayLength);

        bool allowReset = (flags & (kSettingFlagTransient | kSettingFlagResetDisabled)) == 0;
        if (allowReset)
        {
            std::string defaultSettingPath = getAssociatedDefaultsPath(settingPath);
            if (!defaultSettingPath.empty())
            {
                settings->destroyItem(defaultSettingPath.c_str());
                size_t arrayLength = settings->getArrayLength(settingPath);
                for (size_t idx = 0; idx < arrayLength; ++idx)
                {
                    std::string elementPath = std::string(settingPath) + "/" + std::to_string(idx);
                    std::string defaultElementPath = std::string(defaultSettingPath) + "/" + std::to_string(idx);
                    settings->setDefault<SettingArrayType>(
                        defaultElementPath.c_str(), settings->get<SettingArrayType>(elementPath.c_str()));
                }
            }
        }
        // Set per setting flag (persistent, etc.)
        setSettingFlags(*settings, settingPath, flags);
    }

    /**
     * Reads the default value for the given path and restores it.
     * @param path The setting path to restore
     */
    static void resetSettingToDefault(const char* path)
    {
        carb::dictionary::IDictionary* dictionary = getIDictionary();
        carb::settings::ISettings* settings = getISettings();

        std::string defaultsPathStorage;
        defaultsPathStorage = getAssociatedDefaultsPath(path);

        // Write lock so we can safely hold the dictionary pointer while writing to settings
        carb::settings::ScopedWrite writeLock;

        const carb::dictionary::Item* srcItem = settings->getSettingsDictionary(defaultsPathStorage.c_str());
        carb::dictionary::ItemType srcItemType = dictionary->getItemType(srcItem);
        size_t srcItemArrayLength = dictionary->getArrayLength(srcItem);

        if ((srcItemType == carb::dictionary::ItemType::eDictionary) && (srcItemArrayLength == 0))
        {
            resetSectionToDefault(path, writeLock);
            return;
        }

        switch (srcItemType)
        {
            case carb::dictionary::ItemType::eBool:
            {
                settings->set<bool>(path, dictionary->getAsBool(srcItem));
                break;
            }
            case carb::dictionary::ItemType::eInt:
            {
                settings->set<int32_t>(path, dictionary->getAsInt(srcItem));
                break;
            }
            case carb::dictionary::ItemType::eFloat:
            {
                settings->set<float>(path, dictionary->getAsFloat(srcItem));
                break;
            }
            case carb::dictionary::ItemType::eString:
            {
                settings->set<const char*>(path, dictionary->getStringBuffer(srcItem));
                break;
            }
            case carb::dictionary::ItemType::eDictionary:
            {
                if (srcItemArrayLength > 0)
                {
                    // FIXME: This is somewhat unsafe as update() has the potential to clobber the
                    //        input pointer if the settings trees overlap.
                    settings->update(path, srcItem, nullptr, carb::dictionary::kUpdateItemOverwriteOriginal, nullptr);
                }
                break;
            }
            default:
                break;
        }
    }

    /**
     * Restores the subtree at the given path from the backed up values.
     * @param path The subtree setting path
     * @param writeLock The settings lock to ensure this is called under a lock.
     */
    static void resetSectionToDefault(const char* path, const carb::settings::ScopedWrite& writeLock)
    {
        CARB_UNUSED(writeLock);
        carb::settings::ISettings* settings = getISettings();

        std::string defaultsPathStorage;
        const char* defaultsPath = nullptr;

        defaultsPathStorage = getAssociatedDefaultsPath(path);
        if (!defaultsPathStorage.empty())
        {
            defaultsPath = defaultsPathStorage.c_str();
        }

        if (defaultsPath)
        {
            // Do not delete existing original settings.
            // If the source item exists (rtx-default value), overwrite the destination (original rtx value).
            // Otherwise, leave them as-is. We want to keep original values until we find some default values in the
            // future. Plugins may load at a later time and we should not remove original values until we have some
            // default values.
            // FIXME: This is somewhat unsafe as update() has the potential to clobber the
            //        input pointer if the settings trees overlap.
            settings->update(path, settings->getSettingsDictionary(defaultsPath), nullptr,
                             carb::dictionary::kUpdateItemOverwriteOriginal, nullptr);
        }
        else
        {
            CARB_LOG_ERROR("%s: failed to resolve default paths", __func__);
        }
    }

    /**
     * Creates a root level dictionary item.
     * \details This item is created as via \ref carb::dictionary::IDictionary::createItem() with `<rtx context>` as the
     *   name.
     * @returns a \ref carb::dictionary::Item that is of type \ref carb::dictionary::ItemType::eDictionary
     */
    static carb::dictionary::Item* createContext()
    {
        return getIDictionary()->createItem(nullptr, "<rtx context>", carb::dictionary::ItemType::eDictionary);
    }

    /**
     * Helper function to destroy a dictionary item.
     * \details This function is a helper function to call \ref carb::dictionary::IDictionary::destroyItem().
     * @param ctx the \ref carb::dictionary::Item to destroy
     */
    static void destroyContext(carb::dictionary::Item* ctx)
    {
        getIDictionary()->destroyItem(ctx);
    }

    /**
     * Copies a source context to a destination context.
     * \warning This function appears to have a bug where \p dstContext is used after destroyed if \p srcContext is not
     *   `nullptr`.
     * @param dstContext The destination context to overwrite
     * @param srcContext The source context to copy to \p dstContext. Maybe `nullptr` to re-initialize \p dstContext.
     */
    static void cloneToContext(carb::dictionary::Item* dstContext, carb::dictionary::Item* srcContext)
    {
        carb::dictionary::IDictionary* dict = getIDictionary();
        carb::settings::ISettings* settings = getISettings();

        dict->destroyItem(dstContext);
        if (srcContext)
        {
            // TODO: It is undefined behavior to use dstContext after destroyItem above
            dict->update(dstContext, "", srcContext, "", carb::dictionary::kUpdateItemOverwriteOriginal, nullptr);
        }
        else
        {
            dstContext = settings->createDictionaryFromSettings(kSettingsPath);
        }
    }

    /**
     * Copies a subtree over the destination subtree.
     * @param dstContext The destination to overwrite
     * @param overridesContext The subtree to write over \p dstContext
     */
    static void applyOverridesToContext(carb::dictionary::Item* dstContext, carb::dictionary::Item* overridesContext)
    {
        if (!overridesContext)
        {
            CARB_LOG_ERROR("%s needs context to override from", __FUNCTION__);
        }
        carb::dictionary::IDictionary* dict = getIDictionary();

        dict->update(dstContext, "", overridesContext, "", carb::dictionary::kUpdateItemOverwriteOriginal, nullptr);
    }

    /**
     * Dictionary access helper function.
     * @returns \ref carb::dictionary::IDictionary as by \ref carb::getCachedInterface()
     */
    static carb::dictionary::IDictionary* getIDictionary()
    {
        return carb::getCachedInterface<carb::dictionary::IDictionary>();
    }

    /**
     * Settings access helper function.
     * @returns \ref carb::settings::ISettings as by \ref carb::getCachedInterface()
     */
    static carb::settings::ISettings* getISettings()
    {
        return carb::getCachedInterface<carb::settings::ISettings>();
    }

    /**
     * Translates plaintext internal settings to hashed settings and removes the plaintext settings.
     * \details This is to ensure that the plaintext internal settings are not inadvertently saved to USD.
     */
    static void hashInternalRenderSettings()
    {
        auto settings = getISettings();
        auto hashRtxSetting = [&settings](const char* itemPath, uint32_t, void*) -> uint32_t {
            const carb::dictionary::ItemType itemType = settings->getItemType(itemPath);

            if (itemType == carb::dictionary::ItemType::eDictionary)
            {
                return 0;
            }

            const auto newHashedPath = getHashedSettingString(itemPath);

            switch (settings->getItemType(itemPath))
            {
                case carb::dictionary::ItemType::eBool:
                    settings->setBool(newHashedPath.data, settings->getAsBool(itemPath));
                    break;
                case carb::dictionary::ItemType::eFloat:
                    settings->setFloat(newHashedPath.data, settings->getAsFloat(itemPath));
                    break;
                case carb::dictionary::ItemType::eInt:
                    settings->setInt(newHashedPath.data, settings->getAsInt(itemPath));
                    break;
                case carb::dictionary::ItemType::eString:
                    // grabbing the string buffer is safe because this function is called under a ScopedWrite
                    settings->setString(newHashedPath.data, settings->getStringBuffer(itemPath));
                    break;
                case carb::dictionary::ItemType::eDictionary:
                    CARB_FALLTHROUGH;
                default:
                    CARB_ASSERT(0);
            }

            if (hasSettingFlags(*settings, itemPath))
            {
                setSettingFlags(*settings, newHashedPath.data, getSettingFlags(*settings, itemPath));
                removeSettingFlags(*settings, itemPath);
            }

            return 0;
        };

        carb::dictionary::IDictionary* dictionary = getIDictionary();

        for (const char* root : kInternalSettingRoots)
        {
            std::stringstream ss;
            ss << root << '/' << kInternalSettingKey;
            const std::string internalRoot = ss.str();

            // hashRtxSetting() modifies settings so we need to hold a write lock to safely walk settings
            carb::settings::ScopedWrite writeLock;
            carb::settings::walkSettings(dictionary, settings, carb::dictionary::WalkerMode::eSkipRoot,
                                         internalRoot.c_str(), 0u, hashRtxSetting, nullptr);
            settings->destroyItem(internalRoot.c_str());
        }
    }

private:
    // Key : Value = uint32_t : std::vector<uint32_t>
    static void addValueAtKey(std::string key,
                              std::string value,
                              std::unordered_map<uint32_t, std::vector<uint32_t>>& outputDict,
                              const char* debugStr)
    {
        static const char kListElemSep = ',';
        int32_t intKey = 0;
        if (!omni::extras::stringToInteger(key, intKey))
        {
            CARB_LOG_WARN("Non-integer value %s set in \"%s\"", key.c_str(), debugStr);
        }

        // Split the value into a list of values
        std::vector<std::string> intVecStrVec = omni::extras::split(value, kListElemSep);

        int32_t intVecValueEntry = 0;
        outputDict[(uint32_t)intKey].clear();
        for (auto& intVecValueEntryStr : intVecStrVec)
        {
            if (omni::extras::stringToInteger(intVecValueEntryStr, intVecValueEntry))
            {
                outputDict[(uint32_t)intKey].push_back((uint32_t)intVecValueEntry);
            }
            else
            {
                CARB_LOG_WARN("Non-integer value %s set in \"%s\"", intVecValueEntryStr.c_str(), debugStr);
            }
        }
    }
    // Key : Value = std::string : uint32_t
    static void addValueAtKey(std::string key,
                              std::string value,
                              std::unordered_map<std::string, uint32_t>& outputDict,
                              const char* debugStr)
    {
        int32_t outInt = 0;
        if (omni::extras::stringToInteger(value, outInt))
        {
            outputDict[key] = (uint32_t)outInt;
        }
        else
        {
            CARB_LOG_WARN("Non-integer value %s set in \"%s\"", key.c_str(), debugStr);
        }
    }

    static HashedSettingCString getHashedSettingString(const char* settingStr)
    {
        constexpr size_t sizeOfRtxSettingsRoot = carb::countOf(kSettingsPath) - 1;
        const bool isRtxSettingsPath =
            strncmp(settingStr, kSettingsPath, sizeOfRtxSettingsRoot) == 0 && settingStr[sizeOfRtxSettingsRoot] == '/';
        // Default to kTransientSettingsPath for anything outside /rtx/.
        // We don't promise that anything works for paths not rooted in /rtx[-transient]/internal, but implement
        // reasonable behavior rather than crash or map all invalid settings to a null string. Improperly rooted strings
        // will work fine except that hashInternalRenderSettings() won't know to translate them.
        const char* hashedRoot = isRtxSettingsPath ? kSettingsPath : kTransientSettingsPath;

        return getHashedSettingString(
            MD5::getDigestString(MD5::run((const uint8_t*)settingStr, strlen(settingStr))), hashedRoot);
    }

    static HashedSettingCString getHashedSettingString(const MD5::DigestString& digestStr, const char* root)
    {
        HashedSettingCString result = {};

        char* s = std::copy_n(root, strlen(root), result.data);
        *s++ = '/';
        s = std::copy_n(kHashedSettingKey, carb::countOf(kHashedSettingKey) - 1, s);
        *s++ = '/';
        s = std::copy_n(digestStr.s, MD5::kDigestStringSize, s);
        *s = '\0';

        return result;
    }
};

/**
 * Dummy function.
 * \todo remove this?
 * @returns `false`
 */
inline bool enableAperture()
{
    // Enabling Aperture mode adds 2 ray types.
    return false;
}

/**
 * Caches and returns the value of "/rtx/mdltranslator/distillMaterial".
 * \details The value is read from \ref carb::settings::ISettings once and cached; future calls to this function are
 *   very fast.
 * @thread_safety This function is thread safe.
 * @returns The value read from `/rtx/mdltranslator/distillMaterial`
 */
inline bool enableMDLDistilledMtls()
{
    auto&& init = [] {
        carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
        return settings->getAsBool("/rtx/mdltranslator/distillMaterial");
    };
    static bool result = init();
    return result;
}

/**
 * Caches and returns whether the value of "/rtx/rendermode" is "abisko".
 * \details The value is read from \ref carb::settings::ISettings once and cached; future calls to this function are
 *   very fast.
 * @thread_safety This function is thread safe.
 * @returns `true` if the value read from `/rtx/rendermode` is equal to `abisko`
 */
inline bool enableAbiskoMode()
{
    auto&& init = [] {
        carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
        carb::settings::ScopedRead readLock; // read lock to hold the pointer
        const char* renderMode = settings->getStringBuffer("/rtx/rendermode");
        return renderMode && strcmp(renderMode, "abisko") == 0;
    };
    static bool result = init();
    return result;
}

// Returns how many ray types we are going to use during the whole Kit rendering. This CAN'T be changed once the
// renderer is initialized
/**
 * Returns how many ray types the renderer will use based on settings.
 * \details This value cannot be changed once the renderer is initialized. This value is read from
 *   \ref carb::settings::ISettings the first time this function is called and cached so that future calls are very
 *   fast.
 * @thread_safety This function is thread safe.
 * @returns The number of ray types the renderer will use
 */
inline uint32_t getRayTypeCount()
{
    auto&& init = [] {
        uint32_t rayCount = 2; // MATERIAL_RAY and VISIBILITY_RAY for RTX are always available
        if (!rtx::enableAbiskoMode()) // Abisko only has two ray types
        {
            if (rtx::enableAperture())
            {
                rayCount += 2; // APERTURE_MATERIAL_RAY and APERTURE_VISIBILTY_RAY
            }

            if (rtx::enableMDLDistilledMtls())
            {
                rayCount += 1; // DISTILLED_MATERIAL_RAY
            }
        }
        return rayCount;
    };
    static uint32_t result = init();
    return result;
}


/**
 * A helper function that atomically sets the setting value at path if and only if it doesn't exist.
 * @param settings \ref carb::settings::ISettings as if by \ref carb::getCachedInterface()
 * @param path The settings path to check
 * @param value The value to write to \p path if it doesn't exist
 * @retval true The value did not exist and was atomically set to \p value
 * @retval false The value already existed and was not set
 */
inline bool setDefaultBoolEx(carb::settings::ISettings* settings, const char* path, bool value)
{
    // Unfortunately need a write lock since we might be writing
    carb::settings::ScopedWrite writeLock;
    if (settings->getItemType(path) != carb::dictionary::ItemType::eCount)
        return false;
    settings->setBool(path, value);
    return true;
}

} // namespace rtx
