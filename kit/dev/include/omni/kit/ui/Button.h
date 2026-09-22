// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Image.h"
#include "Label.h"

#include <cstdint>
#include <functional>
#include <memory>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a button.
 */
class OMNI_KIT_UI_CLASS_API Button : public Label
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Button);

    /**
     * Constructor.
     *
     * @param text The text for the button to use.
     */
    OMNI_KIT_UI_API explicit Button(const char* text, bool isImage = false, uint32_t defaultColor = 0xffffffff);

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~Button() override;

    /**
     * Sets the callback function when the button is clicked.
     *
     * fn The callback function when the button is clicked.
     */
    OMNI_KIT_UI_API void setClickedFn(const std::function<void(WidgetRef)>& fn);

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    /**
     * @see Widget::draw
     */
    void draw(float elapsedTime) override;

    /**
     * Gets the url of the image.
     *
     * @return The url to be loaded.
     */
    const char* getUrl() const
    {
        return m_image->getUrl();
    }

    /**
     * Sets the alternative url of the image
     *
     * @param url The url to load.
     */
    void setUrl(const char* url)
    {
        m_image->setUrl(url);
    }

protected:
    std::function<void(WidgetRef)> m_clickedFn;
    std::shared_ptr<Image> m_image;
    uint32_t m_defaultColor;
};
}
}
}
