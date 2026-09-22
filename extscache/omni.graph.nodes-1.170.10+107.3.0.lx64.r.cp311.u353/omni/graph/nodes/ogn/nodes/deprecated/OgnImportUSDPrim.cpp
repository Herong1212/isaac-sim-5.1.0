// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnImportUSDPrimDatabase.h>

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <pxr/usd/usd/prim.h>
#include <pxr/usd/usdGeom/bboxCache.h>
#include <pxr/usd/usdGeom/xformCache.h>

#include "USDBundles.h"
#include "Transform.h"
#include "PrimCommon.h"
#include "AttributeNameMap.h"

#include <omni/graph/core/BundlePrims.h>
#include <omni/math/linalg/matrix.h>
#include <omni/math/linalg/vec.h>

#include <omni/fabric/FabricUSD.h>

#include <algorithm>
#include <limits>
#include <mutex>
#include <unordered_map>
#include <unordered_set>

using omni::graph::core::BundleAttributeInfo;
using omni::graph::core::BundlePrim;
using omni::graph::core::BundlePrims;
using omni::graph::nodes::AttributeNameMap;

namespace
{

// Info communicated between the pathChangedCallback and compute
struct PathChangedCallbackInfo
{
    GraphContextObj context;
    NodeObj node;

    bool changeOnAncestorChanged; // set by compute; affects callback behavior
    bool changeOnDescendantChanged; // set by compute; affects callback behavior

    // NOTE: This should be sorted and not contain duplicates.
    std::vector<omni::fabric::PathC> sortedPrevImportedPrimPaths; // populated in compute; affects callback
    std::vector<bool> changedPrimPaths; // populated in callback; affects compute
    std::vector<std::vector<omni::fabric::TokenC>> sortedPrevImportedAttrs; // populated in compute; affects callback
    std::vector<std::vector<bool>> changedAttrs; // populated in callback; affects compute

    std::mutex mutex;
};

pxr::TfHashMap<pxr::SdfValueTypeName, Type, pxr::TfHash> usdTypeToOGType;
std::unordered_map<NodeHandle, std::unique_ptr<PathChangedCallbackInfo>> s_nodeToCallbackInfo;
std::mutex s_callbackMutex;

} // namespace

class OgnImportUSDPrim
{
public:
    static void initializeType(const NodeTypeObj& nodeType)
    {
        const omni::fabric::IFabricUsd* iFabricUsd = carb::getFramework()->acquireInterface<omni::fabric::IFabricUsd>();
        size_t typeCount = iFabricUsd->getUsdTypeCount();
        std::vector<omni::fabric::TypeC> typeCs;
        typeCs.resize(typeCount);
        iFabricUsd->getAllUsdTypes(typeCs.data(), typeCount);
        for (auto typeC : typeCs)
        {
            pxr::SdfValueTypeName usdType = iFabricUsd->fabricTypetoUsdType(typeC);
            usdTypeToOGType[usdType] = Type(typeC);
        }
    }
    // This is called for each import node when USD prims are modified.
    static void pathChangedCallback(const omni::fabric::PathC* paths, const size_t numPaths, void* userData)
    {
        PathChangedCallbackInfo* info = (PathChangedCallbackInfo*)userData;
        CARB_ASSERT(info != nullptr);
        CARB_ASSERT(info->changedPrimPaths.size() == 0 ||
                    info->changedPrimPaths.size() == info->sortedPrevImportedPrimPaths.size());
        std::unique_lock<std::mutex> lock(info->mutex);

        if (info->sortedPrevImportedPrimPaths.size() == 0)
            return;

        const size_t prevImportedPrimCount = info->sortedPrevImportedPrimPaths.size();
        auto* const sortedPrevImportedPrimPathsBegin = info->sortedPrevImportedPrimPaths.data();
        auto* const sortedPrevImportedPrimPathsEnd = sortedPrevImportedPrimPathsBegin + prevImportedPrimCount;

        // If we need to be aware of changes to ancestors or descendants, we need to look at the actual
        // SdfPaths of the paths changed and the paths being imported.
        // Otherwise, we can skip this step and use the integer comparisons of PathC values below.
        if (info->changeOnAncestorChanged || info->changeOnDescendantChanged)
        {
            // TODO: this nested for loop may become a bottleneck in the future.
            // We may want to consider a better approach, like building an ordered set of the changed paths.
            for (auto it = sortedPrevImportedPrimPathsBegin; it != sortedPrevImportedPrimPathsEnd; ++it)
            {
                const pxr::SdfPath& importedPrimPath = omni::fabric::toSdfPath(*it);

                for (size_t i = 0; i < numPaths; ++i)
                {
                    const pxr::SdfPath& changedPrimPath = omni::fabric::toSdfPath(paths[i]).GetPrimPath();

                    if (info->changeOnAncestorChanged && importedPrimPath.HasPrefix(changedPrimPath))
                    {
                        if (info->changedPrimPaths.size() != prevImportedPrimCount)
                        {
                            info->changedPrimPaths.resize(prevImportedPrimCount, false);
                            info->changedAttrs.resize(prevImportedPrimCount);
                        }
                        const size_t primIndex = it - sortedPrevImportedPrimPathsBegin;

                        info->changedPrimPaths[primIndex] = true;
                        info->changedAttrs[primIndex].resize(0);

                        continue;
                    }

                    if (info->changeOnDescendantChanged && changedPrimPath.HasPrefix(importedPrimPath))
                    {
                        if (info->changedPrimPaths.size() != prevImportedPrimCount)
                        {
                            info->changedPrimPaths.resize(prevImportedPrimCount, false);
                            info->changedAttrs.resize(prevImportedPrimCount);
                        }
                        const size_t primIndex = it - sortedPrevImportedPrimPathsBegin;

                        info->changedPrimPaths[primIndex] = true;
                        info->changedAttrs[primIndex].resize(0);

                        continue;
                    }
                }
            }
        }

        // Check whether any of the changed paths were imported by this node,
        // and if so, flag them as changed.
        for (size_t i = 0; i < numPaths; ++i)
        {
            omni::fabric::PathC path = paths[i];

            // The provided paths can be individual attribute paths, so get the prim path, first.
            const pxr::SdfPath& sdfPath = omni::fabric::toSdfPath(path);
            const omni::fabric::PathC primPath = omni::fabric::asInt(sdfPath.GetPrimPath());
#if 0
            printf("Path \"%s\" modified\n", sdfPath.GetText());
            printf("Prim is \"%s\"\n", sdfPath.GetPrimPath().GetText());
            printf("Previously imported:\n");
            for (auto it = sortedPrevImportedPrimPathsBegin; it != sortedPrevImportedPrimPathsEnd; ++it)
            {
                printf("    \"%s\"\n", omni::fabric::toSdfPath(*it).GetText());
            }
#endif
            auto* lower = std::lower_bound(sortedPrevImportedPrimPathsBegin, sortedPrevImportedPrimPathsEnd, primPath);
            if (lower == sortedPrevImportedPrimPathsEnd || *lower != primPath)
                continue;
            size_t primIndex = lower - sortedPrevImportedPrimPathsBegin;

            // Defer resizing until one of the changed prims is actually one of the prims
            // imported by this node, since often, none of the changed prims were imported by this node.
            if (info->changedPrimPaths.size() != prevImportedPrimCount)
            {
                info->changedPrimPaths.resize(prevImportedPrimCount, false);
                info->changedAttrs.resize(prevImportedPrimCount);
            }

            omni::fabric::TokenC attributeName = omni::fabric::kUninitializedToken;
            // TODO: Should this use SdfPath::IsPrimPropertyPath() instead?
            if (sdfPath.IsPropertyPath() && !(info->changedPrimPaths[primIndex]))
            {
                // It's a path for a specific attribute, and the prim itself hasn't been marked changed,
                // so mark the attribute as having changed.
                attributeName = omni::fabric::asInt(sdfPath.GetNameToken());
                const auto& sortedPrevImportedAttrs = info->sortedPrevImportedAttrs[primIndex];
                auto& changedAttrs = info->changedAttrs[primIndex];
                const size_t attrCount = sortedPrevImportedAttrs.size();
                auto* const sortedPrevImportedAttrsBegin = sortedPrevImportedAttrs.data();
                auto* const sortedPrevImportedAttrsEnd = sortedPrevImportedAttrsBegin + attrCount;
                auto* lower = std::lower_bound(sortedPrevImportedAttrsBegin, sortedPrevImportedAttrsEnd, attributeName);
                if (lower == sortedPrevImportedAttrsEnd || *lower != attributeName)
                    continue;
                size_t attrIndex = lower - sortedPrevImportedAttrsBegin;

                // Defer resizing like above
                if (changedAttrs.size() != attrCount)
                {
                    changedAttrs.resize(attrCount, false);
                }
                changedAttrs[attrIndex] = true;
            }
            else
            {
                // It's a path to the prim, so mark the prim itself as having changed
                info->changedPrimPaths[primIndex] = true;

                // The attributes are assumed to have all potentially been changed,
                // so they don't need to be tracked individually.
                info->changedAttrs[primIndex].resize(0);
            }
        }
    }

    // FIXME: pathChangedCallback functions soft-deprecated for 105
    CARB_IGNOREWARNING_MSC_WITH_PUSH(4996)
    CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wdeprecated-declarations")

    static void initialize(const GraphContextObj& context, const NodeObj& node)
    {
        // TODO: Could this node exist in multiple contexts in the future, or can
        //       import nodes only exist in one?
        CARB_ASSERT(s_nodeToCallbackInfo.count(node.nodeHandle) == 0);

        PathChangedCallbackInfo* userData = new PathChangedCallbackInfo{ context, node, false, false };
        {
            std::unique_lock<std::mutex> lock(s_callbackMutex);
            s_nodeToCallbackInfo[node.nodeHandle].reset(userData);
        }
        node.iNode->registerPathChangedCallback(node, PathChangedCallback{ pathChangedCallback, userData });
    }
    static void release(const NodeObj& node)
    {
        PathChangedCallbackInfo* userData;
        {
            std::unique_lock<std::mutex> lock(s_callbackMutex);
            auto it = s_nodeToCallbackInfo.find(node.nodeHandle);
            // An entry for this node should have been added in the initialize function.
            CARB_ASSERT(it != s_nodeToCallbackInfo.end());
            if (it == s_nodeToCallbackInfo.end())
                return;

            userData = it->second.release();
            s_nodeToCallbackInfo.erase(it);
        }
        node.iNode->deregisterPathChangedCallback(node, PathChangedCallback{ pathChangedCallback, userData });
        delete userData;
    }

    CARB_IGNOREWARNING_GNUC_POP
    CARB_IGNOREWARNING_MSC_POP

    static bool compute(OgnImportUSDPrimDatabase& db)
    {
        db.logWarning(
            "ImportUsdPrim is deprecated and will be removed in a future release. Use the ReadPrim set of nodes instead.");

        auto& nodeObj = db.abi_node();
        auto& context = db.abi_context();

        const auto* const iContext = context.iContext;
        const auto* const iToken = context.iToken;
        const auto* const iBundle = context.iBundle;

        const bool optionsChanged = (db.state.prevUsdTimecode() != db.inputs.usdTimecode()) ||
                                    (db.state.prevKeepPrimsSeparate() != db.inputs.keepPrimsSeparate()) ||
                                    (db.state.prevImportAttributes() != db.inputs.importAttributes()) ||
                                    (db.state.prevApplyTransform() != db.inputs.applyTransform()) ||
                                    (db.state.prevComputeBoundingBox() != db.inputs.computeBoundingBox()) ||
                                    (db.state.prevImportPrimvarMetadata() != db.inputs.importPrimvarMetadata()) ||
                                    (db.state.prevImportTransform() != db.inputs.importTransform()) ||
                                    (db.state.prevImportPath() != db.inputs.importPath()) ||
                                    (db.state.prevImportTime() != db.inputs.importTime()) ||
                                    (db.state.prevTimeVaryingAttributes() != db.inputs.timeVaryingAttributes()) ||
                                    (db.state.prevApplySkelBinding() != db.inputs.applySkelBinding()) ||
                                    (db.state.prevRenameAttributes() != db.inputs.renameAttributes()) ||
                                    (db.state.prevInputAttrNames() != db.inputs.inputAttrNames()) ||
                                    (db.state.prevOutputAttrNames() != db.inputs.outputAttrNames()) ||
                                    (db.state.prevAttrNamesToImport() != db.inputs.attrNamesToImport());
        db.state.prevUsdTimecode() = db.inputs.usdTimecode();
        db.state.prevKeepPrimsSeparate() = db.inputs.keepPrimsSeparate();
        db.state.prevImportAttributes() = db.inputs.importAttributes();
        db.state.prevApplyTransform() = db.inputs.applyTransform();
        db.state.prevComputeBoundingBox() = db.inputs.computeBoundingBox();
        db.state.prevImportPrimvarMetadata() = db.inputs.importPrimvarMetadata();
        db.state.prevImportTransform() = db.inputs.importTransform();
        db.state.prevImportPath() = db.inputs.importPath();
        db.state.prevImportTime() = db.inputs.importTime();
        db.state.prevTimeVaryingAttributes() = db.inputs.timeVaryingAttributes();
        db.state.prevApplySkelBinding() = db.inputs.applySkelBinding();
        db.state.prevRenameAttributes() = db.inputs.renameAttributes();
        db.state.prevInputAttrNames() = db.inputs.inputAttrNames();
        db.state.prevOutputAttrNames() = db.inputs.outputAttrNames();
        db.state.prevAttrNamesToImport() = db.inputs.attrNamesToImport();

        pxr::UsdPrim thisPrim = omni::graph::nodes::getUsdPrimFromNode(context, nodeObj);
        if (!thisPrim.IsValid())
        {
            BundleHandle outputBundleHandle = db.outputs.output().abi_bundleHandle();
            iContext->clearBundleContents(context, outputBundleHandle);
            CARB_LOG_ERROR("In OgnImportUSDPrim node, the compute node requires a USD prim in order to access the stage.");
            return false;
        }
        auto stage = thisPrim.GetStage();

        // Since the objective is to import USD data that might not be in the context,
        // we use the USD API directly.  The objective of this node is to avoid needing to
        // use the USD API in every particle system node.
        const pxr::UsdRelationship relationship = thisPrim.GetRelationship(pxr::TfToken("inputs:prim"));
        pxr::SdfPathVector target_paths;
        relationship.GetTargets(&target_paths);
        pxr::SdfPathVector paths;
        for (const auto& path : target_paths)
        {
            const pxr::UsdPrim prim = stage->GetPrimAtPath(path);
            if (prim)
                paths.push_back(path);
        }
        size_t pathCount = paths.size();

        // attribute name map
        AttributeNameMap attributeNameMap{ db.inputs.importAttributes(), db.inputs.renameAttributes(),
                                           db.inputs.inputAttrNames(), db.inputs.outputAttrNames(),
                                           db.inputs.attrNamesToImport() };

        const double primTime = db.inputs.usdTimecode();
        const pxr::TfTokenVector purposes = { pxr::UsdGeomTokens->default_, pxr::UsdGeomTokens->proxy };
        const bool useExtentHints = true;

        pxr::UsdGeomXformCache xformCache(primTime);
        pxr::UsdGeomBBoxCache bboxCache(primTime, purposes, useExtentHints);

        const double attrTime = db.inputs.timeVaryingAttributes() ? primTime : pxr::UsdTimeCode::Default().GetValue();

        bool transformNeeded =
            db.inputs.importTransform() || (db.inputs.importAttributes() && db.inputs.applyTransform());
        bool nodeTransformChanged = false;
        matrix4d inverseNodeTransform;
        if (transformNeeded)
        {
            const pxr::GfMatrix4d nodeTransform = xformCache.GetLocalToWorldTransform(thisPrim);
            inverseNodeTransform = safeCastToOmni(nodeTransform).GetInverse();
            nodeTransformChanged = (inverseNodeTransform != db.state.prevInvNodeTransform());
            if (nodeTransformChanged)
                db.state.prevInvNodeTransform() = inverseNodeTransform;
        }
        else
        {
            db.state.prevTransforms().resize(0);
        }

        bool multiplePrimsSupported = db.inputs.keepPrimsSeparate();

        if (!multiplePrimsSupported && pathCount != 1)
        {
            BundleHandle outputBundleHandle = db.outputs.output().abi_bundleHandle();
            iContext->clearBundleContents(context, outputBundleHandle);
            if (pathCount > 1)
            {
                CARB_LOG_ERROR("In OgnImportUSDPrim node, there must be at most one entry in the input relationship.");
            }
            return false;
        }

        bool allPathsCompletelyChanged = true;
        std::vector<bool> pathsChanged;
        std::vector<bool> pathsCompletelyChanged;
        std::vector<std::vector<omni::fabric::TokenC>> sortedPrevImportedAttrs;
        std::vector<std::vector<bool>> changedAttrs;
        PathChangedCallbackInfo* pathsChangedInfo = nullptr;
        std::unique_lock<std::mutex> pathsChangedLock;
        if (multiplePrimsSupported)
        {
            {
                std::unique_lock<std::mutex> lock(s_callbackMutex);
                auto it = s_nodeToCallbackInfo.find(nodeObj.nodeHandle);
                // An entry for this node should have been added in the initialize function.
                CARB_ASSERT(it != s_nodeToCallbackInfo.end());
                if (it != s_nodeToCallbackInfo.end())
                {
                    pathsChangedInfo = it->second.get();
                    CARB_ASSERT(pathsChangedInfo != nullptr);
                }
                // NOTE: The node shouldn't be running when it gets initialized or deleted,
                //       so we don't need to keep the lock for the map locked.
            }
            if (pathsChangedInfo != nullptr)
            {
                // Lock this pathsChangedInfo, in case this node is running at the same time as the callback.
                pathsChangedLock = std::unique_lock<std::mutex>(pathsChangedInfo->mutex);
                auto& sortedPrevImportedPrimPaths = pathsChangedInfo->sortedPrevImportedPrimPaths;
                if (sortedPrevImportedPrimPaths.size() != 0)
                {
                    if (pathsChangedInfo->changedPrimPaths.size() == 0)
                    {
                        // No paths changed
                        allPathsCompletelyChanged = false;
                    }
                    else
                    {
                        // Check which paths changed
                        size_t completeChangeCount = 0;
                        for (size_t pathi = 0; pathi < paths.size(); ++pathi)
                        {
                            const omni::fabric::PathC path = omni::fabric::asInt(paths[pathi]);
                            // This should be a prim path, not an attribute path
                            // TODO: Should this use SdfPath::IsPrimPropertyPath() instead?
                            CARB_ASSERT(!omni::fabric::toSdfPath(path).IsPropertyPath());
                            auto it = std::lower_bound(
                                sortedPrevImportedPrimPaths.begin(), sortedPrevImportedPrimPaths.end(), path);
                            bool primChanged = it == sortedPrevImportedPrimPaths.end() || *it != path;
                            size_t primIndex;
                            if (!primChanged && pathsChangedInfo->changedPrimPaths.size() != 0)
                            {
                                primIndex = it - sortedPrevImportedPrimPaths.begin();
                                CARB_ASSERT(pathsChangedInfo->changedPrimPaths.size() ==
                                            sortedPrevImportedPrimPaths.size());
                                primChanged = pathsChangedInfo->changedPrimPaths[primIndex];
                            }
                            bool primCompletelyChanged = primChanged;
                            if (!primChanged)
                            {
                                // changedAttrs should be resized at the same time as changedPrimPaths.
                                CARB_ASSERT(pathsChangedInfo->changedAttrs.size() == sortedPrevImportedPrimPaths.size());
                                const auto& changedAttrs = pathsChangedInfo->changedAttrs[primIndex];
                                primChanged = (changedAttrs.size() != 0);
                            }
                            if (primChanged)
                            {
                                // This prim changed
                                if (pathsChanged.size() == 0)
                                {
                                    pathsChanged.resize(paths.size(), false);
                                }
                                pathsChanged[pathi] = true;
                                if (primCompletelyChanged)
                                {
                                    if (pathsCompletelyChanged.size() == 0)
                                    {
                                        pathsCompletelyChanged.resize(paths.size(), false);
                                    }
                                    pathsCompletelyChanged[pathi] = true;
                                    ++completeChangeCount;
                                }
                            }
                        }
                        allPathsCompletelyChanged = (completeChangeCount == paths.size());
                    }
                }

                // Empty changedPrimPaths, so that we're starting from no modifications for next time, the common case.
                pathsChangedInfo->changedPrimPaths.resize(0);

                // Keep old changedAttrs and sortedPrevImportedAttrs for use below.
                // NOTE: Don't need to reorder changedAttrs or sortedPrevImportedAttrs, since the
                //       prim indices can be determined by binary search (std::lower_bound) on
                //       sortedPrevImportedPrimPaths.  If the set of prims changed,
                //       allPathsCompletelyChanged will be true, in which case, these are discarded.
                // NOTE: Don't move sortedPrevImportedAttrs until we know we're not early-exiting.
                changedAttrs = std::move(pathsChangedInfo->changedAttrs);
                // sortedPrevImportedAttrs = std::move(pathsChangedInfo->sortedPrevImportedAttrs);


                // Set state of pathsChangedInfo for use in the next invocation of pathChangedCallback

                // If we are considering a prim's transform, we need to consider changes to the prim's ancestors
                pathsChangedInfo->changeOnAncestorChanged = transformNeeded;
                // If we are importing bounding box attributes, we need to consider changes to descendants
                // of any prim being imported.
                pathsChangedInfo->changeOnDescendantChanged = db.inputs.computeBoundingBox();

                // Copy the imported paths to sortedPrevImportedPaths, then sort and remove duplicates.
                sortedPrevImportedPrimPaths.resize(paths.size());
                for (size_t pathi = 0; pathi < paths.size(); ++pathi)
                {
#if 0
                    printf("Path \"%s\" imported\n", paths[pathi].GetText());
#endif
                    sortedPrevImportedPrimPaths[pathi] = omni::fabric::asInt(paths[pathi]);
                }
                std::sort(sortedPrevImportedPrimPaths.begin(), sortedPrevImportedPrimPaths.end());
                size_t newSize = std::unique(sortedPrevImportedPrimPaths.begin(), sortedPrevImportedPrimPaths.end()) -
                                 sortedPrevImportedPrimPaths.begin();
                sortedPrevImportedPrimPaths.resize(newSize);

                if (!allPathsCompletelyChanged)
                {
                    // Check whether the paths array is different from the previous paths array,
                    // since, for example, the order may have changed or some may have been removed,
                    // and this wouldn't be caught by the check above.
                    // In these cases, fall back to assuming everything changed, for simplicity.
                    auto& prevPaths = db.state.prevPaths();
                    if (paths.size() != prevPaths.size())
                    {
                        allPathsCompletelyChanged = true;
                    }
                    else
                    {
                        for (size_t pathi = 0; pathi < paths.size(); ++pathi)
                        {
                            if (omni::fabric::asInt(paths[pathi].GetToken()) != prevPaths[pathi])
                            {
                                allPathsCompletelyChanged = true;
                                break;
                            }
                        }
                    }
                }
            }
        }

        allPathsCompletelyChanged |= optionsChanged;
        const bool noPathsChanged = !allPathsCompletelyChanged && (pathsChanged.size() == 0);
        if (noPathsChanged)
        {
            // Nothing changed since the previous time, so return.
            return true;
        }

        if (pathsChangedInfo != nullptr)
        {
            // Don't move this until we know that we'll be importing again, so that the
            // array doesn't get emptied in the case where we skip re-importing.
            sortedPrevImportedAttrs = std::move(pathsChangedInfo->sortedPrevImportedAttrs);
        }

        // Don't request db.outputs.output() until it's needed, because the BundleContents::reset
        // function that it calls is fairly expensive.
        // TODO: Consider getting the prim handle a different way.
        BundleHandle outputBundleHandle = db.outputs.output().abi_bundleHandle();
        db.outputs.output.changes().activate();
        BundlePrims output(context, outputBundleHandle);
        if (allPathsCompletelyChanged)
        {
            output.clearContents();

            db.state.prevPaths().resize(paths.size());
            for (size_t pathi = 0; pathi < paths.size(); ++pathi)
            {
                db.state.prevPaths()[pathi] = omni::fabric::asInt(paths[pathi].GetToken());
            }

            // We might as well clear changedAttrs here, since everything changed.
            changedAttrs.resize(0);
            sortedPrevImportedAttrs.resize(0);
        }
        if (multiplePrimsSupported)
        {
            if (paths.size() > 0 && allPathsCompletelyChanged)
                output.addPrims(paths.size());
            if (db.inputs.importAttributes() && db.inputs.applyTransform() &&
                db.state.prevTransforms().size() != paths.size())
            {
                nodeTransformChanged = true;
                db.state.prevTransforms().resize(paths.size());
            }
        }

        std::vector<std::vector<NameToken>> fullImportedAttrs;
        if (pathsChangedInfo != nullptr)
            fullImportedAttrs.resize(paths.size());
        for (size_t pathi = 0; pathi < paths.size(); ++pathi)
        {
            if (pathi != 0 && !multiplePrimsSupported)
            {
                break;
            }

            const pxr::SdfPath& primPath = paths[pathi];
            const omni::fabric::PathC pathInt = omni::fabric::asInt(primPath);

            bool primChanged = allPathsCompletelyChanged || (pathi < pathsChanged.size() && pathsChanged[pathi]);

            const pxr::UsdPrim prim = stage->GetPrimAtPath(primPath);
            if (!prim)
            {
                if (multiplePrimsSupported)
                    output.clearContents();
                else
                {
                    // Detach before clearPrimContents, to avoid crashing trying to write
                    // to the bundle's dirty ID attribute.
                    output.detach();
                    iContext->clearBundleContents(context, outputBundleHandle);
                }
                CARB_LOG_ERROR(
                    "In OgnImportUSDPrim node, there must be a valid path to a prim in the input relationship.");
                return false;
            }

            bool primTransformChanged = false;
            matrix4d primToNodeTransform;
            if (transformNeeded)
            {
                const pxr::GfMatrix4d primTransform = xformCache.GetLocalToWorldTransform(prim);

                // NOTE: USD transformation order accepts row vectors and applies transforms left to right.
                primToNodeTransform = safeCastToOmni(primTransform) * inverseNodeTransform;

                if (db.inputs.importAttributes() && db.inputs.applyTransform())
                {
                    primTransformChanged =
                        (nodeTransformChanged || primToNodeTransform != db.state.prevTransforms()[pathi]);
                    db.state.prevTransforms()[pathi] = primToNodeTransform;
                }
            }

            if (!primChanged && !primTransformChanged)
            {
                // This prim didn't change, and its transform doesn't matter or didn't change,
                // so we can skip re-importing it.

                if (pathsChangedInfo != nullptr)
                {
                    // We still need to keep the array of imported attribute names.

                    const auto& sortedPrevImportedPrimPaths = pathsChangedInfo->sortedPrevImportedPrimPaths;
                    auto it = std::lower_bound(
                        sortedPrevImportedPrimPaths.begin(), sortedPrevImportedPrimPaths.end(), pathInt);
                    CARB_ASSERT(it != sortedPrevImportedPrimPaths.end() && *it == pathInt);

                    size_t sortedPrimIndex = it - sortedPrevImportedPrimPaths.begin();
                    fullImportedAttrs[sortedPrimIndex] = std::move(sortedPrevImportedAttrs[sortedPrimIndex]);
                }

                continue;
            }

            if (db.inputs.importAttributes())
            {
                // UsdSkel bindings are to be applied, some information is needed before
                // attributes are imported.
                UsdSkelData usdSkelData;
                if (db.inputs.applySkelBinding())
                {
                    computeUsdSkelData(
                        stage, prim, primTime, attrTime, transformNeeded ? &xformCache : nullptr, usdSkelData);

                    if (transformNeeded && usdSkelData.hasValidSkelPoints)
                    {
                        // If a mesh is skinned, its transform is ignored, and the transform
                        // actually comes from the skeleton.
                        // Recompute primToNodeTransform with the new primTransform.
                        primToNodeTransform = usdSkelData.primTransform * inverseNodeTransform;
                    }
                }

                TransformInfo transformInfo;
                if (db.inputs.applyTransform())
                {
                    transformInfo.init(primToNodeTransform);
                }

                size_t sortedPrimIndex = std::numeric_limits<size_t>::max();
                std::vector<NameToken>* importedAttrs = nullptr;
                BundlePrim* outputBundlePrim;
                if (multiplePrimsSupported)
                {
                    if (pathsChangedInfo != nullptr)
                    {
                        const auto& sortedPrevImportedPrimPaths = pathsChangedInfo->sortedPrevImportedPrimPaths;
                        auto it = std::lower_bound(
                            sortedPrevImportedPrimPaths.begin(), sortedPrevImportedPrimPaths.end(), pathInt);
                        CARB_ASSERT(it != sortedPrevImportedPrimPaths.end() && *it == pathInt);

                        sortedPrimIndex = it - sortedPrevImportedPrimPaths.begin();
                        importedAttrs = &fullImportedAttrs[sortedPrimIndex];
                    }

                    if (allPathsCompletelyChanged)
                    {
                        // This prim was already cleared above
                        outputBundlePrim = output.getPrim(pathi);
                    }
                    else if (sortedPrimIndex < pathsCompletelyChanged.size() && pathsCompletelyChanged[sortedPrimIndex])
                    {
                        // This prim changed completely, so clear it.
                        outputBundlePrim = output.getClearedPrim(pathi);
                    }
                    else
                    {
                        // This prim only changed partly, so go attribute by attribute.
                        outputBundlePrim = output.getPrim(pathi);
                    }
                }
                else
                {
                    outputBundlePrim = &output.getCommonAttrs();
                    if (!allPathsCompletelyChanged)
                    {
                        // We didn't clear the whole bundle above, so we have to clear this prim now.
                        outputBundlePrim->clearContents();
                    }
                }

                // import usd attributes
                for (auto& usdAttr : prim.GetAttributes())
                {
                    if (!usdAttr)
                        continue;

                    const Type type = usdTypeToOGType[usdAttr.GetTypeName()];

                    // Skip unsupported types
                    if (type.baseType == BaseDataType::eUnknown || type.baseType == BaseDataType::eAsset)
                        continue;

                    // Determine the output attribute name
                    const pxr::TfToken& inputNameTfToken = usdAttr.GetName();
                    const char* const inputNameText = inputNameTfToken.GetText();
                    const NameToken inputNameToken = omni::fabric::asInt(inputNameTfToken);

                    if (attributeNameMap.isNotSpecifiedName(inputNameToken))
                    {
                        continue;
                    }

                    if (importedAttrs != nullptr)
                    {
                        importedAttrs->push_back(inputNameToken);
                    }

                    NameToken outputNameToken = attributeNameMap.getName(inputNameToken);
                    BundleAttributeInfo* attr = outputBundlePrim->getAttr(outputNameToken);
                    if (attr != nullptr && attr->type() == type && attr->isAttributeData())
                    {
                        // Attribute already exists with the correct type, so check if it might have changed.
                        // If it's role is not eNone, it's potentially transforming, so consider it to be
                        // changed if the transform changed.
                        if (sortedPrimIndex < sortedPrevImportedAttrs.size() &&
                            (type.role == AttributeRole::eNone || !primTransformChanged))
                        {
                            const auto& sortedPrevAttrs = sortedPrevImportedAttrs[sortedPrimIndex];
                            // NOTE: Must use *input* name, since that's all that the callback receives.
                            auto it = std::lower_bound(sortedPrevAttrs.begin(), sortedPrevAttrs.end(), inputNameToken);
                            if (it != sortedPrevAttrs.end())
                            {
                                size_t attrIndex = it - sortedPrevAttrs.begin();
                                if (attrIndex >= changedAttrs[sortedPrimIndex].size() ||
                                    !changedAttrs[sortedPrimIndex][attrIndex])
                                {
                                    // This attribute was imported last time and it hasn't changed.
                                    continue;
                                }
                            }
                        }
                    }
                    else
                    {
                        attr = outputBundlePrim->addAttr(outputNameToken, type);
                    }
                    if (usdSkelData.hasValidSkelPoints && inputNameTfToken == pxr::UsdGeomTokens.Get()->points &&
                        type.baseType == BaseDataType::eFloat)
                    {
                        const vec3f* sourceData = usdSkelData.skelPointsArray.data();
                        attr->resize(usdSkelData.skelPointsArray.size());
                        vec3f* destData = attr->getData<vec3f>();
                        std::copy(sourceData, sourceData + usdSkelData.skelPointsArray.size(), destData);
                    }
                    else if (usdSkelData.hasValidSkelNormals && inputNameTfToken == pxr::UsdGeomTokens.Get()->normals &&
                             type.baseType == BaseDataType::eFloat)
                    {
                        const vec3f* sourceData = usdSkelData.skelNormalsArray.data();
                        attr->resize(usdSkelData.skelNormalsArray.size());
                        vec3f* destData = attr->getData<vec3f>();
                        std::copy(sourceData, sourceData + usdSkelData.skelNormalsArray.size(), destData);
                    }
                    else
                    {
                        importAttrFromUSD(*attr, usdAttr, attrTime);
                    }

                    if (db.inputs.importPrimvarMetadata())
                    {
                        NameToken interpolation =
                            getInterpolation(prim, usdAttr, inputNameText, usdSkelData.normalsChangedToVertex);
                        if (interpolation != omni::fabric::kUninitializedToken)
                            attr->setInterpolation(interpolation);
                    }

                    if (db.inputs.applyTransform())
                    {
                        transformAttr(context, attr->handle(), transformInfo);
                    }
                }

                // import usd relationships
                for (auto& usdRel : prim.GetRelationships())
                {
                    if (!usdRel)
                    {
                        continue;
                    }

                    // Determine relationship name
                    const pxr::TfToken& inputNameTfToken = usdRel.GetName();
                    const NameToken inputNameToken = omni::fabric::asInt(inputNameTfToken);

                    if (attributeNameMap.isNotSpecifiedName(inputNameToken))
                    {
                        continue;
                    }

                    pxr::SdfPathVector relTargets;
                    usdRel.GetTargets(&relTargets);

                    if (importedAttrs != nullptr)
                    {
                        importedAttrs->push_back(inputNameToken);
                    }

                    NameToken outputNameToken = attributeNameMap.getName(inputNameToken);
                    BundleAttributeInfo* attr = outputBundlePrim->getAttr(outputNameToken);

                    if (attr != nullptr && attr->isRelationshipData())
                    {
                        // Attribute already exists with the correct type, so check if it might have changed.
                        // If it's role is not eNone, it's potentially transforming, so consider it to be
                        // changed if the transform changed.
                        if (sortedPrimIndex < sortedPrevImportedAttrs.size() &&
                            (attr->type().role == AttributeRole::eNone))
                        {
                            const auto& sortedPrevAttrs = sortedPrevImportedAttrs[sortedPrimIndex];
                            // NOTE: Must use *input* name, since that's all that the callback receives.
                            auto it = std::lower_bound(sortedPrevAttrs.begin(), sortedPrevAttrs.end(), inputNameToken);
                            if (it != sortedPrevAttrs.end())
                            {
                                size_t attrIndex = it - sortedPrevAttrs.begin();
                                if (attrIndex >= changedAttrs[sortedPrimIndex].size() ||
                                    !changedAttrs[sortedPrimIndex][attrIndex])
                                {
                                    // This attribute was imported last time and it hasn't changed.
                                    continue;
                                }
                            }
                        }
                    }
                    else
                    {
                        attr = outputBundlePrim->addRelationship(outputNameToken, relTargets.size());
                    }

                    // populate SdfPaths
                    Token* relData = attr->getData<Token>();
                    for (size_t i = 0; i < relTargets.size(); ++i)
                    {
                        const pxr::SdfPath& relTarget = relTargets[i];
                        const pxr::TfToken& relToken = relTarget.GetToken();
                        omni::fabric::TokenC p = omni::fabric::asInt(relToken);
                        relData[i] = Token{ p };
                    }
                }

                if (importedAttrs != nullptr)
                {
                    std::sort(importedAttrs->begin(), importedAttrs->end());
                }
            }
        }

        if (pathsChangedInfo != nullptr)
        {
            pathsChangedInfo->sortedPrevImportedAttrs = std::move(fullImportedAttrs);
        }

        if (db.inputs.importTransform())
        {
            matrix4d* data;
            if (multiplePrimsSupported)
            {
                auto attr = output.getCommonAttrs().addAttr(iToken->getHandle("transform"),
                                                            Type(BaseDataType::eDouble, 16, 1, AttributeRole::eFrame),
                                                            paths.size());
                data = attr->getData<matrix4d>();
            }
            else
            {
                AttributeDataHandle attr =
                    iBundle->addAttribute(context, outputBundleHandle, iToken->getHandle("transform"),
                                          Type(BaseDataType::eDouble, 16, 0, AttributeRole::eFrame));
                data = getDataW<matrix4d>(context, attr);
            }
            for (size_t pathi = 0; pathi < paths.size(); ++pathi)
            {
                if (pathi != 0 && !multiplePrimsSupported)
                    break;
                const pxr::SdfPath& primPath = paths[pathi];
                const pxr::UsdPrim prim = stage->GetPrimAtPath(primPath);
                CARB_ASSERT(prim);
                const pxr::GfMatrix4d primTransform = xformCache.GetLocalToWorldTransform(prim);
                // NOTE: USD transformation order accepts row vectors and applies transforms left to right.
                data[pathi] = safeCastToOmni(primTransform) * inverseNodeTransform;
            }
        }
        else
        {
            // clean out any stale attribute that may be hanging around
            if (multiplePrimsSupported)
            {
                output.getCommonAttrs().removeAttr(iToken->getHandle("transform"));
            }
            else
            {
                iBundle->removeAttribute(context, outputBundleHandle, iToken->getHandle("transform"));
            }
        }

        if (db.inputs.computeBoundingBox())
        {
            matrix4d* transform;
            vec3d *minCorner, *maxCorner;

            if (multiplePrimsSupported)
            {
                auto transformAttr = output.getCommonAttrs().addAttr(
                    iToken->getHandle("bboxTransform"), Type(BaseDataType::eDouble, 16, 1, AttributeRole::eFrame),
                    paths.size());
                auto minCornerAttr = output.getCommonAttrs().addAttr(
                    iToken->getHandle("bboxMinCorner"), Type(BaseDataType::eDouble, 3, 1, AttributeRole::ePosition),
                    paths.size());
                auto maxCornerAttr = output.getCommonAttrs().addAttr(
                    iToken->getHandle("bboxMaxCorner"), Type(BaseDataType::eDouble, 3, 1, AttributeRole::ePosition),
                    paths.size());
                transform = transformAttr->getData<matrix4d>();
                minCorner = minCornerAttr->getData<vec3d>();
                maxCorner = maxCornerAttr->getData<vec3d>();
            }
            else
            {
                AttributeDataHandle transformAttr =
                    iBundle->addAttribute(context, outputBundleHandle, iToken->getHandle("bboxTransform"),
                                          Type(BaseDataType::eDouble, 16, 0, AttributeRole::eFrame));
                AttributeDataHandle minCornerAttr =
                    iBundle->addAttribute(context, outputBundleHandle, iToken->getHandle("bboxMinCorner"),
                                          Type(BaseDataType::eDouble, 3, 0, AttributeRole::ePosition));
                AttributeDataHandle maxCornerAttr =
                    iBundle->addAttribute(context, outputBundleHandle, iToken->getHandle("bboxMaxCorner"),
                                          Type(BaseDataType::eDouble, 3, 0, AttributeRole::ePosition));
                transform = getDataW<matrix4d>(context, transformAttr);
                minCorner = getDataW<vec3d>(context, minCornerAttr);
                maxCorner = getDataW<vec3d>(context, maxCornerAttr);
            }
            for (size_t pathi = 0; pathi < paths.size(); ++pathi)
            {
                if (pathi != 0 && !multiplePrimsSupported)
                    break;
                const pxr::SdfPath& primPath = paths[pathi];
                const pxr::UsdPrim prim = stage->GetPrimAtPath(primPath);
                CARB_ASSERT(prim);
                const pxr::GfBBox3d bbox = bboxCache.ComputeLocalBound(prim);
                transform[pathi] = safeCastToOmni(bbox.GetMatrix());
                minCorner[pathi] = safeCastToOmni(bbox.GetBox().GetMin());
                maxCorner[pathi] = safeCastToOmni(bbox.GetBox().GetMax());
            }
        }
        else
        {
            // clean out any stale attributes that may be hanging around
            if (multiplePrimsSupported)
            {
                output.getCommonAttrs().removeAttr(iToken->getHandle("bboxTransform"));
                output.getCommonAttrs().removeAttr(iToken->getHandle("bboxMinCorner"));
                output.getCommonAttrs().removeAttr(iToken->getHandle("bboxMaxCorner"));
            }
            else
            {
                iBundle->removeAttribute(context, outputBundleHandle, iToken->getHandle("bboxTransform"));
                iBundle->removeAttribute(context, outputBundleHandle, iToken->getHandle("bboxMinCorner"));
                iBundle->removeAttribute(context, outputBundleHandle, iToken->getHandle("bboxMaxCorner"));
            }
        }

        {
            if (multiplePrimsSupported)
            {
                for (size_t i = 0; i < paths.size(); ++i)
                {
                    BundlePrim* outputBundlePrim = output.getPrim(i);
                    CARB_ASSERT(outputBundlePrim);
                    if (outputBundlePrim)
                    {
                        const pxr::UsdPrim prim = stage->GetPrimAtPath(paths[i]);
                        CARB_ASSERT(prim);
                        outputBundlePrim->setType(omni::fabric::asInt(prim.GetTypeName()));
                    }
                }
            }
            else
            {
                const pxr::UsdPrim prim = stage->GetPrimAtPath(paths[0]);
                CARB_ASSERT(prim);
                output.getCommonAttrs().setType(omni::fabric::asInt(prim.GetTypeName()));
            }
        }

        if (db.inputs.importPath())
        {
            if (multiplePrimsSupported)
            {
                for (size_t i = 0; i < paths.size(); ++i)
                {
                    BundlePrim* outputBundlePrim = output.getPrim(i);
                    CARB_ASSERT(outputBundlePrim);
                    if (outputBundlePrim)
                    {
                        outputBundlePrim->setPath(omni::fabric::asInt(paths[i].GetToken()));
                    }
                }
            }
            else
            {
                output.getCommonAttrs().setPath(omni::fabric::asInt(paths[0].GetToken()));
            }
        }

        if (db.inputs.importTime())
        {
            if (multiplePrimsSupported)
            {
                auto attr = output.getCommonAttrs().addAttr(
                    iToken->getHandle("primTime"), Type(BaseDataType::eDouble, 1, 0, AttributeRole::eNone));
                attr->set(primTime);
            }
            else
            {
                AttributeDataHandle attr =
                    iBundle->addAttribute(context, outputBundleHandle, iToken->getHandle("primTime"),
                                          Type(BaseDataType::eDouble, 1, 0, AttributeRole::eNone));
                double* data = getDataW<double>(context, attr);
                *data = primTime;
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
