// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ViewportDragNodeCommon.h"

#include <omni/kit/IApp.h>
#include <omni/ui/Workspace.h>

#include <OgnReadViewportDragStateDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnReadViewportDragState
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr dragBeganSub;
        carb::events::ISubscriptionPtr dragChangedSub;
        carb::events::ISubscriptionPtr dragEndedSub;
        carb::events::ISubscriptionPtr updateSub;
        ViewportDragEventPayloads eventPayloads;
        ViewportDragEventStates eventStates;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    // Process event payloads and update event states every frame
    static void updateEventStates(ViewportDragEventStates& eventStates, ViewportDragEventPayloads& eventPayloads)
    {
        for (auto& eventState : eventStates)
        {
            eventState.second.velocityNorm = { 0.0, 0.0 };
            eventState.second.velocityPixel = { 0.0, 0.0 };
        }

        for (auto const& dragBeganPayload : eventPayloads.dragBeganPayloads())
        {
            if (!dragBeganPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[dragBeganPayload.first];
            eventStateValue.isDragInProgress = true;

            eventStateValue.initialPositionNorm = dragBeganPayload.second.initialPositionNorm;
            eventStateValue.initialPositionPixel = dragBeganPayload.second.initialPositionPixel;

            eventStateValue.currentPositionNorm = dragBeganPayload.second.currentPositionNorm;
            eventStateValue.currentPositionPixel = dragBeganPayload.second.currentPositionPixel;

            eventStateValue.velocityNorm = dragBeganPayload.second.velocityNorm;
            eventStateValue.velocityPixel = dragBeganPayload.second.velocityPixel;
        }

        for (auto const& dragChangedPayload : eventPayloads.dragChangedPayloads())
        {
            if (!dragChangedPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[dragChangedPayload.first];
            if (eventStateValue.isDragInProgress)
            {
                eventStateValue.currentPositionNorm = dragChangedPayload.second.currentPositionNorm;
                eventStateValue.currentPositionPixel = dragChangedPayload.second.currentPositionPixel;

                eventStateValue.velocityNorm = dragChangedPayload.second.velocityNorm;
                eventStateValue.velocityPixel = dragChangedPayload.second.velocityPixel;
            }
        }

        for (auto const& dragEndedPayload : eventPayloads.dragEndedPayloads())
        {
            if (!dragEndedPayload.second.isValid)
                continue;

            auto& eventStateValue = eventStates[dragEndedPayload.first];
            if (eventStateValue.isDragInProgress)
            {
                eventStateValue.isDragInProgress = false;
                eventStateValue.velocityNorm = { 0.0, 0.0 };
                eventStateValue.velocityPixel = { 0.0, 0.0 };
            }
        }

        eventPayloads.clear();
    }

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnReadViewportDragState& state =
            OgnReadViewportDragStateDatabase::sSharedState<OgnReadViewportDragState>(nodeObj);

        // Subscribe to drag events and update tick
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.dragBeganSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kDragBeganEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportDragState& state =
                            OgnReadViewportDragStateDatabase::sSharedState<OgnReadViewportDragState>(nodeObj);
                        state.m_internalState.eventPayloads.setDragBeganPayload(e->payload);
                        state.m_setStamp.next();
                    }
                });
            state.m_internalState.dragChangedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kDragChangedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportDragState& state =
                            OgnReadViewportDragStateDatabase::sSharedState<OgnReadViewportDragState>(nodeObj);
                        state.m_internalState.eventPayloads.setDragChangedPayload(e->payload);
                        state.m_setStamp.next();
                    }
                });
            state.m_internalState.dragEndedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kDragEndedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportDragState& state =
                            OgnReadViewportDragStateDatabase::sSharedState<OgnReadViewportDragState>(nodeObj);
                        state.m_internalState.eventPayloads.setDragEndedPayload(e->payload);
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
                        OgnReadViewportDragState& state =
                            OgnReadViewportDragStateDatabase::sSharedState<OgnReadViewportDragState>(nodeObj);
                        updateEventStates(state.m_internalState.eventStates, state.m_internalState.eventPayloads);
                        state.m_setStamp.next();
                    }
                });
            CARB_IGNOREWARNING_MSC_POP
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnReadViewportDragState& state =
            OgnReadViewportDragStateDatabase::sSharedState<OgnReadViewportDragState>(nodeObj);

        // Unsubscribe from drag events and update tick
        if (state.m_internalState.dragBeganSub.get())
            state.m_internalState.dragBeganSub.detach()->unsubscribe();

        if (state.m_internalState.dragChangedSub.get())
            state.m_internalState.dragChangedSub.detach()->unsubscribe();

        if (state.m_internalState.dragEndedSub.get())
            state.m_internalState.dragEndedSub.detach()->unsubscribe();

        if (state.m_internalState.updateSub.get())
            state.m_internalState.updateSub.detach()->unsubscribe();
    }

    static bool compute(OgnReadViewportDragStateDatabase& db)
    {
        OgnReadViewportDragState& sharedState = db.sharedState<OgnReadViewportDragState>();
        OgnReadViewportDragState& perInstanceState = db.perInstanceState<OgnReadViewportDragState>();

        if (perInstanceState.m_syncStamp.makeSync(sharedState.m_setStamp))
        {
            // Get the targeted viewport and gesture
            char const* const viewportWindowName = db.tokenToString(db.inputs.viewport());
            char const* const gestureName = db.tokenToString(db.inputs.gesture());

            if (!omni::ui::Workspace::getWindow(viewportWindowName))
            {
                db.logWarning("Viewport window '%s' not found", viewportWindowName);
            }

            // Output drag state
            auto it = sharedState.m_internalState.eventStates.find({ viewportWindowName, gestureName });
            if (it != sharedState.m_internalState.eventStates.end())
            {
                if (db.inputs.useNormalizedCoords())
                {
                    db.outputs.initialPosition() = it->second.initialPositionNorm;
                    db.outputs.currentPosition() = it->second.currentPositionNorm;
                    db.outputs.velocity() = it->second.velocityNorm;
                }
                else
                {
                    db.outputs.initialPosition() = it->second.initialPositionPixel;
                    db.outputs.currentPosition() = it->second.currentPositionPixel;
                    db.outputs.velocity() = it->second.velocityPixel;
                }
                db.outputs.isDragInProgress() = it->second.isDragInProgress;
                db.outputs.isValid() = true;
            }
            else
            {
                db.outputs.initialPosition() = { 0.0, 0.0 };
                db.outputs.currentPosition() = { 0.0, 0.0 };
                db.outputs.velocity() = { 0.0, 0.0 };
                db.outputs.isDragInProgress() = false;
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
