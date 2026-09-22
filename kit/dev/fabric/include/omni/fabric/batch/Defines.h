// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <cstddef>
#include <cstdint>


#if defined(__CUDACC__)
#    if __CUDACC_DEBUG__
#        include <cassert>
#        define BATCH_ASSERT(...) assert(__VA_ARGS__)
#    else
#        define BATCH_ASSERT(...) ((void)0)
#    endif
#    define BATCH_SHARED_API __device__ __host__
#else
#    include <carb/Defines.h>
#    define BATCH_ASSERT(...) CARB_ASSERT(__VA_ARGS__)
#    define BATCH_SHARED_API
#endif // #if defined (__CUDACC__)


namespace omni
{
namespace fabric
{
namespace batch
{

template <typename T, typename U>
BATCH_SHARED_API inline constexpr T alignUp(const T& value, const U& alignment)
{
    BATCH_ASSERT(alignment);
    return ((value + alignment - 1) / alignment) * alignment;
}

template <typename T, typename U>
BATCH_SHARED_API inline constexpr T alignDown(const T& value, const U& alignment)
{
    BATCH_ASSERT(alignment);
    return (value / alignment) * alignment;
}

} // namespace batch
} // namespace fabric
} // namespace omni
