// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "ColorScheme.h"
#include "Widget.h"

namespace omni
{
namespace kit
{
namespace ui
{
/**
 * Defines a progress bar.
 */
class OMNI_KIT_UI_CLASS_API ProgressBar : public Widget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ProgressBar);

    OMNI_KIT_UI_API ProgressBar(Length width,
                                Length height = Pixel(0),
                                const carb::Float4& color = kStatusBarProgressColor);

    OMNI_KIT_UI_API ProgressBar(float width, const carb::Float4& color = kStatusBarProgressColor);

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API virtual ~ProgressBar();

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API virtual WidgetType getType();

    /**
     * @see Widget::draw
     */
    OMNI_KIT_UI_API virtual void draw(float elapsedTime);

    /**
     * Set progress
     *
     * @param value  The current value of progress bar (between 0-1).
     * @param text   The overlay text for the progress bar. If nullptr, the automatic percentage text is displayed.
     */
    OMNI_KIT_UI_API void setProgress(float value, const char* text = nullptr);

    /**
     * Get current progress
     *
     * @return The current value of progress bar (between 0-1).
     */
    OMNI_KIT_UI_API float getProgress() const;

    /**
     * Get current overlay
     *
     * @return The current overlay of progress bar.
     */
    OMNI_KIT_UI_API const char* getOverlay() const;

    /**
     * Set color of bar
     *
     * @param color Value in carb::Float4.
     */
    OMNI_KIT_UI_API void setColor(carb::Float4 color);

    /**
     * Get color of bar
     *
     * @return color Value in carb::Float4.
     */
    OMNI_KIT_UI_API carb::Float4 getColor() const;

protected:
    float m_value; ///< The progress bar value (between 0-1).
    carb::Float4 m_color; // The color of progress bar.
};
}
}
}
