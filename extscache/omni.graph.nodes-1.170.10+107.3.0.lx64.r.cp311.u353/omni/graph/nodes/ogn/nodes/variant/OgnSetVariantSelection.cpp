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

#include "PrimCommon.h"
#include "VariantCommon.h"
#include "LayerIdentifierResolver.h"

#include <OgnSetVariantSelectionDatabase.h>

namespace omni::graph::nodes
{
class OgnSetVariantSelection
{
    PXR_NS::UsdEditTarget m_editTarget;

public:
    static bool compute(OgnSetVariantSelectionDatabase& db)
    {
        try
        {
            pxr::UsdPrim prim = tryGetTargetPrim(db, db.inputs.prim(), "prim");

            pxr::UsdVariantSets variantSets = prim.GetVariantSets();
            auto variantSetName = db.tokenToString(db.inputs.variantSetName());
            pxr::UsdVariantSet variantSet = variantSets.GetVariantSet(variantSetName);
            auto variantName = db.tokenToString(db.inputs.variantName());

            NodeObj nodeObj = db.abi_node();
            GraphContextObj context = db.abi_context();

            auto& state = db.perInstanceState<OgnSetVariantSelection>();

            long stageId = context.iContext->getStageId(context);
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

            auto layerIdentifier = db.inputs.layerIdentifier();
            if (db.state.layerIdentifier() != layerIdentifier)
            {
                state.m_editTarget =
                    resolveLayerEditTarget(nodeObj, stage, inputs::layerIdentifier.m_token, layerIdentifier);
                db.state.layerIdentifier() = layerIdentifier;
            }

            PXR_NS::UsdEditTarget editTarget = stage->GetEditTarget();
            if (layerIdentifier != fabric::kUninitializedToken)
                editTarget = state.m_editTarget;

            pxr::UsdEditContext editContext(stage, editTarget);

            if (db.inputs.setVariant())
            {
                removeLocalOpinion(prim, variantSetName, variantName);
                bool success = variantSet.SetVariantSelection(variantName);
                if (!success)
                    throw warning(std::string("Failed to set variant selection for variant set ") + variantSetName +
                                  " to variant " + variantName); // LCOV_EXCL_LINE
            }
            else
            {
                setLocalOpinion(prim, variantSetName, variantName);
            }
            db.outputs.execOut() = kExecutionAttributeStateEnabled;
            return true;
        }
        catch (const warning& e)
        {
            db.logWarning(e.what());
        }
        // LCOV_EXCL_START
        catch (const std::exception& e)
        {
            db.logError(e.what());
        }
        // LCOV_EXCL_STOP

        return false;
    }
};

REGISTER_OGN_NODE()

} // namespace omni::graph::nodes
