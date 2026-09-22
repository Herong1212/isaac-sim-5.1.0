// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_AbstractContainer                                                                            \
    "Base class for all the items that have children.\n"                                                               \
    "\n"


#define OMNIUI_PYBIND_DOC_AbstractContainer_transformSpace                                                             \
    "Transform the given point from the coordinate system fromspace to the coordinate system tospace.\n"


#define OMNIUI_PYBIND_DOC_AbstractContainer_transformSpace01                                                           \
    "Transform the given vector from the coordinate system fromspace to the coordinate system tospace.\n"


#define OMNIUI_PYBIND_DOC_AbstractContainer_addChild                                                                   \
    "Adds item to this container in a manner specific to the container. If it's allowed to have one sub-widget only, it will be overwriten.\n"


#define OMNIUI_PYBIND_DOC_AbstractContainer_clear "Removes the container items from the container.\n"
