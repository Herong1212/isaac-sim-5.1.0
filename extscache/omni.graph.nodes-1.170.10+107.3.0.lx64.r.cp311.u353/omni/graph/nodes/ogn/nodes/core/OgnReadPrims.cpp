// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

 ReadPrims is deprecated. Use ReadPrimsV2 instead.

 ReadPrimsV2 added a new inputs:prims as the root prims to perform findPrims operation (instead of always starting from
 stage root "/").
 It also removed inputs:useFindPrims. Instead, as long as input:pathPattern is non-empty, it acts as the on toggle in
 place of useFindPrims.
*/

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <carb/dictionary/DictionaryUtils.h>
#include <omni/fabric/FabricUSD.h>

#include <omni/kit/PythonInterOpHelper.h>

#include "OgnReadPrimsDatabase.h"
#include "PrimCommon.h"
#include "ReadPrimCommon.h"

namespace omni
{
namespace graph
{

namespace nodes
{

class OgnReadPrims
{
public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, const NodeObj& nodeObj)
    {
        ogn::OmniGraphDatabase::logWarning(nodeObj, "ReadPrims node is deprecated, use ReadPrimsV2 instead");

        // When inputs:bundle is not an optional input, the outputs need to be cleared when they are disconnected.
        AttributeObj inputBundleAttribObj =
            nodeObj.iNode->getAttributeByToken(nodeObj, OgnReadPrimsAttributes::inputs::prims.m_token);

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
        auto outputTokens = { OgnReadPrimsAttributes::outputs::primsBundle.m_token };
        for (auto& outputToken : outputTokens)
        {
            BundleHandle outBundle = context.iContext->getOutputBundle(
                context, nodeObj.nodeContextHandle, outputToken, kAccordingToContextIndex);
            context.iContext->clearBundleContents(context, outBundle);
        }
    }

    // ----------------------------------------------------------------------------
    static VecOfPath getMatchedPaths(OgnReadPrimsDatabase& db, VecOfPath const*)
    {
        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();

        if (db.inputs.useFindPrims())
        {
            pxr::UsdStageRefPtr stage;
            omni::fabric::FabricId fabricId;
            std::tie(fabricId, stage) = getTargetFabricStage(context);

            pxr::UsdPrim startPrim = stage->GetPseudoRoot();
            pxr::TfToken pathPattern{ std::string{ db.inputs.pathPattern() } };
            if (pathPattern.IsEmpty())
                return {};

            std::string typePatternStr{ db.inputs.typePattern() };
            pxr::TfToken typePattern{ typePatternStr };
            VecOfPath matchedPaths;
            findPrims_findMatching(matchedPaths, startPrim, true, nullptr, typePattern, {}, {}, {}, pathPattern, true);
            return matchedPaths;
        }

        return readPrimBundle_getPaths(
            context, nodeObj, OgnReadPrimsAttributes::inputs::prims.m_token, false, {}, db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static bool writeToBundle(OgnReadPrimsDatabase& db,
                              gsl::span<PathC const> inputPaths,
                              bool force,
                              pxr::UsdTimeCode const& time)
    {
        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();
        std::string attrNamesStr{ db.inputs.attrNamesToImport() };
        NameToken attrNames = db.abi_context().iToken->getHandle(attrNamesStr.c_str());
        return readPrimsBundle_writeToBundle(context, nodeObj, inputPaths, attrNames, db.outputs.primsBundle(), force,
                                             db.inputs.computeBoundingBox(), time, db.getInstanceIndex());
    }

    // ----------------------------------------------------------------------------
    static void clean(OgnReadPrimsDatabase& db)
    {
        db.outputs.primsBundle().clear();
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnReadPrimsDatabase& db)
    {
        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();

        // import by pattern
        bool inputChanged = db.state.useFindPrims() != db.inputs.useFindPrims() ||
                            db.state.pathPattern() != db.inputs.pathPattern() ||
                            db.state.typePattern() != db.inputs.typePattern();

        db.state.useFindPrims() = db.inputs.useFindPrims();
        db.state.pathPattern() = db.inputs.pathPattern();
        db.state.typePattern() = db.inputs.typePattern();

        // bounding box changed
        bool const computeBoundingBox = db.inputs.computeBoundingBox();
        if (db.state.computeBoundingBox() != computeBoundingBox)
        {
            db.state.computeBoundingBox() = computeBoundingBox;
            inputChanged = true;
        }

        // attribute filter changed
        std::string attrNamesToImport{ db.inputs.attrNamesToImport() };
        if (db.state.attrNamesToImport() != attrNamesToImport)
        {
            db.state.attrNamesToImport() = attrNamesToImport;
            inputChanged = true;
        }

        // applySkelBinding toggle changed
        bool const applySkelBinding = db.inputs.applySkelBinding();
        if (db.state.applySkelBinding() != applySkelBinding)
        {
            db.state.applySkelBinding() = applySkelBinding;
            inputChanged = true;
        }

        bool result = readPrimsBundle_compute<OgnReadPrims>(db, inputChanged);

        if (result && applySkelBinding)
        {
            ogn::BundleContents<ogn::kOgnOutput, ogn::kCpu>& outputBundle = db.outputs.primsBundle();

            result = readSkelBinding_compute(context, nodeObj, outputBundle, attrNamesToImport, inputChanged,
                                             computeBoundingBox, getTime(db)) &&
                     applySkelBinding_compute(context, outputBundle);
        }

        return result;
    }

    // ----------------------------------------------------------------------------
    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            if (oldVersion < 3)
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
