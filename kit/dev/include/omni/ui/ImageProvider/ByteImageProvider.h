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

namespace omni
{

namespace kit
{
namespace renderer
{
class IImGuiRenderer;
}
}

namespace ui
{

class OMNIUI_CLASS_API ByteImageProvider : public ImageProvider
{
public:
    OMNIUI_API
    ByteImageProvider();

    OMNIUI_API
    virtual ~ByteImageProvider();

    /**
     * @brief Sets byte data that the image provider will turn into an image.
     * @param bytes Data bytes.
     * @param size Tuple of image size, (width, height).
     * @param stride Number of bytes between rows of data bytes. Value kAutoCalculateStride could be used to
     * auto-calculate stride based on format, given data bytes have no gaps.
     * @param format Image format.
     */
    OMNIUI_API
    virtual void setBytesData(const uint8_t* bytes,
                              carb::Uint2 size,
                              size_t stride = kAutoCalculateStride,
                              carb::Format format = carb::Format::eRGBA8_UNORM);

    OMNIUI_API
    virtual void setMipMappedBytesData(const uint8_t* const* mipMapBytes,
                                       size_t* mipMapStrides,
                                       size_t mipMapCount,
                                       carb::Uint2 size,
                                       carb::Format format = carb::Format::eRGBA8_UNORM);

    OMNIUI_API
    virtual void setMipMappedBytesData(const uint8_t* bytes,
                                       carb::Uint2 size,
                                       size_t stride,
                                       carb::Format format = carb::Format::eRGBA8_UNORM,
                                       size_t maxMipLevels = SIZE_MAX);

    OMNIUI_API
    virtual void setBytesDataFromGPU(const uint8_t* bytes,
                                     carb::Uint2 size,
                                     size_t stride = kAutoCalculateStride,
                                     carb::Format format = carb::Format::eRGBA8_UNORM);

    OMNIUI_API
    void prepareDraw(float widgetWidth, float widgetHeight) override;

protected:
    friend class GpuResourcesCache;

    void _updateImage(const uint8_t* const* mipMapBuffers,
                      size_t* mipMapStrides,
                      size_t mipMapCount,
                      carb::Uint2 size,
                      carb::Format format,
                      bool fromGpu = false);
    OMNIUI_API
    void _releaseImage() override;

    OMNIUI_API
    bool mergeTextureOptions(TextureOptions& textureOptions) const override;

    OMNIUI_API
    bool setTextureOptions(TextureOptions textureOptions) override;

    omni::kit::renderer::TextureGpuData* m_textureGpuData = nullptr;
    omni::kit::renderer::TextureGpuReference m_imageGpuDescRef = {};
    omni::kit::renderer::IImGuiRenderer* m_imGuiRenderer = nullptr;

    std::unique_ptr<TextureOptions> m_textureOptions;
};

}
}
