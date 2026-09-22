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

#include <omni/kit/KitUtils.h>
#include <omni/ui/Font.h>
#include <omni/ui/IGlyphManager.h>

#include <cmath>
#include <functional>
#include <limits>
#include <memory>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

class Widget;
using WidgetRef = std::shared_ptr<Widget>;

struct Mat44
{
    carb::Double4 rows[4];
};

enum class ClippingType
{
    eNone,
    eEllipsisLeft,
    eEllipsisRight,
    eWrap,
    eCount
};

enum class DraggingType
{
    eStarted,
    eStopped
};

enum class UnitType
{
    ePixel,
    ePercent
};

struct Length
{
    float value;
    UnitType unit;
};

struct Percent : public Length
{
    explicit Percent(float v) : Length{ v, UnitType::ePercent }
    {
    }
};

struct Pixel : public Length
{
    explicit Pixel(float v) : Length{ v, UnitType::ePixel }
    {
    }
};

inline float calculateWidth(const Length& length, const float usedWidth = 0.0f)
{
    if (length.unit == UnitType::ePercent)
        return length.value * 0.01f * (getImGui()->getWindowContentRegionWidth() - usedWidth);
    return length.value;
}

inline float calculateHeight(const Length& length)
{
    if (length.unit == UnitType::ePercent)
        return length.value * 0.01f * getImGui()->getWindowContentRegionWidth();
    return length.value;
}

inline const char* getCustomGlyphCode(const char* glyphFilePath, omni::ui::FontStyle fontStyle)
{
    return getGlyphManager()->getGlyphInfo(glyphFilePath, fontStyle).code;
}

inline bool clipText(ClippingType clipType, std::string& text, float& clippingWidth, const float itemWidth, size_t maxLength)
{
    carb::imgui::ImGui* imgui = getImGui();

    using OnClipText = std::function<std::string(const std::string& str, float itemWidth)>;
    auto clipFn = [&text, &clippingWidth, itemWidth, imgui](OnClipText onClipText) {
        // only re-build m_clippedText when the column is re-sized
        if (itemWidth != clippingWidth)
        {
            std::string fullText = text;
            carb::Float2 textWidth = imgui->calcTextSize(text.c_str(), nullptr, false, -1.0f);

            if (textWidth.x > itemWidth && itemWidth > 0.0f)
            {
                text = onClipText(fullText, itemWidth);
            }
            clippingWidth = itemWidth;
            return true;
        }
        return false;
    };

    switch (clipType)
    {
    case ClippingType::eEllipsisLeft:
        return clipFn([maxLength, imgui](const std::string& fullText, float itemWidth) {
            size_t index = 0;
            std::string text = fullText;

            while (++index < fullText.length())
            {
                text = "..." + fullText.substr(index);
                carb::Float2 textWidth = imgui->calcTextSize(text.c_str(), nullptr, false, -1.0f);
                if (textWidth.x < itemWidth || text.length() == maxLength - 1)
                    break;
            }
            return text;
        });
    case ClippingType::eEllipsisRight:
        return clipFn([maxLength, imgui](const std::string& fullText, float itemWidth) {
            int64_t index = static_cast<int64_t>(fullText.length());
            std::string text = fullText;

            while (--index > 0)
            {
                text = fullText.substr(0, index) + "...";
                carb::Float2 textWidth = imgui->calcTextSize(text.c_str(), nullptr, false, -1.0f);
                if (textWidth.x < itemWidth || text.length() == maxLength - 1)
                    break;
            }
            return text;
        });

    case ClippingType::eWrap:
        // not supported
    default:
        break;
    }
    return false;
}

inline bool handleDragging(const std::function<void(WidgetRef, DraggingType)>& draggedFn, WidgetRef widget, bool isDragging)
{
    carb::imgui::ImGui* imgui = getImGui();
    bool dragging = imgui->isMouseDragging(0, -1.0f);

    if (draggedFn != nullptr)
    {
        // dragging handling
        if (dragging == true && isDragging == false)
            draggedFn(widget, DraggingType::eStarted);
        else if (dragging == false && isDragging == true)
            draggedFn(widget, DraggingType::eStopped);
    }

    return dragging;
}

inline void handleDragDrop(std::function<void(WidgetRef, const char*)>& dragDropFn,
                           const char* dragDropPayloadName,
                           WidgetRef widget)
{
    carb::imgui::ImGui* imgui = getImGui();

    // handle drag-drop callback
    if (dragDropFn != nullptr && (dragDropPayloadName != nullptr && dragDropPayloadName[0] != 0) &&
        imgui->beginDragDropTarget())
    {
        const carb::imgui::Payload* payload = imgui->acceptDragDropPayload(dragDropPayloadName, 0);

        if (payload && payload->isDelivery())
        {
            dragDropFn(widget, reinterpret_cast<const char*>(payload->data));
        }
        imgui->endDragDropTarget();
    }
}

template <class T>
inline bool almostEqual(T a, T b)
{
    return a == b;
}

static constexpr float kDefaultEpsilonF = 0.001f;
static constexpr double kDefaultEpsilonD = 0.0001;

inline bool almostEqual(double a, double b, double epsilon = kDefaultEpsilonD)
{
    return std::abs(a - b) < epsilon;
}

inline bool almostEqual(float a, float b, float epsilon = std::numeric_limits<float>::epsilon())
{
    return std::abs(a - b) < epsilon;
}

inline bool almostEqual(carb::ColorRgb a, carb::ColorRgb b, float epsilon = kDefaultEpsilonF)
{
    return almostEqual(a.r, b.r, epsilon) && almostEqual(a.g, b.g, epsilon) && almostEqual(a.b, b.b, epsilon);
}

inline bool almostEqual(carb::ColorRgba a, carb::ColorRgba b, float epsilon = kDefaultEpsilonF)
{
    return almostEqual(a.r, b.r, epsilon) && almostEqual(a.g, b.g, epsilon) && almostEqual(a.b, b.b, epsilon) &&
           almostEqual(a.a, b.a, epsilon);
}

inline bool almostEqual(carb::Float3 a, carb::Float3 b, float epsilon = kDefaultEpsilonF)
{
    return almostEqual(a.x, b.x, epsilon) && almostEqual(a.y, b.y, epsilon) && almostEqual(a.z, b.z, epsilon);
}

inline bool almostEqual(carb::Double2 a, carb::Double2 b, double epsilon = kDefaultEpsilonD)
{
    return almostEqual(a.x, b.x, epsilon) && almostEqual(a.y, b.y, epsilon);
}

inline bool almostEqual(carb::Double3 a, carb::Double3 b, double epsilon = kDefaultEpsilonD)
{
    return almostEqual(a.x, b.x, epsilon) && almostEqual(a.y, b.y, epsilon) && almostEqual(a.z, b.z, epsilon);
}

inline bool almostEqual(carb::Double4 a, carb::Double4 b, double epsilon = kDefaultEpsilonD)
{
    return almostEqual(a.x, b.x, epsilon) && almostEqual(a.y, b.y, epsilon) && almostEqual(a.z, b.z, epsilon) &&
           almostEqual(a.w, b.w, epsilon);
}

inline bool almostEqual(ui::Mat44 a, ui::Mat44 b, double epsilon = kDefaultEpsilonD)
{
    return almostEqual(a.rows[0], b.rows[0], epsilon) && almostEqual(a.rows[1], b.rows[1], epsilon) &&
           almostEqual(a.rows[2], b.rows[2], epsilon) && almostEqual(a.rows[3], b.rows[3], epsilon);
}

inline bool almostEqual(carb::Int2 a, carb::Int2 b)
{
    return (a.x == b.x) && (a.y == b.y);
}

}
}
}
