// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief carb.settings utilities
#pragma once

#include "../dictionary/DictionaryUtils.h"
#include "../dictionary/ISerializer.h"
#include "../cpp/Optional.h"
#include "ISettings.h"

#include <atomic>
#include <mutex>
#include <string>

namespace carb
{
namespace settings
{

/**
 * Retrieves a std::string from a setting key for simplicity.
 *
 * Typically to retrieve a string value from \ref carb::dictionary::Item,
 * \ref ISettings::createStringBufferFromItemValue() must be called, but this means that
 * \ref ISettings::destroyStringBuffer() must be called when finished. This function instead returns a `std::string`.
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path to retrieve.
 * @param defaultValue The value that is returned if \p path is not a valid path.
 * @returns A `std::string` representation of the item value.
 * @see ISettings::createStringBufferFromItemValue(), getStringFromItemValueAt().
 */
inline std::string getStringFromItemValue(const ISettings* settings, const char* path, const std::string& defaultValue = "")
{
    const char* stringBuf = settings->createStringBufferFromItemValue(path);
    if (!stringBuf)
        return defaultValue;
    std::string returnString = stringBuf;
    settings->destroyStringBuffer(stringBuf);
    return returnString;
}

/**
 * Retrieves a std::string from an array setting key for simplicity.
 *
 * Typically to retrieve a string value from an array of \ref carb::dictionary::Item objects,
 * \ref ISettings::createStringBufferFromItemValueAt() must be called, but this means that
 * \ref ISettings::destroyStringBuffer() must be called when finished. This function instead returns a `std::string`.
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path to retrieve (must be an array or \p defaultValue will be returned).
 * @param index The array index to retrieve.
 * @param defaultValue The value that is returned if \p path is not a valid path, not an array, or the index does not
 *   exist.
 * @returns A `std::string` representation of the item value.
 * @see ISettings::createStringBufferFromItemValueAt(), getStringFromItemValue().
 */
inline std::string getStringFromItemValueAt(const ISettings* settings,
                                            const char* path,
                                            size_t index,
                                            const std::string& defaultValue = "")
{
    const char* stringBuf = settings->createStringBufferFromItemValueAt(path, index);
    if (!stringBuf)
        return defaultValue;
    std::string returnString = stringBuf;
    settings->destroyStringBuffer(stringBuf);
    return returnString;
}

/**
 * Retrieves a std::string from a string-type setting for simplicity.
 *
 * Equivalent to:
 * ```cpp
 * auto p = settings->getStringBuffer(path); return p ? std::string(p) : defaultValue;
 * ```
 * @see ISettings::getStringBuffer, getStringAt()
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path to retrieve (must be a string or \p defaultValue will be returned).
 * @param defaultValue The value that is returned if \p path is not a valid path or not a string setting.
 * @returns A `std::string` representation of the item value.
 */
inline std::string getString(const ISettings* settings, const char* path, const std::string& defaultValue = "")
{
    ScopedRead lock;
    const char* value = settings->getStringBuffer(path);
    if (!value)
        return defaultValue;
    return value;
}

/**
 * Retrieves a std::string from a string-type setting for simplicity.
 *
 * Equivalent to:
 * ```cpp
 * auto p = settings->getStringBuffer(path); return p ? std::string(p) : defaultValue;
 * ```
 * @see ISettings::getStringBuffer, getStringAt()
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path to retrieve (must be a string or \p defaultValue will be returned).
 * @returns A `cpp::optional` object that both indicates whether the requested value could be
 *          retrieved and the `std::string` representation of the item value itself if the value
 *          could be retrieved.
 */
inline cpp::optional<std::string> getStringOpt(const ISettings* settings, const char* path)
{
    ScopedRead lock;
    const char* value = settings->getStringBuffer(path);
    if (value == nullptr)
    {
        return carb::cpp::nullopt;
    }
    else
    {
        return cpp::make_optional<std::string>(value);
    }
}

/**
 * Retrieves a std::string from an array of string-type setting for simplicity.
 *
 * Equivalent to:
 * ```cpp
 * auto p = settings->getStringBufferAt(path, index); return p ? std::string(p) : defaultValue;
 * ```
 * @see ISettings::getStringBuffer, getString()
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path to retrieve (must be an array of strings or \p defaultValue will be returned).
 * @param index The array index to retrieve.
 * @param defaultValue The value that is returned if \p path is not a valid path, not an array of strings, or the
 *   index does not exist.
 * @returns A `std::string` representation of the item value.
 */
inline std::string getStringAt(const ISettings* settings,
                               const char* path,
                               size_t index,
                               const std::string& defaultValue = "")
{
    ScopedRead lock;
    const char* value = settings->getStringBufferAt(path, index);
    if (!value)
        return defaultValue;
    return value;
}

/**
 * Retrieves a std::string from an array of string-type setting for simplicity.
 *
 * Equivalent to:
 * ```cpp
 * auto p = settings->getStringBufferAt(path, index); return p ? std::string(p) : defaultValue;
 * ```
 * @see ISettings::getStringBuffer, getString()
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path to retrieve (must be an array of strings or \p defaultValue will be returned).
 * @param index The array index to retrieve.
 * @returns A `cpp::optional` object that both indicates whether the requested value could be
 *          retrieved and the `std::string` representation of the item value itself if the value
 *          could be retrieved.
 */
inline cpp::optional<std::string> getStringAtOpt(const ISettings* settings, const char* path, size_t index)
{
    ScopedRead lock;
    const char* value = settings->getStringBufferAt(path, index);
    if (value == nullptr)
    {
        return carb::cpp::nullopt;
    }
    else
    {
        return cpp::make_optional<std::string>(value);
    }
}

/**
 * A helper function for setting a `std::vector<int>` as an array of integers.
 *
 * Equivalent to:
 * ```cpp
 * settings->setIntArray(path, array.data(), array.size());
 * ```
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. See \ref ISettings::setIntArray for details.
 * @param array A vector containing the integer values for the setting value.
 */
inline void setIntArray(ISettings* settings, const char* path, const std::vector<int>& array)
{
    settings->setIntArray(path, array.data(), array.size());
}

/**
 * A helper function for setting a `std::vector<int64_t>` as an array of 64-bit integers.
 *
 * Equivalent to:
 * ```cpp
 * settings->setInt64Array(path, array.data(), array.size());
 * ```
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. See \ref ISettings::setInt64Array for details.
 * @param array A vector containing the 64-bit integer values for the setting value.
 */
inline void setIntArray(ISettings* settings, const char* path, const std::vector<int64_t>& array)
{
    settings->setInt64Array(path, array.data(), array.size());
}

/**
 * A helper function for setting a `std::vector<float>` as an array of floats.
 *
 * Equivalent to:
 * ```cpp
 * settings->setFloatArray(path, array.data(), array.size());
 * ```
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. See \ref ISettings::setFloatArray for details.
 * @param array A vector containing the float values for the setting value.
 */
inline void setFloatArray(ISettings* settings, const char* path, const std::vector<float>& array)
{
    settings->setFloatArray(path, array.data(), array.size());
}

/**
 * A helper function for setting a `std::vector<double>` as an array of doubles.
 *
 * Equivalent to:
 * ```cpp
 * settings->setFloatArray(path, array.data(), array.size());
 * ```
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. See \ref ISettings::setFloat64Array for details.
 * @param array A vector containing the double values for the setting value.
 */
inline void setFloatArray(ISettings* settings, const char* path, const std::vector<double>& array)
{
    settings->setFloat64Array(path, array.data(), array.size());
}

/**
 * A helper function for setting a `std::vector<bool>` as an array of bools.
 *
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. See \ref ISettings::setBoolArray for details.
 * @param array A vector containing the bool values for the setting value.
 * @note \p array is first converted to an array of `bool` on the stack and then passed in to
 *   \ref ISettings::setBoolArray. If the stack is particularly small and \p array is particularly large, stack space
 *   may be exceeded. In this case, it is advised to call \ref ISettings::setBoolArray directly.
 */
inline void setBoolArray(ISettings* settings, const char* path, const std::vector<bool>& array)
{
    const size_t arraySize = array.size();
    // Since std::vector<bool> is typically specialized and doesn't function like normal vector (i.e. no data()), first
    // convert to an array of bools on the stack.
    bool* pbools = CARB_STACK_ALLOC(bool, arraySize);
    for (size_t i = 0; i != arraySize; ++i)
        pbools[i] = array[i];
    settings->setBoolArray(path, pbools, arraySize);
}

/**
 * A helper function for reading a setting value that is an array of string values as `std::vector<std::string>`.
 *
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. If this path does not exist or is not an array, an empty vector will be returned.
 * @param defaultValue The value that is returned for each array item if the array item is not a string value.
 * @returns a `std::vector<std::string>` of all string array elements. If the value at \p path does not
 *   exist or is not an array type, an empty vector is returned. Otherwise, a vector is returned with the number of
 *   elements matching the number of elements in the value at \p path (as determined via
 *   \ref ISettings::getArrayLength). Any array elements that are not string types will instead be \p defaultValue.
 * @see getStringArrayFromItemValues() for a function that handles values of mixed or non-string types.
 */
inline std::vector<std::string> getStringArray(ISettings* settings, const char* path, const std::string& defaultValue = "")
{
    dictionary::ScopedRead readLock(
        *carb::getCachedInterface<dictionary::IDictionary>(), settings->getSettingsDictionary(""));
    std::vector<std::string> array(settings->getArrayLength(path));
    for (size_t i = 0, arraySize = array.size(); i < arraySize; ++i)
    {
        array[i] = getStringAt(settings, path, i, defaultValue);
    }
    return array;
}

/**
 * A helper function for reading a setting value that is an array of mixed values as `std::vector<std::string>`.
 *
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. If this path does not exist or is not an array, an empty vector will be returned.
 * @param defaultValue The value that is returned for each array item if the array item cannot be converted to a string
 *   value.
 * @returns a `std::vector<std::string>` of all array elements converted to a string. If the value at \p path does not
 *   exist or is not an array type, an empty vector is returned. Otherwise, a vector is returned with the number of
 *   elements matching the number of elements in the value at \p path (as determined via
 *   \ref ISettings::getArrayLength). Any array elements that cannot be converted to a string will instead be
 *   \p defaultValue.
 */
inline std::vector<std::string> getStringArrayFromItemValues(ISettings* settings,
                                                             const char* path,
                                                             const std::string& defaultValue = "")
{
    dictionary::ScopedRead readLock(
        *carb::getCachedInterface<dictionary::IDictionary>(), settings->getSettingsDictionary(""));
    std::vector<std::string> array(settings->getArrayLength(path));
    for (size_t i = 0, arraySize = array.size(); i < arraySize; ++i)
    {
        array[i] = getStringFromItemValueAt(settings, path, i, defaultValue);
    }
    return array;
}

/**
 * A helper function for setting a `std::vector<bool>` as an array of strings.
 *
 * @param settings The acquired \ref ISettings interface.
 * @param path The setting key path. See \ref ISettings::setStringArray for details.
 * @param array A vector containing the bool values for the setting value.
 * @note \p array is first converted to an array of `const char*` on the stack and then passed in to
 *   \ref ISettings::setStringArray. If the stack is particularly small and \p array is particularly large, stack space
 *   may be exceeded. In this case, it is advised to call \ref ISettings::setStringArray directly.
 */
inline void setStringArray(ISettings* settings, const char* path, const std::vector<std::string>& array)
{
    const size_t arraySize = array.size();
    const char** pp = CARB_STACK_ALLOC(const char*, arraySize);
    for (size_t i = 0; i != arraySize; ++i)
        pp[i] = array[i].c_str();
    settings->setStringArray(path, pp, arraySize);
}

/**
 * A helper function to load settings from a file.
 *
 * This function first creates a dictionary from a file using the provided \p serializer passed to
 * \ref carb::dictionary::createDictionaryFromFile(). The dictionary is then applied to the settings system with
 * \ref ISettings::update at settings path \p path using the \ref carb::dictionary::overwriteOriginalWithArrayHandling()
 * method. The created  dictionary is then destroyed. When the function returns, the settings from the given \p filename
 * are available to be queried through the settings system.
 * @param settings The acquired \ref ISettings interface.
 * @param path The path at which the loaded settings are placed. An empty string or "/" is considered the root of the
 *   settings tree.
 * @param dictionary The acquired \ref dictionary::IDictionary interface.
 * @param serializer The \ref dictionary::ISerializer interface to use. The file format should match the format of
 *   \p filename. I.e. if \p filename is a json file, the \ref dictionary::ISerializer from
 *   *carb.dictionary.serializer-json.plugin* should be used.
 * @param filename The filename to read settings from.
 */
inline void loadSettingsFromFile(ISettings* settings,
                                 const char* path,
                                 dictionary::IDictionary* dictionary,
                                 dictionary::ISerializer* serializer,
                                 const char* filename)
{
    carb::dictionary::Item* settingsFromFile = carb::dictionary::createDictionaryFromFile(serializer, filename);
    if (settingsFromFile)
    {
        settings->update(path, settingsFromFile, nullptr, dictionary::overwriteOriginalWithArrayHandling, dictionary);
        dictionary->destroyItem(settingsFromFile);
    }
}

/**
 * A helper function to save settings to a file.
 *
 * @see dictionary::saveFileFromDictionary()
 * @param settings The acquired \ref ISettings interface.
 * @param serializer The \ref dictionary::ISerializer interface to use. The serializer should match the desired output
 *   file format. I.e. if a json file is desired, the \ref dictionary::ISerializer from
 *   *carb.dictionary.serializer-json.plugin* should be used.
 * @param path The settings path to save. An empty string or "/" is considered the root of the settings tree.
 * @param filename The filename to write settings into. This file will be overwritten.
 * @param serializerOptions Options that will be passed to \p serializer.
 */
inline void saveFileFromSettings(const ISettings* settings,
                                 dictionary::ISerializer* serializer,
                                 const char* path,
                                 const char* filename,
                                 dictionary::SerializerOptions serializerOptions)
{
    ScopedRead lock;
    const dictionary::Item* settingsDictionaryAtPath = settings->getSettingsDictionary(path);
    dictionary::saveFileFromDictionary(serializer, settingsDictionaryAtPath, filename, serializerOptions);
}

/**
 * A function for walking all of the settings from a given root.
 *
 * Similar to \ref dictionary::walkDictionary().
 * @tparam ElementData Type of the second parameter passed to \p onItemFn.
 * @tparam OnItemFnType Type of the invocable \p onItemFn.
 * @param idict The acquired \ref dictionary::IDictionary interface.
 * @param settings The acquired \ref ISettings interface.
 * @param walkerMode See \ref dictionary::WalkerMode.
 * @param rootPath The settings root to begin the walk at. An empty string or "/" is considered the root of the settings
 *   tree.
 * @param rootElementData A value of type `ElementData` that is passed as the second parameter to \p onItemFn. This
 *   value is not used by `walkSettings()` and is intended to be used only by the caller and the \p onItemFn invocable.
 * @param onItemFn An invocable that is invoked for each setting value encountered. The type of this invocable should be
 *   `ElementData(const char*, ElementData, void*)`: the encountered item path is the first parameter, followed by the
 *   parent's `ElementData`, followed by \p userData. The return value is only used for dictionary and array settings:
 *   the returned `ElementData` will be passed to \p onItemFn invocations for child settings; the return value is
 *   otherwise ignored.
 * @param userData A caller-specific value that is not used but is passed to every \p onItemFn invocation.
 *
 * @note The callback is fired with a @ref ScopedRead held to ensure that the dictionary can  be walked safely.
 *       If your callback writes to settings, you must hold a @ref ScopedWrite while calling walkSettings()
 *       to ensure the operation is thread safe.
 */
template <typename ElementData, typename OnItemFnType>
inline void walkSettings(carb::dictionary::IDictionary* idict,
                         carb::settings::ISettings* settings,
                         dictionary::WalkerMode walkerMode,
                         const char* rootPath,
                         ElementData rootElementData,
                         OnItemFnType onItemFn,
                         void* userData)
{
    using namespace carb;

    if (!rootPath)
    {
        return;
    }

    if (rootPath[0] == 0)
        rootPath = "/";

    struct ValueToParse
    {
        std::string srcPath;
        ElementData elementData;
    };

    std::vector<ValueToParse> valuesToParse;
    valuesToParse.reserve(100);

    auto enqueueChildren = [&idict, &settings, &valuesToParse](const char* parentPath, ElementData parentElementData) {
        if (!parentPath)
        {
            return;
        }

        const dictionary::Item* parentItem = settings->getSettingsDictionary(parentPath);
        size_t numChildren = idict->getItemChildCount(parentItem);
        for (size_t chIdx = 0; chIdx < numChildren; ++chIdx)
        {
            const dictionary::Item* childItem = idict->getItemChildByIndex(parentItem, numChildren - chIdx - 1);
            const char* childItemName = idict->getItemName(childItem);
            std::string childPath;
            bool isRootParent = (idict->getItemParent(parentItem) == nullptr);
            if (isRootParent)
            {
                childPath = std::string(parentPath) + childItemName;
            }
            else
            {
                childPath = std::string(parentPath) + "/" + childItemName;
            }
            valuesToParse.push_back({ childPath, parentElementData });
        }
    };

    // lock settings to ensure consistency and allow us to safely access the settings dictionary
    ScopedRead readLock;

    if (walkerMode == dictionary::WalkerMode::eSkipRoot)
    {
        const char* parentPath = rootPath;
        ElementData parentElementData = rootElementData;
        enqueueChildren(parentPath, parentElementData);
    }
    else
    {
        valuesToParse.push_back({ rootPath, rootElementData });
    }

    while (valuesToParse.size())
    {
        const ValueToParse& valueToParse = valuesToParse.back();
        std::string curItemPathStorage = std::move(valueToParse.srcPath);
        const char* curItemPath = curItemPathStorage.c_str();
        ElementData elementData = std::move(valueToParse.elementData);
        valuesToParse.pop_back();

        dictionary::ItemType curItemType = settings->getItemType(curItemPath);

        if (curItemType == dictionary::ItemType::eDictionary)
        {
            ElementData parentElementData = onItemFn(curItemPath, elementData, userData);
            enqueueChildren(curItemPath, parentElementData);
        }
        else
        {
            onItemFn(curItemPath, elementData, userData);
        }
    }
}

/**
 * A utility for caching a setting and automatically subscribing to changes of the value, as opposed to constantly
 * polling.
 *
 * @thread_safety Despite the name, this class is not thread-safe except that another thread may change the setting
 * value and `*this` will have the cached value updated in a thread-safe manner. Unless otherwise specified, assume that
 * calls to all functions must be serialized externally.
 *
 * @tparam SettingType The type of the setting. Must be a supported setting value type or compilation errors will
 *   result: `bool`, `int32_t`, `int64_t`, `float`, `double`, `const char*`.
 */
template <typename SettingType>
class ThreadSafeLocalCache
{
public:
    /**
     * Constructor.
     * @param initState The initial value to cache.
     * @note The value is not read from \ref ISettings and tracking does not start until \ref startTracking() is called.
     *   Attempting to read the value before calling \ref startTracking() will result in an assert.
     */
    ThreadSafeLocalCache(SettingType initState = SettingType{}) : m_value(initState), m_valueDirty(false)
    {
    }

    /**
     * Destructor.
     *
     * Calls \ref stopTracking().
     */
    ~ThreadSafeLocalCache()
    {
        stopTracking();
    }

    /**
     * Reads the value from the settings database and subscribes to changes for the value.
     *
     * This function reads the setting value at the given \p settingPath and caches it. Then
     * \ref ISettings::subscribeToNodeChangeEvents is called so that *this can be notified of changes to the value.
     * @note Assertions will occur if \p settingPath is `nullptr` or tracking is already started without calling
     *   \ref stopTracking() first.
     * @param settingPath The path of the setting to read. Must not be `nullptr`.
     */
    void startTracking(const char* settingPath)
    {
        CARB_ASSERT(settingPath, "Must specify a valid setting name.");
        CARB_ASSERT(m_subscription == nullptr,
                    "Already tracking this value, do not track again without calling stopTracking first.");

        Framework* f = getFramework();
        m_settings = f->tryAcquireInterface<settings::ISettings>();
        m_dictionary = f->tryAcquireInterface<dictionary::IDictionary>();
        if (!m_settings || !m_dictionary)
            return;

        m_valueSettingsPath = settingPath;
        m_value.store(m_settings->get<SettingType>(settingPath), std::memory_order_relaxed);
        m_valueDirty.store(false, std::memory_order_release);

        m_subscription = m_settings->subscribeToNodeChangeEvents(
            settingPath,
            [](const dictionary::Item* changedItem, dictionary::ChangeEventType changeEventType, void* userData) {
                if (changeEventType == dictionary::ChangeEventType::eChanged)
                {
                    ThreadSafeLocalCache* thisClassInstance = reinterpret_cast<ThreadSafeLocalCache*>(userData);
                    thisClassInstance->m_value.store(
                        thisClassInstance->getDictionaryInterface()->template get<SettingType>(changedItem),
                        std::memory_order_relaxed);
                    thisClassInstance->m_valueDirty.store(true, std::memory_order_release);
                }
            },
            this);
        if (m_subscription != nullptr)
        {
            f->addReleaseHook(m_settings, sOnRelease, this);
        }
    }

    /**
     * Halts tracking changes on the setting key provided with \ref startTracking().
     *
     * It is safe to call this function even if tracking has already been stopped, or never started. Do not call
     * \ref get() after calling this function without calling \ref startTracking() prior, otherwise an assertion will
     * occur.
     */
    void stopTracking()
    {
        if (m_subscription)
        {
            carb::getFramework()->removeReleaseHook(m_settings, sOnRelease, this);
            m_settings->unsubscribeToChangeEvents(m_subscription);
            m_subscription = nullptr;
        }
    }

    /**
     * Retrieves the cached value.
     *
     * @warning `get()` may only be called while a subscription is active. A subscription is only active once
     *   \ref startTracking() has been called (including on a newly constructed object), and only until
     *   \ref stopTracking() is called (at which point \ref startTracking() may be called to resume). Calling this
     *   function when a subscription is not active will result in an assertion and potentially reading a stale value.
     * @thread_safety This function is safe to call from multiple threads, though if the setting value is changed by
     *   other threads, multiple threads calling this function may receive different results.
     * @returns The cached value of the setting key provided in \ref startTracking().
     */
    SettingType get() const
    {
        CARB_ASSERT(m_subscription, "Call startTracking before reading this variable.");
        return m_value.load(std::memory_order_relaxed);
    }

    /**
     * Syntactic sugar for \ref get().
     */
    operator SettingType() const
    {
        return get();
    }

    /**
     * Sets the value in the setting database.
     *
     * @note Do not call this function after \ref stopTracking() has been called and/or before \ref startTracking() has
     *   been called, otherwise an assertion will occur and the setting database may be corrupted.
     * @param value The new value to set for the setting key given to \ref startTracking().
     */
    void set(SettingType value)
    {
        CARB_ASSERT(m_subscription);
        if (!m_valueSettingsPath.empty())
            m_settings->set<SettingType>(m_valueSettingsPath.c_str(), value);
    }

    /**
     * Checks to see if the cached value has been updated.
     *
     * The dirty flag must be manually reset by calling \ref clearValueDirty(). The dirty flag is set any time the
     * cached value is updated through the subscription. This also includes calls to \ref set(SettingType).
     * @returns \c true if the dirty flag is set; \c false otherwise.
     */
    bool isValueDirty() const
    {
        return m_valueDirty.load(std::memory_order_relaxed);
    }

    /**
     * Resets the dirty flag.
     *
     * After this function returns (and assuming that the subscription has not updated the cached value on a different
     * thread), \ref isValueDirty() will return `false`.
     */
    void clearValueDirty()
    {
        m_valueDirty.store(false, std::memory_order_release);
    }

    /**
     * Retrieves the setting key previously given to \ref startTracking().
     * @returns The setting key previously given to \ref startTracking().
     */
    const char* getSettingsPath() const
    {
        return m_valueSettingsPath.c_str();
    }

    /**
     * Retrieves the cached \ref dictionary::IDictionary pointer.
     * @returns The cached \ref dictionary::IDictionary pointer.
     */
    inline dictionary::IDictionary* getDictionaryInterface() const
    {
        return m_dictionary;
    }

private:
    static void sOnRelease(void* iface, void* user)
    {
        // Settings has gone away, so our subscription is defunct
        static_cast<ThreadSafeLocalCache*>(user)->m_subscription = nullptr;
        carb::getFramework()->removeReleaseHook(iface, sOnRelease, user);
    }

    // NOTE: The callback may come in on another thread so wrap it in an atomic to prevent a race.
    std::atomic<SettingType> m_value;
    std::atomic<bool> m_valueDirty;
    std::string m_valueSettingsPath;
    dictionary::SubscriptionId* m_subscription = nullptr;
    dictionary::IDictionary* m_dictionary = nullptr;
    settings::ISettings* m_settings = nullptr;
};

#ifndef DOXYGEN_SHOULD_SKIP_THIS
template <>
class ThreadSafeLocalCache<const char*>
{
public:
    ThreadSafeLocalCache(const char* initState = "") : m_valueDirty(false)
    {
        std::lock_guard<std::mutex> guard(m_valueMutex);
        m_value = initState;
    }
    ~ThreadSafeLocalCache()
    {
        stopTracking();
    }

    void startTracking(const char* settingPath)
    {
        CARB_ASSERT(settingPath, "Must specify a valid setting name.");
        CARB_ASSERT(m_subscription == nullptr,
                    "Already tracking this value, do not track again without calling stopTracking first.");

        Framework* f = getFramework();
        m_settings = f->tryAcquireInterface<settings::ISettings>();
        m_dictionary = f->tryAcquireInterface<dictionary::IDictionary>();

        m_valueSettingsPath = settingPath;
        const char* valueRaw = m_settings->get<const char*>(settingPath);
        m_value = valueRaw ? valueRaw : "";
        m_valueDirty.store(false, std::memory_order_release);

        m_subscription = m_settings->subscribeToNodeChangeEvents(
            settingPath,
            [](const dictionary::Item* changedItem, dictionary::ChangeEventType changeEventType, void* userData) {
                if (changeEventType == dictionary::ChangeEventType::eChanged)
                {
                    ThreadSafeLocalCache* thisClassInstance = reinterpret_cast<ThreadSafeLocalCache*>(userData);
                    {
                        const char* valueStringBuffer =
                            thisClassInstance->getDictionaryInterface()->template get<const char*>(changedItem);
                        std::lock_guard<std::mutex> guard(thisClassInstance->m_valueMutex);
                        thisClassInstance->m_value = valueStringBuffer ? valueStringBuffer : "";
                    }
                    thisClassInstance->m_valueDirty.store(true, std::memory_order_release);
                }
            },
            this);
        if (m_subscription)
        {
            f->addReleaseHook(m_settings, sOnRelease, this);
        }
    }
    void stopTracking()
    {
        if (m_subscription)
        {
            m_settings->unsubscribeToChangeEvents(m_subscription);
            m_subscription = nullptr;
            carb::getFramework()->removeReleaseHook(m_settings, sOnRelease, this);
        }
    }

    const char* get() const
    {
        // Not a safe operation
        CARB_ASSERT(false);
        CARB_LOG_ERROR("Shouldn't use unsafe get on a ThreadSafeLocalCache<const char*>");
        return "";
    }

    operator const char*() const
    {
        // Not a safe operation
        return get();
    }

    std::string getStringSafe() const
    {
        // Not a safe operation
        CARB_ASSERT(m_subscription, "Call startTracking before reading this variable.");
        std::lock_guard<std::mutex> guard(m_valueMutex);
        return m_value;
    }

    void set(const char* value)
    {
        m_settings->set<const char*>(m_valueSettingsPath.c_str(), value);
    }

    bool isValueDirty() const
    {
        return m_valueDirty.load(std::memory_order_relaxed);
    }
    void clearValueDirty()
    {
        m_valueDirty.store(false, std::memory_order_release);
    }

    const char* getSettingsPath() const
    {
        return m_valueSettingsPath.c_str();
    }

    inline dictionary::IDictionary* getDictionaryInterface() const
    {
        return m_dictionary;
    }

private:
    static void sOnRelease(void* iface, void* user)
    {
        // Settings has gone away, so our subscription is defunct
        static_cast<ThreadSafeLocalCache*>(user)->m_subscription = nullptr;
        carb::getFramework()->removeReleaseHook(iface, sOnRelease, user);
    }

    // NOTE: The callback may come in on another thread so wrap it in a mutex to prevent a race.
    std::string m_value;
    mutable std::mutex m_valueMutex;
    std::atomic<bool> m_valueDirty;
    std::string m_valueSettingsPath;
    dictionary::SubscriptionId* m_subscription = nullptr;
    dictionary::IDictionary* m_dictionary = nullptr;
    settings::ISettings* m_settings = nullptr;
};
#endif

/** Helper class to add a setting node or tree change subscription that will be automatically
 *  unregistered when the object goes out of scope.
 */
class ScopedSubscription
{
public:
    /** Constructor: creates a new scoped subscription for a settings node change.
     *
     *  @param[in] path     The path to the setting node or branch to watch.  This may not be
     *                      `nullptr`.
     *  @param[in] fn       The callback handler function to call when the watched setting
     *                      @p path is created, modified, or destroyed.  This may not be
     *                      `nullptr`.
     *  @param[in] userData Caller provided data that will be passed unmodified to the callback
     *                      function.
     */
    ScopedSubscription(const char* path, carb::dictionary::OnNodeChangeEventFn fn, void* userData)
    {
        _getSettingsInterface();

        if (m_settings != nullptr)
        {
            m_sub = m_settings->subscribeToNodeChangeEvents(path, fn, userData);
        }
    }

    /** Constructor: creates a new scoped subscription for a settings tree change.
     *
     *  @param[in] path     The path to the setting tree to watch.  This may not be `nullptr`.
     *  @param[in] fn       The callback handler function to call when the watched setting
     *                      @p path is created, modified, or destroyed.  This may not be
     *                      `nullptr`.
     *  @param[in] userData Caller provided data that will be passed unmodified to the callback
     *                      function.
     */
    ScopedSubscription(const char* path, carb::dictionary::OnTreeChangeEventFn fn, void* userData)
    {
        _getSettingsInterface();

        if (m_settings != nullptr)
        {
            m_sub = m_settings->subscribeToTreeChangeEvents(path, fn, userData);
        }
    }

    /** Move Constructor: moves another object into this one.
     *
     *  @param[inout] other     Another object to move its values from into this one.
     */
    ScopedSubscription(ScopedSubscription&& other)
    {
        *this = std::move(other);
    }

    /** Destructor: unsubscribes from this change watch. */
    ~ScopedSubscription()
    {
        // remove the release hook since we no longer need it.  Note that if the release hook
        // had fired, it will already have been removed and this will be a no-op.
        carb::getFramework()->removeReleaseHook(m_settings, sOnReleaseSettings, this);

        if (m_sub == nullptr)
            return;

        if (m_settings != nullptr)
        {
            m_settings->unsubscribeToChangeEvents(std::exchange(m_sub, nullptr));
        }
    }

    CARB_PREVENT_COPY(ScopedSubscription);

    /** Move-assigns another object into this one.
     *
     *  @param[inout] other     Another object to move its values from into this one.
     *
     *  @returns A reference to this object.
     */
    ScopedSubscription& operator=(ScopedSubscription&& other)
    {
        if (&other == this)
            return *this;

        m_sub = std::exchange(other.m_sub, nullptr);
        return *this;
    }

    /** Operator to test whether the contained change subscription is valid.
     *
     *  @returns `true` if the contained subscription object is valid.  Returns `false` otherwise.
     */
    explicit operator bool() const noexcept
    {
        return m_sub != nullptr;
    }

private:
    /** ISettings interface release hook callback function.
     *
     *  @param[in] iface    The interface that will be released.  This interface pointer will
     *                      still be valid, but will be released very shortly after this call
     *                      returns.
     *  @param[in] userData Caller provided data value for the callback.
     *
     *  @remarks This callback will clear out the change subscription pointer when called.  If
     *           the `ISettings` interface that the subscription was created with is released,
     *           trying to unsubscribe later would lead to undefined behavior.
     */
    static void sOnReleaseSettings(void* iface, void* userData)
    {
        ScopedSubscription* self = reinterpret_cast<ScopedSubscription*>(userData);
        CARB_UNUSED(iface);

        if (self == nullptr)
            return;

        carb::getFramework()->removeReleaseHook(self->m_settings, sOnReleaseSettings, self);
        self->m_settings = nullptr;
        self->m_sub = nullptr;
    }

    /** Retrieves the `ISettings` interface and registers a release hook for it.
     *
     *  @remarks This retrieves a cached `ISettings` interface and adds a callback for when it
     *           is released.  This is done to ensure that the subscription will be leaked to
     *           avoid undefined behavior if the host app releases the `ISettings` interface
     *           object before this object goes out of scope.
     *
     *  @note This is only intended to be called once during a constructor of this object.
     */
    void _getSettingsInterface()
    {
        m_settings = carb::getCachedInterface<carb::settings::ISettings>();
        carb::getFramework()->addReleaseHook(m_settings, sOnReleaseSettings, this);
    }

    /** The `ISettings` interface being used for this operation. */
    carb::settings::ISettings* m_settings = nullptr;

    /** The contained subscription object.  This will be `nullptr` if the subscription is invalid. */
    carb::dictionary::SubscriptionId* m_sub = nullptr;
};

} // namespace settings
} // namespace carb
