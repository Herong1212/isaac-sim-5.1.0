// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnCurveFrameDatabase.h>
#include "omni/math/linalg/vec.h"

#include <carb/Framework.h>
#include <carb/Types.h>

#include <math.h>

using omni::math::linalg::vec3f;

namespace omni
{
namespace graph
{
namespace nodes
{

static vec3f perpendicular(vec3f v)
{
    vec3f av(abs(v[0]), abs(v[1]), abs(v[2]));
    // Find the smallest coordinate of v.
    int axis = (av[0] < av[1] && av[0] < av[2]) ? 0 : ((av[1] < av[2]) ? 1 : 2);
    // Start with that coordinate.
    vec3f p(0.0f);
    p[axis] = 1.0f;
    // Subtract the portion parallel to v.
    p -= (GfDot(p, v) / GfDot(v, v)) * v;
    // Normalize
    return p.GetNormalized();
}

static vec3f rotateLike(vec3f v, vec3f a, vec3f aPlusb)
{
    // To apply to another vector v, the rotation that brings tangent a to tangent b:
    // - reflect v through the line in direction of unit vector a
    // - reflect that through the line in direction of a+b

    vec3f temp = (2 * GfDot(a, v)) * a - v;
    return (2 * GfDot(aPlusb, temp) / GfDot(aPlusb, aPlusb)) * aPlusb - temp;
}

class OgnCurveFrame
{
public:
    static bool compute(OgnCurveFrameDatabase& db)
    {
        const auto& vertexStartIndices = db.inputs.curveVertexStarts();
        const auto& vertexCounts = db.inputs.curveVertexCounts();
        const auto& curvePoints = db.inputs.curvePoints();
        auto& tangentArray = db.outputs.tangent();
        auto& upArray = db.outputs.up();
        auto& outArray = db.outputs.out();

        size_t curveCount = vertexStartIndices.size();
        if (vertexCounts.size() < curveCount)
            curveCount = vertexCounts.size();
        const size_t pointCount = curvePoints.size();

        if (curveCount == 0)
        {
            tangentArray.resize(0);
            upArray.resize(0);
            outArray.resize(0);
            return true;
        }

        tangentArray.resize(pointCount);
        upArray.resize(pointCount);
        outArray.resize(pointCount);

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
                tangentArray[vertex] = vec3f(0.0f, 0.0f, 1.0f);
                upArray[vertex] = vec3f(0.0f, 1.0f, 0.0f);
                outArray[vertex] = vec3f(1.0f, 0.0f, 0.0f);
                continue;
            }

            // First, compute all tangents.

            // The first tangent is the first edge direction.
            // TODO: Skip zero-length edges to get the first real edge direction.
            vec3f prev = curvePoints[vertex];
            vec3f current = curvePoints[vertex + 1];
            vec3f prevDir = (current - prev).GetNormalized();
            tangentArray[vertex] = prevDir;
            for (size_t i = 1; i < vertexCount - 1; ++i)
            {
                vec3f next = curvePoints[vertex + i + 1];
                vec3f nextDir = (next - current).GetNormalized();

                // Middle tangents are averages of previous and next directions.
                vec3f dir = (prevDir + nextDir).GetNormalized();
                tangentArray[vertex + i] = dir;

                prev = current;
                current = next;
                prevDir = nextDir;
            }

            // The last tangent is the last edge direction.
            tangentArray[vertex + vertexCount - 1] = prevDir;

            // Choose the first up vector as anything that's perpendicular to the first tangent.
            // TODO: Use a curve "normal" for more consistency.
            vec3f prevTangent = tangentArray[vertex];
            vec3f prevUpVector = perpendicular(prevTangent);
            // x = cross(y, z)
            vec3f prevOutVector = GfCross(prevUpVector, prevTangent);
            upArray[vertex] = prevUpVector;
            outArray[vertex] = prevOutVector;
            for (size_t i = 1; i < vertexCount; ++i)
            {
                vec3f nextTangent = tangentArray[vertex + i];
                vec3f midTangent = prevTangent + nextTangent;

                vec3f nextUpVector = rotateLike(prevUpVector, prevTangent, midTangent);
                vec3f nextOutVector = rotateLike(prevOutVector, prevTangent, midTangent);

                upArray[vertex + i] = nextUpVector;
                outArray[vertex + i] = nextOutVector;
                prevTangent = nextTangent;
                prevUpVector = nextUpVector;
                prevOutVector = nextOutVector;
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
