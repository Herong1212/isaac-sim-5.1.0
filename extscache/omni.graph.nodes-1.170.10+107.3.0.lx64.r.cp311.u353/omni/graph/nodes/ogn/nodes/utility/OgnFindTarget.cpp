// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnFindTargetDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

#include <algorithm>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnFindTarget
{
public:
    static size_t computeVectorized(OgnFindTargetDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& targets = db.inputs.targets(idx);
                const auto& searchTargets = db.inputs.searchTarget(idx);
                int foundIndex = -1;
                if (!targets.empty() && !searchTargets.empty())
                {
                    auto it = std::find(targets.begin(), targets.end(), searchTargets[0]);
                    if (it != targets.end())
                        foundIndex = static_cast<int>(it - targets.begin());
                }

                db.outputs.index(idx) = foundIndex;
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
