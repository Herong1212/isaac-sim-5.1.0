// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindAbstractSlider.h"
#include "BindUtils.h"
#include "DocFloatSlider.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_FloatSlider                                                                                 \
    OMNIUI_PYBIND_INIT_AbstractSlider                                                                                  \
    OMNIUI_PYBIND_INIT_CAST(min, setMin, float)                                                                        \
    OMNIUI_PYBIND_INIT_CAST(max, setMax, float)                                                                        \
    OMNIUI_PYBIND_INIT_CAST(step, setStep, float)                                                                      \
    OMNIUI_PYBIND_INIT_CAST(format, setFormat, std::string)                                                            \
    OMNIUI_PYBIND_INIT_CAST(precision, setPrecision, uint32_t)
#define OMNIUI_PYBIND_KWARGS_DOC_FloatSlider                                                                           \
    "\n    `min : float`\n        "                                                                                    \
    OMNIUI_PYBIND_DOC_FloatSlider_min                                                                                  \
    "\n    `max : float`\n        "                                                                                    \
    OMNIUI_PYBIND_DOC_FloatSlider_max                                                                                  \
    "\n    `step : float`\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_FloatSlider_step                                                                                 \
    "\n    `format : str`\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_FloatSlider_format                                                                               \
    "\n    `precision : uint32_t`\n        "                                                                           \
    OMNIUI_PYBIND_DOC_FloatSlider_precision                                                                            \
    OMNIUI_PYBIND_KWARGS_DOC_AbstractSlider
// clang-format on
