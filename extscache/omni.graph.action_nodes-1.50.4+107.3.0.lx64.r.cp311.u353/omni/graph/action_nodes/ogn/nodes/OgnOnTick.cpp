// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnOnTickDatabase.h>
#include <omni/graph/action/IActionGraph.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnOnTick
{
public:
    bool m_firstTick{ true };

    static size_t computeVectorized(OgnOnTickDatabase& db, size_t count)
    {
        auto iActionGraph = getInterface();
        const auto& contextObj = db.abi_context();
        const IGraphContext* const iContext = contextObj.iContext;
        bool isPlaying = iContext->getIsPlaying(contextObj);
        auto elapsed = iContext->getElapsedTime(contextObj);

        auto const t = iContext->getTime(contextObj);
        auto const f = iContext->getFrame(contextObj);
        auto const ts = iContext->getTimeSinceStart(contextObj);
        auto const ast = iContext->getAbsoluteSimTime(contextObj);

        auto onlyPlayback = db.inputs.onlyPlayback.vectorized(count);
        auto framePeriod = db.inputs.framePeriod.vectorized(count);

        auto isPlayingOut = db.outputs.isPlaying.vectorized(count);
        auto time = db.outputs.time.vectorized(count);
        auto frame = db.outputs.frame.vectorized(count);
        auto timeSinceStart = db.outputs.timeSinceStart.vectorized(count);
        auto absoluteSimTime = db.outputs.absoluteSimTime.vectorized(count);
        auto deltaSeconds = db.outputs.deltaSeconds.vectorized(count);

        auto accumulatedSeconds = db.state.accumulatedSeconds.vectorized(count);
        auto frameCount = db.state.frameCount.vectorized(count);

        for (size_t idx = 0; idx < count; ++idx)
        {
            if (onlyPlayback[idx] && !isPlaying)
            {
                accumulatedSeconds[idx] = 0;
                frameCount[idx] = 0;
                continue;
            }

            ++frameCount[idx];
            accumulatedSeconds[idx] += elapsed;

            bool doTick = frameCount[idx] > framePeriod[idx];
            auto& localState = db.perInstanceState<OgnOnTick>(idx);
            if (localState.m_firstTick)
            {
                localState.m_firstTick = false;
                doTick = true;
            }

            if (doTick)
            {
                frameCount[idx] = 0;
                deltaSeconds[idx] = accumulatedSeconds[idx];
                accumulatedSeconds[idx] = 0;

                isPlayingOut[idx] = isPlaying;
                time[idx] = t;
                frame[idx] = f;
                timeSinceStart[idx] = ts;
                absoluteSimTime[idx] = ast;
                iActionGraph->setExecutionEnabled(outputs::tick.token(), db.getInstanceIndex() + idx);
            }
        }

        return count;
    }
};

REGISTER_OGN_NODE()
} // action
} // graph
} // omni
