// SPDX-FileCopyrightText: Copyright (c) 2019-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// WARNING!
// The following code uses low-level ABI functionality and should not be copied for other purposes when such
// low level access is not required. Please use the OGN-generated API whenever possible.

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include "OgnWritePrimDatabase.h"

#define RETURN_TRUE_EXEC                                                                                               \
    {                                                                                                                  \
        db.outputs.execOut() = kExecutionAttributeStateEnabled;                                                        \
        return true;                                                                                                   \
    }

#include <omni/fabric/FabricUSD.h>

#include <omni/graph/core/IAttributeType.h>
#include <omni/graph/core/StringUtils.h>
#include <omni/kit/PythonInterOpHelper.h>
#include <omni/usd/UsdContext.h>

#include "PrimCommon.h"
#include "LayerIdentifierResolver.h"

using namespace omni::fabric;

constexpr size_t kNonDynamicAttributeCount = 3;

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnWritePrim
{

public:
    // ----------------------------------------------------------------------------
    // Called by OG when our prim attrib changes. We want to catch the case of changing the prim attribute interactively
    static void onValueChanged(const AttributeObj& attrObj, const void* userData)
    {
        NodeObj nodeObj = attrObj.iAttribute->getNode(attrObj);
        GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);
        GraphContextObj context = graphObj.iGraph->getDefaultGraphContext(graphObj);

        updateForPrim(
            context, nodeObj, true /* removeStale */, kAccordingToContextIndex, pxr::SdfPath::EmptyPath(), false);
    }

    // ----------------------------------------------------------------------------
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        AttributeObj attribObj = nodeObj.iNode->getAttributeByToken(nodeObj, inputs::prim.m_token);
        // Register for value changed - even when connected. Because it's possible that an OgnPrim
        // connection will be left dangling after clearing the relationship.
        attribObj.iAttribute->registerValueChangedCallback(attribObj, onValueChanged, true);
    }

    /** ----------------------------------------------------------------------------
     * Updates the dynamic attributes for the given node.
     * @param nodeObj The WritePrim node in question
     * @param removeStale true means we should remove any dynamic attributes which aren't for the current inputs:prim
     */
    static bool updateForPrim(GraphContextObj context,
                              NodeObj nodeObj,
                              bool removeStale,
                              InstanceIndex instanceIndex,
                              pxr::SdfPath targetPrimPath,
                              bool usdWriteBack,
                              NameToken layerIdentifier = fabric::kUninitializedToken)
    {
        const INode& iNode = *nodeObj.iNode;
        const IAttribute& iAttribute = *carb::getCachedInterface<IAttribute>();

        // Find our stage
        auto iFabricUsd = carb::getCachedInterface<IFabricUsd>();
        CARB_ASSERT(iFabricUsd);
        pxr::UsdStageRefPtr stage;
        omni::fabric::FabricId fabricId;
        std::tie(fabricId, stage) = getTargetFabricStage(context);
        if (fabricId == omni::fabric::kInvalidFabricId)
            return false;

        // Find the input prim via the relationship
        pxr::UsdPrim targetPrim;
        const char* thisPrimPathStr = iNode.getPrimPath(nodeObj);
        pxr::SdfPath thisPrimPath(thisPrimPathStr);

        {
            // Read the path from the relationship input on this compute node
            const pxr::UsdPrim thisPrim = stage->GetPrimAtPath(thisPrimPath);
            if (!thisPrim.IsValid())
            {
                CARB_LOG_ERROR("ReadPrim requires USD backing.");
                return false;
            }

            if (!targetPrimPath.IsEmpty())
            {
                targetPrim = stage->GetPrimAtPath(targetPrimPath);
                if (!targetPrim)
                {
                    CARB_LOG_ERROR_ONCE("Could not find specified prim at path %s", targetPrimPath.GetText());
                    return false;
                }
            }
            else
            {
                // No input prim specified. This is ok, but we may have stale attributes. We rely on this function being
                // called with removeStale = true to do the clean up.
                if (!removeStale)
                    return true;

                // If we have more attributes than we get by default, we know there is at least one dynamic attribute to
                // be removed
                size_t numAttributes = iNode.getAttributeCount(nodeObj);
                if (numAttributes > kNonDynamicAttributeCount)
                {
                    // Build a python script to disconnect and delete all dynamic attribs in one shot
                    static const char* cmdFmt =
                        "import omni.graph.core as og\n"
                        "og.remove_attributes_if(\"%s\", lambda a: a.is_dynamic() and og.is_attribute_plain_data(a))\n";
                    std::string fullCmd = formatString(cmdFmt, thisPrimPathStr);
                    omni::kit::PythonInterOpHelper::executeCommand(fullCmd.c_str());
                }
                // No need to do anything more since we have no prim specified
                return true;
            }
        }

        // -----------------------------------------------------------------------------------------
        // Update / Add dynamic attributes.

        std::vector<AttrNameAndType> attrsOfInterest;
        bool ok = addDynamicAttribs(
            targetPrim, iFabricUsd, fabricId, targetPrimPath, nodeObj, thisPrimPathStr, true, attrsOfInterest);
        if (!ok)
            return false;

        // We always have to copy our attribute data to the prim
        for (auto iter = attrsOfInterest.begin(); iter != attrsOfInterest.end(); iter++)
        {
            TokenC primAttrName = iter->name;

            // our attribute name will automatically include the "inputs:" prefix
            NameToken thisAttrName =
                iAttribute.ensurePortTypeInName(primAttrName, AttributePortType::kAttributePortType_Input, false);

            copyAttributeDataToPrim(context, asInt(targetPrimPath), primAttrName, nodeObj, thisAttrName, instanceIndex,
                                    false, usdWriteBack, layerIdentifier);
        }
        return true;
    }

    static bool compute(OgnWritePrimDatabase& db)
    {
        NodeObj nodeObj = db.abi_node();
        GraphContextObj context = db.abi_context();

        pxr::SdfPath sdfPath;
        const auto& prims = db.inputs.prim();
        if (prims.size() > 0)
        {
            sdfPath = omni::fabric::toSdfPath(prims[0]);
        }

        auto layerIdentifier = db.inputs.layerIdentifier();
        if (db.state.layerIdentifier() != layerIdentifier)
        {
            long stageId = context.iContext->getStageId(context);
            auto stage = pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
            if (layerIdentifier != fabric::kUninitializedToken)
                db.state.resolvedLayerIdentifier() =
                    resolveLayerIdentifier(nodeObj, stage, inputs::layerIdentifier.m_token, layerIdentifier);
            else
                db.state.resolvedLayerIdentifier() = fabric::kUninitializedToken;

            db.state.layerIdentifier() = layerIdentifier;
        }

        // Update attribs, but do not make any topological changes as this could destabilize the evaluation
        bool ok = updateForPrim(db.abi_context(), db.abi_node(), false /* removeStale */, db.getInstanceIndex(),
                                sdfPath, db.inputs.usdWriteBack(), db.state.resolvedLayerIdentifier());
        if (ok)
            RETURN_TRUE_EXEC
        return false;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
