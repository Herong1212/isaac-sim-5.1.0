// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_RadioCollection                                                                              \
    "Radio Collection is a class that groups RadioButtons and coordinates their state.\n"                              \
    "It makes sure that the choice is mutually exclusive, it means when the user selects a radio button, any previously selected radio button in the same collection becomes deselected.\n"


#define OMNIUI_PYBIND_DOC_RadioCollection_onModelUpdated                                                               \
    "Called by the model when the model value is changed. The class should react to the changes.\n"                    \
    "Reimplemented from ValueModelHelper\n"


#define OMNIUI_PYBIND_DOC_RadioCollection_RadioCollection "Constructs RadioCollection.\n"
