// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ValueWidget.h"

#include <functional>
#include <string>
#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a text field.
 */
class OMNI_KIT_UI_CLASS_API TextBox : public ValueWidget<std::string>
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::TextBox);

    static const size_t kMaxLength = 1024;

    OMNI_KIT_UI_API explicit TextBox(const char* defaultText, bool changeValueOnEnter = false);

    OMNI_KIT_UI_API TextBox(const char* defaultText, const char* hint, bool changeValueOnEnter = false);

    OMNI_KIT_UI_API ~TextBox() override;

    OMNI_KIT_UI_API void setValueChangedFn(const std::function<void(WidgetRef)>& fn);

    OMNI_KIT_UI_API void setValueFinalizedFn(const std::function<void(WidgetRef)>& fn);

    OMNI_KIT_UI_API void setListSuggestionsFn(const std::function<std::vector<std::string>(WidgetRef, const char*)>& fn);

    OMNI_KIT_UI_API bool getReadOnly() const;

    OMNI_KIT_UI_API void setReadOnly(bool readOnly);

    OMNI_KIT_UI_API bool getShowBackground() const;

    OMNI_KIT_UI_API void setShowBackground(bool showBackground);

    OMNI_KIT_UI_API float getTextWidth();

    /**
     * Sets the color of the text.
     *
     * @param textColor
     */
    OMNI_KIT_UI_API void setTextColor(const carb::ColorRgba& textColor);

    /**
     * Resets the color of the text.
     *
     * @param textColor
     */
    OMNI_KIT_UI_API void resetTextColor();

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    /**
     * @see Widget::draw
     */
    OMNI_KIT_UI_API void draw(float elapsedTime) override;

    OMNI_KIT_UI_API virtual std::vector<std::string> listSuggestions(const char* prefix);


    /* NOTE: only eEllipsisLeft & eEllipsisRight are supported
             when clipping is used, the TextBox will be readonly & disabled, but not greyed out
    */
    ClippingType getClippingMode(ClippingType mode) const
    {
        return m_clippingMode;
    }

    void setClippingMode(ClippingType mode)
    {
        if (mode == ClippingType::eWrap)
        {
            CARB_LOG_ERROR("TextBox widget does not support ClippingType::eWrap");
            return;
        }

        m_clippingMode = mode;
    }

protected:
    void _onValueChange() override;

private:
    void setText(const char* text);

    bool m_changeValueOnEnter;
    bool m_isReadOnly = false;
    bool m_wasActive = false;
    bool m_showBackground = true;
    char m_text[kMaxLength] = "";
    char m_hint[kMaxLength] = "";
    std::function<void(WidgetRef)> m_valueChangedFn;
    std::function<void(WidgetRef)> m_valueFinalizedFn;
    std::function<std::vector<std::string>(WidgetRef, const char*)> m_listSuggestionsFn;
    SubscriptionId m_valueSubId;
    float m_clippingWidth;
    ClippingType m_clippingMode;
    bool m_customColor = false;
    carb::ColorRgba m_textColor;
};

}
}
}
