// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <carb/input/IInput.h>
#include <carb/input/InputTypes.h>

#include <omni/kit/IAppWindow.h>
#include <omni/ui/Workspace.h>

#include <OgnReadMouseStateDatabase.h>

using namespace carb::input;

namespace omni
{
namespace graph
{
namespace ui_nodes
{

// We do not read the specific input for scrolls and movements for four directions
// We only read the coordinates instead, normalized one or absolute one.
constexpr size_t s_numNames = size_t(carb::input::MouseInput::eCount) - 8 + 2;

static std::array<NameToken, s_numNames> s_mouseInputTokens;

class OgnReadMouseState
{
public:
    static bool compute(OgnReadMouseStateDatabase& db)
    {
        NameToken const& mouseIn = db.inputs.mouseElement();

        // First time look up all the token string values
        /*static bool callOnce =*/ (void) ([&db] {
            s_mouseInputTokens = {
                db.tokens.LeftButton,
                db.tokens.RightButton,
                db.tokens.MiddleButton,
                db.tokens.ForwardButton,
                db.tokens.BackButton,
                db.tokens.MouseCoordsNormalized,
                db.tokens.MouseCoordsPixel
            };
        } (), true);

        omni::kit::IAppWindow* appWindow = omni::kit::getDefaultAppWindow();
        if (!appWindow)
        {
            return false;
        }

        Mouse* mouse = appWindow->getMouse();
        if (!mouse)
        {
            CARB_LOG_ERROR_ONCE("No Mouse!");
            return false;
        }

        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
        {
            CARB_LOG_ERROR_ONCE("No Input!");
            return false;
        }

        bool isPressed = false;

        // Get the index of the token of the mouse input of interest
        auto iter = std::find(s_mouseInputTokens.begin(), s_mouseInputTokens.end(), mouseIn);
        if (iter == s_mouseInputTokens.end())
            return true;

        size_t token_index = iter - s_mouseInputTokens.begin();
        if (token_index < 5) // Mouse Input is related to a button
        {
            MouseInput button = MouseInput(token_index);
            isPressed = (carb::input::kButtonFlagStateDown & input->getMouseButtonFlags(mouse, button));
            db.outputs.isPressed() = isPressed;
        }
        else // Mouse Input is position
        {
            carb::Float2 coords = input->getMouseCoordsPixel(mouse);

            bool foundWindow{ false };
            NameToken windowToken = omni::fabric::kUninitializedToken;
            float windowWidth = static_cast<float>(appWindow->getWidth());
            float windowHeight = static_cast<float>(appWindow->getHeight());

            if (db.inputs.useRelativeCoords())
            {
                // Find the workspace window the mouse pointer is over, and convert the coords to window-relative
                for (auto const& window : omni::ui::Workspace::getWindows())
                {
                    if ((window->isDocked() && !window->isSelectedInDock()) || !window->isVisible())
                        continue;

                    std::string const& windowTitle = window->getTitle();
                    if (windowTitle == "DockSpace")
                        continue;

                    float dpiScale = omni::ui::Workspace::getDpiScale();
                    float left = window->getPositionX() * dpiScale;
                    float top = window->getPositionY() * dpiScale;
                    float curWindowWidth = window->getWidth() * dpiScale;
                    float curWindowHeight = window->getHeight() * dpiScale;
                    if (coords.x >= left && coords.y >= top && coords.x <= left + curWindowWidth &&
                        coords.y <= top + curWindowHeight)
                    {
                        foundWindow = true;
                        coords.x -= left;
                        coords.y -= top;
                        windowToken = db.stringToToken(windowTitle.c_str());
                        windowWidth = curWindowWidth;
                        windowHeight = curWindowHeight;

                        break;
                    }
                }
            }
            else
            {
                foundWindow = true;
            }

            float* data = db.outputs.coords().data();
            if (foundWindow)
            {
                if (*iter == db.tokens.MouseCoordsNormalized)
                {
                    coords.x /= windowWidth;
                    coords.y /= windowHeight;
                }

                data[0] = coords.x;
                data[1] = coords.y;
            }
            else
            {
                data[0] = 0.f;
                data[1] = 0.f;
            }

            if (windowToken == omni::fabric::kUninitializedToken)
                windowToken = db.stringToToken("");

            db.outputs.window() = windowToken;
        }
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace ui_nodes
} // namespace graph
} // namespace omni
