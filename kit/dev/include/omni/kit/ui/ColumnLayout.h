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

#include <carb/Types.h>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a column(vertical-style) layout.
 */
class OMNI_KIT_UI_CLASS_API ColumnLayout : public Container
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ColumnLayout);

    OMNI_KIT_UI_API explicit ColumnLayout(int itemSpacing = -1, int paddingX = -1, int paddingY = -1);

    OMNI_KIT_UI_API ~ColumnLayout();

    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;

protected:
    carb::Int2 m_padding;
};

}
}
}
