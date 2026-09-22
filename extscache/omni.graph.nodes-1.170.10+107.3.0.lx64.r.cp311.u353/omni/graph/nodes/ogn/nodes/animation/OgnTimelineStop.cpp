// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "TimelineCommon.h"

#include <omni/timeline/ITimeline.h>

#include <OgnTimelineStopDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnTimelineStop
{
public:
    static bool compute(OgnTimelineStopDatabase& db)
    {
        auto handler = [](timeline::TimelinePtr const& timeline)
        {
            // Pause stops at the current frame, stop resets time
            timeline->pause();
            return true;
        };

        return timelineNodeExecute(db, handler);
    }
};

REGISTER_OGN_NODE()
}
}
}
