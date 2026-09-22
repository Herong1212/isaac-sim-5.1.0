// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "../Object.h"
#include "../Property.h"

#include <carb/Types.h>
#include <carb/container/IntrusiveList.h>
#include <carb/tasking/TaskingTypes.h>
#include <carb/imaging/IImaging.h>

#include <omni/kit/renderer/IRenderer.h>

#include <memory>
#include <utility>

namespace omni
{
namespace ui
{

constexpr const size_t kAutoCalculateStride = (size_t)-1;


class OMNIUI_CLASS_API ImageProvider
{
protected:
    using GpuResource = rtx::resourcemanager::RpResource;
    using TextureOptions = omni::kit::renderer::IRendererTextureOptions;

public:
    OMNIUI_API
    ImageProvider();

    OMNIUI_API
    virtual ~ImageProvider();

    /**
     * @brief Returns reference which could be used to draw ImGui images with.
     */
    OMNIUI_API
    virtual void* getImGuiReference();

    /**
     * @brief Returns true if ImGui reference is valid, false otherwise.
     */
    OMNIUI_API
    virtual bool isReferenceValid()
    {
        return m_imGuiReference != nullptr;
    }

    /**
     * @brief Gets image width.
     */
    OMNIUI_API
    size_t getWidth()
    {
        return m_imageSize.x;
    }

    /**
     * @brief Gets image height.
     */
    OMNIUI_API
    size_t getHeight()
    {
        return m_imageSize.y;
    }

    /**
     * @brief Gets tuple (width, height).
     */
    OMNIUI_API
    carb::Uint2 getSize()
    {
        return m_imageSize;
    }

    /**
     * @brief Gets display window w.r.t to the image (data window). The display size is same as the viewport size.
     */
    OMNIUI_API
    carb::imaging::DisplayWindowRect getDisplayWindow()
    {
        return m_imageDisplayWindow;
    }

    /**
     * @brief Gets image format.
     */
    OMNIUI_API
    carb::Format getFormat()
    {
        return m_imageFormat;
    }

    /**
     * @brief Function that should be called when the widget is being prepared to be drawn. Lazy load of image
     * contents may happen there, depending on the image provider logic.
     * @param widgetWidth Computed width of the widget.
     * @param widgetHeight Computed height of the widget.
     */
    OMNIUI_API
    virtual void prepareDraw(float widgetWidth, float widgetHeight);

    /**
     * @brief Sets non-managed image data directly.
     * @param imGuiReference Opaque pointer to the data used in the ImGuiRenderer.
     * @param size Size tuple (width, height) of the image data.
     * @param format Pixel format of the image data.
     * @param rpRsrc The GpuResource to be associated with the image data. The GpuResource is not checked for data compatibility, can be nullptr.
     */
    OMNIUI_API
    void setImageData(void* imGuiReference, carb::Uint2 size, carb::Format format, GpuResource* gpuRsrc = nullptr);

    /**
     * @brief Sets image data directly from an GpuResource.
     * @param rpRsrc The GpuResource to be used for data.
     * @return A boolean value whether the image-data was set.
     *         On success the GpuResource will have been retained, otherwise not.
     */
    OMNIUI_API
    bool setImageData(GpuResource& gpuRsrc);

    /**
     * Sets image data directly from a GpuResource.
     *
     * @param gpuRsrc The GpuResource to be used for data.
     * @param presentationKey The presentation key associated with the GpuResource. Used by the present thread to get the ImGui reference.
     *
     * @return A boolean value indicating whether the image-data was set.
     *         On success, the GpuResource will have been retained, otherwise not.
     */
    OMNIUI_API
    bool setImageData(GpuResource& gpuRsrc, uint64_t presentationKey);

    /**
     * Sets image data directly from an GpuResource.
     *
     * @param gpuRsrc The GpuResource to be used for data.
     * @param presentationKey The presentation key associated with the GpuResource. Used by the present thread to get the ImGui reference.
     * @param metadata The imaging metadata associated with the GpuResource.
     *
     * @return A boolean value indicating whether the image-data was set.
     *         On success, the GpuResource will have been retained, otherwise not.
     */
    OMNIUI_API
    bool setImageData(GpuResource& gpuRsrc, uint64_t presentationKey, carb::imaging::IMetadata* metadata);

    /**
     * @brief Shuts down the image provider system
     */
    OMNIUI_API
    static void shutdown();

    /**
     * @brief Shuts down the image provider system
     */
    OMNIUI_API
    GpuResource* getManagedResource();

protected:
    /**
     * @brief Release the managed image data, called from setImageData
     */
    OMNIUI_API
    virtual void _releaseImage()
    {
    }

    void _shutdown();

    OMNIUI_API
    virtual bool _setManagedResource(GpuResource* rpRsrc);

    OMNIUI_API
    virtual bool mergeTextureOptions(TextureOptions& textureOptions) const;

    OMNIUI_API
    virtual bool setTextureOptions(TextureOptions textureOptions);

    void* m_imGuiReference = nullptr;
    carb::Uint2 m_imageSize = {};
    carb::imaging::DisplayWindowRect m_imageDisplayWindow = { 0.0f, 0.0f, 1.0f, 1.0f };
    carb::Format m_imageFormat = carb::Format::eRGBA8_UNORM;
    size_t m_imageMipCount = 1;
    bool m_isShutdown = false;

    omni::kit::renderer::IRenderer* m_kitRenderer = nullptr;
    GpuResource* m_managedRsrc = nullptr;
    uint64_t m_presentationKey = 0;
    carb::tasking::SharedFuture<gpu::GfResult> m_future;
    bool m_hasFuture = false;
    uint32_t m_id = 0;

public: // Must be public so it can be accessed outside of the class
    carb::container::IntrusiveListLink<ImageProvider> m_link;

    template <typename T, typename... Args>
    static std::shared_ptr<T> create(Args&&... args)
    {
        std::shared_ptr<T> ptr{ new T{ std::forward<Args>(args)... } };
        return ptr;
    }

    template <typename T, typename Deleter, typename... Args>
    static std::shared_ptr<T> createWithDeleter(Deleter&& deleter, Args&&... args)
    {
        return std::shared_ptr<T>{ new T{ std::forward<Args>(args)... }, std::forward<Deleter>(deleter) };
    }
};

}
}
