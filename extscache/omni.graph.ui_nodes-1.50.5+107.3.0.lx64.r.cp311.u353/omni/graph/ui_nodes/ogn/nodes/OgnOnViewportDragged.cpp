// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <OgnOnViewportDraggedDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnOnViewportDragged
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr dragBeganSub;
        carb::events::ISubscriptionPtr dragChangedSub;
        carb::events::ISubscriptionPtr dragEndedSub;
        ViewportDragEventPayloads eventPayloads;
        ViewportDragEventStates eventStates;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnOnViewportDragged& state = OgnOnViewportDraggedDatabase::sSharedState<OgnOnViewportDragged>(nodeObj);

        // Subscribe to drag events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.dragBeganSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kDragBeganEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportDragged& state =
                            OgnOnViewportDraggedDatabase::sSharedState<OgnOnViewportDragged>(nodeObj);
                        state.m_internalState.eventPayloads.clear(); // clear prev payloads when we have a new drag
                        state.m_internalState.eventPayloads.setDragBeganPayload(e->payload);
                        state.m_setStamp.next();

                        if (nodeObj.iNode->isValid(nodeObj))
                            nodeObj.iNode->requestCompute(nodeObj);
                    }
                });
            state.m_internalState.dragChangedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kDragChangedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportDragged& state =
                            OgnOnViewportDraggedDatabase::sSharedState<OgnOnViewportDragged>(nodeObj);
                        state.m_internalState.eventPayloads.setDragChangedPayload(e->payload);
                    }
                });
            state.m_internalState.dragEndedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kDragEndedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportDragged& state =
                            OgnOnViewportDraggedDatabase::sSharedState<OgnOnViewportDragged>(nodeObj);
                        state.m_internalState.eventPayloads.setDragEndedPayload(e->payload);
                        state.m_setStamp.next();

                        if (nodeObj.iNode->isValid(nodeObj))
                            nodeObj.iNode->requestCompute(nodeObj);
                    }
                });
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnOnViewportDragged& state = OgnOnViewportDraggedDatabase::sSharedState<OgnOnViewportDragged>(nodeObj);

        // Unsubscribe from drag events
        if (state.m_internalState.dragBeganSub.get())
            state.m_internalState.dragBeganSub.detach()->unsubscribe();

        if (state.m_internalState.dragChangedSub.get())
            state.m_internalState.dragChangedSub.detach()->unsubscribe();

        if (state.m_internalState.dragEndedSub.get())
            state.m_internalState.dragEndedSub.detach()->unsubscribe();
    }

    static bool compute(OgnOnViewportDraggedDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        OgnOnViewportDragged& sharedState = db.sharedState<OgnOnViewportDragged>();
        OgnOnViewportDragged& perInstanceState = db.perInstanceState<OgnOnViewportDragged>();

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
            bool dragBegan = false;
            for (auto const& dragBeganPayload : sharedState.m_internalState.eventPayloads.dragBeganPayloads())
            {
                if (!dragBeganPayload.second.isValid)
                    continue;

                auto& eventStateValue = sharedState.m_internalState.eventStates[dragBeganPayload.first];
                eventStateValue.isDragInProgress = true;

                eventStateValue.initialPositionNorm = dragBeganPayload.second.initialPositionNorm;
                eventStateValue.initialPositionPixel = dragBeganPayload.second.initialPositionPixel;

                eventStateValue.currentPositionNorm = dragBeganPayload.second.currentPositionNorm;
                eventStateValue.currentPositionPixel = dragBeganPayload.second.currentPositionPixel;

                if (std::strcmp(viewportWindowName, dragBeganPayload.first.viewportWindowName) == 0 &&
                    std::strcmp(gestureName, dragBeganPayload.first.gestureName) == 0)
                {
                    dragBegan = true;
                }
            }

            for (auto const& dragChangedPayload : sharedState.m_internalState.eventPayloads.dragChangedPayloads())
            {
                if (!dragChangedPayload.second.isValid)
                    continue;

                auto& eventStateValue = sharedState.m_internalState.eventStates[dragChangedPayload.first];
                if (eventStateValue.isDragInProgress)
                {
                    eventStateValue.currentPositionNorm = dragChangedPayload.second.currentPositionNorm;
                    eventStateValue.currentPositionPixel = dragChangedPayload.second.currentPositionPixel;
                }
            }

            bool dragEnded = false;
            for (auto const& dragEndedPayload : sharedState.m_internalState.eventPayloads.dragEndedPayloads())
            {
                if (!dragEndedPayload.second.isValid)
                    continue;

                auto& eventStateValue = sharedState.m_internalState.eventStates[dragEndedPayload.first];
                if (eventStateValue.isDragInProgress)
                {
                    eventStateValue.isDragInProgress = false;

                    if (std::strcmp(viewportWindowName, dragEndedPayload.first.viewportWindowName) == 0 &&
                        std::strcmp(gestureName, dragEndedPayload.first.gestureName) == 0)
                    {
                        dragEnded = true;
                    }
                }
            }

            // Get event state and set outputs
            auto it = sharedState.m_internalState.eventStates.find({ viewportWindowName, gestureName });
            if (it != sharedState.m_internalState.eventStates.end())
            {
                if (dragEnded)
                {
                    db.outputs.began() = kExecutionAttributeStateDisabled;
                    db.outputs.ended() = kExecutionAttributeStateEnabled;
                    db.outputs.initialPosition() = db.inputs.useNormalizedCoords() ? it->second.initialPositionNorm :
                                                                                     it->second.initialPositionPixel;
                    db.outputs.finalPosition() = db.inputs.useNormalizedCoords() ? it->second.currentPositionNorm :
                                                                                   it->second.currentPositionPixel;
                }
                else if (dragBegan)
                {
                    db.outputs.began() = kExecutionAttributeStateEnabled;
                    db.outputs.ended() = kExecutionAttributeStateDisabled;
                    db.outputs.initialPosition() = db.inputs.useNormalizedCoords() ? it->second.initialPositionNorm :
                                                                                     it->second.initialPositionPixel;
                    db.outputs.finalPosition() = { 0.0, 0.0 };
                }
                else
                {
                    db.outputs.began() = kExecutionAttributeStateDisabled;
                    db.outputs.ended() = kExecutionAttributeStateDisabled;
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
