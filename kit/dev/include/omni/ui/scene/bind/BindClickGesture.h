// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindShapeGesture.h"
#include "DocClickGesture.h"

#include <omni/ui/scene/ClickGesture.h>

OMNIUI_PROTECT_PYBIND11_OBJECT(OMNIUI_SCENE_NS::ClickGesture, ClickGesture);

// clang-format off

#define OMNIUI_PYBIND_INIT_PyClickGesture                                                                              \
    OMNIUI_PYBIND_INIT_CAST(mouse_button, setMouseButton, uint32_t)                                                    \
    OMNIUI_PYBIND_INIT_CAST(modifiers, setModifiers, uint32_t)                                                         \
    OMNIUI_PYBIND_INIT_CALLBACK(on_ended_fn, setOnEndedFn, void(AbstractShape const*))                                 \
    OMNIUI_PYBIND_INIT_ShapeGesture

#define OMNIUI_PYBIND_KWARGS_DOC_ClickGesture                                                                          \
    "\n    `mouse_button : `\n        "                                                                                \
    OMNIUI_PYBIND_DOC_ClickGesture_mouseButton                                                                         \
    "\n    `modifiers : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_ClickGesture_modifiers                                                                           \
    "\n    `on_ended_fn : `\n        "                                                                                 \
    OMNIUI_PYBIND_DOC_ClickGesture_OnEnded                                                                             \
    OMNIUI_PYBIND_KWARGS_DOC_ShapeGesture

// clang-format on
