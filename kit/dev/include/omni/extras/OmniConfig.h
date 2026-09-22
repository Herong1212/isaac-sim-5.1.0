// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "../../carb/Defines.h"
#include "../../carb/filesystem/IFileSystem.h"
#include "../../carb/dictionary/IDictionary.h"
#include "../../carb/dictionary/ISerializer.h"
#include "../../carb/extras/Utf8Parser.h"
#include "../../carb/extras/Path.h"
#include "../../carb/extras/EnvironmentVariable.h"
#include "ScratchBuffer.h"

#if CARB_POSIX
#    include <unistd.h>
#    include <pwd.h>
#elif CARB_PLATFORM_WINDOWS
#    include "../../carb/CarbWindows.h"
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

namespace omni
{
namespace extras
{

/** Retrieve the path to the home directory.
 *  @retval The path to the home directory.
 *  @retval Empty path on failure.
 *  @remarks This retrieves the path to `$HOME` on POSIX platforms and `%USEPROFILE%` on Windows.
 *           If those are unset, this uses system calls as a fallback.
 */
inline carb::extras::Path getHomePath()
{
#if CARB_POSIX
    constexpr char homeVar[] = "HOME";
#elif CARB_PLATFORM_WINDOWS
    constexpr char homeVar[] = "USERPROFILE";
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif

    // POSIX and Windows both have an envvar for this
    std::string home;
    if (carb::extras::EnvironmentVariable::getValue(homeVar, home) && !home.empty())
    {
        return home;
    }

#if CARB_POSIX
    // omni-config-cpp had code to handle cases where $HOME was unset, so that remains here.
    struct passwd info;
    struct passwd* out = nullptr;
    omni::extras::ScratchBuffer<char, 4096> buffer;

    const long len = sysconf(_SC_GETPW_R_SIZE_MAX);
    if (len == -1)
    {
        return {}; // sysconf() failed
    }

    if (!buffer.resize((size_t)len))
    {
        return {};
    }

    const int result = CARB_RETRY_EINTR(getpwuid_r(getuid(), &info, buffer.data(), (size_t)len, &out));
    if (result != 0 || out != &info)
    {
        return {};
    }

    return info.pw_dir;
#elif CARB_PLATFORM_WINDOWS
    omni::extras::ScratchBuffer<wchar_t, 2048> buffer;
    void* token = nullptr;
    unsigned long len = 0;

    if (!OpenProcessToken(GetCurrentProcess(), CARBWIN_TOKEN_QUERY, &token))
    {
        return {};
    }

    CARB_SCOPE_EXIT
    {
        CloseHandle(token);
    };

    GetUserProfileDirectoryW(token, nullptr, &len);
    if (len == 0)
    {
        return {};
    }

    if (!buffer.resize(len))
    {
        return {};
    }

    if (!GetUserProfileDirectoryW(token, buffer.data(), &len))
    {
        return {};
    }

    const size_t offset = (wcsncmp(buffer.data(), L"\\\\?\\", 4) == 0) ? 4 : 0;
    return carb::extras::convertWideStringToUtf8(buffer.data() + offset);
#else
    CARB_UNSUPPORTED_PLATFORM();
#endif
}


/** This collects information about standard paths for Omniverse applications, such as the config
 *  directory, the logs directory, etc.
 *  This is designed to be a replacement of the omniverse::GlobalConfig class from omni-config-cpp.
 *  This class is designed for serialized access.
 *  This does not require the carb framework to be initialized, but omniverse.toml will not be
 *  loaded without the carb framework.
 */
class OmniConfig
{
public:
    OmniConfig(const char* configFileName = "omniverse.toml")
    {
        carb::extras::Path base;

        m_configFileName = configFileName;
        m_homePath = omni::extras::getHomePath();
        if (!m_homePath.empty())
        {
            base = m_homePath.join(".nvidia-omniverse");
        }

        // config directory
        std::string omniConfigPath;
        if (carb::extras::EnvironmentVariable::getValue("OMNI_CONFIG_PATH", omniConfigPath) && !omniConfigPath.empty())
        {
            m_baseConfigPath = omniConfigPath;
        }
        else if (!base.empty())
        {
            m_baseConfigPath = base.join("config");
        }

        // log directory
        if (!base.empty())
        {
            m_baseLogsPath = base.join("logs");
        }

        // data, library and cache directories
        // OVCC-1272: This is not a POSIX operation but omni-config-cpp just assumed all non-windows
        //            was Linux, leading to this split.
#if CARB_PLATFORM_LINUX
        const carb::extras::Path xdgData = _getXdgDataDir(m_homePath);
        if (!xdgData.empty())
        {
            m_baseDataPath = xdgData.join("ov").join("data");
            m_baseLibraryPath = xdgData.join("ov").join("pkg");
        }

        const carb::extras::Path xdgCache = _getXdgCacheDir(m_homePath);
        if (!xdgCache.empty())
        {
            m_baseCachePath = xdgCache.join("ov");
        }
#elif CARB_PLATFORM_WINDOWS
        // OVCC-1271: More robust to use SHGetKnownFolder here (FOLDERID_LocalAppData)
        std::string localAppDataStr;
        if (carb::extras::EnvironmentVariable::getValue("LOCALAPPDATA", localAppDataStr) && !localAppDataStr.empty())
        {
            const auto localAppDataOv = carb::extras::Path(localAppDataStr).join("ov");
            m_baseDataPath = localAppDataOv.join("data");
            m_baseLibraryPath = localAppDataOv.join("pkg");
            m_baseCachePath = localAppDataOv.join("cache");
        }
#else
        CARB_UNSUPPORTED_PLATFORM();
#endif

        // Load setting overrides from the config file specified.
        // This function uses Carbonite to load these.
        _loadSettingOverrides();
    }

    ~OmniConfig()
    {
        if (m_omniverseToml != nullptr)
        {
            m_dictionary->destroyItem(m_omniverseToml);
        }
    }

    /** Retrieves the directory to the path to the $HOME directory (%USERPROFILE% on Windows).
     *  @retval The $HOME directory.
     *  @retval Empty path on failure.
     */
    inline const carb::extras::Path& getHomePath() const
    {
        return m_homePath;
    }

    /** Retrieves the directory to the path where Omniverse config files are stored.
     *  @retval The config directory.
     *  @retval Empty path on failure.
     *  @note This can be overridden with the `$OMNI_CONFIG_PATH` environment variable.
     */
    inline const carb::extras::Path& getBaseConfigPath() const
    {
        return m_baseConfigPath;
    }

    /** Retrieves the directory to the path where Omniverse log files are stored.
     *  @retval The logs directory.
     *  @retval Empty path on failure.
     */
    inline const carb::extras::Path& getBaseLogsPath() const
    {
        return m_baseLogsPath;
    }

    /** Retrieves the directory to the path where Omniverse data files are stored.
     *  @retval The data directory.
     *  @retval Empty path on failure.
     *  @note This returns a non-standard path on Mac OS.
     *        This is a bug that was inherited from omni-config-cpp.
     *        This will be fixed in a later version, so this should be considered unstable on Mac OS.
     */
    inline const carb::extras::Path& getBaseDataPath() const
    {
        return m_baseDataPath;
    }

    /** Retrieves the directory to the path where Omniverse library files are stored.
     *  @retval The library directory.
     *  @retval Empty path on failure.
     *  @note This returns a non-standard path on Mac OS.
     *        This is a bug that was inherited from omni-config-cpp.
     *        This will be fixed in a later version, so this should be considered unstable on Mac OS.
     */
    inline const carb::extras::Path& getBaseLibraryPath() const
    {
        return m_baseLibraryPath;
    }

    /** Retrieves the directory to the path where Omniverse cache files are stored.
     *  @retval The data directory.
     *  @retval Empty path on failure.
     *  @note This returns a non-standard path on Mac OS.
     *        This is a bug that was inherited from omni-config-cpp.
     *        This will be fixed in a later version, so this should be considered unstable on Mac OS.
     */
    inline const carb::extras::Path& getBaseCachePath() const
    {
        return m_baseCachePath;
    }

    /** Retrieves the omniverse.toml dictionary.
     *  @retval The omniverse.toml dictionary contents.
     *          This is valid until the class instance is destroyed.
     *  @retval nullptr if omniverse.toml couldn't be loaded (e.g. the file doesn't exist, the carb
     *                  framework isn't loaded).
     *  @remarks This is the dictionary that provides overrides for default paths.
     *           You may want to retrieve this for additional information from omniverse.toml (e.g.
     *           kit-kernel retrieves paths.documents_root).
     *  @note omniverse.toml is loaded when the class is constructed.
     */
    inline carb::dictionary::Item* getOmniverseToml()
    {
        return m_omniverseToml;
    }

    /** Helper to retrieve config strings from omniverse.toml.
     *  @param path The path to the element in the config.
     *              Path separators are `/`, so if you wanted `{ paths: { documents_root: "..." } }`,
     *              you would pass `"paths/documents_root"`.
     *  @retval The string from @p path in omniverse.toml, if it exists and was a string.
     *  @retval Empty string if the requested item was not as string, the requested path did not
     *          exist, omniverse.toml did not exist or the carb framework was not loaded.
     */
    std::string getConfigEntry(const char* path)
    {
        if (m_omniverseToml == nullptr)
        {
            return {};
        }

        const carb::dictionary::Item* item = m_dictionary->getItem(m_omniverseToml, path);
        if (item == nullptr)
        {
            return {};
        }

        return m_dictionary->getStringBuffer(item);
    }


private:
#if CARB_PLATFORM_LINUX
    /** Retrieve the XDG standard data directory.
     *  @param[in] home The user's home directory.
     *  @retval The XDG standard data directory.
     *  @retval Empty string if nothing could be retrieved.
     */
    inline carb::extras::Path _getXdgDataDir(const carb::extras::Path& home)
    {
        const char* xdg = getenv("XDG_DATA_HOME");
        if (xdg != nullptr && xdg[0] != '\0')
        {
            return xdg;
        }

        if (home.empty())
        {
            return {};
        }

        return home.join(".local").join("share");
    }

    /** Retrieve the XDG standard cache directory.
     *  @param[in] home The user's home directory.
     *  @retval The XDG standard cache directory.
     *  @retval Empty string if nothing could be retrieved.
     */
    inline carb::extras::Path _getXdgCacheDir(const carb::extras::Path& home)
    {
        const char* xdg = getenv("XDG_CACHE_HOME");
        if (xdg != nullptr && xdg[0] != '\0')
        {
            return xdg;
        }

        if (home.empty())
        {
            return {};
        }

        return home.join(".cache");
    }
#endif

    /** Load omniverse.toml into m_omniverseToml.
     */
    inline void _loadOmniverseToml()
    {
        carb::Framework* framework = carb::getFramework();
        if (framework == nullptr)
        {
            return;
        }

        m_dictionary = framework->tryAcquireInterface<carb::dictionary::IDictionary>();
        carb::filesystem::IFileSystem* fs = framework->tryAcquireInterface<carb::filesystem::IFileSystem>();
        carb::dictionary::ISerializer* serializer =
            framework->tryAcquireInterface<carb::dictionary::ISerializer>("carb.dictionary.serializer-toml.plugin");
        if (fs == nullptr || m_dictionary == nullptr || serializer == nullptr)
        {
            return;
        }

        // Load the file contents
        carb::filesystem::File* f = fs->openFileToRead(m_baseConfigPath.join(m_configFileName).getStringBuffer());
        if (f == nullptr)
        {
            return;
        }

        CARB_SCOPE_EXIT
        {
            fs->closeFile(f);
        };

        omni::extras::ScratchBuffer<char, 4096> buffer;
        size_t size = fs->getFileSize(f);
        if (!buffer.resize(size + 1))
        {
            return;
        }

        size_t read = fs->readFileChunk(f, buffer.data(), size);
        if (read != size)
        {
            return;
        }

        buffer.data()[size] = '\0';

        // Parse the toml
        m_omniverseToml = serializer->createDictionaryFromStringBuffer(buffer.data());
    }


    /** Load the setting overrides from the base config path using the Carbonite framework.
     */
    void _loadSettingOverrides()
    {
        _loadOmniverseToml(); // this loads m_omniverseToml
        if (m_omniverseToml == nullptr)
        {
            return;
        }

        // Load the individual settings
        const carb::dictionary::Item* libraryRoot = m_dictionary->getItem(m_omniverseToml, "paths/library_root");
        if (libraryRoot != nullptr)
        {
            m_baseLibraryPath = m_dictionary->getStringBuffer(libraryRoot);
        }

        const carb::dictionary::Item* dataRoot = m_dictionary->getItem(m_omniverseToml, "paths/data_root");
        if (dataRoot != nullptr)
        {
            m_baseDataPath = m_dictionary->getStringBuffer(dataRoot);
        }

        const carb::dictionary::Item* cacheRoot = m_dictionary->getItem(m_omniverseToml, "paths/cache_root");
        if (cacheRoot != nullptr)
        {
            m_baseCachePath = m_dictionary->getStringBuffer(cacheRoot);
        }

        const carb::dictionary::Item* logsRoot = m_dictionary->getItem(m_omniverseToml, "paths/logs_root");
        if (logsRoot != nullptr)
        {
            m_baseLogsPath = m_dictionary->getStringBuffer(logsRoot);
        }
    }

    std::string m_configFileName;
    carb::extras::Path m_homePath;
    carb::extras::Path m_baseConfigPath;
    carb::extras::Path m_baseLogsPath;
    carb::extras::Path m_baseDataPath;
    carb::extras::Path m_baseLibraryPath;
    carb::extras::Path m_baseCachePath;

    /** The contents of omniverse.toml.
     *  This gets set if _loadOmniverseToml() succeeds.
     */
    carb::dictionary::Item* m_omniverseToml = nullptr;

    /** A cached dictionary interface.
     *  This gets set if _loadOmniverseToml() succeeds.
     */
    carb::dictionary::IDictionary* m_dictionary = nullptr;
};

} // namespace extras
} // namespace omni
