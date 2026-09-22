// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnNegateDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>

namespace omni
{
namespace graph
{
namespace nodes
{
// unnamed namespace to avoid multiple declaration when linking
namespace
{
template <typename T>
bool tryComputeAssumingType(OgnNegateDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output) { output = input * -1; };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, T>(db.inputs.input(), db.outputs.output(), functor, count);
}
template <typename T, size_t N>
bool tryComputeAssumingType(OgnNegateDatabase& db, size_t count)
{
    auto functor = [](auto const& input, auto& output)
    {
        for (size_t i = 0; i < N; ++i)
        {
            output[i] = input[i] * -1;
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N]>(
        db.inputs.input(), db.outputs.output(), functor, count);
}
} // namespace

class OgnNegate
{
public:
    static bool computeVectorized(OgnNegateDatabase& db, size_t count)
    {
        auto& inputType = db.inputs.input().type();
        // Compute the components, if the types are all resolved.
        try
        {
            switch (inputType.baseType)
            {
            case BaseDataType::eDouble:
                switch (inputType.componentCount)
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
                switch (inputType.componentCount)
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
                switch (inputType.componentCount)
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
                switch (inputType.componentCount)
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
                };
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

            db.logWarning("Failed to resolve input types");
        }
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return false;
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto input = node.iNode->getAttributeByToken(node, inputs::input.token());
        auto output = node.iNode->getAttributeByToken(node, outputs::output.token());
        auto inputType = input.iAttribute->getResolvedType(input);

        // Require input to be resolved before determining output's type
        if (inputType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ input, output };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
// end-compute-helpers
