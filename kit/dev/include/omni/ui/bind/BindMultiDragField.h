// Copyright (c) 2020-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindMultiField.h"
#include "DocMultiDragField.h"
#include "DocMultiFloatDragField.h"
#include "DocMultiIntDragField.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_MultiFloatDragField                                                                         \
    OMNIUI_PYBIND_INIT_AbstractMultiField                                                                              \
    OMNIUI_PYBIND_INIT_CAST(min, setMin, double)                                                                       \
    OMNIUI_PYBIND_INIT_CAST(max, setMax, double)                                                                       \
    OMNIUI_PYBIND_INIT_CAST(step, setStep, float)

#define OMNIUI_PYBIND_INIT_MultiIntDragField                                                                           \
    OMNIUI_PYBIND_INIT_AbstractMultiField                                                                              \
    OMNIUI_PYBIND_INIT_CAST(min, setMin, int32_t)                                                                      \
    OMNIUI_PYBIND_INIT_CAST(max, setMax, int32_t)                                                                      \
    OMNIUI_PYBIND_INIT_CAST(step, setStep, float)

#define OMNIUI_PYBIND_KWARGS_DOC_MultiDragField                                                                        \
    "\n    `min : `\n        "                                                                                         \
    OMNIUI_PYBIND_DOC_MultiDragField_min                                                                               \
    "\n    `max : `\n        "                                                                                         \
    OMNIUI_PYBIND_DOC_MultiDragField_max                                                                               \
    "\n    `step : `\n        "                                                                                        \
    OMNIUI_PYBIND_DOC_MultiDragField_step                                                                              \
    OMNIUI_PYBIND_KWARGS_DOC_AbstractMultiField

#define OMNIUI_PYBIND_KWARGS_DOC_MultiFloatDragField                                                                   \
    OMNIUI_PYBIND_KWARGS_DOC_MultiDragField

#define OMNIUI_PYBIND_KWARGS_DOC_MultiIntDragField                                                                     \
    OMNIUI_PYBIND_KWARGS_DOC_MultiDragField
// clang-format on
