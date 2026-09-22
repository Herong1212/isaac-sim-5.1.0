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
#include "DocPoints.h"

// clang-format off

#define OMNIUI_PYBIND_INIT_Points                                                                                      \
    OMNIUI_PYBIND_INIT_AbstractShape                                                                                   \
    OMNIUI_PYBIND_INIT_CALL(positions, setPositions, pythonListToVector3)                                              \
    OMNIUI_PYBIND_INIT_CALL(colors, setColors, pythonListToVector4)                                                    \
    OMNIUI_PYBIND_INIT_CAST(sizes, setSizes, std::vector<float>)                                                       \
    OMNIUI_PYBIND_INIT_CAST(intersection_sizes, setIntersectionSize, float)

#define OMNIUI_PYBIND_KWARGS_DOC_Points                                                                                \
    "\n    `positions : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Points_positions                                                                                 \
    "\n    `colors : `\n        "                                                                                      \
    OMNIUI_PYBIND_DOC_Points_colors                                                                                    \
    "\n    `sizes : `\n        "                                                                                       \
    OMNIUI_PYBIND_DOC_Points_sizes                                                                                     \
    "\n    `intersection_sizes : `\n        "                                                                          \
    OMNIUI_PYBIND_DOC_Points_intersectionSize                                                                          \
    OMNIUI_PYBIND_KWARGS_DOC_AbstractShape

// clang-format on
