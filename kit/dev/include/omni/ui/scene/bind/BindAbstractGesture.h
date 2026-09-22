// Copyright (c) 2019-2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "DocAbstractGesture.h"

#include <omni/ui/bind/BindUtils.h>

OMNIUI_PROTECT_PYBIND11_OBJECT(OMNIUI_SCENE_NS::AbstractGesture, AbstractGesture);

// clang-format off

#define OMNIUI_PYBIND_INIT_AbstractGesture                                                                             \
    OMNIUI_PYBIND_INIT_CAST(name, setName, std::string)                                                                \
    OMNIUI_PYBIND_INIT_CAST(manager, setManager, std::shared_ptr<GestureManager>)

#define OMNIUI_PYBIND_KWARGS_DOC_AbstractGesture                                                                       \
    "\n    `name : `\n        "                                                                                        \
    OMNIUI_PYBIND_DOC_AbstractGesture_name                                                                             \
    "\n    `manager : `\n        "                                                                                     \
    OMNIUI_PYBIND_DOC_AbstractGesture_getManager

// clang-format on
