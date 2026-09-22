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

#include <OgnReadViewportPressStateDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnReadViewportPressState
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
                                           //
    // Process event payloads and update event states immediately after receiving each payload
    static void updateEventStates(ViewportPressEventStates& eventStates, ViewportPressEventPayloads& eventPayloads)
    {
        for (auto const& pressBeganPayload : eventPayloads.pressBeganPayloads())
        {
            if (!pressBeganPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[pressBeganPayload.first];

            eventStateValue.pressPositionNorm = pressBeganPayload.second.pressPositionNorm;
            eventStateValue.pressPositionPixel = pressBeganPayload.second.pressPositionPixel;

            eventStateValue.releasePositionNorm = { 0.0, 0.0 };
            eventStateValue.releasePositionPixel = { 0.0, 0.0 };

            eventStateValue.isPressed = true;
            eventStateValue.isReleasePositionValid = false;
        }

        for (auto const& pressEndedPayload : eventPayloads.pressEndedPayloads())
        {
            if (!pressEndedPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[pressEndedPayload.first];
            if (eventStateValue.isPressed)
            {
                eventStateValue.releasePositionNorm = pressEndedPayload.second.releasePositionNorm;
                eventStateValue.releasePositionPixel = pressEndedPayload.second.releasePositionPixel;

                eventStateValue.isPressed = false;
                eventStateValue.isReleasePositionValid = pressEndedPayload.second.isReleasePositionValid;
            }
        }

        eventPayloads.clear();
    }

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnReadViewportPressState& state =
            OgnReadViewportPressStateDatabase::sSharedState<OgnReadViewportPressState>(nodeObj);

        // Subscribe to press events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.pressBeganSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kPressBeganEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportPressState& state =
                            OgnReadViewportPressStateDatabase::sSharedState<OgnReadViewportPressState>(nodeObj);
                        state.m_internalState.eventPayloads.setPressBeganPayload(e->payload);
                        state.m_setStamp.next();

                        updateEventStates(state.m_internalState.eventStates, state.m_internalState.eventPayloads);
                    }
                });
            state.m_internalState.pressEndedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kPressEndedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportPressState& state =
                            OgnReadViewportPressStateDatabase::sSharedState<OgnReadViewportPressState>(nodeObj);
                        state.m_internalState.eventPayloads.setPressEndedPayload(e->payload);
                        state.m_setStamp.next();

                        updateEventStates(state.m_internalState.eventStates, state.m_internalState.eventPayloads);
                    }
                });
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnReadViewportPressState& state =
            OgnReadViewportPressStateDatabase::sSharedState<OgnReadViewportPressState>(nodeObj);

        // Unsubscribe from press events
        if (state.m_internalState.pressBeganSub.get())
            state.m_internalState.pressBeganSub.detach()->unsubscribe();

        if (state.m_internalState.pressEndedSub.get())
            state.m_internalState.pressEndedSub.detach()->unsubscribe();
    }

    static bool compute(OgnReadViewportPressStateDatabase& db)
    {
        OgnReadViewportPressState& sharedState = db.sharedState<OgnReadViewportPressState>();
        OgnReadViewportPressState& perInstanceState = db.perInstanceState<OgnReadViewportPressState>();

        if (perInstanceState.m_syncStamp.makeSync(sharedState.m_setStamp))
        {
            // Get the targeted viewport and gesture
            char const* const viewportWindowName = db.tokenToString(db.inputs.viewport());
            char const* const gestureName = db.tokenToString(db.inputs.gesture());

            if (!omni::ui::Workspace::getWindow(viewportWindowName))
            {
                db.logWarning("Viewport window '%s' not found", viewportWindowName);
            }

            // Output press state
            auto it = sharedState.m_internalState.eventStates.find({ viewportWindowName, gestureName });
            if (it != sharedState.m_internalState.eventStates.end())
            {
                if (db.inputs.useNormalizedCoords())
                {
                    db.outputs.pressPosition() = it->second.pressPositionNorm;
                    db.outputs.releasePosition() = it->second.releasePositionNorm;
                }
                else
                {
                    db.outputs.pressPosition() = it->second.pressPositionPixel;
                    db.outputs.releasePosition() = it->second.releasePositionPixel;
                }
                db.outputs.isReleasePositionValid() = it->second.isReleasePositionValid;
                db.outputs.isPressed() = it->second.isPressed;
                db.outputs.isValid() = true;
            }
            else
            {
                db.outputs.pressPosition() = { 0.0, 0.0 };
                db.outputs.releasePosition() = { 0.0, 0.0 };
                db.outputs.isReleasePositionValid() = false;
                db.outputs.isPressed() = false;
                db.outputs.isValid() = false;
            }
        }
        return true;
    }
};

REGISTER_OGN_NODE()
} // ui
} // graph
} // omni
