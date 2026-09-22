// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ExtensionWindowTypes.h"

#include <carb/Interface.h>

namespace omni
{
namespace kit
{
/**
 * Defines the minimal interface for an extension window.
 */
struct IExtensionWindow
{
    CARB_PLUGIN_INTERFACE("omni::kit::IExtensionWindow", 1, 1);

    /**
     * Creates an instance of the extension window.
     *
     * @return created instance of extension window.
     */
    ExtensionWindowHandle(CARB_ABI* createInstance)();

    /**
     * Destroys an instance of extension window.
     *
     * @param handle The window handle to be destroyed.
     * @return true if window is destroyed, false if not.
     */
    bool(CARB_ABI* destroyInstance)(const ExtensionWindowHandle handle);

    /**
     * Query if an instance of extension window is visible.
     *
     * @param handle The window handle to be destroyed.
     */
    bool(CARB_ABI* isInstanceVisible)(const ExtensionWindowHandle handle);

    /**
     * Display or hide an instance of extension window.
     *
     * @param handle The window handle to be destroyed.
     * @param visible true to show the window, false to hide the window.
     */
    void(CARB_ABI* setInstanceVisible)(const ExtensionWindowHandle handle, bool visible);

    /**
     * Creates an instance of the viewport window with custom name and usdd stage.
     *
     * @param name The window name.
     * @param usdContextName The usd context to show in the window.
     * @param createMenu When true, the Window menu is created.
     * @return created instance of extension window.
     */
    ExtensionWindowHandle(CARB_ABI* createCustomizedInstance)(const char* name,
                                                              const char* usdContextName,
                                                              bool createMenu);
};
}
}
