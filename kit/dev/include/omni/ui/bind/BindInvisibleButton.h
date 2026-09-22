// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindWidget.h"
#include "DocInvisibleButton.h"

#define OMNIUI_PYBIND_INIT_InvisibleButton                                                                             \
    OMNIUI_PYBIND_INIT_Widget OMNIUI_PYBIND_INIT_CALLBACK(clicked_fn, setClickedFn, void())
// clang-format off
#define OMNIUI_PYBIND_KWARGS_DOC_InvisibleButton                                                                       \
    "\n    `clicked_fn : Callable[[], None]`\n        "                                                                \
    OMNIUI_PYBIND_DOC_InvisibleButton_Clicked                                                                          \
    OMNIUI_PYBIND_KWARGS_DOC_Widget
// clang-format on
