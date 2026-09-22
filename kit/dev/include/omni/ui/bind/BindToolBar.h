// Copyright (c) 2018-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindUtils.h"
#include "BindWindow.h"
#include "DocToolBar.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_ToolBar                                                                                     \
    OMNIUI_PYBIND_INIT_Window                                                                                          \
    OMNIUI_PYBIND_INIT_CAST(axis, setAxis, ToolBar::Axis)                                                              \
    OMNIUI_PYBIND_INIT_CALLBACK(axis_changed_fn, setAxisChangedFn, void(ToolBar::Axis))

#define OMNIUI_PYBIND_KWARGS_DOC_ToolBar                                                                               \
    "\n    `axis : ui.Axis`\n        "                                                                                 \
    OMNIUI_PYBIND_DOC_ToolBar_axis                                                                                     \
    "\n    `axis_changed_fn : Callable[[ui.Axis], None]`\n        "                                                    \
    OMNIUI_PYBIND_DOC_ToolBar_axis                                                                                     \
    OMNIUI_PYBIND_KWARGS_DOC_Window
// clang-format on
