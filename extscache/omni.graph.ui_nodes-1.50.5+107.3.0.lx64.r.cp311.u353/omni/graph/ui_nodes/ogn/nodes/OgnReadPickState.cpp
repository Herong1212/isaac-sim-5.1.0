// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include <OgnReadPickStateDatabase.h>

#include "PickingNodeCommon.h"

#include <omni/kit/IApp.h>
#include <omni/ui/Workspace.h>

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/common.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/relationship.h>
#include <pxr/usd/usdUtils/stageCache.h>
#include <omni/graph/core/PostUsdInclude.h>
// clang-format on

namespace omni
{
namespace graph
{
namespace ui_nodes
{
class OgnReadPickState
{
public:
    struct InternalState
    {
        carb::events::ISubscriptionPtr pickingSub;
        PickingEventPayloads eventPayloads;
    } m_internalState;
    exec::unstable::Stamp m_setStamp; // stamp set when the event occurs
    exec::unstable::SyncStamp m_syncStamp; // stamp set by each instance

    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        OgnReadPickState& state = OgnReadPickStateDatabase::sSharedState<OgnReadPickState>(nodeObj);

        // Subscribe to picking events
        if (omni::kit::IApp* app = carb::getCachedInterface<omni::kit::IApp>())
        {
            state.m_internalState.pickingSub = carb::events::createSubscriptionToPushByType(
                app->getMessageBusEventStream(), kPickingEventType,
                [nodeObj](carb::events::IEvent* e)
                {
                    if (e)
                    {
                        OgnReadPickState& state = OgnReadPickStateDatabase::sSharedState<OgnReadPickState>(nodeObj);
                        state.m_internalState.eventPayloads.setPayload(e->payload);
                        state.m_setStamp.next();
                    }
                });
        }
    }

    static void release(const NodeObj& nodeObj)
    {
        OgnReadPickState& state = OgnReadPickStateDatabase::sSharedState<OgnReadPickState>(nodeObj);

        // Unsubscribe from picking events
        if (state.m_internalState.pickingSub.get())
            state.m_internalState.pickingSub.detach()->unsubscribe();
    }

    static bool compute(OgnReadPickStateDatabase& db)
    {
        OgnReadPickState& sharedState = db.sharedState<OgnReadPickState>();
        OgnReadPickState& perInstanceState = db.perInstanceState<OgnReadPickState>();

        if (perInstanceState.m_syncStamp.makeSync(sharedState.m_setStamp))
        {
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
                // Get the picked path and pos for the targeted viewport and gesture
                char const* const pickedPrimPath = eventPayloadValuePtr->pickedPrimPath;
                pxr::GfVec3d const& pickedWorldPos = eventPayloadValuePtr->pickedWorldPos;

                // Determine if a tracked prim is picked
                bool isTrackedPrimPicked;

                // First determine if any prim is picked
                bool const isAnyPrimPicked = pickedPrimPath && pickedPrimPath[0] != '\0';
                if (isAnyPrimPicked)
                {
                    TargetPath pickedPrim = db.stringToPath(pickedPrimPath);

                    // If any prim is picked, determine if the picked prim is tracked
                    if (db.inputs.usePaths())
                    {
                        // Get the list of tracked prims from the path[] input
                        auto& trackedPrimPaths = db.inputs.trackedPrimPaths();

                        // If no tracked prims are specified then we consider all prims to be tracked
                        // Else search the list of tracked prims for the picked prim
                        if (trackedPrimPaths.empty())
                            isTrackedPrimPicked = true;
                        else
                            isTrackedPrimPicked =
                                std::any_of(trackedPrimPaths.begin(), trackedPrimPaths.end(),
                                            [&db, pickedPrimPath](NameToken const& path)
                                            { return (std::strcmp(db.tokenToString(path), pickedPrimPath) == 0); });
                    }
                    else
                    {
                        // Get the list of tracked prims
                        const auto& trackedPrims = db.inputs.trackedPrims();

                        // If no tracked prims are specified then we consider all prims to be tracked
                        // Else search the list of tracked prims for the picked prim
                        if (trackedPrims.empty())
                            isTrackedPrimPicked = true;
                        else
                            isTrackedPrimPicked = std::any_of(trackedPrims.begin(), trackedPrims.end(),
                                                              [pickedPrim](TargetPath const& trackedPrim)
                                                              { return (trackedPrim == pickedPrim); });
                    }

                    db.outputs.pickedPrim().resize(1);
                    db.outputs.pickedPrim()[0] = pickedPrim;
                    db.outputs.pickedPrimPath() = db.stringToToken(pickedPrimPath);
                }
                else
                {
                    // No prim is picked at all, so a tracked prim certainly isn't picked
                    isTrackedPrimPicked = false;
                    db.outputs.pickedPrim().resize(0);
                    db.outputs.pickedPrimPath() = Token();
                }

                // Set outputs
                db.outputs.pickedWorldPos() = pickedWorldPos;
                db.outputs.isTrackedPrimPicked() = isTrackedPrimPicked;
                db.outputs.isValid() = true;
            }
            else
            {
                db.outputs.pickedPrim().resize(0);
                db.outputs.pickedPrimPath() = Token();
                db.outputs.pickedWorldPos() = { 0, 0, 0 };
                db.outputs.isTrackedPrimPicked() = false;
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
