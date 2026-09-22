// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindContainer.h"
#include "BindUtils.h"
#include "DocStack.h"

// clang-format off
#define OMNIUI_PYBIND_INIT_Stack                                                                                       \
    OMNIUI_PYBIND_INIT_Container                                                                                       \
    OMNIUI_PYBIND_INIT_CAST(direction, setDirection, Stack::Direction)                                                 \
    OMNIUI_PYBIND_INIT_CAST(content_clipping, setContentClipping, bool)                                                \
    OMNIUI_PYBIND_INIT_CAST(spacing, setSpacing, float)                                                                \
    OMNIUI_PYBIND_INIT_CAST(send_mouse_events_to_back, setSendMouseEventsToBack, bool)

#define OMNIUI_PYBIND_KWARGS_DOC_Stack                                                                                 \
    "\n    `direction : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Stack_Direction                                                                                  \
    "\n    `content_clipping : `\n        "                                                                            \
    OMNIUI_PYBIND_DOC_Stack_contentClipping                                                                            \
    "\n    `spacing : `\n        "                                                                                     \
    OMNIUI_PYBIND_DOC_Stack_spacing                                                                                    \
    "\n    `send_mouse_events_to_back : `\n        "                                                                   \
    OMNIUI_PYBIND_DOC_Stack_sendMouseEventsToBack                                                                      \
    OMNIUI_PYBIND_KWARGS_DOC_Container
// clang-format on
