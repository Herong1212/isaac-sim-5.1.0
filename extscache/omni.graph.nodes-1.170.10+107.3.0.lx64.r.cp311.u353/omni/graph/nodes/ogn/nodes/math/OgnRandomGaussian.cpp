// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "OgnRandomGaussianDatabase.h"
#include "random/RandomNodeBase.h"

#include <omni/graph/core/ogn/ComputeHelpers.h>

namespace omni
{
namespace graph
{
namespace nodes
{
using namespace random;

class OgnRandomGaussian : public NodeBase<OgnRandomGaussian, OgnRandomGaussianDatabase>
{
    template <typename T>
    static bool tryComputeAssumingType(OgnRandomGaussianDatabase& db, size_t count)
    {
        if (db.inputs.useLog())
        {
            return ogn::compute::tryComputeWithArrayBroadcasting<T>(
                db.state.gen(), db.inputs.mean(), db.inputs.stdev(), db.outputs.random(),
                [](GenBuffer_t const& genBuffer, T const& mean, T const& stdev, T& result)
                {
                    // Generate next random
                    result = asGenerator(genBuffer).nextLogNormal(mean, stdev);
                },
                count);
        }

        return ogn::compute::tryComputeWithArrayBroadcasting<T>(
            db.state.gen(), db.inputs.mean(), db.inputs.stdev(), db.outputs.random(),
            [](GenBuffer_t const& genBuffer, T const& mean, T const& stdev, T& result)
            {
                // Generate next random
                result = asGenerator(genBuffer).nextNormal(mean, stdev);
            },
            count);
    }

    template <typename T, size_t N>
    static bool tryComputeAssumingType(OgnRandomGaussianDatabase& db, size_t count)
    {
        if (db.inputs.useLog())
        {
            return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(
                db.state.gen(), db.inputs.mean(), db.inputs.stdev(), db.outputs.random(),
                [](GenBuffer_t const& genBuffer, T const& mean, T const& stdev, T& result)
                {
                    // Generate next random
                    result = asGenerator(genBuffer).nextLogNormal(mean, stdev);
                },
                count);
        }

        return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(
            db.state.gen(), db.inputs.mean(), db.inputs.stdev(), db.outputs.random(),
            [](GenBuffer_t const& genBuffer, T const& mean, T const& stdev, T& result)
            {
                // Generate next random
                result = asGenerator(genBuffer).nextNormal(mean, stdev);
            },
            count);
    }

    static bool defaultCompute(OgnRandomGaussianDatabase& db, size_t count)
    {
        auto const genBuffers = db.state.gen.vectorized(count);
        if (genBuffers.size() != count)
        {
            db.logWarning("Failed to write to output standard normal distribution (wrong genBuffers size)");
            return false;
        }
        for (size_t i = 0; i < count; ++i)
        {
            auto outPtr = db.outputs.random(i).get<double>();
            if (!outPtr)
            {
                db.logWarning("Failed to write to output standard normal distribution (null output pointer)");
                return false;
            }
            *outPtr = asGenerator(genBuffers[i]).nextNormal<double>(0.0, 1.0);
        }

        return true;
    }

public:
    static void initialize(GraphContextObj const& contextObj, NodeObj const& nodeObj)
    {
        generateRandomSeed(contextObj, nodeObj, inputs::seed, inputs::useSeed);
    }

    static bool onCompute(OgnRandomGaussianDatabase& db, size_t count)
    {
        auto const& meanAttr{ db.inputs.mean() };
        auto const& stdevAttr{ db.inputs.stdev() };
        auto const& outAttr{ db.outputs.random() };

        if (!outAttr.resolved())
        {
            // Output type not yet resolved, can't compute
            db.logWarning("Unsupported input types");
            return false;
        }

        if (!meanAttr.resolved() && !stdevAttr.resolved())
        {
            // Output using default mean and stdev
            return defaultCompute(db, count);
        }

        // Inputs and outputs are resolved, try all real types
        auto const outType = outAttr.type();

        switch (outType.baseType) // NOLINT(clang-diagnostic-switch-enum)
        {
        case BaseDataType::eDouble:
            switch (outType.componentCount)
            {
            case 1:
                return tryComputeAssumingType<double>(db, count);
            case 2:
                return tryComputeAssumingType<double, 2>(db, count);
            case 3:
                return tryComputeAssumingType<double, 3>(db, count);
            case 4:
                return tryComputeAssumingType<double, 4>(db, count);
            case 9:
                return tryComputeAssumingType<double, 9>(db, count);
            case 16:
                return tryComputeAssumingType<double, 16>(db, count);
            default:
                break;
            }

        case BaseDataType::eFloat:
            switch (outType.componentCount)
            {
            case 1:
                return tryComputeAssumingType<float>(db, count);
            case 2:
                return tryComputeAssumingType<float, 2>(db, count);
            case 3:
                return tryComputeAssumingType<float, 3>(db, count);
            case 4:
                return tryComputeAssumingType<float, 4>(db, count);
            default:
                break;
            }

        case BaseDataType::eHalf:
            switch (outType.componentCount)
            {
            case 1:
                return tryComputeAssumingType<pxr::GfHalf>(db, count);
            case 2:
                return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
            case 3:
                return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
            case 4:
                return tryComputeAssumingType<pxr::GfHalf, 4>(db, count);
            default:
                break;
            }

        default:
            break;
        }

        db.logWarning("Unsupported input types");
        return false;
    }

    static void onConnectionTypeResolve(NodeObj const& node)
    {
        resolveOutputType(node, inputs::mean.token(), inputs::stdev.token(), outputs::random.token());
    }
};

#undef TRY_CASE

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
