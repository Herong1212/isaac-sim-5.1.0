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

#include "OgnReadPrimAttributesDatabase.h"
#include "ReadPrimCommon.h"

#include <omni/kit/commands/ICommandBridge.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReadPrimAttributes
{
    std::unordered_set<NameToken> m_added;

public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        // When inputs:bundle is not an optional input, the outputs need to be cleared when they are disconnected.
        AttributeObj inputBundleAttribObj =
            nodeObj.iNode->getAttributeByToken(nodeObj, OgnReadPrimAttributesAttributes::inputs::prim.m_token);

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
        auto outputTokens = { OgnReadPrimAttributesAttributes::outputs::primBundle.m_token };
        for (auto& outputToken : outputTokens)
        {
            BundleHandle outBundle = context.iContext->getOutputBundle(
                context, nodeObj.nodeContextHandle, outputToken, kAccordingToContextIndex);
            context.iContext->clearBundleContents(context, outBundle);
        }

        // Remove dynamic attributes
        BundleType empty;
        updateAttributes(context, nodeObj, empty, kAccordingToContextIndex);
    }

    // ----------------------------------------------------------------------------
    static PathC getPath(OgnReadPrimAttributesDatabase& db)
    {
        GraphContextObj contextObj = db.abi_context();
        std::string const primPathStr{ db.inputs.primPath() };
        NameToken primPath = contextObj.iToken->getHandle(primPathStr.c_str());

        return readPrimBundle_getPath(contextObj, db.abi_node(), OgnReadPrimAttributesAttributes::inputs::prim.m_token,
                                      db.inputs.usePath(), primPath, db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static bool writeToBundle(OgnReadPrimAttributesDatabase& db, PathC inputPath, bool force, pxr::UsdTimeCode const& time)
    {
        GraphContextObj contextObj = db.abi_context();
        NodeObj nodeObj = db.abi_node();

        std::string attrNamesStr{ db.inputs.attrNamesToImport() };
        NameToken attrNames = contextObj.iToken->getHandle(attrNamesStr.c_str());
        return readPrimBundle_writeToBundle(contextObj, nodeObj, inputPath, attrNames, db.outputs.primBundle(), force,
                                            false, time, db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static void clean(OgnReadPrimAttributesDatabase& db)
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
        OgnReadPrimAttributes& state = OgnReadPrimAttributesDatabase::sSharedState<OgnReadPrimAttributes>(nodeObj);
        omni::kit::commands::ICommandBridge::ScopedUndoGroup scopedUndoGroup;
        extractBundle_reflectBundleDynamicAttributes(nodeObj, contextObj, bundle, state.m_added, instIdx);
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnReadPrimAttributesDatabase& db)
    {
        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();

        // import by pattern
        bool inputChanged = false;

        // attribute filter changed
        std::string attrNamesToImport{ db.inputs.attrNamesToImport() };
        if (db.state.attrNamesToImport() != attrNamesToImport)
        {
            db.state.attrNamesToImport() = attrNamesToImport;
            inputChanged = true;
        }

        // compute
        bool result = readPrimBundle_compute<OgnReadPrimAttributes>(db, inputChanged);
        if (!result)
            return false;

        // update dynamic attributes
        BundleType outputBundle(context, db.outputs.primBundle().abi_bundleHandle());
        updateAttributes(context, nodeObj, outputBundle, db.getInstanceIndex());
        return outputBundle.isValid();
    }

    // ----------------------------------------------------------------------------
    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            if (oldVersion < 2)
            {
                return upgradeUsdTimeCodeInput(context, nodeObj);
            }
        }
        return false;
    }
};

REGISTER_OGN_NODE()

}
}
}
