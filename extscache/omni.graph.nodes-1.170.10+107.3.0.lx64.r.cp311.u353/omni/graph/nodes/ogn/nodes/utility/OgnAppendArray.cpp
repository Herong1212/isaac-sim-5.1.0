// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnAppendArrayDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

namespace omni
{
namespace graph
{
namespace nodes
{

// unnamed namespace to avoid multiple declaration when linking
namespace
{
template <typename BaseType>
size_t tryComputeAssumingType(OgnAppendArrayDatabase& db, size_t count)
{
    auto const& dynamicInputs = db.getDynamicInputs();
    std::vector<ogn::DynamicInput> allInputs{ db.inputs.input0, db.inputs.input1 };
    allInputs.reserve(dynamicInputs.size() + 2);
    allInputs.insert(allInputs.end(), dynamicInputs.begin(), dynamicInputs.end());

    for (size_t idx = 0; idx < count; ++idx)
    {
        auto outputArray = db.outputs.array(idx).template get<BaseType[]>();

        // Find the combined size and resize the output
        size_t arraySize = 0;
        for (auto const& input : allInputs)
            arraySize += input(idx).size();
        (*outputArray).resize(arraySize);

        // Copy inputs to output
        size_t start = 0;
        for (auto const& input : allInputs)
        {
            const auto inputArray = input(idx).template get<BaseType[]>();
            if (!inputArray->empty())
            {
                memcpy(outputArray->data() + start, inputArray->data(), sizeof(BaseType) * inputArray.size());
                start += inputArray.size();
            }
        }
    }
    return count;
}
} // namespace

class OgnAppendArray
{
public:
    static size_t computeVectorized(OgnAppendArrayDatabase& db, size_t count)
    {
        try
        {
            auto& inputType = db.inputs.input0().type();
            switch (inputType.baseType)
            {
            case BaseDataType::eBool:
                return tryComputeAssumingType<bool>(db, count);
            case BaseDataType::eToken:
                return tryComputeAssumingType<ogn::Token>(db, count);
            case BaseDataType::eDouble:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<double>(db, count);
                case 2:
                    return tryComputeAssumingType<double[2]>(db, count);
                case 3:
                    return tryComputeAssumingType<double[3]>(db, count);
                case 4:
                    return tryComputeAssumingType<double[4]>(db, count);
                case 9:
                    return tryComputeAssumingType<double[9]>(db, count);
                case 16:
                    return tryComputeAssumingType<double[16]>(db, count);
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
                    return tryComputeAssumingType<float[2]>(db, count);
                case 3:
                    return tryComputeAssumingType<float[3]>(db, count);
                case 4:
                    return tryComputeAssumingType<float[4]>(db, count);
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
                    return tryComputeAssumingType<pxr::GfHalf[2]>(db, count);
                case 3:
                    return tryComputeAssumingType<pxr::GfHalf[3]>(db, count);
                case 4:
                    return tryComputeAssumingType<pxr::GfHalf[4]>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt:
                switch (inputType.componentCount)
                {
                case 1:
                    return tryComputeAssumingType<int>(db, count);
                case 2:
                    return tryComputeAssumingType<int[2]>(db, count);
                case 3:
                    return tryComputeAssumingType<int[3]>(db, count);
                case 4:
                    return tryComputeAssumingType<int[4]>(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUChar:
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
        auto totalCount = node.iNode->getAttributeCount(node);
        std::vector<AttributeObj> allAttributes(totalCount);
        node.iNode->getAttributes(node, allAttributes.data(), totalCount);

        std::vector<AttributeObj> attrs;
        attrs.reserve(totalCount - 2);

        for (auto const& attr : allAttributes)
        {
            if (attr.iAttribute->getPortType(attr) == AttributePortType::kAttributePortType_Input)
            {
                attrs.push_back(attr);
            }
        }

        auto output = node.iNode->getAttributeByToken(node, outputs::array.token());
        attrs.push_back(output);

        node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
