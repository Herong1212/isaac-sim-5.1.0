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
#include "UsdPCH.h"
// clang-format on

#include "OgnReadPrimMaterialDatabase.h"
#include <omni/fabric/FabricUSD.h>

#include "CoverageUtils.h"

using namespace omni::fabric;

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReadPrimMaterial
{

public:
    static bool compute(OgnReadPrimMaterialDatabase& db)
    {
        // Fetch from the target input by default, if it's not set,
        // use the prim path
        PXR_NS::SdfPath sdfPath;
        if (db.inputs.prim.size() == 0)
        {
            const auto& primPath = db.inputs.primPath();
            if (!PXR_NS::SdfPath::IsValidPathString(primPath))
            {
                db.logError("Invalid prim path");
                return false;
            }
            sdfPath = PXR_NS::SdfPath(primPath);
        }
        else
        {
            sdfPath = omni::fabric::toSdfPath(db.inputs.prim()[0]);
        }

        // Find our stage
        const GraphContextObj& context = db.abi_context();
        long stageId = context.iContext->getStageId(context);
        PXR_NS::UsdStagePtr stage = PXR_NS::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
        FIREWALL_RET_ERROR(db, !stage, false, "Could not find USD stage %ld", stageId); // LCOV_EXCL_LINE

        PXR_NS::UsdPrim prim = stage->GetPrimAtPath(sdfPath);
        if (!prim)
        {
            db.logError("Could not find USD prim at %s", sdfPath.GetText());
            return false;
        }

        PXR_NS::UsdShadeMaterialBindingAPI materialBinding(prim);
        PXR_NS::UsdShadeMaterial boundMat = materialBinding.ComputeBoundMaterial();

        if (!boundMat)
        {
            db.outputs.material() = "";
            db.outputs.materialPrim().resize(0);
            return true;
        }

        db.outputs.material() = boundMat.GetPath().GetString().c_str();
        db.outputs.materialPrim().resize(1);
        db.outputs.materialPrim()[0] = omni::fabric::asInt(boundMat.GetPath());

        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
