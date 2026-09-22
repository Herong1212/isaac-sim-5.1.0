// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnMultiplyDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
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
bool tryComputeAssumingType(OgnMultiplyDatabase& db, size_t count)
{
    auto const& dynamicInputs = db.getDynamicInputs();
    if (dynamicInputs.empty())
    {
        auto functor = [](T const& a, T const& b, T& result) { result = a * b; };
        return ogn::compute::tryComputeWithArrayBroadcasting<T>(
            db.inputs.a(), db.inputs.b(), db.outputs.product(), functor, count);
    }
    else
    {
        std::vector<ogn::InputAttribute> inputArray{ db.inputs.a(), db.inputs.b() };
        inputArray.reserve(dynamicInputs.size() + 2);
        for (auto const& input : dynamicInputs)
            inputArray.emplace_back(input());

        auto functor = [](const auto& input, auto& result) { result = result * input; };
        return ogn::compute::tryComputeInputsWithArrayBroadcasting<T>(inputArray, db.outputs.product(), functor, count);
    }
}
template <typename T, size_t N>
bool tryComputeAssumingType(OgnMultiplyDatabase& db, size_t count)
{
    auto const& dynamicInputs = db.getDynamicInputs();
    if (dynamicInputs.empty())
    {
        auto functor = [](T const& a, T const& b, T& result) { result = a * b; };
        return ogn::compute::tryComputeWithTupleBroadcasting<N, T>(
            db.inputs.a(), db.inputs.b(), db.outputs.product(), functor, count);
    }
    else
    {
        std::vector<ogn::InputAttribute> inputArray{ db.inputs.a(), db.inputs.b() };
        inputArray.reserve(dynamicInputs.size() + 2);
        for (auto const& input : dynamicInputs)
            inputArray.emplace_back(input());

        auto functor = [](const auto& input, auto& result) { result = result * input; };
        return ogn::compute::tryComputeInputsWithTupleBroadcasting<N, T>(
            inputArray, db.outputs.product(), functor, count);
    }
}
} // namespace

class OgnMultiply
{
public:
    static size_t computeVectorized(OgnMultiplyDatabase& db, size_t count)
    {
        try
        {
            auto& productType = db.outputs.product().type();
            switch (productType.baseType)
            {
            case BaseDataType::eDouble:
                switch (productType.componentCount)
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
                switch (productType.componentCount)
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
                switch (productType.componentCount)
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
                switch (productType.componentCount)
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
                };
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUChar:
                return tryComputeAssumingType<unsigned char>(db, count);
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
        auto totalCount = node.iNode->getAttributeCount(node);
        std::vector<AttributeObj> allAttributes(totalCount);
        node.iNode->getAttributes(node, allAttributes.data(), totalCount);

        std::vector<AttributeObj> attributes;
        std::vector<uint8_t> componentCounts;
        std::vector<uint8_t> arrayDepths;
        std::vector<AttributeRole> roles;

        attributes.reserve(totalCount - 2);
        componentCounts.reserve(totalCount - 2);
        arrayDepths.reserve(totalCount - 2);
        roles.reserve(totalCount - 2);

        uint8_t maxArrayDepth = 0;
        uint8_t maxComponentCount = 0;
        AttributeRole outRole = AttributeRole::eUnknown;

        auto product = node.iNode->getAttributeByToken(node, outputs::product.token());
        for (auto const& attr : allAttributes)
        {
            if (attr.iAttribute->getPortType(attr) == AttributePortType::kAttributePortType_Input)
            {
                auto resolvedType = attr.iAttribute->getResolvedType(attr);

                // if some inputs are not connected stop - the output port resolution is only completed when all inputs
                // are connected
                if (resolvedType.baseType == BaseDataType::eUnknown)
                {
                    product.iAttribute->setResolvedType(product, Type(BaseDataType::eUnknown));
                    return;
                }

                // If we find a matrix, force the output to be a matrix
                if (resolvedType.componentCount >= 9)
                    outRole = resolvedType.role;

                componentCounts.push_back(resolvedType.componentCount);
                arrayDepths.push_back(resolvedType.arrayDepth);
                roles.push_back(resolvedType.role);
                maxComponentCount = std::max(maxComponentCount, resolvedType.componentCount);
                maxArrayDepth = std::max(maxArrayDepth, resolvedType.arrayDepth);

                attributes.push_back(attr);
            }
        }

        attributes.push_back(product);
        // All inputs and the output should have the same tuple count
        componentCounts.push_back(maxComponentCount);
        // Allow for a mix of singular and array inputs. If any input is an array, the output must be an array
        arrayDepths.push_back(maxArrayDepth);
        // Copy the attribute role from the resolved type to the output type
        roles.push_back(outRole);

        node.iNode->resolvePartiallyCoupledAttributes(
            node, attributes.data(), componentCounts.data(), arrayDepths.data(), roles.data(), attributes.size());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
