// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_CallbackHelper                                                                                                                                                                                                                                                                                                                        \
    "Base class for the objects that should automatically clean up the callbacks. It collects all the callbacks created with OMNIUI_CALLBACK and is able to clean all of them. We use it to destroy the callbacks if the parent object is destroyed, and it helps to break circular references created by pybind11 because pybind11 can't use weak pointers.\n" \
    "\n"
