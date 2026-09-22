// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnSelectIfDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/string.h>
#include <omni/graph/core/ogn/Types.h>
#include <carb/logging/Log.h>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
template <typename T>
size_t tryComputeAssumingType(OgnSelectIfDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto const& condition, auto& result) { result = condition ? a : b; };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, T, bool, T>(
               db.inputs.ifTrue(), db.inputs.ifFalse(), db.inputs.condition(), db.outputs.result(), functor, count) ?
               count :
               0;
}

template <>
size_t tryComputeAssumingType<string>(OgnSelectIfDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        const bool condition = *db.inputs.condition(idx).template get<bool>();
        auto ifTrue = db.inputs.ifTrue(idx).template get<const uchar[]>();
        auto ifFalse = db.inputs.ifFalse(idx).template get<const uchar[]>();
        auto result = db.outputs.result(idx).template get<uchar[]>();
        if (condition)
        {
            result->resize(ifTrue->size());
            memcpy(result->data(), ifTrue->data(), result->size());
        }
        else
        {
            result->resize(ifFalse->size());
            memcpy(result->data(), ifFalse->data(), result->size());
        }
    }
    return count;
}

template <typename T, size_t N>
size_t tryComputeAssumingType(OgnSelectIfDatabase& db, size_t count)
{
    auto functor = [](auto const& a, auto const& b, auto const& condition, auto& result)
    {
        if (condition)
        {
            memcpy(result, a, sizeof(T) * N);
        }
        else
        {
            memcpy(result, b, sizeof(T) * N);
        }
    };
    return ogn::compute::tryComputeWithArrayBroadcasting<T[N], T[N], bool, T[N]>(
               db.inputs.ifTrue(), db.inputs.ifFalse(), db.inputs.condition(), db.outputs.result(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnSelectIf
{
public:
    static size_t computeVectorized(OgnSelectIfDatabase& db, size_t count)
    {
        try
        {
            const auto& ifTrueType = db.inputs.ifTrue().type();
            const auto& ifFalseType = db.inputs.ifFalse().type();
            const auto& conditionType = db.inputs.condition().type();
            if (ifTrueType.componentCount != ifFalseType.componentCount)
                throw ogn::compute::InputError("Mismatched tuple counts: " + std::to_string(ifTrueType.componentCount) +
                                               " and " + std::to_string(ifFalseType.componentCount));

            switch (ifTrueType.baseType)
            {
            case BaseDataType::eBool:
                return tryComputeAssumingType<bool>(db, count);
            case BaseDataType::eToken:
                return tryComputeAssumingType<ogn::Token>(db, count);
            case BaseDataType::eDouble:
                switch (ifTrueType.componentCount)
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
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eFloat:
                switch (ifTrueType.componentCount)
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
                switch (ifTrueType.componentCount)
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
            case BaseDataType::eInt:
                switch (ifTrueType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int32_t>(db, count);
                case 2:
                    return tryComputeAssumingType<int32_t, 2>(db, count);
                case 3:
                    return tryComputeAssumingType<int32_t, 3>(db, count);
                case 4:
                    return tryComputeAssumingType<int32_t, 4>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUChar:
                // This handles string case (arrays of strings are not supported)
                if (ifTrueType.arrayDepth == 1 && ifFalseType.arrayDepth == 1 && conditionType.arrayDepth == 0 &&
                    (ifTrueType.role == AttributeRole::eText || ifTrueType.role == AttributeRole::ePath) &&
                    (ifFalseType.role == AttributeRole::eText || ifFalseType.role == AttributeRole::ePath))
                {
                    return tryComputeAssumingType<string>(db, count);
                }
                return tryComputeAssumingType<uchar>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t>(db, count);
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
        auto ifTrue = node.iNode->getAttributeByToken(node, inputs::ifTrue.token());
        auto ifFalse = node.iNode->getAttributeByToken(node, inputs::ifFalse.token());
        auto condition = node.iNode->getAttributeByToken(node, inputs::condition.token());
        auto result = node.iNode->getAttributeByToken(node, outputs::result.token());

        auto ifTrueType = ifTrue.iAttribute->getResolvedType(ifTrue);
        auto ifFalseType = ifFalse.iAttribute->getResolvedType(ifFalse);
        auto conditionType = condition.iAttribute->getResolvedType(condition);

        // Require ifTrue, ifFalse, and condition to be resolved before determining result's type
        if (ifTrueType.baseType != BaseDataType::eUnknown && ifFalseType.baseType != BaseDataType::eUnknown &&
            conditionType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ ifTrue, ifFalse, result };
            std::array<uint8_t, 3> tupleCounts{ ifTrueType.componentCount, ifFalseType.componentCount,
                                                std::max(ifTrueType.componentCount, ifFalseType.componentCount) };
            std::array<uint8_t, 3> arrayDepths{ ifTrueType.arrayDepth, ifFalseType.arrayDepth,
                                                std::max(conditionType.arrayDepth,
                                                         std::max(ifTrueType.arrayDepth, ifFalseType.arrayDepth)) };
            const bool isStringInput =
                (ifTrueType.baseType == BaseDataType::eUChar && ifTrueType.arrayDepth == 1 &&
                 ifFalseType.baseType == BaseDataType::eUChar && ifFalseType.arrayDepth == 1 &&
                 (ifTrueType.role == AttributeRole::eText || ifTrueType.role == AttributeRole::ePath) &&
                 (ifFalseType.role == AttributeRole::eText || ifFalseType.role == AttributeRole::ePath) &&
                 conditionType.arrayDepth == 0);
            std::array<AttributeRole, 3> rolesBuf{ ifTrueType.role, ifFalseType.role,
                                                   isStringInput ? AttributeRole::eText : AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
