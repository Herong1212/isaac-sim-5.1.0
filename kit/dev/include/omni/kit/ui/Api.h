// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#if defined _WIN32
#    ifdef OMNI_KIT_UI_EXPORTS
#        define OMNI_KIT_UI_API __declspec(dllexport)
#        define OMNI_KIT_UI_CLASS_API
#    else
#        define OMNI_KIT_UI_API __declspec(dllimport)
#        define OMNI_KIT_UI_CLASS_API
#    endif
#else
#    ifdef OMNI_KIT_UI_EXPORTS
#        define OMNI_KIT_UI_API __attribute__((visibility("default")))
#        define OMNI_KIT_UI_CLASS_API __attribute__((visibility("default")))
#    else
#        define OMNI_KIT_UI_API
#        define OMNI_KIT_UI_CLASS_API
#    endif
#endif
