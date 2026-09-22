// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#    include "XRGpuToolsConvertParams.h"
#    include "xr_cvw/CameraViewWarp.h"
#endif


struct XRGpuToolsResampleImageSamplers
{
    StaticSamplerState pointSampler;
    StaticSamplerState linearSampler;
};


#define XRGpuToolsResampleImageParams_definition(texture_datatype, output_datatype)                                    \
    struct XRGpuToolsResampleImageParams_##texture_datatype##_##output_datatype                                        \
    {                                                                                                                  \
        XRArbitraryWarp warp;                                                                                          \
                                                                                                                       \
        uint2 outOffset;                                                                                               \
        uint2 outSize;                                                                                                 \
        float2 inOffset;                                                                                               \
        float2 inStride;                                                                                               \
        float2 inSize;                                                                                                 \
                                                                                                                       \
        float lowresDimFactor;                                                                                         \
        float highresDimFactor;                                                                                        \
        XRConvertFunctionParams convertParams;                                                                         \
                                                                                                                       \
        uint resampleMode;                                                                                             \
        float invBlendDistance;                                                                                        \
                                                                                                                       \
        BeginResources();                                                                                              \
                                                                                                                       \
        RGTexture2D<texture_datatype> inputTexture;                                                                    \
        RGRWTexture2D<output_datatype> outputTexture;                                                                  \
                                                                                                                       \
        EndResourcesSamplers(XRGpuToolsResampleImageSamplers);                                                         \
    };

XRGpuToolsResampleImageParams_definition(float, float);
XRGpuToolsResampleImageParams_definition(float2, float2);
XRGpuToolsResampleImageParams_definition(float3, float3);
XRGpuToolsResampleImageParams_definition(float4, float4);
XRGpuToolsResampleImageParams_definition(float, float4);
XRGpuToolsResampleImageParams_definition(float2, float4);
XRGpuToolsResampleImageParams_definition(float3, float4);
