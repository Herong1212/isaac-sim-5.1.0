// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/FilterGroup.h>
#include <omni/kit/ui/ColorScheme.h>
#include <omni/ui/IGlyphManager.h>

#include <string>
#include <vector>

namespace omni
{
namespace kit
{
namespace ui
{
template <typename FilterGroupT>
class FilterGroupWidget
{
public:
    explicit FilterGroupWidget(FilterGroupT& filterGroup) : m_filterGroup(filterGroup)
    {
        m_glyphManager = carb::getFramework()->acquireInterface<omni::ui::IGlyphManager>();
    }

    void draw(carb::imgui::ImGui* imgui, float elapsedTime)
    {
        using namespace carb::imgui;

        const float kFontSize = imgui->getFontSize();
        const carb::Float2 kItemSpacing = imgui->getStyle()->itemSpacing;

        bool filterEnabled = m_filterGroup.isFilterGroupEnabled();
        if (filterEnabled)
        {
            imgui->pushStyleColor(StyleColor::eText, kAssetExplorerFilterIconEnabledColor);
        }

        auto filterGlyph = m_glyphManager->getGlyphInfo("${glyphs}/filter.svg");
        bool filterIconClicked = imgui->selectable(filterGlyph.code, false, 0, { kFontSize, kFontSize });
        if (filterEnabled)
        {
            imgui->popStyleColor();
        }

        // (RMB / hold LMB / Click LMB & No filter is enabled) to open filter list
        bool showFilterList = imgui->isItemClicked(1) || (imgui->isItemClicked(0) && !m_filterGroup.isAnyFilterEnabled());
        m_mouseHeldOnFilterIconTime += elapsedTime;
        if (!(imgui->isItemHovered(0) && imgui->isMouseDown(0)))
        {
            m_mouseHeldOnFilterIconTime = 0.f;
        }

        const float kMouseHoldTime = 0.3f;
        if (showFilterList || m_mouseHeldOnFilterIconTime >= kMouseHoldTime)
        {
            imgui->openPopup("FilterList");
        }
        else
        {
            if (filterIconClicked)
            {
                m_filterGroup.setFilterGroupEnabled(!filterEnabled);
            }
        }

        if (imgui->beginPopup("FilterList", 0))
        {
            imgui->text("Filter");
            imgui->sameLineEx(0.f, kFontSize * 3);
            imgui->textColored(kAssetExplorerClearFilterColor, "Clear Filters");
            bool clearFilters = imgui->isItemClicked(0);

            imgui->separator();

            std::vector<std::string> filterNames;
            m_filterGroup.getFilterNames(filterNames);
            for (auto& name : filterNames)
            {
                if (clearFilters)
                {
                    m_filterGroup.setFilterEnabled(name, false);
                }

                bool enabled = m_filterGroup.isFilterEnabled(name);
                imgui->pushIdString(name.c_str());
                auto checkGlyph = enabled ? m_glyphManager->getGlyphInfo("${glyphs}/check_square.svg") :
                                            m_glyphManager->getGlyphInfo("${glyphs}/square.svg");
                if (imgui->selectable((std::string(checkGlyph.code) + "  ").c_str(), false,
                                      kSelectableFlagDontClosePopups, { 0.f, 0.f }))
                {
                    m_filterGroup.setFilterEnabled(name, !enabled);
                }
                imgui->popId();
                imgui->sameLine();
                imgui->text(name.c_str());
            }
            imgui->endPopup();
        }

        // Draw the tiny triangle at corner of the filter icon
        {
            imgui->sameLine();
            auto cursorPos = imgui->getCursorScreenPos();
            auto drawList = imgui->getWindowDrawList();
            carb::Float2 points[3];

            points[0] = { cursorPos.x - kItemSpacing.x, cursorPos.y + kFontSize * 0.75f + kItemSpacing.y * 0.5f };
            points[1] = { cursorPos.x - kItemSpacing.x, cursorPos.y + kFontSize + kItemSpacing.y * 0.5f };
            points[2] = { cursorPos.x - kItemSpacing.x - kFontSize * 0.25f,
                          cursorPos.y + kFontSize + kItemSpacing.y * 0.5f };

            imgui->addTriangleFilled(
                drawList, points[0], points[1], points[2], imgui->getColorU32StyleColor(StyleColor::eText, 1.f));
            imgui->newLine();
        }
    }

private:
    FilterGroupT& m_filterGroup;
    omni::ui::IGlyphManager* m_glyphManager = nullptr;
    float m_mouseHeldOnFilterIconTime = 0.f;
};
}
}
}
