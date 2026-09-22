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

#include "FindPrimsPathTracker.h"
#include "LayerIdentifierResolver.h"
#include "OgnWritePrimsV2Database.h"
#include "PathUtils.h"
#include "WritePrimCommon.h"

namespace omni
{
namespace graph
{
namespace nodes
{

class OgnWritePrimsV2
{
    // Cache the contextObj and nodeObj for cleaning up CreatedObject in perInstanceState.
    GraphContextObj contextObj;
    NodeObj nodeObj;

    // tracker group to keep track of what objects are CREATED by this node
    // The information is computed every compute to generate diff to previous compute, so that removed objects can be
    // cleaned up from stage.
    CreatedObjectsTrackerGroup trackerGroup;

    // BundlePrimInfoMaps from previous compute. Entries are reused if in subsequent compute the bundle is not changed
    // and no force rebuild is performed
    // In scatterUnderTargets mode, there's only one entry that covers all connected bundles.
    // In writeToTargets mode, each connected bundle will have its own map.
    std::vector<BundlePrimInfoMap> prevBundlePrimInfoMaps;

    // Used for writeToTargets mode only. This is a cache of how many unique root paths are in each bundle. This is used
    // for path remapping in subsequence compute for those unchanged bundles.
    std::vector<size_t> prevUniqueRootPathsCounts;

    // number of previously connected prims bundle. If it is changed, it triggers export for newly added bundle and
    // potentially rebuild of prim information in old bundles
    size_t prevConnectedBundleCount = 0;

    PrimPathsState targetPrimPaths;

    static size_t getConnectedPrimCount(OgnWritePrimsV2Database& db)
    {
        GraphContextObj const& contextObj = db.abi_context();
        NodeObj const& nodeObj = db.abi_node();

        NodeContextHandle const nodeHandle = nodeObj.nodeContextHandle;
        NameToken const primsToken = inputs::primsBundle.token();
        return contextObj.iContext->getInputTargetCount(contextObj, nodeHandle, primsToken, db.getInstanceIndex());
    }

    //! Check if any of the targetPrim paths are descendants of any of the Root Prims paths in find/read prims.
    //! If any of the path is an descendant, then the output prim(s) can potentially mutate the input prims' states,
    //! creating a loop. This is undesirable and prohibited to prevent user errors.
    //!
    //! returns true if loop is detected.
    static bool detectFindPrimsPathsLoop(GraphContextObj const& context, NodeObj const& nodeObj, SpanOfPathC targetPrimPaths)
    {
        fabric::FabricId fabricId;
        std::tie(fabricId, std::ignore) = getTargetFabricStage(context);

        auto const rootPrimPaths = getRootPrimPathsSet(fabricId);
        if (rootPrimPaths.empty())
        {
            return false;
        }

        // AbsoluteRootPath has to be the smallest path in the set if exists
        // a quick test
        if (*rootPrimPaths.begin() == PXR_NS::SdfPath::AbsoluteRootPath())
        {
            ogn::OmniGraphDatabase::logError(
                nodeObj,
                "FindPrims/ReadPrims source contains absolute root path \"/\", writing to any target on the stage may mutate the input state. "
                "Please choose a different source root prim path for FindPrims/ReadPrims.");
            return true;
        }

        PXR_NS::SdfPathSet targetPrimPathsSet;
        std::transform(targetPrimPaths.begin(), targetPrimPaths.end(),
                       std::inserter(targetPrimPathsSet, targetPrimPathsSet.begin()),
                       [](fabric::PathC pathC) { return fabric::toSdfPath(pathC); });

        for (auto const& rootPrimPath : rootPrimPaths)
        {
            auto const lb = targetPrimPathsSet.lower_bound(rootPrimPath);
            // if a lower_bound in targetPrimPaths is a descendant of rootPrimPath, a loop could form
            if (lb != targetPrimPathsSet.end() && lb->HasPrefix(rootPrimPath))
            {
                ogn::OmniGraphDatabase::logError(
                    nodeObj,
                    "Target prim '%s' is a descendant of FindPrims/ReadPrims source '%s', writing to the target may mutate the input state. Please choose a different target",
                    lb->GetText(), rootPrimPath.GetText());
                return true;
            }
        }

        return false;
    }

    // Example behavior:
    // - Source PrimBundle(s) contains prim with sourcePrimPath /world/foo and /world/bar
    // - Target Prims are /target0 and /target1
    // - Each source prim will be scattered *under* *every* targets, with the target paths prefixing sourcePrimPath. The
    //   target prims themselves will not change.
    // - After export, you will have:
    //   /target0/world/foo  (from /world/foo)
    //   /target0/world/bar  (from /world/bar)
    //   /target1/world/foo  (from /world/foo)
    //   /target1/world/bar  (from /world/bar)
    static WritePrimResult scatterUnderTargets(OgnWritePrimsV2Database& db,
                                               GraphContextObj const& contextObj,
                                               NodeObj const& nodeObj,
                                               gsl::span<ConstBundleHandle> connectedBundleHandles,
                                               bool const inputChanged,
                                               PrimBundleChanges& bundleChanges,
                                               SpanOfPathC targetPrimPaths,
                                               bool const usdWriteBack,
                                               NameToken const& layerIdentifier,
                                               WritePrimMatchers const& matchers,
                                               CreatedObjectsTrackerGroup& trackerGroup,
                                               WritePrimDiagnostics& diagnostics)
    {
        auto result = WritePrimResult::None;
        auto& internalState = db.perInstanceState<OgnWritePrimsV2>();

        // a map to contain all valid bundle prims info from ALL connected bundles and descendant bundles.
        auto& bundlePrimInfoMaps = internalState.prevBundlePrimInfoMaps;
        bundlePrimInfoMaps.resize(1);
        auto& bundlePrimInfoMap = bundlePrimInfoMaps.back();

        bool anyBundleOrInputChanged = inputChanged;

        // When scatter under targets, the prims from ALL connected bundles are collected and sorted, collectively
        // exported under target prims. Thus any one of the bundle change can potentially affect other bundle's export.
        // Thus we check all connected bundle for changes and do a re-collect of prims to export.
        if (!anyBundleOrInputChanged)
        {
            if (internalState.prevConnectedBundleCount != connectedBundleHandles.size())
            {
                anyBundleOrInputChanged = true;
            }
            else
            {
                for (ConstBundleHandle const& bundleHandle : connectedBundleHandles)
                {
                    if (bundleChanges.abi_getChange(bundleHandle) != BundleChangeType::None)
                    {
                        anyBundleOrInputChanged = true;
                        break;
                    }
                }
            }
        }

        // If ANY input changed, the output target will be different. Rebuild everything.
        // If ANY bundle changed, rebuild bundlePrimInfoMap, since it's a collection of prims from all bundles.
        if (anyBundleOrInputChanged)
        {
            bundlePrimInfoMap.clear();

            for (ConstBundleHandle const& bundleHandle : connectedBundleHandles)
            {
                WritePrimResult const subResult =
                    collectPrimsFromBundleHierarchy(contextObj, nodeObj, diagnostics, bundleHandle, inputChanged,
                                                    bundleChanges, matchers, bundlePrimInfoMap);

                mergeWritePrimResult(result, subResult);
            }

            internalState.prevConnectedBundleCount = connectedBundleHandles.size();
        }

        std::unordered_set<ConstBundleHandle, ConstBundleHandleHash> unchangedBundleHandles;
        for (auto const& [_, info] : bundlePrimInfoMap)
        {
            CARB_UNUSED(_);
            if (!inputChanged && bundleChanges.abi_getChange(info.bundleHandle) == BundleChangeType::None)
            {
                // bundleHandle may have duplicates for different info object, collect them and process later.
                unchangedBundleHandles.insert(info.bundleHandle);
                continue;
            }

            for (auto const& targetPrefix : targetPrimPaths)
            {
                WritePrimResult const subResult = writePrimAndAttributes(
                    contextObj, nodeObj, diagnostics, info, usdWriteBack, layerIdentifier, targetPrefix,
                    fabric::asInt(PXR_NS::SdfPath::AbsoluteRootPath()), trackerGroup);

                mergeWritePrimResult(result, subResult);
            }
        }

        // for unchanged bundles, since the processing of this bundle will be skipped, we need to retain the record of
        // created object information from previous compute so that in the handleMissing* phase, the created objects in
        // previous compute won't be treated as missing and removed.
        for (auto const& bundleHandle : unchangedBundleHandles)
        {
            fabric::PathC const bundlePath = fabric::PathC(HandleInt(bundleHandle));
            trackerGroup.copyObjectCreatedInfoFromPrevCompute(bundlePath, usdWriteBack);
        }

        return result;
    }

    // Example behavior:
    // - Source PrimBundle(s) contains prim with sourcePrimPath /world/bar, /world/foo (always being sorted due to
    //   nondeterminism of child bundle order)
    // - Target Prims are /target0 and /target1
    // - Each source prim will be exported to each targets, The target prims will be directly written to.
    // - After export, you will have:
    //   /target0  (from /world/bar)
    //   /target1  (from /world/foo)
    //
    // Example behavior 2:
    // - Source PrimBundle(s) contains prim with sourcePrimPath /world/bar, /world/bar/foo, /world/foo (always being
    //   sorted due to nondeterminism of child bundle order)
    // - Target Prims are /target0, /target1
    // - Source prims that share the same prefix will be exported to the same target prim hierarchy.
    // - After export, you will have:
    //   /target0  (from /world/bar)
    //   /target0/foo  (from /world/bar/foo)
    //   /target1  (from /world/foo)
    // * For details, see "Path mapping logic" below
    static WritePrimResult writeToTargets(OgnWritePrimsV2Database& db,
                                          GraphContextObj const& contextObj,
                                          NodeObj const& nodeObj,
                                          gsl::span<ConstBundleHandle> connectedBundleHandles,
                                          bool const inputChanged,
                                          PrimBundleChanges& bundleChanges,
                                          SpanOfPathC targetPrimPaths,
                                          bool const usdWriteBack,
                                          NameToken const& layerIdentifier,
                                          WritePrimMatchers const& matchers,
                                          CreatedObjectsTrackerGroup& trackerGroup,
                                          WritePrimDiagnostics& diagnostics)
    {
        auto result = WritePrimResult::None;
        auto& internalState = db.perInstanceState<OgnWritePrimsV2>();

        auto& bundlePrimInfoMaps = internalState.prevBundlePrimInfoMaps;
        auto& prevUniqueRootPathsCounts = internalState.prevUniqueRootPathsCounts;
        bundlePrimInfoMaps.resize(connectedBundleHandles.size());
        prevUniqueRootPathsCounts.resize(connectedBundleHandles.size());
        internalState.prevConnectedBundleCount = connectedBundleHandles.size();

        size_t targetPrimIndex = 0;
        bool pathMappingChanged = false;
        std::unordered_set<ConstBundleHandle, ConstBundleHandleHash> unchangedBundleHandles;
        for (size_t i = 0; i < connectedBundleHandles.size(); i++)
        {
            bool forcedChange = inputChanged || pathMappingChanged;

            ConstBundleHandle& bundleHandle = connectedBundleHandles[i];

            // a map to contain all valid bundle prims info from ONE connected bundle and descendant bundles.
            BundlePrimInfoMap& bundlePrimInfoMap = bundlePrimInfoMaps[i];

            bool anyBundleOrInputChanged = forcedChange;
            if (!anyBundleOrInputChanged)
            {
                anyBundleOrInputChanged = bundleChanges.abi_getChange(bundleHandle) != BundleChangeType::None;
            }

            if (anyBundleOrInputChanged)
            {
                // Rebuild bundlePrimInfoMap for this bundle if bundle or input has changed.
                bundlePrimInfoMap.clear();

                WritePrimResult const subResult =
                    collectPrimsFromBundleHierarchy(contextObj, nodeObj, diagnostics, bundleHandle, forcedChange,
                                                    bundleChanges, matchers, bundlePrimInfoMap);

                mergeWritePrimResult(result, subResult);

                // remove the paths that are already prefixed by other paths.
                // similar to SdfPath::RemoveDescendentPaths, but BundlePrimInfoMap is already ordered so we don't have
                // to sort again
                PXR_NS::SdfPathVector uniqueRootPaths;
                uniqueRootPaths.reserve(bundlePrimInfoMap.size());
                for (auto const& entry : bundlePrimInfoMap)
                {
                    if (uniqueRootPaths.empty() || !entry.first.HasPrefix(uniqueRootPaths.back()))
                    {
                        uniqueRootPaths.push_back(entry.first);
                    }
                }

                if (prevUniqueRootPathsCounts[i] != uniqueRootPaths.size())
                {
                    prevUniqueRootPathsCounts[i] = uniqueRootPaths.size();

                    // if current bundle is dirty with a different unique root paths count, it can affect path mapping
                    // in subsequent bundles. In this case, we need to dirty ALL bundles following it, even if they did
                    // not change.
                    pathMappingChanged = true;
                }

                // Path mapping logic:
                // input prim bundle contains these sourcePrimPaths (guarantee sorted because bundlePrimInfoMap is an
                // *ordered* map):
                //   /foo
                //   /foo/bar
                //   /qux
                //
                // output prim targets are:
                //   /target0
                //   /target1
                //
                // We want to export the sourcePrimPath of the same prefix to the same target (i.e. each unique common
                // prefix will map to a target), so the exported targets will be:
                //   /foo is exported as /target0
                //   /foo/bar is exported as /target0/bar
                //   /qux is exported as /target1
                //
                // The logic here is that when /qux no longer shares the same prefix with /foo/bar, the target should be
                // moved from /target0 to target1

                // index to the currently mapped unique root prim path
                size_t rootIndex = 0;
                for (auto const& [sourcePrimPath, info] : bundlePrimInfoMap)
                {
                    // when the sourcePrimPath is no longer a descendant of current unique root, move it onto the next
                    // one
                    if (rootIndex < uniqueRootPaths.size() && !sourcePrimPath.HasPrefix(uniqueRootPaths[rootIndex]))
                    {
                        rootIndex++;

                        // each root index takes up a target prim index
                        targetPrimIndex++;
                    }

                    if (targetPrimIndex >= targetPrimPaths.size())
                    {
                        ogn::OmniGraphDatabase::logWarning(
                            nodeObj,
                            "Not enough 'prims' targets to write out all source prims. Skipping the rest of the prims");
                        break;
                    }

                    if (!forcedChange && bundleChanges.abi_getChange(info.bundleHandle) == BundleChangeType::None)
                    {
                        // bundleHandle may have duplicates for different info object, collect them and process later.
                        unchangedBundleHandles.insert(info.bundleHandle);
                    }
                    else
                    {
                        WritePrimResult const subResult =
                            writePrimAndAttributes(contextObj, nodeObj, diagnostics, info, usdWriteBack, layerIdentifier,
                                                   targetPrimPaths[(VecOfPathC::size_type)targetPrimIndex],
                                                   fabric::asInt(uniqueRootPaths[rootIndex]), trackerGroup);

                        mergeWritePrimResult(result, subResult);
                    }
                }

                // always increment targetPrimIndex when moving onto next bundle
                targetPrimIndex++;
            }
            else
            {
                // there should be no changes in the bundle if we reach here. Just skip all bundleHandles in info map.
                for (auto const& [sourcePrimPath, info] : bundlePrimInfoMap)
                {
                    CARB_UNUSED(sourcePrimPath);
                    unchangedBundleHandles.insert(info.bundleHandle);
                }
                targetPrimIndex += prevUniqueRootPathsCounts[i];
            }
        }

        // for unchanged bundles, since the processing of this bundle will be skipped, we need to retain the record of
        // created object information from previous compute so that in the handleMissing* phase, the created objects in
        // previous compute won't be treated as missing and removed.
        for (auto const& bundleHandle : unchangedBundleHandles)
        {
            fabric::PathC const bundlePath = fabric::PathC(HandleInt(bundleHandle));
            trackerGroup.copyObjectCreatedInfoFromPrevCompute(bundlePath, usdWriteBack);
        }

        return result;
    }

public:
    static bool compute(OgnWritePrimsV2Database& db)
    {
        auto result = WritePrimResult::None;

        auto& context = db.abi_context();
        auto& nodeObj = db.abi_node();

        auto& internalState = db.perInstanceState<OgnWritePrimsV2>();

        // cache context and node for node cleanup
        // When per-instance release callback is added in OM-85240, this should not be necessary
        internalState.contextObj = context;
        internalState.nodeObj = nodeObj;

        bool inputChanged = db.state.attrNamesToExport() != db.inputs.attrNamesToExport() ||
                            db.state.pathPattern() != db.inputs.pathPattern() ||
                            db.state.typePattern() != db.inputs.typePattern() ||
                            db.state.usdWriteBack() != db.inputs.usdWriteBack() ||
                            db.state.scatterUnderTargets() != db.inputs.scatterUnderTargets() ||
                            db.state.layerIdentifier() != db.inputs.layerIdentifier();

        db.state.attrNamesToExport() = db.inputs.attrNamesToExport();
        db.state.pathPattern() = db.inputs.pathPattern();
        db.state.typePattern() = db.inputs.typePattern();
        db.state.usdWriteBack() = db.inputs.usdWriteBack();
        db.state.scatterUnderTargets() = db.inputs.scatterUnderTargets();
        db.state.layerIdentifier() = db.inputs.layerIdentifier();

        VecOfPath const targetPrimPaths =
            getPathsFromInputRelationship(context, nodeObj, inputs::prims.token(), db.getInstanceIndex());

        SpanOfPathC const targetPrimPathSpan = toSpanOfPathC(targetPrimPaths);

        if (internalState.targetPrimPaths.changed(targetPrimPathSpan))
        {
            internalState.targetPrimPaths.store(targetPrimPathSpan);
            inputChanged = true;
        }

        auto primBundleChanges = db.inputs.primsBundle.changes();

        // primBundleChanges only reflect the changes in the first bundle at the time this code was written. So if
        // there's more than 1 connected bundle, this does not work correctly. When it supports multiple connected
        // bundles, enable the block below.
        // For now, check anyBundleChanged with primBundleChanges.abi_getChange(bundleHandle) on each bundle manually
        // below.
#if 0
        if (!primBundleChanges && !inputChanged)
        {
            return true;
        }
#endif
        bool anyBundleChanged = false;

        long stageId = context.iContext->getStageId(context);
        auto stage = PXR_NS::UsdUtilsStageCache::Get().Find(PXR_NS::UsdStageCache::Id::FromLongInt(stageId));

        auto resolvedLayerIdentifier =
            resolveLayerIdentifier(nodeObj, stage, inputs::layerIdentifier.m_token, db.inputs.layerIdentifier());

        // Since the bundle input allows multiple connections, we need to collect all of them
        size_t const connectedPrimCount = getConnectedPrimCount(db);

        // If any bundles are disconnected, we need to make sure they get cleaned up later
        // checking inside of primBundleChanges may not reveal such change.
        bool anyBundleDisconnected = connectedPrimCount < internalState.prevConnectedBundleCount;

        // Even when we have no connected prims, we still return true, because the node *did* compute, and execOut
        // attribute will be set.
        if (connectedPrimCount > 0)
        {
            auto handler = [&db, &result, targetPrimPathSpan, &internalState, &resolvedLayerIdentifier, inputChanged,
                            &primBundleChanges, &anyBundleChanged,
                            connectedPrimCount](gsl::span<ConstBundleHandle> connectedBundleHandles)
            {
                GraphContextObj const& contextObj = db.abi_context();
                NodeObj const& nodeObj = db.abi_node();

                NodeContextHandle const nodeHandle = nodeObj.nodeContextHandle;
                NameToken const primsToken = inputs::primsBundle.token();

                contextObj.iContext->getInputTargets(contextObj, nodeHandle, primsToken,
                                                     (omni::fabric::PathC*)(connectedBundleHandles.data()),
                                                     db.getInstanceIndex());

                for (auto const& bundleHandle : connectedBundleHandles)
                {
                    // abi_getChange *MUST* be called for every bundleHandle that needs dirty tracking to setup correct
                    // initial state, even if it's not used now.
                    anyBundleChanged |= primBundleChanges.abi_getChange(bundleHandle) != BundleChangeType::None;
                }

                if (!anyBundleChanged && !inputChanged)
                {
                    return;
                }

                if (detectFindPrimsPathsLoop(contextObj, nodeObj, targetPrimPathSpan))
                {
                    mergeWritePrimResult(result, WritePrimResult::Fail);

                    // do not proceed
                    return;
                }

                bool const usdWriteBack = db.inputs.usdWriteBack();
                ogn::const_string const attrPattern = db.inputs.attrNamesToExport();
                ogn::const_string const pathPattern = db.inputs.pathPattern();
                ogn::const_string const typePattern = db.inputs.typePattern();

                WritePrimMatchers const matchers{ attrPattern, pathPattern, typePattern };

                // Write back all bundles
                WritePrimDiagnostics diagnostics;

                [[maybe_unused]] auto writeResult = WritePrimResult::None;
                if (db.inputs.scatterUnderTargets())
                {
                    writeResult =
                        scatterUnderTargets(db, contextObj, nodeObj, connectedBundleHandles, inputChanged,
                                            primBundleChanges, targetPrimPathSpan, usdWriteBack,
                                            resolvedLayerIdentifier, matchers, internalState.trackerGroup, diagnostics);
                }
                else
                {
                    writeResult =
                        writeToTargets(db, contextObj, nodeObj, connectedBundleHandles, inputChanged, primBundleChanges,
                                       targetPrimPathSpan, usdWriteBack, resolvedLayerIdentifier, matchers,
                                       internalState.trackerGroup, diagnostics);
                }

                // Report skipped invalid bundles
                mergeWritePrimResult(result, diagnostics.report(contextObj, nodeObj));
            };

            withStackScopeBuffer<ConstBundleHandle>(connectedPrimCount, handler);
        }
        else
        {
            // prevConnectedBundleCount will be updated accordingly if connectedPrimCount > 0
            internalState.prevConnectedBundleCount = 0;
        }

        if (inputChanged || anyBundleDisconnected || anyBundleChanged)
        {
            internalState.trackerGroup.update(context, nodeObj, db.inputs.usdWriteBack());
        }

        auto const ok = result != WritePrimResult::Fail;
        if (ok)
        {
            db.outputs.execOut() = kExecutionAttributeStateEnabled;
        }

        return ok;
    }

    ~OgnWritePrimsV2()
    {
        // When the node is removed, this will cleanup all CreatedObjects
        // Since nothing is created before calling update, all previously created object will be removed.
        // Set usdWriteBack to true to force a usd clean up
        trackerGroup.update(contextObj, nodeObj, true);
    }
};

REGISTER_OGN_NODE()

} // namespace nodes
} // namespace graph
} // namespace omni
