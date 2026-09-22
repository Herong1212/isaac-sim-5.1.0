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

struct IWorkflowSpecsLinking
{
    CARB_PLUGIN_INTERFACE("omni::kit::usd::layers::IWorkflowSpecsLinking", 1, 0)

    bool(CARB_ABI* isEnabled)(ILayersInstance* layersIntance);

    void(CARB_ABI* suspend)(ILayersInstance* layersIntance);

    void(CARB_ABI* resume)(ILayersInstance* layersIntance);

    /**
     * Links spec to specific layer.
     *
     * @param specPath The spec path to be linked to layer, which can be prim or property path. If it's prim path,
     *  all of its properties will be linked also.
     * @param layerIdentifier The layer that the spec is linked to.
     * @param hierarchy If it's true, all descendants of this spec will be linked to the specified layer also.
     *
     * @return Array of specs that are successfully linked.
     */
    carb::dictionary::Item*(CARB_ABI* linkSpec)(ILayersInstance* layersIntance,
                                                const char* specPath,
                                                const char* layerIdentifier,
                                                bool hierarchy);

    /**
     * Unlinks spec from layer.
     *
     * @param specPath The spec path to be unlinked.
     * @param layerIdentifier The layer that the spec is unlinked from.
     * @param hierarchy If it's true, it means all of its descendants will be unlinked also. False otherwise.
     * @return Array of specs that are successfully unlinked.
     */
    carb::dictionary::Item*(CARB_ABI* unlinkSpec)(ILayersInstance* layersIntance,
                                                  const char* specPath,
                                                  const char* layerIdentifier,
                                                  bool hierarchy);

    /**
     * Unlinks spec from all linked layers.
     *
     * @param specPath The spec path to be unlinked.
     * @param hierarchy If it's true, it means all of its descendants will be unlinked also. False otherwise.
     *
     * @return Array of specs that are successfully unlinked.
     */
    carb::dictionary::Item*(CARB_ABI* unlinkSpecFromAllLayers)(ILayersInstance* layersIntance,
                                                               const char* specPath,
                                                               bool hierarchy);

    /**
     * Unlinks specs that are linked to specific layer.
     *
     * @param layerIdentifier The layer identifier to unlink all specs from.
     *
     * @return array of specs that are successfully unlinked.
     */
    carb::dictionary::Item*(CARB_ABI* unlinkSpecsToLayer)(ILayersInstance* layersIntance, const char* layerIdentifier);

    /**
     * Clears all spec links.
     */
    void(CARB_ABI* unlinkAllSpecs)(ILayersInstance* layersIntance);

    /**
     * Gets all layer identifiers that specs are linked to.
     *
     * @param hierarchy If it's true, it means all of its descendants will be unlinked also. False otherwise.
     * @return Map of specs that are linked, of which key is the spec path, and value is list of layers that spec is
     * linked to.
     */
    carb::dictionary::Item*(CARB_ABI* getSpecLayerLinks)(ILayersInstance* layersIntance,
                                                         const char* specPath,
                                                         bool hierarchy);

    /**
     * Gets all spec paths that link to this layer.
     */
    carb::dictionary::Item*(CARB_ABI* getSpecLinksForLayer)(ILayersInstance* layersIntance, const char* layerIdentifier);

    /**
     * Gets all spec links.
     *
     * @return Map of spec links, of which key is the spec path, and value is layers that spec is linked to.
     */
    carb::dictionary::Item*(CARB_ABI* getAllSpecLinks)(ILayersInstance* layersIntance);

    /**
     * Checks if spec is linked or not.
     *
     * @param specPath The spec path.
     * @param layerIdentifier Layer identifier. If it's empty or null, it will return true if it's linked to any layers.
     * If it's not null and not empty, it will return true only when spec is linked to the specific layer.
     */
    bool(CARB_ABI* isSpecLinked)(ILayersInstance* layersIntance, const char* specPath, const char* layerIdentifier);
};

}
}
}
}
