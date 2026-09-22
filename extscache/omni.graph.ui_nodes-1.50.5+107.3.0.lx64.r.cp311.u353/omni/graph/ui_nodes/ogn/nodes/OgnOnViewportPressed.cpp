// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ViewportPressNodeCommon.h"

#include <omni/kit/IApp.h>
#include <omni/ui/Workspace.h>

#include <OgnOnViewportPressedDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnOnViewportPressed
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr pressBeganSub;
        carb::events::ISubscriptionPtr pressEndedSub;
        ViewportPressEventPayloads eventPayloads;
        ViewportPressEventStates eventStates;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnOnViewportPressed& state = OgnOnViewportPressedDatabase::sSharedState<OgnOnViewportPressed>(nodeObj);

        // Subscribe to press events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.pressBeganSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kPressBeganEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportPressed& state =
                            OgnOnViewportPressedDatabase::sSharedState<OgnOnViewportPressed>(nodeObj);
                        state.m_internalState.eventPayloads.clear(); // invalidate previous payloads
                        state.m_internalState.eventPayloads.setPressBeganPayload(e->payload);
                        state.m_setStamp.next();
                        if (nodeObj.iNode->isValid(nodeObj))
                            nodeObj.iNode->requestCompute(nodeObj);
                    }
                });
            state.m_internalState.pressEndedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kPressEndedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportPressed& state =
                            OgnOnViewportPressedDatabase::sSharedState<OgnOnViewportPressed>(nodeObj);
                        state.m_internalState.eventPayloads.setPressEndedPayload(e->payload);
                        state.m_setStamp.next();

                        if (nodeObj.iNode->isValid(nodeObj))
                            nodeObj.iNode->requestCompute(nodeObj);
                    }
                });
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnOnViewportPressed& state = OgnOnViewportPressedDatabase::sSharedState<OgnOnViewportPressed>(nodeObj);

        // Unsubscribe from press events
        if (state.m_internalState.pressBeganSub.get())
            state.m_internalState.pressBeganSub.detach()->unsubscribe();

        if (state.m_internalState.pressEndedSub.get())
            state.m_internalState.pressEndedSub.detach()->unsubscribe();
    }

    static bool compute(OgnOnViewportPressedDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        OgnOnViewportPressed& sharedState = db.sharedState<OgnOnViewportPressed>();
        OgnOnViewportPressed& perInstanceState = db.perInstanceState<OgnOnViewportPressed>();

        if (perInstanceState.m_syncStamp.makeSync(sharedState.m_setStamp))
        {
            if (sharedState.m_internalState.eventPayloads.empty())
                return true;

            // Get the targeted viewport and gesture
            char const* const viewportWindowName = db.tokenToString(db.inputs.viewport());
            char const* const gestureName = db.tokenToString(db.inputs.gesture());

            if (!omni::ui::Workspace::getWindow(viewportWindowName))
            {
                db.logWarning("Viewport window '%s' not found", viewportWindowName);
            }

            // Process event payloads and update event state
            bool pressBegan = false;
            for (auto const& pressBeganPayload : sharedState.m_internalState.eventPayloads.pressBeganPayloads())
            {
                if (!pressBeganPayload.second.isValid)
                    continue;

                auto& eventStateValue = sharedState.m_internalState.eventStates[pressBeganPayload.first];

                eventStateValue.pressPositionNorm = pressBeganPayload.second.pressPositionNorm;
                eventStateValue.pressPositionPixel = pressBeganPayload.second.pressPositionPixel;

                eventStateValue.releasePositionNorm = { 0.0, 0.0 };
                eventStateValue.releasePositionPixel = { 0.0, 0.0 };

                eventStateValue.isPressed = true;
                eventStateValue.isReleasePositionValid = false;

                if (std::strcmp(viewportWindowName, pressBeganPayload.first.viewportWindowName) == 0 &&
                    std::strcmp(gestureName, pressBeganPayload.first.gestureName) == 0)
                {
                    pressBegan = true;
                }
            }

            bool pressEnded = false;
            for (auto const& pressEndedPayload : sharedState.m_internalState.eventPayloads.pressEndedPayloads())
            {
                if (!pressEndedPayload.second.isValid)
                    continue;

                auto& eventStateValue = sharedState.m_internalState.eventStates[pressEndedPayload.first];
                if (eventStateValue.isPressed)
                {
                    eventStateValue.releasePositionNorm = pressEndedPayload.second.releasePositionNorm;
                    eventStateValue.releasePositionPixel = pressEndedPayload.second.releasePositionPixel;

                    eventStateValue.isPressed = false;
                    eventStateValue.isReleasePositionValid = pressEndedPayload.second.isReleasePositionValid;

                    if (std::strcmp(viewportWindowName, pressEndedPayload.first.viewportWindowName) == 0 &&
                        std::strcmp(gestureName, pressEndedPayload.first.gestureName) == 0)
                    {
                        pressEnded = true;
                    }
                }
            }


            // Get event state and set outputs
            auto it = sharedState.m_internalState.eventStates.find({ viewportWindowName, gestureName });
            if (it != sharedState.m_internalState.eventStates.end())
            {
                if (pressEnded)
                {
                    db.outputs.pressed() = kExecutionAttributeStateDisabled;
                    db.outputs.released() = kExecutionAttributeStateEnabled;
                    db.outputs.pressPosition() =
                        db.inputs.useNormalizedCoords() ? it->second.pressPositionNorm : it->second.pressPositionPixel;
                    db.outputs.releasePosition() = db.inputs.useNormalizedCoords() ? it->second.releasePositionNorm :
                                                                                     it->second.releasePositionPixel;
                    db.outputs.isReleasePositionValid() = it->second.isReleasePositionValid;
                }
                else if (pressBegan)
                {
                    db.outputs.pressed() = kExecutionAttributeStateEnabled;
                    db.outputs.released() = kExecutionAttributeStateDisabled;
                    db.outputs.pressPosition() =
                        db.inputs.useNormalizedCoords() ? it->second.pressPositionNorm : it->second.pressPositionPixel;
                    db.outputs.releasePosition() = { 0.0, 0.0 };
                    db.outputs.isReleasePositionValid() = false;
                }
                else
                {
                    db.outputs.pressed() = kExecutionAttributeStateDisabled;
                    db.outputs.released() = kExecutionAttributeStateDisabled;
                }
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // ui
} // graph
} // omni
