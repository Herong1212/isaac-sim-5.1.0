// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnSelectTargetIfDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnSelectTargetIf
{
public:
    static size_t computeVectorized(OgnSelectTargetIfDatabase& db, size_t count)
    {
        try
        {
            const auto& conditionType = db.inputs.condition().type();
            switch (conditionType.arrayDepth)
            {
            case 0:
                for (size_t idx = 0; idx < count; ++idx)
                {
                    const auto& ifTrue = db.inputs.ifTrue(idx);
                    const auto& ifFalse = db.inputs.ifFalse(idx);
                    const auto condition = db.inputs.condition(idx).template get<bool>();
                    auto& result = db.outputs.result(idx);
                    if (*condition)
                    {
                        result.resize(ifTrue.size());
                        std::copy(ifTrue.begin(), ifTrue.end(), result.begin());
                    }
                    else
                    {
                        result.resize(ifFalse.size());
                        std::copy(ifFalse.begin(), ifFalse.end(), result.begin());
                    }
                }
                return count;
            case 1:
                for (size_t idx = 0; idx < count; ++idx)
                {
                    const auto& ifTrue = db.inputs.ifTrue(idx);
                    const auto& ifFalse = db.inputs.ifFalse(idx);
                    const auto condition = db.inputs.condition(idx).template get<bool[]>();
                    auto& result = db.outputs.result(idx);

                    if (condition.size() != ifTrue.size() || condition.size() != ifFalse.size())
                        throw ogn::compute::InputError("Unable to broadcast arrays of differing lengths: condition (" +
                                                       std::to_string(condition.size()) + ") != ifTrue (" +
                                                       std::to_string(ifTrue.size()) + ") != ifFalse (" +
                                                       std::to_string(ifFalse.size()) + ")");

                    result.resize(ifFalse.size());
                    std::copy(ifFalse.begin(), ifFalse.end(), result.begin());
                    for (size_t i = 0; i < condition.size(); i++)
                    {
                        if ((*condition)[i])
                            result[i] = ifTrue[i];
                    }
                }
                return count;
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

} // namespace nodes
} // namespace graph
} // namespace omni
