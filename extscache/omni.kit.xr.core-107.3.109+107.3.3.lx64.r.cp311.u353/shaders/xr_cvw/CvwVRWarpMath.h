// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#ifdef __cplusplus

#    pragma once

#    include "CameraViewWarp.h"
#    include "VRPiecewiseQuadraticWarp.h"
#endif

#ifdef __cplusplus
#    include <cmath>

static inline float clamp(float x, float minVal, float maxVal)
{
    return x < minVal ? minVal : x > maxVal ? maxVal : x;
}
#endif

float cvw_piecewiseQuadraticWarpForFoveation(float x, VRShaderPiecewiseQuadraticWarpDesc desc)
{
    if (x < desc.switchLeft)
    {
        return desc.al * x * x + desc.bl * x + desc.cl;
    }
    else if (x > desc.switchRight)
    {
        return desc.ar * x * x + desc.br * x + desc.cr;
    }
    else
    {
        return desc.am * x + desc.bm;
    }
}

float cvw_piecewiseQuadraticWarpDerivativeForFoveation(float x, VRShaderPiecewiseQuadraticWarpDesc desc)
{
    if (x < desc.switchLeft)
    {
        return 2 * desc.al * x + desc.bl;
    }
    else if (x > desc.switchRight)
    {
        return 2 * desc.ar * x + desc.br;
    }
    else
    {
        return desc.am;
    }
}

float cvw_piecewiseQuadraticWarpBlurFactorForFoveation(float x, float factor, VRShaderPiecewiseQuadraticWarpDesc desc)
{
    if (x < desc.switchLeft)
    {
        return clamp(abs(factor * (2 * desc.al * x + desc.bl - desc.am)), 0.0f, 1.0f);
    }
    else if (x > desc.switchRight)
    {
        return clamp(abs(factor * (2 * desc.ar * x + desc.br - desc.am)), 0.0f, 1.0f);
    }
    else
    {
        return 0.0;
    }
}

float cvw_inversePiecewiseQuadraticWarpForFoveation(float y, VRShaderPiecewiseQuadraticWarpDesc desc)
{
    if (y < desc.invSwitchLeft)
    {
        return (sqrt(-4 * desc.al * desc.cl + 4 * desc.al * y + desc.bl * desc.bl) - desc.bl) / (2 * desc.al);
    }
    else if (y > desc.invSwitchRight)
    {
        return (sqrt(-4 * desc.ar * desc.cr + 4 * desc.ar * y + desc.br * desc.br) - desc.br) / (2 * desc.ar);
    }
    else
    {
        return (y - desc.bm) / desc.am;
    }
}
