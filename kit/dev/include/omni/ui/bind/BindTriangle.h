// Copyright (c) 2018-2021, NVIDIA CORPORATION. All rights reserved.
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
#include "DocTriangle.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_Triangle                                                                                    \
    OMNIUI_PYBIND_INIT_Shape                                                                                           \
    OMNIUI_PYBIND_INIT_CAST(alignment, setAlignment, Alignment)                                                        \

#define OMNIUI_PYBIND_KWARGS_DOC_Triangle                                                                              \
    "\n    `alignment : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Triangle_alignment                                                                               \
    OMNIUI_PYBIND_KWARGS_DOC_Shape
// clang-format on
