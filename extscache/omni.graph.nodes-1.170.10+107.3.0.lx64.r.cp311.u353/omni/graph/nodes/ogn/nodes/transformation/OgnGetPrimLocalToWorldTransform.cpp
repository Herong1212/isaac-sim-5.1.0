// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/common.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/relationship.h>
#include <pxr/usd/usdGeom/xformCache.h>
#include <pxr/usd/usdUtils/stageCache.h>

#include <omni/graph/core/PostUsdInclude.h>

#include <omni/fabric/FabricUSD.h>

#include <OgnGetPrimLocalToWorldTransformDatabase.h>
#include <omni/math/linalg/SafeCast.h>

#include "PrimCommon.h"
// clang-format on

using namespace omni::fabric;

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnGetPrimLocalToWorldTransform
{
public:
    static bool compute(OgnGetPrimLocalToWorldTransformDatabase& db)
    {
        // Get interfaces
        auto& nodeObj = db.abi_node();
        const IPath& iPath = *db.abi_context().iPath;
        const INode& iNode = *nodeObj.iNode;

        bool usePath = db.inputs.usePath();

        long stageId = db.abi_context().iContext->getStageId(db.abi_context());
        auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
        if (!stage)
        {
            db.logWarning("Could not find USD stage %ld", stageId);
            return true;
        }

        // Find the target prim path one of 2 ways
        std::string destPrimPathStr;

        if (usePath)
        {
            // Use the absolute path
            NameToken primPath = db.inputs.primPath();
            destPrimPathStr = db.tokenToString(primPath);
            if (destPrimPathStr.empty())
            {
                db.logWarning("No target prim path specified");
                return true;
            }
        }
        else
        {
            // Read the path from the relationship input on this compute node
            const char* thisPrimPathStr = iNode.getPrimPath(nodeObj);

            // Find our stage
            long stageId = db.abi_context().iContext->getStageId(db.abi_context());
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
            if (!stage)
            {
                db.logWarning("Could not find USD stage %ld", stageId);
                return true;
            }
            // Find this prim
            const pxr::UsdPrim thisPrim = stage->GetPrimAtPath(pxr::SdfPath(thisPrimPathStr));
            if (!thisPrim.IsValid())
            {
                db.logError("GetPrimAttribute requires USD backing when 'usePath' is false.");
                return false;
            }
            try
            {
                // Find the relationship
                const pxr::SdfPath primPath = getRelationshipPrimPath(
                    db.abi_context(), nodeObj, OgnGetPrimLocalToWorldTransformAttributes::inputs::prim.m_token,
                    db.getInstanceIndex());
                destPrimPathStr = primPath.GetString();
            }
            catch (const std::exception& e)
            {
                db.logError(e.what());
                return false;
            }
        }

        // Retrieve a reference to the prim
        PathC destPath = iPath.getHandle(destPrimPathStr.c_str());
        pxr::UsdPrim prim = stage->GetPrimAtPath(pxr::SdfPath(toSdfPath(destPath)));

        if (!prim.IsValid())
        {
            return true;
        }

        pxr::UsdGeomXformCache xformCache;
        pxr::GfMatrix4d usdTransform = xformCache.GetLocalToWorldTransform(prim);
        db.outputs.localToWorldTransform() = omni::math::linalg::safeCastToOmni(usdTransform);

        return true;
    }
};

REGISTER_OGN_NODE()
}
}
}
