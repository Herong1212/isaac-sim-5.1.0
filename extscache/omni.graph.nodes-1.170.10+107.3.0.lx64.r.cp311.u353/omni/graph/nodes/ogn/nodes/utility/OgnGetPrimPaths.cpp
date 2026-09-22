// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetPrimPathsDatabase.h>
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetPrimPaths
{
public:
    static size_t computeVectorized(OgnGetPrimPathsDatabase& db, size_t count)
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        FIREWALL_RET_ERROR(db, !tokenInterface, 0, "Failed to initialize token interface"); // LCOV_EXCL_LINE

        for (size_t p = 0; p < count; p++)
        {
            const auto& prims = db.inputs.prims(p);
            auto& primPaths = db.outputs.primPaths(p);
            primPaths.resize(prims.size());
            for (size_t i = 0; i < prims.size(); i++)
            {
                primPaths[i] = tokenInterface->getHandle(pathInterface->getText(prims[i]));
            }
        }
        return count;
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
