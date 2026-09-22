// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnGetPrimPathDatabase.h>
#include "CoverageUtils.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetPrimPath
{
public:
    static size_t computeVectorized(OgnGetPrimPathDatabase& db, size_t count)
    {
        auto pathInterface = carb::getCachedInterface<omni::fabric::IPath>();
        FIREWALL_RET_ERROR(db, !pathInterface, 0, "Failed to initialize path interface"); // LCOV_EXCL_LINE
        auto tokenInterface = carb::getCachedInterface<omni::fabric::IToken>();
        FIREWALL_RET_ERROR(db, !tokenInterface, 0, "Failed to initialize token interface"); // LCOV_EXCL_LINE

        auto primPaths = db.outputs.primPath.vectorized(count);
        for (size_t i = 0; i < count; i++)
        {
            const auto& prims = db.inputs.prim(i);
            if (prims.size() > 0)
            {
                auto text = pathInterface->getText(prims[0]);
                db.outputs.path(i) = text;
                primPaths[i] = tokenInterface->getHandle(text);
            }
            else
            {
                db.outputs.path(i) = "";
                primPaths[i] = Token();
            }
        }
        return count;
    }
};

REGISTER_OGN_NODE();

} // nodes
} // graph
} // omni
