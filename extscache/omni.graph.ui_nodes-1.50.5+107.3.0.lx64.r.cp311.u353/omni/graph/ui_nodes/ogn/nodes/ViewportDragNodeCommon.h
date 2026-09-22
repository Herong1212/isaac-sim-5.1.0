// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include <carb/dictionary/DictionaryUtils.h>
#include <carb/dictionary/IDictionary.h>

#include "UINodeCommon.h"

namespace omni
{
namespace graph
{
namespace ui_nodes
{

constexpr carb::events::EventType kDragBeganEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.drag.began");
constexpr carb::events::EventType kDragChangedEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.drag.changed");
constexpr carb::events::EventType kDragEndedEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.drag.ended");

class ViewportDragEventPayloads
{
public:
    struct Key
    {
        char const* viewportWindowName;
        char const* gestureName;

        bool operator<(Key const& other) const
        {
            int const ret = std::strcmp(viewportWindowName, other.viewportWindowName);
            if (ret < 0)
                return true;
            else if (ret <= 0)
                return std::strcmp(gestureName, other.gestureName) < 0;

            return false;
        }
    };

    struct DragBeganValue
    {
        pxr::GfVec2d initialPositionNorm;
        pxr::GfVec2d initialPositionPixel;
        pxr::GfVec2d currentPositionNorm;
        pxr::GfVec2d currentPositionPixel;
        pxr::GfVec2d velocityNorm;
        pxr::GfVec2d velocityPixel;
        bool isValid;
    };

    struct DragChangedValue
    {
        pxr::GfVec2d currentPositionNorm;
        pxr::GfVec2d currentPositionPixel;
        pxr::GfVec2d velocityNorm;
        pxr::GfVec2d velocityPixel;
        bool isValid;
    };

    struct DragEndedValue
    {
        bool isValid;
    };

    // Store a drag began event payload
    void setDragBeganPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")),
                 stringMemo.lookup(idict->get<char const*>(payload, "gesture")) };
        dragBeganPayloadMap[key] = DragBeganValue{
            pxr::GfVec2d{ idict->get<double>(payload, "start_pos_norm_x"),
                          idict->get<double>(payload, "start_pos_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "start_pos_pixel_x"),
                          idict->get<double>(payload, "start_pos_pixel_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "pos_norm_x"), idict->get<double>(payload, "pos_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "pos_pixel_x"), idict->get<double>(payload, "pos_pixel_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "vel_norm_x"), idict->get<double>(payload, "vel_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "vel_pixel_x"), idict->get<double>(payload, "vel_pixel_y") },
            true
        };
    }

    // Store a drag changed event payload
    void setDragChangedPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")),
                 stringMemo.lookup(idict->get<char const*>(payload, "gesture")) };
        dragChangedPayloadMap[key] = DragChangedValue{
            pxr::GfVec2d{ idict->get<double>(payload, "pos_norm_x"), idict->get<double>(payload, "pos_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "pos_pixel_x"), idict->get<double>(payload, "pos_pixel_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "vel_norm_x"), idict->get<double>(payload, "vel_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "vel_pixel_x"), idict->get<double>(payload, "vel_pixel_y") }, true
        };
    }

    // Store a drag ended event payload
    void setDragEndedPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")),
                 stringMemo.lookup(idict->get<char const*>(payload, "gesture")) };
        dragEndedPayloadMap[key] = DragEndedValue{ true };
    }

    // Invalidate all stored payloads
    void clear()
    {
        for (auto& p : dragBeganPayloadMap)
        {
            p.second.isValid = false;
        }
        for (auto& p : dragChangedPayloadMap)
        {
            p.second.isValid = false;
        }
        for (auto& p : dragEndedPayloadMap)
        {
            p.second.isValid = false;
        }
    }

    bool empty()
    {
        if (std::any_of(
                dragBeganPayloadMap.begin(), dragBeganPayloadMap.end(), [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }
        if (std::any_of(dragChangedPayloadMap.begin(), dragChangedPayloadMap.end(),
                        [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }
        if (std::any_of(
                dragEndedPayloadMap.begin(), dragEndedPayloadMap.end(), [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }

        return true;
    }

    std::map<Key, DragBeganValue> const& dragBeganPayloads()
    {
        return dragBeganPayloadMap;
    }

    std::map<Key, DragChangedValue> const& dragChangedPayloads()
    {
        return dragChangedPayloadMap;
    }

    std::map<Key, DragEndedValue> const& dragEndedPayloads()
    {
        return dragEndedPayloadMap;
    }

private:
    std::map<Key, DragBeganValue> dragBeganPayloadMap;
    std::map<Key, DragChangedValue> dragChangedPayloadMap;
    std::map<Key, DragEndedValue> dragEndedPayloadMap;
    StringMemo stringMemo;
};

using ViewportDragEventStateKey = ViewportDragEventPayloads::Key;

struct ViewportDragEventStateValue
{
    bool isDragInProgress = false;
    pxr::GfVec2d initialPositionNorm = { 0.0, 0.0 };
    pxr::GfVec2d initialPositionPixel = { 0.0, 0.0 };
    pxr::GfVec2d currentPositionNorm = { 0.0, 0.0 };
    pxr::GfVec2d currentPositionPixel = { 0.0, 0.0 };
    pxr::GfVec2d velocityNorm = { 0.0, 0.0 };
    pxr::GfVec2d velocityPixel = { 0.0, 0.0 };
};

using ViewportDragEventStates = std::map<ViewportDragEventStateKey, ViewportDragEventStateValue>;

}
}
}
