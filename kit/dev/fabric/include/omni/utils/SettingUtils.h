// Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/settings/ISettings.h>
#include <carb/settings/SettingsUtils.h>
#include "IPtr.h"

namespace omni
{
    template<typename T>
    struct CachedSetting
    {
        CachedSetting(const char* settingPath)
        {
            if (m_settings.m_ptr)
            {
                m_subscription = m_settings->subscribeToNodeChangeEvents(
                    settingPath,
                    [](const carb::dictionary::Item* changedItem, carb::dictionary::ChangeEventType changeEventType, void* userData)
                    {
                        if (changeEventType == carb::dictionary::ChangeEventType::eChanged)
                        {
                            T* valuePtr = (T*)userData;
                            *valuePtr = carb::getCachedInterface<carb::dictionary::IDictionary>()->get<T>(changedItem);
                        }
                    },
                    &m_value);
                m_value = m_settings->get<T>(settingPath);
            }
        }

        CachedSetting(const char* settingPath, const T& defaultValue)
            : CachedSetting(settingPath)
        {
            if (m_settings.m_ptr)
            {
                m_settings->setDefault(settingPath, defaultValue);
            }
        }

        ~CachedSetting()
        {
            if (m_subscription && m_settings.m_ptr)
            {
                m_settings->unsubscribeToChangeEvents(m_subscription);
                m_subscription = nullptr;
            }
        }

        const T& get() const
        {
            return m_value;
        }

        CachedIPtr<carb::settings::ISettings> m_settings;
        carb::dictionary::SubscriptionId* m_subscription = nullptr;
        T m_value;
    };

    template<typename T>
    struct CachedSettingWithPath : CachedSetting<T>
    {
        CachedSettingWithPath(const char* settingPath)
            : CachedSetting<T>(settingPath)
            , m_path(settingPath)
        {
        }

        CachedSettingWithPath(const char* settingPath, const T& defaultValue)
            : CachedSetting<T>(settingPath, defaultValue)
            , m_path(settingPath)
        {
        }

        void set(const T& value)
        {
            this->m_settings->set(m_path.c_str(), value);
        }

        std::string m_path;
    };

}
