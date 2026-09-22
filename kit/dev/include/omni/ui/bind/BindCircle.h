// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindShape.h"
#include "BindUtils.h"
#include "DocCircle.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_Circle                                                                                      \
    OMNIUI_PYBIND_INIT_Shape                                                                                           \
    OMNIUI_PYBIND_INIT_CAST(radius, setRadius, float)                                                                  \
    OMNIUI_PYBIND_INIT_CAST(alignment, setAlignment, Alignment)                                                        \
    OMNIUI_PYBIND_INIT_CAST(arc, setArc, Alignment)                                                                    \
    OMNIUI_PYBIND_INIT_CAST(size_policy, setSizePolicy, Circle::SizePolicy)

#define OMNIUI_PYBIND_KWARGS_DOC_Circle                                                                                \
    "\n    `alignment :`\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Circle_alignment                                                                                 \
    "\n    `radius :`\n        "                                                                                      \
    OMNIUI_PYBIND_DOC_Circle_radius                                                                                    \
    "\n    `arc :`\n        "                                                                                         \
    OMNIUI_PYBIND_DOC_Circle_arc                                                                                       \
    "\n    `size_policy :`\n        "                                                                                 \
    OMNIUI_PYBIND_DOC_Circle_sizePolicy                                                                                \
    OMNIUI_PYBIND_KWARGS_DOC_Shape
// clang-format on
