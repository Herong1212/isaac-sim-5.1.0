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
#include "DocFraction.h"
#include "DocLength.h"
#include "DocPercent.h"
#include "DocPixel.h"

#define OMNIUI_PYBIND_INIT_Length
#define OMNIUI_PYBIND_KWARGS_DOC_Length

#define OMNIUI_PYBIND_INIT_Percent OMNIUI_PYBIND_INIT_Length
#define OMNIUI_PYBIND_KWARGS_DOC_Percent OMNIUI_PYBIND_KWARGS_DOC_Length

#define OMNIUI_PYBIND_INIT_Pixel OMNIUI_PYBIND_INIT_Length
#define OMNIUI_PYBIND_KWARGS_DOC_Pixel OMNIUI_PYBIND_KWARGS_DOC_Length

#define OMNIUI_PYBIND_INIT_Fraction OMNIUI_PYBIND_INIT_Length
#define OMNIUI_PYBIND_KWARGS_DOC_Fraction OMNIUI_PYBIND_KWARGS_DOC_Length
