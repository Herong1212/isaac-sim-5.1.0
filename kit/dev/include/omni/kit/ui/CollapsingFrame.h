// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Container.h"

#include <string>

namespace omni
{
namespace kit
{
namespace ui
{
/**
 * Defines a expanding/collapsing frame layout.
 */
class OMNI_KIT_UI_CLASS_API CollapsingFrame : public Container
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::CollapsingFrame);

    OMNI_KIT_UI_API CollapsingFrame(const char* title, bool defaultOpen);

    OMNI_KIT_UI_API ~CollapsingFrame();

    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;

    void setTitle(const char* title)
    {
        m_title = title;
    }
    const char* getTitle() const
    {
        return m_title.c_str();
    }

    void setOpen(bool open)
    {
        m_open = open;
    }

    bool isOpen() const
    {
        return m_open;
    }

    void setUseFrameBackgroundColor(bool useFrameBackgroundColor)
    {
        m_useFrameBackgroundColor = useFrameBackgroundColor;
    }
    bool getUseFrameBackgroundColor() const
    {
        return m_useFrameBackgroundColor;
    }

protected:
    std::string m_title;
    bool m_open;
    float m_calculatedHeight;
    bool m_useFrameBackgroundColor;
};

}
}
}
