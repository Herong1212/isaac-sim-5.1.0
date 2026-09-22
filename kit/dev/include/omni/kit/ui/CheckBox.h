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

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a check box.
 */
class OMNI_KIT_UI_CLASS_API CheckBox : public SimpleValueWidget<bool>
{
public:
    static const WidgetType kType = CARB_HASH_STRING("CheckBox");

    OMNI_KIT_UI_API explicit CheckBox(const char* text = "",
                                      bool value = false,
                                      bool leftHanded = false,
                                      bool styled = false);

    OMNI_KIT_UI_API ~CheckBox() override;

    OMNI_KIT_UI_API WidgetType getType() override;

    bool styled;

protected:
    bool _drawImGuiWidget(carb::imgui::ImGui* imgui, bool& value) override;
};
}
}
}
