// SPDX-FileCopyrightText: Copyright (c) 2019-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

 ReadPrim is deprecated and should not be used.

 First version of ReadPrim outputs 'Single Primitive in a Bundle'(SPiB) + Dynamic Attributes(DA).
 The successor ReadPrims outputs 'Multiple Primitives in a Bundle'(MPiB) with no dynamic attributes.
 This operator is kept for backward compatibility.
*/

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include "OgnReadPrimDatabase.h"
#include "PrimCommon.h"
#include "ReadPrimCommon.h"

#include <omni/kit/commands/ICommandBridge.h>

#include <carb/dictionary/DictionaryUtils.h>
#include <omni/fabric/FabricUSD.h>

#include <omni/kit/PythonInterOpHelper.h>

namespace omni
{
namespace graph
{

namespace nodes
{

class OgnReadPrim
{
    std::unordered_set<NameToken> m_added;

public:
    // ----------------------------------------------------------------------------
    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        char const* primNodePath = nodeObj.iNode->getPrimPath(nodeObj);
        CARB_LOG_WARN("ReadPrim node is deprecated: %s, use ReadPrimAttributes instead", primNodePath);

        // When inputs:bundle is not an optional input, the outputs need to be cleared when they are disconnected.
        AttributeObj inputBundleAttribObj =
            nodeObj.iNode->getAttributeByToken(nodeObj, OgnReadPrimAttributes::inputs::prim.m_token);

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
        auto outputTokens = { OgnReadPrimAttributes::outputs::primBundle.m_token };
        for (auto& outputToken : outputTokens)
        {
            BundleHandle outBundle = context.iContext->getOutputBundle(
                context, nodeObj.nodeContextHandle, outputToken, kAccordingToContextIndex);
            context.iContext->clearBundleContents(context, outBundle);
        }
    }

    // ----------------------------------------------------------------------------
    static PathC getPath(OgnReadPrimDatabase& db)
    {
        return readPrimBundle_getPath(db.abi_context(), db.abi_node(), OgnReadPrimAttributes::inputs::prim.m_token,
                                      false, omni::fabric::kUninitializedToken, db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static bool writeToBundle(OgnReadPrimDatabase& db, PathC inputPath, bool force, pxr::UsdTimeCode const& time)
    {
        return readPrimBundle_writeToBundle(db.abi_context(), db.abi_node(), inputPath, db.inputs.attrNamesToImport(),
                                            db.outputs.primBundle(), force, db.inputs.computeBoundingBox(), time,
                                            db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static void clean(OgnReadPrimDatabase& db)
    {
        db.outputs.primBundle().clear();

        // remove dynamic attributes
        BundleType empty;
        updateAttributes(db.abi_context(), db.abi_node(), empty, db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static void updateAttributes(GraphContextObj const& contextObj,
                                 NodeObj const& nodeObj,
                                 BundleType const& bundle,
                                 InstanceIndex instIdx)
    {
        OgnReadPrim& state = OgnReadPrimDatabase::sSharedState<OgnReadPrim>(nodeObj);
        omni::kit::commands::ICommandBridge::ScopedUndoGroup scopedUndoGroup;
        extractBundle_reflectBundleDynamicAttributes(nodeObj, contextObj, bundle, state.m_added, instIdx);
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnReadPrimDatabase& db)
    {
        // import by pattern
        bool inputChanged = false;

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

        // compute
        bool result = readPrimBundle_compute<OgnReadPrim>(db, inputChanged);
        if (!result)
            return false;

        // update dynamic attributes
        BundleType outputBundle(db.abi_context(), db.outputs.primBundle().abi_bundleHandle());
        updateAttributes(db.abi_context(), db.abi_node(), outputBundle, db.getInstanceIndex());
        return outputBundle.isValid();
    }

    static bool updateNodeVersion(GraphContextObj const& context, NodeObj const& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            bool upgraded = false;
            if (oldVersion < 6)
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
            if (oldVersion < 8)
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
