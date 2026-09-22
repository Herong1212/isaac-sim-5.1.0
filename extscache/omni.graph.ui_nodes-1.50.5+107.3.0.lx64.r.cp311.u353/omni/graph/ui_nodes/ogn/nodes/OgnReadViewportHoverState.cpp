// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ViewportHoverNodeCommon.h"

#include <omni/kit/IApp.h>
#include <omni/ui/Workspace.h>

#include <OgnReadViewportHoverStateDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnReadViewportHoverState
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr hoverBeganSub;
        carb::events::ISubscriptionPtr hoverChangedSub;
        carb::events::ISubscriptionPtr hoverEndedSub;
        carb::events::ISubscriptionPtr updateSub;
        ViewportHoverEventPayloads eventPayloads;
        ViewportHoverEventStates eventStates;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    // Process event payloads and update event states every frame
    static void updateEventStates(ViewportHoverEventStates& eventStates, ViewportHoverEventPayloads& eventPayloads)
    {
        for (auto& eventState : eventStates)
        {
            eventState.second.velocityNorm = { 0.0, 0.0 };
            eventState.second.velocityPixel = { 0.0, 0.0 };
        }

        for (auto const& hoverBeganPayload : eventPayloads.hoverBeganPayloads())
        {
            if (!hoverBeganPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[hoverBeganPayload.first];
            eventStateValue.isHovered = true;

            eventStateValue.positionNorm = hoverBeganPayload.second.positionNorm;
            eventStateValue.positionPixel = hoverBeganPayload.second.positionPixel;
            eventStateValue.velocityNorm = { 0.0, 0.0 };
            eventStateValue.velocityPixel = { 0.0, 0.0 };
        }

        for (auto const& hoverChangedPayload : eventPayloads.hoverChangedPayloads())
        {
            if (!hoverChangedPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[hoverChangedPayload.first];
            if (eventStateValue.isHovered)
            {
                eventStateValue.positionNorm = hoverChangedPayload.second.positionNorm;
                eventStateValue.positionPixel = hoverChangedPayload.second.positionPixel;
                eventStateValue.velocityNorm = hoverChangedPayload.second.velocityNorm;
                eventStateValue.velocityPixel = hoverChangedPayload.second.velocityPixel;
            }
        }

        for (auto const& hoverEndedPayload : eventPayloads.hoverEndedPayloads())
        {
            if (!hoverEndedPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[hoverEndedPayload.first];
            if (eventStateValue.isHovered)
            {
                eventStateValue.isHovered = false;

                eventStateValue.positionNorm = { 0.0, 0.0 };
                eventStateValue.positionPixel = { 0.0, 0.0 };
                eventStateValue.velocityNorm = { 0.0, 0.0 };
                eventStateValue.velocityPixel = { 0.0, 0.0 };
            }
        }

        eventPayloads.clear();
    }

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnReadViewportHoverState& state =
            OgnReadViewportHoverStateDatabase::sSharedState<OgnReadViewportHoverState>(nodeObj);

        // Subscribe to hover events and update tick
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.hoverBeganSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kHoverBeganEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportHoverState& state =
                            OgnReadViewportHoverStateDatabase::sSharedState<OgnReadViewportHoverState>(nodeObj);
                        state.m_internalState.eventPayloads.setHoverBeganPayload(e->payload);
                        state.m_setStamp.next();
                    }
                });
            state.m_internalState.hoverChangedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kHoverChangedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportHoverState& state =
                            OgnReadViewportHoverStateDatabase::sSharedState<OgnReadViewportHoverState>(nodeObj);
                        state.m_internalState.eventPayloads.setHoverChangedPayload(e->payload);
                        state.m_setStamp.next();
                    }
                });
            state.m_internalState.hoverEndedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kHoverEndedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportHoverState& state =
                            OgnReadViewportHoverStateDatabase::sSharedState<OgnReadViewportHoverState>(nodeObj);
                        state.m_internalState.eventPayloads.setHoverEndedPayload(e->payload);
                        state.m_setStamp.next();
                    }
                });
            // TODO: Use Events 2.0
            CARB_IGNOREWARNING_MSC_WITH_PUSH(4996)
            state.m_internalState.updateSub = carb::events::createSubscriptionToPush(
                app->getUpdateEventStream(),
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportHoverState& state =
                            OgnReadViewportHoverStateDatabase::sSharedState<OgnReadViewportHoverState>(nodeObj);
                        updateEventStates(state.m_internalState.eventStates, state.m_internalState.eventPayloads);
                        state.m_setStamp.next();
                    }
                });
            CARB_IGNOREWARNING_MSC_POP
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnReadViewportHoverState& state =
            OgnReadViewportHoverStateDatabase::sSharedState<OgnReadViewportHoverState>(nodeObj);

        // Unsubscribe from hover events and update tick
        if (state.m_internalState.hoverBeganSub.get())
            state.m_internalState.hoverBeganSub.detach()->unsubscribe();

        if (state.m_internalState.hoverChangedSub.get())
            state.m_internalState.hoverChangedSub.detach()->unsubscribe();

        if (state.m_internalState.hoverEndedSub.get())
            state.m_internalState.hoverEndedSub.detach()->unsubscribe();

        if (state.m_internalState.updateSub.get())
            state.m_internalState.updateSub.detach()->unsubscribe();
    }

    static bool compute(OgnReadViewportHoverStateDatabase& db)
    {
        OgnReadViewportHoverState& sharedState = db.sharedState<OgnReadViewportHoverState>();
        OgnReadViewportHoverState& perInstanceState = db.perInstanceState<OgnReadViewportHoverState>();

        if (perInstanceState.m_syncStamp.makeSync(sharedState.m_setStamp))
        {
            // Get the targeted viewport
            char const* const viewportWindowName = db.tokenToString(db.inputs.viewport());
            if (!omni::ui::Workspace::getWindow(viewportWindowName))
            {
                db.logWarning("Viewport window '%s' not found", viewportWindowName);
            }

            // Output hover state
            auto it = sharedState.m_internalState.eventStates.find({ viewportWindowName });
            if (it != sharedState.m_internalState.eventStates.end())
            {
                if (db.inputs.useNormalizedCoords())
                {
                    db.outputs.position() = it->second.positionNorm;
                    db.outputs.velocity() = it->second.velocityNorm;
                }
                else
                {
                    db.outputs.position() = it->second.positionPixel;
                    db.outputs.velocity() = it->second.velocityPixel;
                }
                db.outputs.isHovered() = it->second.isHovered;
                db.outputs.isValid() = true;
            }
            else
            {
                db.outputs.position() = { 0.0, 0.0 };
                db.outputs.velocity() = { 0.0, 0.0 };
                db.outputs.isHovered() = false;
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
