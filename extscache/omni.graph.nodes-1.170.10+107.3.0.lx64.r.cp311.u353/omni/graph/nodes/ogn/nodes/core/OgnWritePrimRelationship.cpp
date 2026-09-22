// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include <OgnWritePrimRelationshipDatabase.h>
#include "PrimCommon.h"
#include "CoverageUtils.h"
#include "LayerIdentifierResolver.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnWritePrimRelationship
{

public:
    // ----------------------------------------------------------------------------
    // Prefetch prim to fabric
    static void setup(GraphObj const& graphObj, OgnWritePrimRelationshipDatabase& db, size_t offset)
    {
        db.state.correctlySetup(offset) = false;

        TargetPath prim = db.inputs.prim.firstOrDefault(offset);
        NameToken name = db.inputs.name(offset);
        std::set<omni::fabric::TokenC> attributes = { name.token };
        prefetchPrim(graphObj, prim, attributes);

        db.state.correctlySetup(offset) = true;
        db.state.prim(offset).resize(1);
        db.state.prim(offset)[0] = prim;
        db.state.name(offset) = name;
    }

    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        NodeObj nodeObj{ attrObj.iAttribute->getNode(attrObj) };
        FIREWALL_RETURN(nodeObj.nodeHandle == kInvalidNodeHandle); // LCOV_EXCL_LINE

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        FIREWALL_RETURN(graphObj.graphHandle == kInvalidGraphHandle); // LCOV_EXCL_LINE

        OgnWritePrimRelationshipDatabase db(nodeObj);
        setup(graphObj, db, 0);
    }

    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        std::array<NameToken, 2> attribNames{ inputs::name.m_token, inputs::prim.m_token };
        for (auto const& attribName : attribNames)
        {
            AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, attribName);
            attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
        }
    }

    // ----------------------------------------------------------------------------
    static size_t computeVectorized(OgnWritePrimRelationshipDatabase& db, size_t count)
    {
        NodeObj nodeObj = db.abi_node();
        GraphContextObj context = db.abi_context();
        GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);
        long stageId = context.iContext->getStageId(context);
        auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));

        auto name = db.inputs.name.vectorized(count);
        auto usdWriteBack = db.inputs.usdWriteBack.vectorized(count);
        auto layerIdentifier = db.inputs.layerIdentifier.vectorized(count);
        auto correctlySetup = db.state.correctlySetup.vectorized(count);
        auto nameState = db.state.name.vectorized(count);
        auto layerIdentifierState = db.state.layerIdentifier.vectorized(count);
        auto resolvedLayerIdentifier = db.state.resolvedLayerIdentifier.vectorized(count);
        auto execOut = db.outputs.execOut.vectorized(count);

        for (size_t idx = 0; idx < count; ++idx)
        {
            TargetPath curPrim = db.inputs.prim.firstOrDefault(idx);
            if (!correctlySetup[idx] || db.state.prim(idx).size() == 0 || db.state.prim(idx)[0] != curPrim ||
                nameState[idx] != name[idx])
            {
                setup(graphObj, db, idx);
            }

            if (layerIdentifierState[idx] != layerIdentifier[idx])
            {
                if (layerIdentifier[idx] != fabric::kUninitializedToken)
                    resolvedLayerIdentifier[idx] = resolveLayerIdentifier(
                        db.abi_node({ idx }), stage, inputs::layerIdentifier.m_token, layerIdentifier[idx]);
                else
                    resolvedLayerIdentifier[idx] = fabric::kUninitializedToken;

                layerIdentifierState[idx] = layerIdentifier[idx];
            }

            if (correctlySetup[idx])
            {
                setRelationshipTargets(
                    context, curPrim, name[idx], db.inputs.value(idx), usdWriteBack[idx], resolvedLayerIdentifier[idx]);
                execOut[idx] = kExecutionAttributeStateEnabled;
            }
        }
        return count;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
