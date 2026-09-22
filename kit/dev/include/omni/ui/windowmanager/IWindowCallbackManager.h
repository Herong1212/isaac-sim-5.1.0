// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Framework.h>
#include <carb/Interface.h>
#include <carb/logging/Log.h>
#include <carb/profiler/Profile.h>

namespace omni
{

namespace kit
{
class IAppWindow;
}

namespace ui
{
namespace windowmanager
{

enum class DockPreference : uint32_t
{
    eDisabled,
    eMain,
    eRight,
    eLeft,
    eRightTop,
    eRightBottom,
    eLeftBottom
};

/**
 * Interface to implement for event listener.
 */
class IEventListener : public carb::IObject
{
public:
    virtual void onDraw(float elapsedTime) = 0;
};

using IEventListenerPtr = carb::ObjectPtr<IEventListener>;

struct WindowSet;

class IWindowCallback : public carb::IObject
{
public:
    virtual const char* getTitle() = 0;
    virtual uint32_t getWidth() = 0;
    virtual uint32_t getHeight() = 0;
    virtual DockPreference getDockPreference() = 0;
    virtual WindowSet* getWindowSet() = 0;
    virtual omni::kit::IAppWindow* getAppWindow() = 0;

    virtual void draw(float elapsedTime) = 0;
};

using IWindowCallbackPtr = carb::ObjectPtr<IWindowCallback>;

class IWindowCallbackManager
{
public:
    CARB_PLUGIN_INTERFACE("omni::ui::windowmanager::IWindowCallbackManager", 0, 3)

    virtual IWindowCallback* createWindowCallbackPtr(
        const char* title, uint32_t width, uint32_t height, DockPreference dockPreference, IEventListener* listener) = 0;

    IWindowCallbackPtr createWindowCallback(
        const char* title, uint32_t width, uint32_t height, DockPreference dockPreference, IEventListener* listener)
    {
        return stealObject(this->createWindowCallbackPtr(title, width, height, dockPreference, listener));
    }

    virtual void removeWindowCallback(IWindowCallback* windowCallback) = 0;

    virtual size_t getWindowCallbackCount() = 0;
    virtual IWindowCallback* getWindowCallbackAt(size_t index) = 0;

    inline void drawWindows(float elapsedTime);
    inline IWindowCallback* findWindowCallbackByName(const char* name);


    virtual WindowSet* createWindowSet() = 0;
    virtual void destroyWindowSet(WindowSet* windowSet) = 0;
    virtual WindowSet* getDefaultWindowSet() = 0;

    virtual void attachWindowSetToAppWindow(WindowSet* windowSet, omni::kit::IAppWindow* appWindow) = 0;
    virtual WindowSet* getWindowSetByAppWindow(omni::kit::IAppWindow* appWindow) = 0;
    virtual omni::kit::IAppWindow* getAppWindowFromWindowSet(WindowSet* windowSet) = 0;

    virtual size_t getWindowSetCount() = 0;
    virtual WindowSet* getWindowSetAt(size_t index) = 0;

    virtual IWindowCallback* createWindowSetCallbackPtr(WindowSet* windowSet,
                                                        const char* title,
                                                        uint32_t width,
                                                        uint32_t height,
                                                        DockPreference dockPreference,
                                                        IEventListener* listener) = 0;

    IWindowCallbackPtr createWindowSetCallback(WindowSet* windowSet,
                                               const char* title,
                                               uint32_t width,
                                               uint32_t height,
                                               DockPreference dockPreference,
                                               IEventListener* listener)
    {
        return stealObject(this->createWindowSetCallbackPtr(windowSet, title, width, height, dockPreference, listener));
    }

    IWindowCallbackPtr createAppWindowCallback(omni::kit::IAppWindow* appWindow,
                                               const char* title,
                                               uint32_t width,
                                               uint32_t height,
                                               DockPreference dockPreference,
                                               IEventListener* listener)
    {
        WindowSet* windowSet = this->getWindowSetByAppWindow(appWindow);
        if (!windowSet)
        {
            CARB_LOG_WARN("createAppWindowCallback: No window set attached to supplied app window!");
            return IWindowCallbackPtr();
        }
        return stealObject(this->createWindowSetCallbackPtr(windowSet, title, width, height, dockPreference, listener));
    }

    virtual void addWindowSetCallback(WindowSet* windowSet, IWindowCallback* windowCallback) = 0;

    virtual void removeWindowSetCallback(WindowSet* windowSet, IWindowCallback* windowCallback) = 0;

    void removeAppWindowCallback(omni::kit::IAppWindow* appWindow, IWindowCallback* windowCallback)
    {
        WindowSet* windowSet = this->getWindowSetByAppWindow(appWindow);
        if (!windowSet)
        {
            CARB_LOG_WARN("removeAppWindowCallback: No window set attached to supplied app window!");
            return;
        }
        this->removeWindowSetCallback(windowSet, windowCallback);
    }

    void moveCallbackToAppWindow(IWindowCallback* windowCallback, omni::kit::IAppWindow* newAppWindow)
    {
        WindowSet* newWindowSet = this->getWindowSetByAppWindow(newAppWindow);
        if (!newWindowSet)
        {
            CARB_LOG_WARN("moveCallbackToAppWindow: No window set attached to supplied app window!");
            return;
        }
        WindowSet* oldWindowSet = windowCallback->getWindowSet();
        this->removeWindowSetCallback(oldWindowSet, windowCallback);
        this->addWindowSetCallback(newWindowSet, windowCallback);
    }

    virtual size_t getWindowSetCallbackCount(WindowSet* windowSet) = 0;
    virtual IWindowCallback* getWindowSetCallbackAt(WindowSet* windowSet, size_t index) = 0;

    inline void drawWindowSet(WindowSet* windowSet, float elapsedTime);
    inline IWindowCallback* findWindowSetCallbackByName(WindowSet* windowSet, const char* name);
};

inline void IWindowCallbackManager::drawWindows(float elapsedTime)
{
    WindowSet* windowSet = getDefaultWindowSet();
    drawWindowSet(windowSet, elapsedTime);
}

inline IWindowCallback* IWindowCallbackManager::findWindowCallbackByName(const char* name)
{
    WindowSet* windowSet = getDefaultWindowSet();
    return findWindowSetCallbackByName(windowSet, name);
}

inline void IWindowCallbackManager::drawWindowSet(WindowSet* windowSet, float elapsedTime)
{
    size_t windowCallbackCount = getWindowSetCallbackCount(windowSet);
    omni::ui::windowmanager::IWindowCallback* editorMenuCallback = nullptr;

    for (size_t idx = 0; idx < windowCallbackCount; ++idx)
    {
        omni::ui::windowmanager::IWindowCallback* windowCallback = getWindowSetCallbackAt(windowSet, idx);
        if (windowCallback)
        {
            if (!editorMenuCallback && strcmp(windowCallback->getTitle(), "[editor_menu_hookup]") == 0)
            {
                // HACK, draw [editor_menu_hookup] last so MainWindow menu goes before it
                editorMenuCallback = windowCallback;
                continue;
            }
            CARB_PROFILE_ZONE(1, "'%s' ext window[new]", windowCallback->getTitle());
            windowCallback->draw(elapsedTime);
        }
    }
    if (editorMenuCallback)
    {
        CARB_PROFILE_ZONE(1, "[editor_menu_hookup] ext window[new]", editorMenuCallback->getTitle());
        editorMenuCallback->draw(elapsedTime);
    }
}

inline IWindowCallback* IWindowCallbackManager::findWindowSetCallbackByName(WindowSet* windowSet, const char* name)
{
    size_t nameLen = strlen(name);
    size_t windowCallbackCount = getWindowSetCallbackCount(windowSet);
    for (size_t idx = 0; idx < windowCallbackCount; ++idx)
    {
        omni::ui::windowmanager::IWindowCallback* windowCallback = getWindowSetCallbackAt(windowSet, idx);
        if (windowCallback && (strncmp(windowCallback->getTitle(), name, nameLen) == 0))
        {
            return windowCallback;
        }
    }
    return nullptr;
}

} // windowmanager
} // ui
} // omni
