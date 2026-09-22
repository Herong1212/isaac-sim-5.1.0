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

#include <OgnOnViewportScrolledDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnOnViewportScrolled
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr scrollSub;
        ViewportScrollEventPayloads eventPayloads;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnOnViewportScrolled& state = OgnOnViewportScrolledDatabase::sSharedState<OgnOnViewportScrolled>(nodeObj);

        // Subscribe to scroll events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.scrollSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kScrollEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportScrolled& state =
                            OgnOnViewportScrolledDatabase::sSharedState<OgnOnViewportScrolled>(nodeObj);
                        state.m_internalState.eventPayloads.clear(); // invalidate previous payloads
                        state.m_internalState.eventPayloads.setPayload(e->payload);
                        state.m_setStamp.next();

                        if (nodeObj.iNode->isValid(nodeObj))
                            nodeObj.iNode->requestCompute(nodeObj);
                    }
                });
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnOnViewportScrolled& state = OgnOnViewportScrolledDatabase::sSharedState<OgnOnViewportScrolled>(nodeObj);

        // Unsubscribe from scroll events
        if (state.m_internalState.scrollSub.get())
            state.m_internalState.scrollSub.detach()->unsubscribe();
    }

    static bool compute(OgnOnViewportScrolledDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        OgnOnViewportScrolled& sharedState = db.sharedState<OgnOnViewportScrolled>();
        OgnOnViewportScrolled& perInstanceState = db.perInstanceState<OgnOnViewportScrolled>();
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

            auto const* eventPayloadValuePtr =
                sharedState.m_internalState.eventPayloads.getPayloadValue(viewportWindowName);
            if (eventPayloadValuePtr)
            {
                db.outputs.scrollValue() = eventPayloadValuePtr->scrollValue;
                db.outputs.position() = db.inputs.useNormalizedCoords() ? eventPayloadValuePtr->positionNorm :
                                                                          eventPayloadValuePtr->positionPixel;
                db.outputs.scrolled() = kExecutionAttributeStateEnabled;
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // ui
} // graph
} // omni
