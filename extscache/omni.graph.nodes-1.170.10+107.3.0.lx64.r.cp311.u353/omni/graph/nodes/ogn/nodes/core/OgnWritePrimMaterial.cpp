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

#include <omni/fabric/FabricUSD.h>
#include "OgnWritePrimMaterialDatabase.h"
#include "CoverageUtils.h"
#include "LayerIdentifierResolver.h"

using namespace omni::fabric;

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnWritePrimMaterial
{
    PXR_NS::UsdEditTarget m_editTarget;

public:
    static bool compute(OgnWritePrimMaterialDatabase& db)
    {
        // Find our stage
        NodeObj nodeObj = db.abi_node();
        const GraphContextObj& context = db.abi_context();
        auto& state = db.perInstanceState<OgnWritePrimMaterial>();

        long stageId = context.iContext->getStageId(context);
        PXR_NS::UsdStagePtr stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
        FIREWALL_RET_ERROR(db, !stage, false, "Could not find USD stage %ld", stageId); // LCOV_EXCL_LINE

        PXR_NS::SdfPath sdfPath;
        if (db.inputs.prim().size() == 0)
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
            if (db.inputs.prim().size() > 1)
                db.logWarning("Only one prim target is supported, the rest will be ignored");

            sdfPath = omni::fabric::toSdfPath(db.inputs.prim()[0]);
        }

        PXR_NS::UsdPrim prim = stage->GetPrimAtPath(sdfPath);
        if (!prim)
        {
            db.logError("Could not find USD prim");
            return false;
        }

        PXR_NS::SdfPath materialSdfPath;
        if (db.inputs.material().size() == 0)
        {
            const auto& materialPath = db.inputs.materialPath();
            if (!PXR_NS::SdfPath::IsValidPathString(materialPath))
            {
                db.logError("Invalid material path");
                return false;
            }
            materialSdfPath = PXR_NS::SdfPath(materialPath);
        }
        else
        {
            if (db.inputs.material().size() > 1)
                db.logWarning("Only one material target is supported, the rest will be ignored");

            materialSdfPath = omni::fabric::toSdfPath(db.inputs.material()[0]);
        }

        PXR_NS::UsdPrim materialPrim = stage->GetPrimAtPath(materialSdfPath);
        if (!materialPrim)
        {
            db.logError("Could not find USD material");
            return false;
        }

        auto layerIdentifier = db.inputs.layerIdentifier();
        if (db.state.layerIdentifier() != layerIdentifier)
        {
            state.m_editTarget = resolveLayerEditTarget(nodeObj, stage, inputs::layerIdentifier.m_token, layerIdentifier);
            db.state.layerIdentifier() = layerIdentifier;
        }

        PXR_NS::UsdEditTarget editTarget = stage->GetEditTarget();
        if (layerIdentifier != fabric::kUninitializedToken)
            editTarget = state.m_editTarget;

        pxr::UsdEditContext editContext(stage, editTarget);

        PXR_NS::UsdShadeMaterialBindingAPI materialBinding(prim);
        PXR_NS::UsdShadeMaterial material(materialPrim);
        if (!materialBinding.Bind(material))
        {
            db.logError("Could not bind USD material to USD prim");
            return false;
        }

        db.outputs.execOut() = kExecutionAttributeStateEnabled;

        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
