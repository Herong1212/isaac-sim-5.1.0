// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>

namespace omni
{
namespace kit
{
/**
 * Defines the interface for ScriptEditor Window.
 */
struct IScriptEditor
{
    CARB_PLUGIN_INTERFACE("omni::kit::IScriptEditor", 1, 0);

    void(CARB_ABI* showHideWindow)(void* window, bool visible);
};
}
}
