// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnInsertTargetsDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include "ArrayCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnInsertTargets
{
public:
    static size_t computeVectorized(OgnInsertTargetsDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& targets = db.inputs.targets(idx);
                const auto& insertTargets = db.inputs.insertTargets(idx);
                auto& outTargets = db.outputs.targets(idx);

                if (!targets.empty())
                {
                    if (!insertTargets.empty())
                    {
                        size_t const index = tryClampIndex(db.inputs.index(idx), targets.size());
                        outTargets.resize(targets.size() + insertTargets.size());
                        std::copy(targets.begin(), targets.begin() + index, outTargets.begin());
                        std::copy(insertTargets.begin(), insertTargets.end(), outTargets.begin() + index);
                        std::copy(
                            targets.begin() + index, targets.end(), outTargets.begin() + index + insertTargets.size());
                    }
                    else
                    {
                        outTargets.resize(targets.size());
                        std::copy(targets.begin(), targets.end(), outTargets.begin());
                    }
                }
                else
                {
                    if (!insertTargets.empty())
                    {
                        outTargets.resize(insertTargets.size());
                        std::copy(insertTargets.begin(), insertTargets.end(), outTargets.begin());
                    }
                    else
                        outTargets.resize(0);
                }
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
