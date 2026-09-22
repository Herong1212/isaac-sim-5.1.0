// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <OgnOnGamepadInputDatabase.h>
#include <atomic>

using namespace carb::input;

namespace omni
{
namespace graph
{
namespace action
{

// This is different from carb::input::GamepadInput::eCount by 10 because we don't allow joysticks and triggers input.
constexpr auto s_firstEventWeCareAbout = carb::input::GamepadInput::eA;
constexpr size_t s_numNames = size_t(carb::input::GamepadInput::eCount) - size_t(s_firstEventWeCareAbout);

static std::array<NameToken, s_numNames> s_elementTokens;

class OgnOnGamepadInput
{
public:
    // Assume a zero subsId means not registered
    SubscriptionId m_gamepadConnectionSubsId{ 0 };
    SubscriptionId m_elementEventSubsId{ 0 };
    GamepadEvent m_elementEvent;
    std::atomic<bool> m_requestedRegistrationInCompute{ false }; // Dirty flag to ask compute() to potentially subscribe
                                                                 // to the new gamepad if needed
    exec::unstable::Stamp m_elementSetStamp; // The stamp set by the authoring node when the even occurs
    exec::unstable::SyncStamp m_elementSetSyncStamp; // The stamp used by each instance

    static bool trySwitchGamepadSubscription(const size_t newGamepadId, const NodeObj& nodeObj)
    {
        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
            return false;

        auto& state = OgnOnGamepadInputDatabase::sSharedState<OgnOnGamepadInput>(nodeObj);
        omni::kit::IAppWindow* appWindow = omni::kit::getDefaultAppWindow();
        if (!appWindow)
        {
            return false;
        }

        Gamepad* gamepad = appWindow->getGamepad(newGamepadId);
        if (!gamepad)
        {
            CARB_LOG_WARN_ONCE("The new gamepad ID is not associated with any gamepad");
            if (state.m_elementEventSubsId > 0)
            {
                input->unsubscribeToInputEvents(state.m_elementEventSubsId);
            }
            state.m_elementEventSubsId = 0;
            return false;
        }

        if (state.m_elementEventSubsId > 0)
        {
            input->unsubscribeToInputEvents(state.m_elementEventSubsId);
        }

        state.m_elementEventSubsId =
            input->subscribeToInputEvents((carb::input::InputDevice*)gamepad, kEventTypeAll, onGamepadEvent,
                                          reinterpret_cast<void*>(nodeObj.nodeHandle), kSubscriptionOrderDefault);

        return true;
    }

    static bool onGamepadEvent(const InputEvent& e, void* userData)
    {
        if (e.deviceType != DeviceType::eGamepad)
        {
            return false;
        }

        NodeHandle nodeHandle = reinterpret_cast<NodeHandle>(userData);

        auto iNode = carb::getCachedInterface<omni::graph::core::INode>();
        NodeObj nodeObj = iNode->getNodeFromHandle(nodeHandle);
        if (!nodeObj.isValid())
            return false;

        // Copy the event data and request the next compute()
        auto& authoringState = OgnOnGamepadInputDatabase::sSharedState<OgnOnGamepadInput>(nodeObj);

        authoringState.m_elementSetStamp.next();
        authoringState.m_elementEvent = e.gamepadEvent;

        iNode->requestCompute(nodeObj);

        return true;
    }

    static void onGamepadIdChanged(const AttributeObj& attrObj, const void* value)
    {
        NodeObj nodeObj{ attrObj.iAttribute->getNode(attrObj) };
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return;

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return;

        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        if (context.contextHandle == kInvalidGraphContextHandle)
            return;

        ConstAttributeDataHandle attributeDataHandle =
            attrObj.iAttribute->getConstAttributeDataHandle(attrObj, kAccordingToContextIndex);
        const uint32_t gamepadId = *getDataR<uint32_t>(context, attributeDataHandle);

        // Change subscription target
        trySwitchGamepadSubscription(gamepadId, nodeObj);
    }

    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        // First time look up all the tokens and their lowercase equivalents
        [[maybe_unused]] static bool callOnce = ([] {
            s_elementTokens = {
                OgnOnGamepadInputDatabase::tokens.FaceButtonBottom,
                OgnOnGamepadInputDatabase::tokens.FaceButtonRight,
                OgnOnGamepadInputDatabase::tokens.FaceButtonLeft,
                OgnOnGamepadInputDatabase::tokens.FaceButtonTop,
                OgnOnGamepadInputDatabase::tokens.LeftShoulder,
                OgnOnGamepadInputDatabase::tokens.RightShoulder,
                OgnOnGamepadInputDatabase::tokens.SpecialLeft,
                OgnOnGamepadInputDatabase::tokens.SpecialRight,
                OgnOnGamepadInputDatabase::tokens.LeftStickButton,
                OgnOnGamepadInputDatabase::tokens.RightStickButton,
                OgnOnGamepadInputDatabase::tokens.DpadUp,
                OgnOnGamepadInputDatabase::tokens.DpadRight,
                OgnOnGamepadInputDatabase::tokens.DpadDown,
                OgnOnGamepadInputDatabase::tokens.DpadLeft
            };
        } (), true);

        // Get the default or stored gamepad ID when creating new nodes or loading a saved file
        auto gamepadIdAttr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::gamepadId.token());

        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
            return; // Happens normally in headless

        auto& authoringState = OgnOnGamepadInputDatabase::sSharedState<OgnOnGamepadInput>(nodeObj);

        authoringState.m_requestedRegistrationInCompute.store(true);

        gamepadIdAttr.iAttribute->registerValueChangedCallback(gamepadIdAttr, onGamepadIdChanged, true);

        // This will allow user to connect gamepad after specifying gamepad ID
        authoringState.m_gamepadConnectionSubsId = input->subscribeToGamepadConnectionEvents(
            [](const carb::input::GamepadConnectionEvent& evt, void* userData)
            {
                NodeHandle nodeHandle = reinterpret_cast<NodeHandle>(userData);
                auto iNode = carb::getCachedInterface<omni::graph::core::INode>();
                NodeObj nodeObj = iNode->getNodeFromHandle(nodeHandle);
                auto& state = OgnOnGamepadInputDatabase::sSharedState<OgnOnGamepadInput>(nodeObj);
                state.m_requestedRegistrationInCompute.store(true);
                // Since the subscription depends on another GamepadConnectionEvents in IAppWindowImplCommon, and we
                // cannot assume the execution order
                iNode->requestCompute(nodeObj);
            },
            reinterpret_cast<void*>(nodeObj.nodeHandle));
    }

    static void release(const NodeObj& nodeObj)
    {
        auto& authoringState = OgnOnGamepadInputDatabase::sSharedState<OgnOnGamepadInput>(nodeObj);
        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
            return;

        if (authoringState.m_elementEventSubsId > 0)
        {
            input->unsubscribeToInputEvents(authoringState.m_elementEventSubsId);
        }

        if (authoringState.m_gamepadConnectionSubsId > 0)
        {
            input->unsubscribeToGamepadConnectionEvents(authoringState.m_gamepadConnectionSubsId);
        }
    }

    static bool compute(OgnOnGamepadInputDatabase& db)
    {
        auto& authoringState = db.sharedState<OgnOnGamepadInput>();
        auto& localState = db.perInstanceState<OgnOnGamepadInput>();

        // Retry subscribe gamepad when new gamepad is connected
        if (authoringState.m_requestedRegistrationInCompute.exchange(false))
        {
            trySwitchGamepadSubscription(db.inputs.gamepadId(), db.abi_node());
        }

        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        if (localState.m_elementSetSyncStamp.makeSync(authoringState.m_elementSetStamp))
        {
            NameToken const& gamepadElementIn = db.inputs.gamepadElementIn();

            // Offset the index by 10 since we excluded the joysticks and triggers.
            if (size_t(authoringState.m_elementEvent.input) < size_t(s_firstEventWeCareAbout))
                return true;

            size_t elementIndex = size_t(authoringState.m_elementEvent.input) - size_t(s_firstEventWeCareAbout);
            if (elementIndex >= s_elementTokens.size())
            {
                db.logError("Invalid Key %d detected", authoringState.m_elementEvent.input);
                return false;
            }
            auto iActionGraph = getInterface();
            if (gamepadElementIn == s_elementTokens[elementIndex])
            {
                if (authoringState.m_elementEvent.value == 1)
                {
                    iActionGraph->setExecutionEnabled(
                        outputs::pressed.token(), omni::graph::core::kAccordingToContextIndex);
                    db.outputs.isPressed() = true;
                }
                else
                {
                    iActionGraph->setExecutionEnabled(
                        outputs::released.token(), omni::graph::core::kAccordingToContextIndex);
                    db.outputs.isPressed() = false;
                }
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace action
} // namespace graph
} // namespace omni
