// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_ColorWidget                                                                                                    \
    "The ColorWidget widget is a button that displays the color from the item model and can open a picker window to change the color.\n" \
    "\n"


#define OMNIUI_PYBIND_DOC_ColorWidget_setComputedContentWidth                                                          \
    "Reimplemented the method to indicate the width hint that represents the preferred size of the widget. Currently this widget can't be smaller than the size of the ColorWidget square.\n"


#define OMNIUI_PYBIND_DOC_ColorWidget_setComputedContentHeight                                                         \
    "Reimplemented the method to indicate the height hint that represents the preferred size of the widget. Currently this widget can't be smaller than the size of the ColorWidget square.\n"


#define OMNIUI_PYBIND_DOC_ColorWidget_onModelUpdated                                                                   \
    "Reimplemented the method from ItemModelHelper that is called when the model is changed.\n"                        \
    "\n"                                                                                                               \
    "\n"                                                                                                               \
    "### Arguments:\n"                                                                                                 \
    "\n"                                                                                                               \
    "    `item :`\n"                                                                                                   \
    "        The item in the model that is changed. If it's NULL, the root is chaged.\n"


#define OMNIUI_PYBIND_DOC_ColorWidget_ColorWidget "Construct ColorWidget.\n"
