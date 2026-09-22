// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

/*
  _____   ______  _____   _____   ______  _____         _______  ______  _____
 |  __ \ |  ____||  __ \ |  __ \ |  ____|/ ____|    /\ |__   __||  ____||  __ \
 | |  | || |__   | |__) || |__) || |__  | |        /  \   | |   | |__   | |  | |
 | |  | ||  __|  |  ___/ |  _  / |  __| | |       / /\ \  | |   |  __|  | |  | |
 | |__| || |____ | |     | | \ \ | |____| |____  / ____ \ | |   | |____ | |__| |
 |_____/ |______||_|     |_|  \_\|______|\_____|/_/    \_\|_|   |______||_____/

 ReadPrimBundle is deprecated and should not be used.

 First version of ReadPrimBundle outputs 'Single Primitive in a Bundle'(SPiB).
 The successor ReadPrimsBundle outputs 'Multiple Primitives in a Bundle'(MPiB).
 This operator is kept for backward compatibility.
*/


// clang-format off
#include "UsdPCH.h"

#include <omni/graph/core/PreUsdInclude.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usd/prim.h>
#include <omni/graph/core/PostUsdInclude.h>
// clang-format on

#include "OgnReadPrimBundleDatabase.h"

#include <omni/fabric/FabricUSD.h>

#include "PrimCommon.h"
#include "ReadPrimCommon.h"

#include <omni/usd/UsdContext.h>

using namespace omni::fabric;

namespace omni
{
namespace graph
{
namespace nodes
{

/************************************************************************/
/*                                                                      */
/************************************************************************/
class OgnReadPrimBundle
{
public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        char const* primNodePath = nodeObj.iNode->getPrimPath(nodeObj);
        CARB_LOG_WARN("ReadPrimBundle node is deprecated: %s, use ReadPrims instead", primNodePath);

        // When inputs:bundle is not an optional input, the outputs need to be cleared when they are disconnected.
        AttributeObj inputBundleAttribObj =
            nodeObj.iNode->getAttributeByToken(nodeObj, OgnReadPrimBundleAttributes::inputs::prim.m_token);

        inputBundleAttribObj.iAttribute->registerValueChangedCallback(
            inputBundleAttribObj, onInputBundleValueChanged, true);
    }

    // ----------------------------------------------------------------------------
    static void onInputBundleValueChanged(AttributeObj const& inputBundleAttribObj, void const* userData)
    {
        NodeObj nodeObj = inputBundleAttribObj.iAttribute->getNode(inputBundleAttribObj);
        GraphObj graphObj = nodeObj.iNode->getGraph(nodeObj);

        // If the graph is currently disabled then delay the update until the next compute.
        // Arguably this should be done at the message propagation layer, then this wouldn't be necessary.
        if (graphObj.iGraph->isDisabled(graphObj))
        {
            return;
        }

        // clear the output bundles
        GraphContextObj context = graphObj.iGraph->getDefaultGraphContext(graphObj);
        auto outputTokens = { OgnReadPrimBundleAttributes::outputs::primBundle.m_token };
        for (auto& outputToken : outputTokens)
        {
            BundleHandle outBundle = context.iContext->getOutputBundle(
                context, nodeObj.nodeContextHandle, outputToken, kAccordingToContextIndex);
            context.iContext->clearBundleContents(context, outBundle);
        }
    }

    // ----------------------------------------------------------------------------
    static PathC getPath(OgnReadPrimBundleDatabase& db)
    {
        return readPrimBundle_getPath(db.abi_context(), db.abi_node(), OgnReadPrimBundleAttributes::inputs::prim.m_token,
                                      db.inputs.usePath(), db.inputs.primPath(), db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static bool writeToBundle(OgnReadPrimBundleDatabase& db, PathC inputPath, bool force, pxr::UsdTimeCode const& time)
    {
        return readPrimBundle_writeToBundle(db.abi_context(), db.abi_node(), inputPath, db.inputs.attrNamesToImport(),
                                            db.outputs.primBundle(), force, db.inputs.computeBoundingBox(), time,
                                            db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static void clean(OgnReadPrimBundleDatabase& db)
    {
        db.outputs.primBundle().clear();
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnReadPrimBundleDatabase& db)
    {
        bool inputChanged = false;
        if (db.state.usePath() != db.inputs.usePath())
        {
            db.state.usePath() = db.inputs.usePath();
            inputChanged = true;
        }

        // bounding box changed
        if (db.state.computeBoundingBox() != db.inputs.computeBoundingBox())
        {
            db.state.computeBoundingBox() = db.inputs.computeBoundingBox();
            inputChanged = true;
        }

        // attribute filter changed
        NameToken const attrNamesToImport = db.inputs.attrNamesToImport();
        if (db.state.attrNamesToImport() != attrNamesToImport.token)
        {
            db.state.attrNamesToImport() = attrNamesToImport.token;
            inputChanged = true;
        }

        return readPrimBundle_compute<OgnReadPrimBundle>(db, inputChanged);
    }

    static bool updateNodeVersion(GraphContextObj const& context, NodeObj const& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            bool upgraded = false;
            if (oldVersion < 4)
            {
                // backward compatibility: `inputs:attrNamesToImport`
                // Prior to this version `inputs:attrNamesToImport` attribute did not support wild cards.
                // The meaning of an empty string was to include all attributes. With the introduction of the wild cards
                // we need to convert an empty string to "*" in order to include all attributes.
                static Token const value{ "*" };
                if (nodeObj.iNode->getAttributeExists(nodeObj, "inputs:attrNamesToImport"))
                {
                    AttributeObj attr = nodeObj.iNode->getAttribute(nodeObj, "inputs:attrNamesToImport");
                    auto roHandle = attr.iAttribute->getAttributeDataHandle(attr, kAccordingToContextIndex);
                    Token const* roValue = getDataR<Token const>(context, roHandle);
                    if (roValue && roValue->getString().empty())
                    {
                        Token* rwValue = getDataW<Token>(
                            context, attr.iAttribute->getAttributeDataHandle(attr, kAccordingToContextIndex));
                        *rwValue = value;
                    }
                }
                else
                {
                    nodeObj.iNode->createAttribute(nodeObj, "inputs:attrNamesToImport", Type(BaseDataType::eToken),
                                                   &value, nullptr, kAttributePortType_Input,
                                                   kExtendedAttributeType_Regular, nullptr);
                }
                upgraded = true;
            }
            if (oldVersion < 6)
            {
                upgraded |= upgradeUsdTimeCodeInput(context, nodeObj);
            }
            return upgraded;
        }

        return false;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
