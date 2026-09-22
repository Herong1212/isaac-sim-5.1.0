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

#include <OgnTimelineSetDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{
class OgnTimelineSet
{
public:
    static bool compute(OgnTimelineSetDatabase& db)
    {
        auto handler = [&db](timeline::TimelinePtr const& timeline)
        {
            auto const value = db.inputs.propValue();

            bool clamped = false;

            auto setTime = [&timeline](double desiredTime) -> bool
            {
                auto const startTime = timeline->getStartTime();
                auto const endTime = timeline->getEndTime();
                auto const clampedTime = std::clamp(desiredTime, startTime, endTime);
                timeline->setCurrentTime(clampedTime);
                return clampedTime != desiredTime; // NOLINT(clang-diagnostic-float-equal)
            };

            auto const propName = db.inputs.propName();

            if (propName == OgnTimelineSetDatabase::tokens.Time)
                clamped = setTime(value);
            else if (propName == OgnTimelineSetDatabase::tokens.StartTime)
                timeline->setStartTime(value);
            else if (propName == OgnTimelineSetDatabase::tokens.EndTime)
                timeline->setEndTime(value);
            else if (propName == OgnTimelineSetDatabase::tokens.FramesPerSecond)
                timeline->setTimeCodesPerSecond(value);
            else
            {
                // The property to set is frame-based, convert to time in seconds.
                auto const time = timeline->timeCodeToTime(value);
                if (propName == OgnTimelineSetDatabase::tokens.Frame)
                    clamped = setTime(time);
                else if (propName == OgnTimelineSetDatabase::tokens.StartFrame)
                    timeline->setStartTime(time);
                else if (propName == OgnTimelineSetDatabase::tokens.EndFrame)
                    timeline->setEndTime(time);
            }

            db.outputs.clamped() = clamped;

            return true;
        };

        return timelineNodeExecute(db, handler);
    }
};

REGISTER_OGN_NODE()
}
}
}
