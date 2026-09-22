// SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnReadPrimRelationshipDatabase.h>
#include "PrimCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReadPrimRelationship
{

public:
    // ----------------------------------------------------------------------------
    // Prefetch prim to fabric
    static void setup(GraphObj const& graphObj, OgnReadPrimRelationshipDatabase& db, size_t offset)
    {
        db.state.correctlySetup(offset) = false;

        TargetPath prim = db.inputs.prim.firstOrDefault(offset);
        NameToken name = db.inputs.name(offset);
        std::set<omni::fabric::TokenC> attributes = { name.token };
        prefetchPrim(graphObj, prim, attributes);

        // The prefetch won't cache a relationship if it does not currently have any authored targets.
        // If the relationship didn't get cached then we need to ensure we try again next time.
        GraphContextObj context{ graphObj.iGraph->getDefaultGraphContext(graphObj) };
        auto iStageReaderWriter = carb::getCachedInterface<omni::fabric::IStageReaderWriter>();
        long stageId = context.iContext->getStageId(context);
        auto stageReaderWriterId = iStageReaderWriter->get(stageId);
        db.state.correctlySetup(offset) = iStageReaderWriter->attributeExists(stageReaderWriterId, prim, name.token);

        db.state.prim(offset).resize(1);
        db.state.prim(offset)[0] = prim;
        db.state.name(offset) = name;
    }

    // ----------------------------------------------------------------------------
    // Called by OG when attribute changes
    static void onValueChanged(AttributeObj const& attrObj, void const* userData)
    {
        NodeObj nodeObj{ attrObj.iAttribute->getNode(attrObj) };
        if (nodeObj.nodeHandle == kInvalidNodeHandle)
            return;

        GraphObj graphObj{ nodeObj.iNode->getGraph(nodeObj) };
        if (graphObj.graphHandle == kInvalidGraphHandle)
            return;

        OgnReadPrimRelationshipDatabase db(nodeObj);
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
    static size_t computeVectorized(OgnReadPrimRelationshipDatabase& db, size_t count)
    {
        NodeObj nodeObj = db.abi_node();
        GraphContextObj context = db.abi_context();
        GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);

        auto name = db.inputs.name.vectorized(count);
        auto correctlySetup = db.state.correctlySetup.vectorized(count);
        auto nameState = db.state.name.vectorized(count);

        for (size_t idx = 0; idx < count; ++idx)
        {
            TargetPath curPrim = db.inputs.prim.firstOrDefault(idx);
            if (!correctlySetup[idx] || db.state.prim(idx).size() == 0 || db.state.prim(idx)[0] != curPrim ||
                nameState[idx] != name[idx])
            {
                setup(graphObj, db, idx);
            }

            gsl::span<TargetPath> targets = getRelationshipTargets(context, curPrim, name[idx]);
            db.outputs.value(idx).resize(targets.size());
            for (size_t i = 0; i < targets.size(); i++)
            {
                db.outputs.value(idx)[i] = targets[i];
            }
        }
        return count;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
