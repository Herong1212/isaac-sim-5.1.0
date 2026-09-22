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

constexpr carb::events::EventType kPickingEventType = CARB_EVENTS_TYPE_FROM_STR("omni.graph.picking");

pxr::TfToken const kTrackedPrimsRelToken{ "inputs:trackedPrims" };

class PickingEventPayloads
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

    struct Value
    {
        char const* pickedPrimPath;
        pxr::GfVec3d pickedWorldPos;
        bool isValid;
    };

    // Store an event payload as a key-value pair
    void setPayload(carb::dictionary::Item* payload)
    {
        auto idict = carb::dictionary::getCachedDictionaryInterface();

        Key key{ stringMemo.lookup(idict->get<char const*>(payload, "viewport")),
                 stringMemo.lookup(idict->get<char const*>(payload, "gesture")) };
        payloadMap[key] = Value{ stringMemo.lookup(idict->get<char const*>(payload, "path")),
                                 pxr::GfVec3d{ idict->get<double>(payload, "pos_x"), idict->get<double>(payload, "pos_y"),
                                               idict->get<double>(payload, "pos_z") },
                                 true };
    }

    // Retrieve a payload value by key
    Value const* getPayloadValue(char const* viewportWindowName, char const* gestureName)
    {
        auto it = payloadMap.find({ viewportWindowName, gestureName });
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
