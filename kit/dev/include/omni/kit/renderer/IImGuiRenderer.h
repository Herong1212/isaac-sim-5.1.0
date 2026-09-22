// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IRenderer.h"

#include <carb/Interface.h>

#include <omni/ui/windowmanager/IWindowCallbackManager.h>

namespace carb
{
namespace graphics
{
struct CommandList;
struct Descriptor;
struct DescriptorSet;
}
}

namespace rtx
{
namespace resourcemanager
{
class Context;
}
}

namespace carb
{
namespace graphics
{
struct Graphics;
struct Device;
struct ResourceBindingSignature;
}

namespace windowing
{
struct Cursor;
}
namespace imgui
{
struct Context;
}
}

namespace omni
{

namespace ui
{
namespace windowmanager
{
struct WindowSet;
}
}

namespace kit
{
namespace renderer
{

class DrawDataHandler;

class IImGuiRenderer
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::renderer::IImGuiRenderer", 1, 3);

    virtual void startup() = 0;
    virtual void shutdown() = 0;

    virtual uint32_t getResourceManagerDeviceMask() = 0;
    virtual carb::graphics::ResourceBindingSignature* getResourceBindingSignature() = 0;

    virtual TextureGpuReference allocateReferenceForTexture() = 0;
    virtual TextureGpuReference allocateReferenceForDrawable() = 0;

    virtual bool isPossibleToAttachAppWindow() = 0;
    virtual bool attachAppWindow(IAppWindow* appWindow) = 0;
    virtual bool attachAppWindowWithImGuiContext(IAppWindow* appWindow, carb::imgui::Context* imGuiContext) = 0;
    virtual void detachAppWindow(IAppWindow* appWindow) = 0;
    virtual bool isAppWindowAttached(IAppWindow* appWindow) = 0;
    virtual omni::ui::windowmanager::WindowSet* getWindowSet(IAppWindow* appWindow) = 0;

    virtual void setCursorShapeOverride(IAppWindow* appWindow, carb::windowing::CursorStandardShape cursor) = 0;
    virtual bool hasCursorShapeOverride(IAppWindow* appWindow) const = 0;
    virtual carb::windowing::CursorStandardShape getCursorShapeOverride(IAppWindow* appWindow) const = 0;
    virtual void clearCursorShapeOverride(IAppWindow* appWindow) = 0;

    virtual void deallocateReferenceForTexture(const TextureGpuReference& textureGpuReference) = 0;
    virtual void deallocateReferenceForDrawable(const TextureGpuReference& textureGpuReference) = 0;

    virtual DrawDataHandler* createDrawData() const = 0;
    virtual void destroyDrawData(DrawDataHandler* drawDataHandler) const = 0;
    virtual void fillDrawData(DrawDataHandler* drawDataHandler, void* data) const = 0;
    virtual void renderDrawData(IAppWindow* appWindow,
                                carb::graphics::CommandList* commandList,
                                const DrawDataHandler* drawDataHandler) const = 0;

    virtual void registerCursorShapeExtend(const char* shapeName, const char* imagePath) = 0;
    virtual void unregisterCursorShapeExtend(const char* shapeName) = 0;
    virtual void setCursorShapeOverrideExtend(IAppWindow* appWindow, const char* shapeName) = 0;
    virtual omni::string getCursorShapeOverrideExtend(IAppWindow* appWindow) const = 0;
    virtual void getAllCursorShapeNames(const char** names, size_t count) const = 0;
    virtual size_t getAllCursorShapeNamesCount() const = 0;
};

}
}
}
