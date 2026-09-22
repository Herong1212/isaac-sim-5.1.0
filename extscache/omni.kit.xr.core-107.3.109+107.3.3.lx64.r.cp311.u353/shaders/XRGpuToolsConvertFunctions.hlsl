// Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#ifdef __cplusplus
#include "XRGpuToolsConvertParams.h"
#endif

inline float convertFunction(float input, XRConvertFunctionParams params)
{
    if (params.fcn == kXRConvertFcnNone)
    {
        return input;
    }
    if (params.fcn == kXRConvertFcnScale)
    {
        return input * params.alpha + params.beta;
    }
    if (params.fcn == kXRConvertFcnInvScale)
    {
        return 1.0f / ( input * params.alpha + params.beta ) + params.gamma;
    }

    return input;
}

inline float2 convertFunction(float2 input, XRConvertFunctionParams params)
{
    if (params.fcn == kXRConvertFcnNone)
    {
        return input;
    }
    if (params.fcn == kXRConvertFcnScale)
    {
        return input * params.alpha + params.beta * float2(1.0f);
    }
    if (params.fcn == kXRConvertFcnInvScale)
    {
        return float2(1.0f) / ( input * params.alpha + params.beta * float2(1.0f)) + params.gamma * float2(1.0f);
    }

    return input;
}

inline float3 convertFunction(float3 input, XRConvertFunctionParams params)
{
    if (params.fcn == kXRConvertFcnNone)
    {
        return input;
    }
    if (params.fcn == kXRConvertFcnScale)
    {
        return input * params.alpha + params.beta * float3(1.0f);
    }
    if (params.fcn == kXRConvertFcnInvScale)
    {
        return float3(1.0f) / ( input * params.alpha + params.beta * float3(1.0f)) + params.gamma * float3(1.0f);
    }

    return input;
}

inline float4 convertFunction(float4 input, XRConvertFunctionParams params)
{
    float4 ret;
    ret.xyz = convertFunction(input.xyz, params);

    if (params.alphaFcn == kXRAlphaFcnNone)
    {
        ret.w = convertFunction(input.w, params);
    }
    else if (params.alphaFcn == kXRAlphaFcnSetOne)
    {
        ret.w = 1.0;
    }
    else if (params.alphaFcn == kXRAlphaFcnSetZero)
    {
        ret.w = 0.0;
    }
    else if (params.alphaFcn == kXRAlphaFcnCopyToRGB)
    {
        ret.x = input.w;
        ret.y = input.w;
        ret.z = input.w;
        ret.w = 1.0f;
    }

    return ret;
}
