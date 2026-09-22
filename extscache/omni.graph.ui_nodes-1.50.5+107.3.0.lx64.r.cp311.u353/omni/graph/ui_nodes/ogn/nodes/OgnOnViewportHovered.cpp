// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <OgnOnViewportHoveredDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnOnViewportHovered
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr hoverBeganSub;
        carb::events::ISubscriptionPtr hoverEndedSub;
        ViewportHoverEventPayloads eventPayloads;
        ViewportHoverEventStates eventStates;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnOnViewportHovered& state = OgnOnViewportHoveredDatabase::sSharedState<OgnOnViewportHovered>(nodeObj);

        // Subscribe to hover events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.hoverBeganSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kHoverBeganEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportHovered& state =
                            OgnOnViewportHoveredDatabase::sSharedState<OgnOnViewportHovered>(nodeObj);
                        state.m_internalState.eventPayloads.clear();
                        state.m_internalState.eventPayloads.setHoverBeganPayload(e->payload);
                        state.m_setStamp.next();

                        if (nodeObj.iNode->isValid(nodeObj))
                            nodeObj.iNode->requestCompute(nodeObj);
                    }
                });
            state.m_internalState.hoverEndedSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kHoverEndedEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportHovered& state =
                            OgnOnViewportHoveredDatabase::sSharedState<OgnOnViewportHovered>(nodeObj);
                        state.m_internalState.eventPayloads.setHoverEndedPayload(e->payload);
                        state.m_setStamp.next();

                        if (nodeObj.iNode->isValid(nodeObj))
                            nodeObj.iNode->requestCompute(nodeObj);
                    }
                });
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnOnViewportHovered& state = OgnOnViewportHoveredDatabase::sSharedState<OgnOnViewportHovered>(nodeObj);

        // Unsubscribe from hover events
        if (state.m_internalState.hoverBeganSub.get())
            state.m_internalState.hoverBeganSub.detach()->unsubscribe();

        if (state.m_internalState.hoverEndedSub.get())
            state.m_internalState.hoverEndedSub.detach()->unsubscribe();
    }

    static bool compute(OgnOnViewportHoveredDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        OgnOnViewportHovered& sharedState = db.sharedState<OgnOnViewportHovered>();
        OgnOnViewportHovered& perInstanceState = db.perInstanceState<OgnOnViewportHovered>();
        if (perInstanceState.m_syncStamp.makeSync(sharedState.m_setStamp))
        {
            if (sharedState.m_internalState.eventPayloads.empty())
                return true;

            // Get the targeted viewport
            char const* const viewportWindowName = db.tokenToString(db.inputs.viewport());
            if (!omni::ui::Workspace::getWindow(viewportWindowName))
            {
                db.logWarning("Viewport window '%s' not found", viewportWindowName);
            }

            // Process event payloads and update event state
            bool hoverBegan = false;
            for (auto const& hoverBeganPayload : sharedState.m_internalState.eventPayloads.hoverBeganPayloads())
            {
                if (!hoverBeganPayload.second.isValid)
                    continue;

                auto& eventStateValue = sharedState.m_internalState.eventStates[hoverBeganPayload.first];
                eventStateValue.isHovered = true;

                if (std::strcmp(viewportWindowName, hoverBeganPayload.first.viewportWindowName) == 0)
                {
                    hoverBegan = true;
                }
            }

            bool hoverEnded = false;
            for (auto const& hoverEndedPayload : sharedState.m_internalState.eventPayloads.hoverEndedPayloads())
            {
                if (!hoverEndedPayload.second.isValid)
                    continue;

                auto& eventStateValue = sharedState.m_internalState.eventStates[hoverEndedPayload.first];
                if (eventStateValue.isHovered)
                {
                    eventStateValue.isHovered = false;

                    if (std::strcmp(viewportWindowName, hoverEndedPayload.first.viewportWindowName) == 0)
                    {
                        hoverEnded = true;
                    }
                }
            }


            // Get event state and set outputs
            auto it = sharedState.m_internalState.eventStates.find({ viewportWindowName });
            if (it != sharedState.m_internalState.eventStates.end())
            {
                if (hoverEnded)
                {
                    db.outputs.began() = kExecutionAttributeStateDisabled;
                    db.outputs.ended() = kExecutionAttributeStateEnabled;
                }
                else if (hoverBegan)
                {
                    db.outputs.began() = kExecutionAttributeStateEnabled;
                    db.outputs.ended() = kExecutionAttributeStateDisabled;
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
