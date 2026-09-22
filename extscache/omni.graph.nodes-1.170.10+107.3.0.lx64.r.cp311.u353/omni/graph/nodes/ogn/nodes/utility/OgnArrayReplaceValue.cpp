// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnArrayReplaceValueDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
// Custom implementation of std::replace_if.
// Using std::replace_if fails to build when the underlying type is a tuple (eg int[3])
template <class ForwardIt, class UnaryPredicate, class T>
void replaceAllArray(ForwardIt first, ForwardIt last, UnaryPredicate p, const T& value)
{
    for (; first != last; ++first)
        if (p(*first))
            memcpy(&*first, &*value, sizeof(*first));
}

template <typename BaseType>
size_t tryComputeAssumingType(OgnArrayReplaceValueDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        auto const inputArray = db.inputs.array(idx).template get<BaseType[]>();
        auto const value = db.inputs.value(idx).template get<BaseType>();
        auto const newValue = db.inputs.newValue(idx).template get<BaseType>();
        auto outputArray = db.outputs.array(idx).template get<BaseType[]>();
        db.outputs.found(idx) = false;

        if (value && inputArray && outputArray)
        {
            db.outputs.array(idx).copyData(db.inputs.array(idx));
            auto equalsValue = [&value](auto& i) { return memcmp(&i, &*value, sizeof(BaseType)) == 0; };
            auto const it = std::find_if(inputArray->begin(), inputArray->end(), equalsValue);
            if (it != inputArray->end())
            {
                if (db.inputs.replaceAllFound(idx))
                {
                    replaceAllArray(outputArray->begin(), outputArray->end(), equalsValue, newValue);
                }
                else
                {
                    const int index = static_cast<int>(it - inputArray->begin());
                    memcpy(&((*outputArray)[index]), &*newValue, sizeof(BaseType));
                }
                db.outputs.found(idx) = true;
            }
        }
    }
    return count;
}
} // namespace

class OgnArrayReplaceValue
{
public:
    static size_t computeVectorized(OgnArrayReplaceValueDatabase& db, size_t count)
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
        auto const inputNewValue = node.iNode->getAttributeByToken(node, inputs::newValue.token());
        auto const outputArray = node.iNode->getAttributeByToken(node, outputs::array.token());
        auto const inputArrayType = inputArray.iAttribute->getResolvedType(inputArray);

        if (inputArrayType.baseType != BaseDataType::eUnknown)
        {
            std::array<AttributeObj, 4> attrs{ inputArray, inputValue, inputNewValue, outputArray };
            // all should have the same tuple count
            std::array<uint8_t, 4> tupleCounts{ inputArrayType.componentCount, inputArrayType.componentCount,
                                                inputArrayType.componentCount, inputArrayType.componentCount };
            // value type can not be an array because we don't support arrays-of-arrays
            std::array<uint8_t, 4> arrayDepths{ 1, 0, 0, 1 };
            std::array<AttributeRole, 4> rolesBuf{ inputArrayType.role, AttributeRole::eUnknown,
                                                   AttributeRole::eUnknown, inputArrayType.role };
            node.iNode->resolvePartiallyCoupledAttributes(
                node, attrs.data(), tupleCounts.data(), arrayDepths.data(), rolesBuf.data(), attrs.size());
        }
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
