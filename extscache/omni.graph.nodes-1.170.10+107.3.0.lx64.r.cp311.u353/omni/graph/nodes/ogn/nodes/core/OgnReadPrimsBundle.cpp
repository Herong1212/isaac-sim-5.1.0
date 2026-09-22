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

#include <omni/graph/core/PreUsdInclude.h>
#include <omni/usd/UsdContext.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/bboxCache.h>
#include <omni/graph/core/PostUsdInclude.h>
// clang-format on

#include "OgnReadPrimsBundleDatabase.h"
#include "PrimCommon.h"
#include "ReadPrimCommon.h"


namespace omni
{
namespace graph
{
namespace nodes
{

/************************************************************************/
/*                                                                      */
/************************************************************************/
class OgnReadPrimsBundle
{
public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        // When inputs:bundle is not an optional input, the outputs need to be cleared when they are disconnected.
        AttributeObj inputBundleAttribObj =
            nodeObj.iNode->getAttributeByToken(nodeObj, OgnReadPrimsBundleAttributes::inputs::prims.m_token);

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
        auto outputTokens = { OgnReadPrimsBundleAttributes::outputs::primsBundle.m_token };
        for (auto& outputToken : outputTokens)
        {
            BundleHandle outBundle = context.iContext->getOutputBundle(
                context, nodeObj.nodeContextHandle, outputToken, kAccordingToContextIndex);
            context.iContext->clearBundleContents(context, outBundle);
        }
    }

    // ----------------------------------------------------------------------------
    static VecOfPath getMatchedPaths(OgnReadPrimsBundleDatabase& db, VecOfPath const*)
    {
        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();
        return readPrimBundle_getPaths(context, nodeObj, OgnReadPrimsBundleAttributes::inputs::prims.m_token,
                                       db.inputs.usePaths(), db.inputs.primPaths(), db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static bool writeToBundle(OgnReadPrimsBundleDatabase& db,
                              gsl::span<PathC const> inputPaths,
                              bool force,
                              pxr::UsdTimeCode const& time)
    {
        std::string attrNamesStr{ db.inputs.attrNamesToImport() };
        NameToken attrNames = db.abi_context().iToken->getHandle(attrNamesStr.c_str());
        return readPrimsBundle_writeToBundle(db.abi_context(), db.abi_node(), inputPaths, attrNames,
                                             db.outputs.primsBundle(), force, false, time, db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static void clean(OgnReadPrimsBundleDatabase& db)
    {
        db.outputs.primsBundle().clear();
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnReadPrimsBundleDatabase& db)
    {
        bool inputChanged = false;
        if (db.state.usePaths() != db.inputs.usePaths())
        {
            db.state.usePaths() = db.inputs.usePaths();
            inputChanged = true;
        }

        // attribute filter changed
        std::string attrNamesToImport{ db.inputs.attrNamesToImport() };
        if (db.state.attrNamesToImport() != attrNamesToImport)
        {
            db.state.attrNamesToImport() = attrNamesToImport;
            inputChanged = true;
        }

        return readPrimsBundle_compute<OgnReadPrimsBundle>(db, inputChanged);
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

} // namespace nodes
} // namespace graph
} // namespace omni
