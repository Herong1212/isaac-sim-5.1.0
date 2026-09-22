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

constexpr carb::events::EventType kHoverBeganEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.hover.began");
constexpr carb::events::EventType kHoverChangedEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.hover.changed");
constexpr carb::events::EventType kHoverEndedEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.hover.ended");

class ViewportHoverEventPayloads
{
public:
    struct Key
    {
        char const* viewportWindowName;

        bool operator<(Key const& other) const
        {
            return std::strcmp(viewportWindowName, other.viewportWindowName) < 0;
        }
    };

    struct HoverBeganValue
    {
        pxr::GfVec2d positionNorm;
        pxr::GfVec2d positionPixel;
        bool isValid;
    };

    struct HoverChangedValue
    {
        pxr::GfVec2d positionNorm;
        pxr::GfVec2d positionPixel;
        pxr::GfVec2d velocityNorm;
        pxr::GfVec2d velocityPixel;
        bool isValid;
    };

    struct HoverEndedValue
    {
        bool isValid;
    };

    // Store a hover began event payload
    void setHoverBeganPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")) };
        hoverBeganPayloadMap[key] = HoverBeganValue{
            pxr::GfVec2d{ idict->get<double>(payload, "pos_norm_x"), idict->get<double>(payload, "pos_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "pos_pixel_x"), idict->get<double>(payload, "pos_pixel_y") }, true
        };
    }

    // Store a hover changed event payload
    void setHoverChangedPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")) };
        hoverChangedPayloadMap[key] = HoverChangedValue{
            pxr::GfVec2d{ idict->get<double>(payload, "pos_norm_x"), idict->get<double>(payload, "pos_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "pos_pixel_x"), idict->get<double>(payload, "pos_pixel_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "vel_norm_x"), idict->get<double>(payload, "vel_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "vel_pixel_x"), idict->get<double>(payload, "vel_pixel_y") }, true
        };
    }

    // Store a hover ended event payload
    void setHoverEndedPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")) };
        hoverEndedPayloadMap[key] = HoverEndedValue{ true };
    }

    // Invalidate all stored payloads
    void clear()
    {
        for (auto& p : hoverBeganPayloadMap)
        {
            p.second.isValid = false;
        }
        for (auto& p : hoverChangedPayloadMap)
        {
            p.second.isValid = false;
        }
        for (auto& p : hoverEndedPayloadMap)
        {
            p.second.isValid = false;
        }
    }

    bool empty()
    {
        if (std::any_of(hoverBeganPayloadMap.begin(), hoverBeganPayloadMap.end(),
                        [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }
        if (std::any_of(hoverChangedPayloadMap.begin(), hoverChangedPayloadMap.end(),
                        [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }
        if (std::any_of(hoverEndedPayloadMap.begin(), hoverEndedPayloadMap.end(),
                        [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }

        return true;
    }

    std::map<Key, HoverBeganValue> const& hoverBeganPayloads()
    {
        return hoverBeganPayloadMap;
    }

    std::map<Key, HoverChangedValue> const& hoverChangedPayloads()
    {
        return hoverChangedPayloadMap;
    }

    std::map<Key, HoverEndedValue> const& hoverEndedPayloads()
    {
        return hoverEndedPayloadMap;
    }

private:
    std::map<Key, HoverBeganValue> hoverBeganPayloadMap;
    std::map<Key, HoverChangedValue> hoverChangedPayloadMap;
    std::map<Key, HoverEndedValue> hoverEndedPayloadMap;
    StringMemo stringMemo;
};

using ViewportHoverEventStateKey = ViewportHoverEventPayloads::Key;

struct ViewportHoverEventStateValue
{
    bool isHovered = false;
    pxr::GfVec2d positionNorm = { 0.0, 0.0 };
    pxr::GfVec2d positionPixel = { 0.0, 0.0 };
    pxr::GfVec2d velocityNorm = { 0.0, 0.0 };
    pxr::GfVec2d velocityPixel = { 0.0, 0.0 };
};

using ViewportHoverEventStates = std::map<ViewportHoverEventStateKey, ViewportHoverEventStateValue>;

}
}
}
