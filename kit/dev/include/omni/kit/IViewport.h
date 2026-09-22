// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Interface.h>

#include <omni/kit/IExtensionWindow.h>
#include <omni/kit/ViewportTypes.h>

namespace omni
{
namespace kit
{
/**
 * Defines the interface for Viewport Window.
 */
struct IViewport
{
    CARB_PLUGIN_INTERFACE("omni::kit::IViewport", 1, 0);

    /**
     * Gets a ViewportWindow instance from its ExtensionWindowHandle.
     *
     * @param handle The ExtensionWindowHandle. Pass nullptr to get the first available viewport (in creation order).
     * @return ViewportWindow instance associated with the ExtensionWindowHandle.
     */
    IViewportWindow*(CARB_ABI* getViewportWindow)(const ExtensionWindowHandle handle);

    /**
     * Creates a viewport window.
     *
     * TODO: add @param name (optional) The name of the viewport.
     * If no name is specified the default names are Viewport, Viewport_2, etc.
     * @return the viewport window count
     */
    ExtensionWindowHandle(CARB_ABI* createViewportWindow)(/* TODO support: const char* name */);

    /**
     * Destroys a viewport window.
     *
     * @param handle The window handle to be destroyed.
     * @return true if window is destroyed, false if not.
     */
    bool(CARB_ABI* destroyViewportWindow)(const ExtensionWindowHandle viewportWindow);

    /**
     * Gets a ViewportWindow's ExtensionWindowHandle from its name.
     *
     * @param name the window name to retrieve an ExtensionWindowHandle for.
     * @return ExtensionWindowHandle associated with the window name.
     */
    ExtensionWindowHandle(CARB_ABI* getViewportWindowInstance)(const char* name);

    /**
     * Gets a ViewportWindow name from its ExtensionWindowHandle.
     *
     * @param handle The ExtensionWindowHandle. Pass nullptr to get the first available viewport (in creation order).
     * @return ViewportWindow name associated with the ExtensionWindowHandle.
     */
    const char*(CARB_ABI* getViewportWindowName)(const ExtensionWindowHandle handle);

    /**
     * Gets the number of viewport windows currently open
     *
     * @return the viewport window count
     */
    size_t(CARB_ABI* getViewportWindowInstanceCount)();

    /**
     * Returns a list of all open viewport window handles
     *
     * @param viewportWindowList An array of viewport window handles
     *
     * @param count number of viewport window handles to retrieve
     *
     * @remarks It is up to the caller to allocate memory for the viewport
     *          list, using getViewportWindowInstanceCount() to determine the list
     *          size.
     *          The call will fail if count is larger than the number of
     *          viewport windows, or if viewportWindowList is NULL.
     *
     * @return true if successful, false otherwise
     */
    bool(CARB_ABI* getViewportWindowInstances)(ExtensionWindowHandle* viewportWindowList, size_t count);

    /**
     * Add a viewport drop helper
     * Returns the current drop helper node.
     *
     * @param dropHelper  Specified the drop helper.
     */
    DropHelperNode*(CARB_ABI* addDropHelper)(const DropHelper& dropHelper);

    /**
     * Remove a viewport drop helper
     *
     * @param node  Specified the drop helper node to remove.
     */
    void(CARB_ABI* removeDropHelper)(const DropHelperNode* node) = 0;
};

struct IViewportAddOn
{
    CARB_PLUGIN_INTERFACE("omni::kit::IViewportAddOn", 0, 1);
    void* (CARB_ABI* getCarbRendererContext)();
};
}
}
