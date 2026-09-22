// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnReplaceTargetsDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>

#include <algorithm>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReplaceTargets
{
public:
    static size_t computeVectorized(OgnReplaceTargetsDatabase& db, size_t count)
    {
        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& targets = db.inputs.targets(idx);
                const auto& replaceTargets = db.inputs.replaceTargets(idx);
                const auto& setTargets = db.inputs.setTargets(idx);
                auto& outTargets = db.outputs.targets(idx);

                if (!targets.empty())
                {
                    outTargets.resize(targets.size());
                    std::copy(targets.begin(), targets.end(), outTargets.begin());
                    // Replace - replace and set have targets
                    if (!replaceTargets.empty() & !setTargets.empty())
                    {
                        if (replaceTargets.size() != setTargets.size())
                            throw ogn::compute::InputError("Unable to broadcast arrays of differing lengths: " +
                                                           std::to_string(replaceTargets.size()) +
                                                           "!=" + std::to_string(setTargets.size()));

                        for (size_t i = 0; i < replaceTargets.size(); i++)
                            std::replace(outTargets.begin(), outTargets.end(), replaceTargets[i], setTargets[i]);
                    }
                    // Remove - replace has targets, set is empty
                    else if (!replaceTargets.empty() & setTargets.empty())
                    {
                        auto end = outTargets.end();
                        for (size_t i = 0; i < replaceTargets.size(); i++)
                            end = std::remove(outTargets.begin(), end, replaceTargets[i]);

                        size_t newSize = std::distance(outTargets.begin(), end);
                        outTargets.resize(newSize);
                    }
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
