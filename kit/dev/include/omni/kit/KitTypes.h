// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/datasource/IDataSource.h>

namespace carb
{
struct Float4;
namespace input
{
struct Keyboard;
struct Mouse;
}
namespace imgui
{
struct ImGui;
}
}

namespace omni
{
namespace kit
{

typedef uint64_t SubscriptionId;

constexpr size_t kBackBufferCount = 3; ///< Maximum number of frames to queue up.

struct Prompt;
struct Window;
struct ContentWindowWidget;
struct ContentWindowToolButton;

typedef void (*OnUpdateEventFn)(float elapsedTime, void* userData);
typedef void (*OnConnectionEventFn)(const carb::datasource::ConnectionEventType& eventType, void* userData);
typedef void (*OnWindowDrawFn)(const char* windowName, float elapsedTime, void* userData);
typedef void (*OnWindowStateChangeFn)(const char* name, bool open, void* userData);
typedef void (*OnExtensionsChangeFn)(void* userData);
typedef void (*OnShutdownEventFn)(void* userData);

typedef void (*OnLogEventFn)(
    const char* source, int32_t level, const char* filename, int lineNumber, const char* message, void* userData);
typedef void (*OnUIDrawEventFn)(carb::imgui::ImGui*,
                                const double* viewMatrix,
                                const double* projMatrix,
                                const carb::Float4& viewPortRect,
                                void* userData);

struct ExtensionInfo
{
    const char* id;
    bool enabled;
    const char* name;
    const char* description;
    const char* path;
};

struct ExtensionFolderInfo
{
    const char* path;
    bool builtin;
};

enum class GraphicsMode
{
    eVulkan,
    eDirect3D12
};

enum class RendererMode
{
    eRtx, ///< NVIDIA RTX renderer, a fully ray traced renderer.
    eNvf ///< NVIDIA NVF renderer. reserved for internal use.
};

struct EnumClassHash
{
    template <typename T>
    std::size_t operator()(T t) const
    {
        return static_cast<std::size_t>(t);
    }
};
}
}
