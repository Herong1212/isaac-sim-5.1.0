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
 * @brief Used to specify how shadow is rendered
 */
enum ShadowFlag : uint8_t
{
    eNone = 0,
    eCutOutShapeBackground = 1 << 0   // Do not render the shadow shape under the objects to be shadowed to save on
                                      // fill-rate or facilitate blending. Slower on CPU.
};

OMNIUI_NAMESPACE_CLOSE_SCOPE
