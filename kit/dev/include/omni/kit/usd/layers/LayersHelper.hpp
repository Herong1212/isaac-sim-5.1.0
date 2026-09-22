// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/usd/layers/ILayers.h>

// clang-format off
#include <omni/usd/UsdContextIncludes.h>
#include <omni/usd/UsdContext.h>
// clang-format on

#if defined(__GNUC__)
#    pragma GCC diagnostic push
#    pragma GCC diagnostic ignored "-Wunused-function"
#endif


namespace omni
{
namespace kit
{
namespace usd
{
namespace layers
{
namespace internal
{

static carb::dictionary::IDictionary* getDictInterface()
{
    static auto staticInterface = carb::getCachedInterface<carb::dictionary::IDictionary>();

    return staticInterface;
}

}

static ILayers* getLayersInterface()
{
    static auto staticInterface = carb::getCachedInterface<omni::kit::usd::layers::ILayers>();

    return staticInterface;
}

static ILayersState* getLayersStateInterface()
{
    static auto staticInterface = carb::getCachedInterface<omni::kit::usd::layers::ILayersState>();

    return staticInterface;
}

static IWorkflowAutoAuthoring* getAutoAuthoringInterface()
{
    static auto staticInterface = carb::getCachedInterface<omni::kit::usd::layers::IWorkflowAutoAuthoring>();

    return staticInterface;
}

static IWorkflowLiveSyncing* getLiveSyncingInterface()
{
    static auto staticInterface = carb::getCachedInterface<omni::kit::usd::layers::IWorkflowLiveSyncing>();

    return staticInterface;
}

static IWorkflowSpecsLocking* getSpecsLockingInterface()
{
    static auto staticInterface = carb::getCachedInterface<omni::kit::usd::layers::IWorkflowSpecsLocking>();

    return staticInterface;
}

static ILayersInstance* getLayersInstanceByName(const std::string& name)
{
    auto layers = getLayersInterface();
    return layers->getLayersInstanceByName(name.c_str());
}

static ILayersInstance* getLayersInstanceByUsdContext(omni::usd::UsdContext* usdContext)
{
    auto layers = getLayersInterface();
    return layers->getLayersInstanceByContext(usdContext);
}

static carb::events::IEventStream* getEventStream(omni::usd::UsdContext* usdContext)
{
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);

    return layerInstance->getEventStream();
}

static LayerEditMode getEditMode(omni::usd::UsdContext* usdContext)
{
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);

    return layerInstance->getEditMode();
}

static void setEditMode(omni::usd::UsdContext* usdContext, LayerEditMode editMode)
{
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);

    layerInstance->setEditMode(editMode);
}

static std::vector<std::string> getLocalLayerIdentifiers(
    omni::usd::UsdContext* usdContext, bool includeSessionLayer = true,
    bool includeAnonymous = true, bool includeInvalid = true)
{
    std::vector<std::string> layerIdentifiers;
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);
    auto layersState = getLayersStateInterface();
    auto item = layersState->getLocalLayerIdentifiers(layerInstance, includeSessionLayer, includeAnonymous, includeInvalid);
    if (item)
    {
        auto dict = internal::getDictInterface();
        size_t length = dict->getArrayLength(item);
        for (size_t i = 0; i < length; i++)
        {
            layerIdentifiers.push_back(dict->getStringBufferAt(item, i));
        }

        dict->destroyItem(item);
    }

    return layerIdentifiers;
}

static std::vector<std::string> getDirtyLayerIdentifiers(omni::usd::UsdContext* usdContext)
{
    std::vector<std::string> layerIdentifiers;
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);
    auto layersState = getLayersStateInterface();
    auto item = layersState->getDirtyLayerIdentifiers(layerInstance);
    if (item)
    {
        auto dict = internal::getDictInterface();
        size_t length = dict->getArrayLength(item);
        for (size_t i = 0; i < length; i++)
        {
            layerIdentifiers.push_back(dict->getStringBufferAt(item, i));
        }

        dict->destroyItem(item);
    }

    return layerIdentifiers;
}

static std::string getLayerName(omni::usd::UsdContext* usdContext, const std::string& layerIdentifier)
{
    std::vector<std::string> layerIdentifiers;
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);
    auto layersState = getLayersStateInterface();
    const std::string& name = layersState->getLayerName(layerInstance, layerIdentifier.c_str());
    if (name.empty())
    {
        if (PXR_NS::SdfLayer::IsAnonymousLayerIdentifier(layerIdentifier))
        {
            return layerIdentifier;
        }
        else
        {
            return PXR_NS::SdfLayer::GetDisplayNameFromIdentifier(layerIdentifier);
        }
    }
    else
    {
        return name;
    }
}

static void suspendAutoAuthoring(omni::usd::UsdContext* usdContext)
{
    auto autoAuthoring = getAutoAuthoringInterface();
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);

    autoAuthoring->suspend(layerInstance);
}

static void resumeAutoAuthoring(omni::usd::UsdContext* usdContext)
{
    auto autoAuthoring = getAutoAuthoringInterface();
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);

    autoAuthoring->resume(layerInstance);
}

static std::string getDefaultLayerIdentifier(omni::usd::UsdContext* usdContext)
{
    auto autoAuthoring = getAutoAuthoringInterface();
    auto layerInstance = getLayersInstanceByUsdContext(usdContext);

    return autoAuthoring->getDefaultLayer(layerInstance);
}

}
}
}
}

#if defined(__GNUC__)
#    pragma GCC diagnostic pop
#endif

