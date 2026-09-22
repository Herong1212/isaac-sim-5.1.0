// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

namespace carb
{
namespace imgui
{
struct ImGui;
}
}

namespace omni
{
namespace kit
{
struct ContentWindowWidget;

class ContentExplorer;
using OnMenuItemClickedFn = void (*)(const char* menuPath, bool value, void* userData);
using OnMenuItemCheckFn = bool (*)(const char* contentUrl, void* userData);
using OnContentWindowToolButtonClickedFn = void (*)(const char* name, void* userData);

class IContentWindow
{
public:
    /**
     * Destructor.
     */
    virtual ~IContentWindow() = default;

    /**
     * Query the visibility of the window.
     *
     * @return visibility of the window.
     */
    virtual bool isVisible() const = 0;

    /**
     * Sets the visibility of the window.
     *
     * @param visible true to show the window, false to hide the window.
     */
    virtual void setVisible(bool visible) = 0;

    /**
     * Navigates to a path.
     *
     * @param path The path to navigate to.
     * @param changeSelection When true the path's parent directory will be expanded and leaf selected,
     *                        when false the path itself will be expanded and nothing will be selected.
     */
    virtual void navigateTo(const char* path, bool changeSelection = false) = 0;

    /**
     * Add context menu item to content window.
     *
     * @param menuItemName The name to the menu (e.g. "Open"), this name must be unique across context menu.
     * @param tooltip The helper text.
     * @param onMenuItemClicked The callback function called when menu item is clicked.
     * @param userData The custom data to be passed back via callback function.
     * @return true if success, false otherwise. When it returned with false,
     *         it means there is existing item that has the same name.
     */
    virtual bool addContextMenu(const char* menuItemName,
                                const char* tooltip,
                                OnMenuItemClickedFn onMenuItemClicked,
                                void* userData) = 0;

    /**
     * Removes a context menu item in content window.
     *
     * @param menuItemName The name of the menu item to be removed.
     */
    virtual void removeContextMenu(const char* menuItemName) = 0;

    /**
     * Add Icon menu item to content window.
     * @param menuItemName The name to the menu (e.g. "Open"), this name must be unique across context menu.
     * @param onMenuItemClicked The callback function called when menu item is clicked.
     * @param userData The custom data to be passed back via callback function.
     * @param onMenuItemCheck The callback function called when menu item is created. If the callback returns true, the
     *        menu item will not be created.
     * @param userDataCheck The custom data to be passed back to onMenuItemCheck callback.
     */
    virtual bool addIconMenu(const char* menuItemName,
                             OnMenuItemClickedFn onMenuItemClicked,
                             void* userData,
                             OnMenuItemCheckFn onMenuItemCheck,
                             void* userDataCheck) = 0;

    /**
     * Removes a Icon menu item in content window.
     *
     * @param menuItemName The name of the menu item to be removed.
     */
    virtual void removeIconMenu(const char* menuItemName) = 0;

    /**
     * Refresh selected node of content window.
     */
    virtual void refresh() = 0;

    /**
     * Adds tool button for content window, which locates at the left of search bar.
     *
     * @param name The name of the button, this name must be unique across tool bar of content window.
     * @param toolTip The helper text.
     * @param validDataSource If this is true, the button will only be enabled when a valid data source is selected.
     * @param clickedFn The callback function called when button is clicked.
     * @param userData The custom data to be passed back via callback function.
     * @param priority The priority to sort tool buttons. It's sorted in ascending order.
     * @return true if success, false otherwise. When it returned with false,
     *         it means there is existing item that has the same name.
     */
    virtual bool addToolButton(const char* name,
                               const char* tooltip,
                               bool validDataSource,
                               OnContentWindowToolButtonClickedFn clickedFn,
                               void* userData,
                               int priority) = 0;

    /**
     * Removes tool button for content window.
     *
     * @param name Button name to be removed.
     */
    virtual void removeToolButton(const char* name) = 0;

    /**
     * Gets current selected path protocol in content window.
     *
     * @return current selected path protocol in content window, (e.g. "" for local, or "omniverse:" for OV).
     */
    virtual const char* getSelectedPathProtocol() const = 0;

    /**
     * Gets current selected directory in content window.
     *
     * @return current selected directory in content window, (e.g. "/Users/test/", or "E:/test/").
     */
    virtual const char* getSelectedDirectoryPath() const = 0;

    /**
     * Gets current selected icon protocol in content window.
     *
     * @return current selected icon protocol in content window, (e.g. "" for local, or "omniverse:" for OV).
     */
    virtual const char* getSelectedIconProtocol() const = 0;

    /**
     * Gets current selected icon in content window.
     *
     * @return current selected icon in content window, (e.g. "/Users/test/1.usd", or "E:/test/1.usd").
     */
    virtual const char* getSelectedIconPath() const = 0;
};
}
}
