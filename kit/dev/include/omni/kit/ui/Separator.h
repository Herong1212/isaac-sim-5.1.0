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

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a separator element.
 */
class OMNI_KIT_UI_CLASS_API Separator : public Widget
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Separator);

    OMNI_KIT_UI_API Separator();

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    /**
     * @see Widget::draw
     */
    void draw(float elapsedTime) override;
};

}
}
}
