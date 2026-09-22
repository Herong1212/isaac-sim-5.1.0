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

constexpr carb::events::EventType kScrollEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.viewport.scroll");

class ViewportScrollEventPayloads
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

    struct Value
    {
        pxr::GfVec2d positionNorm;
        pxr::GfVec2d positionPixel;
        float scrollValue;
        bool isValid;
    };

    // Store an event payload as a key-value pair
    void setPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")) };
        payloadMap[key] =
            Value{ pxr::GfVec2d{ idict->get<double>(payload, "pos_norm_x"), idict->get<double>(payload, "pos_norm_y") },
                   pxr::GfVec2d{ idict->get<double>(payload, "pos_pixel_x"), idict->get<double>(payload, "pos_pixel_y") },
                   idict->get<float>(payload, "scroll"), true };
    }

    // Retrieve a payload value by key
    Value const* getPayloadValue(char const* viewportWindowName)
    {
        auto it = payloadMap.find({ viewportWindowName });
        if (it != payloadMap.end() && it->second.isValid)
        {
            return &(it->second);
        }

        return nullptr;
    }

    // Invalidate all stored payloads
    void clear()
    {
        for (auto& p : payloadMap)
        {
            p.second.isValid = false;
        }
    }

    // Check if there exists a valid payload
    bool empty()
    {
        return std::none_of(payloadMap.begin(), payloadMap.end(), [](auto const& p) { return p.second.isValid; });
    }

private:
    std::map<Key, Value> payloadMap;
    StringMemo stringMemo;
};

}
}
}
