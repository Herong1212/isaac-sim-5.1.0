// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Widget.h"

#include <carb/renderer/RendererTypes.h>

#include <mutex>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a image.
 */
class OMNI_KIT_UI_CLASS_API Image : public Widget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Image);

    /**
     * Constructor.
     * ALWAYS create Image with make_shared so enable_shared_from_this works correctly.
     *
     * @param text The text for the label to use.
     */
    OMNI_KIT_UI_API Image(const char* url, uint32_t width, uint32_t height);

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~Image() override;

    /**
     * Gets the url of the image.
     *
     * @return The url to be loaded.
     */
    OMNI_KIT_UI_API const char* getUrl() const;

    /**
     * Sets the url of the image
     *
     * @param url The url to load.
     */
    OMNI_KIT_UI_API virtual void setUrl(const char* url);

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    /**
     * @see Widget::draw
     */
    void draw(float elapsedTime) override;

    /**
     * draw image
     *
     * @param imgui imgui ptr
     * @param cursorPos position to draw image
     * @param width width of image to draw
     * @param height height of image to draw
     * @param color color of image to draw
     */
    OMNI_KIT_UI_API virtual void drawImage(carb::imgui::ImGui* imgui,
                                           const carb::Float2& cursorPos,
                                           float width,
                                           float height,
                                           uint32_t color = 0xffffffff,
                                           uint32_t defaultColor = 0xffffffff,
                                           bool hovered = false);

protected:
    void loadUrl();

    std::string m_url;
    std::mutex m_textureMutex;
    carb::renderer::Texture* m_texture = nullptr;
    carb::renderer::TextureHandle m_textureGpuHandle = {};
    bool m_hasSetUrl = false;
};

}
}
}
