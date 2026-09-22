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
 * Defines a FixedSizeFrame layout.
 */
class OMNI_KIT_UI_CLASS_API ScrollingFrame : public Container
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ScrollingFrame);

    OMNI_KIT_UI_API ScrollingFrame(const char* title, float width, float height);

    OMNI_KIT_UI_API ~ScrollingFrame();

    OMNI_KIT_UI_API virtual void scrollTo(float scrollTo);

    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;

protected:
    float m_width;
    float m_height;
    bool m_needsScrolling = false;
    float m_scrollTo;
    std::string m_title;
    bool m_defaultOpen;
};

}
}
}
