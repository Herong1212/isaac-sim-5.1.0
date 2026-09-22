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
 * Defines a slider.
 *
 * Usage:
 * Slider<int>
 * Slider<double>
 */
template <class T, class RangeT = double>
class OMNI_KIT_UI_CLASS_API Slider : public SimpleValueWidget<T>
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Slider<T>);

    OMNI_KIT_UI_API explicit Slider(const char* text = "", T value = {}, RangeT min = {}, RangeT max = {});

    OMNI_KIT_UI_API ~Slider();

    RangeT min = {};
    RangeT max = {};
    float power = 1.0f;
    std::string format;

    WidgetType getType() override;

protected:
    bool _drawImGuiWidget(carb::imgui::ImGui* imgui, T& value) override;
};

#if CARB_POSIX
extern template class OMNI_KIT_UI_API Slider<int, int>;
extern template class OMNI_KIT_UI_API Slider<uint32_t, uint32_t>;
extern template class OMNI_KIT_UI_API Slider<carb::Int2, int32_t>;
extern template class OMNI_KIT_UI_API Slider<double>;
extern template class OMNI_KIT_UI_API Slider<carb::Double2>;
extern template class OMNI_KIT_UI_API Slider<carb::Double3>;
extern template class OMNI_KIT_UI_API Slider<carb::Double4>;
#endif

}
}
}
