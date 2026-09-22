// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
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

namespace omni
{
namespace kit
{
namespace usd
{
namespace layers
{

struct IWorkflowAutoAuthoring
{
    CARB_PLUGIN_INTERFACE("omni::kit::usd::layers::IWorkflowAutoAuthoring", 1, 0)

    bool(CARB_ABI* isEnabled)(ILayersInstance* layersIntance);

    void(CARB_ABI* suspend)(ILayersInstance* layersIntance);

    void(CARB_ABI* resume)(ILayersInstance* layersIntance);

    void(CARB_ABI* setDefaultLayer)(ILayersInstance* layersIntance, const char* layerIdentifier);

    const char*(CARB_ABI* getDefaultLayer)(ILayersInstance* layersIntance);

    bool(CARB_ABI* isAutoAuthoringLayer)(ILayersInstance* layersIntance, const char* layerIdentifier);
};

}
}
}
}
