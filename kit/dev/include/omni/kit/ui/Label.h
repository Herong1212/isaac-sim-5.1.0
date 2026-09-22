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

#include <functional>
#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a label.
 */
class OMNI_KIT_UI_CLASS_API Label : public Widget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Label);

    /**
     * Constructor.
     *
     * @param text The text for the label to use.
     */
    OMNI_KIT_UI_API explicit Label(const char* text);

    /**
     * Constructor.
     *
     * @param text The text for the label to use.
     * @param copyToClipboard when true, can be copied to clipboard via context menu
     */
    OMNI_KIT_UI_API Label(const char* text, bool copyToClipboard, ClippingType clipping, omni::ui::FontStyle fontStyle);

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~Label() override;

    /**
     * Gets the text of the label.
     *
     * @return The text of the label.
     */
    OMNI_KIT_UI_API const char* getText() const;

    /**
     * Sets the text of the label.
     *
     * @param text The text of the label.
     */
    OMNI_KIT_UI_API virtual void setText(const char* text);

    /**
     * Sets the color of the label text.
     *
     * @param textColor
     */
    OMNI_KIT_UI_API virtual void setTextColor(const carb::ColorRgba& textColor);

    /**
     * Resets the color of the label text.
     *
     * @param textColor
     */
    OMNI_KIT_UI_API virtual void resetTextColor();

    /**
     * Sets the callback function when the label is clicked.
     *
     * fn The callback function when the label is clicked.
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

    std::shared_ptr<Widget> tooltip;

    void setPaddingX(float px)
    {
        m_paddingX = px;
    }

protected:
    std::string m_text;
    bool m_customColor = false;
    carb::ColorRgba m_textColor = { 1.f, 1.f, 1.f, 1.f };
    std::function<void(WidgetRef)> m_clickedFn;
    std::string m_clippedText;
    float m_clippingWidth;
    float m_paddingX = 0.0f;
    bool m_copyToClipboard;
    ClippingType m_clippingMode = ClippingType::eNone;
};
}
}
}
