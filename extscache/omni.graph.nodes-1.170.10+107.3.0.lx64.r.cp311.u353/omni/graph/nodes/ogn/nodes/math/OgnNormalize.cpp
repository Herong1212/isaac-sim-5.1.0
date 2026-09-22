// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnNormalizeDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/math/linalg/vec.h>
#include <carb/logging/Log.h>
#include <cmath>

namespace omni
{
namespace graph
{
namespace nodes
{

// unnamed namespace to avoid multiple declaration when linking
namespace
{

template <typename T, size_t N>
size_t tryComputeAssumingType(OgnNormalizeDatabase& db, size_t count)
{
    auto functor = [](auto const& vector, auto& result)
    {
        const auto& vec = *reinterpret_cast<const omni::math::linalg::base_vec<T, N>*>(vector);
        auto& res = *reinterpret_cast<omni::math::linalg::base_vec<T, N>*>(result);
        res = vec.GetNormalized();
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N]>(
               db.inputs.vector(), db.outputs.result(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnNormalize
{
public:
    static size_t computeVectorized(OgnNormalizeDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.vector().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eDouble:
                switch (inputType.componentCount)
                {
                case 2:
                    return tryComputeAssumingType<double, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<double, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<double, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (inputType.componentCount)
                {
                case 2:
                    return tryComputeAssumingType<float, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<float, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<float, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eHalf:
                switch (inputType.componentCount)
                {
                case 2:
                    return tryComputeAssumingType<pxr::GfHalf, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            // LCOV_EXCL_START
            default:
                throw ogn::compute::InputError("Failed to resolve input types");
                // LCOV_EXCL_STOP
            }
        }
        // LCOV_EXCL_START
        catch (ogn::compute::InputError& error)
        {
            db.logError(error.what());
        }
        return 0;
        // LCOV_EXCL_STOP
    }

    static void onConnectionTypeResolve(const NodeObj& node)
    {
        auto vector = node.iNode->getAttributeByToken(node, inputs::vector.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        // Require input to be resolved before determining result's type
        auto vectorType = vector.iAttribute->getResolvedType(vector);
        if (vectorType.baseType != BaseDataType::eUnknown)
        {
            Type resultType(vectorType.baseType, vectorType.componentCount, vectorType.arrayDepth);
            result.iAttribute->setResolvedType(result, resultType);
        }
        else
            result.iAttribute->setResolvedType(result, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
// end-compute-helpers
