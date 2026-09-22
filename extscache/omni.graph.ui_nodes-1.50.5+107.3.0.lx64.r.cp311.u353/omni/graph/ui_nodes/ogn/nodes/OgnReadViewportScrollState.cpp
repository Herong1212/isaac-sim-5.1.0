// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ViewportScrollNodeCommon.h"

#include <omni/kit/IApp.h>
#include <omni/ui/Workspace.h>

#include <OgnReadViewportScrollStateDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnReadViewportScrollState
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr scrollSub;
        ViewportScrollEventPayloads eventPayloads;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        OgnReadViewportScrollState& state =
            OgnReadViewportScrollStateDatabase::sSharedState<OgnReadViewportScrollState>(nodeObj);

        // Subscribe to scroll events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.scrollSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kScrollEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadViewportScrollState& state =
                            OgnReadViewportScrollStateDatabase::sSharedState<OgnReadViewportScrollState>(nodeObj);
                        state.m_internalState.eventPayloads.setPayload(e->payload);
                        state.m_setStamp.next();
                    }
                });
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnReadViewportScrollState& state =
            OgnReadViewportScrollStateDatabase::sSharedState<OgnReadViewportScrollState>(nodeObj);

        // Unsubscribe from scroll events
        if (state.m_internalState.scrollSub.get())
            state.m_internalState.scrollSub.detach()->unsubscribe();
    }

    static bool compute(OgnReadViewportScrollStateDatabase& db)
    {
        OgnReadViewportScrollState& sharedState = db.sharedState<OgnReadViewportScrollState>();
        OgnReadViewportScrollState& perInstanceState = db.perInstanceState<OgnReadViewportScrollState>();
        if (perInstanceState.m_syncStamp.makeSync(sharedState.m_setStamp))
        {
            // Get the targeted viewport and gesture
            char const* const viewportWindowName = db.tokenToString(db.inputs.viewport());
            if (!omni::ui::Workspace::getWindow(viewportWindowName))
            {
                db.logWarning("Viewport window '%s' not found", viewportWindowName);
            }

            auto const* eventPayloadValuePtr =
                sharedState.m_internalState.eventPayloads.getPayloadValue(viewportWindowName);
            if (eventPayloadValuePtr)
            {
                db.outputs.scrollValue() = eventPayloadValuePtr->scrollValue;
                db.outputs.position() = db.inputs.useNormalizedCoords() ? eventPayloadValuePtr->positionNorm :
                                                                          eventPayloadValuePtr->positionPixel;
                db.outputs.isValid() = true;
            }
            else
            {
                db.outputs.scrollValue() = 0.0f;
                db.outputs.position() = { 0.0, 0.0 };
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
