// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindArrowHelper.h"
#include "BindShapeAnchorHelper.h"
#include "BindShape.h"
#include "BindUtils.h"
#include "DocLine.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_Line                                                                                        \
    OMNIUI_PYBIND_INIT_Shape                                                                                           \
    OMNIUI_PYBIND_INIT_ArrowHelper                                                                                     \
    OMNIUI_PYBIND_INIT_CAST(alignment, setAlignment, Alignment)                                                        \
    OMNIUI_PYBIND_INIT_ShapeAnchorHelper

#define OMNIUI_PYBIND_KWARGS_DOC_Line                                                                                  \
    "\n    `alignment : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Line_alignment                                                                                   \
    OMNIUI_PYBIND_KWARGS_DOC_Shape                                                                                     \
    OMNIUI_PYBIND_KWARGS_DOC_ShapeAnchorHelper
// clang-format on
