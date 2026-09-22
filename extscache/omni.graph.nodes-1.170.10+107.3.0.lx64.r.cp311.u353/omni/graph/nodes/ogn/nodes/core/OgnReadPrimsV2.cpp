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

#include <carb/dictionary/DictionaryUtils.h>

#include <omni/fabric/FabricUSD.h>
#include <omni/kit/PythonInterOpHelper.h>
#include <omni/graph/core/BundleWriteBlock.h>

#include "FindPrimsPathTracker.h"

#include "ReadPrimCommonV2.h"
#include "DebugUtils.h"
#include "PathUtils.h"

#include "OgnReadPrimsV2Database.h"
// clang-format on

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnReadPrimsV2
{
    fabric::FabricId m_fabricId;
    fabric::Token m_pathTrackerId;
    unstable::UsdPrimChangeTracker::Subscription m_changeTrackerSubscription;
    PrimPathsState m_inputPrimPaths;
    PrimPathsState m_primPaths;

    // Print debug stuff to the console?
#if 0
#    define debugPrintLn(nodeObj, fmt, ...) DebugHelper::printLn((nodeObj), (fmt), ##__VA_ARGS__)
#else
#    define debugPrintLn(nodeObj, fmt, ...) ((void)0)
#endif

    // ----------------------------------------------------------------------------
    // OGN currently doesn't offer per-instance initialize/release callbacks,
    // so we must create per-instance state on demand, during compute
    static OgnReadPrimsV2& ensurePerInstanceState(OgnReadPrimsV2Database& db)
    {
        auto& internalState = db.perInstanceState<OgnReadPrimsV2>();

        if (internalState.m_fabricId == fabric::kInvalidFabricId)
        {
            auto& context = db.abi_context();
            auto& nodeObj = db.abi_node();

            // Initialize per-instance internal state.
            std::tie(internalState.m_fabricId, std::ignore) = getTargetFabricStage(context);

            // Initialize path tracker
            IToken const& iToken = *carb::getCachedInterface<omni::fabric::IToken>();

            // Build a unique per-node-instance key for the path target.
            std::stringstream ss;
            ss << nodeObj.iNode->getPrimPath(nodeObj);

            auto const graphObj = nodeObj.iNode->getGraph(nodeObj);

            if (graphObj.iGraph->getInstanceCount(graphObj))
            {
                // For instances, append the graph target.
                ss << iToken.getText(db.getGraphTarget());
            }

            internalState.m_pathTrackerId = iToken.getHandle(PXR_NS::TfMakeValidIdentifier(ss.str()).c_str());

            unstable::UsdPrimChangeTracker::AnyTrackedPrimChangedCallback primChangedCallback = [nodeObj]()
            {
                // If any tracked prim changes, force this node to recompute.
                debugPrintLn(nodeObj, "Any tracked prim was changed in instance '%s' => requesting re-computation",
                             intToToken(nodeObj.iNode->getGraphInstanceID(nodeObj.nodeHandle, {}).id).GetText());

                nodeObj.iNode->requestCompute(nodeObj);
            };

            // Initialize prim change tracker
            if (internalState.m_changeTrackerSubscription.initialize(context))
            {
                internalState.m_changeTrackerSubscription.setTrackedPrimChangedCallback(std::move(primChangedCallback));
            }
            else
            {
                OgnReadPrimsV2Database::logError(nodeObj, "Failed to initialize USD prim change tracker!");
            }
        }

        return internalState;
    }

    // ----------------------------------------------------------------------------
    static void onInputBundleValueChanged(AttributeObj const& inputBundleAttribObj, void const* userData)
    {
        NodeObj const nodeObj = inputBundleAttribObj.iAttribute->getNode(inputBundleAttribObj);
        GraphObj const graphObj = nodeObj.iNode->getGraph(nodeObj);

        // If the graph is currently disabled then delay the update until the next compute.
        // Arguably this should be done at the message propagation layer, then this wouldn't be necessary.
        if (graphObj.iGraph->isDisabled(graphObj))
        {
            return;
        }

        // clear the output bundles
        GraphContextObj const context = graphObj.iGraph->getDefaultGraphContext(graphObj);
        auto const outputTokens = { OgnReadPrimsV2Attributes::outputs::primsBundle.m_token };
        for (auto& outputToken : outputTokens)
        {
            BundleHandle const outBundle = context.iContext->getOutputBundle(
                context, nodeObj.nodeContextHandle, outputToken, kAccordingToContextIndex);
            context.iContext->clearBundleContents(context, outBundle);
        }
    }

    // ----------------------------------------------------------------------------
    static VecOfPath getMatchedPaths(OgnReadPrimsV2Database const& db, VecOfPath const* primPaths)
    {
        auto& context = db.abi_context();

        VecOfPath matchedPaths;
        if (!db.inputs.pathPattern().empty())
        {
            PXR_NS::UsdStageRefPtr stage;
            std::tie(std::ignore, stage) = getTargetFabricStage(context);

            PXR_NS::TfToken const pathPattern{ std::string{ db.inputs.pathPattern() } };
            if (pathPattern.IsEmpty())
                return {};

            std::string const typePatternStr{ db.inputs.typePattern() };
            PXR_NS::TfToken const typePattern{ typePatternStr };

            if (!primPaths || primPaths->empty())
            {
                PXR_NS::UsdPrim const startPrim = stage->GetPseudoRoot();
                findPrims_findMatching(
                    matchedPaths, startPrim, true, nullptr, typePattern, {}, {}, {}, pathPattern, true, true);
            }
            else
            {
                PXR_NS::SdfPathVector consolidatedPaths;
                consolidatedPaths.reserve(primPaths->size());
                std::transform(primPaths->cbegin(), primPaths->cend(), std::back_inserter(consolidatedPaths),
                               [](fabric::PathC pathC) { return fabric::toSdfPath(pathC); });
                // There's no need to find prims in /foo/bar if /foo is already one of the search paths
                PXR_NS::SdfPath::RemoveDescendentPaths(&consolidatedPaths);

                for (auto const& path : consolidatedPaths)
                {
                    if (PXR_NS::UsdPrim startPrim = stage->GetPrimAtPath(path))
                    {
                        findPrims_findMatching(
                            matchedPaths, startPrim, true, nullptr, typePattern, {}, {}, {}, pathPattern, true, true);
                    }
                }
            }
        }
        else
        {
            matchedPaths = *primPaths;
        }

        return matchedPaths;
    }

    // ----------------------------------------------------------------------------
    static bool writeToBundle(OgnReadPrimsV2Database& db,
                              SpanOfPathC inputPaths,
                              bool forceFullUpdate,
                              bool enableChangeTracking,
                              pxr::UsdTimeCode const& time)
    {
        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();

        std::string const attrNamesStr{ db.inputs.attrNamesToImport() };
        NameToken const attrNames = context.iToken->getHandle(attrNamesStr.c_str());
        bool const computeBoundingBox = db.inputs.computeBoundingBox();
        auto& containerBundle = db.outputs.primsBundle();
        int const debugStamp = db.inputs._debugStamp();

        bool const timeSampling = pxr::UsdTimeCode::Default() != time;

        // Update or reset the USD prim change tracker.
        auto& subscription = db.perInstanceState<OgnReadPrimsV2>().m_changeTrackerSubscription;

        if (!subscription.isValid() || timeSampling || !enableChangeTracking)
        {
            debugPrintLn(nodeObj, "Doing full container bundle update (w/o change tracking)");

            // We don't do any change tracking when time sampling the prims, this has overhead for nothing.
            // TODO: We could detect that the prim doesn't have any time sampled attributes!
            subscription.reset();

            return readPrimsBundleV2_writeToBundle(context, nodeObj, inputPaths, attrNames, containerBundle,
                                                   forceFullUpdate, computeBoundingBox, time, db.getInstanceIndex(),
                                                   debugStamp);
        }

        // Update change tracking.
        // When doing a forced output update, we need to start change tracking now,
        // so we can get the changes in the next compute.
        // NOTE: We assume that `force` will be true when switching from animated to non-animate compute!
        unstable::UsdPrimChangeTracker::TrackOptions trackOptions;

        // TODO: We should make world matrices optional
        constexpr bool computeWorldMatrix = true;

        // NOTE: We output local bounding boxes, and these depend on the world matrix too.
        trackOptions.ancestors = computeBoundingBox || computeWorldMatrix;

        // When computing bounding boxes, we need to observe descendant changes.
        trackOptions.descendants = computeBoundingBox;

        auto const changedPrimPaths =
            forceFullUpdate ? subscription.track(inputPaths, trackOptions) : subscription.update();

        if (!forceFullUpdate &&
            readPrimsBundleV2_updateOutputBundle(context, nodeObj, changedPrimPaths, attrNames, containerBundle,
                                                 computeBoundingBox, time, db.getInstanceIndex(), debugStamp))
        {
            // Incremental update succeeded.
            return true;
        }

        // Full update
        debugPrintLn(nodeObj, "Doing full container bundle update (forced)");

        return readPrimsBundleV2_writeToBundle(context, nodeObj, inputPaths, attrNames, containerBundle, true,
                                               computeBoundingBox, time, db.getInstanceIndex(), debugStamp);
    }

    // ----------------------------------------------------------------------------
    static void clean(OgnReadPrimsV2Database& db)
    {
        db.outputs.primsBundle().clear();
        if (db.inputs.enableBundleChangeTracking())
        {
            db.outputs.primsBundle.changes().activate();
        }
        else
        {
            db.outputs.primsBundle.changes().deactivate();
        }
    }

    // ----------------------------------------------------------------------------
    void updatePathTracker(bool hasPathPattern, SpanOfPathC rootPrimPaths) const
    {
        if (hasPathPattern)
        {
            if (rootPrimPaths.empty())
            {
                PathC const rootPathArray[1] = { fabric::asInt(PXR_NS::SdfPath::AbsoluteRootPath()) };
                setFindPrimsRootPrimPaths(m_fabricId, m_pathTrackerId, rootPathArray);
            }
            else
            {
                setFindPrimsRootPrimPaths(m_fabricId, m_pathTrackerId, rootPrimPaths);
            }
        }
        else
        {
            setFindPrimsRootPrimPaths(m_fabricId, m_pathTrackerId, {});
        }
    }

public:
    // ----------------------------------------------------------------------------
    static void initialize(GraphContextObj const& context, NodeObj const& nodeObj)
    {
        // When inputs:bundle is not an optional input, the outputs need to be cleared when they are disconnected.
        AttributeObj const inputBundleAttribObj =
            nodeObj.iNode->getAttributeByToken(nodeObj, OgnReadPrimsV2Attributes::inputs::prims.m_token);

        inputBundleAttribObj.iAttribute->registerValueChangedCallback(
            inputBundleAttribObj, onInputBundleValueChanged, true);
    }

    // ----------------------------------------------------------------------------
    ~OgnReadPrimsV2()
    {
        removeFindPrimsRootPrimPathsEntry(m_fabricId, m_pathTrackerId);
    }

    // ----------------------------------------------------------------------------
    static bool compute(OgnReadPrimsV2Database& db)
    {
        auto& internalState = ensurePerInstanceState(db);

        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();

        auto const prevPathPattern = db.state.pathPattern();
        auto const& pathPattern = db.inputs.pathPattern();

        bool const pathPatternChanged = prevPathPattern != pathPattern;

        // import by pattern
        bool inputChanged = pathPatternChanged || db.state.typePattern() != db.inputs.typePattern();

        db.state.pathPattern() = pathPattern;
        db.state.typePattern() = db.inputs.typePattern();

        // primPaths changed
        // primPaths serves two different purposes.
        // - if pathPattern not empty, primPaths are used as the root prims to apply pattern matching on
        // - if pathPattern is empty, primPaths are the prims to be read directly from
        auto const primPaths = readPrimBundle_getPaths(
            context, nodeObj, OgnReadPrimsV2Attributes::inputs::prims.m_token, false, {}, db.getInstanceIndex());
        auto const primPathSpan = toSpanOfPathC(primPaths);

        bool const rootPrimPathsChanged = internalState.m_inputPrimPaths.changed(primPathSpan);
        if (rootPrimPathsChanged)
        {
            internalState.m_inputPrimPaths.store(primPathSpan);
            inputChanged = true;
        }

        // bounding box changed
        bool const computeBoundingBox = db.inputs.computeBoundingBox();
        if (db.state.computeBoundingBox() != computeBoundingBox)
        {
            db.state.computeBoundingBox() = computeBoundingBox;
            inputChanged = true;
        }

        // attribute filter changed
        std::string const attrNamesToImport{ db.inputs.attrNamesToImport() };
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

        // enableChangeTracking toggle changed
        bool const enableUsdChangeTracking = db.inputs.enableChangeTracking();
        if (db.state.enableChangeTracking() != enableUsdChangeTracking)
        {
            db.state.enableChangeTracking() = enableUsdChangeTracking;
            inputChanged = true;
        }

        bool const enableBundleChangeTracking = db.inputs.enableBundleChangeTracking();
        if (db.state.enableBundleChangeTracking() != enableBundleChangeTracking)
        {
            db.state.enableBundleChangeTracking() = enableBundleChangeTracking;
            inputChanged = true;
        }

        // root prim paths changed or path pattern changed to/from empty
        if (rootPrimPathsChanged || (pathPatternChanged && (pathPattern.empty() || prevPathPattern.empty())))
        {
            internalState.updatePathTracker(!pathPattern.empty(), primPathSpan);
        }

        // NOTE: we need to use UsdTimeCode to compare to current and previous time,
        // because unlike SdfTimeCode, UsdTimeCode correctly deals with Default (NaN) time.
        pxr::UsdTimeCode const time = getTime(db);
        if (time != db.state.usdTimecode())
        {
            // time changed
            inputChanged = true;
            db.state.usdTimecode() = pxr::SdfTimeCode(time.GetValue());
        }

        // matched paths changed
        VecOfPath const matchedPaths = getMatchedPaths(db, &primPaths);
        SpanOfPathC const matchedPathSpan = toSpanOfPathC(matchedPaths);

        if (internalState.m_primPaths.changed(matchedPathSpan))
        {
            internalState.m_primPaths.store(matchedPathSpan);
            inputChanged = true;
        }

        // clean this node only when something changed
        if (inputChanged)
        {
            clean(db);
        }

        // nothing to write
        if (matchedPaths.empty())
        {
            return false;
        }

        omni::graph::core::unstable::BundleWriteBlock const bundleWriteBlock{ db.abi_context() };

        // write the data
        bool outputChanged = writeToBundle(db, matchedPathSpan, inputChanged, enableUsdChangeTracking, time);

        if (applySkelBinding)
        {
            ogn::BundleContents<ogn::kOgnOutput, ogn::kCpu>& outputBundle = db.outputs.primsBundle();

            if (readSkelBinding_compute(
                    context, nodeObj, outputBundle, attrNamesToImport, inputChanged, computeBoundingBox, getTime(db)))
            {
                outputChanged |= applySkelBinding_compute(context, outputBundle);
            }
        }

        return outputChanged;
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
