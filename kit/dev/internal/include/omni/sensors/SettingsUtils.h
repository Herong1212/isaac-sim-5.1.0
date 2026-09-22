// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "Settings.h"

#include <carb/InterfaceUtils.h>
#include <carb/settings/ISettings.h>

#include <omni/String.h>

#include <GenericModelOutputTypes.h>
#include <algorithm>
#include <cctype>
namespace omni
{
namespace sensors
{
namespace nv
{


inline omni::string getStringFromSetting(const char* key)
{
    omni::string result;
    // Make sure omni::string is empty by default!
    result.clear();
    if (auto* iSettings = carb::getCachedInterface<carb::settings::ISettings>())
    {
        if (iSettings->isAccessibleAs(carb::dictionary::ItemType::eString, key))
        {
            auto value = iSettings->getStringBuffer(key);
            if (value)
            {
                result = omni::string(value);
            }
        }
    }
    return result;
}


inline bool getFloatArrayFromSetting(const char* key, float* array, size_t arraySize)
{
    bool found = false;
    if (auto* iSettings = carb::getCachedInterface<carb::settings::ISettings>())
    {
        if (iSettings->getArrayLength(key) == arraySize)
        {
            iSettings->getAsFloatArray(key, array, arraySize);
            found = true;
        }
    }
    return found;
}


inline AuxType getAuxOutputType(const char* key, bool& settingAvailable)
{
    AuxType result{ AuxType::NONE };
    omni::string value = getStringFromSetting(key);
    settingAvailable = false;
    if (!value.empty())
    {
        settingAvailable = true;
        std::transform(value.begin(), value.end(), value.begin(), ::toupper);
        if (value == "BASIC")
        {
            result = AuxType::BASIC;
        }
        else if (value == "EXTRA")
        {
            result = AuxType::EXTRA;
        }
        else if (value == "FULL")
        {
            result = AuxType::FULL;
        }
    }
    return result;
}


//-----------------------------------------------------------------------------
struct StringToAuxOutputType
{
    using InType = const char*;
    using OutType = omni::sensors::AuxType;

    OutType operator()(InType v) const
    {
        std::string value(v);
        std::transform(value.begin(), value.end(), value.begin(), ::tolower);
        const uint64_t hash = carb::hashString(value.c_str());

        OutType out = omni::sensors::AuxType::NONE;

        switch (hash)
        {
        case CARB_HASH_STRING("none"):
            out = omni::sensors::AuxType::NONE;
            break;
        case CARB_HASH_STRING("basic"):
            out = omni::sensors::AuxType::BASIC;
            break;
        case CARB_HASH_STRING("extra"):
            out = omni::sensors::AuxType::EXTRA;
            break;
        case CARB_HASH_STRING("full"):
            out = omni::sensors::AuxType::FULL;
            break;
        }

        return out;
    }
};


} // namespace nv
} // namespace sensors
} // namespace omni
