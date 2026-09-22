// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

[__AttributeUsage(_AttributeTargets.Var)]
struct StaticSamplerAttribute
{
};

#define BeginResources()
#define EndResources()
#define EndResourcesSamplers(samplerType) samplerType staticSamplers;

#define RGTexture2D Texture2D
#define RGRWTexture2D RWTexture2D
#define StaticSamplerState [StaticSampler] SamplerState
