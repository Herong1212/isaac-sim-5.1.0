// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "LayerTypes.h"

#include <carb/Interface.h>
#include <carb/dictionary/IDictionary.h>


namespace omni
{
namespace kit
{
namespace usd
{
namespace layers
{

/**
 * ILayersState works for managing all layers states of the corresponding stage. Not all layer states can be queried through ILayersState,
 * but only those ones that are not easily accessed from USD APIs or extended in Omniverse. All the following interfaces work for the used
 * layers in the bound UsdContext.
 */
struct ILayersState
{
    CARB_PLUGIN_INTERFACE("omni::kit::usd::layers::ILayersState", 1, 1)

    // Gets all sublayers rooted from root layer, or session layer if includeSessionLayer is true. It's sorted from
    // strongest to weakest. If includeAnonymous is false, it will exclude anonymous ones. If includeInvalid is true, it
    // will include invalid sublayers. Invalid sublayers are those ones that in the layers list but its layer handle
    // cannot be found.
    carb::dictionary::Item*(CARB_ABI* getLocalLayerIdentifiers)(ILayersInstance* layerInstance,
                                                                bool includeSessionLayer,
                                                                bool includeAnonymous,
                                                                bool includeInvalid);

    // Gets all dirty used layers excluding anonymous ones.
    carb::dictionary::Item*(CARB_ABI* getDirtyLayerIdentifiers)(ILayersInstance* layerInstance);

    /**
     * Muteness scope is a concept extended by Omniverse. It includes two modes: global and local. When it's in global mode,
     * muteness will be serialized and will broadcasted during live session, while local mode means they are transient and will
     * not be broadcasted during live session.
     */
    void(CARB_ABI* setMutenessScope)(ILayersInstance* layersInstance, bool global);

    bool(CARB_ABI* isMutenessGlobal)(ILayersInstance* layersInstance);

    bool(CARB_ABI* isLayerGloballyMuted)(ILayersInstance* layersInstance, const char* layerIdentifier);

    bool(CARB_ABI* isLayerLocallyMuted)(ILayersInstance* layersInstance, const char* layerIdentifier);

    // If layer is writable means it can be set as edit target, it should satisfy:
    // 1. It's not read-only on disk.
    // 2. It's not muted.
    // 3. It's not locked by setLayerLockState.
    // You can still set it as edit target forcely if it's not writable, while this is useful for guardrails.
    bool(CARB_ABI* isLayerWritable)(ILayersInstance* layersInstance, const char* layerIdentifier);

    // If layer is savable means it can be saved to disk, it should satisfy:
    // 1. It's writable checked by isLayerWritable.
    // 2. It's not anonymous.
    // You can still save the layer forcely even it's locally locked or muted, while this is useful for guardrails.
    bool(CARB_ABI* isLayerSavable)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * Layer is a lock extended in Omniverse. It's not real ACL control to lock the layer for accessing, but a bool
     * flag that's checked by all applications to access it for UX purpose so it cannot be set as edit target.
     * Currently, only sublayers in the local layer stack can be locked.
     */
    void(CARB_ABI* setLayerLockState)(ILayersInstance* layersInstance, const char* layerIdentifier, bool locked);

    bool(CARB_ABI* isLayerLocked)(ILayersInstance* layersInstance, const char* layerIdentifier);

    void(CARB_ABI* setLayerName)(ILayersInstance* layersInstance, const char* layerIdentifier, const char* name);

    const char*(CARB_ABI* getLayerName)(ILayersInstance* layersInstance, const char* layerIdentifier);

    /**
     * If layer is outdated, it means it has updates on-disk. Currently, only layers in Nucleus can be watched
     * for updates.
     */
    bool(CARB_ABI* isLayerOutdated)(ILayersInstance* layersInstance, const char* layerIdentifier);

    // If layer is read-only on disk, this is used to check file permission only.
    // It's only useful when layer is not anonymous.
    bool(CARB_ABI* isLayerReadOnlyOnDisk)(ILayersInstance* layersInstance, const char* layerIdentifier);

    // Gets all outdated layers.
    carb::dictionary::Item*(CARB_ABI* getAllOutdatedLayerIdentifiers)(ILayersInstance* layerInstance);

    // Gets all outdated sublayers in the stage's local layer stack.
    carb::dictionary::Item*(CARB_ABI* getOutdatedSublayerIdentifiers)(ILayersInstance* layerInstance);

    // Gets all outdated layers except those ones in the sublayers list, like those reference or payload layers.
    // If a layer is both inserted as sublayer, or reference, it will be treated as sublayer only.
    carb::dictionary::Item*(CARB_ABI* getOutdatedNonSublayerIdentifiers)(ILayersInstance* layerInstance);

    // Reload all outdated layers.
    void(CARB_ABI* reloadAllOutdatedLayers)(ILayersInstance* layerInstance);

    // Reload all outdated sublayers.
    void(CARB_ABI* reloadOutdatedSublayers)(ILayersInstance* layerInstance);

    // Reload all outdated layers except sublayers. If a layer is both inserted as sublayer, or reference, it will
    // be treated as sublayer only.
    void(CARB_ABI* reloadOutdatedNonSublayers)(ILayersInstance* layerInstance);

    // Gets the file owner. It's empty if file system does not support it.
    const char* (CARB_ABI* getLayerOwner)(ILayersInstance* layersInstance, const char* layerIdentifier);
};

}
}
}
}
