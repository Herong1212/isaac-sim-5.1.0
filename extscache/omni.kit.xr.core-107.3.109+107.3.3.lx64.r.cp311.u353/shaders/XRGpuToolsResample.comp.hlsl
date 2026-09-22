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
#include "xr_cvw/CameraViewWarpMath.hlsl"
#include "XRGpuToolsConvertFunctions.hlsl"
#include "XRGpuToolsResampleFunctions.hlsl"
#include "XRGpuToolsResampleParams.h"
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
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float_float
#elif TEXTURE_CHANNELS == 2
#define TEXTURE_DATATYPE float2
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float2_float2
#elif TEXTURE_CHANNELS == 3
#define TEXTURE_DATATYPE float3
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float3_float3
#elif TEXTURE_CHANNELS == 4
#define TEXTURE_DATATYPE float4
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float4_float4
#else
#error "TEXTURE_CHANNELS must be defined from within the set of (1,2,3,4)"
#define TEXTURE_DATATYPE float4
#endif
#else
#if TEXTURE_CHANNELS == 1
#define TEXTURE_DATATYPE float
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float_float4
#elif TEXTURE_CHANNELS == 2
#define TEXTURE_DATATYPE float2
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float2_float4
#elif TEXTURE_CHANNELS == 3
#define TEXTURE_DATATYPE float3
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float3_float4
#elif TEXTURE_CHANNELS == 4
#define TEXTURE_DATATYPE float4
#define XRGpuToolsResampleImageParams_t XRGpuToolsResampleImageParams_float4_float4
#else
#error "TEXTURE_CHANNELS must be defined from within the set of (1,2,3,4)"
#define TEXTURE_DATATYPE float4
#endif
#endif

[[vk::binding(0, 0)]]
ParameterBlock<XRGpuToolsResampleImageParams_t> gXRResampleImageParams : register(space0);

[numthreads(16, 16, 1)] void main(uint2 pixelIndex
                                  : SV_DispatchThreadID) {
    if (pixelIndex.x >= gXRResampleImageParams.outSize.x || pixelIndex.y >= gXRResampleImageParams.outSize.y)
    {
        return;
    }

    float2 inputCoords =
        gXRResampleImageParams.inOffset + gXRResampleImageParams.inStride * pixelIndex;

    inputCoords = cvw_calculateInverseWarp(inputCoords, gXRResampleImageParams.warp);

    bool outOfBounds = inputCoords.x < 0 || inputCoords.x >= 1 || inputCoords.y < 0 || inputCoords.y >= 1;

#if TEXTURE_CHANNELS == 4
    TEXTURE_DATATYPE color = float4(0, 0, 0, 1);
#else
    TEXTURE_DATATYPE color = TEXTURE_DATATYPE(0.0f);
#endif

#if CONVERT_TO_RGBA == 0
    TEXTURE_DATATYPE outColor = color;
#else
    float4 outColor = float4(0, 0, 0, 1);
#endif

    if (!outOfBounds)
    {
        if (gXRResampleImageParams.resampleMode == 0)
        {
            color = gXRResampleImageParams.inputTexture.SampleLevel(gXRResampleImageParams.staticSamplers.linearSampler, inputCoords, 0);
        }
        else if (gXRResampleImageParams.resampleMode == 1)
        {
            color = gXRResampleImageParams.inputTexture.SampleLevel(gXRResampleImageParams.staticSamplers.pointSampler, inputCoords, 0);
        }
        else
        {
            color = lanczosSample(gXRResampleImageParams.inputTexture, gXRResampleImageParams.inSize, inputCoords);
        }

#if CONVERT_TO_RGBA == 0
        outColor = convertFunction(color, gXRResampleImageParams.convertParams);
#else
#if TEXTURE_CHANNELS == 1
        outColor = convertFunction(float4(color,color,color,1),gXRResampleImageParams.convertParams);
#elif TEXTURE_CHANNELS == 2
        outColor = convertFunction(float4(color.x,color.y,0,1),gXRResampleImageParams.convertParams);
#elif TEXTURE_CHANNELS == 3
        outColor = convertFunction(float4(color.x,color.y,color.z,1),gXRResampleImageParams.convertParams);
#else
        outColor = convertFunction(color, gXRResampleImageParams.convertParams);
#endif
#endif

        if (gXRResampleImageParams.lowresDimFactor != 1.0f || gXRResampleImageParams.highresDimFactor != 1.0f)
        {
            if (!cvw_calculateIsPointInFovea(inputCoords, gXRResampleImageParams.warp))
            {
#if CONVERT_TO_RGBA == 1
                outColor.xyz = outColor.xyz * gXRResampleImageParams.lowresDimFactor;
#else
                outColor = outColor * gXRResampleImageParams.lowresDimFactor;
#endif
            }
            else
            {
#if CONVERT_TO_RGBA == 1
                outColor.xyz = outColor.xyz * gXRResampleImageParams.highresDimFactor;
#else
                outColor = outColor * gXRResampleImageParams.highresDimFactor;
#endif
            }
        }
    }

    if (gXRResampleImageParams.invBlendDistance > 0.0f)
    {
        float dist = min(min(inputCoords.x, 1.0 - inputCoords.x), min(inputCoords.y, 1.0 - inputCoords.y));
        float alpha = min(gXRResampleImageParams.invBlendDistance * dist, 1.0f);
        outColor = outColor * alpha + (1.0f - alpha) * gXRResampleImageParams.outputTexture[pixelIndex + gXRResampleImageParams.outOffset];
    }

    gXRResampleImageParams.outputTexture[pixelIndex + gXRResampleImageParams.outOffset] = outColor;
}
