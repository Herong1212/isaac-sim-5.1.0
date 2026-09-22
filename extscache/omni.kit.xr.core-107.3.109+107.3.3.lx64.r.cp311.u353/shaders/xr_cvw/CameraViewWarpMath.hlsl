// Copyright (c) 2019-2022, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#ifdef __cplusplus
#pragma once

#include "CameraViewWarp.h"
#include "VRPiecewiseQuadraticWarp.h"
#include "CvwVRWarpMath.h"

#endif

VRShaderPiecewiseWarps XRArbitraryWarpToPiecewiseQuadraticWarps(XRArbitraryWarp warp)
{
    VRShaderPiecewiseQuadraticWarpDesc xWarp;
    VRShaderPiecewiseQuadraticWarpDesc yWarp;

    xWarp.al = warp.data0.x;
    xWarp.bl = warp.data0.y;
    xWarp.cl = warp.data0.z;
    xWarp.am = warp.data0.w;
    xWarp.bm = warp.data1.x;
    xWarp.ar = warp.data1.y;
    xWarp.br = warp.data1.z;
    xWarp.cr = warp.data1.w;
    xWarp.switchLeft = warp.data2.x;
    xWarp.switchRight = warp.data2.y;
    xWarp.invSwitchLeft = warp.data2.z;
    xWarp.invSwitchRight = warp.data2.w;

    yWarp.al = warp.data3.x;
    yWarp.bl = warp.data3.y;
    yWarp.cl = warp.data3.z;
    yWarp.am = warp.data3.w;
    yWarp.bm = warp.data4.x;
    yWarp.ar = warp.data4.y;
    yWarp.br = warp.data4.z;
    yWarp.cr = warp.data4.w;
    yWarp.switchLeft = warp.data5.x;
    yWarp.switchRight = warp.data5.y;
    yWarp.invSwitchLeft = warp.data5.z;
    yWarp.invSwitchRight = warp.data5.w;

    return {xWarp, yWarp};
}

float2 cvw_calculateForwardWarp(float2 pos, XRArbitraryWarp warp)
{
    if (warp.warpType == XRWarpType::eNone)
    {
        return pos;
    }
    else if (warp.warpType == XRWarpType::eVRPiecewiseQuadraticPerAxis)
    {
        VRShaderPiecewiseWarps piecewiseWarps = XRArbitraryWarpToPiecewiseQuadraticWarps(warp);

        pos.x = cvw_piecewiseQuadraticWarpForFoveation(pos.x, piecewiseWarps.xWarp);
        pos.y = cvw_piecewiseQuadraticWarpForFoveation(pos.y, piecewiseWarps.yWarp);

        return pos;
    }

    return pos;
}

float2 cvw_calculateInverseWarp(float2 pos, XRArbitraryWarp warp)
{
    if (warp.warpType == XRWarpType::eNone)
    {
        return pos;
    }
    else if (warp.warpType == XRWarpType::eVRPiecewiseQuadraticPerAxis)
    {
        VRShaderPiecewiseWarps piecewiseWarps = XRArbitraryWarpToPiecewiseQuadraticWarps(warp);

        pos.x = cvw_inversePiecewiseQuadraticWarpForFoveation(pos.x, piecewiseWarps.xWarp);
        pos.y = cvw_inversePiecewiseQuadraticWarpForFoveation(pos.y, piecewiseWarps.yWarp);

        return pos;
    }

    return pos;
}

float2 cvw_calculateWarpDerivative(float2 pos, XRArbitraryWarp warp)
{
    if (warp.warpType == XRWarpType::eNone)
    {
        return float2(1, 1);
    }
    else if (warp.warpType == XRWarpType::eVRPiecewiseQuadraticPerAxis)
    {
        VRShaderPiecewiseWarps piecewiseWarps = XRArbitraryWarpToPiecewiseQuadraticWarps(warp);

        pos.x = cvw_piecewiseQuadraticWarpDerivativeForFoveation(pos.x, piecewiseWarps.xWarp);
        pos.y = cvw_piecewiseQuadraticWarpDerivativeForFoveation(pos.y, piecewiseWarps.yWarp);

        return pos;
    }

    return float2(1, 1);
}

float2 cvw_calculateWarpBlurFactor(float2 pos, float factor, XRArbitraryWarp warp)
{
    if (warp.warpType == XRWarpType::eNone)
    {
        return float2(0, 0);
    }
    else if (warp.warpType == XRWarpType::eVRPiecewiseQuadraticPerAxis)
    {
        float2 ret;
        VRShaderPiecewiseWarps piecewiseWarps = XRArbitraryWarpToPiecewiseQuadraticWarps(warp);

        ret.x = cvw_piecewiseQuadraticWarpDerivativeForFoveation(pos.x, piecewiseWarps.xWarp) - piecewiseWarps.xWarp.am;
        ret.y = cvw_piecewiseQuadraticWarpDerivativeForFoveation(pos.y, piecewiseWarps.yWarp) - piecewiseWarps.xWarp.am;

        ret.x = clamp(abs(factor * ret.x), 0.0f, 1.0f);
        ret.y = clamp(abs(factor * ret.y), 0.0f, 1.0f);

        return pos;
    }

    return float2(0, 0);
}

bool cvw_calculateIsPointInFovea(float2 pos, XRArbitraryWarp warp)
{
    if (warp.warpType == XRWarpType::eNone)
    {
        return true;
    }
    else if (warp.warpType == XRWarpType::eVRPiecewiseQuadraticPerAxis)
    {
        VRShaderPiecewiseWarps piecewiseWarps = XRArbitraryWarpToPiecewiseQuadraticWarps(warp);

        if(pos.x < piecewiseWarps.xWarp.switchLeft)
        {
            return false;
        }
        if(pos.x > piecewiseWarps.xWarp.switchRight)
        {
            return false;
        }
        if(pos.y < piecewiseWarps.yWarp.switchLeft)
        {
            return false;
        }
        if(pos.y > piecewiseWarps.yWarp.switchRight)
        {
            return false;
        }

        return true;
    }

    return true;
}
