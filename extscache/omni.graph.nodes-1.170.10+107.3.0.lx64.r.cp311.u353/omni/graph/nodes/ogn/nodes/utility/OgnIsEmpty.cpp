// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnIsEmptyDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <omni/graph/core/ogn/Types.h>
#include <string>

namespace omni
{
namespace graph
{
namespace nodes
{

namespace
{
size_t tryComputeEmpty(OgnIsEmptyDatabase& db, size_t count)
{
    for (size_t idx = 0; idx < count; ++idx)
    {
        const auto& input = db.inputs.input(idx);
        db.outputs.isEmpty(idx) = input.size() == 0;
    }
    return count;
}

size_t tryComputeEmptyToken(OgnIsEmptyDatabase& db, size_t count)
{
    const auto input = db.inputs.input().template get<ogn::Token>();
    if (input)
    {
        const auto inputVec = input.vectorized(count);
        auto outputVec = db.outputs.isEmpty.vectorized(count);
        for (size_t idx = 0; idx < count; ++idx)
        {
            outputVec[idx] = inputVec[idx] == omni::fabric::kUninitializedToken;
        }
    }
    return count;
}
} // namespace

class OgnIsEmpty
{
public:
    static size_t computeVectorized(OgnIsEmptyDatabase& db, size_t count)
    {
        try
        {
            const auto& inputType = db.inputs.input().type();
            switch (inputType.arrayDepth)
            {
            case 0:
                switch (inputType.baseType)
                {
                case BaseDataType::eBool:
                case BaseDataType::eUChar:
                case BaseDataType::eInt:
                case BaseDataType::eUInt:
                case BaseDataType::eInt64:
                case BaseDataType::eUInt64:
                case BaseDataType::eHalf:
                case BaseDataType::eFloat:
                case BaseDataType::eDouble:
                    db.outputs.isEmpty() = false;
                    return count;
                case BaseDataType::eToken:
                    return tryComputeEmptyToken(db, count);
                // LCOV_EXCL_START
                default:
                    throw ogn::compute::InputError("Failed to resolve input types");
                    // LCOV_EXCL_STOP
                }
            case 1:
                return tryComputeEmpty(db, count);
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
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
