// Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// This file contains support for CUDA or CUDA/C++ common code

// TODO: find out how to assert in CUDA
#ifndef __CUDACC__
#    define CUDA_SAFE_ASSERT(cond, ...) CARB_ASSERT(cond, ##__VA_ARGS__)
#    define CUDA_CALLABLE
#else
#    define CUDA_SAFE_ASSERT(cond, ...)
#    define CUDA_CALLABLE __device__ __host__
#endif
