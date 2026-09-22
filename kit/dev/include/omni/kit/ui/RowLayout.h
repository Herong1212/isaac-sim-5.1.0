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

namespace omni
{
namespace kit
{
namespace ui
{
/**
 *
 */
class OMNI_KIT_UI_CLASS_API RowLayout : public Container
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::RowLayout);

    OMNI_KIT_UI_API RowLayout();

    OMNI_KIT_UI_API ~RowLayout() override;

    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;
};

}
}
}
