// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Image.h"
#include "ScalarXYZ.h"
#include "ValueWidget.h"

#include <memory>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a ScalarXYZW widget.
 */
class OMNI_KIT_UI_CLASS_API ScalarXYZW : public ValueWidget<carb::Double4>
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ScalarXYZW);

    /**
     * Constructor.
     *
     */
    OMNI_KIT_UI_API ScalarXYZW(
        const char* displayFormat, float speed, float wrapValue, float minValue, float maxValue, carb::Double4 value = {});

    /**
     * Destructor.
     */
    OMNI_KIT_UI_API ~ScalarXYZW();

    /**
     * @see Widget::getType
     */
    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;

private:
    std::shared_ptr<ScalarXYZ> m_scalar;
    bool m_edited;
    bool m_init;
};
}
}
}
