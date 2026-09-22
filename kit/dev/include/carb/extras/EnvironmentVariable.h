// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "../Defines.h"
#include "../cpp/Optional.h"
#include "../cpp/StringView.h"

#include <string>
#include <utility>

#if CARB_PLATFORM_LINUX
#    include <cstdlib>
#endif

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#    include "../../omni/extras/ScratchBuffer.h"
#    include "Unicode.h"
#endif

namespace carb
{
namespace extras
{

/**
 * Defines an environment variable class that allows one to get, set, and restore value on destruction.
 */
class EnvironmentVariable final
{
    CARB_PREVENT_COPY(EnvironmentVariable);

    template <typename T>
    using optional = ::carb::cpp::optional<T>;

public:
    EnvironmentVariable() = delete;

    /**
     * Create instance from environment variable called @p name.
     *
     * @param name name of the environment variable
     */
    EnvironmentVariable(carb::cpp::string_view name)
        : m_name(name), m_restore(false), m_restoreValue(carb::cpp::nullopt)
    {
        CARB_ASSERT(!m_name.empty());
    }

    /**
     * Create instance from environment variable called @p name, setting it's value to @p value, to be restored to
     * it's original value on destruction.
     *
     * @param name name of the environment variable
     * @param value optional value to set variable, if not set (nullopt) then unset the variable
     */
    EnvironmentVariable(carb::cpp::string_view name, const optional<const std::string>& value)
        : m_name(name), m_restore(false), m_restoreValue(carb::cpp::nullopt)
    {
        CARB_ASSERT(!m_name.empty());

        // attempt to get and store current value
        std::string currentValue;
        if (getValue(m_name.c_str(), currentValue))
        {
            m_restoreValue = currentValue;
        }

        // attempt to set to new value
        if (setValue(m_name.c_str(), value ? value->c_str() : nullptr))
        {
            m_restore = true;
        }
    }

    ~EnvironmentVariable()
    {
        if (m_restore)
        {
            bool ret = setValue(m_name.c_str(), m_restoreValue ? m_restoreValue->c_str() : nullptr);
            CARB_ASSERT(ret);
            CARB_UNUSED(ret);
        }
    }

    /** move constructor */
    EnvironmentVariable(EnvironmentVariable&& other)
        : m_name(std::move(other.m_name)),
          m_restore(std::exchange(other.m_restore, false)),
          m_restoreValue(std::move(other.m_restoreValue))
    {
    }

    /** move operator */
    EnvironmentVariable& operator=(EnvironmentVariable&& other)
    {
        m_name = std::move(other.m_name);
        m_restore = std::exchange(other.m_restore, false);
        m_restoreValue = std::move(other.m_restoreValue);
        return *this;
    }

    /**
     * Get the environment variable name
     *
     * @return environment variable name
     */
    const std::string& getName() const noexcept
    {
        return m_name;
    }

    /**
     * Get the environment variable current value
     *
     * @return environment variable current value
     */
    optional<const std::string> getValue() const noexcept
    {
        optional<const std::string> result;
        std::string value;
        if (getValue(m_name.c_str(), value))
        {
            result = value;
        }
        return result;
    }

    /**
     * Sets new environment value for a variable.
     *
     * @param name  Environment variable string that we want to get the value for.
     * @param value The value of environment variable to get (MAX 256 characters).
     *              Can be nullptr - which means the variable should be unset.
     *
     * @warning (Linux) While calls like `setenv()` and `unsetenv()` are thread-safe with respect to all calls that
     *   modify the environment, there is **no thread-safe way** to read the environment with `getenv()` if any thread
     *   is modifying the environment. Unfortunately many GLIBC functions read the environment through `getenv()`.
     *   Therefore **avoid modifying the enviornment!**.
     *
     * @return true if the operation was successful.
     */
    static bool setValue(const char* name, const char* value)
    {
        bool result;

        // Set the new value
#if CARB_PLATFORM_WINDOWS
        std::wstring nameWide = convertUtf8ToWide(name);
        if (value)
        {
            std::wstring valueWide = convertUtf8ToWide(value);
            result = (SetEnvironmentVariableW(nameWide.c_str(), valueWide.c_str()) != 0);
        }
        else
        {
            result = (SetEnvironmentVariableW(nameWide.c_str(), nullptr) != 0);
        }
#else
        // ‘*((void*)(& scoped)+16).std::basic_string<char>::_M_dataplus.std::basic_string<char>::_Alloc_hider::_M_p’
        // may be used uninitialized in this function, reported by GCC, possibly based on our optional<> impl?
        CARB_GNUC_ONLY(CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wmaybe-uninitialized")) // exclude Clang
        if (value)
        {
            result = (setenv(name, value, /*overwrite=*/1) == 0);
        }
        else
        {
            result = (unsetenv(name) == 0);
        }
        CARB_GNUC_ONLY(CARB_IGNOREWARNING_GNUC_POP)
#endif
        return result;
    }

    /**
     * Static helper to get the value of the current environment variable.
     *
     * @param name  Environment variable string that we want to get the value for.
     * @param value The value of environment variable to get.
     *
     * @return true if the variable exists
     */
    static bool getValue(const char* name, std::string& value)
    {
#if CARB_PLATFORM_WINDOWS
        std::wstring nameWide = convertUtf8ToWide(name);

        omni::extras::ScratchBuffer<wchar_t> buffer;
        while (true)
        {
            DWORD count = GetEnvironmentVariableW(nameWide.c_str(), buffer.data(), static_cast<DWORD>(buffer.size()));
            if (count == 0)
            {
                if (GetLastError() == 0)
                {
                    // no error but no count means we got an empty env var
                    value = "";
                    return true;
                }
                else
                {
                    // the error case here means the env var does not exist
                    return false;
                }
            }
            else if (count < buffer.size())
            {
                // success case
                value = convertWideToUtf8(buffer.data());
                return true;
            }
            else
            {
                // env var is too large for the current buffer -- grow it and try again
                buffer.resize(count + 1U); // include null termination
                continue;
            }
        }
#else
        const char* buffer = getenv(name);
        if (buffer == nullptr)
        {
            return false;
        }
        value = buffer; // Copy string
#endif
        return true;
    }

private:
    std::string m_name;
    bool m_restore;
    optional<const std::string> m_restoreValue;
};

} // namespace extras
} // namespace carb
