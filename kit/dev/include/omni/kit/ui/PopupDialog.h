// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/imgui/ImGui.h>

#include <string>
#include <utility>
#include <vector>

namespace carb
{
namespace imgui
{
struct ImGui;
}
}

namespace omni
{
namespace kit
{
namespace ui
{
/**
 * Defines an PopupDialog class that draws popup dialogbox.
 */
class PopupDialog
{
public:
    /**
     * Constructor.
     *
     * @param title Title of the popup dialog.
     * @param message Message of the popup dialog.
     * @modal True to create a modal popup.
     */
    PopupDialog(const char* title, const char* message, bool modal) : m_title(title), m_message(message), m_modal(modal)
    {
    }

    /**
     * Adds option button to the dialog.
     *
     * @param name Name of the option button.
     * @param tooltop Tooltip of the option button.
     */
    void addOptionButton(const char* name, const char* tooltip)
    {
        m_options.emplace_back(name, tooltip);
    }

    /**
     * Gets the selected option button index.
     *
     * @param index The selected index.
     * @return True if the index is valid. False if none selected.
     */
    bool getSelectedOption(size_t& index) const
    {
        if (m_selectedIndex != kInvalidSelection)
        {
            index = m_selectedIndex;
            return true;
        }
        return false;
    }

    /**
     * Draws the popup window.
     *
     * @param The imgui instance.
     */
    void draw(carb::imgui::ImGui* imgui)
    {
        using namespace carb::imgui;
        imgui->openPopup(m_title.c_str());
        if (m_modal ? imgui->beginPopupModal(m_title.c_str(), nullptr, kWindowFlagAlwaysAutoResize) :
                      imgui->beginPopup(m_title.c_str(), kWindowFlagAlwaysAutoResize))
        {
            imgui->text(m_message.c_str());

            m_selectedIndex = kInvalidSelection;
            for (size_t i = 0; i < m_options.size(); i++)
            {
                if (imgui->button(m_options[i].first.c_str()))
                {
                    m_selectedIndex = i;
                }
                if (imgui->isItemHovered(0) && m_options[i].second.length())
                {
                    imgui->setTooltip(m_options[i].second.c_str());
                }
                imgui->sameLine();
            }
            imgui->endPopup();
        }
    }

private:
    static const size_t kInvalidSelection = SIZE_MAX;

    std::string m_title;
    std::string m_message;
    bool m_modal;
    std::vector<std::pair<std::string, std::string>> m_options;
    size_t m_selectedIndex = kInvalidSelection;
};
}
}
}
