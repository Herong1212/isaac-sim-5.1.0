// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"

#include <cstdint>

OMNIUI_NAMESPACE_OPEN_SCOPE

/**
 * @brief Used to set the rasterization behaviour.
 */
enum class RasterPolicy : uint8_t
{
    // Do not rasterize the widget at any time.
    eNever = 0,
    // Rasterize the widget as soon as possible and always use the
    // rasterized version. This means that the widget will only be updated
    // when the user called invalidateRaster.
    eOnDemand,
    // Automatically determine whether to rasterize the widget based on
    // performance considerations. If necessary, the widget will be
    // rasterized and updated when its content changes.
    eAuto
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
