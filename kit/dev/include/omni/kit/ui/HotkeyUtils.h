// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/InterfaceUtils.h>
#include <carb/imgui/ImGui.h>
#include <carb/input/IInput.h>
#include <carb/input/InputUtils.h>

#include <imgui/imgui.h>

#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Classical keyboard Hotkey (modifier + key). Can be polled, works nicely with imgui windows.
 */
class Hotkey
{
public:
    void initialize(carb::input::KeyboardModifierFlags mod, carb::input::KeyboardInput key, std::string displayName = "")
    {
        m_key = key;
        m_mod = mod;
        m_displayName = displayName;

        m_shortcut = carb::input::getModifierFlagsString(mod);
        if (!m_shortcut.empty())
            m_shortcut += " + ";
        m_shortcut += carb::input::getKeyboardInputString(key);
    }

    bool isPressedInCurrentWindow(carb::imgui::ImGui* imgui, carb::input::Keyboard* keyboard) const
    {
        return imgui->isWindowFocused(carb::imgui::kFocusedFlagRootAndChildWindows) && isPressed(keyboard, m_mod, m_key);
    }

    bool isPressed(carb::input::Keyboard* keyboard) const
    {
        return isPressed(keyboard, m_mod, m_key);
    }

    static bool isPressed(carb::input::Keyboard* keyboard,
                          carb::input::KeyboardModifierFlags mod,
                          carb::input::KeyboardInput key)
    {
        using namespace carb::input;
        if ((uint32_t)key >= (uint32_t)carb::input::KeyboardInput::eCount)
        {
            return false;
        }

        // TODO: That's not correct to use ImGui directly here. It's better to add this functionality to
        // carb::imgui::ImGui, but it's not possible to update it at this moment because physxui that is also using
        // carb::imgui::ImGui is blocked. The only way to access WantCaptureKeyboard is using directly ImGui.
        ::ImGuiIO& io = ::ImGui::GetIO();
        if (io.WantCaptureKeyboard)
        {
            // When wantCaptureKeyboard is true, ImGui is using the keyboard input exclusively, and it's not necessary
            // to dispatch the input to the application. (e.g. InputText active, or an ImGui window is focused and
            // navigation is enabled, etc.).
            return false;
        }

        carb::input::IInput* input = carb::getCachedInterface<carb::input::IInput>();
        const auto isKeyPressed = [input, keyboard](KeyboardInput key) {
            return (input->getKeyboardButtonFlags(keyboard, key) & kButtonFlagTransitionDown);
        };
        const auto isUp = [input, keyboard](KeyboardInput key) {
            return (input->getKeyboardButtonFlags(keyboard, key) & kButtonFlagStateUp);
        };
        const auto isDown = [input, keyboard](KeyboardInput key) {
            return (input->getKeyboardButtonFlags(keyboard, key) & kButtonFlagStateDown);
        };

        if (!isKeyPressed(key))
            return false;
        if (!(mod & kKeyboardModifierFlagShift) &&
            (isDown(KeyboardInput::eLeftShift) || isDown(KeyboardInput::eRightShift)))
            return false;
        if (!(mod & kKeyboardModifierFlagControl) &&
            (isDown(KeyboardInput::eLeftControl) || isDown(KeyboardInput::eRightControl)))
            return false;
        if (!(mod & kKeyboardModifierFlagAlt) && (isDown(KeyboardInput::eLeftAlt) || isDown(KeyboardInput::eRightAlt)))
            return false;
        if ((mod & kKeyboardModifierFlagShift) && isUp(KeyboardInput::eLeftShift) && isUp(KeyboardInput::eRightShift))
            return false;
        if ((mod & kKeyboardModifierFlagControl) && isUp(KeyboardInput::eLeftControl) &&
            isUp(KeyboardInput::eRightControl))
            return false;
        if ((mod & kKeyboardModifierFlagAlt) && isUp(KeyboardInput::eLeftAlt) && isUp(KeyboardInput::eRightAlt))
            return false;
        if ((mod & kKeyboardModifierFlagSuper) && isUp(KeyboardInput::eLeftSuper) && isUp(KeyboardInput::eRightSuper))
            return false;
        if ((mod & kKeyboardModifierFlagCapsLock) && isUp(KeyboardInput::eCapsLock))
            return false;
        if ((mod & kKeyboardModifierFlagNumLock) && isUp(KeyboardInput::eNumLock))
            return false;

        return true;
    }

    const char* getDisplayName() const
    {
        return m_displayName.c_str();
    }

    const char* getShortcut() const
    {
        return m_shortcut.c_str();
    }

    carb::input::KeyboardInput getKey() const
    {
        return m_key;
    }
    carb::input::KeyboardModifierFlags getModifiers() const
    {
        return m_mod;
    }

private:
    carb::input::KeyboardInput m_key = carb::input::KeyboardInput::eCount;
    carb::input::KeyboardModifierFlags m_mod = 0;
    std::string m_shortcut;
    std::string m_displayName;
};
}
}
}
