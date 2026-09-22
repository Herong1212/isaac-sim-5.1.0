// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#if defined _WIN32
#    ifdef OMNI_USD_EXPORTS
#        define OMNI_USD_API __declspec(dllexport)
#    else
#        define OMNI_USD_API __declspec(dllimport)
#    endif
#else
#    ifdef OMNI_USD_EXPORTS
#        define OMNI_USD_API __attribute__((visibility("default")))
#    else
#        define OMNI_USD_API
#    endif
#endif
