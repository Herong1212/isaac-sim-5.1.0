// Copyright (c) 2020-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_ManipulatorModelHelper                                                                       \
    "The ManipulatorModelHelper class provides the basic model functionality.\n"


#define OMNIUI_PYBIND_DOC_ManipulatorModelHelper_onModelUpdated                                                        \
    "Called by the model when the model value is changed. The class should react to the changes.\n"                    \
    "\n"                                                                                                               \
    "\n"                                                                                                               \
    "### Arguments:\n"                                                                                                 \
    "\n"                                                                                                               \
    "    `item :`\n"                                                                                                   \
    "        The item in the model that is changed. If it's NULL, the root is changed.\n"


#define OMNIUI_PYBIND_DOC_ManipulatorModelHelper_getRayFromNdc "Convert NDC 2D [-1..1] coordinates to 3D ray.\n"


#define OMNIUI_PYBIND_DOC_ManipulatorModelHelper_setModel "Set the current model.\n"


#define OMNIUI_PYBIND_DOC_ManipulatorModelHelper_getModel "Returns the current model.\n"
