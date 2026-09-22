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
#endif

#define kXRConvertFcnNone 0 // out = in
#define kXRConvertFcnScale 1 // out = in * alpha + beta
#define kXRConvertFcnInvScale 2 // out = 1 / (in * alpha + beta) + gamma

#define kXRAlphaFcnNone 0 // alpha = alpha
#define kXRAlphaFcnSetZero 1 // alpha = 0
#define kXRAlphaFcnSetOne 2 // alpha = 1
#define kXRAlphaFcnCopyToRGB 3 // copy alpha to rgb

struct XRConvertFunctionParams
{
    uint fcn;
    uint alphaFcn;

    float alpha;
    float beta;
    float gamma;
    float delta;

    float2 padding;
};
