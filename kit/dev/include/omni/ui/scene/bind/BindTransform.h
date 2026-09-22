// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "BindAbstractContainer.h"
#include "DocTransform.h"

// clang-format off

#define OMNIUI_PYBIND_INIT_Transform                                                                                   \
    OMNIUI_PYBIND_INIT_AbstractContainer                                                                               \
    OMNIUI_PYBIND_INIT_CALL(transform, setTransform, pythonToMatrix4)                                                  \
    OMNIUI_PYBIND_INIT_CAST(scale_to, setScaleTo, Space)                                                               \
    OMNIUI_PYBIND_INIT_CAST(look_at, setLookAt,  Transform::LookAt)                                                    \
    OMNIUI_PYBIND_INIT_CAST(basis, setBasis,  std::shared_ptr<TransformBasis>)

#define OMNIUI_PYBIND_KWARGS_DOC_Transform                                                                             \
    "\n    `transform : `\n        "                                                                                   \
    OMNIUI_PYBIND_DOC_Transform_transform                                                                              \
    "\n    `scale_to : `\n        "                                                                                    \
    OMNIUI_PYBIND_DOC_Transform_scaleTo                                                                                \
    "\n    `look_at : `\n        "                                                                                     \
    OMNIUI_PYBIND_DOC_Transform_lookAt                                                                                 \
    "\n    `basis : `\n        "                                                                                       \
    OMNIUI_PYBIND_DOC_Transform_basis                                                                                  \
    OMNIUI_PYBIND_KWARGS_DOC_AbstractContainer

// clang-format on
