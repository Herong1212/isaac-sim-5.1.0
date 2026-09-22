// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// Define this macro so that other headers that are supposed to have this header included before them can check against
// it.
#define USD_CONTEXT_INCLUDES

// Include cstdio here so that vsnprintf is properly declared. This is necessary because pyerrors.h has
// #define vsnprintf _vsnprintf which later causes <cstdio> to declare std::_vsnprintf instead of the correct and proper
// std::vsnprintf. By doing it here before everything else, we avoid this nonsense.
#include <cstdio>

// Hide deprecated TBB warnings since they are emited from OpenUsd headers
#if !defined(TBB_SUPPRESS_DEPRECATED_MESSAGES)
  #define TBB_SUPPRESS_DEPRECATED_MESSAGES 1
#endif

// Python must be included first because it monkeys with macros that cause
// TBB to fail to compile in debug mode if TBB is included before Python
#include <boost/python/object.hpp>

// This suppresses deprecated header warnings, which is impossible with pragmas.
// Alternative is to specify -Wno-deprecated build option, but that disables other useful warnings too.
#ifdef __DEPRECATED
#    define OMNI_USD_SUPPRESS_DEPRECATION_WARNINGS
#    undef __DEPRECATED
#endif
#include <pxr/usd/usdGeom/bboxCache.h>
#include <pxr/usd/usdLux/cylinderLight.h>
#include <pxr/usd/usdLux/diskLight.h>
#include <pxr/usd/usdLux/distantLight.h>
#include <pxr/usd/usdLux/domeLight.h>
#include <pxr/usd/usdLux/rectLight.h>
#include <pxr/usd/usdLux/sphereLight.h>
#include <pxr/usd/usdShade/material.h>
#include <pxr/usd/usdShade/shader.h>
