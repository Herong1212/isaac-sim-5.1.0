// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Types.h>
#include <carb/logging/Log.h>

#include <unordered_map>

namespace omni
{
namespace kit
{
namespace ui
{
// Generic
const carb::Float4 kErrorMessageColor = { 1.f, 0.f, 0.f, 1.f };

// Asset Explorer
const carb::Float4 kAssetExplorerFilterIconEnabledColor = { 126.f / 255.f, 187.f / 255.f, 199.f / 255.f, 1.f };
const carb::Float4 kAssetExplorerClearFilterColor = { 15.f / 255.f, 110.f / 255.f, 131.f / 255.f, 1.f };
const carb::Float4 kAssetExplorerAssetIconSelectedBgColorDark = { 0.2f, 0.2f, 0.2f, 0.6f };
const carb::Float4 kAssetExplorerAssetIconSelectedBgColorLight = { 0.84f, 0.84f, 0.84f, 1.0f };
const carb::Float4 kAssetExplorerAssetIconHoveredBgColorDark = { 0.2f, 0.2f, 0.2f, 0.8f };
const carb::Float4 kAssetExplorerAssetIconHoveredBgColorLight = { 0.749f, 0.8f, 0.812f, 1.0f };
const carb::Float4 kAssetExplorerPopulatedFolderColor = { 119.f / 255.f, 134 / 255.f, 137 / 255.f, 1.0f };
const carb::Float4 kAssetExplorerUnpopulatedFolderColor = { 0.39f, 0.39f, 0.39f, 1.0f };

// ECS Debug View
const carb::Float4 kEcsDebugViewSelectedComponentColor = { 1.f, 1.f, 0.f, 1.f };

// IEditor Window
const carb::Float4 kEditorWindowConnectionStateDisconnectedColor = { 1.f, 0.f, 0.f, 1.f };
const carb::Float4 kEditorWindowConnectionStateConnectedNoLiveColor = { 0.796f, 0.416f, 0.416f, 1.f };
const carb::Float4 kEditorWindowConnectionStateConnectedLiveColor = { 0.46f, 0.72f, 0.f, 1.f };

// Scene Hierarchy
const carb::Float4 kSceneHierarchySearchMatchedColor = { 1.f, 1.f, 1.f, 1.f };
const carb::Float4 kSceneHierarchySearchUnmatchedColor = { 0.5f, 0.5f, 0.5f, 1.f };

// Status Bar
const carb::Float4 kStatusBarProgressColor = { 79.f / 255.f, 125.f / 255.f, 160.f / 255.f, 1.f };

// Simple Tree View
const carb::Float4 kTreeViewColor = { 0.3f, 0.3f, 0.3f, 1.0f };

// Viewport
const carb::Float4 kViewportChildWindowBgColor = { 0.f, 0.f, 0.f, 0.f };

// Layers Window
const carb::Float4 kLayerWarningColor = { 1.0f, 111.0f / 255.0f, 114.0f / 255.0f, 1.0f };

// Message
using ColorMap = std::unordered_map<int32_t, carb::Float4>;

const carb::Float4 kMessageTextColorLightDefault = { 0.30980f, 0.49020f, 0.62745f, 1.f };
const ColorMap kMessageTextColorLight = {
    // Other levels use default color
    { carb::logging::kLevelVerbose, carb::Float4{ 0.49020f, 0.49020f, 0.49020f, 1.f } },
    { carb::logging::kLevelWarn, carb::Float4{ 0.89020f, 0.54118f, 0.14118f, 1.f } },
    { carb::logging::kLevelError, carb::Float4{ 0.57255f, 0.25882f, 0.22745f, 1.f } },
    { carb::logging::kLevelFatal, carb::Float4{ 0.57255f, 0.25882f, 0.22745f, 1.f } }
};

const carb::Float4 kMessageTextColorDarkDefault = { 0.47451f, 0.72941f, 0.92157f, 1.f };
const ColorMap kMessageTextColorDark = {
    // Other levels use default color
    { carb::logging::kLevelVerbose, carb::Float4{ 0.72941f, 0.72941f, 0.72941f, 1.f } },
    { carb::logging::kLevelWarn, carb::Float4{ 0.87451f, 0.79608f, 0.29020f, 1.f } },
    { carb::logging::kLevelError, carb::Float4{ 0.96471f, 0.69412f, 0.66667f, 1.f } },
    { carb::logging::kLevelFatal, carb::Float4{ 0.96471f, 0.69412f, 0.66667f, 1.f } }
};

const carb::Float4 kMessageIconColorLightDefault = { 0.30980f, 0.49020f, 0.62745f, 1.f };
const ColorMap kMessageIconColorLight = {
    // Other levels use default color
    { carb::logging::kLevelVerbose, carb::Float4{ 0.49020f, 0.49020f, 0.49020f, 1.f } },
    { carb::logging::kLevelWarn, carb::Float4{ 0.89020f, 0.54118f, 0.14118f, 1.f } },
    { carb::logging::kLevelError, carb::Float4{ 0.973f, 0.541f, 0.49f, 1.f } },
    { carb::logging::kLevelFatal, carb::Float4{ 0.973f, 0.541f, 0.49f, 1.f } }
};

const carb::Float4 kMessageIconColorDarkDefault = { 0.47451f, 0.72941f, 0.92157f, 1.f };
const ColorMap kMessageIconColorDark = {
    // Other levels use default color
    { carb::logging::kLevelVerbose, carb::Float4{ 0.72941f, 0.72941f, 0.72941f, 1.f } },
    { carb::logging::kLevelWarn, carb::Float4{ 0.87451f, 0.79608f, 0.29020f, 1.f } },
    { carb::logging::kLevelError, carb::Float4{ 0.973f, 0.541f, 0.49f, 1.f } },
    { carb::logging::kLevelFatal, carb::Float4{ 0.973f, 0.541f, 0.49f, 1.f } }
};

inline carb::Float4 selectColor(bool darkUi,
                                int32_t level,
                                const ColorMap& darkMap,
                                const ColorMap& lightMap,
                                const carb::Float4& darkDefault,
                                const carb::Float4& lightDefault)
{
    const ColorMap& colorMap = darkUi ? darkMap : lightMap;
    carb::Float4 color = darkUi ? darkDefault : lightDefault;

    auto colorEntry = colorMap.find(level);
    if (colorEntry != colorMap.end())
    {
        color = colorEntry->second;
    }

    return color;
}
}
}
}
