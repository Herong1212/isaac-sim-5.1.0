// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <OgnExportUSDPrimDatabase.h>

// clang-format off
#include "UsdPCH.h"
// clang-format on

#include <omni/usd/UsdUtils.h>

#include "USDBundles.h"
#include "Transform.h"
#include "PrimCommon.h"
#include "AttributeNameMap.h"

#include <omni/fabric/FabricUSD.h>
#include <carb/Defines.h>
#include <omni/graph/core/BundlePrims.h>
#include <pxr/base/tf/hashmap.h>
#include <pxr/usd/sdf/path.h>

#include <algorithm>

using omni::graph::core::BundleAttributeInfo;
using omni::graph::core::checkDirtyIDChanged;
using omni::graph::core::ConstBundlePrim;
using omni::graph::core::ConstBundlePrims;
using omni::graph::nodes::AttributeNameMap;

static const pxr::TfToken s_cacheKeyTfToken("cacheKey");
static const pxr::TfToken s_tokenTfToken("token");

class OgnExportUSDPrim
{
public:
    static void initialize(const GraphContextObj& contextObj, const NodeObj& nodeObj)
    {
        pxr::UsdPrim thisPrim = omni::graph::nodes::getUsdPrimFromNode(contextObj, nodeObj);
        if (!thisPrim.IsValid())
            return;

        if (!thisPrim.HasRelationship(pxr::TfToken("outputs:prim")))
        {
            pxr::UsdRelationship usdRel = thisPrim.CreateRelationship(pxr::TfToken("outputs:prim"));
            usdRel.SetCustomDataByKey(pxr::TfToken("reverse_flow_graph_connection"), pxr::VtValue(true));
        }
    }

    static bool compute(OgnExportUSDPrimDatabase& db)
    {
        db.logWarning(
            "ExportUsdPrim is deprecated and will be removed in a future release. Use the WritePrim set of nodes instead.");

        auto& nodeObj = db.abi_node();
        auto& context = db.abi_context();

        auto& prevPrimDirtyIDs = db.state.prevPrimDirtyIDs();

        const bool optionsChanged = (db.state.prevPrimPathFromBundle() != db.inputs.primPathFromBundle()) ||
                                    (db.state.prevApplyTransform() != db.inputs.applyTransform()) ||
                                    (db.state.prevUsdTimecode() != db.inputs.usdTimecode()) ||
                                    (db.state.prevTimeVaryingAttributes() != db.inputs.timeVaryingAttributes()) ||
                                    (db.state.prevOnlyExportToExisting() != db.inputs.onlyExportToExisting()) ||
                                    (db.state.prevRenameAttributes() != db.inputs.renameAttributes()) ||
                                    (db.state.prevInputAttrNames() != db.inputs.inputAttrNames()) ||
                                    (db.state.prevOutputAttrNames() != db.inputs.outputAttrNames()) ||
                                    (db.state.prevExcludedAttrNames() != db.inputs.excludedAttrNames()) ||
                                    (db.state.prevAttrNamesToExport() != db.inputs.attrNamesToExport()) ||
                                    (db.state.prevRemoveMissingAttrs() != db.inputs.removeMissingAttrs()) ||
                                    (db.state.prevExportToRootLayer() != db.inputs.exportToRootLayer()) ||
                                    (db.state.prevLayerName() != db.inputs.layerName());
        db.state.prevPrimPathFromBundle() = db.inputs.primPathFromBundle();
        db.state.prevApplyTransform() = db.inputs.applyTransform();
        db.state.prevUsdTimecode() = db.inputs.usdTimecode();
        db.state.prevTimeVaryingAttributes() = db.inputs.timeVaryingAttributes();
        db.state.prevOnlyExportToExisting() = db.inputs.onlyExportToExisting();
        db.state.prevRenameAttributes() = db.inputs.renameAttributes();
        db.state.prevInputAttrNames() = db.inputs.inputAttrNames();
        db.state.prevOutputAttrNames() = db.inputs.outputAttrNames();
        db.state.prevExcludedAttrNames() = db.inputs.excludedAttrNames();
        db.state.prevAttrNamesToExport() = db.inputs.attrNamesToExport();
        db.state.prevRemoveMissingAttrs() = db.inputs.removeMissingAttrs();
        db.state.prevExportToRootLayer() = db.inputs.exportToRootLayer();
        db.state.prevLayerName() = db.inputs.layerName();

        ConstBundlePrims inputPrims(context, db.inputs.bundle().abi_bundleHandle());
        const size_t primCount = inputPrims.getPrimCount();
        CARB_IGNOREWARNING_MSC_WITH_PUSH(4996)
        CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wdeprecated-declarations")
        if (!checkDirtyIDChanged(db.state.prevBundleDirtyID(), inputPrims.getBundleDirtyID()) &&
            prevPrimDirtyIDs.size() == primCount && !optionsChanged)
        {
            // Input not changed since last time, so just return.
            return true;
        }
        CARB_IGNOREWARNING_GNUC_POP
        CARB_IGNOREWARNING_MSC_POP

        pxr::UsdPrim thisPrim = omni::graph::nodes::getUsdPrimFromNode(context, nodeObj);
        if (!thisPrim.IsValid())
        {
            CARB_LOG_ERROR("In OgnExportUSDPrim node, the compute node requires a USD prim in order to access the stage.");
            prevPrimDirtyIDs.resize(0);
            return false;
        }

        AttributeNameMap attributeNameMap{ db.inputs.renameAttributes(), db.inputs.inputAttrNames(),
                                           db.inputs.outputAttrNames(), db.inputs.attrNamesToExport() };

        std::vector<NameToken> excludedAttrNames = AttributeNameMap::splitNames(db.inputs.excludedAttrNames());

        const bool containsPrims = (primCount != 0);

        pxr::SdfPathVector outputPrimPaths;
        bool usingPrimPathAttr = false;
        if (db.inputs.primPathFromBundle())
        {
            if (containsPrims)
            {
                outputPrimPaths.reserve(primCount);

                for (ConstBundlePrim& inputPrim : inputPrims)
                {
                    outputPrimPaths.push_back(pxr::SdfPath(db.tokenToString(inputPrim.path())));
                }

                usingPrimPathAttr = true;
            }
            else
            {
                const auto primPathAttr = db.inputs.bundle().attributeByName(db.tokens.primPath);
                auto primPathData = primPathAttr.get<ogn::Token>();
                if (primPathData)
                {
                    auto usdPrimPath = *primPathData;
                    outputPrimPaths.push_back(pxr::SdfPath(db.tokenToString(usdPrimPath)));
                    usingPrimPathAttr = true;
                }
                else
                {
                    auto primPathsData = primPathAttr.get<ogn::Token[]>();
                    if (primPathsData)
                    {
                        auto usdPrimPath = *primPathsData;
                        outputPrimPaths.reserve(usdPrimPath.size());

                        for (size_t pathi = 0; pathi < usdPrimPath.size(); ++pathi)
                        {
                            outputPrimPaths.push_back(pxr::SdfPath(db.tokenToString(usdPrimPath[pathi])));
                        }
                        usingPrimPathAttr = true;
                    }
                }
            }
        }
        if (!usingPrimPathAttr)
        {
            const pxr::UsdRelationship relationship = thisPrim.GetRelationship(pxr::TfToken("outputs:prim"));
            relationship.GetTargets(&outputPrimPaths);
        }
        auto stage = thisPrim.GetStage();

        std::vector<bool> skipPrims;
        size_t skippedPrimCount = 0;

        const size_t outputPrimCount = outputPrimPaths.size();

        // Create the output USD prims if they don't exist yet
        for (size_t primi = 0; primi < outputPrimCount; ++primi)
        {
            const auto& sdfPath = outputPrimPaths[primi];
            pxr::UsdPrim outputUSDPrim = stage->GetPrimAtPath(sdfPath);
            if (!outputUSDPrim.IsValid())
            {
                // Check for a primType attribute
                NameToken usdPrimType = omni::fabric::kUninitializedToken;
                if (containsPrims)
                {
                    ConstBundlePrim* inputPrim = inputPrims.getConstPrim(primi);
                    CARB_ASSERT(inputPrim != nullptr);
                    if (inputPrim != nullptr)
                    {
                        usdPrimType = inputPrim->type();
                    }
                }
                else
                {
                    const auto primTypeAttr = db.inputs.bundle().attributeByName(db.tokens.primType);
                    auto primTypeData = primTypeAttr.get<ogn::Token>();

                    if (primTypeData)
                    {
                        usdPrimType = *primTypeData;
                    }
                    else
                    {
                        auto primTypesData = primTypeAttr.get<ogn::Token[]>();
                        if (primTypesData && primi < primTypesData->size())
                        {
                            usdPrimType = (*primTypesData)[primi];
                        }
                    }
                }

                const pxr::TfToken primType = (usdPrimType == omni::fabric::kUninitializedToken) ?
                                                  pxr::TfToken() :
                                                  pxr::TfToken(db.tokenToString(usdPrimType));
                outputUSDPrim = stage->DefinePrim(sdfPath, primType);
                if (!outputUSDPrim.IsValid())
                {
                    CARB_LOG_ERROR("In OgnExportUSDPrim node, there must be a valid USD prim path.");
                    prevPrimDirtyIDs.resize(0);
                    return false;
                }
            }

            // FIXME: cacheKey is probably not being handled correctly here, and should probably
            //        be replaced by use of dirty IDs!
            pxr::UsdAttribute outputCacheKeyAttr = outputUSDPrim.GetAttribute(s_cacheKeyTfToken);
            if (outputCacheKeyAttr.GetTypeName() == s_tokenTfToken)
            {
                static const NameToken cacheKeyToken = db.stringToToken("cacheKey");
                const auto inputCacheKeyAttr = db.inputs.bundle().attributeByName(cacheKeyToken);
                auto inputCacheKeyData = inputCacheKeyAttr.get<ogn::Token>();
                if (inputCacheKeyData)
                {
                    NameToken inputToken = *inputCacheKeyData;
                    pxr::TfToken outputToken;
                    bool success = outputCacheKeyAttr.Get(&outputToken);
                    if (success && outputToken == pxr::TfToken(db.tokenToString(inputToken)))
                    {
                        // cacheKey hasn't changed, so skip exporting to this prim.
                        if (skipPrims.size() == 0)
                            skipPrims.resize(outputPrimCount, false);
                        skipPrims[primi] = true;
                        ++skippedPrimCount;
                    }
                }
                else
                {
                    auto inputCacheKeysData = inputCacheKeyAttr.get<ogn::Token[]>();
                    if (inputCacheKeysData && primi < inputCacheKeysData->size())
                    {
                        NameToken inputToken = (*inputCacheKeysData)[primi];
                        pxr::TfToken outputToken;
                        bool success = outputCacheKeyAttr.Get(&outputToken);
                        if (success && outputToken == pxr::TfToken(db.tokenToString(inputToken)))
                        {
                            // cacheKey hasn't changed, so skip exporting to this prim.
                            if (skipPrims.size() == 0)
                                skipPrims.resize(outputPrimCount, false);
                            skipPrims[primi] = true;
                            ++skippedPrimCount;
                        }
                    }
                }
            }
        }

        if (skippedPrimCount == outputPrimCount)
        {
            // All prims explicitly skipped due to cacheKey
            return true;
        }

        // Locally set the edit target to the specified layer.  The edit target will be changed back
        // to the previous edit target (authoring layer) when scopedLayerEdit goes out of scope.
        pxr::SdfLayerHandle layer;
        if (db.inputs.exportToRootLayer())
        {
            layer = stage->GetRootLayer();
        }
        else
        {
            const char* layerName = db.tokenToString(db.inputs.layerName());
            if (layerName != nullptr && layerName[0] != 0)
            {
                layer = pxr::SdfLayer::Find(layerName);
                if (!layer)
                {
                    db.logWarning("Skipping export to invalid layer \"%s\" in ExportUSDPrim node.", layerName);
                    prevPrimDirtyIDs.resize(0);
                    return false;
                }
            }
            else
            {
                layer = stage->GetSessionLayer();
            }
        }
        omni::usd::UsdUtils::ScopedLayerEdit scopedLayerEdit(stage, layer);

        std::vector<TransformInfo> transformInfos;
        if (db.inputs.applyTransform())
        {
            // Set up all of the transforms.
            transformInfos.resize(outputPrimCount);
            pxr::UsdGeomXformCache xformCache(db.inputs.usdTimecode());

            const pxr::GfMatrix4d nodeTransform = xformCache.GetLocalToWorldTransform(thisPrim);
            for (size_t primi = 0; primi < outputPrimCount; ++primi)
            {
                const auto& sdfPath = outputPrimPaths[primi];
                pxr::UsdPrim outputUSDPrim = stage->GetPrimAtPath(sdfPath);
                const pxr::GfMatrix4d primTransform = xformCache.GetLocalToWorldTransform(outputUSDPrim);

                matrix4d nodeToPrimTransform =
                    safeCastToOmni(nodeTransform) * (safeCastToOmni(primTransform).GetInverse());
                transformInfos[primi].init(nodeToPrimTransform);
            }
        }

        const double primTime = db.inputs.usdTimecode();
        const double attrTime = db.inputs.timeVaryingAttributes() ? primTime : pxr::UsdTimeCode::Default().GetValue();

        bool exportAll = (prevPrimDirtyIDs.size() != primCount) || optionsChanged;
        if (prevPrimDirtyIDs.size() != primCount)
            prevPrimDirtyIDs.resize(primCount);

        const bool removeMissingAttrs = db.inputs.removeMissingAttrs();
        using OutputAttrsMap = pxr::TfHashMap<pxr::SdfPath, std::vector<NameToken>, pxr::SdfPath::Hash>;
        OutputAttrsMap exportedOutputAttrs;
        if (removeMissingAttrs)
            exportedOutputAttrs.reserve(primCount);

        for (size_t primi = 0; primi < primCount; ++primi)
        {
            ConstBundlePrim* inputPrim = inputPrims.getConstPrim(primi);
            CARB_ASSERT(inputPrim != nullptr);
            if (inputPrim == nullptr)
            {
                continue;
            }

            CARB_IGNOREWARNING_MSC_WITH_PUSH(4996)
            CARB_IGNOREWARNING_GNUC_WITH_PUSH("-Wdeprecated-declarations")
            const DirtyIDType currentPrimDirtyID = inputPrim->dirtyID();
            if (!exportAll && prevPrimDirtyIDs[primi] == currentPrimDirtyID)
            {
                // This prim hasn't changed, so skip it.
                continue;
            }
            CARB_IGNOREWARNING_GNUC_POP
            CARB_IGNOREWARNING_MSC_POP

            prevPrimDirtyIDs[primi] = currentPrimDirtyID;

            std::vector<NameToken>* localExportedOutputAttrs{ nullptr };
            if (removeMissingAttrs)
            {
                localExportedOutputAttrs = &exportedOutputAttrs[outputPrimPaths[primi]];
                localExportedOutputAttrs->reserve(inputPrim->attrCount());
            }

            for (const auto& attr : *inputPrim)
            {
                NameToken inputName = attr.name();

                // Skip copying bundle/prim management attributes, (for now, unless exporting them is useful later.)
                if (inputName == db.tokens.primPath || inputName == db.tokens.primType ||
                    inputName == db.tokens.primTime || inputName == db.tokens.primCount ||
                    inputName == db.tokens.transform)
                {
                    continue;
                }

                auto excludedIter = std::find(excludedAttrNames.begin(), excludedAttrNames.end(), inputName);
                if (excludedIter != excludedAttrNames.end())
                {
                    // Attribute is excluded
                    continue;
                }

                if (attributeNameMap.isNotSpecifiedName(inputName))
                {
                    continue;
                }

                NameToken outputNameToken = attributeNameMap.getName(inputName);


                if (removeMissingAttrs)
                    localExportedOutputAttrs->push_back(outputNameToken);

                // Copy just to the specified prim
                const auto& sdfPath = outputPrimPaths[primi];
                pxr::UsdPrim outputUSDPrim = stage->GetPrimAtPath(sdfPath);
                exportAttrToUSD(attr, db.inputs.applyTransform() ? &transformInfos[primi] : nullptr,
                                db.inputs.onlyExportToExisting(), outputNameToken, outputUSDPrim, attrTime);
            }
        }

        for (auto const& attr : inputPrims.getCommonAttrs())
        {
            NameToken inputName = attr.name();

            // Skip copying bundle/prim management attributes, (for now, unless exporting them is useful later.)
            if (inputName == db.tokens.primPath || inputName == db.tokens.primType || inputName == db.tokens.primTime ||
                inputName == db.tokens.primCount || inputName == db.tokens.transform)
            {
                continue;
            }

            auto excludedIter = std::find(excludedAttrNames.begin(), excludedAttrNames.end(), inputName);
            if (excludedIter != excludedAttrNames.end())
            {
                // Attribute is excluded
                continue;
            }

            if (attributeNameMap.isNotSpecifiedName(inputName))
            {
                continue;
            }

            NameToken outputNameToken = attributeNameMap.getName(inputName);

            // Copy to all output prims
            for (size_t primi = 0; primi < outputPrimCount; ++primi)
            {
                if (removeMissingAttrs)
                {
                    std::vector<NameToken>& localExportedOutputAttrs = exportedOutputAttrs[outputPrimPaths[primi]];
                    localExportedOutputAttrs.push_back(outputNameToken);
                }

                const auto& sdfPath = outputPrimPaths[primi];
                pxr::UsdPrim outputUSDPrim = stage->GetPrimAtPath(sdfPath);
                exportAttrToUSD(attr, db.inputs.applyTransform() ? &transformInfos[primi] : nullptr,
                                db.inputs.onlyExportToExisting(), outputNameToken, outputUSDPrim, attrTime);
            }
        }

        if (removeMissingAttrs && exportedOutputAttrs.size() != 0)
        {
            for (size_t primi = 0; primi < outputPrimCount; ++primi)
            {
                const auto& sdfPath = outputPrimPaths[primi];
                auto pathIt = exportedOutputAttrs.find(sdfPath);
                if (pathIt == exportedOutputAttrs.end())
                    continue;
                std::vector<NameToken>& localExportedOutputAttrs = pathIt->second;
                std::sort(localExportedOutputAttrs.begin(), localExportedOutputAttrs.end());
                pxr::UsdPrim outputUSDPrim = stage->GetPrimAtPath(sdfPath);
                std::vector<pxr::UsdProperty> properties = outputUSDPrim.GetAuthoredProperties();
                for (auto& property : properties)
                {
                    NameToken propertyName = omni::fabric::asInt(property.GetName());
                    auto it =
                        std::lower_bound(localExportedOutputAttrs.begin(), localExportedOutputAttrs.end(), propertyName);
                    if (it == localExportedOutputAttrs.end() || *it != propertyName)
                    {
                        // Not exported, so remove it from the output prim.
#if CARB_ASSERT_ENABLED
                        bool success =
#endif
                            outputUSDPrim.RemoveProperty(property.GetName());
                        CARB_ASSERT(success);
                    }
                }
            }
        }

        return true;
    }
};

REGISTER_OGN_NODE()
