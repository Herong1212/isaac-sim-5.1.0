// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#    include "CvwWarpTypeEnum.h"
#endif

#define CVW_WARP_DATA_SIZE 24

/**
 * An opaque block that can hold different types of warp information.
 */

struct XRArbitraryWarp
{
    XRWarpType warpType;
    int pad1;
    int pad2;
    int pad3;

    float4 data0;
    float4 data1;
    float4 data2;
    float4 data3;
    float4 data4;
    float4 data5;
};

struct XRCameraData
{
    XRArbitraryWarp warp;

    float fovxInRadians;
    float tanHalfFovY;
    float farPlane;
    float nearPlane;

    float aspectRatio;

    float pad1, pad2, pad3;
};
