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
#include "DocCurve.h"

// clang-format off

#define OMNIUI_PYBIND_INIT_Curve                                                                                       \
    OMNIUI_PYBIND_INIT_AbstractShape                                                                                   \
    OMNIUI_PYBIND_INIT_CALL(positions, setPositions, pythonListToVector3)                                              \
    OMNIUI_PYBIND_INIT_CALL(colors, setColors, pythonListToVector4)                                                    \
    OMNIUI_PYBIND_INIT_CAST(thicknesses, setThicknesses, std::vector<float>)                                           \
    OMNIUI_PYBIND_INIT_CAST(intersection_thickness, setIntersectionThickness, float)                                   \
    OMNIUI_PYBIND_INIT_CAST(curve_type, setCurveType, Curve::CurveType)                                                \
    OMNIUI_PYBIND_INIT_CAST(tessellation, setTessellation, uint16_t)

#define OMNIUI_PYBIND_KWARGS_DOC_Curve                                                                                 \
    "\n    `positions : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Curve_positions                                                                                  \
    "\n    `colors : `\n        "                                                                                      \
    OMNIUI_PYBIND_DOC_Curve_colors                                                                                     \
    "\n    `thicknesses : `\n        "                                                                                 \
    OMNIUI_PYBIND_DOC_Curve_thicknesses                                                                                \
    "\n    `intersection_thickness : `\n        "                                                                      \
    OMNIUI_PYBIND_DOC_Curve_intersectionThickness                                                                      \
    "\n    `curve_type : `\n        "                                                                                  \
    OMNIUI_PYBIND_DOC_Curve_curveType                                                                                  \
    "\n    `tessellation : `\n        "                                                                                \
    OMNIUI_PYBIND_DOC_Curve_tessellation                                                                               \
    OMNIUI_PYBIND_KWARGS_DOC_AbstractShape

// clang-format on
