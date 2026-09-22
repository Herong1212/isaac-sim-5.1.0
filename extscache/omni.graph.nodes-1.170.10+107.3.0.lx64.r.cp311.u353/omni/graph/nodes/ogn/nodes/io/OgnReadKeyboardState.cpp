// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnReadKeyboardStateDatabase.h>

#include <carb/input/IInput.h>
#include <carb/input/InputTypes.h>

#include <omni/kit/IAppWindow.h>

#include "CoverageUtils.h"

using namespace carb::input;

namespace omni
{
namespace graph
{
namespace action
{

// This list matches carb::input::KeyboardInput
constexpr size_t s_numNames = size_t(carb::input::KeyboardInput::eCount);
static constexpr std::array<const char*, s_numNames> s_keyNames = { "Unknown",
                                                                    "Space",
                                                                    "Apostrophe",
                                                                    "Comma",
                                                                    "Minus",
                                                                    "Period",
                                                                    "Slash",
                                                                    "Key0",
                                                                    "Key1",
                                                                    "Key2",
                                                                    "Key3",
                                                                    "Key4",
                                                                    "Key5",
                                                                    "Key6",
                                                                    "Key7",
                                                                    "Key8",
                                                                    "Key9",
                                                                    "Semicolon",
                                                                    "Equal",
                                                                    "A",
                                                                    "B",
                                                                    "C",
                                                                    "D",
                                                                    "E",
                                                                    "F",
                                                                    "G",
                                                                    "H",
                                                                    "I",
                                                                    "J",
                                                                    "K",
                                                                    "L",
                                                                    "M",
                                                                    "N",
                                                                    "O",
                                                                    "P",
                                                                    "Q",
                                                                    "R",
                                                                    "S",
                                                                    "T",
                                                                    "U",
                                                                    "V",
                                                                    "W",
                                                                    "X",
                                                                    "Y",
                                                                    "Z",
                                                                    "LeftBracket",
                                                                    "Backslash",
                                                                    "RightBracket",
                                                                    "GraveAccent",
                                                                    "Escape",
                                                                    "Tab",
                                                                    "Enter",
                                                                    "Backspace",
                                                                    "Insert",
                                                                    "Del",
                                                                    "Right",
                                                                    "Left",
                                                                    "Down",
                                                                    "Up",
                                                                    "PageUp",
                                                                    "PageDown",
                                                                    "Home",
                                                                    "End",
                                                                    "CapsLock",
                                                                    "ScrollLock",
                                                                    "NumLock",
                                                                    "PrintScreen",
                                                                    "Pause",
                                                                    "F1",
                                                                    "F2",
                                                                    "F3",
                                                                    "F4",
                                                                    "F5",
                                                                    "F6",
                                                                    "F7",
                                                                    "F8",
                                                                    "F9",
                                                                    "F10",
                                                                    "F11",
                                                                    "F12",
                                                                    "Numpad0",
                                                                    "Numpad1",
                                                                    "Numpad2",
                                                                    "Numpad3",
                                                                    "Numpad4",
                                                                    "Numpad5",
                                                                    "Numpad6",
                                                                    "Numpad7",
                                                                    "Numpad8",
                                                                    "Numpad9",
                                                                    "NumpadDel",
                                                                    "NumpadDivide",
                                                                    "NumpadMultiply",
                                                                    "NumpadSubtract",
                                                                    "NumpadAdd",
                                                                    "NumpadEnter",
                                                                    "NumpadEqual",
                                                                    "LeftShift",
                                                                    "LeftControl",
                                                                    "LeftAlt",
                                                                    "LeftSuper",
                                                                    "RightShift",
                                                                    "RightControl",
                                                                    "RightAlt",
                                                                    "RightSuper",
                                                                    "Menu" };
static_assert(s_keyNames.size() == size_t(carb::input::KeyboardInput::eCount), "enum must match this table");

static std::array<NameToken, s_numNames> s_keyTokens;

class OgnReadKeyboardState
{
public:
    static bool compute(OgnReadKeyboardStateDatabase& db)
    {
        NameToken const& keyIn = db.inputs.key();
        auto contextObj = db.abi_context();

        // First time look up all the token string values
        [[maybe_unused]] static bool callOnce = ([&contextObj] {
            std::transform(s_keyNames.begin(), s_keyNames.end(), s_keyTokens.begin(),
                [&contextObj](auto const& s) { return contextObj.iToken->getHandle(s); });
        } (), true);

        omni::kit::IAppWindow* appWindow = omni::kit::getDefaultAppWindow();
        FIREWALL_RETURN(!appWindow, false); // LCOV_EXCL_LINE

        Keyboard* keyboard = appWindow->getKeyboard();
        FIREWALL_RET_ERROR(db, !keyboard, false, "No Keyboard!"); // LCOV_EXCL_LINE

        IInput* input = carb::getCachedInterface<IInput>();
        FIREWALL_RET_ERROR(db, !input, false, "No Input!"); // LCOV_EXCL_LINE

        bool isPressed = false;
        // Get the index of the token of the key of interest
        auto iter = std::find(s_keyTokens.begin(), s_keyTokens.end(), keyIn);
        if (iter != s_keyTokens.end())
        {
            size_t index = iter - s_keyTokens.begin();
            KeyboardInput key = KeyboardInput(index);

            isPressed = (carb::input::kButtonFlagStateDown & input->getKeyboardButtonFlags(keyboard, key));
        }
        db.outputs.shiftOut() =
            (carb::input::kButtonFlagStateDown & input->getKeyboardButtonFlags(keyboard, KeyboardInput::eLeftShift)) ||
            (carb::input::kButtonFlagStateDown & input->getKeyboardButtonFlags(keyboard, KeyboardInput::eRightShift));
        db.outputs.ctrlOut() =
            (carb::input::kButtonFlagStateDown & input->getKeyboardButtonFlags(keyboard, KeyboardInput::eLeftControl)) ||
            (carb::input::kButtonFlagStateDown & input->getKeyboardButtonFlags(keyboard, KeyboardInput::eRightControl));
        db.outputs.altOut() =
            (carb::input::kButtonFlagStateDown & input->getKeyboardButtonFlags(keyboard, KeyboardInput::eLeftAlt)) ||
            (carb::input::kButtonFlagStateDown & input->getKeyboardButtonFlags(keyboard, KeyboardInput::eRightAlt));
        db.outputs.isPressed() = isPressed;
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
