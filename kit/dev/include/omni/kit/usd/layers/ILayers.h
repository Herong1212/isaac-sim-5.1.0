// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "ILayersState.h"
#include "IWorkflowAutoAuthoring.h"
#include "IWorkflowLiveSyncing.h"
#include "IWorkflowSpecsLinking.h"
#include "IWorkflowSpecsLocking.h"


namespace omni
{
namespace kit
{
namespace usd
{
namespace layers
{

struct ILayers
{
    CARB_PLUGIN_INTERFACE("omni::kit::usd::layers::ILayers", 1, 0)

    ILayersInstance*(CARB_ABI* getLayersInstanceByName)(const char* usdContextName);

    ILayersInstance*(CARB_ABI* getLayersInstanceByContext)(void* usdContext);
};

}
}
}
}
