// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnArrayIndexDatabase.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <carb/logging/Log.h>
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

// helper to wrap a given index from legal range [-arrayLength, arrayLength) to [0:arrayLength).
// values outside of the legal range with throw
size_t tryWrapIndex(int index, size_t arraySize)
{
    int wrappedIndex = index;
    if (index < 0)
        wrappedIndex = (int)arraySize + index;
    if ((wrappedIndex >= (int)arraySize) || (wrappedIndex < 0))
        throw ogn::compute::InputError(
            formatString("inputs:index %d is out of range for inputs:array of size %zu", wrappedIndex, arraySize));
    return size_t(wrappedIndex);
}

template <typename BaseType>
size_t tryComputeAssumingType(OgnArrayIndexDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inputArray = db.inputs.array(idx).template get<BaseType[]>();
        size_t const index = tryWrapIndex(db.inputs.index(idx), db.inputs.array(idx).size());
        auto outputValue = db.outputs.value(idx).template get<BaseType>();

        if (outputValue && inputArray)
            memcpy(&*outputValue, &((*inputArray)[index]), sizeof(BaseType));
    }
    return count;
}
} // namespace

class OgnArrayIndex
{
public:
    static size_t computeVectorized(OgnArrayIndexDatabase& db, size_t count)
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
        auto const array = node.iNode->getAttributeByToken(node, inputs::array.token());
        auto const value = node.iNode->getAttributeByToken(node, outputs::value.token());

        auto const arrayType = array.iAttribute->getResolvedType(array);

        if (arrayType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 2> attrs{ array, value };
            // array and value should have the same tuple count
            std::array<uint8_t, 2> tupleCounts{ arrayType.componentCount, arrayType.componentCount };
            // value type can not be an array because we don't support arrays-of-arrays
            std::array<uint8_t, 2> arrayDepths{ 1, 0 };
            std::array<AttributeRole, 2> rolesBuf{ arrayType.role,
                                                   // Copy the attribute role from the array type to the value type
                                                   AttributeRole::eUnknown };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
