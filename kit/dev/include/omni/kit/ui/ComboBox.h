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
#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines a combo box.
 */
template <class T>
class OMNI_KIT_UI_CLASS_API ComboBox : public SimpleValueWidget<T>
{
public:
    static const WidgetType kType = CARB_HASH_TYPE(omni::kit::ui::ComboBox<T>);

    OMNI_KIT_UI_API explicit ComboBox(const char* text,
                                      const std::vector<T>& items = {},
                                      const std::vector<std::string>& displayNames = {});

    OMNI_KIT_UI_API ~ComboBox() override;

    OMNI_KIT_UI_API size_t getItemCount() const;

    OMNI_KIT_UI_API const T& getItemAt(size_t index) const;

    OMNI_KIT_UI_API void addItem(const T& item, const std::string& displayName = "");

    OMNI_KIT_UI_API void removeItem(size_t index);

    OMNI_KIT_UI_API void clearItems();

    OMNI_KIT_UI_API void setItems(const std::vector<T>& items, const std::vector<std::string>& displayNames = {});

    OMNI_KIT_UI_API int64_t getSelectedIndex() const;

    OMNI_KIT_UI_API void setSelectedIndex(int64_t index);

    OMNI_KIT_UI_API WidgetType getType() override;

protected:
    virtual bool _isTransientChangeSupported() const override
    {
        return false;
    }

    bool _drawImGuiWidget(carb::imgui::ImGui* imgui, T& value) override;

private:
    struct Element
    {
        T value;
        std::string displayName;
    };

    std::vector<Element> m_items;
    int64_t m_selectedIndex = -1;
};

using ComboBoxString = ComboBox<std::string>;
using ComboBoxInt = ComboBox<int>;


}
}
}
