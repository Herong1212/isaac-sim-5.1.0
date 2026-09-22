// Copyright (c) 2018-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindFloatSlider.h"
#include "BindUtils.h"
#include "DocFloatDrag.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_FloatDrag                                                                                   \
        OMNIUI_PYBIND_INIT_FloatSlider
#define OMNIUI_PYBIND_KWARGS_DOC_FloatDrag                                                                             \
        OMNIUI_PYBIND_KWARGS_DOC_FloatSlider
// clang-format on
