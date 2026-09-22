// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#define OMNIUI_PYBIND_DOC_SceneContainerScopeBase                                                                                          \
    "Puts the given container to the top of the stack when this object is constructed. And removes this container when it's destructed.\n" \
    "\n"


#define OMNIUI_PYBIND_DOC_SceneContainerScopeBase_get "Returns the container it was created with.\n"


#define OMNIUI_PYBIND_DOC_SceneContainerScopeBase_isValid                                                              \
    "Checks if this object is valid. It's always valid untill it's invalidated. Once it's invalidated, there is no way to make it valid again.\n"


#define OMNIUI_PYBIND_DOC_SceneContainerScopeBase_invalidate "Makes this object invalid.\n"
