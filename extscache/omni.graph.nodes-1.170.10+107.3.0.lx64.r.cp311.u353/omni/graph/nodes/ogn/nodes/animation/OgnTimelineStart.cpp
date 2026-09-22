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

#include <OgnTimelineStartDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnTimelineStart
{
public:
    static bool compute(OgnTimelineStartDatabase& db)
    {
        auto handler = [](timeline::TimelinePtr const& timeline)
        {
            timeline->play();
            return true;
        };

        return timelineNodeExecute(db, handler);
    }
};

REGISTER_OGN_NODE()
}
}
}
