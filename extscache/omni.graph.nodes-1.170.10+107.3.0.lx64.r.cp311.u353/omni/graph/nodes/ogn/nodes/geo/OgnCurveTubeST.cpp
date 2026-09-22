// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnCurveTubeSTDatabase.h>
#include "omni/math/linalg/vec.h"

#include <carb/Framework.h>
#include <carb/Types.h>

#include <omni/graph/core/ArrayWrapper.h>
#include <omni/graph/core/NodeTypeRegistrar.h>
#include <omni/graph/core/iComputeGraph.h>

#include <vector>

#define _USE_MATH_DEFINES
#include <math.h>

using omni::math::linalg::vec2f;

namespace omni
{
namespace graph
{
namespace nodes
{

static void computeNewSs(std::vector<float>& sValues, size_t edgeCount)
{
    if (sValues.size() == edgeCount + 1)
        return;

    sValues.resize(edgeCount + 1);

    sValues[0] = 0.0f;

    if (edgeCount == 0)
        return;

    for (size_t i = 1; i < edgeCount; ++i)
    {
        sValues[i] = float(double(i) / double(edgeCount));
    }

    sValues[edgeCount] = 1.0f;
}

class OgnCurveTubeST
{
public:
    static bool compute(OgnCurveTubeSTDatabase& db)
    {
        const auto& curveStartIndices = db.inputs.curveVertexStarts();
        const auto& tubeVertexCounts = db.inputs.curveVertexCounts();
        const auto& tubeSTStartArray = db.inputs.tubeSTStarts();
        const auto& tubeQuadStartArray = db.inputs.tubeQuadStarts();
        const auto& columnsArray = db.inputs.cols();
        const auto& widthArray = db.inputs.width();
        const auto& tArray = db.inputs.t();
        auto scaleTLikeS = db.inputs.scaleTLikeS(); // Might change, so get a copy
        auto& stArray = db.outputs.primvars_st();
        auto& stIndicesArray = db.outputs.primvars_st_indices();

        size_t curveCount = curveStartIndices.size();
        if (tubeVertexCounts.size() < curveCount)
            curveCount = tubeVertexCounts.size();
        size_t tubeCount = tubeSTStartArray.size();
        if (tubeQuadStartArray.size() < tubeCount)
        {
            tubeCount = tubeQuadStartArray.size();
        }
        const size_t colValueCount = columnsArray.size();
        const int32_t tubeSTsCount = (tubeCount == 0) ? 0 : tubeSTStartArray[tubeCount - 1];
        const int32_t tubeQuadsCount = (tubeCount == 0) ? 0 : tubeQuadStartArray[tubeCount - 1];
        if (tubeCount != 0)
            --tubeCount;

        const size_t tCount = tArray.size();

        size_t widthCount = 0;
        if (scaleTLikeS)
        {
            widthCount = widthArray.size();
            if (widthCount == 0 || (widthCount != 1 && widthCount != tCount && widthCount != tubeCount))
            {
                scaleTLikeS = false;
            }
        }

        if (tubeSTsCount <= 0 || tubeCount == 0 || (colValueCount != 1 && colValueCount != tubeCount) ||
            (colValueCount == 1 && columnsArray[0] <= 0) || (tubeCount != curveCount))
        {
            stArray.resize(0);
            stIndicesArray.resize(0);
            return true;
        }

        if (tCount == 0)
        {
            stArray.resize(0);
            stIndicesArray.resize(0);
            return true;
        }

        std::vector<float> sValues;
        size_t circleN = 0;
        float perimeterScale = 0.0f;
        if (colValueCount == 1)
        {
            circleN = columnsArray[0];
            computeNewSs(sValues, circleN);
            perimeterScale = float(circleN * sin(M_PI / circleN));
        }

        stArray.resize(tubeSTsCount);
        stIndicesArray.resize(4 * tubeQuadsCount);

        float width = (scaleTLikeS ? widthArray[0] : 0.0f);

        for (size_t tube = 0; tube < tubeCount; ++tube)
        {
            if (tubeSTStartArray[tube] < 0 || curveStartIndices[tube] < 0 || tubeQuadStartArray[tube] < 0 ||
                tubeVertexCounts[tube] < 0)
                continue;

            size_t tubeSTStartIndex = tubeSTStartArray[tube];
            size_t tubeSTEndIndex = tubeSTStartArray[tube + 1];
            size_t tubeQuadStartIndex = 4 * tubeQuadStartArray[tube];
            size_t tubeQuadEndIndex = 4 * tubeQuadStartArray[tube + 1];
            size_t curveStartIndex = curveStartIndices[tube];
            size_t curveEndIndex = curveStartIndex + tubeVertexCounts[tube];

            if (colValueCount != 1)
            {
                circleN = columnsArray[tube];
                if (circleN <= 0)
                    continue;
                computeNewSs(sValues, circleN);
                perimeterScale = float(circleN * sin(M_PI / circleN));
            }

            if ((int32_t)tubeSTEndIndex > tubeSTsCount || tubeSTEndIndex < tubeSTStartIndex)
                break;
            if (tubeSTEndIndex == tubeSTStartIndex)
                continue;

            size_t curveTCount = curveEndIndex - curveStartIndex;
            size_t tubeSTCount = tubeSTEndIndex - tubeSTStartIndex;
            if (curveTCount * (circleN + 1) != tubeSTCount)
            {
                continue;
            }

            if (scaleTLikeS)
            {
                if (widthCount == tubeCount)
                {
                    width = widthArray[tube];
                }
                else if (widthCount == tCount)
                {
                    // Use the max width along the curve for the whole curve's
                    // t scaling, just for stability for now.
                    // Some situations need varying scale, but that's more complicated,
                    // and not what's needed for the current use cases.
                    width = widthArray[curveStartIndex];
                    for (size_t i = curveStartIndex + 1; i < curveEndIndex; ++i)
                    {
                        if (widthArray[i] > width)
                        {
                            width = widthArray[i];
                        }
                    }
                }
            }

            // First, compute the st values.
            size_t circleIndex = 0;
            float tScale = 1.0f;
            if (scaleTLikeS)
            {
                // Scale t by 1/(2nr*sin(2pi/2n)), where 2r*sin(2pi/2n) is the side length,
                // and the full denominator is the perimeter of the tube's circle.
                // This is, in a sense, scaling t by the same factor that s was "scaled"
                // by, to make it go from 0 to 1, instead of 0 to the perimeter.
                // This way, t will change proportionally to s moving along the surface in 3D space.
                tScale = 1.0f / (width * perimeterScale);
            }
            float tValue = tScale * tArray[curveStartIndex];
            for (size_t sti = tubeSTStartIndex; sti < tubeSTEndIndex; ++sti)
            {
                vec2f st(sValues[circleIndex], tValue);

                stArray[sti] = st;

                ++circleIndex;
                if (circleIndex >= circleN + 1)
                {
                    circleIndex = 0;
                    ++curveStartIndex;
                    if (curveStartIndex < curveEndIndex)
                    {
                        tValue = tScale * tArray[curveStartIndex];
                    }
                }
            }

            // Second, compute indices into the st values.
            circleIndex = 0;
            for (size_t indexi = tubeQuadStartIndex, sti = tubeSTStartIndex; indexi < tubeQuadEndIndex; indexi += 4, ++sti)
            {
                stIndicesArray[indexi] = int32_t(sti);
                stIndicesArray[indexi + 1] = int32_t(sti + 1);
                stIndicesArray[indexi + 2] = int32_t(sti + circleN + 1 + 1);
                stIndicesArray[indexi + 3] = int32_t(sti + circleN + 1);

                ++circleIndex;
                if (circleIndex >= circleN)
                {
                    circleIndex = 0;
                    ++sti;
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
