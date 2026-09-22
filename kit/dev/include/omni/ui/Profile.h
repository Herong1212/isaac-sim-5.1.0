// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/profiler/Profile.h>

// Enable top-level Window zones by default.
#define OMNIUI_PROFILE_ENABLE

// Extra zones for recursive Widget layout and drawing functions, causes performance slowdown so disabled by default.
// Recommend using the profiler maxZoneDepth option if enabled.
// #define OMNIUI_PROFILE_VERBOSE

#ifdef OMNIUI_PROFILE_ENABLE
#    define OMNIUI_PROFILE_ZONE(zoneName, ...) CARB_PROFILE_ZONE(1, zoneName, ##__VA_ARGS__)
#    define OMNIUI_PROFILE_FUNCTION CARB_PROFILE_FUNCTION(1)
#    define OMNIUI_PROFILE_WIDGET_FUNCTION                                                                             \
        CARB_PROFILE_ZONE(1, "[%s] %s '%s'", this->getTypeName().c_str(), CARB_PRETTY_FUNCTION, this->getName().c_str())
#else
#    define OMNIUI_PROFILE_ZONE(...)
#    define OMNIUI_PROFILE_FUNCTION
#    define OMNIUI_PROFILE_WIDGET_FUNCTION
#endif

#ifdef OMNIUI_PROFILE_VERBOSE
#    define OMNIUI_PROFILE_VERBOSE_ZONE OMNIUI_PROFILE_ZONE
#    define OMNIUI_PROFILE_VERBOSE_FUNCTION OMNIUI_PROFILE_FUNCTION
#    define OMNIUI_PROFILE_VERBOSE_WIDGET_FUNCTION OMNIUI_PROFILE_WIDGET_FUNCTION
#else
#    define OMNIUI_PROFILE_VERBOSE_ZONE(...)
#    define OMNIUI_PROFILE_VERBOSE_FUNCTION
#    define OMNIUI_PROFILE_VERBOSE_WIDGET_FUNCTION
#endif
