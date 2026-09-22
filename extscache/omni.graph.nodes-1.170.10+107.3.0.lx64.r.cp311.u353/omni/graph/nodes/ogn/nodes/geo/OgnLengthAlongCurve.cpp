// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnLengthAlongCurveDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnLengthAlongCurve
{
public:
    static bool compute(OgnLengthAlongCurveDatabase& db)
    {
        const auto& vertexStartIndices = db.inputs.curveVertexStarts();
        const auto& vertexCounts = db.inputs.curveVertexCounts();
        const auto& curvePoints = db.inputs.curvePoints();
        const auto& normalize = db.inputs.normalize();
        auto& lengthArray = db.outputs.length();

        size_t curveCount = std::min(vertexStartIndices.size(), vertexCounts.size());
        const size_t pointCount = curvePoints.size();

        if (curveCount == 0)
        {
            lengthArray.resize(0);
            return true;
        }

        lengthArray.resize(pointCount);

        for (size_t curve = 0; curve < curveCount; ++curve)
        {
            if (vertexCounts[curve] <= 0)
                continue;

            const size_t vertex = vertexStartIndices[curve];
            if (vertex >= pointCount)
                break;

            size_t vertexCount = size_t(vertexCounts[curve]);

            // Limit the vertex count on this curve if it goes past the end of the points array.
            if (vertexCount > pointCount - vertex)
            {
                vertexCount = pointCount - vertex;
            }

            if (vertexCount == 1)
            {
                // Only one vertex: predetermined frame.
                lengthArray[vertex] = 0.0f;
                continue;
            }

            // First, compute all lengths along the curve.
            auto prev = curvePoints[vertex];
            lengthArray[vertex] = 0.0f;
            // Sum in double precision to avoid catastrophic roundoff error.
            double lengthSum = 0.0;
            for (size_t i = 1; i < vertexCount; ++i)
            {
                auto& current = curvePoints[vertex + i];
                auto edge = (current - prev);
                lengthSum += edge.GetLength();
                lengthArray[vertex + i] = float(lengthSum);
                prev = current;
            }

            // Don't normalize if lengthSum is zero.
            if (normalize && float(lengthSum) != 0)
            {
                for (size_t i = 0; i < vertexCount; ++i)
                {
                    lengthArray[vertex + i] /= float(lengthSum);
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
