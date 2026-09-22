// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include "OgnAddPrimRelationshipDatabase.h"

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/common.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/relationship.h>
#include <pxr/usd/usdUtils/stageCache.h>
#include <omni/graph/core/PostUsdInclude.h>

#include <algorithm>

namespace omni
{
namespace graph
{
namespace action
{

class OgnAddPrimRelationship
{
public:
    // Add relationship data on a prim
    static bool compute(OgnAddPrimRelationshipDatabase& db)
    {
        const auto& path = db.inputs.path();
        const auto& target = db.inputs.target();
        auto& isSuccessful = db.outputs.isSuccessful();
        isSuccessful = false;

        if (!pxr::SdfPath::IsValidPathString(path) || !pxr::SdfPath::IsValidPathString(target))
        {
            return false;
        }

        const char* relName = db.tokenToString(db.inputs.name());
        if (!relName)
        {
            return false;
        }

        pxr::SdfPath primPath(path);
        pxr::SdfPath targetPath(target);

        long int stageId = db.abi_context().iContext->getStageId(db.abi_context());
        pxr::UsdStageRefPtr stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

        pxr::UsdPrim prim = stage->GetPrimAtPath(primPath);
        if (!prim)
        {
            return false;
        }

        if (pxr::UsdRelationship myRel = prim.CreateRelationship(pxr::TfToken(relName)))
        {
            isSuccessful = myRel.AddTarget(targetPath);
        }

        return isSuccessful;
    }
};

REGISTER_OGN_NODE()

}
}
}
