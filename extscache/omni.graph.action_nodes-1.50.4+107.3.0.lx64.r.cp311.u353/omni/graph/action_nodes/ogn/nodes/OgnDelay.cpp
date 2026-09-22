// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnDelayDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

namespace
{
constexpr double kUninitializedStartTime = -1.;
}

class OgnDelay
{
    double m_startTime{ kUninitializedStartTime }; // The value of the context time when we started latent state

public:
    static bool compute(OgnDelayDatabase& db)
    {
        auto iActionGraph = getInterface();
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;
        auto& state = db.perInstanceState<OgnDelay>();

        double startTime = state.m_startTime;
        double now = iContext->getTimeSinceStart(contextObj);

        bool start = iActionGraph->getExecutionEnabled(inputs::execIn.token(), db.getInstanceIndex());

        if (!start)
        {
            // We are being polled, check if we have slept long enough
            double duration = db.inputs.duration();
            duration = std::max(duration, 0.);

            if (now - startTime >= duration)
            {
                state.m_startTime = kUninitializedStartTime;
                iActionGraph->endLatentState(db.getInstanceIndex());
                iActionGraph->setExecutionEnabled(outputs::finished.token(), db.getInstanceIndex());
                return true;
            }
        }
        else
        {
            // This is the first entry, start sleeping
            state.m_startTime = now;
            iActionGraph->startLatentState(db.getInstanceIndex());
            return true;
        }
        // still sleeping

        return true;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
