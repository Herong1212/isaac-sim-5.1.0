// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <stddef.h>

namespace omni
{
namespace graph
{
namespace core
{

template <typename T>
struct GpuArray
{
    // GPU pointer to data
    T* const* gpuData;

    // GPU pointer to elem count
    const size_t* elemCount;

#ifdef __CUDACC__
    __device__ T* data()
    {
        return *gpuData;
    }

    __device__ size_t size() const
    {
        return *elemCount;
    }
#endif
};

template <typename T>
struct ArrayOfGpuArray
{
    // GPU array of GPU data pointers
    T* const* gpuData;

    // GPU array of elem counts
    const size_t* elemCount;

#ifdef __CUDACC__
    __device__ T* data(size_t i) const
    {
        return gpuData[i];
    }

    __device__ size_t size(size_t i) const
    {
        return elemCount[i];
    }
#endif
};

template <typename T>
struct ConstGpuArray
{
    // GPU pointer to data
    const T* const* gpuData;

    // GPU pointer to elem count
    const size_t* elemCount;

#ifdef __CUDACC__
    __device__ const T* data() const
    {
        return *gpuData;
    }

    __device__ size_t size() const
    {
        return *elemCount;
    }
#endif
};

template <typename T>
struct ArrayOfConstGpuArray
{
    // GPU array of GPU data pointers
    const T* const* gpuData;

    // GPU array of elem counts
    const size_t* elemCount;

#ifdef __CUDACC__
    __device__ const T* data(size_t i) const
    {
        return gpuData[i];
    }

    __device__ size_t size(size_t i) const
    {
        return elemCount[i];
    }
#endif
};

}
}
}
