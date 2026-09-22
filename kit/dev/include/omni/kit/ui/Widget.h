// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"
#include "Common.h"

#include <omni/ui/Font.h>

#include <functional>
#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

class Container;
class Window;

typedef uint64_t WidgetType;

/**
 * Parent this class it to asscoiate your own data with a Widget.
 */
class WidgetUserData
{
public:
    virtual ~WidgetUserData() = default;
};


/**
 * Defines a widget.
 */
class OMNI_KIT_UI_CLASS_API Widget : public std::enable_shared_from_this<Widget>
{
    friend class Container;
    friend class Window;

public:
    /**
     * Constructor.
     */
    OMNI_KIT_UI_API Widget();

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API virtual ~Widget();

    /**
     * Determines if the widget is enabled.
     *
     * @return true if the widget is enabled, false if disabled.
     */
    OMNI_KIT_UI_API bool isEnabled() const;

    /**
     * Set the widget to enabled.
     */
    OMNI_KIT_UI_API void setEnabled(bool enable);

    /**
     * Gets the layout this widget is within.
     *
     * A nullptr indicates the widget is not in a layout but directly in window.
     *
     * @return The layout this widget is within.
     */
    OMNI_KIT_UI_API Container* getLayout() const;

    /**
     * Gets the type of widget.
     *
     * @return The type of widget.
     */
    OMNI_KIT_UI_API virtual WidgetType getType() = 0;

    /**
     * Draws the widget.
     *
     * @param elapsedTime The time elapsed (in seconds)
     */
    OMNI_KIT_UI_API virtual void draw(float elapsedTime) = 0;

    /**
     * set the font
     *
     * @param font The font to use
     */
    OMNI_KIT_UI_API void setFontStyle(omni::ui::FontStyle fontStyle);

    /**
     * get the font
     *
     * @return The font in use
     */
    OMNI_KIT_UI_API omni::ui::FontStyle getFontStyle() const;

    /**
     * Get the font size (height in pixels) of the current font style with the current scaling applied.
     *
     * @return The font size.
     */
    OMNI_KIT_UI_API float getFontSize() const;

    /**
     * Sets the callback function when the widget recieves a dragdrop payload
     *
     * @param fn The callback function when the widget recieves a dragdrop payload
     * @param payloadName the name of acceptable payload
     */
    OMNI_KIT_UI_API void setDragDropFn(const std::function<void(WidgetRef, const char*)>& fn, const char* payloadName);

    /**
     * Sets the callback function when the widget is dragged.
     *
     * @param fn The callback function when the widget is dragged.
     */
    void setDraggingFn(const std::function<void(WidgetRef, DraggingType)>& fn)
    {
        m_draggedFn = fn;
    }

    /**
     * A way to associate arbitrary user data with it.
     */
    std::shared_ptr<WidgetUserData> userData;

    /**
     * Determines if the widget is visible.
     *
     * @return true if the widget is visible, false if hidden.
     */
    OMNI_KIT_UI_API bool isVisible() const;

    /**
     * Set the widget visibility state.
     */
    OMNI_KIT_UI_API void setVisible(bool visible);

    Length width = Pixel(0);
    Length height = Pixel(0);

    static constexpr size_t kUniqueIdSize = 4;

protected:
    bool m_enabled = true;
    bool m_visible = true;
    bool m_isDragging;
    Container* m_layout = nullptr;

    char m_uniqueId[kUniqueIdSize + 1];
    std::string m_label;

    omni::ui::FontStyle m_fontStyle;
    carb::imgui::Font* m_font;
    std::function<void(WidgetRef, const char*)> m_dragDropFn;
    std::function<void(WidgetRef, DraggingType)> m_draggedFn;
    std::string m_dragDropPayloadName;
};
}
}
}
