// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ActionNodeCommon.h"

#include <carb/input/IInput.h>
#include <carb/input/InputTypes.h>

#include <omni/graph/action/IActionGraph.h>
#include <omni/kit/IAppWindow.h>

#include <OgnOnMouseInputDatabase.h>
#include <thread>

using namespace carb::input;

namespace omni
{
namespace graph
{
namespace action
{

// Three buttons, normalized or absolute movements and scroll
constexpr size_t s_numNames = 6;

static std::array<NameToken, s_numNames> s_elementTokens;

class OgnOnMouseInput
{
public:
    SubscriptionId m_mouseEventSubsId{ 0 };
    MouseEvent m_mouseEvent;
    exec::unstable::Stamp m_elementSetStamp; // The stamp set by the authoring node when the event occurs
    exec::unstable::SyncStamp m_elementSetSyncStamp; // The stamp used by each instance

    static bool onMouseEvent(const InputEvent& e, void* userData)
    {
        if (e.deviceType != DeviceType::eMouse)
        {
            return false;
        }
        NodeHandle nodeHandle = reinterpret_cast<NodeHandle>(userData);

        auto iNode = carb::getCachedInterface<omni::graph::core::INode>();
        NodeObj nodeObj = iNode->getNodeFromHandle(nodeHandle);
        if (!nodeObj.isValid())
            return false;

        auto& authoringState = OgnOnMouseInputDatabase::sSharedState<OgnOnMouseInput>(nodeObj);

        authoringState.m_elementSetStamp.next();
        authoringState.m_mouseEvent = e.mouseEvent;

        iNode->requestCompute(nodeObj);

        return true;
    }


    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        // First time initialization will fill up the token array
        [[maybe_unused]] static bool callOnce = ([]
        {   s_elementTokens = {
                OgnOnMouseInputDatabase::tokens.LeftButton,
                OgnOnMouseInputDatabase::tokens.MiddleButton,
                OgnOnMouseInputDatabase::tokens.RightButton,
                OgnOnMouseInputDatabase::tokens.NormalizedMove,
                OgnOnMouseInputDatabase::tokens.PixelMove,
                OgnOnMouseInputDatabase::tokens.Scroll
            };
        } (), true);

        omni::kit::IAppWindow* appWindow = omni::kit::getDefaultAppWindow();
        if (!appWindow)
            return;

        // TODO: We may want to change the mouse into a camera one instead of appWindow one.
        Mouse* mouse = appWindow->getMouse();
        if (!mouse)
            return;

        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
            return;

        auto& authoringState = OgnOnMouseInputDatabase::sSharedState<OgnOnMouseInput>(nodeObj);


        // Someone will consume the mouse event so cannot subscribe this as the last one.
        // TODO: Is it good to subscribe this to the front?
        authoringState.m_mouseEventSubsId =
            input->subscribeToInputEvents((carb::input::InputDevice*)mouse, kEventTypeAll, onMouseEvent,
                                          reinterpret_cast<void*>(nodeObj.nodeHandle), kSubscriptionOrderFirst);
    }

    static void release(const NodeObj& nodeObj)
    {
        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
            return;

        auto const& authoringState = OgnOnMouseInputDatabase::sSharedState<OgnOnMouseInput>(nodeObj);

        if (authoringState.m_mouseEventSubsId > 0)
        {
            input->unsubscribeToInputEvents(authoringState.m_mouseEventSubsId);
        }
    }

    static bool compute(OgnOnMouseInputDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        auto const& authoringState = db.sharedState<OgnOnMouseInput>();
        auto& localState = db.perInstanceState<OgnOnMouseInput>();

        if (localState.m_elementSetSyncStamp.makeSync(authoringState.m_elementSetStamp))
        {
            NameToken const& elementIn = db.inputs.mouseElement();

            size_t const eventIndex = static_cast<size_t>(authoringState.m_mouseEvent.type);
            bool eventMatched = false;
            if (eventIndex < 6) // Left/Middle/Right Buttons
            {
                eventMatched = s_elementTokens[eventIndex / 2] == elementIn;
            }
            else if (eventIndex == 6) // Move
            {
                eventMatched = elementIn == db.tokens.NormalizedMove || elementIn == db.tokens.PixelMove;
            }
            else if (eventIndex == 7) // Scroll
            {
                eventMatched = elementIn == db.tokens.Scroll;
            }
            else
            {
                db.logError("Invalid Input Event %zu detected", eventIndex);
            }

            float* deltaValue = db.outputs.value().data();
            carb::Float2 eventValue{ 0.0f, 0.0f };
            auto iActionGraph = getInterface();
            if (eventMatched)
            {
                switch (authoringState.m_mouseEvent.type)
                {
                case MouseEventType::eLeftButtonDown:
                case MouseEventType::eMiddleButtonDown:
                case MouseEventType::eRightButtonDown:
                    db.outputs.isPressed() = true;
                    iActionGraph->setExecutionEnabled(outputs::pressed.token(), db.getInstanceIndex());
                    break;
                case MouseEventType::eLeftButtonUp:
                case MouseEventType::eMiddleButtonUp:
                case MouseEventType::eRightButtonUp:
                    db.outputs.isPressed() = false;
                    iActionGraph->setExecutionEnabled(outputs::released.token(), db.getInstanceIndex());
                    break;
                case MouseEventType::eMove:
                    db.outputs.isPressed() = false;
                    iActionGraph->setExecutionEnabled(outputs::valueChanged.token(), db.getInstanceIndex());
                    if (elementIn == db.tokens.NormalizedMove)
                    {
                        eventValue = authoringState.m_mouseEvent.normalizedCoords;
                    }
                    else
                    {
                        eventValue = authoringState.m_mouseEvent.pixelCoords;
                    }
                    break;
                case MouseEventType::eScroll:
                    db.outputs.isPressed() = false;
                    iActionGraph->setExecutionEnabled(outputs::valueChanged.token(), db.getInstanceIndex());
                    eventValue = authoringState.m_mouseEvent.scrollDelta;
                    break;
                default:
                    break;
                }
            }
            deltaValue[0] = eventValue.x;
            deltaValue[1] = eventValue.y;
        }
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace action
} // namespace graph
} // namespace omni
