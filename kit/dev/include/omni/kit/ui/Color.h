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
 * Defines a color edit.
 */
template <class T>
class OMNI_KIT_UI_CLASS_API Color : public SimpleValueWidget<T>
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::Color<T>);

    OMNI_KIT_UI_API explicit Color(const char* text = "", T value = {});

    OMNI_KIT_UI_API ~Color();

    OMNI_KIT_UI_API WidgetType getType() override;

protected:
    bool _drawImGuiWidget(carb::imgui::ImGui* imgui, T& value) override;
};

#if CARB_POSIX
extern template class OMNI_KIT_UI_API Color<carb::ColorRgb>;
extern template class OMNI_KIT_UI_API Color<carb::ColorRgba>;
#endif

using ColorRgb = Color<carb::ColorRgb>;
using ColorRgba = Color<carb::ColorRgba>;

}
}
}
