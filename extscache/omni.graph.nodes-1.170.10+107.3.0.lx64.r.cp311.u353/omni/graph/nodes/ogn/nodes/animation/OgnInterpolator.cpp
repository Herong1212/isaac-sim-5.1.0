// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnInterpolatorDatabase.h>

namespace omni
{
namespace graph
{
namespace nodes
{

inline float computeInterpolation(size_t numSamples, const float* knots, const float* values, const float& param)
{
    // do really simple search for now
    for (size_t i = 0; i < numSamples - 1; i++)
    {
        float knot = knots[i];
        float knotNext = knots[i + 1];
        float value = values[i];
        float valueNext = values[i + 1];

        if (param < knot)
            return value;

        if (param <= knotNext)
        {
            float interpolant = (param - knot) / (knotNext - knot);
            float interpolatedValue = interpolant * valueNext + (1.0f - interpolant) * value;
            return interpolatedValue;
        }
    }

    return values[numSamples - 1];
}


class OgnInterpolator
{
public:
    static bool compute(OgnInterpolatorDatabase& db)
    {
        const auto& inputKnots = db.inputs.knots();
        const auto& inputValues = db.inputs.values();

        size_t numSamples = inputValues.size();
        if (inputKnots.size() != numSamples)
        {
            db.logWarning(
                "Knots size %zu does not match value size %zu, skipping evaluation", inputKnots.size(), numSamples);
            return false;
        }

        if (numSamples > 0)
        {
            db.outputs.value() =
                computeInterpolation(numSamples, inputKnots.data(), inputValues.data(), db.inputs.param());
        }

        return true;
    }
};

REGISTER_OGN_NODE()

}
}
}
