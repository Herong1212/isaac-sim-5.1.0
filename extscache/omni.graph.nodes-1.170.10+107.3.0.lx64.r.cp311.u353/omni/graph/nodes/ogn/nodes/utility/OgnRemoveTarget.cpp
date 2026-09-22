// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnRemoveTargetDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "ArrayCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnRemoveTarget
{
public:
    static size_t computeVectorized(OgnRemoveTargetDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& targets = db.inputs.targets(idx);
                auto& outTargets = db.outputs.targets(idx);

                if (!targets.empty())
                {
                    size_t const index = tryWrapIndex(db.inputs.index(idx), targets.size());
                    outTargets.resize(targets.size() - 1);
                    std::copy(targets.begin(), targets.begin() + index, outTargets.begin());
                    std::copy(targets.begin() + index + 1, targets.end(), outTargets.begin() + index);
                }
                else
                    outTargets.resize(0);
            }
            return count;
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
