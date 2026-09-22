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

#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a input field.
 *
 * Usage:
 * Field<int>
 * Field<double>
 */
template <class T>
class OMNI_KIT_UI_CLASS_API Field : public SimpleValueWidget<T>
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Field<T>);

    OMNI_KIT_UI_API explicit Field(const char* text, T value = 0, T step = 1, T stepFast = 100);

    OMNI_KIT_UI_API ~Field();

    T step = 0;
    T stepFast = 0;
    std::string format;

    OMNI_KIT_UI_API WidgetType getType() override;

protected:
    bool _drawImGuiWidget(carb::imgui::ImGui* imgui, T& value) override;
};

}
}
}
