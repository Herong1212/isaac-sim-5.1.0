// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#ifndef USD_UTILS_INCLUDES
#    error "Please include UtilsIncludes.h before including this header or in pre-compiled header."
#endif

#include "PathUtils.h"

#include <omni/kit/SettingsUtils.h>

#include <carb/InterfaceUtils.h>
#include <carb/extras/Path.h>
#include <carb/logging/Log.h>
#include <carb/omniclient/OmniClientUtils.h>
#include <carb/settings/ISettings.h>

#include <functional>
#include <regex>
#include <vector>

PXR_NAMESPACE_OPEN_SCOPE
inline bool GfIsClose(const pxr::GfQuatd& val1, const pxr::GfQuatd& val2, double tolerance)
{
    bool result1 = pxr::GfIsClose(val1.GetReal(), val2.GetReal(), tolerance) &&
                   GfIsClose(val1.GetImaginary(), val2.GetImaginary(), tolerance);
    bool result2 = GfIsClose(val1.GetReal(), -val2.GetReal(), tolerance) &&
                   GfIsClose(val1.GetImaginary(), -val2.GetImaginary(), tolerance);
    return result1 || result2;
}
PXR_NAMESPACE_CLOSE_SCOPE

namespace omni
{
namespace usd
{

static constexpr char kAuthorOldMdlSchemaSettingPath[] = "/omni.kit.plugin/authorOldMdlSchema";
static constexpr char kCreateXformForTypelessReferenceSettingPath[] = "/omni.kit.plugin/createXformForTypelessReference";
static constexpr char kCreateExplicitRefForNoneDefaultPrimSettingPath[] =
    "/omni.kit.plugin/createExplicitRefForNoneDefaultPrim";
static constexpr char kAuthorXformsWithFastUpdatesSettingPath[] = "/omni.kit.plugin/authorXformsWithFastUpdates";
static constexpr char kDefaultRotationOrderSettingPath[] =
    PERSISTENT_SETTINGS_PREFIX "/app/primCreation/DefaultRotationOrder";
static constexpr char kDefaultXforOpTypeSettingPath[] = PERSISTENT_SETTINGS_PREFIX "/app/primCreation/DefaultXformOpType";

/**
 * Defines a helper class to perform various USD operations.
 *
 * Because different project might want to include USD headers differently (Kit uses pre-compiled header for USD
 * includes), UsdUtils.h doesn't include any USD headers. Users are responsible for including the correct headers.
 */
class UsdUtils
{
public:
    /**
     * Defines a helper class to do scoped layer editing. It sets scoped edit target and layer editing permission.
     */
    class ScopedLayerEdit
    {
    public:
        ScopedLayerEdit(pxr::UsdStageWeakPtr stage, const pxr::SdfLayerHandle& layer)
            : m_usdEditCtx(stage, layer), m_layer(layer)
        {
            m_wasLayerEditable = m_layer->PermissionToEdit();
            m_layer->SetPermissionToEdit(true);
            CARB_ASSERT(m_layer->PermissionToEdit());
        }

        ~ScopedLayerEdit()
        {
            m_layer->SetPermissionToEdit(m_wasLayerEditable);
        }

    private:
        pxr::UsdEditContext m_usdEditCtx;
        pxr::SdfLayerHandle m_layer;
        bool m_wasLayerEditable;
    };

    /**
     * Helper base class to subscribe to pxr::TfNotice
     */
    template <typename T>
    class UsdNoticeListener : public pxr::TfWeakBase
    {
    public:
        virtual ~UsdNoticeListener()
        {
            revokeListener();
        }

        void registerListener()
        {
            // To avoid leak
            revokeListener();
            m_usdNoticeListenerKey =
                pxr::TfNotice::Register(pxr::TfCreateWeakPtr(this), &UsdNoticeListener::handleNotice);
        }

        void revokeListener()
        {
            if (m_usdNoticeListenerKey.IsValid())
            {
                pxr::TfNotice::Revoke(m_usdNoticeListenerKey);
            }
        }

        virtual void handleNotice(const T& objectsChanged) = 0;

    private:
        pxr::TfNotice::Key m_usdNoticeListenerKey;
    };

    using OnCreateFn = std::function<pxr::UsdPrim(pxr::UsdStageWeakPtr stage, const pxr::SdfPath& path)>;
    /**
     * Checks if a UsdGeomXformable instance is time sampled.
     *
     * @param xform The UsdGeomXformable to be checked.
     * @return True if the xform is timesampled.
     */
    static bool isTimeSampled(const pxr::UsdGeomXformable& xform)
    {
        // Iterate every xformOps check if any of them is timesampled.
        // Don't call xform.GetTimeSamples() since this function will perform a very low efficient timesamples union for
        // all xformOps.
        // Also xform.TransformsMightBeTimeVarying() is not fit here since it will return true only one of
        // the xformOp's numTimesamples > 1.
        bool resetXformStack = false;
        auto xformOps = xform.GetOrderedXformOps(&resetXformStack);
        for (auto xformOp : xformOps)
        {
            if (xformOp.GetNumTimeSamples() > 0)
            {
                return true;
            }
        }
        return false;
    }

    /**
     * Checks if a UsdGeomXformable has timeSample on Key time
     * TODO: currently imgizmo can only handle matrix, which brings that we need to set translate/rotation/scale have
     * same key times But this is not correct, need to be fixed.
     * @param xform The UsdGeomXformable to be checked.
     * @param timeCode The timeCode to be checked on xform.
     * @return True if the xform is timesampled on key timeCode.
     */
    static bool hasTimeSample(const pxr::UsdGeomXformable& xform, pxr::UsdTimeCode timeCode)
    {
        if (timeCode.IsDefault())
            return false;

        bool resetXformStack = false;
        auto xformOps = xform.GetOrderedXformOps(&resetXformStack);
        for (auto xformOp : xformOps)
        {
            if (hasTimeSample(xformOp.GetAttr(), timeCode))
            {
                return true;
            }
        }
        return false;
    }

    /**
     * Checks if a UsdAttribute instance is time sampled.
     *
     * @param attribute The UsdAttribute to be checked.
     * @return True if the attribute is timesampled.
     */
    static bool isTimeSampled(const pxr::UsdAttribute& attribute)
    {
        return attribute.GetNumTimeSamples() > 0;
    }

    /**
     * Checks if a UsdAttribute instance has time sample on key timeCode
     *
     * @param attribute The UsdAttribute to be checked.
     * @param timeCode The timeCode to be checked.
     * @return True if the attribute has timesampled on key timeCode.
     */
    static bool hasTimeSample(const pxr::UsdAttribute& attribute, pxr::UsdTimeCode timeCode)
    {
        if (timeCode.IsDefault())
            return false;

        std::vector<double> times;
        if (attribute.GetTimeSamples(&times))
        {
            double timeCodeValue = timeCode.GetValue();
            if (round(timeCodeValue) != timeCode.GetValue())
            {
                CARB_LOG_WARN("Error : Try to identify attribute %s has time sample on a fractinal key frame %f",
                              attribute.GetPath().GetText(), timeCodeValue);
                return false;
            }
            return std::find(times.begin(), times.end(), timeCodeValue) != times.end();
        }
        return false;
    }

    /**
     * Gets current UsdTimeCode of given stage.
     *
     * @param stage The stage to get time code from.
     * @param isTimeSampled If the property is timesampled.
     * @param time Current timecode.
     * @return Current timecode of the stage.
     */
    static pxr::UsdTimeCode getUsdTimeCode(pxr::UsdStageWeakPtr stage, bool isTimeSampled, pxr::UsdTimeCode time)
    {
        return isTimeSampled ? time : pxr::UsdTimeCode::Default();
    }

    /**
     * Removes a prim from stage.
     *
     * @param prim The prim instance to be removed.
     * @return True if prim is removed successfully.
     */
    static bool removePrim(pxr::UsdPrim& prim)
    {
        auto stage = prim.GetStage();
        bool ret = false;

        if (checkAncestral(prim))
        {
            CARB_LOG_ERROR("Cannot remove ancestral prim %s", prim.GetPath().GetText());
            return false;
        }

        pxr::SdfChangeBlock changeBlock;

        if (stage->HasDefaultPrim() && stage->GetDefaultPrim() == prim)
        {
            stage->ClearDefaultPrim();
        }

        auto layerStack = stage->GetLayerStack();
        std::set<pxr::SdfLayerHandle> layerSet(layerStack.begin(), layerStack.end());

        auto primStack = prim.GetPrimStack();
        for (auto&& primSpec : primStack)
        {
            auto layer = primSpec->GetLayer();
            // Only remove from layers in the stage
            if (layerSet.find(layer) == layerSet.end() || primSpec->GetPath() != prim.GetPath())
            {
                continue;
            }

            pxr::SdfBatchNamespaceEdit nsEdits;
            nsEdits.Add(pxr::SdfNamespaceEdit::Remove(primSpec->GetPath()));
            ret |= layer->Apply(nsEdits);
        }

        return ret;
    }

    /**
     * Removes a prim from layer
     *
     * @param prim The prim instance to be removed.
     * @param layer Layer from which to remove prim
     * @return True if prim is removed successfully.
     */
    static bool removePrimFromLayer(pxr::UsdPrim& prim, pxr::SdfLayerHandle layer)
    {
        auto stage = prim.GetStage();

        if (checkAncestral(prim))
        {
            CARB_LOG_ERROR("Cannot remove ancestral prim %s", prim.GetPath().GetText());
            return false;
        }

        pxr::SdfChangeBlock changeBlock;

        if (stage->HasDefaultPrim() && stage->GetDefaultPrim() == prim)
        {
            stage->ClearDefaultPrim();
        }

        auto primSpec = layer->GetPrimAtPath(prim.GetPath());
        auto parent = primSpec->GetNameParent();
        if (!parent)
        {
            parent = layer->GetPseudoRoot();
        }

        return parent->RemoveNameChild(primSpec);
    }


    /**
     * Copies a prim in the stage.
     *
     * @param prim The prim to be copied.
     * @param tarPath The target path of copied prim, or nullptr if you want a auto generated path (e.g. "foo" ->
     * "foo_2").
     * @param defOrRefOnly True to only copy the layer that defines or references the Prim. False copy deltas on all
     * layers. @p defOrRefOnly has no effect if @p combineAllLayers is true.
     * @param combineAllLayers True to combine deltas on all layers and make a consolidated copy on current edit layer.
     * False to copy each delta on their own layer.
     * @return The copied prim. Call IsValid on the return value to check if copy is successful.
     */
    static PXR_NS::UsdPrim copyPrim(PXR_NS::UsdPrim& prim, const char* tarPath, bool defOrRefOnly, bool combineAllLayers)
    {
        PXR_NS::UsdPrim ret;
        auto stage = prim.GetStage();

        std::string tarPathStr;
        if (tarPath)
        {
            tarPathStr = tarPath;
        }
        else
        {
            tarPathStr = findNextNoneExisitingNodePath(stage, prim.GetPath().GetString(), false);
        }

        PXR_NS::SdfPath srcPath(prim.GetPath());
        PXR_NS::SdfPath dstPath(tarPathStr);

        if (!combineAllLayers)
        {
            PXR_NS::SdfChangeBlock changeBlock;
            auto layers = prim.GetStage()->GetLayerStack();
            for (const auto& layer : layers)
            {
                auto oldPrimSpec = layer->GetPrimAtPath(srcPath);
                if (oldPrimSpec)
                {
                    PXR_NS::SdfLayerHandle dstLayer = layer;
                    if (!defOrRefOnly)
                    {
                        dstLayer = stage->GetEditTarget().GetLayer();
                    }
                    if (defOrRefOnly || (!defOrRefOnly && oldPrimSpec->HasReferences()) ||
                        oldPrimSpec->GetSpecifier() == PXR_NS::SdfSpecifier::SdfSpecifierDef)
                    {
                        PXR_NS::SdfCreatePrimInLayer(dstLayer, dstPath);
                        PXR_NS::SdfCopySpec(layer, srcPath, dstLayer, dstPath);

                        if (!defOrRefOnly)
                        {
                            break;
                        }
                    }
                }
            }
        }
        else // Combine all prim spec from all visible layers and copy to current edit target
        {
            auto editTargetLayerHandle = stage->GetEditTarget().GetLayer();

            // Make a temporary stage to hold the Prim to copy, and flatten it later
            auto flattenStage = PXR_NS::UsdStage::CreateInMemory();

            PXR_NS::SdfPrimSpecHandleVector primSpecs;

            // If the prim is introduced by its ancestor, its primSpec might now exist in current stage (if no "over" is
            // made to it) we need to copy from its primStack
            if (checkAncestral(prim))
            {
                primSpecs = prim.GetPrimStack();
            }
            else
            {
                for (auto& layer : prim.GetStage()->GetLayerStack())
                {
                    auto primSpec = layer->GetPrimAtPath(prim.GetPath());
                    if (primSpec)
                    {
                        primSpecs.push_back(primSpec);
                    }
                }
            }

            for (const auto& primSpec : primSpecs)
            {
                auto srcLayer = primSpec->GetLayer();
                PXR_NS::SdfLayerRefPtr dstLayer = nullptr;
                if (srcLayer->IsAnonymous())
                {
                    // If src layer is Anonymous, all relative path has been converted to absolute path.
                    dstLayer = PXR_NS::SdfLayer::CreateAnonymous();
                }
                else
                {
                    // If src layer is not Anonymous, we need to create a layer at the same parent dir so
                    // relative path can be resolved.
                    carb::extras::Path layerPath(srcLayer->GetRealPath());
                    size_t counter = 0;
                    while (!dstLayer)
                    {
                        std::string tempFileName = layerPath.getParent() / layerPath.getStem() +
                                                   std::to_string(counter++) + layerPath.getExtension();

                        // Make sure we create a none-exist temp layer
                        if (PXR_NS::SdfLayer::FindOrOpen(tempFileName))
                        {
                            continue;
                        }

                        auto format = PXR_NS::SdfFileFormat::FindByExtension(layerPath.getExtension());

                        // Use PXR_NS::SdfLayer::New instead of PXR_NS::SdfLayer::CreateNew so no file is created
                        dstLayer = PXR_NS::SdfLayer::New(format, tempFileName);
                    }
                }

                PXR_NS::SdfCreatePrimInLayer(dstLayer, srcPath);
                PXR_NS::SdfCopySpec(srcLayer, primSpec->GetPath(), dstLayer, srcPath);

                flattenStage->GetRootLayer()->InsertSubLayerPath(dstLayer->GetIdentifier());
            }

            auto flattenLayer = flattenStage->Flatten();
            PXR_NS::SdfCopySpec(flattenLayer, srcPath, editTargetLayerHandle, dstPath);
        }

        prim = stage->GetPrimAtPath(dstPath);
        return prim;
    }

    /**
     * Resolve all prim path reference to use new path. This is mainly used to remapping
     * prim path reference after structure change of original prim.
     * @param layer Layer to resolve.
     * @param oldPath Old prim path.
     * @param newPath New prim path that all old prim path references will be resolved to.
     */
    static void resolvePrimPathReferences(const PXR_NS::SdfLayerRefPtr& layer,
        const PXR_NS::SdfPath& oldPath, const PXR_NS::SdfPath& newPath)
    {
        static auto updatePrimPathRef = [](const PXR_NS::SdfPrimSpecHandle& primSpec, const PXR_NS::SdfPath& oldPath, const PXR_NS::SdfPath& newPath)
        {
            auto modifyItemEditsCallback = [&oldPath, &newPath](const PXR_NS::SdfPath& path)
            {
                return path.ReplacePrefix(oldPath, newPath);
            };

            auto modifyItemReferencesCallback = [&oldPath, &newPath](const PXR_NS::SdfReference& reference)
            {
                PXR_NS::SdfPath primPath;
                if (reference.GetAssetPath().empty())
                {
                    primPath = reference.GetPrimPath().ReplacePrefix(oldPath, newPath);
                }
                else
                {
                    primPath = reference.GetPrimPath();
                }

                return PXR_NS::SdfReference(
                    reference.GetAssetPath(),
                    primPath,
                    reference.GetLayerOffset(),
                    reference.GetCustomData()
                );
            };

            // Update relationships
            for (const auto& relationship : primSpec->GetRelationships())
            {
                relationship->GetTargetPathList().ModifyItemEdits(modifyItemEditsCallback);
            }

            // Update connections
            for (const auto& attribute : primSpec->GetAttributes())
            {
                attribute->GetConnectionPathList().ModifyItemEdits(modifyItemEditsCallback);
            }

            primSpec->GetReferenceList().ModifyItemEdits(modifyItemReferencesCallback);
        };

        auto onPrimSpecPath = [&layer, &oldPath, &newPath](const PXR_NS::SdfPath& primPath)
        {
            if (primPath.IsPropertyPath() || primPath == PXR_NS::SdfPath::AbsoluteRootPath())
            {
                return;
            }

            auto primSpec = layer->GetPrimAtPath(primPath);
            if (primSpec)
            {
                updatePrimPathRef(primSpec, oldPath, newPath);
            }
        };

        layer->Traverse(PXR_NS::SdfPath::AbsoluteRootPath(), onPrimSpecPath);
    }

    /**
     * Resolve all prim paths reference to use new path. This is mainly used to remapping
     * prim path reference after structure change of original prim.
     * @param layer Layer to resolve.
     * @param oldPaths Old prim paths.
     * @param newPaths New prim paths that all old prim paths references will be resolved to.
     */
    static void resolvePrimPathsReferences(const PXR_NS::SdfLayerRefPtr& layer,
                                           const std::vector<std::string>& oldPaths,
                                           const std::vector<std::string>& newPaths)
    {
        if (oldPaths.size() != newPaths.size())
        {
            CARB_LOG_ERROR("UsdUtils: oldPaths and newPaths must be the same size. %d != %d", (int)oldPaths.size(),
                           (int)newPaths.size());
            return;
        }

        struct ResolveTargetPath
        {
            PXR_NS::SdfPath oldPrimPath;
            PXR_NS::SdfPath newPrimPath;
        };

        // Convert string to SdfPath first to reduce unnecessary duplicate parsing overhead.
        std::vector<ResolveTargetPath> resolveTargetPaths(oldPaths.size());
        for (size_t i = 0; i < resolveTargetPaths.size(); ++i)
        {
            resolveTargetPaths[i] = { PXR_NS::SdfPath(oldPaths[i]), PXR_NS::SdfPath(newPaths[i]) };
        }

        // Local cache to avoid redundant iterations
        std::map<PXR_NS::SdfPrimSpecHandle, std::vector<PXR_NS::SdfTargetsProxy>> targetProxyLists;
        std::map<PXR_NS::SdfPrimSpecHandle, std::vector<PXR_NS::SdfConnectionsProxy>> connectionProxyLists;
        std::map<PXR_NS::SdfPrimSpecHandle, PXR_NS::SdfReferencesProxy> referenceProxyList;

        auto onPrimSpecPath = [&layer, &resolveTargetPaths, &targetProxyLists, &connectionProxyLists,
                               &referenceProxyList](const PXR_NS::SdfPath& primPath)
        {
            if (primPath.IsPropertyPath() || primPath == PXR_NS::SdfPath::AbsoluteRootPath())
            {
                return;
            }

            const PXR_NS::SdfPrimSpecHandle primSpec = layer->GetPrimAtPath(primPath);

            if (primSpec)
            {
                for (const ResolveTargetPath& resolveTargetPath : resolveTargetPaths)
                {
                    const PXR_NS::SdfPath& oldPath = resolveTargetPath.oldPrimPath;
                    const PXR_NS::SdfPath& newPath = resolveTargetPath.newPrimPath;

                    auto modifyItemEditsCallback = [&oldPath, &newPath](const PXR_NS::SdfPath& path)
                    { return path.ReplacePrefix(oldPath, newPath); };

                    auto modifyItemReferencesCallback = [&oldPath, &newPath](const PXR_NS::SdfReference& reference)
                    {
                        PXR_NS::SdfPath primPath;
                        if (reference.GetAssetPath().empty())
                        {
                            primPath = reference.GetPrimPath().ReplacePrefix(oldPath, newPath);
                        }
                        else
                        {
                            primPath = reference.GetPrimPath();
                        }

                        return PXR_NS::SdfReference(
                            reference.GetAssetPath(), primPath, reference.GetLayerOffset(), reference.GetCustomData());
                    };

                    // Prepare relationship target paths if it's not cached. GetRelationships GetTargetPathList take a
                    // long time. These cache logics are safe because the prim relationships and connections are not
                    // changed during path resolve.
                    if (targetProxyLists.find(primSpec) == targetProxyLists.end())
                    {
                        const PXR_NS::SdfRelationshipSpecView& relationships = primSpec->GetRelationships();
                        std::vector<PXR_NS::SdfTargetsProxy>& targetProxyList = targetProxyLists[primSpec];
                        targetProxyList.reserve(relationships.size());

                        for (const PXR_NS::SdfRelationshipSpecHandle& relationship : relationships)
                        {
                            targetProxyList.push_back(relationship->GetTargetPathList());
                        }
                    }

                    // Update relationship target paths
                    for (PXR_NS::SdfTargetsProxy& targetPathList : targetProxyLists[primSpec])
                    {
                        targetPathList.ModifyItemEdits(modifyItemEditsCallback);
                    }

                    // Prepare connection paths
                    if (connectionProxyLists.find(primSpec) == connectionProxyLists.end())
                    {
                        const PXR_NS::SdfAttributeSpecView& attributes = primSpec->GetAttributes();
                        std::vector<PXR_NS::SdfConnectionsProxy>& proxyList = connectionProxyLists[primSpec];
                        proxyList.reserve(attributes.size());

                        for (const PXR_NS::SdfAttributeSpecHandle& attribute : attributes)
                        {
                            proxyList.push_back(attribute->GetConnectionPathList());
                        }
                    }

                    // Update connection paths
                    for (PXR_NS::SdfConnectionsProxy& connectionPathList : connectionProxyLists[primSpec])
                    {
                        connectionPathList.ModifyItemEdits(modifyItemEditsCallback);
                    }

                    if (referenceProxyList.find(primSpec) == referenceProxyList.end())
                    {
                        referenceProxyList[primSpec] = primSpec->GetReferenceList();
                    }

                    // Update reference list
                    referenceProxyList[primSpec].ModifyItemEdits(modifyItemReferencesCallback);
                }
            }
        };

        layer->Traverse(PXR_NS::SdfPath::AbsoluteRootPath(), onPrimSpecPath);
    }


    /**
     * Moves a prim to a new path.
     *
     * @param prim The prim to be moved.
     * @param newPath The new path to move prim to.
     * @param supportNamespaceEdit false if (omni::usd::UsdContext::getContext()->isStageLive() &&
     * strncmp(realPath.c_str(), "omniverse:", 10) == 0 && pxr::SdfFileFormat::GetFileExtension(realPath) != "usdov")
     * @return True if Prim is moved successfully.
     */
    static bool movePrim(pxr::UsdPrim& prim, const char* newPath, bool supportNamespaceEdit)
    {
        if (!prim)
        {
            return false;
        }

        if (checkAncestral(prim))
        {
            CARB_LOG_ERROR("Cannot remove ancestral prim %s", prim.GetPath().GetText());
            return false;
        }

        auto stage = prim.GetStage();
        const char* oldPath = prim.GetPath().GetText();

        // If src and target path are the same, don't move.
        if (strcmp(newPath, oldPath) == 0)
        {
            return false;
        }

        bool wasDefaultPrim = stage->GetDefaultPrim() == prim;

        auto newPathStr = findNextNoneExisitingNodePath(prim.GetStage(), newPath, false);
        if (!pxr::SdfPath::IsValidPathString(newPathStr))
        {
            return false;
        }

        pxr::SdfPath newSdfPath(newPathStr);
        pxr::TfToken newName = newSdfPath.GetNameToken();
        pxr::SdfPath newParentPath = newSdfPath.GetParentPath();
        pxr::SdfPath oldSdfPath = prim.GetPath();
        pxr::TfToken oldName = prim.GetName();
        pxr::SdfPath oldParentPath = prim.GetParent().GetPath();

        auto layerStack = stage->GetLayerStack();
        std::set<pxr::SdfLayerHandle> layerSet(layerStack.begin(), layerStack.end());

        auto primStack = prim.GetPrimStack();
        for (auto&& primSpec : primStack)
        {
            bool useNamespaceEdit = true;
            auto layer = primSpec->GetLayer();

            // Only remove from layers in the stage
            if (layerSet.find(layer) == layerSet.end())
            {
                continue;
            }

            if (!supportNamespaceEdit)
            {
                CARB_LOG_WARN(
                    "Current USD format doesn't support NamespaceEdit to move/rename prim, fallback to copy/delete");
                useNamespaceEdit = false;
            }

            if (useNamespaceEdit)
            {
                pxr::SdfBatchNamespaceEdit nsEdits;
                if (oldParentPath == newParentPath)
                {
                    CARB_LOG_INFO("Rename %s to %s", oldSdfPath.GetText(),
                                  (oldSdfPath.GetParentPath().AppendChild(newName)).GetText());
                    nsEdits.Add(pxr::SdfNamespaceEdit::Rename(oldSdfPath, newName));
                }
                else
                {
                    // SdfNamespaceEdit::Reparent somehow doesn't work for move without renaming

                    CARB_LOG_INFO("Move %s to %s", oldSdfPath.GetText(), (newParentPath.AppendChild(newName)).GetText());
                    nsEdits.Add(pxr::SdfNamespaceEdit::ReparentAndRename(
                        primSpec->GetPath(), newParentPath, newName, pxr::SdfNamespaceEdit::AtEnd));
                }
                layer->Apply(nsEdits);
            }
            else
            {
                if (pxr::SdfCreatePrimInLayer(layer, newSdfPath))
                {
                    if (pxr::SdfCopySpec(layer, oldSdfPath, layer, newSdfPath))
                    {
                        pxr::SdfBatchNamespaceEdit nsEdits;
                        nsEdits.Add(pxr::SdfNamespaceEdit::Remove(oldSdfPath));
                        layer->Apply(nsEdits);
                    }
                }
            }

            auto newPrim = layer->GetPrimAtPath(newSdfPath);
            if (newPrim)
            {
                // Fixup connections and relationships
                resolvePrimPathReferences(layer, prim.GetPrimPath(), newSdfPath);
            }
        }

        auto newPrim = stage->GetPrimAtPath(newSdfPath);
        if (newPrim)
        {
            // Restore defaultPrim state
            if (wasDefaultPrim && newPrim.GetParent() == stage->GetPseudoRoot())
            {
                stage->SetDefaultPrim(newPrim);
            }
        }

        return newPrim.IsValid();
    }

    /**
     * Creates a prim on given stage.
     *
     * @param stage The stage to create prim on.
     * @param path The path to create prim at.
     * @param onCreateFn The creating function for the prim.
     * @param prependDefaultPrimPath Whether to prepend defaultPrim path to Prim path. True to put the prim under
     * defaultPrim path.
     * @return The created prim. Call IsValid on the return value to check if creation is successful.
     */
    static pxr::UsdPrim createPrim(pxr::UsdStageWeakPtr stage,
                                   const char* path,
                                   OnCreateFn onCreateFn,
                                   bool prependDefaultPrimPath = true)
    {
        std::string newPath = findNextNoneExisitingNodePath(stage, path, prependDefaultPrimPath);
        return onCreateFn(stage, pxr::SdfPath(newPath));
    }

    /**
     * Creates a prim on given stage.
     *
     * @param stage The stage to create prim on.
     * @param path The path to create prim at.
     * @param typeName The type name of the prim.
     * @param prependDefaultPrimPath Whether to prepend defaultPrim path to Prim path. True to put the prim under
     * defaultPrim path.
     * @return The created prim. Call IsValid on the return value to check if creation is successful.
     */
    static pxr::UsdPrim createPrim(pxr::UsdStageWeakPtr stage,
                                   const char* path,
                                   const char* typeName,
                                   bool prependDefaultPrimPath = true)
    {
        std::string newPath = findNextNoneExisitingNodePath(stage, path, prependDefaultPrimPath);
        return stage->DefinePrim(pxr::SdfPath(newPath), pxr::TfToken(typeName));
    }

    /**
     * Returns if a prim exists at given path.
     *
     * @param stage The stage to check prim existence.
     * @param path The prim path
     * @param prependDefaultPrimPath Whether to check under defaultPrim path or stage root.
     */
    static bool hasPrimAtPath(pxr::UsdStageWeakPtr stage, std::string path, bool prependDefaultPrimPath = true)
    {
        if (prependDefaultPrimPath && stage->HasDefaultPrim())
        {
            path = stage->GetDefaultPrim().GetPath().GetString() + path;
        }

        return stage->GetPrimAtPath(pxr::SdfPath(path)).IsValid();
    }

    /**
     * Gets if a prim is visible.
     *
     * @param prim The prim to get visibility from.
     * @param prim The visibility of the prim's parent.
     * @param time Current timecode.
     * @return True if prim is visible.
     */
    static bool isPrimVisible(const pxr::UsdPrim& prim, pxr::UsdTimeCode time = pxr::UsdTimeCode::Default())
    {
        pxr::UsdGeomImageable imageable(prim);
        auto visibilityAttr = imageable.GetVisibilityAttr();

        auto visibility = imageable.ComputeVisibility(time);
        return visibility != pxr::UsdGeomTokens->invisible;
    }

    /**
     * Sets the visibility on a prim.
     *
     * @param prim The prim to set visibility.
     * @param visible True to make a prim visible. False to hide it.
     * @param time Current timecode.
     */
    static void setPrimVisibility(pxr::UsdPrim prim, bool visible, pxr::UsdTimeCode time = pxr::UsdTimeCode::Default())
    {
        pxr::UsdGeomImageable imageable(prim);
        auto visibilityAttr = imageable.GetVisibilityAttr();

        visibilityAttr.Set(visible ? pxr::UsdGeomTokens->inherited : pxr::UsdGeomTokens->invisible, time);
    }

    /**
     * Gets if prim have transforms at key time_code.
     *
     * @param The prim to check transform sequence.
     * @param time Current timecode.
     * @return if prim has transform at time_code
     */
    // TODO : Need more tweak on each kinds of transformop after timesample authoring support all kinds of transformop
    static bool getPrimHasTransformAtKey(const pxr::UsdPrim& prim,
                                         pxr::UsdTimeCode time_code = pxr::UsdTimeCode::Default())
    {
        pxr::UsdGeomXformable xform(prim);

        bool resetXFormStack;
        auto xformOps = xform.GetOrderedXformOps(&resetXFormStack);

        if (time_code.IsDefault())
        {
            return false;
        }

        for (auto xformOp : xformOps)
        {
            std::vector<double> times;
            if (xformOp.GetTimeSamples(&times))
            {
                if (std::find(times.begin(), times.end(), time_code.GetValue()) != times.end())
                {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Gets local transform matrix of a prim.
     *
     * @param prim The prim to get local transform matrix from.
     * @param time Current timecode.
     * @return The local transform matrix.
     */
    static pxr::GfMatrix4d getLocalTransformMatrix(const pxr::UsdPrim& prim,
                                                   pxr::UsdTimeCode time = pxr::UsdTimeCode::Default())
    {
        bool resetXformStack = false;
        pxr::UsdGeomXformable xform(prim);
        pxr::GfMatrix4d mat;

        xform.GetLocalTransformation(&mat, &resetXformStack, time);

        return mat;
    }

    /**
     * Gets GfRotation from XformOp that is UsdGeomXformOp::TypeOrient.
     * It is caller's responsibility to pass the xformOp with correct type.
     *
     * @param xformOp The UsdGeomXformOp to get rotation from. It must be of type UsdGeomXformOp::TypeOrient.
     * @param time The timecode to get value from.
     * @return GfRotation of the xformOp. The value is set to identity if failed to fetch from xformOp (mismatched type or undefined value).
     */
    template <typename QuatT>
    static PXR_NS::GfRotation getRotationFromXformOpOrient(const PXR_NS::UsdGeomXformOp& xformOp,
                                                           const PXR_NS::UsdTimeCode& time)
    {
        QuatT quat;
        if (xformOp.Get<QuatT>(&quat, time))
        {
            return PXR_NS::GfRotation(quat);
        }
        return PXR_NS::GfRotation({ 1, 0, 0 }, 0);
    }

    /**
     * Gets local transform if applied in scale, rotation, translation order.
     *
     * Depending on the xformOpOrder of the prim, the returned value may not be identical to the final local
     * transform. Only use this function on simple SRT xformOpOrder or matrix.
     *
     * @param prim The prim to get local transform matrix from.
     * @param time translation to be written to.
     * @param time rotation euler angle (in degree) to be written to.
     * @param time rotation order to be written to.
     * @param time scale to be written to.
     * @param time Current timecode.
     * @return true if operation succeed.
     */
    static bool getLocalTransformSRT(const PXR_NS::UsdPrim& prim,
                                     PXR_NS::GfVec3d& translation,
                                     PXR_NS::GfVec3d& rotation,
                                     PXR_NS::GfVec3i& rotationOrder,
                                     PXR_NS::GfVec3d &scale, PXR_NS::UsdTimeCode time = pxr::UsdTimeCode::Default())
    {
        using namespace PXR_NS;

        bool resetXformStack = false;
        pxr::UsdGeomXformable xform(prim);

        std::vector<UsdGeomXformOp> extraXformOps;
        std::vector<UsdGeomXformOp> orderedXformOps = xform.GetOrderedXformOps(&resetXformStack);

        bool seenScale = false;
        uint32_t seenRotation = 0; // use a counter here, because euler angle can show up as individual xformOp.
        bool seenAxes[3] = { false, false, false };
        bool seenTranslation = false;

        // default values
        scale.Set(1.0, 1.0, 1.0);
        rotation.Set(0.0, 0.0, 0.0);
        rotationOrder.Set(-1, -1, -1); // placeholder
        translation.Set(0.0, 0.0, 0.0);

        for (auto it = orderedXformOps.rbegin(); it != orderedXformOps.rend(); ++it)
        {
            const UsdGeomXformOp& xformOp = *it;

            if (xformOp.IsInverseOp())
            {
                continue;
            }

            // A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
            // for preop we need still full matrix computation for post op we can reconstruct at the end
            static const TfToken kUnitsResolve = TfToken("unitsResolve");
            if (xformOp.HasSuffix(kUnitsResolve))
            {
                if (xformOp == orderedXformOps[0])
                {
                    GfMatrix4d mtx;
                    bool resetXformStack;
                    xform.GetLocalTransformation(&mtx, &resetXformStack, time);

                    pxr::GfMatrix4d rotMat(1.0);
                    pxr::GfMatrix4d scaleOrientMatUnused, perspMatUnused;
                    mtx.Factor(&scaleOrientMatUnused, &scale, &rotMat, &translation, &perspMatUnused);

                    // By default decompose as XYZ order (make it an option?)
                    GfVec3d decompRot =
                        rotMat.ExtractRotation().Decompose(GfVec3d::ZAxis(), GfVec3d::YAxis(), GfVec3d::XAxis());
                    rotation = { decompRot[2], decompRot[1], decompRot[0] };
                    rotationOrder = { 0, 1, 2 };
                    return true;
                }
                else
                {
                    extraXformOps.push_back(xformOp);
                }
                continue;
            }

            const UsdGeomXformOp::Type opType = xformOp.GetOpType();
            const UsdGeomXformOp::Precision precision = xformOp.GetPrecision();

            if (opType == UsdGeomXformOp::TypeTransform)
            {
                seenScale = true;
                seenRotation = 3;
                seenTranslation = true;
                GfMatrix4d mtx = xformOp.GetOpTransform(time);

                pxr::GfMatrix4d rotMat(1.0);
                pxr::GfMatrix4d scaleOrientMatUnused, perspMatUnused;
                mtx.Factor(&scaleOrientMatUnused, &scale, &rotMat, &translation, &perspMatUnused);

                // By default decompose as XYZ order (make it an option?)
                GfVec3d decompRot =
                    rotMat.ExtractRotation().Decompose(GfVec3d::ZAxis(), GfVec3d::YAxis(), GfVec3d::XAxis());
                rotation = { decompRot[2], decompRot[1], decompRot[0] };
                rotationOrder = { 0, 1, 2 };

                break;
            }

            if (!seenScale)
            {
                if (opType == UsdGeomXformOp::TypeScale)
                {
                    if (seenRotation || seenTranslation)
                    {
                        CARB_LOG_WARN("Incompatible xformOpOrder, rotation or translation applied before scale.");
                    }

                    seenScale = true;
                    xformOp.GetAs<>(&scale, time);
                }
            }

            if (seenRotation != 3)
            {
                if (opType >= UsdGeomXformOp::TypeRotateXYZ && opType <= UsdGeomXformOp::TypeRotateZYX)
                {
                    if (seenTranslation || seenRotation != 0)
                    {
                        CARB_LOG_WARN("Incompatible xformOpOrder, translation applied before rotation or too many rotation ops.");
                    }

                    seenRotation = 3;
                    xformOp.GetAs<>(&rotation, time);

                    static const GfVec3i kRotationOrder[] = {
                        { 0, 1, 2 }, // XYZ
                        { 0, 2, 1 }, // XZY
                        { 1, 0, 2 }, // YXZ
                        { 1, 2, 0 }, // YZX
                        { 2, 0, 1 }, // ZXY
                        { 2, 1, 0 }, // ZYX
                    };

                    rotationOrder = kRotationOrder[opType - UsdGeomXformOp::TypeRotateXYZ];
                }
                else if (opType >= UsdGeomXformOp::TypeRotateX && opType <= UsdGeomXformOp::TypeRotateZ)
                {
                    if (seenTranslation || seenRotation > 3)
                    {
                        CARB_LOG_WARN("Incompatible xformOpOrder, too many single axis rotation ops.");
                    }

                    // Set rotation order based on individual axis order
                    rotationOrder[seenRotation++] = opType - UsdGeomXformOp::TypeRotateX;
                    seenAxes[opType - UsdGeomXformOp::TypeRotateX] = true;

                    double angle = 0.0;
                    xformOp.GetAs<>(&angle, time);
                    rotation[opType - UsdGeomXformOp::TypeRotateX] = angle;
                }
                else if (opType == UsdGeomXformOp::TypeOrient)
                {
                    if (seenTranslation || seenRotation != 0)
                    {
                        CARB_LOG_WARN("Incompatible xformOpOrder, translation applied before rotation or too many rotation ops.");
                    }

                    seenRotation = 3;
                    GfRotation rot;

                    // GetAs cannot convert between Quath, Quatf and Quatd
                    switch (precision)
                    {
                    case PXR_NS::UsdGeomXformOp::PrecisionHalf:
                    {
                        rot = getRotationFromXformOpOrient<GfQuath>(xformOp, time);
                        break;
                    }
                    case PXR_NS::UsdGeomXformOp::PrecisionFloat:
                    {
                        rot = getRotationFromXformOpOrient<GfQuatf>(xformOp, time);
                        break;
                    }
                    case PXR_NS::UsdGeomXformOp::PrecisionDouble:
                    {
                        rot = getRotationFromXformOpOrient<GfQuatd>(xformOp, time);
                        break;
                    }
                    default:
                        break;
                    }

                    // By default decompose as XYZ order (make it an option?)
                    GfVec3d decompRot = rot.Decompose(GfVec3d::ZAxis(), GfVec3d::YAxis(), GfVec3d::XAxis());
                    rotation = { decompRot[2], decompRot[1], decompRot[0] };
                    rotationOrder = { 0, 1, 2 };
                }
            }

            if (!seenTranslation)
            {
                // Do not get translation from pivot
                if (opType == UsdGeomXformOp::TypeTranslate && !xformOp.HasSuffix(PXR_NS::TfToken("pivot")))
                {
                    seenTranslation = true;
                    xformOp.GetAs<>(&translation, time);
                }
            }
        }

        if (seenRotation == 0)
        {
            // If we did not see any rotation op, get it from the preferences
            static const std::unordered_map<std::string, PXR_NS::GfVec3i> s_orderMap{
                { "XYZ", { 0, 1, 2 } }, { "XZY", { 0, 2, 1 } }, { "YXZ", { 1, 0, 2 } },
                { "YZX", { 1, 2, 0 } }, { "ZXY", { 2, 0, 1 } }, { "ZYX", { 2, 1, 0 } },
            };

            PXR_NS::GfVec3i preferredDefaultRotationOrder = { 0, 1, 2 }; // fallback
            const char* orderStr =
                carb::getCachedInterface<carb::settings::ISettings>()->getStringBuffer(kDefaultRotationOrderSettingPath);
            const auto orderEntry = s_orderMap.find(orderStr);
            if (orderEntry != s_orderMap.end())
            {
                preferredDefaultRotationOrder = orderEntry->second;
            }
            rotationOrder = preferredDefaultRotationOrder;
            seenRotation = 3;
        }
        else
        {
            // Assign rotation order to missing rotation ops after existing rotation ops
            for (size_t i = 0; i < 3; i++)
            {
                int32_t& order = rotationOrder[i];
                if (order == -1)
                {
                    for (int32_t j = 0; j < 3; j++)
                    {
                        if (!seenAxes[j])
                        {
                            order = j;
                            seenAxes[j] = true;
                            break;
                        }
                    }
                }
            }
        }

        // A.B. this is a known transformation, we have a rotateX + -90 and scale
        // we can just add the X euler rotation and swap the scale Y, Z axis, this should represent the additonal transformation
        if (!extraXformOps.empty())
        {
            for (const UsdGeomXformOp& extraOp : extraXformOps)
            {
                if (extraOp.GetOpType() == UsdGeomXformOp::Type::TypeScale)
                {
                    PXR_NS::GfVec3d scaleValue;
                    extraOp.GetAs<>(&scaleValue, time);

                    scale = PXR_NS::GfCompMult(scale, scaleValue);
                }
                else if (extraOp.GetOpType() == UsdGeomXformOp::Type::TypeRotateX)
                {
                    double rotValue;
                    extraOp.GetAs<>(&rotValue, time);

                    if (PXR_NS::GfIsClose(abs(rotValue), 90.0, 0.01))
                    {
                        rotation[0] = rotation[0] + rotValue;
                        std::swap(scale[1], scale[2]);
                    }
                    else
                    {
                        CARB_LOG_WARN(
                            "UnitsResolve rotateX supports only +-90 degree on prim: %s", prim.GetPrimPath().GetText());
                    }
                }
            }
        }

        return true;
    }

    /**
     * Gets the inversed pivot transform matrix of a prim.
     *
     * @param prim The prim to get inversed pivot transform matrix from.
     * @param time Current timecode.
     * @return The inversed pivot transform matrix. If prim has no pivot, identity matrix will be returned.
     */
    static pxr::GfMatrix4d getLocalTransformPivotInv(const pxr::UsdPrim& prim,
                                                     pxr::UsdTimeCode time = pxr::UsdTimeCode::Default())
    {
        pxr::UsdGeomXformable xform(prim);

        bool resetXFormStack;
        auto xformOps = xform.GetOrderedXformOps(&resetXFormStack);

        // potential pivot inv node
        if (xformOps.size())
        {
            auto pivotOpInv = xformOps.back();
            if (pivotOpInv.GetOpType() == pxr::UsdGeomXformOp::Type::TypeTranslate &&
                pivotOpInv.HasSuffix(pxr::TfToken("pivot")) && pivotOpInv.IsInverseOp())
            {
                return pivotOpInv.GetOpTransform(time);
            }
        }

        // return an identity matrix if no pivot is found
        return pxr::GfMatrix4d(1.f);
    }

    /**
     * Gets world transform matrix of a prim.
     *
     * @param prim The prim to get world transform matrix from.
     * @param time Current timecode.
     * @return The world transform matrix.
     */
    static pxr::GfMatrix4d getWorldTransformMatrix(const pxr::UsdPrim& prim,
                                                   pxr::UsdTimeCode time = pxr::UsdTimeCode::Default())
    {
        pxr::UsdGeomXformable xform(prim);
        return xform.ComputeLocalToWorldTransform(time);
    }

    /**
     * Given a target local transform matrix for a prim, determine what value to set just
     * the transformOp when other xformOps are present.
     *
     * @param prim The prim in question
     * @param mtx The desired final transform matrix for the prim including all ops
     * @param foundTransformOp returns true if there is a transform xformOp
     */
    static pxr::GfMatrix4d findInnerTransform(pxr::UsdPrim prim,
                                              const pxr::GfMatrix4d& mtx,
                                              bool& foundTransformOp,
                                              pxr::UsdTimeCode timecode = pxr::UsdTimeCode::Default(),
                                              bool skipEqualSetForTimeSample = false)
    {
        pxr::UsdGeomXformable xform(prim);

        bool resetXFormStack;
        auto xformOps = xform.GetOrderedXformOps(&resetXFormStack);
        foundTransformOp = false;
        bool foundOtherOps = false;
        pxr::GfMatrix4d preTransform = pxr::GfMatrix4d(1.);
        pxr::GfMatrix4d postTransform = pxr::GfMatrix4d(1.);

        for (auto xformOp : xformOps)
        {
            if (!foundTransformOp && xformOp.GetOpType() == pxr::UsdGeomXformOp::TypeTransform)
            {
                foundTransformOp = true;
            }
            else
            {
                bool isInverseOp = false;
                pxr::UsdGeomXformOp op(xformOp.GetAttr(), isInverseOp);
                if (op)
                {
                    static const PXR_NS::TfToken kPivotSuffix("pivot");
                    if (op.HasSuffix(kPivotSuffix))
                    {
                        continue;
                    }

                    // possibly check for identity and skip multiplication
                    auto opTransform = op.GetOpTransform(timecode);
                    if (foundTransformOp)
                    {
                        preTransform = opTransform * preTransform;
                    }
                    else
                    {
                        postTransform = opTransform * postTransform;
                    }
                    foundOtherOps = true;
                }
            }
        }

        if (foundTransformOp && foundOtherOps)
        {
            return preTransform.GetInverse() * mtx * postTransform.GetInverse();
        }

        return mtx;
    }

    /**
     * Sets local transform matrix of a prim.
     *
     * @param prim The prim to set local transform matrix to.
     * @param mtx The local transform matrix.
     */
    static bool setLocalTransformMatrix(pxr::UsdPrim prim,
                                        const pxr::GfMatrix4d& mtxIn,
                                        pxr::UsdTimeCode timecode = pxr::UsdTimeCode::Default(),
                                        bool skipEqualSetForTimeSample = false,
                                        std::unique_ptr<PXR_NS::SdfChangeBlock>* parentChangeBlock = nullptr)
    {
        // If prim is defined in session layer, we author in session layer.
        std::unique_ptr<PXR_NS::UsdEditContext> editCtx;
        auto mightDefOnSessionLayer = getLayerIfDefOnSessionOrItsSublayers(prim.GetStage(), prim.GetPath());
        if (mightDefOnSessionLayer)
        {
            editCtx = std::make_unique<PXR_NS::UsdEditContext>(prim.GetStage(), mightDefOnSessionLayer);
        }

        carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
        bool fastUpdates = settings->getAsBool(kAuthorXformsWithFastUpdatesSettingPath);
        std::unique_ptr<PXR_NS::SdfChangeBlock> localChangeBlock;
        std::unique_ptr<PXR_NS::SdfChangeBlock>& changeBlock =
            (parentChangeBlock != nullptr) ? *parentChangeBlock : localChangeBlock;
        if (!changeBlock.get())
        {
            // https://github.com/PixarAnimationStudios/USD/commit/5e38b2aac0693fcf441a607165346e42cd625b59
            // fastUpdates have long been deprecated, and will be removed from the API
            // in nv-usd 22.05, as they not conflict with the "enabled" parameter
            // added by Pixar in USD v22.03
            changeBlock.reset(new PXR_NS::SdfChangeBlock());
        }

        pxr::UsdGeomXformable xform(prim);

        bool resetXFormStack;
        auto xformOps = xform.GetOrderedXformOps(&resetXFormStack);
        PXR_NS::VtTokenArray xformOpOrders;
        xform.GetXformOpOrderAttr().Get(&xformOpOrders);
        bool foundTransformOp = false;
        PXR_NS::UsdGeomXformOp transformOp;
        bool success = true;
        pxr::GfMatrix4d mtx = mtxIn;

        const pxr::GfMatrix4d innerMtx =
            findInnerTransform(prim, mtx, foundTransformOp, timecode, skipEqualSetForTimeSample);

        for (auto xformOp : xformOps)
        {
            // Found transform op, trying to set its value
            if (xformOp.GetOpType() == pxr::UsdGeomXformOp::TypeTransform)
            {
                foundTransformOp = true;
                success &= UsdUtils::setAttribute(xformOp.GetAttr(), innerMtx, timecode, skipEqualSetForTimeSample);
            }
        }

        // If transformOp is not found, make individual xformOp or reuse old ones.
        if (!foundTransformOp)
        {
            // A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
            static const PXR_NS::TfToken kUnitsResolve = PXR_NS::TfToken("unitsResolve");
            bool preTransformStack = false;
            std::vector<PXR_NS::UsdGeomXformOp> extraXformOps;

            for (auto& xformOp : xformOps)
            {
                if (xformOp.HasSuffix(kUnitsResolve))
                {
                    extraXformOps.push_back(xformOp);
                    if (xformOp == xformOps[0])
                    {
                        preTransformStack = true;
                    }
                }
            }

            // A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
            // reconstruct the values back after modifying the incoming transform
            if (!extraXformOps.empty())
            {
                PXR_NS::GfMatrix4d extraTransform(1.0);
                for (auto& extraOp : extraXformOps)
                {
                    extraTransform *= extraOp.GetOpTransform(timecode);
                }
                const PXR_NS::GfMatrix4d extraTransformInv = extraTransform.GetInverse();
                if (preTransformStack)
                {
                    mtx = mtx * extraTransformInv;
                }
                else
                {
                    mtx = extraTransformInv * mtx;
                }
            }

            pxr::GfVec3d translation;
            pxr::GfMatrix4d rotMat(1.0);
            pxr::GfVec3d doubleScale(1.0);
            pxr::GfMatrix4d scaleOrientMatUnused, perspMatUnused;
            mtx.Factor(&scaleOrientMatUnused, &doubleScale, &rotMat, &translation, &perspMatUnused);

            rotMat.Orthonormalize(false);
            pxr::GfRotation rotation = rotMat.ExtractRotation();

            // Don't use UsdGeomXformCommonAPI. It can only manipulate a very limited subset of xformOpOrder
            // combinations Do it manually as non-destructively as possible
            pxr::UsdGeomXformOp xformOp;
            std::vector<pxr::UsdGeomXformOp> newXformOps;

            if (!extraXformOps.empty() && preTransformStack)
            {
                for (auto& copyXformOp : extraXformOps)
                {
                    newXformOps.push_back(copyXformOp);
                }
            }

            auto findOrAdd = [&xformOps, &xformOpOrders, &xform, &changeBlock, &fastUpdates](
                                 pxr::UsdGeomXformOp::Type xformOpType, pxr::UsdGeomXformOp& outXformOp,
                                 bool createIfNotExist, pxr::UsdGeomXformOp::Precision& precision,
                                 pxr::TfToken const& opSuffix = pxr::TfToken()) {
                for (auto xformOp : xformOps)
                {
                    if (xformOp.GetOpType() == xformOpType)
                    {
                        // To differentiate translate and translate:pivot
                        const pxr::TfToken expectedOpName = pxr::UsdGeomXformOp::GetOpName(xformOpType, opSuffix);
                        const pxr::TfToken opName = xformOp.GetOpName();
                        if (opName == expectedOpName)
                        {
                            precision = xformOp.GetPrecision();
                            outXformOp = xformOp;
                            return true;
                        }
                    }
                }

                if (createIfNotExist)
                {
                    // It is not safe to create new xformOps inside of SdfChangeBlocks, since
                    // new attribute creation via anything above Sdf API requires the PcpCache
                    // to be up to date. Flush the current change block before creating
                    // the new xformOp.
                    changeBlock.reset(nullptr);
                    if (std::find(xformOpOrders.begin(), xformOpOrders.end(),
                                  pxr::UsdGeomXformOp::GetOpName(xformOpType, opSuffix)) == xformOpOrders.end())
                        outXformOp = xform.AddXformOp(xformOpType, precision, opSuffix);
                    else
                    {
                        // Sometimes XformOp attributes and XformOpOrder don't match. GetOrderedXformOps() considers both XformOp attributes and XformOpOrder. But AddXformOp() considers only XformOpOrder. So we need to fix it here.
                        auto opAttr = xform.GetPrim().CreateAttribute(
                            pxr::UsdGeomXformOp::GetOpName(xformOpType, opSuffix),
                            pxr::UsdGeomXformOp::GetValueTypeName(xformOpType, precision), false);
                        outXformOp = pxr::UsdGeomXformOp(opAttr);
                    }

                    // Create a new change block to batch the subsequent authoring operations
                    // where possible.
                    changeBlock.reset(new PXR_NS::SdfChangeBlock());
                    // Creation may have failed for a variety of reasons (including instanceable=True)
                    return static_cast<bool>(outXformOp);
                }
                return false;
            };

            auto getFirstRotateOpType = [&xformOps](pxr::UsdGeomXformOp::Precision& precision) {
                for (auto xformOp : xformOps)
                {
                    if (xformOp.GetOpType() >= pxr::UsdGeomXformOp::Type::TypeRotateX &&
                        xformOp.GetOpType() <= pxr::UsdGeomXformOp::Type::TypeOrient &&
                        !xformOp.HasSuffix(kUnitsResolve))
                    {
                        precision = xformOp.GetPrecision();
                        return xformOp.GetOpType();
                    }
                }
                return pxr::UsdGeomXformOp::Type::TypeInvalid;
            };

            auto decomposeAndSetValue = [&rotation, &findOrAdd, &newXformOps](
                                            pxr::UsdGeomXformOp::Type rotationType, const pxr::GfVec3d& axis0,
                                            const pxr::GfVec3d& axis1, const pxr::GfVec3d& axis2, size_t xIndex,
                                            size_t yIndex, size_t zIndex, pxr::UsdGeomXformOp::Precision precision,
                                            pxr::UsdTimeCode timecode, bool skipEqualSetForTimeSample) {
                bool ret = false;
                pxr::GfVec3d angles = rotation.Decompose(axis0, axis1, axis2);
                pxr::GfVec3d rotate = { angles[xIndex], angles[yIndex], angles[zIndex] };
                pxr::UsdGeomXformOp xformOp;
                if (findOrAdd(rotationType, xformOp, true, precision))
                {
                    ret = setValueWithPrecision<pxr::GfVec3h, pxr::GfVec3f, pxr::GfVec3d, pxr::GfVec3d>(
                        xformOp, rotate, timecode, skipEqualSetForTimeSample);
                    newXformOps.push_back(xformOp);
                }
                return ret;
            };

            // Set translation
            pxr::UsdGeomXformOp::Precision precision = pxr::UsdGeomXformOp::PrecisionDouble;
            if (findOrAdd(pxr::UsdGeomXformOp::TypeTranslate, xformOp, true, precision))
            {
                success &= setValueWithPrecision<pxr::GfVec3h, pxr::GfVec3f, pxr::GfVec3d, pxr::GfVec3d>(
                    xformOp, translation, timecode, skipEqualSetForTimeSample);
                newXformOps.push_back(xformOp);
            }

            // Set pivot
            static const pxr::TfToken kPivot = pxr::TfToken("pivot");
            precision = pxr::UsdGeomXformOp::PrecisionFloat;
            pxr::UsdGeomXformOp pivotOp;
            pxr::UsdGeomXformOp pivotOpInv;
            pxr::GfVec3d pivotValue(0., 0., 0.);
            const bool hasPivot =
                findOrAdd(pxr::UsdGeomXformOp::TypeTranslate, pivotOp, false, precision, kPivot);
            if (hasPivot)
            {
                newXformOps.push_back(pivotOp);
                for (size_t k = xformOps.size(); k--;)
                {
                    if (xformOps[k].IsInverseOp() && xformOps[k].HasSuffix(kPivot))
                    {
                        pivotOpInv = xformOps[k];
                        break;
                    }
                }
            }

            // Set rotation
            precision = pxr::UsdGeomXformOp::PrecisionFloat;
            auto firstRotateOpType = getFirstRotateOpType(precision);

            if (firstRotateOpType == pxr::UsdGeomXformOp::TypeInvalid)
            {
                static const std::unordered_map<std::string, PXR_NS::UsdGeomXformOp::Type> s_typeMap{
                    { "XYZ", PXR_NS::UsdGeomXformOp::TypeRotateXYZ }, { "XZY", PXR_NS::UsdGeomXformOp::TypeRotateXZY },
                    { "YXZ", PXR_NS::UsdGeomXformOp::TypeRotateYXZ }, { "YZX", PXR_NS::UsdGeomXformOp::TypeRotateYZX },
                    { "ZXY", PXR_NS::UsdGeomXformOp::TypeRotateZXY }, { "ZYX", PXR_NS::UsdGeomXformOp::TypeRotateZYX },
                };

                firstRotateOpType = PXR_NS::UsdGeomXformOp::TypeRotateXYZ; // fallback
                const char* orderStr = carb::getCachedInterface<carb::settings::ISettings>()->getStringBuffer(
                    kDefaultRotationOrderSettingPath);
                const auto orderEntry = s_typeMap.find(orderStr);
                if (orderEntry != s_typeMap.end())
                {
                    firstRotateOpType = orderEntry->second;
                }
            }

            switch (firstRotateOpType)
            {
            case pxr::UsdGeomXformOp::TypeRotateX:
            case pxr::UsdGeomXformOp::TypeRotateY:
            case pxr::UsdGeomXformOp::TypeRotateZ:
            {
                pxr::GfVec3d angles =
                    rotation.Decompose(pxr::GfVec3d::ZAxis(), pxr::GfVec3d::YAxis(), pxr::GfVec3d::XAxis());
                pxr::GfVec3d rotateZYX = { angles[2], angles[1], angles[0] };
                if (findOrAdd(pxr::UsdGeomXformOp::TypeRotateZ, xformOp, true, precision))
                {
                    success &= setValueWithPrecision<pxr::GfHalf, float, double, double>(
                        xformOp, rotateZYX[2], timecode, skipEqualSetForTimeSample);
                    newXformOps.push_back(xformOp);
                }
                if (findOrAdd(pxr::UsdGeomXformOp::TypeRotateY, xformOp, true, precision))
                {
                    success &= setValueWithPrecision<pxr::GfHalf, float, double, double>(
                        xformOp, rotateZYX[1], timecode, skipEqualSetForTimeSample);
                    newXformOps.push_back(xformOp);
                }
                if (findOrAdd(pxr::UsdGeomXformOp::TypeRotateX, xformOp, true, precision))
                {
                    success &= setValueWithPrecision<pxr::GfHalf, float, double, double>(
                        xformOp, rotateZYX[0], timecode, skipEqualSetForTimeSample);
                    newXformOps.push_back(xformOp);
                }
                break;
            }
            case pxr::UsdGeomXformOp::TypeRotateZYX:
                success &= decomposeAndSetValue(firstRotateOpType, pxr::GfVec3d::XAxis(), pxr::GfVec3d::YAxis(),
                                                pxr::GfVec3d::ZAxis(), 0, 1, 2, precision, timecode,
                                                skipEqualSetForTimeSample);
                break;
            case pxr::UsdGeomXformOp::TypeRotateXZY:
                success &= decomposeAndSetValue(firstRotateOpType, pxr::GfVec3d::YAxis(), pxr::GfVec3d::ZAxis(),
                                                pxr::GfVec3d::XAxis(), 2, 0, 1, precision, timecode,
                                                skipEqualSetForTimeSample);
                break;
            case pxr::UsdGeomXformOp::TypeRotateYXZ:
                success &= decomposeAndSetValue(firstRotateOpType, pxr::GfVec3d::ZAxis(), pxr::GfVec3d::XAxis(),
                                                pxr::GfVec3d::YAxis(), 1, 2, 0, precision, timecode,
                                                skipEqualSetForTimeSample);
                break;
            case pxr::UsdGeomXformOp::TypeRotateYZX:
                success &= decomposeAndSetValue(firstRotateOpType, pxr::GfVec3d::XAxis(), pxr::GfVec3d::ZAxis(),
                                                pxr::GfVec3d::YAxis(), 0, 2, 1, precision, timecode,
                                                skipEqualSetForTimeSample);
                break;
            case pxr::UsdGeomXformOp::TypeRotateZXY:
                success &= decomposeAndSetValue(firstRotateOpType, pxr::GfVec3d::YAxis(), pxr::GfVec3d::XAxis(),
                                                pxr::GfVec3d::ZAxis(), 1, 0, 2, precision, timecode,
                                                skipEqualSetForTimeSample);
                break;
            case pxr::UsdGeomXformOp::TypeOrient:
                if (findOrAdd(pxr::UsdGeomXformOp::TypeOrient, xformOp, false, precision))
                {
                    success &= setValueWithPrecision<pxr::GfQuath, pxr::GfQuatf, pxr::GfQuatd, pxr::GfQuatd>(
                        xformOp, rotation.GetQuat(), timecode, skipEqualSetForTimeSample);
                    newXformOps.push_back(xformOp);
                }
                break;
            case pxr::UsdGeomXformOp::TypeRotateXYZ:
            default:
                success &= decomposeAndSetValue(pxr::UsdGeomXformOp::TypeRotateXYZ, pxr::GfVec3d::ZAxis(),
                                                pxr::GfVec3d::YAxis(), pxr::GfVec3d::XAxis(), 2, 1, 0, precision,
                                                timecode, skipEqualSetForTimeSample);
                break;
            }

            // Set scale
            precision = pxr::UsdGeomXformOp::PrecisionFloat;
            if (findOrAdd(pxr::UsdGeomXformOp::TypeScale, xformOp, true, precision))
            {
                success &= setValueWithPrecision<pxr::GfVec3h, pxr::GfVec3f, pxr::GfVec3d, pxr::GfVec3d>(
                    xformOp, doubleScale, timecode, skipEqualSetForTimeSample);
                newXformOps.push_back(xformOp);
            }

            // Set extra ops from units resolve
            if (!extraXformOps.empty() && !preTransformStack)
            {
                for (auto& copyXformOp : extraXformOps)
                {
                    newXformOps.push_back(copyXformOp);
                }
            }

            // Set inverse pivot
            if (hasPivot && pivotOpInv)
            {
                // Assume the last xformOps is the pivot
                newXformOps.push_back(pivotOpInv);
            }

            success &= xform.SetXformOpOrder(newXformOps, resetXFormStack);
        }
        return success;
    }

    static PXR_NS::GfMatrix4d constructTransformMatrixFromSRT(const PXR_NS::GfVec3d& translation,
                                                              const PXR_NS::GfVec3d& rotationEuler,
                                                              const PXR_NS::GfVec3i& rotationOrder,
                                                              const PXR_NS::GfVec3d& scale)
    {
        using namespace PXR_NS;
        GfMatrix4d transMtx, rotMtx, scaleMtx;

        transMtx.SetTranslate(translation);

        static const GfVec3d kAxes[] = { GfVec3d::XAxis(), GfVec3d::YAxis(), GfVec3d::ZAxis() };
        GfRotation rotation = GfRotation(kAxes[rotationOrder[0]], rotationEuler[rotationOrder[0]]) *
                              GfRotation(kAxes[rotationOrder[1]], rotationEuler[rotationOrder[1]]) *
                              GfRotation(kAxes[rotationOrder[2]], rotationEuler[rotationOrder[2]]);

        rotMtx.SetRotate(rotation);

        scaleMtx.SetScale(scale);

        return scaleMtx * rotMtx * transMtx;
    }

    /**
     * Sets local transform matrix of a prim.
     *
     * @param prim The prim to set local transform matrix to.
     * @param mtx The local transform matrix.
     */
    static bool setLocalTransformSRT(PXR_NS::UsdPrim prim,
                                     const PXR_NS::GfVec3d& translationIn,
                                     const PXR_NS::GfVec3d& rotationEulerIn,
                                     const PXR_NS::GfVec3i& rotationOrder,
                                     const PXR_NS::GfVec3d& scaleIn,
                                     PXR_NS::UsdTimeCode timecode = PXR_NS::UsdTimeCode::Default(),
                                     bool skipEqualSetForTimeSample = false,
                                     std::unique_ptr<PXR_NS::SdfChangeBlock>* parentChangeBlock = nullptr)
    {
        using namespace PXR_NS;

        // If prim is defined in session layer, we author in session layer.
        std::unique_ptr<PXR_NS::UsdEditContext> editCtx;
        auto mightDefOnSessionLayer = getLayerIfDefOnSessionOrItsSublayers(prim.GetStage(), prim.GetPath());
        if (mightDefOnSessionLayer)
        {
            editCtx = std::make_unique<PXR_NS::UsdEditContext>(prim.GetStage(), mightDefOnSessionLayer);
        }

        carb::settings::ISettings* settings = carb::getCachedInterface<carb::settings::ISettings>();
        bool fastUpdates = settings->getAsBool(kAuthorXformsWithFastUpdatesSettingPath);
        std::unique_ptr<SdfChangeBlock> localChangeBlock;
        std::unique_ptr<SdfChangeBlock>& changeBlock =
            (parentChangeBlock != nullptr) ? *parentChangeBlock : localChangeBlock;
        if (!changeBlock.get())
        {
            changeBlock.reset(new SdfChangeBlock());
        }

        UsdGeomXformable xform(prim);

        bool resetXFormStack;
        auto xformOps = xform.GetOrderedXformOps(&resetXFormStack);
        PXR_NS::VtTokenArray xformOpOrders;
        xform.GetXformOpOrderAttr().Get(&xformOpOrders);
        bool foundTransformOp = false;
        UsdGeomXformOp transformOp;
        bool success = true;

        PXR_NS::GfVec3d translation = translationIn;
        PXR_NS::GfVec3d rotationEuler = rotationEulerIn;
        PXR_NS::GfVec3d scale = scaleIn;

        // A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
        static const TfToken kUnitsResolve = TfToken("unitsResolve");
        bool preTransformStack = false;
        std::vector<UsdGeomXformOp> extraXformOps;


        for (auto& xformOp : xformOps)
        {
            // Found transform op, trying to set its value
            if (xformOp.GetOpType() == UsdGeomXformOp::TypeTransform)
            {
                foundTransformOp = true;
                transformOp = xformOp;
            }
            else if (xformOp.HasSuffix(kUnitsResolve))
            {
                extraXformOps.push_back(xformOp);
                if (xformOp == xformOps[0])
                {
                    preTransformStack = true;
                }
            }
        }

        // A.B.temp solution to unblock a showstopper for supporting unitsResolve suffix xformOp stacks
        // reconstruct the values back after modifying the incoming transform
        if (!extraXformOps.empty() && !foundTransformOp)
        {
            if (preTransformStack)
            {
                GfMatrix4d mtx = constructTransformMatrixFromSRT(translation, rotationEuler, rotationOrder, scale);
                GfMatrix4d extraTransform(1.0);
                for (auto& extraOp : extraXformOps)
                {
                    extraTransform *= extraOp.GetOpTransform(timecode);
                }
                const GfMatrix4d extraTransformInv = extraTransform.GetInverse();
                mtx = mtx * extraTransformInv;

                PXR_NS::GfVec3d translationNew;
                PXR_NS::GfVec3d rotationNew;
                PXR_NS::GfMatrix4d rotMat(1.0);
                PXR_NS::GfVec3d scaleNew(1.0);
                PXR_NS::GfMatrix4d scaleOrientMatUnused, perspMatUnused;
                mtx.Factor(
                    &scaleOrientMatUnused, &scaleNew, &rotMat, &translationNew, &perspMatUnused);

                static const PXR_NS::GfVec3d kAxis[] = { PXR_NS::GfVec3d::XAxis(), PXR_NS::GfVec3d::YAxis(),
                                                         PXR_NS::GfVec3d::ZAxis() };

                auto decompRot = rotMat.ExtractRotation().Decompose(
                    kAxis[rotationOrder[2]], kAxis[rotationOrder[1]], kAxis[rotationOrder[0]]);

                PXR_NS::GfVec3i indexOrder;
                for (int32_t i = 0; i < 3; i++)
                {
                    indexOrder[rotationOrder[i]] = 2 - i;
                }

                rotationNew[0] = decompRot[indexOrder[0]];
                rotationNew[1] = decompRot[indexOrder[1]];
                rotationNew[2] = decompRot[indexOrder[2]];

                translation = translationNew;
                rotationEuler = rotationNew;
                scale = scaleNew;
            }
            else
            {
                // Post transform, we should know what to do
                for (const UsdGeomXformOp& extraOp : extraXformOps)
                {
                    if (extraOp.GetOpType() == UsdGeomXformOp::Type::TypeScale)
                    {
                        PXR_NS::GfVec3d scaleValue;
                        extraOp.GetAs<>(&scaleValue, timecode);
                        scale = PXR_NS::GfCompDiv(scale, scaleValue);
                    }
                    else if (extraOp.GetOpType() == UsdGeomXformOp::Type::TypeRotateX)
                    {
                        double rotValue;
                        extraOp.GetAs<>(&rotValue, timecode);

                        if (PXR_NS::GfIsClose(abs(rotValue), 90.0, 0.01))
                        {
                            rotationEuler[0] = rotationEuler[0] - rotValue;
                            std::swap(scale[1], scale[2]);
                        }
                        else
                        {
                            CARB_LOG_WARN(
                                "UnitsResolve rotateX supports only +-90 degree on prim: %s", prim.GetPrimPath().GetText());
                        }
                    }
                }
            }
        }

        // If transformOp is not found, make individual xformOp or reuse old ones.
        if (!foundTransformOp)
        {
            // Don't use UsdGeomXformCommonAPI. It can only manipulate a very limited subset of xformOpOrder
            // combinations Do it manually as non-destructively as possible
            UsdGeomXformOp xformOp;
            std::vector<UsdGeomXformOp> newXformOps;
            newXformOps.reserve(5);  // SRT + pivot and pivot inv

            if (!extraXformOps.empty() && preTransformStack)
            {
                for (auto& copyXformOp : extraXformOps)
                {
                    newXformOps.push_back(copyXformOp);
                }
            }

            auto findOrAdd = [&xformOps, &xformOpOrders, &xform, &changeBlock, &fastUpdates](
                                 UsdGeomXformOp::Type xformOpType, UsdGeomXformOp& outXformOp, bool createIfNotExist,
                                 UsdGeomXformOp::Precision& precision, TfToken const& opSuffix = TfToken()) {
                TfToken expectedOpName = UsdGeomXformOp::GetOpName(xformOpType, opSuffix);
                for (auto& xformOp : xformOps)
                {
                    if (xformOp.GetOpType() == xformOpType)
                    {
                        // To differentiate translate and translate:pivot
                        TfToken opName = xformOp.GetOpName();
                        if (opName == expectedOpName)
                        {
                            precision = xformOp.GetPrecision();
                            outXformOp = xformOp;
                            return true;
                        }
                    }
                }

                if (createIfNotExist)
                {
                    // It is not safe to create new xformOps inside of SdfChangeBlocks, since
                    // new attribute creation via anything above Sdf API requires the PcpCache
                    // to be up to date. Flush the current change block before creating
                    // the new xformOp.
                    changeBlock.reset(nullptr);
                    if (std::find(xformOpOrders.begin(), xformOpOrders.end(), expectedOpName) == xformOpOrders.end())
                    {
                        outXformOp = xform.AddXformOp(xformOpType, precision, opSuffix);
                    }
                    else
                    {
                        // Sometimes XformOp attributes and XformOpOrder don't match. GetOrderedXformOps() considers
                        // both XformOp attributes and XformOpOrder. But AddXformOp() considers only XformOpOrder. So we
                        // need to fix it here.
                        auto opAttr = xform.GetPrim().CreateAttribute(
                            expectedOpName, UsdGeomXformOp::GetValueTypeName(xformOpType, precision), false);
                        outXformOp = UsdGeomXformOp(opAttr);
                    }

                    // Create a new change block to batch the subsequent authoring operations
                    // where possible.
                    changeBlock.reset(new SdfChangeBlock());
                    // Creation may have failed for a variety of reasons (including instanceable=True)
                    return static_cast<bool>(outXformOp);
                }
                return false;
            };

            auto getFirstRotateOpType = [&xformOps](UsdGeomXformOp::Precision& precision) {
                for (auto& xformOp : xformOps)
                {
                    if (xformOp.GetOpType() >= UsdGeomXformOp::Type::TypeRotateX &&
                        xformOp.GetOpType() <= UsdGeomXformOp::Type::TypeOrient &&
                        !xformOp.HasSuffix(kUnitsResolve))
                    {
                        precision = xformOp.GetPrecision();
                        return xformOp.GetOpType();
                    }
                }
                return UsdGeomXformOp::Type::TypeInvalid;
            };

            auto setEulerValue = [&rotationEuler, &findOrAdd, &newXformOps](
                                     UsdGeomXformOp::Type rotationType, UsdGeomXformOp::Precision precision,
                                     UsdTimeCode timecode, bool skipEqualSetForTimeSample) {
                bool ret = false;
                UsdGeomXformOp xformOp;
                if (findOrAdd(rotationType, xformOp, true, precision))
                {
                    ret = setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(
                        xformOp, rotationEuler, timecode, skipEqualSetForTimeSample);
                    newXformOps.push_back(xformOp);
                }
                return ret;
            };

            // Set translation
            UsdGeomXformOp::Precision precision = UsdGeomXformOp::PrecisionDouble;
            if (findOrAdd(UsdGeomXformOp::TypeTranslate, xformOp, true, precision))
            {
                success &= setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(
                    xformOp, translation, timecode, skipEqualSetForTimeSample);
                newXformOps.push_back(xformOp);
            }

            // Set pivot
            precision = UsdGeomXformOp::PrecisionFloat;
            UsdGeomXformOp pivotOp;
            static const TfToken kPivot = TfToken("pivot");
            const bool hasPivot = findOrAdd(UsdGeomXformOp::TypeTranslate, pivotOp, false, precision, kPivot);
            UsdGeomXformOp pivotOpInv;
            if (hasPivot)
            {
                newXformOps.push_back(pivotOp);
                for (size_t k = xformOps.size();k--;)
                {
                    if (xformOps[k].IsInverseOp() && xformOps[k].HasSuffix(kPivot))
                    {
                        pivotOpInv = xformOps[k];
                        break;
                    }
                }
            }

            // Set rotation
            precision = UsdGeomXformOp::PrecisionFloat;
            auto firstRotateOpType = getFirstRotateOpType(precision);

            struct HashFn
            {
                size_t operator()(const GfVec3i& vec) const
                {
                    return hash_value(vec);
                }
            };

            static const std::unordered_map<GfVec3i, UsdGeomXformOp::Type, HashFn> kRotationOrderToTypeMap{
                { { 0, 1, 2 }, UsdGeomXformOp::TypeRotateXYZ }, { { 0, 2, 1 }, UsdGeomXformOp::TypeRotateXZY },
                { { 1, 0, 2 }, UsdGeomXformOp::TypeRotateYXZ }, { { 1, 2, 0 }, UsdGeomXformOp::TypeRotateYZX },
                { { 2, 0, 1 }, UsdGeomXformOp::TypeRotateZXY }, { { 2, 1, 0 }, UsdGeomXformOp::TypeRotateZYX },
            };

            if (firstRotateOpType == UsdGeomXformOp::TypeInvalid)
            {
                const char* defaultOpXformType =
                    carb::getCachedInterface<carb::settings::ISettings>()->getStringBuffer(kDefaultXforOpTypeSettingPath);

                if (defaultOpXformType &&
                    strncmp(defaultOpXformType, "Scale, Orient, Translate", sizeof("Scale, Orient, Translate") - 1) == 0)
                {
                    firstRotateOpType = UsdGeomXformOp::TypeOrient;
                }
                else
                {
                    // TODO what if default_xform_ops == "Transform" ?
                    // If no rotation was defined on the prim, use rotationOrder as default
                    const auto orderEntry = kRotationOrderToTypeMap.find(rotationOrder);
                    if (orderEntry != kRotationOrderToTypeMap.end())
                    {
                        firstRotateOpType = orderEntry->second;
                    }
                }
            }

            switch (firstRotateOpType)
            {
            case UsdGeomXformOp::TypeRotateX:
            case UsdGeomXformOp::TypeRotateY:
            case UsdGeomXformOp::TypeRotateZ:
            {
                // Add in reverse order
                for (int32_t i = 2; i >= 0; i--)
                {
                    size_t axis = rotationOrder[i];
                    if (findOrAdd(static_cast<UsdGeomXformOp::Type>(UsdGeomXformOp::TypeRotateX + axis), xformOp, true,
                                  precision))
                    {
                        success &= setValueWithPrecision<GfHalf, float, double, double>(
                            xformOp, rotationEuler[axis], timecode, skipEqualSetForTimeSample);
                        newXformOps.push_back(xformOp);
                    }
                }

                break;
            }
            case UsdGeomXformOp::TypeRotateXYZ:
            case UsdGeomXformOp::TypeRotateXZY:
            case UsdGeomXformOp::TypeRotateYXZ:
            case UsdGeomXformOp::TypeRotateYZX:
            case UsdGeomXformOp::TypeRotateZXY:
            case UsdGeomXformOp::TypeRotateZYX:
            {
                UsdGeomXformOp::Type providedRotationOrder = firstRotateOpType;
                const auto orderEntry = kRotationOrderToTypeMap.find(rotationOrder);
                if (orderEntry != kRotationOrderToTypeMap.end())
                {
                    providedRotationOrder = orderEntry->second;
                }

                if (providedRotationOrder != firstRotateOpType)
                {
                    CARB_LOG_WARN(
                        "Existing rotation order on prim %s is different than desired (%d, %d, %d), overriding...",
                        prim.GetPrimPath().GetText(), rotationOrder[0], rotationOrder[1], rotationOrder[2]);
                }
                success &= setEulerValue(providedRotationOrder, precision, timecode, skipEqualSetForTimeSample);
                break;
            }
            case UsdGeomXformOp::TypeOrient:
                if (findOrAdd(UsdGeomXformOp::TypeOrient, xformOp, true, precision))
                {
                    static const GfVec3d kAxes[] = { GfVec3d::XAxis(), GfVec3d::YAxis(), GfVec3d::ZAxis() };
                    GfRotation rotation = GfRotation(kAxes[rotationOrder[0]], rotationEuler[rotationOrder[0]]) *
                                          GfRotation(kAxes[rotationOrder[1]], rotationEuler[rotationOrder[1]]) *
                                          GfRotation(kAxes[rotationOrder[2]], rotationEuler[rotationOrder[2]]);

                    success &= setValueWithPrecision<GfQuath, GfQuatf, GfQuatd, GfQuatd>(
                        xformOp, rotation.GetQuat(), timecode, skipEqualSetForTimeSample);
                    newXformOps.push_back(xformOp);
                }
                break;
            default:
                CARB_LOG_ERROR("Failed to determine rotation order");
            }

            // Set scale
            precision = UsdGeomXformOp::PrecisionFloat;
            if (findOrAdd(UsdGeomXformOp::TypeScale, xformOp, true, precision))
            {
                success &= setValueWithPrecision<GfVec3h, GfVec3f, GfVec3d, GfVec3d>(
                    xformOp, scale, timecode, skipEqualSetForTimeSample);
                newXformOps.push_back(xformOp);
            }


            // Set extra ops from units resolve
            if (!extraXformOps.empty() && !preTransformStack)
            {
                for (auto& copyXformOp : extraXformOps)
                {
                    newXformOps.push_back(copyXformOp);
                }
            }

            // Set inverse pivot
            if (hasPivot && pivotOpInv)
            {
                newXformOps.push_back(pivotOpInv);
            }

            success &= xform.SetXformOpOrder(newXformOps, resetXFormStack);
        }
        else
        {
            const GfMatrix4d mtx = constructTransformMatrixFromSRT(translation, rotationEuler, rotationOrder, scale);
            const GfMatrix4d innerMtx =
                findInnerTransform(prim, mtx, foundTransformOp, timecode, skipEqualSetForTimeSample);

            success &= UsdUtils::setAttribute(transformOp.GetAttr(), innerMtx, timecode, skipEqualSetForTimeSample);
        }

        return success;
    }

    /**
     * Sets local transform of a prim from its world transform matrix.
     *
     * @param prim The prim to set local transform matrix to.
     * @param time Current timecode.
     * @param mtx The world transform matrix.
     */
    static bool setLocalTransformFromWorldTransformMatrix(pxr::UsdPrim prim,
                                                          const pxr::GfMatrix4d& mtx,
                                                          pxr::UsdTimeCode timeCode = pxr::UsdTimeCode::Default(),
                                                          bool skipEqualSetForTimeSample = false)
    {
        pxr::GfMatrix4d parentToWorldMat = pxr::UsdGeomXformable(prim).ComputeParentToWorldTransform(timeCode);
        pxr::GfMatrix4d worldToParentMat = parentToWorldMat.GetInverse();

        return UsdUtils::setLocalTransformMatrix(prim, mtx * worldToParentMat, timeCode, skipEqualSetForTimeSample);
    }

    /**
     * Creates a reference prim from external USD asset.
     *
     * @param stage The stage to create reference prim on.
     * @param refUrl The URL of the reference asset.
     * @param primPath The path to create the reference prim at.
     * @param warningMsg Output warning message during the process.
     * @param prependDefaultPrimPath Whether to check under defaultPrim path or stage root.
     */
    static pxr::UsdPrim createExternalRefNodeAtPath(pxr::UsdStageWeakPtr stage,
                                                    const char* refUrl,
                                                    const char* primPath,
                                                    std::string& warningMsg,
                                                    bool prependDefaultPrimPath = true,
                                                    bool adjustLayerOffset = true)
    {
        pxr::UsdPrim prim;
        std::string newPrimPath = findNextNoneExisitingNodePath(stage, primPath, prependDefaultPrimPath);

        std::string refUrlStr(refUrl);
        std::replace(refUrlStr.begin(), refUrlStr.end(), '\\', '/');

        std::string relativeUrl = refUrlStr;
        if (!makePathRelativeToLayer(stage->GetEditTarget().GetLayer(), relativeUrl))
        {
#if CARB_PLATFORM_LINUX
            // makePathRelativeToLayer returns false, it is a absolute path.
            auto omniclient = carb::getCachedInterface<carb::omniclient::IOmniClient>();

            carb::omniclient::OmniClientUrlPtr url(omniclient, relativeUrl.c_str());
            if (!url->scheme || url->scheme[0] == '\0')
            {
                relativeUrl = carb::omniclient::makeFileUrl(omniclient, relativeUrl.c_str());
            }
#endif
        }

        carb::settings::ISettings* settings = carb::getFramework()->acquireInterface<carb::settings::ISettings>();
        bool xformForTypelessRef = settings->getAsBool(kCreateXformForTypelessReferenceSettingPath);
        bool explictRefForNoneDefaultPrim = settings->getAsBool(kCreateExplicitRefForNoneDefaultPrimSettingPath);

        pxr::UsdStageRefPtr refStage = pxr::UsdStage::Open(refUrl, pxr::UsdStage::InitialLoadSet::LoadNone);
        if (refStage)
        {
            PXR_NS::SdfLayerOffset layerOffset;
            if (adjustLayerOffset)
                layerOffset.SetScale(stage->GetTimeCodesPerSecond() / refStage->GetTimeCodesPerSecond());

            if (refStage->HasDefaultPrim() && refStage->GetDefaultPrim())
            {
                auto defaultPrim = refStage->GetDefaultPrim();
                const std::string& typeName = defaultPrim.GetTypeName().GetString();

                if (typeName.empty() && xformForTypelessRef)
                {
                    warningMsg =
                        "The defaultPrim of this USD is typeless. Overriding it to Xform. Do not rely on this behavior, it will be removed at anytime.";

                    // If the defaultPrim is typeless,
                    // define a root Xfrom node for the external refs so it can be moved around
                    prim = pxr::UsdGeomXform::Define(stage, pxr::SdfPath(newPrimPath)).GetPrim();
                }
                else
                {
                    prim = stage->DefinePrim(pxr::SdfPath(newPrimPath));
                }

                if (prim)
                {
                    // If has DefaultPrim, reference it directly.
                    auto ref = prim.GetReferences();
                    ref.AddReference(relativeUrl, layerOffset);
                }
            }
            else if (explictRefForNoneDefaultPrim)
            {
                if (refStage->HasDefaultPrim() && !refStage->GetDefaultPrim())
                {
                    warningMsg =
                        "The USD file has a defaultPrim but references an invalid prim, creating explicit reference for each root-level object. Do not rely on this behavior, it will be removed at anytime.";
                }
                else if (!refStage->HasDefaultPrim())
                {
                    warningMsg =
                        "There's no defaultPrim in this USD file, creating explicit reference for each root-level object. Do not rely on this behavior, it will be removed at anytime.";
                }

                // Define a root Xfrom node for the external refs
                prim = pxr::UsdGeomXform::Define(stage, pxr::SdfPath(newPrimPath)).GetPrim();

                // If has no defaultPrim, reference each root level Prim individually.
                auto refRoot = refStage->GetPseudoRoot();
                auto refRootDirectChildren = refRoot.GetAllChildren();

                // iterate through all root level children and create reference for them
                for (const auto& child : refRootDirectChildren)
                {
                    std::string newPath = newPrimPath + child.GetPrimPath().GetString();
                    auto subPrim = stage->DefinePrim(pxr::SdfPath(newPath));
                    if (subPrim)
                    {
                        auto ref = subPrim.GetReferences();
                        ref.AddReference(relativeUrl, child.GetPrimPath(), layerOffset);
                    }
                    else
                    {
                        CARB_LOG_WARN("Failed to import %s from %s", child.GetPrimPath().GetText(), refUrl);
                    }
                }
            }

            if (prim)
            {
                // Get the timeline of the referenced stage and extend current stage timeline if needed.
                double refStartTimeCode = refStage->GetStartTimeCode();
                double refEndTimeCode = refStage->GetEndTimeCode();
                double refTimeCodePerSecond = refStage->GetTimeCodesPerSecond();

                double startTimeCode = stage->GetStartTimeCode();
                double endTimeCode = stage->GetEndTimeCode();
                double timeCodePerSecond = stage->GetTimeCodesPerSecond();

                if (refStartTimeCode < startTimeCode)
                {
                    UsdUtils::ScopedLayerEdit scopedLayerEdit(stage, stage->GetRootLayer());
                    stage->SetStartTimeCode(refStartTimeCode);
                }
                if (refEndTimeCode > endTimeCode)
                {
                    UsdUtils::ScopedLayerEdit scopedLayerEdit(stage, stage->GetRootLayer());
                    stage->SetEndTimeCode(refEndTimeCode);
                }

                // Also warn if fps of referenced
                if (refTimeCodePerSecond != timeCodePerSecond)
                {
                    warningMsg =
                        "Referenced USD file TimeCodesPerSecond does not match current USD file TimeCodesPerSecond.";
                }
            }
        }

        if (!prim)
        {
            warningMsg = std::string("Could not create reference from ") + refUrl;
        }

        return prim;
    }

    /**
     * Gets the enclosing model of given prim.
     *
     * @param prim The prim to get enclosing model from.
     * @return The enclosing model of given prim.
     */
    static pxr::UsdPrim getEnclosingModelPrim(pxr::UsdPrim prim)
    {
        // Code partially ported from USD\pxr\usdImaging\lib\usdviewq\common.py
        while (prim)
        {
            pxr::UsdModelAPI modelApi(prim);

            pxr::TfToken kind;
            modelApi.GetKind(&kind);

            if (pxr::KindRegistry::IsA(kind, pxr::KindTokens->model))
            {
                break;
            }

            prim = prim.GetParent();
        }
        return prim;
    }

    /**
     * Takes an absolute path and makes it relative to a layer.
     *
     * @param layer The layer to make path relative to.
     * @param path The absolute path to be converted in place.
     * @return true if the conversion is successful, false if failed to make relative path (possible reasons: layer is
     * in-memory only, layer and path have different protocol (omni: vs file:), layer and path are on different Window
     * drive etc.).
     */
    static bool makePathRelativeToLayer(pxr::SdfLayerHandle layer, std::string& path)
    {
        if (layer->IsAnonymous() || PXR_NS::SdfLayer::IsAnonymousLayerIdentifier(path))
        {
            return false;
        }

        std::string realPath = layer->GetRealPath();
        std::string externRefPathRelative;
        if (makeRelativePathTo(path, realPath, externRefPathRelative))
        {
            path = externRefPathRelative;
            return true;
        }
        else
        {
            CARB_LOG_INFO("Cannot make '%s' relative to '%s'", path.c_str(), realPath.c_str());
        }
        return false;
    }

    /**
     * Removes a property from all layer specs.
     *
     * @param stage The stage to remove property.
     * @param primPath The parent prim path of the property to be removed.
     * @param propertyName Name of the property to be removed.
     * @return true if property has been removed from at least one layer.
     */
    static bool removeProperty(pxr::UsdStageWeakPtr stage, const pxr::SdfPath& primPath, const pxr::TfToken& propertyName)
    {
        bool ret = false;
        auto layerStack = stage->GetLayerStack();
        for (auto&& layer : layerStack)
        {
            auto primSpec = layer->GetPrimAtPath(primPath);
            if (primSpec)
            {
                auto propertySpec = layer->GetPropertyAtPath(primPath.AppendProperty(propertyName));
                if (propertySpec)
                {
                    primSpec->RemoveProperty(propertySpec);
                    ret |= true;
                }
            }
        }
        return ret;
    }

    /**
     * Gets the attribute value.
     *
     * @tparam T the data type of the attribute.
     * @param attribute The attribute to get value from.
     * @param time Current timecode.
     * @return the value of the attribute.
     */
    template <class T>
    static T getAttribute(pxr::UsdAttribute& attribute, pxr::UsdTimeCode time)
    {
        T val;
        attribute.Get(&val, time);
        return val;
    }

    /**
     * Gets the attribute array value.
     *
     * @tparam T The data type of the attribute array.
     * @param attribute The attribute to get value from.
     * @param out the value of the attribute.
     * @return True if the out value is valid.
     */
    template <typename T>
    static bool getAttributeArray(pxr::UsdAttribute& attribute, pxr::VtArray<T>& out, pxr::UsdTimeCode time)
    {
        pxr::VtValue arrayDataValue;
        attribute.Get(&arrayDataValue, time);
        if (arrayDataValue.GetArraySize())
        {
            out = arrayDataValue.Get<pxr::VtArray<T>>();
            return true;
        }
        return false;
    }

    /**
     * enum to show effective timesamples in layerstacks based on current authoring layer
     */
    enum class TimeSamplesOnLayer
    {
        eNoTimeSamples,
        eOnCurrentLayer,
        eOnStrongerLayer,
        eOnWeakerLayer
    };

    /**
     * check if attribute has efficient timesample and
     * these data are on currentlayer/strongerlayer/weakerlayer
     * @tparam Stage  Current Working Stage.
     * @param attribute The attribute to check.
     */
    static TimeSamplesOnLayer getAttributeEffectiveTimeSampleLayerInfo(const pxr::UsdStage& stage,
                                                                       const pxr::UsdAttribute& attr,
                                                                       pxr::SdfLayerRefPtr* outLayer = nullptr)
    {
        if (attr.GetNumTimeSamples() == 0)
            return TimeSamplesOnLayer::eNoTimeSamples;

        auto authoringLayer = stage.GetEditTarget().GetLayer();

        bool isOnStrongerLayer = true;
        const pxr::PcpLayerStackPtr& nodeLayers = attr.GetResolveInfo().GetNode().GetLayerStack();
        const pxr::SdfLayerRefPtrVector& layerStack = nodeLayers->GetLayers();
        for (auto layer : layerStack)
        {
            auto attrSpec = layer->GetAttributeAtPath(attr.GetPath());
            if (attrSpec && attrSpec->GetTimeSampleMap().size() > 0)
            {
                if (outLayer)
                {
                    *outLayer = layer;
                }
                if (layer == authoringLayer)
                {
                    return TimeSamplesOnLayer::eOnCurrentLayer;
                }
                else if (isOnStrongerLayer)
                {
                    return TimeSamplesOnLayer::eOnStrongerLayer;
                }
                else
                {
                    return TimeSamplesOnLayer::eOnWeakerLayer;
                }
            }
            else
            {
                if (layer == authoringLayer)
                {
                    isOnStrongerLayer = false;
                }
            }
        }
        return TimeSamplesOnLayer::eNoTimeSamples;
    }
    /**
     * Copy TimeSample From Waker Layer.
     *
     * @param Stage  Current Working Stage.
     * @param attribute The attribute to check.
     */
    static void copyTimeSamplesFromWeakerLayer(pxr::UsdStage& stage, const pxr::UsdAttribute& attr)
    {
        pxr::SdfLayerRefPtr outLayer;
        if (getAttributeEffectiveTimeSampleLayerInfo(stage, attr, &outLayer) == TimeSamplesOnLayer::eOnWeakerLayer)
        {
            pxr::SdfTimeSampleMap timesamples;
            if (attr.GetMetadata(pxr::TfToken("timeSamples"), &timesamples))
            {
                attr.SetMetadata(pxr::TfToken("timeSamples"), timesamples);
            }
        }
    }

    /**
     * Sets attribute value.
     *
     * @tparam T The data type of the attribute.
     * @param attribute The attribute to set value to.
     * @param val The value to set.
     * @param autoTargetSessionLayer whether the edit target should auto switch to session layer.
     * @return true if set is successfully.
     */
    template <class ValueType>
    static bool setAttribute(const pxr::UsdAttribute& attribute,
                             const ValueType& val,
                             pxr::UsdTimeCode timeCode = pxr::UsdTimeCode::Default(),
                             bool skipEqualSetForTimeSample = false,
                             bool autoTargetSessionLayer = true)
    {
        PXR_NS::UsdTimeCode setTimeCode = timeCode;
        if (!isTimeSampled(attribute))
        {
            setTimeCode = PXR_NS::UsdTimeCode::Default();
        }

        // This is here to prevent the TransformGizmo from writing a translation, rotation and scale on every
        // key where it sets a value. At some point we should revisit the gizmo to simplify the logic, and
        // start setting only the transform value the user intends.
        if (skipEqualSetForTimeSample)
        {
            if (!setTimeCode.IsDefault() && !hasTimeSample(attribute, setTimeCode))
            {
                ValueType value;
                bool result = attribute.Get(&value, timeCode);
                if (result && PXR_NS::GfIsClose(value, val, 1e-6))
                {
                    return false;
                }
            }
        }

        // if the prim is defined on session layer, or the attribute itself is on session layer, switch EditTarget to session layer instead
        std::unique_ptr<PXR_NS::UsdEditContext> editCtx;
        auto stage = attribute.GetStage();
        if (autoTargetSessionLayer)
        {
            // check first if the attribute is on session layer
            auto sessionOrSubLayer = getLayerIfSpecOnSessionOrItsSublayers(stage, attribute.GetPath());
            if (!sessionOrSubLayer)
            {
                // if attribute doesn't exist, fallback to prim "def" (but not "over")
                sessionOrSubLayer = getLayerIfDefOnSessionOrItsSublayers(stage, attribute.GetPrim().GetPath());
            }
            if (sessionOrSubLayer)
            {
                editCtx = std::make_unique<PXR_NS::UsdEditContext>(stage, sessionOrSubLayer);
            }
        }

        if (!setTimeCode.IsDefault())
        {
            copyTimeSamplesFromWeakerLayer(*stage, attribute);
        }

        return attribute.Set(val, setTimeCode);
    }

    static bool getDefaultPrimName(const pxr::UsdStageRefPtr stage, std::string& defaultPrimName)
    {
        if (stage && stage->HasDefaultPrim())
        {
            defaultPrimName = stage->GetDefaultPrim().GetName();
            return true;
        }
        return false;
    }

    static pxr::UsdStageRefPtr getUsdStageFromId(long int stageId)
    {
        return pxr::UsdUtilsStageCache::Get().Find(pxr::UsdStageCache::Id::FromLongInt(stageId));
    }

    static bool isSameDriveOrProtocol(const std::string& path1, const std::string& path2)
    {
        auto absolutePathArray = tokenizePath(path1);
        auto anchorPathArray = tokenizePath(path2);

        if (absolutePathArray.size() > 0 && anchorPathArray.size() > 0)
        {
            const std::string& protocolOrDrivePath = absolutePathArray.front();
            const std::string& protocolOrDriveAnchor = anchorPathArray.front();

            return isSameDriveOrProtocolInternal(protocolOrDrivePath, protocolOrDriveAnchor);
        }

        return false;
    }

    static std::string findNextNoneExisitingNodePath(pxr::UsdStageWeakPtr stage,
                                                     std::string path,
                                                     bool prependDefaultPrimPath)
    {
        uint64_t dupSuffix = 2;
        pxr::UsdPrim oldPrim;
        std::string newPrimPath;

        // Do not support dot in the path
        std::replace(path.begin(), path.end(), '.', '_');

        // Do not support Prim names begin with a number in any part of the path
        // Add a "_" in front of any section that starts with number. e.g. /1foo/2bar/baz -> /_1foor/_2bar/baz
        static const std::regex kNodeNameStartsWithNumber(
            "(\\/)([0-9])", std::regex_constants::icase | std::regex_constants::optimize);
        path = std::regex_replace(path, kNodeNameStartsWithNumber, "/_$2");

        if (prependDefaultPrimPath && stage->HasDefaultPrim())
        {
            auto defaultPrim = stage->GetDefaultPrim();
            if (defaultPrim)
            {
                path = stage->GetDefaultPrim().GetPath().GetString() + path;
            }
        }

        std::string oldPrimTestPath = path;

        // Find out if the path already has a dup suffix number
        static const std::regex kNodeNameEndsWithUnderscoreNumber(
            "(_)([0-9]+)$", std::regex_constants::icase | std::regex_constants::optimize);
        std::smatch m;
        if (std::regex_search(path, m, kNodeNameEndsWithUnderscoreNumber))
        {
            std::string dupSuffixStr = m[m.size() - 1];
            dupSuffix = std::strtoul(dupSuffixStr.c_str(), nullptr, 0);
            path = m.prefix();
        }

        for (;;)
        {
            // If the node already exists, append a "_n" to the end
            oldPrim = stage->GetPrimAtPath(pxr::SdfPath(oldPrimTestPath));
            if (oldPrim.IsValid())
            {
                oldPrimTestPath = std::string(path) + "_" + std::to_string(dupSuffix++);
            }
            else
            {
                newPrimPath = oldPrimTestPath;
                break;
            }
        }
        return newPrimPath;
    }

    static PXR_NS::SdfPathVector fromStringArray(const char** stringArray, size_t count)
    {
        PXR_NS::SdfPathVector sdfPaths(count);
        for (size_t i = 0; i < count; i++)
        {
            sdfPaths[i] = PXR_NS::SdfPath(stringArray[i]);
        }

        return sdfPaths;
    }

    static PXR_NS::SdfPathVector fromStringArray(const std::vector<std::string>& stringArray)
    {
        PXR_NS::SdfPathVector sdfPaths(stringArray.size());
        for (size_t i = 0; i < stringArray.size(); i++)
        {
            sdfPaths[i] = PXR_NS::SdfPath(stringArray[i]);
        }

        return sdfPaths;
    }

    static std::vector<std::string> toStringArray(const PXR_NS::SdfPathVector& paths)
    {
        std::vector<std::string> stringArray(paths.size());
        for (size_t i = 0; i < paths.size(); i++)
        {
            stringArray[i] = paths[i].GetString();
        }

        return stringArray;
    }


    /**
     * Finds if the given path (prim/attribute/property/object/etc) has a spec on session layer or its sublayers.
     *
     * @param stage of the prim.
     * @param path The path to be checked for spec.
     * @param predicate additional predicate to be called if spec is found on the layer.
     *
     * @return the layer that has spec at given path, or nullptr if not found.
     */
    static PXR_NS::SdfLayerRefPtr getLayerIfSpecOnSessionOrItsSublayers(
        PXR_NS::UsdStageRefPtr stage,
        const PXR_NS::SdfPath& path,
        const std::function<bool(PXR_NS::SdfSpecHandle)>& predicate = nullptr)
    {
        const auto rootLayer = stage->GetRootLayer();
        const auto layerStack = stage->GetLayerStack(true);

        auto hasSpec = [&path, &predicate](PXR_NS::SdfLayerRefPtr layer)
        {
            auto spec = layer->GetObjectAtPath(path);

            return spec && (!predicate || predicate(spec));
        };

        for (const auto& layer : layerStack)
        {
            // session layers always come before root layer. We're only interested in session and its
            // sublayers, break when hit root layer.
            if (layer == rootLayer)
            {
                break;
            }

            if (hasSpec(layer))
            {
                return layer;
            }
        }

        return nullptr;
    }

    /**
     * Finds if the given *prim* path has a "def" *primSpec* on session layer or its sublayers.
     * If you want to find attributeSpec use @ref getLayerIfSpecOnSessionOrItsSublayers instead.
     *
     * @stage stage of the prim.
     * @param path The path to be checked for "def" primSpec.
     *
     * @return the layer that has "def" prim spec, or nullptr if not found.
     */
    static PXR_NS::SdfLayerRefPtr getLayerIfDefOnSessionOrItsSublayers(PXR_NS::UsdStageRefPtr stage,
                                                                       const PXR_NS::SdfPath& path)
    {
        return getLayerIfSpecOnSessionOrItsSublayers(
            stage, path,
            [](PXR_NS::SdfSpecHandle spec)
            {
                auto primSpec = PXR_NS::SdfSpecStatic_cast<PXR_NS::SdfPrimSpecHandle>(spec);
                return primSpec && PXR_NS::SdfIsDefiningSpecifier(primSpec->GetSpecifier());
            });
    }


    /*
     * This function will find the local layer that defines this prim, or the first introducing
     * layer that introduces the prim into the local layer stack if prim is defined in a reference
     * or payload. An introducing layer is the layer that adds the prim into the composition graph.
     *
     * The difference of this function to Usd.PrimCompositionQuery is that it will return
     * the first local layer where the prim is defined. If it's not defined locally, it will find
     * the reference or payload arcs with Usd.PrimCompositionQuery to find the first introducing
     * layer and its introducing prim path in the local layer stack.
     *
     * @param prim Prim handle
     * @param[out] introducingLayer introducing layer of the prim.
     * @param[out] introducingPath introducing layer of the prim.
     *
     * @returns true if introducingLayer and introducingPath is successfully obtained. false otherwise.
     */
    static bool getIntroducingLayer(const PXR_NS::UsdPrim& prim,
                                           PXR_NS::SdfLayerHandle& introducingLayer,
                                           PXR_NS::SdfPath& introducingPath)
    {
        const auto stage = prim.GetStage();
        const auto& primStack = prim.GetPrimStack();
        for (const auto& primSpec: primStack)
        {
            if (PXR_NS::SdfIsDefiningSpecifier(primSpec->GetSpecifier()) && stage->HasLocalLayer(primSpec->GetLayer()))
            {
                introducingLayer = primSpec->GetLayer();
                introducingPath = primSpec->GetPath();
                return true;
            }
        }

        auto query = PXR_NS::UsdPrimCompositionQuery(prim);
        auto qFilter = PXR_NS::UsdPrimCompositionQuery::Filter();
        qFilter.arcTypeFilter = PXR_NS::UsdPrimCompositionQuery::ArcTypeFilter::ReferenceOrPayload;
        qFilter.arcIntroducedFilter = PXR_NS::UsdPrimCompositionQuery::ArcIntroducedFilter::IntroducedInRootLayerStack;
        query.SetFilter(qFilter);
        const auto arcs = query.GetCompositionArcs();
        for (const auto& arc : arcs)
        {
            auto layer = arc.GetIntroducingLayer();
            if (layer)
            {
                introducingLayer = layer;
                introducingPath = arc.GetIntroducingPrimPath();
                return true;
            }
        }
        return false;
    }

private:
    static std::list<std::string> tokenizePath(std::string path)
    {
        std::list<std::string> result;
        for (;;)
        {
            size_t pos = path.find_first_of('/');
            if (pos == std::string::npos)
            {
                if (!path.empty())
                {
                    result.push_back(path);
                }
                break;
            }
            else
            {
                std::string token = path.substr(0, pos);
                if (!token.empty())
                {
                    result.push_back(token);
                }
                path = path.substr(pos + 1);
            }
        }
        return result;
    }

    static bool isSameDriveOrProtocolInternal(const std::string& protocol1, const std::string& protocol2)
    {
        // If E: or omni:
        if (protocol1.length() && protocol2.length() && protocol1.back() == ':' && protocol2.back() == ':')
        {
            if (protocol1.length() == protocol2.length())
            {
#if CARB_PLATFORM_WINDOWS
                constexpr auto strncasecmp = _strnicmp;
#endif
                if (strncasecmp(protocol1.c_str(), protocol2.c_str(), protocol1.length()) == 0)
                {
                    return true;
                }
            }
        }
        return false;
    }

    static bool makeRelativePathTo(const std::string& absolutePath, const std::string& anchor, std::string& relativePath)
    {
        auto omniclient = carb::getCachedInterface<carb::omniclient::IOmniClient>();
        if (omniclient)
        {
            std::string result;
            relativePath = carb::omniclient::makeRelativeUrl(omniclient, anchor.c_str(), absolutePath.c_str());
#if CARB_PLATFORM_WINDOWS
            carb::omniclient::OmniClientUrlPtr clientUrl(omniclient, relativePath.c_str());
            if (!clientUrl->scheme) // omniverse path can have '\'
            {
                std::replace(relativePath.begin(), relativePath.end(), '\\', '/');
            }
#endif
            return relativePath != absolutePath;
        }
        return false;
    }

    static bool checkAncestralNode(const pxr::PcpNodeRef& node)
    {
        bool isAncestral = node.IsDueToAncestor();
        if (!isAncestral)
        {
            using namespace pxr;
            TF_FOR_ALL(childIt, node.GetChildrenRange())
            {
                isAncestral |= checkAncestralNode(*childIt);
                if (isAncestral)
                {
                    break;
                }
            }
        }
        return isAncestral;
    }

    static bool checkAncestral(const pxr::UsdPrim& prim)
    {
        return checkAncestralNode(prim.GetPrimIndex().GetRootNode());
    }

    template <class HalfType, class FloatType, class DoubleType, class ValueType>
    static bool setValueWithPrecision(pxr::UsdGeomXformOp& xformOp,
                                      const ValueType& value,
                                      pxr::UsdTimeCode timeCode = pxr::UsdTimeCode::Default(),
                                      bool skipEqualSetForTimeSample = false)
    {
        switch (xformOp.GetPrecision())
        {
        case pxr::UsdGeomXformOp::PrecisionHalf:
            return UsdUtils::setAttribute(
                xformOp.GetAttr(), HalfType(FloatType(value)), timeCode, skipEqualSetForTimeSample);
        case pxr::UsdGeomXformOp::PrecisionFloat:
            return UsdUtils::setAttribute(xformOp.GetAttr(), FloatType(value), timeCode, skipEqualSetForTimeSample);
        case pxr::UsdGeomXformOp::PrecisionDouble:
            return UsdUtils::setAttribute(xformOp.GetAttr(), DoubleType(value), timeCode, skipEqualSetForTimeSample);
        }
        return false;
    }
};

/**
 * Gets the string attribute value.
 *
 * @param attribute The attribute to get value from.
 * @param time Current timecode.
 * @return the value of the attribute.
 */
template <> // Define it out of class body to avoid "Explicit specialization in non-namespace scope" error.
inline std::string UsdUtils::getAttribute(pxr::UsdAttribute& attribute, pxr::UsdTimeCode time)
{
    pxr::VtValue val;
    attribute.Get(&val, time);
    if (attribute.GetTypeName() == pxr::SdfValueTypeNames->String)
    {
        return val.Get<std::string>();
    }
    else if (attribute.GetTypeName() == pxr::SdfValueTypeNames->Asset)
    {
        auto path = val.Get<pxr::SdfAssetPath>();
        return path.GetAssetPath();
    }
    return "";
}
}
}
