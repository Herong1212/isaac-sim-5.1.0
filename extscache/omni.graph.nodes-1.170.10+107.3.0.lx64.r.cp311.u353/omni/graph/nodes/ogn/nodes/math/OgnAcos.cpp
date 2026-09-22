// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnAcosDatabase.h>
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

// Compute for scalar non-half inputs
template <typename T>
size_t tryComputeAssumingType(OgnAcosDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result)
    { result = static_cast<T>(pxr::GfRadiansToDegrees(std::acos(value))); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T>(db.inputs.value(), db.outputs.value(), functor, count) ?
               count :
               0;
}

// Compute for scalar half inputs
template <>
size_t tryComputeAssumingType<pxr::GfHalf>(OgnAcosDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result)
    { result = static_cast<pxr::GfHalf>(static_cast<float>(pxr::GfRadiansToDegrees(std::acos(value)))); };
    return ogn::compute::tryComputeWithArrayBroadcasting<pxr::GfHalf>(
               db.inputs.value(), db.outputs.value(), functor, count) ?
               count :
               0;
}

// Compute for tuple non-half types
template <typename T, size_t N, std::enable_if_t<!std::is_same<T, pxr::GfHalf>::value, bool> = true>
size_t tryComputeAssumingType(OgnAcosDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result)
    { result = static_cast<T>(pxr::GfRadiansToDegrees(std::acos(value))); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(db.inputs.value(), db.outputs.value(), functor, count) ?
               count :
               0;
}

// Compute for tuple half types
template <typename T, size_t N, std::enable_if_t<std::is_same<T, pxr::GfHalf>::value, bool> = true>
size_t tryComputeAssumingType(OgnAcosDatabase& db, size_t count)
{
    auto functor = [](auto const& value, auto& result)
    { result = static_cast<pxr::GfHalf>(static_cast<float>(pxr::GfRadiansToDegrees(std::acos(value)))); };
    return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(db.inputs.value(), db.outputs.value(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnAcos
{
public:
    static size_t computeVectorized(OgnAcosDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.value().type();
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
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
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
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
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
        auto input = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::value.token());

        auto inputType = input.iAttribute->getResolvedType(input);

        // Require inputs to be resolved before determining output's type
        if (inputType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ input, result };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
