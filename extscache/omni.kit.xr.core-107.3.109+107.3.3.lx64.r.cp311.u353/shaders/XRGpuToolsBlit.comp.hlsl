// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#ifdef __cplusplus
#include "ParamBlock.hlsl"
#include "XRGpuToolsConvertFunctions.hlsl"
#include "XRGpuToolsBlitParams.h"
#endif

#ifndef TEXTURE_CHANNELS
#define TEXTURE_CHANNELS 0
#endif

#ifndef CONVERT_TO_RGBA
#define CONVERT_TO_RGBA 0
#endif

#if CONVERT_TO_RGBA == 0
#if TEXTURE_CHANNELS == 1
#define TEXTURE_DATATYPE float
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float_float
#elif TEXTURE_CHANNELS == 2
#define TEXTURE_DATATYPE float2
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float2_float2
#elif TEXTURE_CHANNELS == 3
#define TEXTURE_DATATYPE float3
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float3_float3
#elif TEXTURE_CHANNELS == 4
#define TEXTURE_DATATYPE float4
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float4_float4
#else
#error "TEXTURE_CHANNELS must be defined from within the set of (1,2,3,4)"
#define TEXTURE_DATATYPE float4
#endif
#else
#if TEXTURE_CHANNELS == 1
#define TEXTURE_DATATYPE float
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float_float4
#elif TEXTURE_CHANNELS == 2
#define TEXTURE_DATATYPE float2
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float2_float4
#elif TEXTURE_CHANNELS == 3
#define TEXTURE_DATATYPE float3
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float3_float4
#elif TEXTURE_CHANNELS == 4
#define TEXTURE_DATATYPE float4
#define XRGpuToolsBlitImageParams_t XRGpuToolsBlitImageParams_float4_float4
#else
#error "TEXTURE_CHANNELS must be defined from within the set of (1,2,3,4)"
#define TEXTURE_DATATYPE float4
#endif
#endif

[[vk::binding(0, 0)]]
ParameterBlock<XRGpuToolsBlitImageParams_t> gXRBlitImageParams : register(space0);

[numthreads(16, 16, 1)]
void main(uint2 pixelIndex: SV_DispatchThreadID)
{
    if (pixelIndex.x >= gXRBlitImageParams.outSize.x || pixelIndex.y >= gXRBlitImageParams.outSize.y)
    {
        return;
    }

    if (pixelIndex.x >= gXRBlitImageParams.inSize.x || pixelIndex.y >= gXRBlitImageParams.inSize.y)
    {
        return;
    }

    TEXTURE_DATATYPE color = gXRBlitImageParams.inputTexture[pixelIndex + gXRBlitImageParams.inOffset];

#if CONVERT_TO_RGBA == 0
    TEXTURE_DATATYPE outColor = color;
#else
    float4 outColor = float4(0, 0, 0, 1);
#endif

#if CONVERT_TO_RGBA == 0
    outColor = convertFunction(color, gXRBlitImageParams.convertParams);
#else
#if TEXTURE_CHANNELS == 1
    outColor = convertFunction(float4(color, color, color, 1), gXRBlitImageParams.convertParams);
#elif TEXTURE_CHANNELS == 2
    outColor = convertFunction(float4(color.x, color.y, 0, 1), gXRBlitImageParams.convertParams);
#elif TEXTURE_CHANNELS == 3
    outColor = convertFunction(float4(color.x, color.y, color.z, 1), gXRBlitImageParams.convertParams);
#else
    outColor = convertFunction(color, gXRBlitImageParams.convertParams);
#endif
#endif

gXRBlitImageParams.outputTexture[pixelIndex + gXRBlitImageParams.outOffset] = outColor;

}
