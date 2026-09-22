// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#include "OgnExtractBundleDatabase.h"
#include "ReadPrimCommon.h"

#include <omni/fabric/FabricUSD.h>

#include <omni/kit/commands/ICommandBridge.h>

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnExtractBundle
{
private:
    std::unordered_set<NameToken> m_added;

public:
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        // When inputs:bundle is not an optional input, the outputs need to be cleared when they are disconnected.
        AttributeObj inputBundleAttribObj =
            nodeObj.iNode->getAttributeByToken(nodeObj, OgnExtractBundleAttributes::inputs::bundle.m_token);

        inputBundleAttribObj.iAttribute->registerValueChangedCallback(
            inputBundleAttribObj, onInputBundleValueChanged, true);
    }

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
        GraphContextObj context = graphObj.iGraph->getDefaultGraphContext(graphObj);
        cleanOutput(context, nodeObj, kAccordingToContextIndex);
    }

    static void cleanOutput(GraphContextObj const& contextObj, NodeObj const& nodeObj, InstanceIndex instanceIdx)
    {
        // clear the output bundles
        auto outputTokens = { OgnExtractBundleAttributes::outputs::passThrough.m_token };

        for (auto& outputToken : outputTokens)
        {
            BundleHandle outBundle =
                contextObj.iContext->getOutputBundle(contextObj, nodeObj.nodeContextHandle, outputToken, instanceIdx);
            contextObj.iContext->clearBundleContents(contextObj, outBundle);
        }

        // remove dynamic attributes
        BundleType empty;
        updateAttributes(contextObj, nodeObj, empty, instanceIdx);
    }

    static void updateAttributes(GraphContextObj const& contextObj,
                                 NodeObj const& nodeObj,
                                 BundleType const& bundle,
                                 InstanceIndex instIdx)
    {
        OgnExtractBundle& state = OgnExtractBundleDatabase::sSharedState<OgnExtractBundle>(nodeObj);
        omni::kit::commands::ICommandBridge::ScopedUndoGroup scopedUndoGroup;
        extractBundle_reflectBundleDynamicAttributes(nodeObj, contextObj, bundle, state.m_added, instIdx);
    }

    // Copies attributes from an input bundle to attributes directly on the node
    static bool compute(OgnExtractBundleDatabase& db)
    {
        auto& contextObj = db.abi_context();
        auto& nodeObj = db.abi_node();
        auto const& inputBundle = db.inputs.bundle();
        if (!inputBundle.isValid())
        {
            cleanOutput(contextObj, nodeObj, db.getInstanceIndex());
            return false;
        }

        // extract attributes directly from input bundle
        updateAttributes(contextObj, nodeObj, inputBundle, db.getInstanceIndex());
        db.outputs.passThrough() = inputBundle;
        return true;
    }
};

REGISTER_OGN_NODE()

} // nodes
} // graph
} // omni
