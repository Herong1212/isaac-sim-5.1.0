// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindMenuHelper.h"
#include "BindUtils.h"
#include "BindWidget.h"
#include "DocMenuItem.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_MenuItem                                                                                    \
    OMNIUI_PYBIND_INIT_MenuHelper                                                                                      \
    OMNIUI_PYBIND_INIT_Widget

#define OMNIUI_PYBIND_KWARGS_DOC_MenuItem                                                                              \
    OMNIUI_PYBIND_KWARGS_DOC_MenuHelper                                                                                \
    OMNIUI_PYBIND_KWARGS_DOC_Widget
// clang-format on
