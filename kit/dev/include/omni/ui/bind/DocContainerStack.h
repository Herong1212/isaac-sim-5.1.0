// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_ContainerStack                                                                                                               \
    "Singleton object that holds the stack of containers. We use it to automatically add widgets to the top container when the widgets are created.\n" \
    "\n"


#define OMNIUI_PYBIND_DOC_ContainerStack_push                                                                          \
    "Push the container to the top of the stack. All the newly created widgets will be added to this container.\n"


#define OMNIUI_PYBIND_DOC_ContainerStack_pop "Removes the container from the stack. The previous one will be active.\n"


#define OMNIUI_PYBIND_DOC_ContainerStack_addChildToTop "Add the given widget to the top container.\n"


#define OMNIUI_PYBIND_DOC_ContainerStack_instance "The only instance of the singleton.\n"
