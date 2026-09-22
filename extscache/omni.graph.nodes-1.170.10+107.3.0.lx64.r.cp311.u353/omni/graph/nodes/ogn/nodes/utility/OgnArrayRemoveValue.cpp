// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnArrayRemoveValueDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/string.h>
#include <omni/graph/core/ogn/Types.h>

#include <algorithm>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{
// unnamed namespace to avoid multiple declaration when linking
namespace
{
// Custom implementation of std::remove_if.
// Using std::remove_if fails to build when the underlying type is a tuple (eg int[3])
// DEPREACTED - Produces incorrect results.  Doesn't account for size after find_if runs
template <class ForwardIt, class UnaryPredicate>
int removeArray(ForwardIt first, ForwardIt last, UnaryPredicate p)
{
    int outputArraySize = 0;
    first = std::find_if(first, last, p);
    if (first != last)
    {
        for (ForwardIt i = first; ++i != last;)
        {
            if (!p(*i))
            {
                memcpy(&*first++, &*i, sizeof(*first));
                outputArraySize++;
            }
        }
    }
    return outputArraySize;
}

// Custom implementation of std::remove_if.
// Using std::remove_if fails to build when the underlying type is a tuple (eg int[3])
template <class ForwardIt, class UnaryPredicate>
int removeAllArray(ForwardIt first, ForwardIt last, UnaryPredicate p)
{
    int outputArraySize = 0;
    for (ForwardIt i = first; i != last; i++)
    {
        if (!p(*i))
        {
            memcpy(&*first++, &*i, sizeof(*first));
            outputArraySize++;
        }
    }
    return outputArraySize;
}

template <typename BaseType>
size_t tryComputeAssumingType(OgnArrayRemoveValueDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inputArray = db.inputs.array(idx).template get<BaseType[]>();
        auto const value = db.inputs.value(idx).template get<BaseType>();
        size_t const inputArraySize = db.inputs.array(idx).size();
        size_t const stride = sizeof(BaseType);
        auto outputArray = db.outputs.array(idx).template get<BaseType[]>();
        db.outputs.found(idx) = false;

        if (value && inputArray && outputArray)
        {
            db.outputs.array(idx).copyData(db.inputs.array(idx));
            auto equalsValue = [&value, &stride](auto& i) { return memcmp(&i, &*value, stride) == 0; };
            auto const it = std::find_if(inputArray->begin(), inputArray->end(), equalsValue);
            if (it != inputArray->end())
            {

                if (db.inputs.removeAll(idx))
                {
                    // This behavior reduces the size of the array due to incorrectly counting the removed elements
                    // Retained for backward compatibility
                    const int outputArraySize = removeArray(outputArray->begin(), outputArray->end(), equalsValue);
                    (*outputArray).resize(outputArraySize);
                }
                else if (db.inputs.removeAllFound(idx))
                {
                    const int outputArraySize = removeAllArray(outputArray->begin(), outputArray->end(), equalsValue);
                    (*outputArray).resize(outputArraySize);
                }
                else
                {
                    const int index = static_cast<int>(it - inputArray->begin());
                    memmove(outputArray->data() + index, outputArray->data() + index + 1,
                            stride * (inputArraySize - index - 1));
                    (*outputArray).resize(inputArraySize - 1);
                }
                db.outputs.found(idx) = true;
            }
        }
    }
    return count;
}
} // namespace

class OgnArrayRemoveValue
{
public:
    static size_t computeVectorized(OgnArrayRemoveValueDatabase& db, size_t count)
    {
        try
        {
            auto& inputType = db.inputs.value().type();
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
        auto const inputValue = node.iNode->getAttributeByToken(node, inputs::value.token());
        auto const outputArray = node.iNode->getAttributeByToken(node, outputs::array.token());
        auto const inputArrayType = inputArray.iAttribute->getResolvedType(inputArray);

        if (inputArrayType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 3> attrs{ inputArray, inputValue, outputArray };
            // all should have the same tuple count
            std::array<uint8_t, 3> tupleCounts{ inputArrayType.componentCount, inputArrayType.componentCount,
                                                inputArrayType.componentCount };
            // value type can not be an array because we don't support arrays-of-arrays
            std::array<uint8_t, 3> arrayDepths{ 1, 0, 1 };
            std::array<AttributeRole, 3> rolesBuf{ inputArrayType.role, AttributeRole::eUnknown, inputArrayType.role };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
