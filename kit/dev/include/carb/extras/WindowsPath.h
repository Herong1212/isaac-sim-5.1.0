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
//! @brief Carbonite Windows path utilities
#pragma once

#include "../Defines.h"

#if CARB_PLATFORM_WINDOWS || defined(DOXYGEN_BUILD)

#    include "../CarbWindows.h"
#    include "../Error.h"
#    include "Unicode.h"

#    include <algorithm>
#    include <string>

namespace carb
{
namespace extras
{

/**
 * (Windows only) Converts a UTF-8 file path to Windows system file path.
 *
 * Slashes are replaced with backslashes, and @ref fixWindowsPathPrefix() is called.
 *
 * @note Use of this function is discouraged. Use @ref carb::filesystem::IFileSystem for filesystem needs.
 *
 * @par Errors
 * Accessible via @ref carb::ErrorApi
 * * Note: Error state is not cleared on success
 * * @ref omni::core::kResultFail - UTF-8 to wide conversion failed
 *
 * @param path Input string to convert, in UTF-8 encoding.
 * @return Wide string containing Windows system file path or empty string if conversion cannot be performed.
 */
std::wstring convertCarboniteToWindowsPath(const std::string& path);

/**
 * (Windows only) Converts Windows system file path to a UTF-8 file path.
 *
 * Backslashes are replaced with slashes and the long path prefix is removed if present.
 *
 * @note Use of this function is discouraged. Use @ref carb::filesystem::IFileSystem for filesystem needs.
 *
 * @par Errors
 * Accessible via @ref carb::ErrorApi
 * * Note: Error state is not cleared on success
 * * @ref omni::core::kResultFail - UTF-8 to wide conversion failed
 *
 * @param pathW Input string to convert, in Unicode (Windows native) encoding.
 * @return UTF-8 encoded file path or empty string if conversion cannot be performed.
 */
std::string convertWindowsToCarbonitePath(const std::wstring& pathW);

/**
 * (Windows only) Performs fixup on a Windows file path by adding or removing the long path prefix as necessary.
 *
 * If the file path is too long and doesn't have long path prefix, the prefix is added.
 * If the file path is short and has long path prefix, the prefix is removed.
 * Otherwise, the path is not modified.
 *
 * @par Errors
 * Accessible via @ref carb::ErrorApi
 * * None
 *
 * @param pathW Input string to convert, in Unicode (Windows native) encoding.
 * @return Valid Windows system file path.
 */
std::wstring fixWindowsPathPrefix(const std::wstring& pathW);

/**
 * (Windows only) Converts Windows path string into a canonical form.
 *
 * @note This uses Windows platform functions to canonicalize the path and is fairly costly.
 *
 * @par Errors
 * Accessible via @ref carb::ErrorApi
 * * Note: Error state is not cleared on success
 * * @ref omni::core::kResultFail - An error occurred
 *
 * @param pathW Windows system file path, in Unicode (Windows native) encoding.
 * @return The canonical form of the input path. If an error occurs, @p pathW is returned without modifications. In
 *         order to determine if an error occurred, use @ref carb::ErrorApi. Since error state is not cleared on
 *         success, clear the error state before calling this function if you wish to make sure that it succeeds.
 */
std::wstring getWindowsCanonicalPath(const std::wstring& pathW);

/**
 * (Windows only) Retrieves the full path and file name of the specified file.
 *
 * If it's not possible, original path is returned.
 *
 * @par Errors
 * Accessible via @ref carb::ErrorApi
 * * Note: Error state is not cleared on success
 * * @ref omni::core::kResultFail - An error occurred
 * * Other errors may be reported based on the underlying platform calls
 *
 * @param pathW Windows system file path, in Unicode (Windows native) encoding.
 * @return The full path and file name of the input file. If an error occurs, @p pathW is returned without modification.
 *         In order to determine if an error occurred, use @ref carb::ErrorApi. Since the error state is not cleared on
 *         success, clear the error state before calling this function if you wish to make sure that it succeeds.
 */
std::wstring getWindowsFullPath(const std::wstring& pathW);

/**
 * (Windows only) Sets the default DLL search directories for the application.
 *
 * This calls `SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS)`. From the
 * <a
 * href="https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-setdefaultdlldirectories">documentation</a>
 * this value is the combination of three separate values which comprise the recommended maximum number of directories
 * an application should include in its DLL search path:
 * * The application directory
 * * `%windows%\system32`
 * * User directories: any path explicitly added by `AddDllDirectory()` or `SetDllDirectory()`.
 *
 * See also: <a href="https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order">DLL Search
 * Order</a>
 *
 * @ref ErrorApi state is not changed by this function.
 */
void adjustWindowsDllSearchPaths();

//
// Implementations
//

inline std::wstring convertCarboniteToWindowsPath(const std::string& path)
{
    std::wstring pathW = convertUtf8ToWide(path);
    if (pathW == kUnicodeToWideFailure)
    {
        ErrorApi::instance().setError(kResultFail);
        return L"";
    }
    std::replace(pathW.begin(), pathW.end(), L'/', L'\\');
    return fixWindowsPathPrefix(pathW);
}

inline std::string convertWindowsToCarbonitePath(const std::wstring& pathW)
{
    bool hasPrefix = (pathW.compare(0, 4, L"\\\\?\\") == 0);
    std::string path = convertWideToUtf8(pathW.c_str() + (hasPrefix ? 4 : 0));
    if (path == kUnicodeToUtf8Failure)
    {
        ErrorApi::instance().setError(kResultFail);
        return "";
    }
    std::replace(path.begin(), path.end(), '\\', '/');
    return path;
}

inline std::wstring fixWindowsPathPrefix(const std::wstring& pathW)
{
    bool hasPrefix = (pathW.compare(0, 4, L"\\\\?\\") == 0);

    if (pathW.size() >= CARBWIN_MAX_PATH && !hasPrefix)
    {
        return L"\\\\?\\" + pathW;
    }
    if (pathW.size() < CARBWIN_MAX_PATH && hasPrefix)
    {
        return pathW.substr(4, pathW.size() - 4);
    }

    return pathW;
}

inline std::wstring getWindowsCanonicalPath(const std::wstring& pathW)
{
    wchar_t* canonical = nullptr;
    auto hr = PathAllocCanonicalize(pathW.c_str(), CARBWIN_PATHCCH_ALLOW_LONG_PATHS, &canonical);
    if (CARBWIN_SUCCEEDED(hr))
    {
        std::wstring result = canonical;
        LocalFree(canonical);
        return result;
    }

    ErrorApi::instance().setError(
        omni::core::kResultFail, omni::string{ omni::formatted, "PathAllocCanonicalize failed with HRESULT 0x%08x", hr });
    return pathW;
}

inline std::wstring getWindowsFullPath(const std::wstring& pathW)
{
    // Retrieve the size
    DWORD size = GetFullPathNameW(pathW.c_str(), 0, nullptr, nullptr);
    if (size != 0)
    {
        std::wstring fullPathName(size - 1, '\0');
        size = GetFullPathNameW(pathW.c_str(), size, &fullPathName[0], nullptr);
        if (size)
        {
            // Assert if the Win32 API lied to us. Note that sometimes it does use less than asked for.
            CARB_ASSERT(size <= fullPathName.size());
            fullPathName.resize(size);
            return fullPathName;
        }
    }

    ErrorApi::setFromWinApiErrorCode();
    return pathW;
}

inline void adjustWindowsDllSearchPaths()
{
    // MSDN:
    // https://docs.microsoft.com/en-us/windows/desktop/api/libloaderapi/nf-libloaderapi-setdefaultdlldirectories
    // LOAD_LIBRARY_SEARCH_DEFAULT_DIRS
    // This value is a combination of LOAD_LIBRARY_SEARCH_APPLICATION_DIR, LOAD_LIBRARY_SEARCH_SYSTEM32, and
    // LOAD_LIBRARY_SEARCH_USER_DIRS.
    SetDefaultDllDirectories(CARBWIN_LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
}

} // namespace extras
} // namespace carb

#endif
