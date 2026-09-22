// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnDotProductDatabase.h>
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
size_t tryComputeAssumingType(OgnDotProductDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& product)
    {
        const auto& vecA = *reinterpret_cast<const omni::math::linalg::base_vec<T, N>*>(a);
        const auto& vecB = *reinterpret_cast<const omni::math::linalg::base_vec<T, N>*>(b);
        product = vecA.Dot(vecB);
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N], T>(
               db.inputs.a(), db.inputs.b(), db.outputs.product(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnDotProduct
{
public:
    static size_t computeVectorized(OgnDotProductDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.a().type();
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
        auto a = node.iNode->getAttributeByToken(node, inputs::a.token());
        auto b = node.iNode->getAttributeByToken(node, inputs::b.token());
        auto product = node.iNode->getAttributeByToken(node, outputs::product.token());

        // Require inputs to be resolved before determining product's type
        auto aType = a.iAttribute->getResolvedType(a);
        auto bType = b.iAttribute->getResolvedType(b);
        if (aType.baseType != BaseDataType::eUnknown && bType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ a, b, product };
            // a, b should all have the same tuple count
            std::array<uint8_t, 3> tupleCounts{ aType.componentCount, bType.componentCount, 1 };
            std::array<uint8_t, 3> arrayDepths{ aType.arrayDepth, bType.arrayDepth,
                                                // Allow for a mix of singular and array inputs. If any input is an
                                                // array, the output must be an array
                                                std::max(aType.arrayDepth, bType.arrayDepth) };
            std::array<AttributeRole, 3> rolesBuf{ aType.role, bType.role, AttributeRole::eNone };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
// end-compute-helpers
