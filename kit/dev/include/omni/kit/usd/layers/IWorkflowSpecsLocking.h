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
#include <carb/dictionary/IDictionary.h>


namespace omni
{
namespace kit
{
namespace usd
{
namespace layers
{

struct IWorkflowSpecsLocking
{
    CARB_PLUGIN_INTERFACE("omni::kit::usd::layers::IWorkflowSpecsLocking", 1, 0)

    carb::dictionary::Item*(CARB_ABI* lockSpec)(ILayersInstance* layersIntance, const char* specPath, bool hierarchy);

    carb::dictionary::Item*(CARB_ABI* unlockSpec)(ILayersInstance* layersIntance, const char* specPath, bool hierarchy);

    void(CARB_ABI* unlockAllSpecs)(ILayersInstance* layersIntance);

    bool(CARB_ABI* isSpecLocked)(ILayersInstance* layersInstance, const char* specPath);

    carb::dictionary::Item*(CARB_ABI* getAllLockedSpecs)(ILayersInstance* layersIntance);
};

}
}
}
}
