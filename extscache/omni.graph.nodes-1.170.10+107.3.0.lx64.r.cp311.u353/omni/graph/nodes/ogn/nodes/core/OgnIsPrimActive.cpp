// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// clang-format off
#include "OgnIsPrimActiveDatabase.h"

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usdUtils/stageCache.h>
#include <omni/graph/core/PostUsdInclude.h>
#include <omni/fabric/FabricUSD.h>
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnIsPrimActive
{
public:
    // ----------------------------------------------------------------------------
    static bool compute(OgnIsPrimActiveDatabase& db)
    {
        // At some point, only target input types will be supported, so at the time that the path input is deprecated,
        // also rename "primTarget" to "prim"
        auto const& primPath = db.inputs.prim();
        auto const& prim = db.inputs.primTarget();

        if (prim.size() > 0 || pxr::SdfPath::IsValidPathString(primPath))
        {
            // Find our stage
            const GraphContextObj& context = db.abi_context();
            long stageId = context.iContext->getStageId(context);
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
            if (!stage)
            {
                db.logError("Could not find USD stage %ld", stageId);
                return false;
            }
            pxr::UsdPrim targetPrim =
                stage->GetPrimAtPath(prim.size() == 0 ? pxr::SdfPath(primPath) : omni::fabric::toSdfPath(prim[0]));
            if (!targetPrim)
            {
                // Should this really be an error?? When prim path input is removed, might be worth changing this to
                // just a warning instead
                db.logError("Could not find prim \"%s\" in USD stage",
                            prim.size() == 0 ? primPath.data() : db.pathToString(prim[0]));
                db.outputs.active() = false;
                return false;
            }
            db.outputs.active() = targetPrim.IsActive();
        }
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
