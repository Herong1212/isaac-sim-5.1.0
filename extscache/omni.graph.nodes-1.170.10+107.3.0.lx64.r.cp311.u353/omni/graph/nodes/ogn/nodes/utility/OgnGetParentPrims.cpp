// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetParentPrimsDatabase.h>
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetParentPrims
{
public:
    static size_t computeVectorized(OgnGetParentPrimsDatabase& db, size_t count)
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE

        for (size_t i = 0; i < count; i++)
        {
            const auto& prims = db.inputs.prims(i);
            auto& parentPaths = db.outputs.parentPrims(i);
            parentPaths.resize(prims.size());
            std::transform(prims.begin(), prims.end(), parentPaths.begin(),
                           [&](const auto& p) { return pathInterface->getParent(p); });
        }
        return count;
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
