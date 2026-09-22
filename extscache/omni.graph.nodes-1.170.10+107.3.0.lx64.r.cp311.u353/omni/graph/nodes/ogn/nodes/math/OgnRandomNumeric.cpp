// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "OgnRandomNumericDatabase.h"
#include "random/RandomNodeBase.h"

#include <omni/graph/core/ogn/ComputeHelpers.h>

namespace omni
{
namespace graph
{
namespace nodes
{
using namespace random;

class OgnRandomNumeric : public NodeBase<OgnRandomNumeric, OgnRandomNumericDatabase>
{
    template <typename T>
    static bool tryComputeAssumingType(OgnRandomNumericDatabase& db, size_t count)
    {
        return ogn::compute::tryComputeWithArrayBroadcasting<T>(
            db.state.gen(), db.inputs.min(), db.inputs.max(), db.outputs.random(),
            [](GenBuffer_t const& genBuffer, T const& min, T const& max, T& result)
            {
                // Generate next random
                result = asGenerator(genBuffer).nextUniform(min, max);
            },
            count);
    }

    template <typename T, size_t N>
    static bool tryComputeAssumingType(OgnRandomNumericDatabase& db, size_t count)
    {
        return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(
            db.state.gen(), db.inputs.min(), db.inputs.max(), db.outputs.random(),
            [](GenBuffer_t const& genBuffer, T const& min, T const& max, T& result)
            {
                // Generate next random
                result = asGenerator(genBuffer).nextUniform(min, max);
            },
            count);
    }

    static bool defaultCompute(OgnRandomNumericDatabase& db, size_t count)
    {
        auto const genBuffers = db.state.gen.vectorized(count);
        if (genBuffers.size() != count)
        {
            db.logWarning("Failed to write to output using default range [0..1) (wrong genBuffers size)");
            return false;
        }
        for (size_t i = 0; i < count; ++i)
        {
            auto outPtr = db.outputs.random(i).get<double>();
            if (!outPtr)
            {
                db.logWarning("Failed to write to output using default range [0..1) (null output pointer)");
                return false;
            }
            *outPtr = asGenerator(genBuffers[i]).nextUniform<double>(0.0, 1.0);
        }

        return true;
    }

public:
    static void initialize(GraphContextObj const& contextObj, NodeObj const& nodeObj)
    {
        generateRandomSeed(contextObj, nodeObj, inputs::seed, inputs::useSeed);
    }

    static bool onCompute(OgnRandomNumericDatabase& db, size_t count)
    {
        auto const& minAttr{ db.inputs.min() };
        auto const& maxAttr{ db.inputs.max() };
        auto const& outAttr{ db.outputs.random() };

        if (!outAttr.resolved())
        {
            // Output type not yet resolved, can't compute
            db.logWarning("Unsupported input types");
            return false;
        }

        if (!minAttr.resolved() && !maxAttr.resolved())
        {
            // Output using default min and max
            return defaultCompute(db, count);
        }

        // Inputs and outputs are resolved, try all possible types, excluding bool and ogn::string
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

        case BaseDataType::eInt:
            switch (outType.componentCount)
            {
            case 1:
                return tryComputeAssumingType<int32_t>(db, count);
            case 2:
                return tryComputeAssumingType<int32_t, 2>(db, count);
            case 3:
                return tryComputeAssumingType<int32_t, 3>(db, count);
            case 4:
                return tryComputeAssumingType<int32_t, 4>(db, count);
            default:
                break;
            }

        case BaseDataType::eInt64:
            return tryComputeAssumingType<int64_t>(db, count);

        case BaseDataType::eUChar:
            return tryComputeAssumingType<unsigned char>(db, count);

        case BaseDataType::eUInt:
            return tryComputeAssumingType<uint32_t>(db, count);

        case BaseDataType::eUInt64:
            return tryComputeAssumingType<uint64_t>(db, count);

        default:
            break;
        }

        db.logWarning("Unsupported input types");
        return false;
    }

    static void onConnectionTypeResolve(NodeObj const& node)
    {
        resolveOutputType(node, inputs::min.token(), inputs::max.token(), outputs::random.token());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
