// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/datasource/DataSourceUtils.h>
#include <carb/datasource/IDataSource.h>
#include <carb/events/IEvents.h>
#include <carb/imgui/ImGui.h>
#include <carb/input/IInput.h>
#include <carb/input/InputUtils.h>
#include <carb/settings/SettingsUtils.h>
#include <carb/tokens/ITokens.h>

#include <omni/kit/AssetUtils.h>
#include <omni/kit/IFileDialog.h>
#include <omni/kit/SettingsUtils.h>
#include <omni/ui/IGlyphManager.h>

#include <atomic>

namespace omni
{
namespace kit
{
/**
 * Set of helpers to pass std::function in Carbonite interfaces.
 * This is borrowed from <carb/BindingsPythonUtils.h>.
 */
template <typename ReturnT, typename... ArgsT>
class FuncUtils
{
public:
    using StdFuncT = std::function<ReturnT(ArgsT...)>;
    using CallbackT = ReturnT (*)(ArgsT..., void*);

    static ReturnT callbackWithUserData(ArgsT... args, void* userData)
    {
        StdFuncT* fn = (StdFuncT*)userData;
        if (fn)
            return (*fn)(args...);
        else
            return ReturnT();
    }

    static StdFuncT* createStdFuncCopy(const StdFuncT& fn)
    {
        return new StdFuncT(fn);
    }

    static void destroyStdFuncCopy(StdFuncT* fn)
    {
        delete fn;
    }
};

template <class T>
struct StdFuncUtils;

template <class R, class... Args>
struct StdFuncUtils<std::function<R(Args...)>> : public omni::kit::FuncUtils<R, Args...>
{
};

template <class R, class... Args>
struct StdFuncUtils<const std::function<R(Args...)>> : public FuncUtils<R, Args...>
{
};

template <class R, class... Args>
struct StdFuncUtils<const std::function<R(Args...)>&> : public FuncUtils<R, Args...>
{
};

inline omni::kit::IFileDialog* getIFileDialog()
{
    return carb::getCachedInterface<omni::kit::IFileDialog>();
}

inline carb::imgui::ImGui* getImGui()
{
    return carb::getCachedInterface<carb::imgui::ImGui>();
}

inline carb::input::IInput* getInput()
{
    return carb::getCachedInterface<carb::input::IInput>();
}

inline carb::dictionary::IDictionary* getDictionary()
{
    return carb::getCachedInterface<carb::dictionary::IDictionary>();
}

inline carb::settings::ISettings* getSettings()
{
    return carb::getCachedInterface<carb::settings::ISettings>();
}

inline carb::filesystem::IFileSystem* getFileSystem()
{
    return carb::getCachedInterface<carb::filesystem::IFileSystem>();
}

inline omni::ui::IGlyphManager* getGlyphManager()
{
    return carb::getCachedInterface<omni::ui::IGlyphManager>();
}

struct ProcessEventSkipHotkey
{
    carb::input::KeyboardModifierFlags mod;
    carb::input::KeyboardInput key;
};

inline void processImguiInputEvents(ProcessEventSkipHotkey* skipHotkeys = nullptr,
                                    size_t skipHotkeysCount = 0,
                                    carb::input::IInput* input = nullptr,
                                    carb::imgui::ImGui* imgui = nullptr)
{
    if (!imgui)
    {
        imgui = getImGui();
    }
    if (!input)
    {
        input = getInput();
    }

    carb::input::filterBufferedEvents(input, [&](carb::input::InputEvent& evt) -> carb::input::FilterResult {
        if (evt.deviceType != carb::input::DeviceType::eKeyboard)
        {
            return carb::input::FilterResult::eRetain;
        }

        const carb::input::KeyboardEvent* event = &evt.keyboardEvent;
        {
            bool needToConsume = false;
            bool needToFeed = false;

            // Always pass through key release events to make sure keys do not get "stuck".
            // Possibly limit the keys in the future to maintain a map of pressed keys on the widget activation.
            if (event->type == carb::input::KeyboardEventType::eKeyRelease)
            {
                needToConsume = false;
                needToFeed = true;
            }
            else
            {
                // Always consume character input events
                if (event->type == carb::input::KeyboardEventType::eChar)
                {
                    needToConsume = true;
                    needToFeed = true;
                }
                // Do not consume Tab key to allow free navigation
                else if (event->key != carb::input::KeyboardInput::eTab)
                {
                    needToConsume = true;
                    needToFeed = true;
                }

                // Check if the event hotkey is in the list of skip hotkeys, and if so, always avoid passing those to
                // imgui
                if (skipHotkeys)
                {
                    for (size_t hkIdx = 0; hkIdx < skipHotkeysCount; ++hkIdx)
                    {
                        ProcessEventSkipHotkey& skipHk = skipHotkeys[hkIdx];
                        if (event->modifiers == skipHk.mod && event->key == skipHk.key)
                        {
                            needToConsume = false;
                            needToFeed = false;
                            break;
                        }
                    }
                }
            }

            if (needToFeed)
            {
                imgui->feedKeyboardEvent(imgui->getCurrentContext(), *event);
            }
            if (needToConsume)
            {
                return carb::input::FilterResult::eConsume;
            }
        }

        return carb::input::FilterResult::eRetain;
    });
}

// Helper functions for the child windows
inline bool predictActiveProcessImguiInput(const char* widgetIdString,
                                           ProcessEventSkipHotkey* skipHotkeys = nullptr,
                                           size_t skipHotkeysCount = 0)
{
    carb::imgui::ImGui* imgui = getImGui();
    carb::input::IInput* input = getInput();
    uint32_t widgetId = imgui->getIdString(widgetIdString);
    bool isItemPredictedActive = imgui->isItemIdActive(widgetId);
    if (isItemPredictedActive)
    {
        processImguiInputEvents(skipHotkeys, skipHotkeysCount, input, imgui);
    }
    return isItemPredictedActive;
}

inline bool isWritableUrl(const char* url)
{
    bool writable = false;

    auto omniClientDataSource =
        carb::getFramework()->acquireInterface<carb::datasource::IDataSource>("carb.datasource-omniclient.plugin");

    omniClientDataSource->isWritable(
        nullptr, url,
        [](carb::datasource::Response response, const char* path, bool isWritable, void* userData) {
            if (response == carb::datasource::Response::eOk)
            {
                *reinterpret_cast<bool*>(userData) = isWritable;
            }
        },
        &writable);

    return writable;
}

// Copied from Client Library
inline const char* getDefaultUser()
{
    for (auto e : { "OV_USER", "USER", "USERNAME", "LOGNAME" })
    {
#ifdef _MSC_VER
#    pragma warning(push)
#    pragma warning(disable : 4996) // 'sprintf': This function or variable may be unsafe.
#endif
        auto user = getenv(e);
#ifdef _MSC_VER
#    pragma warning(pop)
#endif
        if (user)
        {
            return user;
        }
    }
    return "";
}
}
}
