// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

// #include <carb/logging/Log.h>
// #ifndef __CUDACC__
// #    include <carb/profiler/Profile.h> // This has some useful macros (OVCC-1220 to make it more general).
// #endif

#include <cuda_runtime.h>
#include <iostream>


#define NVPTXCOMPILER_SAFE_CALL(x)                                                                                     \
    do                                                                                                                 \
    {                                                                                                                  \
        nvPTXCompileResult result = x;                                                                                 \
        if (result != NVPTXCOMPILE_SUCCESS)                                                                            \
        {                                                                                                              \
            printf("%s failed with error code %s \n", #x, result);                                                     \
        }                                                                                                              \
    } while (0)

/**
 * Protects a CUDA call that could fail.
 *
 * The user can optionally supply additional context in the form a of printf qualifiers in the case of an error.
 *
 * Eg
 *   CUDA_CALL(cudaFree(ptr))
 * or
 *   CUDA_CALL(cudaFree(ptr), "ptr = %p", ptr);
 *
 * This can make debugging crashes and other hard to find issues easier.
 */
#ifndef __CUDACC__
#    define CUDA_CALL(call, ...)                                                                                       \
        do                                                                                                             \
        {                                                                                                              \
            cudaError_t result = call;                                                                                 \
            if (result != cudaSuccess)                                                                                 \
            {                                                                                                          \
                printf("CUDA error %d in %s:%d:%s (%s) \n", result, __FILE__, __LINE__, cudaGetErrorString(result),    \
                       #call);                                                                                         \
            }                                                                                                          \
        } while (0)
#else
#    define CUDA_CALL(call, ...)                                                                                       \
        do                                                                                                             \
        {                                                                                                              \
            cudaError_t result = call;                                                                                 \
            if (result != cudaSuccess)                                                                                 \
            {                                                                                                          \
                printf("CUDA error %d in %s:%d:%s (%s) \n", result, __FILE__, __LINE__, cudaGetErrorString(result),    \
                       #call);                                                                                         \
            }                                                                                                          \
        } while (0)
#endif

#define CUDA_SAFE_CALL(x)                                                                                              \
    do                                                                                                                 \
    {                                                                                                                  \
        CUresult result = x;                                                                                           \
        if (result != CUDA_SUCCESS)                                                                                    \
        {                                                                                                              \
            const char* msg;                                                                                           \
            cuGetErrorName(result, &msg);                                                                              \
            printf("%s failed with error %s \n", #x, msg);                                                             \
        }                                                                                                              \
    } while (0)

#define CUDA_DRIVER_CALL(x)                                                                                            \
    do                                                                                                                 \
    {                                                                                                                  \
        CUresult _res = x;                                                                                             \
        if (_res != CUDA_SUCCESS)                                                                                      \
        {                                                                                                              \
            const char* _errString;                                                                                    \
            cuGetErrorString(_res, &_errString);                                                                       \
            printf("CUDA Driver CALL FAILED at line %d: %s \n", __LINE__, _errString);                                 \
        }                                                                                                              \
    } while (0)

#define NVRTC_CALL(x)                                                                                                  \
    do                                                                                                                 \
    {                                                                                                                  \
        nvrtcResult _res = x;                                                                                          \
        if (_res != NVRTC_SUCCESS)                                                                                     \
        {                                                                                                              \
            const char* _errString = nvrtcGetErrorString(_res);                                                        \
            printf("NVRTC CALL FAILED at line %d: %s \n", __LINE__, _errString);                                       \
        }                                                                                                              \
    } while (0)

#define NVRTC_PROGRAM_LOG(prog, log)                                                                                   \
    do                                                                                                                 \
    {                                                                                                                  \
        size_t logSize;                                                                                                \
        if (nvrtcGetProgramLogSize(prog, &logSize) == NVRTC_SUCCESS)                                                   \
        {                                                                                                              \
            log.resize(logSize, '\0');                                                                                 \
            if (nvrtcGetProgramLog(prog, &log[0]) != NVRTC_SUCCESS)                                                    \
            {                                                                                                          \
                printf("Unable to get nvrtc program log.\n");                                                          \
                log.clear();                                                                                           \
            }                                                                                                          \
        }                                                                                                              \
        else                                                                                                           \
        {                                                                                                              \
            printf("Unable to get nvrtc program log size\n");                                                          \
        }                                                                                                              \
    } while (0)

//-----------------------------------------------------------------------------
#if defined(__CUDACC__) || defined(__CUDABE__)
#    include <cuda_runtime.h>
#    define NV_HOST __host__
#    define NV_DEVICE __device__
#    define NV_HOSTDEVICE NV_HOST NV_DEVICE
#    define NV_HOSTDEVICENOINLINE NV_HOST NV_DEVICE __noinline__
#    define NV_DEVICECODE(...) __VA_ARGS__
#    define NV_HOSTCODE(...)
#else
#    define NV_HOST
#    define NV_DEVICE
#    define NV_HOSTDEVICE
#    define NV_HOSTDEVICENOINLINE
#    define NV_DEVICECODE(...)
#    define NV_HOSTCODE(...) __VA_ARGS__
#endif
