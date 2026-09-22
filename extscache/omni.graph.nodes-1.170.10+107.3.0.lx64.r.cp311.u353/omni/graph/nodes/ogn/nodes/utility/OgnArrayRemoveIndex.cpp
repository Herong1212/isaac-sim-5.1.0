// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnArrayRemoveIndexDatabase.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
#include <algorithm>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{
using core::ogn::array;

// unnamed namespace to avoid multiple declaration when linking
namespace
{

// helper to wrap a given index from legal range [-arrayLength, arrayLength) to [0:arrayLength)
// This will throw if the wrapped index is out of bounds
size_t tryWrapIndex(int index, size_t arraySize)
{
    int wrappedIndex = index;
    if (index < 0)
        wrappedIndex = static_cast<int>(arraySize) + index;
    if (wrappedIndex < 0 || wrappedIndex >= static_cast<int>(arraySize))
        throw ogn::compute::InputError(
            formatString("inputs:index %d is out of range for inputs:array of size %zu", wrappedIndex, arraySize));
    return static_cast<size_t>(wrappedIndex);
}

template <typename BaseType>
size_t tryComputeAssumingType(OgnArrayRemoveIndexDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inputArray = db.inputs.array(idx).template get<BaseType[]>();
        size_t const inputArraySize = db.inputs.array(idx).size();
        size_t const index = tryWrapIndex(db.inputs.index(idx), inputArraySize);
        auto outputArray = db.outputs.array(idx).template get<BaseType[]>();

        if (inputArray && outputArray)
        {
            db.outputs.array(idx).copyData(db.inputs.array(idx));
            memmove(outputArray->data() + index, outputArray->data() + index + 1,
                    sizeof(BaseType) * (inputArraySize - index - 1));
            (*outputArray).resize(inputArraySize - 1);
        }
    }
    return true;
}
} // namespace

class OgnArrayRemoveIndex
{
public:
    static size_t computeVectorized(OgnArrayRemoveIndexDatabase& db, size_t count)
    {
        try
        {
            auto& inputType = db.inputs.array().type();
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
        auto const inputArray = node.iNode->getAttributeByToken(node, inputs::array.token());
        auto const outputArray = node.iNode->getAttributeByToken(node, outputs::array.token());
        auto const inputArrayType = inputArray.iAttribute->getResolvedType(inputArray);

        if (inputArrayType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ inputArray, outputArray };
            node.iNode->resolveCoupledAttributes(node, attrs.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
