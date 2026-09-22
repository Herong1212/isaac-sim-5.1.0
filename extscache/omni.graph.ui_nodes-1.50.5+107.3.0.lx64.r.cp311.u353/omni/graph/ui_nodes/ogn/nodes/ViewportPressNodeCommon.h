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

constexpr carb::events::EventType kPressBeganEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.press.began");
constexpr carb::events::EventType kPressEndedEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.press.ended");

class ViewportPressEventPayloads
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

    struct PressBeganValue
    {
        pxr::GfVec2d pressPositionNorm;
        pxr::GfVec2d pressPositionPixel;
        bool isValid;
    };

    struct PressEndedValue
    {
        pxr::GfVec2d releasePositionNorm;
        pxr::GfVec2d releasePositionPixel;
        bool isReleasePositionValid;
        bool isValid;
    };

    // Store a press began event payload
    void setPressBeganPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")),
                 stringMemo.lookup(idict->get<char const*>(payload, "gesture")) };
        pressBeganPayloadMap[key] = PressBeganValue{
            pxr::GfVec2d{ idict->get<double>(payload, "pos_norm_x"), idict->get<double>(payload, "pos_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "pos_pixel_x"), idict->get<double>(payload, "pos_pixel_y") }, true
        };
    }

    // Store a press ended event payload
    void setPressEndedPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")),
                 stringMemo.lookup(idict->get<char const*>(payload, "gesture")) };
        pressEndedPayloadMap[key] = PressEndedValue{
            pxr::GfVec2d{ idict->get<double>(payload, "pos_norm_x"), idict->get<double>(payload, "pos_norm_y") },
            pxr::GfVec2d{ idict->get<double>(payload, "pos_pixel_x"), idict->get<double>(payload, "pos_pixel_y") },
            idict->get<bool>(payload, "pos_valid"), true
        };
    }

    // Invalidate all stored payloads
    void clear()
    {
        for (auto& p : pressBeganPayloadMap)
        {
            p.second.isValid = false;
        }
        for (auto& p : pressEndedPayloadMap)
        {
            p.second.isValid = false;
        }
    }

    bool empty()
    {
        if (std::any_of(pressBeganPayloadMap.begin(), pressBeganPayloadMap.end(),
                        [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }
        if (std::any_of(pressEndedPayloadMap.begin(), pressEndedPayloadMap.end(),
                        [](auto const& p) { return p.second.isValid; }))
        {
            return false;
        }

        return true;
    }

    std::map<Key, PressBeganValue> const& pressBeganPayloads()
    {
        return pressBeganPayloadMap;
    }

    std::map<Key, PressEndedValue> const& pressEndedPayloads()
    {
        return pressEndedPayloadMap;
    }

private:
    std::map<Key, PressBeganValue> pressBeganPayloadMap;
    std::map<Key, PressEndedValue> pressEndedPayloadMap;
    StringMemo stringMemo;
};

using ViewportPressEventStateKey = ViewportPressEventPayloads::Key;

struct ViewportPressEventStateValue
{
    pxr::GfVec2d pressPositionNorm = { 0.0, 0.0 };
    pxr::GfVec2d pressPositionPixel = { 0.0, 0.0 };
    pxr::GfVec2d releasePositionNorm = { 0.0, 0.0 };
    pxr::GfVec2d releasePositionPixel = { 0.0, 0.0 };
    bool isPressed = false;
    bool isReleasePositionValid = false;
};

using ViewportPressEventStates = std::map<ViewportPressEventStateKey, ViewportPressEventStateValue>;

}
}
}
