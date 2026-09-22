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

#include <carb/extras/Path.h>
#include <carb/filesystem/IFileSystem.h>
#include <carb/profiler/Profile.h>
#include <carb/tokens/TokensUtils.h>
#include <carb/profiler/Profile.h>

#include <omni/kit/AssetUtils.h>
#include <omni/kit/KitUtils.h>
#include <omni/usd/UsdUtils.h>
#include <pxr/base/tf/pathUtils.h>
#include <pxr/pxr.h>
#include <pxr/usd/ar/resolver.h>
#include <pxr/usd/ar/resolverScopedCache.h>
#include <pxr/usd/sdf/assetPath.h>
#include <pxr/usd/sdf/copyUtils.h>
#include <pxr/usd/sdf/layerUtils.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdUtils/flattenLayerStack.h>

#include <random>

namespace omni
{
namespace usd
{
/**
 * USD does not provide the way to save muteness. Kit will save those inside the custom data of root layer
 * of the stage.
 */
static const std::string kLayerMuteCustomKey = "omni_layer:muteness";
static const std::string kLayerNameCustomKey = "omni_layer:custom_name";
static const std::string kLayerLockedCustomKey = "omni_layer:locked";
static constexpr size_t kLayerIndexNone = SIZE_MAX;

class LayerUtils
{
public:
    /**
     * Gets the global muteness. Global muteness is the one that's saved inside the custom data of stage's root layer.
     * @param stage Root layer to get muteness from.
     * @param layerIdentifier Layer identifier.
     * @return True if it muted, or false otherwise.
     */
    static bool getLayerGlobalMuteness(PXR_NS::SdfLayerRefPtr rootLayer, const std::string& layerIdentifier)
    {
        bool muted = false;
        getLayerCustomFieldInRootLayer<bool>(rootLayer, layerIdentifier, kLayerMuteCustomKey, muted);

        return muted;
    }

    /**
     * Set global muteness for layer.
     * @param rootLayer Root layer to save muteness to.
     * @param layerIdentifier Layer identifier.
     * @param muted Mute or not.
     * @return true if it's successful.
     */
    static void setLayerGlobalMuteness(PXR_NS::SdfLayerRefPtr rootLayer, const std::string& layerIdentifier, bool muted)
    {
        setLayerCustomFieldInRootLayer(rootLayer, layerIdentifier, kLayerMuteCustomKey, muted);
    }

    /**
     * Clear all muteness from stage.
     */
    static void clearLayerMutenessFromCustomFields(PXR_NS::SdfLayerRefPtr rootLayer)
    {
        auto rootLayerCustomData = rootLayer->GetCustomLayerData();
        rootLayerCustomData.EraseValueAtPath(kLayerMuteCustomKey);
        rootLayer->SetCustomLayerData(rootLayerCustomData);
    }

    /**
     * Set layer's muteness based on global muteness saved in custom fields from stage.
     */
    static void setLayerMuteStateFromCustomFields(PXR_NS::UsdStageRefPtr stage)
    {
        auto rootLayer = stage->GetRootLayer();
        auto rootLayerCustomData = rootLayer->GetCustomLayerData();
        const PXR_NS::VtValue* muteness = rootLayerCustomData.GetValueAtPath(kLayerMuteCustomKey);
        PXR_NS::VtDictionary mutenessDict;
        if (muteness && !muteness->IsEmpty())
        {
            mutenessDict = muteness->Get<PXR_NS::VtDictionary>();
        }

        std::vector<std::string> mutedLayers;
        std::vector<std::string> unmutedLayers;
        for (const auto& identifierMutenessPair : mutenessDict)
        {
            const std::string& layerIdentifier = rootLayer->ComputeAbsolutePath(identifierMutenessPair.first);
            bool muted = identifierMutenessPair.second.Get<bool>();
            if (muted != stage->IsLayerMuted(layerIdentifier))
            {
                if (muted)
                {
                    mutedLayers.push_back(layerIdentifier);
                }
                else
                {
                    unmutedLayers.push_back(layerIdentifier);
                }
            }
        }

        if (mutedLayers.size() > 0 || unmutedLayers.size() > 0)
        {
            stage->MuteAndUnmuteLayers(mutedLayers, unmutedLayers);
        }
    }

    // Checks if the layer can be saved to disk.
    static bool isLayerSavable(PXR_NS::UsdStageRefPtr stage, const std::string& layerIdentifier)
    {
        bool anonymous = PXR_NS::SdfLayer::IsAnonymousLayerIdentifier(layerIdentifier);
        bool locked = LayerUtils::isLayerLocked(stage->GetRootLayer(), layerIdentifier);
        bool muted = stage->IsLayerMuted(layerIdentifier);
        bool writable = omni::kit::isWritableUrl(layerIdentifier.c_str());;
        if (!anonymous && !locked && !muted && writable)
        {
            return true;
        }

        return false;
    }

    // Gets the customized layer lock status in root layer.
    static bool isLayerLocked(PXR_NS::SdfLayerRefPtr rootLayer, const std::string& layerIdentifier)
    {
        // Layer lock is a concept extended from Kit that does not use real ACL
        // from disk to control the lock of layer but only an instruction to
        // save that this layer is locked and should not be touched.
        bool locked = false;
        getLayerCustomFieldInRootLayer<bool>(rootLayer, layerIdentifier, kLayerLockedCustomKey, locked);

        return locked;
    }

    static void setLayerLockStatus(PXR_NS::SdfLayerRefPtr rootLayer, const std::string& layerIdentifier, bool locked)
    {
        setLayerCustomFieldInRootLayer(rootLayer, layerIdentifier, kLayerLockedCustomKey, locked);
    }

    static std::string getLayerName(const std::string& identifier, bool includeExtension = true)
    {
        if (PXR_NS::SdfLayer::IsAnonymousLayerIdentifier(identifier))
        {
            return identifier;
        }

        carb::extras::Path path;
        auto omniclient = carb::getCachedInterface<carb::omniclient::IOmniClient>();
        if (omniclient)
        {
            auto url = omniclient->breakUrl(identifier.c_str());
            if (url && url->path)
            {
                path = carb::extras::Path(url->path);
            }
            else
            {
                path = carb::extras::Path(identifier);
            }
        }
        else
        {
            path = carb::extras::Path(identifier);
        }

        if (includeExtension)
        {
            return path.getFilename().getString();
        }
        else
        {
            return path.getStem().getString();
        }
    }

    static std::string getCustomLayerName(PXR_NS::SdfLayerRefPtr layer)
    {
        PXR_NS::VtDictionary valueMap;
        const PXR_NS::VtDictionary& layerCustomData = layer->GetCustomLayerData();
        const auto& customDataValue = layerCustomData.GetValueAtPath(kLayerNameCustomKey);
        if (customDataValue && !customDataValue->IsEmpty())
        {
            auto value = customDataValue->Get<PXR_NS::TfToken>();
            return value.GetString();
        }
        else
        {
            return LayerUtils::getLayerName(layer->GetIdentifier());
        }
    }

    /**
     * Select a existing layer as edit target.
     *
     * @param stage The stage of the operation.
     * @param layerIdentifier Layer identifier.
     * @return true if the layer is selected, false otherwise.
     *
     **/
    static bool setAuthoringLayer(PXR_NS::UsdStageRefPtr stage, const std::string& layerIdentifier)
    {
        const auto& sublayer = PXR_NS::SdfLayer::Find(layerIdentifier);
        if (!sublayer || !stage->HasLocalLayer(sublayer))
        {
            return false;
        }

        PXR_NS::UsdEditTarget editTarget = stage->GetEditTargetForLocalLayer(sublayer);
        stage->SetEditTarget(editTarget);

        return true;
    }

    /**
     * Gets the current authoring layer (edit target).
     *
     * @param stage The stage of the operation.
     * @return layer identifier of the authoring layer.
     **/
    static std::string getAuthoringLayerIdentifier(PXR_NS::UsdStageRefPtr stage)
    {
        if (stage->GetEditTarget().GetLayer())
        {
            return stage->GetEditTarget().GetLayer()->GetIdentifier();
        }

        return "";
    }

    /**
     * Gets the layer identifier of sublayer at specific position.
     *
     * @param hostLayer Layer handle to query.
     * @param position Sublayer position. It should not be over the count of total sublayers.
     * @param sublayerIdentifier Returned identifier.
     * @return false if position is over the count of total sublayers, or true otherwise.
     */
    static bool getSublayerIdentifier(const PXR_NS::SdfLayerRefPtr& hostLayer,
                                      size_t position,
                                      std::string& sublayerIdentifier)
    {
        if (position >= hostLayer->GetNumSubLayerPaths())
        {
            return false;
        }

        const auto& sublayerPaths = hostLayer->GetSubLayerPaths();
        const std::string& sublayer = sublayerPaths[position];
        sublayerIdentifier = computeAbsolutePath(hostLayer, sublayer);

        return true;
    }

    /**
     * Gets sublayer position of specific layer in parent layer.
     *
     * @param hostLayer Parent layer to search.
     * @param layerIdentifier Layer identifier.
     * @return Sublayer position if it's found, or kLayerIndexNone if it's not found.
     */
    static size_t getSublayerPositionInHost(const PXR_NS::SdfLayerRefPtr& hostLayer, const std::string& layerIdentifier)
    {
        const auto& sublayerPaths = hostLayer->GetSubLayerPaths();
        for (size_t i = 0; i < sublayerPaths.size(); i++)
        {
            const auto& absolutePath = computeAbsolutePath(hostLayer, sublayerPaths[i]);
            if (normalizeUrl(absolutePath) == normalizeUrl(layerIdentifier))
            {
                return i;
            }
        }

        return kLayerIndexNone;
    }

    /**
     * Gets the sublayer handle at specific position.
     *
     * @param hostLayer Layer handle.
     * @param position Sublayer position.
     * @return layer handle if position is valid, otherwise, nullptr is returned.
     */
    static PXR_NS::SdfLayerRefPtr getSublayer(const PXR_NS::SdfLayerRefPtr& hostLayer, size_t position)
    {
        if (position >= hostLayer->GetNumSubLayerPaths())
        {
            return nullptr;
        }

        const auto& sublayerPaths = hostLayer->GetSubLayerPaths();
        const std::string& path = sublayerPaths[position];
        const auto& absolutePath = hostLayer->ComputeAbsolutePath(path);

        return findOrOpen(absolutePath);
    };

    /**
     * Adds a new layer.
     *
     * @param stage The stage this sublayer will be inserted to.
     * @param hostLayer Host Layer to create sublayer.
     * @param position The position to insert the new layer before. If position > sublayerCount,
     * it will create the layer at the end.
     * @param anonymous If the layer should be anonymous. Anonymous layer is in memory only and will not be saved to
     * file.
     * @param saveOnCreate Saves layer file after create or not.
     * @param finalPosition Real sublayer position of new layer in hostLayer. It's valid only when the return is not
     * nullptr.
     * @return layer handle. It will be nullptr if it's failed.
     */
    static PXR_NS::SdfLayerRefPtr createSublayer(PXR_NS::UsdStageRefPtr stage,
                                                 PXR_NS::SdfLayerRefPtr hostLayer,
                                                 size_t position,
                                                 const char* layerPath,
                                                 bool saveOnCreate,
                                                 size_t& finalPosition)
    {
        size_t newLayerPos;
        size_t numLayers = hostLayer->GetNumSubLayerPaths();
        if (position > numLayers)
        {
            newLayerPos = numLayers;
        }
        else
        {
            newLayerPos = position;
        }

        // It's possible that this layer is already existed
        PXR_NS::SdfLayerRefPtr newLayer = nullptr;
        if (layerPath && layerPath[0] != '\0')
        {
            newLayer = PXR_NS::SdfLayer::FindOrOpen(layerPath);
            if (!newLayer)
            {
                if (saveOnCreate)
                {
                    newLayer = PXR_NS::SdfLayer::CreateNew(layerPath);
                }
                else
                {
                    newLayer = PXR_NS::SdfLayer::New(hostLayer->GetFileFormat(), layerPath);
                }
            }
            else
            {
                newLayer->Clear();
            }
        }
        else
        {
            newLayer = PXR_NS::SdfLayer::CreateAnonymous();
        }

        if (newLayer)
        {
            std::string relativePath = newLayer->GetIdentifier();
            UsdUtils::makePathRelativeToLayer(hostLayer, relativePath);
            hostLayer->InsertSubLayerPath(relativePath, (int)newLayerPos);
            finalPosition = newLayerPos;
        }

        return newLayer;
    }

    /**
     * Inserts a layer into the current sublayers.
     *
     * @param stage The stage this sublayer will be inserted to.
     * @param hostLayer The Layer to create sublayer.
     * @param position The position to insert the new layer before. If sublayerPosition > sublayerCount,
     * it will create the layer at the end.
     * @param name Name of the new layer.
     * @param path Absolute path of the new layer.
     * @param newLayerIndex Real sublayer position this layer creates to. It's valid only when return is not nullptr.
     * @return layer identifier of created identifier. It's failed if it's empty.
     */
    static PXR_NS::SdfLayerRefPtr insertSublayer(PXR_NS::UsdStageRefPtr stage,
                                                 PXR_NS::SdfLayerRefPtr hostLayer,
                                                 size_t position,
                                                 const std::string& path,
                                                 size_t& newLayerIndex)
    {
        size_t newLayerPos;
        size_t numLayers = hostLayer->GetNumSubLayerPaths();
        if (position > numLayers)
        {
            newLayerPos = numLayers;
        }
        else
        {
            newLayerPos = position;
        }

        const auto& absolutePath = computeAbsolutePath(hostLayer, path);
        const PXR_NS::SdfLayerRefPtr& newLayer = PXR_NS::SdfLayer::FindOrOpen(absolutePath);
        if (newLayer)
        {
            std::string relativePath = absolutePath;
            UsdUtils::makePathRelativeToLayer(hostLayer, relativePath);
            hostLayer->InsertSubLayerPath(relativePath, (int)newLayerPos);
        }
        else
        {
            CARB_LOG_ERROR("ERROR! Failed to insert sublayer at path %s", absolutePath.c_str());
        }
        newLayerIndex = newLayerPos;

        return newLayer;
    }

    /**
     * Replaces layer with new path.
     *
     * @param stage The stage this sublayer will be inserted to.
     * @param hostLayer The layer handle to create sublayer.
     * @param position The position to replace. It must be [0, num_of_sublayers).
     * @param path New layer path.
     * @return layer handle. It will be nullptr if it's failed.
     **/
    static PXR_NS::SdfLayerRefPtr replaceSublayer(PXR_NS::UsdStageRefPtr stage,
                                                  PXR_NS::SdfLayerRefPtr hostLayer,
                                                  size_t position,
                                                  const std::string& path)
    {
        if (position >= hostLayer->GetNumSubLayerPaths())
        {
            CARB_LOG_ERROR("ERROR! Failed to replace sublayer as position %zu is invalid", position);
            return nullptr;
        }

        const auto& absolutePath = computeAbsolutePath(hostLayer, path);
        const PXR_NS::SdfLayerRefPtr& newLayer = PXR_NS::SdfLayer::FindOrOpen(absolutePath);
        if (newLayer)
        {
            PXR_NS::SdfChangeBlock changeBlock;
            auto sublayerPaths = hostLayer->GetSubLayerPaths();
            std::string oldSublayerPath = sublayerPaths[position];
            oldSublayerPath = computeAbsolutePath(hostLayer, oldSublayerPath);
            std::string relativePath = absolutePath;
            UsdUtils::makePathRelativeToLayer(hostLayer, relativePath);
            sublayerPaths[position] = relativePath;
        }
        else
        {
            CARB_LOG_ERROR("ERROR! Failed to replace sublayer at path %s", absolutePath.c_str());
        }

        return newLayer;
    }

    /**
     * Delete a existing layer. Delete root layer will do nothing.
     *
     * @param stage The stage of the operation.
     * @param hostLayer The layer to create sublayer.
     * @param position The sublayer position to delete. If it's not a valid sublayer index, it will do nothing.
     * @return true if the layer is deleted, false otherwise.
     *
     **/
    static bool deleteSublayer(PXR_NS::SdfLayerRefPtr hostLayer, size_t position)
    {
        std::string sublayerIdentifier;
        if (!getSublayerIdentifier(hostLayer, position, sublayerIdentifier))
        {
            return false;
        }

        hostLayer->RemoveSubLayerPath((int)position);

        return true;
    }

    /**
     * Move sublayer from source to target position.
     *
     * @param fromLayerIdentifier Layer identifier of source layer.
     * @param fromSublayerIndex The sublayer position of source layer to move.
     * @param toLayerIdentifier Layer identifier of target layer.
     * @param toSublayerIndex The sublayer position of target layer that source sublayer moves to.
     * @return true if the layer is moved successfully, false otherwise.
     */
    static bool moveSublayer(const std::string& fromLayerIdentifier,
                             size_t fromSublayerIndex,
                             const std::string& toLayerIdentifier,
                             size_t toSublayerIndex,
                             size_t& toFinalPosition)
    {
        if (fromLayerIdentifier == toLayerIdentifier && fromSublayerIndex == toSublayerIndex)
        {
            return false;
        }

        auto fromLayer = PXR_NS::SdfLayer::FindOrOpen(fromLayerIdentifier);
        auto toLayer = PXR_NS::SdfLayer::FindOrOpen(toLayerIdentifier);
        if (!fromLayer || !toLayer)
        {
            return false;
        }

        if (fromSublayerIndex >= fromLayer->GetNumSubLayerPaths())
        {
            return false;
        }

        if (fromLayerIdentifier != toLayerIdentifier && toSublayerIndex > toLayer->GetNumSubLayerPaths())
        {
            toFinalPosition = toLayer->GetNumSubLayerPaths();
        }
        else if (toSublayerIndex > toLayer->GetNumSubLayerPaths())
        {
            toFinalPosition = toLayer->GetNumSubLayerPaths() - 1;
        }
        else
        {
            toFinalPosition = toSublayerIndex;
        }

        const auto& sublayerPaths = fromLayer->GetSubLayerPaths();
        std::string sublayer = sublayerPaths[fromSublayerIndex];
        sublayer = computeAbsolutePath(fromLayer, sublayer);
        UsdUtils::makePathRelativeToLayer(toLayer, sublayer);

        fromLayer->RemoveSubLayerPath((int)fromSublayerIndex);
        toLayer->InsertSubLayerPath(sublayer, (int)toFinalPosition);

        return true;
    }

    /**
     * Save all changes of the specified layers.
     * @param layerIdentifiers List of layer identifiers to be saved.
     */
    static bool saveLayers(const std::vector<std::string>& layerIdentifiers)
    {
        bool success = true;
        for (const auto& layerIdentifier : layerIdentifiers)
        {
            if (!LayerUtils::saveLayer(layerIdentifier))
            {
                success = false;
                CARB_LOG_ERROR("ERROR! Failed to save layer %s due to permission issue.", layerIdentifier.c_str());
            }
        }

        return success;
    }

    /**
     * Gets all identifiers of all dirty layers in the local stack of stage (anonymous layers are not included).
     */
    static std::vector<std::string> getLocalDirtyLayers(PXR_NS::UsdStageRefPtr stage)
    {
        std::vector<std::string> layerIdentifiers;
        PXR_NS::SdfLayerHandleVector layerStack = stage->GetLayerStack(true);
        for (const auto& layer : layerStack)
        {
            if (layer && !layer->IsAnonymous() && layer->IsDirty())
            {
                layerIdentifiers.push_back(layer->GetIdentifier());
            }
        }

        return layerIdentifiers;
    }

    /**
     * Saves layer and all its sublayers.
     *
     * @param layerIdentifier Layer identifier.
     * @return true if it's successful, or false otherwise.
     */
    static bool saveLayer(const std::string& layerIdentifier, bool saveSublayers = false)
    {
        auto layer = PXR_NS::SdfLayer::Find(layerIdentifier);
        if (!layer)
        {
            return false;
        }

        if (saveSublayers)
        {
            auto stage = PXR_NS::UsdStage::Open(layer);
            stage->Save();
            return true;
        }
        else
        {
            return layer->Save();
        }
    }

    /**
     * Checks if a layer is empty (no root prims) or not.
     *
     * @param layerIdentifier Layer identifier.
     * @return true if it includes root prims, or false otherwise.
     */
    static bool hasRootPrimSpecs(const std::string& layerIdentifier)
    {
        auto layer = PXR_NS::SdfLayer::FindOrOpen(layerIdentifier);
        if (!layer)
        {
            return false;
        }

        return layer->GetPseudoRoot()->GetNameChildren().size() > 0;
    }

    struct PairHash
    {
        template <class T1, class T2>
        std::size_t operator()(const std::pair<T1, T2>& pair) const
        {
            return std::hash<T1>()(pair.first) ^ std::hash<T2>()(pair.second);
        }
    };

    // Depth-first pre-order traverse of layer and its sublayer descendants.
    // LayerGroupStartCallback will be called before iterating sublayers of a layer.
    // If LayerGroupStartCallback returns false, it will stop to traverse this layer.
    // For each layer it found, it will call LayerCallback.
    // After all sublayers have been traversed, it will call LayerGroupEndCallback.
    // You need to track the depth of whole traverse.
    // If layer is not found, LayerGroupStartCallback  and LayerGroupEndCallback will be called
    // also by passing a nullptr as the layer handle, and its layer identifier.
    // REMINDER: Don't call this per frame, which may be harmful to performance as
    // it insolves with resolver.
    using LayerGroupStartCallback =
        std::function<bool(PXR_NS::SdfLayerRefPtr hostLayer, const std::string& layerIdentifier)>;
    using LayerCallback = std::function<void(
        PXR_NS::SdfLayerRefPtr hostLayer, PXR_NS::SdfLayerRefPtr sublayer, const std::string& layerIdentifier, size_t sublayerIndex)>;
    using LayerGroupEndCallback =
        std::function<void(PXR_NS::SdfLayerRefPtr hostLayer, const std::string& layerIdentifier)>;
    static void iterateSublayerTreeDFS(PXR_NS::SdfLayerRefPtr rootLayer,
                                       const LayerGroupStartCallback groupStartCallback,
                                       const LayerCallback callback,
                                       const LayerGroupEndCallback groupEndCallback)
    {
        CARB_PROFILE_ZONE(1, "iterateSublayerTreeDFS");
        PXR_NS::ArResolverScopedCache cache;
        // If there is circular reference like layer1 -> sublayer1 -> layer1 -> sublayer2 ...,
        // it needs to be detected to avoid endless loop.
        // This map is used to record if <parent layer, current layer> has been accessed already
        // to avoid endless loop.
        std::unordered_set<std::pair<std::string, std::string>, PairHash> accessMap;
        iterateSublayerTreeDFSInternal(nullptr, rootLayer, rootLayer->GetIdentifier(), kLayerIndexNone,
                                       groupStartCallback, callback, groupEndCallback, accessMap);
    }

    // Depth-first pre-order traverse of prim tree.
    // PrimSpecGroupStartCallback will be called before iterating children of a prim.
    // It will stop to traverse it's children if it returns false.
    // For each prim it found, it will call PrimSpecCallback.
    // After all children haved been traversed, it will call PrimSpecGroupEndCallback.
    // You need to track the depth of whole traverse.
    using PrimSpecGroupStartCallback = std::function<bool(PXR_NS::SdfPrimSpecHandle parentSpecPrim)>;
    using PrimSpecCallback = std::function<void(
        PXR_NS::SdfPrimSpecHandle parentSpecPrim, PXR_NS::SdfPrimSpecHandle childSpecPrim, size_t primSpecIndex)>;
    using PrimSpecGroupEndCallback = std::function<void(PXR_NS::SdfPrimSpecHandle parentSpecPrim)>;
    static void iteratePrimSpecTreeDFS(PXR_NS::SdfLayerRefPtr layer,
                                       const PrimSpecGroupStartCallback groupStartCallback,
                                       const PrimSpecCallback callback,
                                       const PrimSpecGroupEndCallback groupEndCallback)
    {
        CARB_PROFILE_ZONE(1, "iteratePrimSpecTreeDFS");
        PXR_NS::SdfPrimSpecHandle empty;
        auto children = layer->GetPseudoRoot()->GetNameChildren();
        for (size_t i = 0; i < children.size(); i++)
        {
            iteratePrimTreeDFSInternal(empty, children[i], 0, groupStartCallback, callback, groupEndCallback);
        }
    }

    static void iteratePrimSpecTreeDFS(const std::string& layerIdentifier,
                                       const PrimSpecGroupStartCallback groupStartCallback,
                                       const PrimSpecCallback callback,
                                       const PrimSpecGroupEndCallback groupEndCallback)
    {
        auto layer = PXR_NS::SdfLayer::FindOrOpen(layerIdentifier);
        if (!layer)
        {
            return;
        }

        iteratePrimSpecTreeDFS(layer, groupStartCallback, callback, groupEndCallback);
    }

    /**
     * Gets the absolute path that's relative to root layer.
     *
     * @param rootLayer Root layer that the path is relative to.
     * @param path Path string.
     * @return Absolute path. If it's anonymous layer path, it will return it directly.
     */
    static std::string computeAbsolutePath(const PXR_NS::SdfLayerRefPtr& rootLayer, const std::string& path)
    {
        if (PXR_NS::SdfLayer::IsAnonymousLayerIdentifier(path) || rootLayer->IsAnonymous())
        {
            return path;
        }
        else
        {
            // Compute the path through the resolver
            const std::string& absolutePath = rootLayer->ComputeAbsolutePath(path);
            return normalizePath(absolutePath);
        }
    }

    /**
     * Similar to SdfLayer::FindOrOpen, but only calls SdfLayer::Find on anonymous layer to prevent USD Coding Error.
     *
     * @param identifier Layer identifier to be found or opened.
     * @return Found layer, or nullptr if not found.
     */
    static PXR_NS::SdfLayerRefPtr findOrOpen(const std::string& identifier)
    {
        if (PXR_NS::SdfLayer::IsAnonymousLayerIdentifier(identifier))
        {
            return PXR_NS::SdfLayer::Find(identifier);
        }
        return PXR_NS::SdfLayer::FindOrOpen(identifier);
    }

    static bool hasDirtyLayers(PXR_NS::UsdStageRefPtr stage)
    {
        CARB_PROFILE_ZONE(1, "hasDirtyLayers");
        if (!stage)
        {
            return false;
        }

        for (auto& layer : stage->GetUsedLayers())
        {
            if (!layer->IsAnonymous() && layer->IsDirty())
            {
                return true;
            }
        }

        return false;
    }

    // Checks if layerIdentifier is in the sublayer tree rooted from hostLayer, and this layer
    // must be existed.
    static bool isLayerInSublayerTree(PXR_NS::SdfLayerRefPtr hostLayer, const std::string& identifier)
    {
        bool found = false;
        LayerUtils::iterateSublayerTreeDFS(hostLayer,
            [&identifier, &found](const pxr::SdfLayerRefPtr layer, const std::string& layerIdentifier) {
                if (layer && identifier == layerIdentifier)
                {
                    found = true;
                    return false;
                }

                return true;
            },
            nullptr,
            nullptr
        );

        return found;
    }

    static std::string normalizePath(const std::string& path)
    {
        // OMPE-43063: The result of makeRelativeUrl may include %xx escape characters, so here we
        // need to go through an unquote process to decode the escapte characters.
        // Because the input will not always be % escaped, we only convert valid % escaped characters.
        std::string finalPath;
        finalPath.reserve(path.length());

        auto hexCharToInt = [](char c) -> int
        {
            if (c >= '0' && c <= '9') return c - '0';
            c = std::toupper(c);
            if (c >= 'A' && c <= 'F') return c - 'A' + 10;
            return -1;
        };

        for (size_t i = 0; i < path.length(); ++i)
        {
            if (path[i] == '%')
            {
                if (i + 2 < path.length())
                {
                    int high = hexCharToInt(path[i + 1]);
                    int low = hexCharToInt(path[i + 2]);
                    if (high != -1 && low != -1)
                    {
                        finalPath += static_cast<char>((high << 4) | low);
                        i += 2;
                    }
                    else
                    {

                        finalPath += '%';
                    }
                }
                else
                {

                    finalPath += '%';
                }
            }

            else if (path[i] == '+')
            {
                finalPath += ' ';
            }
            else
            {
                finalPath += path[i];
            }
        }

        std::replace(finalPath.begin(), finalPath.end(), '\\', '/');

        return finalPath;
    }

    static std::string normalizeUrl(const std::string& url)
    {
        std::string result;
        auto omniclient = carb::getCachedInterface<carb::omniclient::IOmniClient>();
        if (omniclient)
        {
            size_t bufferSize = 0;
            omniclient->normalizeUrl(url.c_str(), nullptr, &bufferSize);
            if (bufferSize != 0)
            {
                auto stringBufferHeap = std::unique_ptr<char[]>(new char[bufferSize]);
                const char* normalizedUrl = omniclient->normalizeUrl(url.c_str(), stringBufferHeap.get(), &bufferSize);
                if (!normalizedUrl)
                {
                    result = url;
                }
                else
                {
                    result = normalizedUrl;
                }
            }
            else
            {
                result = url;
            }
        }
        else
        {
            result = url;
        }

        return result;
    }

private:
    template<typename T>
    static bool getLayerCustomFieldInRootLayer(PXR_NS::SdfLayerRefPtr rootLayer, const std::string& layerIdentifier, const std::string& key, T& value)
    {
        // By default, the layer is not muted.
        PXR_NS::VtDictionary valueMap;
        const PXR_NS::VtDictionary& rootLayerCustomData = rootLayer->GetCustomLayerData();
        const auto& customDataValue = rootLayerCustomData.GetValueAtPath(key);
        if (customDataValue && !customDataValue->IsEmpty())
        {
            valueMap = customDataValue->Get<PXR_NS::VtDictionary>();
        }

        auto omniclient = carb::getCachedInterface<carb::omniclient::IOmniClient>();
        for (const auto& valuePair : valueMap)
        {
            std::string absolutePath = rootLayer->ComputeAbsolutePath(valuePair.first);
            if (normalizeUrl(absolutePath) == normalizeUrl(layerIdentifier))
            {
                value = valuePair.second.Get<T>();
                return true;
            }
        }

        return false;
    }

    template<typename T>
    static bool setLayerCustomFieldInRootLayer(PXR_NS::SdfLayerRefPtr rootLayer, const std::string& layerIdentifier,
        const std::string& key,  const T& value)
    {
        PXR_NS::VtDictionary valueMap;
        PXR_NS::VtDictionary rootLayerCustomData = rootLayer->GetCustomLayerData();
        const auto& oldValue = rootLayerCustomData.GetValueAtPath(key);
        if (oldValue && !oldValue->IsEmpty())
        {
            valueMap = oldValue->Get<PXR_NS::VtDictionary>();
        }

        std::string relativePath = layerIdentifier;
        UsdUtils::makePathRelativeToLayer(rootLayer, relativePath);
        LayerUtils::normalizePath(relativePath);
        for (auto iter = valueMap.begin(); iter != valueMap.end(); iter++)
        {
            const std::string& absolutePath = rootLayer->ComputeAbsolutePath(iter->first);
            if (normalizeUrl(absolutePath) == normalizeUrl(layerIdentifier))
            {
                valueMap.erase(iter);
                break;
            }
        }

        valueMap[relativePath] = PXR_NS::VtValue(value);
        rootLayerCustomData.SetValueAtPath(key, PXR_NS::VtValue(valueMap));
        rootLayer->SetCustomLayerData(rootLayerCustomData);

        return true;
    }

    static void iterateSublayerTreeDFSInternal(PXR_NS::SdfLayerRefPtr hostLayer,
                                               PXR_NS::SdfLayerRefPtr currentlayer,
                                               const std::string& currentLayeridentifier,
                                               size_t sublayerIndex,
                                               const LayerGroupStartCallback& groupStartCallback,
                                               const LayerCallback& callback,
                                               const LayerGroupEndCallback& groupEndCallback,
                                               std::unordered_set<std::pair<std::string, std::string>, PairHash>& accessMap)
    {
        std::string hostLayerIdentifier;
        if (hostLayer)
        {
            hostLayerIdentifier = hostLayer->GetIdentifier();
        }
        auto iter = accessMap.find({ hostLayerIdentifier, currentLayeridentifier });
        if (iter != accessMap.end()) // This layer has been accessed already
        {
            return;
        }
        else
        {
            accessMap.insert({ hostLayerIdentifier, currentLayeridentifier });
        }

        if (callback)
        {
            callback(hostLayer, currentlayer, currentLayeridentifier, sublayerIndex);
        }

        bool stop = false;
        if (groupStartCallback && !groupStartCallback(currentlayer, currentLayeridentifier))
        {
            stop = true;
        }

        if (!stop && currentlayer)
        {
            const auto& sublayerPaths = currentlayer->GetSubLayerPaths();
            for (size_t i = 0; i < sublayerPaths.size(); i++)
            {
                auto sublayer = getSublayer(currentlayer, i);
                std::string layerIdentifier;
                if (sublayer)
                {
                    layerIdentifier = sublayer->GetIdentifier();
                }
                else
                {
                    getSublayerIdentifier(currentlayer, i, layerIdentifier);
                }
                iterateSublayerTreeDFSInternal(currentlayer, sublayer, layerIdentifier, i, groupStartCallback, callback,
                                               groupEndCallback, accessMap);
            }
        }

        if (groupEndCallback)
        {
            groupEndCallback(currentlayer, currentLayeridentifier);
        }
    }

    static void iteratePrimTreeDFSInternal(PXR_NS::SdfPrimSpecHandle parentPrim,
                                           PXR_NS::SdfPrimSpecHandle currentPrim,
                                           size_t primIndex,
                                           const PrimSpecGroupStartCallback& groupStartCallback,
                                           const PrimSpecCallback& callback,
                                           const PrimSpecGroupEndCallback& groupEndCallback)
    {
        if (!currentPrim || currentPrim->IsDormant())
        {
            return;
        }

        if (callback)
        {
            callback(parentPrim, currentPrim, primIndex);
        }

        // Early stop
        bool stop = false;
        if (groupStartCallback)
        {
            stop = !groupStartCallback(currentPrim);
        }

        if (!stop)
        {
            auto childrenPrims = currentPrim->GetNameChildren();
            for (size_t i = 0; i < childrenPrims.size(); i++)
            {
                iteratePrimTreeDFSInternal(
                    currentPrim, childrenPrims[i], i, groupStartCallback, callback, groupEndCallback);
            }
        }

        if (groupEndCallback)
        {
            groupEndCallback(currentPrim);
        }

        return;
    }
};
}
}
