// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_AbstractItemDelegate                                                                         \
    "AbstractItemDelegate is used to generate widgets that display and edit data items from a model.\n"                \
    "\n"


#define OMNIUI_PYBIND_DOC_AbstractItemDelegate_buildBranch                                                             \
    "This pure abstract method must be reimplemented to generate custom collapse/expand button.\n"


#define OMNIUI_PYBIND_DOC_AbstractItemDelegate_buildWidget                                                             \
    "This pure abstract method must be reimplemented to generate custom widgets for specific item in the model.\n"


#define OMNIUI_PYBIND_DOC_AbstractItemDelegate_buildHeader                                                             \
    "This pure abstract method must be reimplemented to generate custom widgets for the header table.\n"


#define OMNIUI_PYBIND_DOC_AbstractItemDelegate_AbstractItemDelegate "Constructs AbstractItemDelegate.\n"
