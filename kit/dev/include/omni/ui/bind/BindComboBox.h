// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindUtils.h"
#include "BindWidget.h"
#include "DocComboBox.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_ComboBox                                                                                    \
    OMNIUI_PYBIND_INIT_Widget                                                                                          \
    OMNIUI_PYBIND_INIT_CAST(arrow_only, setArrowOnly, bool)
#define OMNIUI_PYBIND_KWARGS_DOC_ComboBox                                                                              \
    "\n    `arrow_only : bool`\n        "                                                                              \
    OMNIUI_PYBIND_DOC_ComboBox_arrowOnly                                                                               \
    OMNIUI_PYBIND_KWARGS_DOC_Widget
// clang-format on
