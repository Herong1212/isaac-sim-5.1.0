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

#include <cstdint>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a input drag.
 *
 * Usage:
 * Drag<int, int>
 * Drag<carb::Int2, int>
 * Drag<double>
 * Drag<carb::Double2>
 * Drag<carb::Double3>
 * Drag<carb::Double4>
 */
template <class T, class RangeT = double>
class OMNI_KIT_UI_CLASS_API Drag : public SimpleValueWidget<T>
{
public:
    static const WidgetType kType;

    OMNI_KIT_UI_API explicit Drag(
        const char* text = "", T value = {}, RangeT min = {}, RangeT max = {}, float valueDragSpeed = 1.0f);

    OMNI_KIT_UI_API ~Drag();

    RangeT min;
    RangeT max;
    std::string format;
    float dragSpeed;

    OMNI_KIT_UI_API WidgetType getType() override;

protected:
    bool _drawImGuiWidget(carb::imgui::ImGui* imgui, T& value) override;
};

#if CARB_POSIX && !CARB_TOOLCHAIN_CLANG
extern template class OMNI_KIT_UI_API Drag<int, int>;
extern template class OMNI_KIT_UI_API Drag<uint32_t, uint32_t>;
extern template class OMNI_KIT_UI_API Drag<carb::Int2, int>;
extern template class OMNI_KIT_UI_API Drag<double>;
extern template class OMNI_KIT_UI_API Drag<carb::Double2>;
extern template class OMNI_KIT_UI_API Drag<carb::Double3>;
extern template class OMNI_KIT_UI_API Drag<carb::Double4>;
#endif

using DragInt = Drag<int, int>;
using DragUInt = Drag<uint32_t, uint32_t>;
using DragInt2 = Drag<carb::Int2, int>;
using DragDouble = Drag<double>;
using DragDouble2 = Drag<carb::Double2>;
using DragDouble3 = Drag<carb::Double3>;
using DragDouble4 = Drag<carb::Double4>;

}
}
}
