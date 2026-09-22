// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnFModDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include <omni/math/linalg/math.h>
#include <math.h>

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
double safeFMod(T a, T b)
{
    if (static_cast<double>(b) == 0.0)
        return T(0);
    return std::fmod(a, b);
}

// Compute for scalar non-half inputs
template <typename T>
size_t tryComputeAssumingType(OgnFModDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result) { result = static_cast<T>(safeFMod(a, b)); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T>(
               db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Compute for scalar half inputs
template <>
size_t tryComputeAssumingType<pxr::GfHalf>(OgnFModDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    { result = static_cast<pxr::GfHalf>(static_cast<float>(safeFMod(a, b))); };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf>(
               db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Compute for tuple non-half types
template <typename T, size_t N, std::enable_if_t<!std::is_same<T, pxr::GfHalf>::value, bool> = true>
size_t tryComputeAssumingType(OgnFModDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result) { result = static_cast<T>(safeFMod(a, b)); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(
               db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count) ?
               count :
               0;
}

// Compute for tuple half types
template <typename T, size_t N, std::enable_if_t<std::is_same<T, pxr::GfHalf>::value, bool> = true>
size_t tryComputeAssumingType(OgnFModDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto& result)
    { result = static_cast<pxr::GfHalf>(static_cast<float>(safeFMod(a, b))); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(
               db.inputs.a(), db.inputs.b(), db.outputs.result(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnFMod
{
public:
    static size_t computeVectorized(OgnFModDatabase& db, size_t count)
    {
        try
        {
            const auto& outputType = db.outputs.result().type();
            switch (outputType.baseType)
            {
            case BaseDataType::eDouble:
                switch (outputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
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
                switch (outputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<float>(db, count);
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
                switch (outputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<pxr::GfHalf>(db, count);
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
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto aType = a.iAttribute->getResolvedType(a);
        auto bType = b.iAttribute->getResolvedType(b);

        if (aType.baseType != BaseDataType::eUnknown && bType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ a, b, result };
            std::array<uint8_t, 3> tupleCounts{ aType.componentCount, bType.componentCount,
                                                std::max(aType.componentCount, bType.componentCount) };
            std::array<uint8_t, 3> arrayDepths{ aType.arrayDepth, bType.arrayDepth,
                                                std::max(aType.arrayDepth, bType.arrayDepth) };
            std::array<AttributeRole, 3> rolesBuf{ aType.role, bType.role, AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
