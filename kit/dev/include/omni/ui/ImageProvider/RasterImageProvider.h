// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ImageProvider.h"

#include <memory>
#include <mutex>
#include <string>

namespace carb
{
namespace settings
{
struct ISettings;
}
}

namespace omni
{
namespace ui
{

class OMNIUI_CLASS_API RasterImageProvider : public ImageProvider
{
public:
    OMNIUI_API
    RasterImageProvider(std::string = {});

    OMNIUI_API
    ~RasterImageProvider();

    /**
     * @brief Sets the raster image URL. Asset loading doesn't happen immediately, but rather is started the next time
     * widget is visible, in prepareDraw call.
     */
    OMNIUI_API
    virtual void setSourceUrl(const char* url);

    /**
     * @brief Returns vector image URL.
     */
    OMNIUI_API
    virtual std::string getSourceUrl() const;

    /**
     * @brief This function needs to be called every frame to make sure asset loading is moving forward, and resources
     * are properly allocated.
     */
    OMNIUI_API
    void prepareDraw(float widgetWidth, float widgetHeight) override;

    /**
     * @brief Sets the maximum number of mip map levels allowed.
     */
    OMNIUI_API
    virtual void setMaxMipLevels(size_t maxMipLevels);

    /**
     * @brief Returns the maximum number of mip map levels allowed.
     */
    OMNIUI_API
    virtual size_t getMaxMipLevels() const;

protected:
    void _shutdown();

    struct TextureData;

    carb::settings::ISettings* m_settings = nullptr;
    int32_t m_shutdownIterMax = 0;
    std::string m_sourceRasterUrl;
    bool m_sourceRasterUrlChanged = false;
    mutable std::mutex m_sourceRasterUrlMutex;
    std::unique_ptr<TextureData> m_textureData;
    bool m_assetLoading = false;
    std::string m_cacheKey;

    size_t m_maxMipLevels = 3;
    mutable std::mutex m_maxMipLevelsMutex;

    time_t _getModTime(const std::string& assetPathString);
    std::string _getCacheKey(const std::string& filePath);
    /**
     * @brief Function to trigger asset loading. Asset loading is non-blocking, so the image won't be available
     * immediately after _loadAsset is called - instead the image resources will be recreated eventually in
     * one of the subsequent _pollAsset calls when snapshot will be ready.
     */
    void _loadAsset(const std::string& assetPathString);
    /**
     * @brief Function to check asset loading status. If asset snapshot is not ready, do nothing. When it is ready,
     * proceed to create image resources from the loaded asset.
     */
    void _pollAsset();
    void _releaseAsset();
    void _waitAsset();
};

}
}
