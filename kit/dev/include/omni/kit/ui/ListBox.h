// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Label.h"

#include <functional>
#include <string>
#include <utility>
#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{


/**
 * Defines a list box.
 */
class OMNI_KIT_UI_CLASS_API ListBox : public Label
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ListBox);

    OMNI_KIT_UI_API explicit ListBox(const char* text,
                                     bool multiSelect = true,
                                     int visibleItemCount = -1,
                                     const std::vector<std::string>& items = {});

    OMNI_KIT_UI_API ~ListBox() override;

    OMNI_KIT_UI_API bool isMultiSelect() const;

    OMNI_KIT_UI_API void setMultiSelect(bool multiSelect);

    OMNI_KIT_UI_API int getItemHeightCount() const;

    OMNI_KIT_UI_API void setItemHeightCount(int itemHeightCount);

    OMNI_KIT_UI_API size_t getItemCount() const;

    OMNI_KIT_UI_API const char* getItemAt(size_t index) const;

    OMNI_KIT_UI_API void addItem(const char* item);

    OMNI_KIT_UI_API void removeItem(size_t index);

    OMNI_KIT_UI_API void clearItems();

    OMNI_KIT_UI_API std::vector<int> getSelected() const;

    OMNI_KIT_UI_API void setSelected(int index, bool selected);

    OMNI_KIT_UI_API void clearSelection();

    OMNI_KIT_UI_API void setSelectionChangedFn(const std::function<void(WidgetRef)>& fn);

    OMNI_KIT_UI_API WidgetType getType() override;

    void draw(float elapsedTime) override;

private:
    int m_itemHeightCount = -1;
    bool m_multiSelect = false;
    int m_selectedIndex = -1;
    std::vector<std::pair<std::string, bool>> m_items;
    std::function<void(WidgetRef)> m_selectionChangedFn;
};
}
}
}
