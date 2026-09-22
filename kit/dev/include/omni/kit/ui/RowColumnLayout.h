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

#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a row/column (wrapping horizontal-style) layout.
 */
class OMNI_KIT_UI_CLASS_API RowColumnLayout : public Container
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::RowColumnLayout);

    OMNI_KIT_UI_API RowColumnLayout(size_t columnCount, bool columnBorders);

    OMNI_KIT_UI_API ~RowColumnLayout();

    OMNI_KIT_UI_API const Length& getColumnWidth(size_t index) const;

    OMNI_KIT_UI_API void setColumnWidth(size_t index, Length length, float min = 0.0f, float max = 0.0f);

    void setColumnWidth(size_t index, float width, float min = 0.0f, float max = 0.0f)
    {
        setColumnWidth(index, Pixel(width), min, max);
    }

    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;

protected:
    typedef struct
    {
        Length len;
        float min;
        float max;
    } ColumnSize;

    std::vector<ColumnSize> m_columnWidths;
    bool m_columnBorders = false;
};
}
}
}
