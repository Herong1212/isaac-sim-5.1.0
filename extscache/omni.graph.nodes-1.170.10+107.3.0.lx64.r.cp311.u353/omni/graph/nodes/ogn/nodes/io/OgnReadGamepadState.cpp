// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnReadGamepadStateDatabase.h>
#include <carb/input/IInput.h>
#include <carb/input/InputTypes.h>

#include <omni/kit/IAppWindow.h>

#include "CoverageUtils.h"

using namespace carb::input;

namespace omni
{
namespace graph
{
namespace nodes
{

// This is different from carb::input::GamepadInput::eCount by 4 because we combine the joystick inputs by axis (x/y)
constexpr size_t s_numNames = size_t(carb::input::GamepadInput::eCount) - 4;

static std::array<NameToken, s_numNames> s_elementTokens;

class OgnReadGamepadState
{
public:
    static bool compute(OgnReadGamepadStateDatabase& db)
    {
        NameToken const& elementIn = db.inputs.gamepadElement();
        const unsigned int gamepadId = db.inputs.gamepadId();
        const float deadzone = db.inputs.deadzone();

        // First time initialization of all the token values
        [[maybe_unused]] static bool callOnce = ([&db] {
            s_elementTokens = {
                db.tokens.LeftStickXAxis,
                db.tokens.LeftStickYAxis,
                db.tokens.RightStickXAxis,
                db.tokens.RightStickYAxis,
                db.tokens.LeftTrigger,
                db.tokens.RightTrigger,
                db.tokens.FaceButtonBottom,
                db.tokens.FaceButtonRight,
                db.tokens.FaceButtonLeft,
                db.tokens.FaceButtonTop,
                db.tokens.LeftShoulder,
                db.tokens.RightShoulder,
                db.tokens.SpecialLeft,
                db.tokens.SpecialRight,
                db.tokens.LeftStickButton,
                db.tokens.RightStickButton,
                db.tokens.DpadUp,
                db.tokens.DpadRight,
                db.tokens.DpadDown,
                db.tokens.DpadLeft
            };
        } (), true);

        omni::kit::IAppWindow* appWindow = omni::kit::getDefaultAppWindow();
        FIREWALL_RETURN(!appWindow, false); // LCOV_EXCL_LINE

        Gamepad* gamepad = appWindow->getGamepad(gamepadId);
        FIREWALL_RET_WARN(db, !gamepad, false, "No Gamepad!"); // LCOV_EXCL_LINE

        IInput* input = carb::getCachedInterface<IInput>();
        FIREWALL_RET_WARN(db, !input, false, "No Input!"); // LCOV_EXCL_LINE

        bool isPressed = false;
        float value = 0.0;
        // Get the index of the token of the element of interest
        auto iter = std::find(s_elementTokens.begin(), s_elementTokens.end(), elementIn);
        if (iter != s_elementTokens.end())
        {
            size_t index = iter - s_elementTokens.begin();
            if (index < 4)
            {
                // We want to combine the joystick inputs by its axis (x/y instead of right/left/up/down)
                GamepadInput positiveElement = GamepadInput(2 * index);
                GamepadInput negativeElement = GamepadInput(2 * index + 1);
                value =
                    input->getGamepadValue(gamepad, positiveElement) - input->getGamepadValue(gamepad, negativeElement);
            }
            else
            {
                // index is offset by 4 because we combine the joystick x/y axis
                GamepadInput element = GamepadInput(index + 4);
                value = input->getGamepadValue(gamepad, element);
            }

            // Check for deadzone threshold
            if (std::abs(value) < deadzone)
            {
                value = 0.0;
                isPressed = false;
            }
            else
            {
                isPressed = true;
            }
        }
        db.outputs.isPressed() = isPressed;
        db.outputs.value() = value;
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
