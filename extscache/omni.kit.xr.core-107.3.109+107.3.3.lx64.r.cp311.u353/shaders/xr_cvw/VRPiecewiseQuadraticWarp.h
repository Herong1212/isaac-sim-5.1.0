// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#endif
struct VRShaderPiecewiseQuadraticWarpDesc
{
    // left parabola: al * x^2 + bl * x + cl
    float al, bl, cl;
    // middle linear piece: am * x + bm.  am should give 1:1 pixel mapping between warped size and full size.
    float am, bm;
    // right parabola: ar * x^2 + br * x + cr
    float ar, br, cr;

    // points where left and right switch over from quadratic to linear
    float switchLeft, switchRight;
    // same, in inverted space
    float invSwitchLeft, invSwitchRight;
};

struct VRShaderPiecewiseWarps
{
    VRShaderPiecewiseQuadraticWarpDesc xWarp;
    VRShaderPiecewiseQuadraticWarpDesc yWarp;
};
