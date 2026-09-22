// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnCreateTubeTopologyDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnCreateTubeTopology
{
public:
    static bool compute(OgnCreateTubeTopologyDatabase& db)
    {
        const auto& inputRows = db.inputs.rows();
        const auto& inputColumns = db.inputs.cols();
        auto& faceVertexCounts = db.outputs.faceVertexCounts();
        auto& faceVertexIndices = db.outputs.faceVertexIndices();

        const size_t rowValueCount = inputRows.size();
        const size_t colValueCount = inputColumns.size();

        size_t inputTubeCount;
        if (colValueCount == 1 || colValueCount == rowValueCount)
        {
            inputTubeCount = rowValueCount;
        }
        else if (rowValueCount == 1)
        {
            inputTubeCount = colValueCount;
        }
        else
        {
            faceVertexCounts.resize(0);
            faceVertexIndices.resize(0);
            return true;
        }

        size_t validTubeCount = 0;
        size_t quadCount = 0;
        for (size_t inputTube = 0; inputTube < inputTubeCount; ++inputTube)
        {
            auto rows = inputRows[(rowValueCount == 1) ? 0 : inputTube];
            auto cols = inputColumns[(colValueCount == 1) ? 0 : inputTube];
            if (rows <= 0 || cols <= 1)
            {
                continue;
            }
            const size_t currentQuadCount = size_t(rows) * cols;
            quadCount += currentQuadCount;
            ++validTubeCount;
        }

        // Generate a faceVertexCounts array with all 4, for all quads.
        faceVertexCounts.resize(quadCount);
        for (auto& faceVertex : faceVertexCounts)
        {
            faceVertex = 4;
        }

        faceVertexIndices.resize(4 * quadCount);
        size_t faceVertexIndex{ 0 };
        int pointIndex = 0;
        for (size_t inputTube = 0; inputTube < inputTubeCount; ++inputTube)
        {
            auto rows = inputRows[(rowValueCount == 1) ? 0 : inputTube];
            auto cols = inputColumns[(colValueCount == 1) ? 0 : inputTube];
            if (rows <= 0 || cols <= 1)
            {
                continue;
            }

            for (auto row = 0; row < rows; ++row)
            {
                // Main quads of the row
                for (auto col = 0; col < cols - 1; ++col)
                {
                    faceVertexIndices[faceVertexIndex++] = pointIndex;
                    faceVertexIndices[faceVertexIndex++] = pointIndex + 1;
                    faceVertexIndices[faceVertexIndex++] = pointIndex + cols + 1;
                    faceVertexIndices[faceVertexIndex++] = pointIndex + cols;
                    ++pointIndex;
                }

                // Wrap around
                faceVertexIndices[faceVertexIndex++] = pointIndex;
                faceVertexIndices[faceVertexIndex++] = pointIndex - cols + 1;
                faceVertexIndices[faceVertexIndex++] = pointIndex + 1;
                faceVertexIndices[faceVertexIndex++] = pointIndex + cols;
                ++pointIndex;
            }

            pointIndex += cols;
        }

        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
