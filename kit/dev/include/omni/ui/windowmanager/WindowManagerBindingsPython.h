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

#include <carb/BindingsPythonUtils.h>

#include <functional>

DISABLE_PYBIND11_DYNAMIC_CAST(omni::ui::windowmanager::IWindowCallback)
DISABLE_PYBIND11_DYNAMIC_CAST(omni::ui::windowmanager::IWindowCallbackManager)

namespace omni
{

namespace kit
{
class IAppWindow
{
};
}

namespace ui
{
namespace windowmanager
{

struct WindowSet
{
};

class PythonEventListener : public IEventListener
{
public:
    PythonEventListener(const std::function<void(float)>& fn) : m_fn(fn)
    {
    }

    void onDraw(float dt) override
    {
        carb::callPythonCodeSafe(m_fn, dt);
    }

private:
    std::function<void(float)> m_fn;

    CARB_IOBJECT_IMPL
};


inline void definePythonModule(py::module& m)
{
    m.doc() = "pybind11 omni.ui.windowmanager bindings";

    py::class_<WindowSet>(m, "WindowSet");


    py::class_<IWindowCallback, IWindowCallbackPtr>(m, "IWindowCallback", R"(
        IWindowCallback object.
        )")
        .def("get_title", &IWindowCallback::getTitle)
        .def("get_width", &IWindowCallback::getWidth)
        .def("get_height", &IWindowCallback::getHeight)
        .def("get_dock_preference", &IWindowCallback::getDockPreference)
        .def("get_window_set", &IWindowCallback::getWindowSet, py::return_value_policy::reference)
        .def("get_app_window", &IWindowCallback::getAppWindow, py::return_value_policy::reference)
        .def("draw", &IWindowCallback::draw)
        /**/;

    m.def("acquire_window_callback_manager_interface",
          []() { return carb::getCachedInterface<omni::ui::windowmanager::IWindowCallbackManager>(); },
          py::return_value_policy::reference)
        /**/;

    py::class_<IWindowCallbackManager>(m, "IWindowCallbackManager")
        .def("create_window_callback",
             [](IWindowCallbackManager* self, const char* title, uint32_t width, uint32_t height,
                DockPreference dockPreference, const std::function<void(float)>& onDrawFn) {
                 return self->createWindowCallback(
                     title, width, height, dockPreference, carb::stealObject(new PythonEventListener(onDrawFn)).get());
             },
             py::return_value_policy::reference)
        .def("remove_window_callback", &IWindowCallbackManager::removeWindowCallback)
        .def("get_window_callback_count", &IWindowCallbackManager::getWindowCallbackCount)
        .def("get_window_callback_at", &IWindowCallbackManager::getWindowCallbackAt, py::return_value_policy::reference)

        .def("create_window_set", &IWindowCallbackManager::createWindowSet, py::return_value_policy::reference)
        .def("destroy_window_set", &IWindowCallbackManager::destroyWindowSet)
        .def("get_default_window_set", &IWindowCallbackManager::getDefaultWindowSet)
        .def("attach_window_set_to_app_window", &IWindowCallbackManager::attachWindowSetToAppWindow)
        .def("get_window_set_by_app_window", &IWindowCallbackManager::getWindowSetByAppWindow,
             py::return_value_policy::reference)
        .def("get_app_window_from_window_set", &IWindowCallbackManager::getAppWindowFromWindowSet,
             py::return_value_policy::reference)

        .def("get_window_set_count", &IWindowCallbackManager::getWindowSetCount)
        .def("get_window_set_at", &IWindowCallbackManager::getWindowSetAt, py::return_value_policy::reference)

        .def("create_window_set_callback",
             [](IWindowCallbackManager* self, WindowSet* windowSet, const char* title, uint32_t width, uint32_t height,
                DockPreference dockPreference, const std::function<void(float)>& onDrawFn) {
                 return self->createWindowSetCallback(windowSet, title, width, height, dockPreference,
                                                      carb::stealObject(new PythonEventListener(onDrawFn)).get());
             },
             py::return_value_policy::reference)
        .def("create_app_window_callback",
             [](IWindowCallbackManager* self, omni::kit::IAppWindow* appWindow, const char* title, uint32_t width,
                uint32_t height, DockPreference dockPreference, const std::function<void(float)>& onDrawFn) {
                 return self->createAppWindowCallback(appWindow, title, width, height, dockPreference,
                                                      carb::stealObject(new PythonEventListener(onDrawFn)).get());
             },
             py::return_value_policy::reference)
        .def("add_window_set_callback", &IWindowCallbackManager::addWindowSetCallback)
        .def("remove_window_set_callback", &IWindowCallbackManager::removeWindowSetCallback)
        .def("remove_app_window_callback", &IWindowCallbackManager::removeAppWindowCallback)
        .def("move_callback_to_app_window", &IWindowCallbackManager::moveCallbackToAppWindow)
        .def("get_window_set_callback_count", &IWindowCallbackManager::getWindowSetCallbackCount)
        .def("get_window_set_callback_at", &IWindowCallbackManager::getWindowSetCallbackAt,
             py::return_value_policy::reference)
        /**/;
}

}
}
}
