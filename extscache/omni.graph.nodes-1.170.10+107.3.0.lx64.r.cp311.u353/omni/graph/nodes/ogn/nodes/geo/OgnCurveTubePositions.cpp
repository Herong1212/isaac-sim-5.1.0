// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnCurveTubePositionsDatabase.h>
#include <carb/Framework.h>
#include <carb/Types.h>
#include <vector>

#define _USE_MATH_DEFINES
#include <math.h>

using carb::Float2;
using carb::Float3;

namespace omni
{
namespace graph
{
namespace nodes
{

static void computeNewCircle(std::vector<Float2>& circle, size_t edgeCount)
{
    if (circle.size() == edgeCount)
        return;

    circle.resize(edgeCount);
    circle[0] = Float2{ 1.0f, 0.0f };
    for (size_t i = 1; i < edgeCount; ++i)
    {
        double theta = ((2 * M_PI) / double(edgeCount)) * double(i);
        float c = float(cos(theta));
        float s = float(sin(theta));
        circle[i] = Float2{ c, s };
    }
}

class OgnCurveTubePositions
{
public:
    static bool compute(OgnCurveTubePositionsDatabase& db)
    {
        const auto& curveStartIndices = db.inputs.curveVertexStarts();
        const auto& tubeVertexCounts = db.inputs.curveVertexCounts();
        const auto& curvePointsArray = db.inputs.curvePoints();
        const auto& tubeStartIndices = db.inputs.tubePointStarts();
        const auto& columnsArray = db.inputs.cols();
        const auto& widthArray = db.inputs.width();
        const auto& upArray = db.inputs.up();
        const auto& outArray = db.inputs.out();
        auto& pointsArray = db.outputs.points();

        size_t curveCount = curveStartIndices.size();
        if (tubeVertexCounts.size() < curveCount)
            curveCount = tubeVertexCounts.size();
        size_t tubeCount = tubeStartIndices.size();
        const size_t colValueCount = columnsArray.size();
        const int32_t tubePointsCount = (tubeCount == 0) ? 0 : tubeStartIndices[tubeCount - 1];
        if (tubeCount != 0)
            --tubeCount;

        const size_t curvePointCount = curvePointsArray.size();
        const size_t upCount = upArray.size();
        const size_t outCount = outArray.size();
        const size_t widthCount = widthArray.size();
        size_t curvePointsCount = curvePointCount;
        if (upCount != 1 && upCount < curvePointsCount)
            curvePointsCount = upCount;
        if (outCount != 1 && outCount < curvePointsCount)
            curvePointsCount = outCount;
        if (widthCount != 1 && widthCount < curvePointsCount)
            curvePointsCount = widthCount;

        if (tubePointsCount <= 0 || tubeCount == 0 || (colValueCount != 1 && colValueCount != tubeCount) ||
            (colValueCount == 1 && columnsArray[0] <= 0) || (tubeCount != curveCount))
        {
            pointsArray.resize(0);
            return true;
        }

        if (curvePointsCount == 0)
        {
            pointsArray.resize(0);
            return true;
        }

        std::vector<Float2> circle;
        size_t circleN = 0;
        if (colValueCount == 1)
        {
            circleN = columnsArray[0];
            computeNewCircle(circle, circleN);
        }

        pointsArray.resize(tubePointsCount);

        for (size_t tube = 0; tube < tubeCount; ++tube)
        {
            if (tubeStartIndices[tube] < 0 || curveStartIndices[tube] < 0 || tubeVertexCounts[tube] < 0)
                continue;

            size_t tubeStartIndex = tubeStartIndices[tube];
            size_t tubeEndIndex = tubeStartIndices[tube + 1];
            size_t curveStartIndex = curveStartIndices[tube];
            size_t curveEndIndex = curveStartIndex + tubeVertexCounts[tube];

            if (colValueCount != 1)
            {
                circleN = columnsArray[tube];
                if (circleN <= 0)
                    continue;
                computeNewCircle(circle, circleN);
            }

            if ((int32_t)tubeEndIndex > tubePointsCount || tubeEndIndex < tubeStartIndex)
                break;
            if (tubeEndIndex == tubeStartIndex)
                continue;

            size_t curvePointCount = curveEndIndex - curveStartIndex;
            size_t tubePointCount = tubeEndIndex - tubeStartIndex;
            if (curvePointCount * circleN != tubePointCount)
            {
                continue;
            }

            size_t circleIndex = 0;
            // Do bounds check on up and out arrays.
            auto center = curvePointsArray[curveStartIndex];
            auto up = upArray[(upCount == 1) ? 0 : curveStartIndex];
            auto out = outArray[(outCount == 1) ? 0 : curveStartIndex];
            float width = 0.5f * widthArray[(widthCount == 1) ? 0 : curveStartIndex];
            for (size_t point = tubeStartIndex; point < tubeEndIndex; ++point)
            {
                float x = width * circle[circleIndex].x;
                float y = width * circle[circleIndex].y;

                auto newPoint = (center + (x * out + y * up));
                pointsArray[point] = newPoint;

                ++circleIndex;
                if (circleIndex >= circleN)
                {
                    circleIndex = 0;
                    ++curveStartIndex;
                    if (curveStartIndex < curveEndIndex)
                    {
                        center = curvePointsArray[curveStartIndex];
                        up = upArray[(upCount == 1) ? 0 : curveStartIndex];
                        out = outArray[(outCount == 1) ? 0 : curveStartIndex];
                        width = 0.5f * widthArray[(widthCount == 1) ? 0 : curveStartIndex];
                    }
                }
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
