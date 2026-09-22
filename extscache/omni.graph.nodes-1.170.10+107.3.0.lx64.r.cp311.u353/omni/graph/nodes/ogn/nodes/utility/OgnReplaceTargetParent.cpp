// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <OgnReplaceTargetParentDatabase.h>
#include <omni/graph/core/ogn/ComputeHelpers.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReplaceTargetParent
{
public:
    static size_t computeVectorized(OgnReplaceTargetParentDatabase& db, size_t count)
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE

        try
        {
            for (size_t idx = 0; idx < count; ++idx)
            {
                const auto& targets = db.inputs.targets(idx);
                const auto& oldParents = db.inputs.oldParent(idx);
                const auto& newParents = db.inputs.newParent(idx);
                auto& outTargets = db.outputs.targets(idx);

                if (!targets.empty())
                {
                    outTargets.resize(targets.size());
                    if (!oldParents.empty())
                    {
                        auto oldParent = usdrt::SdfPath(oldParents[0]);
                        usdrt::SdfPath newParent("/");
                        if (!newParents.empty())
                            newParent = usdrt::SdfPath(newParents[0]);

                        for (size_t i = 0; i < targets.size(); i++)
                        {
                            const auto replacedPath = usdrt::SdfPath(targets[i]).ReplacePrefix(oldParent, newParent);
                            pathInterface->addRef((omni::fabric::PathC)replacedPath); // refcount needs to be manually
                                                                                      // updated
                            outTargets[i] = (omni::fabric::PathC)replacedPath;
                        }
                    }
                    else
                        std::copy(targets.begin(), targets.end(), outTargets.begin());
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
