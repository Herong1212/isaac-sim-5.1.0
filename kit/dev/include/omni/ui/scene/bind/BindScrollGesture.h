// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindShapeGesture.h"
#include "DocScrollGesture.h"

#include <omni/ui/scene/ScrollGesture.h>

OMNIUI_PROTECT_PYBIND11_OBJECT(OMNIUI_SCENE_NS::ScrollGesture, ScrollGesture);

// clang-format off

#define OMNIUI_PYBIND_INIT_PyScrollGesture                                                                             \
    OMNIUI_PYBIND_INIT_CAST(mouse_button, setMouseButton, uint32_t)                                                    \
    OMNIUI_PYBIND_INIT_CAST(modifiers, setModifiers, uint32_t)                                                         \
    OMNIUI_PYBIND_INIT_CALLBACK(on_ended_fn, setOnEndedFn, void(AbstractShape const*))                                 \
    OMNIUI_PYBIND_INIT_ShapeGesture

#define OMNIUI_PYBIND_KWARGS_DOC_ScrollGesture                                                                         \
    "\n    `mouse_button : `\n        "                                                                                \
    OMNIUI_PYBIND_DOC_ScrollGesture_mouseButton                                                                        \
    "\n    `modifiers : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_ScrollGesture_modifiers                                                                          \
    "\n    `on_ended_fn : `\n        "                                                                                 \
    OMNIUI_PYBIND_DOC_ScrollGesture_OnEnded                                                                            \
    OMNIUI_PYBIND_KWARGS_DOC_ShapeGesture

// clang-format on
