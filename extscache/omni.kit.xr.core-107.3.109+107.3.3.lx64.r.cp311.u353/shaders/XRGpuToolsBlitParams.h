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
#endif

#define XRGpuToolsBlitImageParams_definition(texture_datatype, output_datatype)                                        \
    struct XRGpuToolsBlitImageParams_##texture_datatype##_##output_datatype                                            \
    {                                                                                                                  \
        uint2 outSize;                                                                                                 \
        uint2 outOffset;                                                                                               \
        uint2 inSize;                                                                                                  \
        uint2 inOffset;                                                                                                \
        XRConvertFunctionParams convertParams;                                                                         \
                                                                                                                       \
        BeginResources();                                                                                              \
                                                                                                                       \
        RGTexture2D<texture_datatype> inputTexture;                                                                    \
        RGRWTexture2D<output_datatype> outputTexture;                                                                  \
        EndResources();                                                                                                \
    };

XRGpuToolsBlitImageParams_definition(float, float);
XRGpuToolsBlitImageParams_definition(float2, float2);
XRGpuToolsBlitImageParams_definition(float3, float3);
XRGpuToolsBlitImageParams_definition(float4, float4);
XRGpuToolsBlitImageParams_definition(float, float4);
XRGpuToolsBlitImageParams_definition(float2, float4);
XRGpuToolsBlitImageParams_definition(float3, float4);
