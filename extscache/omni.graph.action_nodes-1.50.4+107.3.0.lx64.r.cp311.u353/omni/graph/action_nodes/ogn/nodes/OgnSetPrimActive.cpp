// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.


#include "OgnSetPrimActiveDatabase.h"
#include <omni/graph/action/IActionGraph.h>
#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usdUtils/stageCache.h>
#include <omni/graph/core/PostUsdInclude.h>
#include <omni/fabric/FabricUSD.h>

namespace omni
{
namespace graph
{
namespace action
{

class OgnSetPrimActive
{
public:
    // ----------------------------------------------------------------------------
    static bool compute(OgnSetPrimActiveDatabase& db)
    {
        PXR_NS::SdfPath sdfPath;
        if (db.inputs.primTarget().size() == 0)
        {
            const auto& primPath = db.inputs.prim();
            if (pxr::SdfPath::IsValidPathString(primPath))
            {
                sdfPath = pxr::SdfPath(primPath);
            }
            else
            {
                return true;
            }
        }
        else
        {
            if (db.inputs.primTarget().size() > 1)
                db.logWarning("Only one prim target is supported, the rest will be ignored");
            sdfPath = omni::fabric::toSdfPath(db.inputs.primTarget()[0]);
        }

        // Find our stage
        const GraphContextObj& context = db.abi_context();
        long stageId = context.iContext->getStageId(context);
        auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
        if (!stage)
        {
            db.logError("Could not find USD stage %ld", stageId);
            return false;
        }

        pxr::UsdPrim targetPrim = stage->GetPrimAtPath(sdfPath);
        if (!targetPrim)
        {
            db.logError("Could not find prim \"%s\" in USD stage", sdfPath.GetText());
            return false;
        }
        bool ok = targetPrim.SetActive(db.inputs.active());

        if (ok)
        {
            auto iActionGraph = getInterface();
            iActionGraph->setExecutionEnabled(outputs::execOut.token(), db.getInstanceIndex());
            return true;
        }
        db.logError("Failed to set %s active state", sdfPath.GetText());
        return false;
    }
};

REGISTER_OGN_NODE()

} // namespace action
} // namespace graph
} // namespace omni
