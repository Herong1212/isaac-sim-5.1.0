// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindClickGesture.h"
#include "DocDoubleClickGesture.h"

#include <omni/ui/scene/DoubleClickGesture.h>

OMNIUI_PROTECT_PYBIND11_OBJECT(OMNIUI_SCENE_NS::DoubleClickGesture, DoubleClickGesture);

// clang-format off

#define OMNIUI_PYBIND_INIT_PyDoubleClickGesture                                                                        \
    OMNIUI_PYBIND_INIT_PyClickGesture

#define OMNIUI_PYBIND_KWARGS_DOC_DoubleClickGesture                                                                    \
    OMNIUI_PYBIND_KWARGS_DOC_ClickGesture

#define OMNIUI_PYBIND_DOC_DoubleClickGesture_OnEnded OMNIUI_PYBIND_DOC_ClickGesture_OnEnded

// clang-format on
