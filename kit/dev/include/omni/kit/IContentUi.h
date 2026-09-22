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

#include <omni/kit/ContentUiTypes.h>
#include <omni/kit/IExtensionWindow.h>

namespace omni
{
namespace kit
{
/**
 * Defines the interface for Content UI.
 */
class IContentUi
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::IContentUi", 0, 1);

    /**
     * Gets a ContentWindow instance from its ExtensionWindowHandle.
     *
     * @param handle The ExtensionWindowHandle. Pass nullptr to get the first available ContentWindow (in creation
     * order).
     * @return ContentWindow instance associated with the ExtensionWindowHandle.
     */
    virtual IContentWindow* getContentWindow(const ExtensionWindowHandle handle) = 0;

    /**
     * Creates content window widget.
     *
     * @param width Width in pixel
     * @param height Height in pixel
     * @return ContentWindowWidget instance
     */
    virtual ContentWindowWidget* createContentWindowWidget(uint32_t width, uint32_t height) = 0;

    /**
     * Destroys content window widget.
     *
     * @param widget ContentWindowWidget instance
     */
    virtual void destroyContentWindowWidget(ContentWindowWidget* widget) = 0;

    /**
     * Refreshes content window widget.
     *
     * @param widget ContentWindowWidget instance
     */
    virtual void refreshContentWindowWidget(ContentWindowWidget* widget) = 0;

    /**
     * Draws content window widget.
     *
     * @param widget ContentWindowWidget instance
     * @param elapsedTime Time in seconds since last draw
     */
    virtual void drawContentWindowWidget(ContentWindowWidget* widget, float elapsedTime) = 0;

    /**
     * Allocates buffer and fill buffer with selected tree node information.
     *
     * @param ContentWindowWidget instance
     * @param protocol Path protocol (e.g., "", or "omniverse:"")
     * @param realUrl Real path (e.g., e:/test for local, or /Users/test for OV)
     * @param contentUrl Content path (e.g., /e/test for local, or /Users/test/ for OV)
     */
    virtual void createSelectedTreeNodeBuffersFromContentWindowWidget(ContentWindowWidget* widget,
                                                                      const char** protocol,
                                                                      const char** realUrl,
                                                                      const char** contentUrl) = 0;

    /**
     * Allocates buffer and fill buffer with selected file node information.
     *
     * @param ContentWindowWidget instance
     * @param protocol Path protocol (e.g., "", or "omniverse:"")
     * @param realUrl Real path (e.g., e:/test/test.txt for local, or /Users/test/test.txt for OV)
     * @param contentUrl Content path (e.g., /e/test/test.txt for local, or /Users/test/test.txt for OV)
     */
    virtual void createSelectedFileNodeBuffersFromContentWindowWidget(ContentWindowWidget* widget,
                                                                      const char** protocol,
                                                                      const char** realUrl,
                                                                      const char** contentUrl) = 0;

    /**
     * Destroys allocated buffers.
     */
    virtual void destroyBuffersFromContentWindowWidget(const char* protocol,
                                                       const char* realUrl,
                                                       const char* contentUrl) = 0;

    /**
     * Sets filter for content window.
     *
     * @param widget ContentWindowWidget instance
     * @param filter File filter that supports regex (e.g., *.usd).
     */
    virtual void setFilterForContentWindowWidget(ContentWindowWidget* widget, const char* filter) = 0;

    /**
     * Navigates to path.
     *
     * @param widget ContentWindowWidget instance
     * @param path
     */
    virtual void navigateContentWindowWidget(ContentWindowWidget* widget, const char* path) = 0;

    /**
     * Gets the download task status from download manager.
     *
     * @param[out] finishedFiles Number of finished files.
     * @param[out] totalFiles Number of total files.
     * @param[out] lastUrl Url of last downloaded file.
     * return true if download is in progress, false if no file is being downloaded.
     */
    virtual bool getDownloadTaskStatus(int32_t& finishedFiles, int32_t& totalFiles, const char*& lastUrl) = 0;
};
}
}
