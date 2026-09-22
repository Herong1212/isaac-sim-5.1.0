// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnToUint64Database.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/UsdTypes.h>

namespace omni
{
namespace graph
{
namespace nodes
{
namespace
{

template <typename T>
size_t tryComputeAssumingType(OgnToUint64Database& db, size_t count)
{
    auto functor = [](auto const& value, auto& converted) { converted = static_cast<uint64_t>(value); };
    return ogn::compute::tryComputeWithArrayBroadcasting<T, uint64_t>(
               db.inputs.value(), db.outputs.converted(), functor, count) ?
               count :
               0;
}

} // namespace

class OgnToUint64
{
public:
    // Node to convert numeric inputs to floats
    static size_t computeVectorized(OgnToUint64Database& db, size_t count)
    {
        auto& valueType = db.inputs.value().type();
        try
        {
            switch (valueType.baseType)
            {
            case BaseDataType::eBool:
                return tryComputeAssumingType<bool>(db, count);
            case BaseDataType::eUChar:
                return tryComputeAssumingType<uchar>(db, count);
            case BaseDataType::eInt:
                return tryComputeAssumingType<int32_t>(db, count);
            case BaseDataType::eUInt:
                return tryComputeAssumingType<uint32_t>(db, count);
            case BaseDataType::eInt64:
                return tryComputeAssumingType<int64_t>(db, count);
            case BaseDataType::eUInt64:
                return tryComputeAssumingType<uint64_t>(db, count);
            case BaseDataType::eHalf:
                return tryComputeAssumingType<pxr::GfHalf>(db, count);
            case BaseDataType::eFloat:
                return tryComputeAssumingType<float>(db, count);
            case BaseDataType::eDouble:
                return tryComputeAssumingType<double>(db, count);
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

    static void onConnectionTypeResolve(const NodeObj& nodeObj)
    {
        auto valueAttr = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::value.token());
        auto outAttr = nodeObj.iNode->getAttributeByToken(nodeObj, outputs::converted.token());

        auto valueType = valueAttr.iAttribute->getResolvedType(valueAttr);

        // The output shape must match the input shape and visa-versa, however we can't say anything
        // about the input base type until it's connected
        if (valueType.baseType != BaseDataType::eUnknown)
        {
            Type resultType(BaseDataType::eUInt64, 1, valueType.arrayDepth);
            outAttr.iAttribute->setResolvedType(outAttr, resultType);
        }
        else
            outAttr.iAttribute->setResolvedType(outAttr, Type(BaseDataType::eUnknown));
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
