// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "PrimCommon.h"
#include <OgnTimerDatabase.h>

using namespace pxr;
using DB = OgnTimerDatabase;

namespace omni::graph::nodes
{

namespace
{
constexpr double kUninitializedStartTime = -1.;
}

enum TimeState : uint32_t
{
    kTimeStateInit,
    kTimeStateStart,
    kTimeStatePlay,
    kTimeStateLast,
    kTimeStateFinish
};

class OgnTimer
{
    double m_startTime{ kUninitializedStartTime }; // The value of the context time when we started latent state
    TimeState m_timeState{ kTimeStateInit };

public:
    static bool compute(DB& db)
    {
        const auto& contextObj = db.abi_context();
        auto iContext = contextObj.iContext;
        double now = iContext->getTimeSinceStart(contextObj);

        auto& state = db.perInstanceState<OgnTimer>();
        auto& timeState = state.m_timeState;
        auto& startTime = state.m_startTime;

        const double duration = std::max(db.inputs.duration(), 1.0e-6);
        const double startValue = db.inputs.startValue();
        const double endValue = db.inputs.endValue();

        switch (timeState)
        {
        case kTimeStateInit:
        {
            timeState = kTimeStateStart;
            db.outputs.finished() = kExecutionAttributeStateLatentPush;
            break;
        }
        case kTimeStateStart:
        {
            startTime = now;
            timeState = kTimeStatePlay;
            // Do not break here, we want to fall through to the next case
        }
        case kTimeStatePlay:
        {
            double deltaTime = now - startTime;
            double value = startValue + (endValue - startValue) * deltaTime / duration;
            value = std::min(value, 1.0);

            db.outputs.value() = value;

            if (deltaTime >= duration)
            {
                timeState = kTimeStateLast;
            }
            else
            {
                db.outputs.updated() = kExecutionAttributeStateEnabled;
            }
            break;
        }
        case kTimeStateLast:
        {
            timeState = kTimeStateFinish;
            db.outputs.value() = endValue;
            db.outputs.updated() = kExecutionAttributeStateEnabled;
            break;
        }
        case kTimeStateFinish:
        {
            startTime = kUninitializedStartTime;
            timeState = kTimeStateInit;
            db.outputs.finished() = kExecutionAttributeStateLatentFinish;
            break;
        }
        }
        return true;
    }
};
REGISTER_OGN_NODE()
}
