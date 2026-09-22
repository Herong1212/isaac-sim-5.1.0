// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "IWindowCallbackManager.h"

#include <carb/IObject.h>
#include <carb/ObjectUtils.h>
#include <carb/InterfaceUtils.h>

#include <functional>

namespace omni
{
namespace ui
{
namespace windowmanager
{

class LambdaEventListener : public IEventListener
{
public:
    LambdaEventListener(const std::function<void(float)>& fn) : m_fn(fn)
    {
    }

    void onDraw(float elapsedTime) override
    {
        if (m_fn)
            m_fn(elapsedTime);
    }

private:
    std::function<void(float)> m_fn;

    CARB_IOBJECT_IMPL
};

inline IWindowCallbackPtr createWindowCallback(IWindowCallbackManager* windowCallbackManager,
                                               const char* title,
                                               uint32_t width,
                                               uint32_t height,
                                               DockPreference dockPreference,
                                               const std::function<void(float)>& onDrawFn)
{
    return windowCallbackManager->createWindowCallback(
        title, width, height, dockPreference, carb::stealObject(new LambdaEventListener(onDrawFn)).get());
}

inline IWindowCallbackPtr createWindowSetCallback(WindowSet* windowSet,
                                                  IWindowCallbackManager* windowCallbackManager,
                                                  const char* title,
                                                  uint32_t width,
                                                  uint32_t height,
                                                  DockPreference dockPreference,
                                                  const std::function<void(float)>& onDrawFn)
{
    return windowCallbackManager->createWindowSetCallback(
        windowSet, title, width, height, dockPreference, carb::stealObject(new LambdaEventListener(onDrawFn)).get());
}

inline IWindowCallbackPtr createAppWindowCallback(omni::kit::IAppWindow* appWindow,
                                                  IWindowCallbackManager* windowCallbackManager,
                                                  const char* title,
                                                  uint32_t width,
                                                  uint32_t height,
                                                  DockPreference dockPreference,
                                                  const std::function<void(float)>& onDrawFn)
{
    return windowCallbackManager->createAppWindowCallback(
        appWindow, title, width, height, dockPreference, carb::stealObject(new LambdaEventListener(onDrawFn)).get());
}

inline bool removeWindowCallbackFromDefaultManager(IWindowCallback* windowCallback)
{
    IWindowCallbackManager* uiWindowManager = carb::getCachedInterface<IWindowCallbackManager>();
    if (windowCallback && uiWindowManager)
    {
        uiWindowManager->removeWindowCallback(windowCallback);
        return true;
    }
    return false;
}

}
}
}
