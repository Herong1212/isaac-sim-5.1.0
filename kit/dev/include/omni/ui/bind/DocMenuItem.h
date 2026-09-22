// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_MenuItem                                                                                     \
    "A MenuItem represents the items the Menu consists of.\n"                                                          \
    "MenuItem can be inserted only once in the menu.\n"


#define OMNIUI_PYBIND_DOC_MenuItem_setComputedContentWidth                                                             \
    "Reimplemented the method to indicate the width hint that represents the preferred size of the widget.\n"


#define OMNIUI_PYBIND_DOC_MenuItem_setComputedContentHeight                                                            \
    "Reimplemented the method to indicate the height hint that represents the preferred size of the widget.\n"


#define OMNIUI_PYBIND_DOC_MenuItem_cascadeStyle                                                                        \
    "It's called when the style is changed. It should be propagated to children to make the style cached and available to children.\n"


#define OMNIUI_PYBIND_DOC_MenuItem_MenuItem "Construct MenuItem.\n"
