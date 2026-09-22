// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ViewportClickNodeCommon.h"

#include <omni/kit/IApp.h>
#include <omni/ui/Workspace.h>

#include <OgnOnViewportClickedDatabase.h>

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnOnViewportClicked
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr clickSub;
        ViewportClickEventPayloads eventPayloads;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    static void initialize(GraphContextObj const&, NodeObj const& nodeObj)
    {
        OgnOnViewportClicked& state = OgnOnViewportClickedDatabase::sSharedState<OgnOnViewportClicked>(nodeObj);

        // Subscribe to click events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.clickSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kClickEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnOnViewportClicked& state =
                            OgnOnViewportClickedDatabase::sSharedState<OgnOnViewportClicked>(nodeObj);
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
        OgnOnViewportClicked& state = OgnOnViewportClickedDatabase::sSharedState<OgnOnViewportClicked>(nodeObj);

        // Unsubscribe from click events
        if (state.m_internalState.clickSub.get())
            state.m_internalState.clickSub.detach()->unsubscribe();
    }

    static bool compute(OgnOnViewportClickedDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        OgnOnViewportClicked& sharedState = db.sharedState<OgnOnViewportClicked>();
        OgnOnViewportClicked& perInstanceState = db.perInstanceState<OgnOnViewportClicked>();
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

            auto const* eventPayloadValuePtr =
                sharedState.m_internalState.eventPayloads.getPayloadValue(viewportWindowName, gestureName);
            if (eventPayloadValuePtr)
            {
                db.outputs.position() = db.inputs.useNormalizedCoords() ? eventPayloadValuePtr->positionNorm :
                                                                          eventPayloadValuePtr->positionPixel;
                db.outputs.clicked() = kExecutionAttributeStateEnabled;
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
} // ui
} // graph
} // omni
