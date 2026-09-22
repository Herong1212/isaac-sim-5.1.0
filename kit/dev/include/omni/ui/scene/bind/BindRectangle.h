// Copyright (c) 2020-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindAbstractShape.h"
#include "DocRectangle.h"

// clang-format off

#define OMNIUI_PYBIND_INIT_Rectangle                                                                                   \
    OMNIUI_PYBIND_INIT_AbstractShape                                                                                   \
    OMNIUI_PYBIND_INIT_CAST(width, setWidth, Float)                                                                    \
    OMNIUI_PYBIND_INIT_CAST(height, setHeight, Float)                                                                  \
    OMNIUI_PYBIND_INIT_CAST(thickness, setThickness, float)                                                            \
    OMNIUI_PYBIND_INIT_CAST(intersection_thickness, setIntersectionThickness, float)                                   \
    OMNIUI_PYBIND_INIT_CALL(color, setColor, pythonToColor4)                                                           \
    OMNIUI_PYBIND_INIT_CAST(axis, setAxis, uint8_t)                                                                    \
    OMNIUI_PYBIND_INIT_CAST(wireframe, setWireframe, bool)

#define OMNIUI_PYBIND_KWARGS_DOC_Rectangle                                                                             \
    "\n    `width : `\n        "                                                                                       \
    OMNIUI_PYBIND_DOC_Rectangle_width                                                                                  \
    "\n    `height : `\n        "                                                                                      \
    OMNIUI_PYBIND_DOC_Rectangle_height                                                                                 \
    "\n    `thickness : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Rectangle_thickness                                                                              \
    "\n    `intersection_thickness : `\n        "                                                                      \
    OMNIUI_PYBIND_DOC_Rectangle_intersectionThickness                                                                  \
    "\n    `color : `\n        "                                                                                       \
    OMNIUI_PYBIND_DOC_Rectangle_color                                                                                  \
    "\n    `axis : `\n        "                                                                                        \
    OMNIUI_PYBIND_DOC_Rectangle_axis                                                                                   \
    "\n    `wireframe : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Rectangle_wireframe                                                                              \
    OMNIUI_PYBIND_KWARGS_DOC_AbstractShape

// clang-format on
