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

#include "CudaHelperDecl.h"

#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <type_traits>

namespace omni
{
namespace sensors
{
namespace cuda
{

enum class MemKind : uint8_t
{
    GPU = 0,
    CPU_PINNED = 1,
    CPU_MALLOC = 2,
    CPU_NEW = 3,
};

struct MemcpyData
{
    void* dstPtr;
    void* srcPtr;
    size_t sizeInBytes;
};

template <class T>
inline NV_HOST void allocateBlob(T** ptr, const size_t numElems, const MemKind mem)
{
    *ptr = nullptr;

    if (numElems > 0)
    {
        switch (mem)
        {
        case MemKind::GPU:
        {
            CUDA_CALL(cudaMalloc(ptr, numElems * sizeof(T)));
            break;
        }
        case MemKind::CPU_PINNED:
        {
            CUDA_CALL(cudaMallocHost(ptr, numElems * sizeof(T)));
            break;
        }
        case MemKind::CPU_MALLOC:
        {
            *ptr = (T*)malloc(numElems * sizeof(T));
            break;
        }
        case MemKind::CPU_NEW:
        {
            *ptr = new T[numElems]{};
            break;
        }
        default:
            printf("allocateBlob: invalid MemKind \n");
        }
    }
    else
    {
        printf("allocateBlob: attempt to allocate 0 sized buffer \n");
    }
}

inline NV_HOST void allocateBlob(void** ptr, const size_t sizeInBytes, const MemKind mem)
{
    *ptr = nullptr;

    if (sizeInBytes > 0)
    {
        switch (mem)
        {
        case MemKind::GPU:
        {
            CUDA_CALL(cudaMalloc(ptr, sizeInBytes));
            break;
        }
        case MemKind::CPU_PINNED:
        {
            CUDA_CALL(cudaMallocHost(ptr, sizeInBytes));
            break;
        }
        case MemKind::CPU_MALLOC:
        {
            *ptr = malloc(sizeInBytes);
            break;
        }
        case MemKind::CPU_NEW:
        {
            printf("allocateBlob: MemKind CPU_NEW needs a non void pointer \n");
            break;
        }
        default:
            printf("allocateBlob: invalid MemKind \n");
        }
    }
    else
    {
        printf("allocateBlob: attempt to allocate 0 sized buffer \n");
    }
}

template <class T>
inline NV_HOST void freeBlob(T* ptr, MemKind mem)
{
    if (ptr)
    {
        switch (mem)
        {
        case MemKind::GPU:
        {
            CUDA_CALL(cudaFree(ptr));
            break;
        }
        case MemKind::CPU_PINNED:
        {
            CUDA_CALL(cudaFreeHost(ptr));
            break;
        }
        case MemKind::CPU_MALLOC:
        {
            free(ptr);
            break;
        }
        case MemKind::CPU_NEW:
        {
            delete[] (ptr);
            break;
        }
        default:
            printf("freeBlob: invalid MemKind \n");
        }
    }
    else
    {
        printf("freeBlob: attempt to free invalid buffer \n");
    }
}

inline NV_HOST void freeBlob(void* ptr, MemKind mem)
{
    if (ptr)
    {
        switch (mem)
        {
        case MemKind::GPU:
        {
            CUDA_CALL(cudaFree(ptr));
            break;
        }
        case MemKind::CPU_PINNED:
        {
            CUDA_CALL(cudaFreeHost(ptr));
            break;
        }
        case MemKind::CPU_MALLOC:
        {
            free(ptr);
            break;
        }
        case MemKind::CPU_NEW:
        {
            printf("freeBlob: MemKind CPU_NEW needs a non void pointer \n");
            break;
        }
        default:
            printf("freeBlob: invalid MemKind \n");
        }
    }
    else
    {
        printf("freeBlob: attempt to free invalid buffer \n");
    }
}

template <class T>
inline NV_HOST void setMem(T* ptr, int value, size_t numElems, int32_t cudaDevice = -1, cudaStream_t cudaStream = 0)
{
    if (cudaDevice >= 0)
    {
        if (cudaStream)
        {
            CUDA_CALL(cudaMemsetAsync((void*)ptr, value, numElems * sizeof(T), cudaStream));
        }
        else
        {
            CUDA_CALL(cudaMemset((void*)ptr, value, numElems * sizeof(T)));
        }
    }
    else
    {
        memset((void*)ptr, value, numElems * sizeof(T));
    }
}


inline NV_HOST void setMem(void* ptr, int value, size_t sizeInBytes, int32_t cudaDevice = -1, cudaStream_t cudaStream = 0)
{
    if (cudaDevice >= 0)
    {
        if (cudaStream)
        {
            CUDA_CALL(cudaMemsetAsync((void*)ptr, value, sizeInBytes, cudaStream));
        }
        else
        {
            CUDA_CALL(cudaMemset((void*)ptr, value, sizeInBytes));
        }
    }
    else
    {
        memset((void*)ptr, value, sizeInBytes);
    }
}

/**
 * @brief Copy memory from srcPtr to dstPtr (array version)
 *
 * @tparam T type of the data
 * @param dstPtr destination pointer
 * @param srcPtr source pointer
 * @param numElems number of elements to copy
 * @param kind cudaMemcpyKind to perform
 * @param cudaDevice device ID
 * @param cudaStream stream to run copy on
 * @return NV_HOST
 */
template <class T>
inline NV_HOST void cpyMem(T* dstPtr,
                           T* srcPtr,
                           const size_t numElems,
                           const cudaMemcpyKind kind,
                           const int32_t cudaDevice = -1,
                           const cudaStream_t cudaStream = 0)
{
    if (cudaDevice >= 0)
    {
        if (cudaStream)
        {
            if (kind == cudaMemcpyHostToHost)
            {
                MemcpyData* data = new MemcpyData{ dstPtr, srcPtr, numElems * sizeof(T) };
                cudaLaunchHostFunc(
                    cudaStream,
                    [](void* userData)
                    {
                        MemcpyData* data = (MemcpyData*)userData;
                        memcpy(data->dstPtr, data->srcPtr, data->sizeInBytes);
                        delete (data);
                    },
                    (void*)data);
            }
            else
            {
                CUDA_CALL(cudaMemcpyAsync((void*)dstPtr, (void*)srcPtr, numElems * sizeof(T), kind, cudaStream));
            }
        }
        else
        {
            CUDA_CALL(cudaMemcpy((void*)dstPtr, (void*)srcPtr, numElems * sizeof(T), kind));
        }
    }
    else
    {
        memcpy((void*)dstPtr, (void*)srcPtr, numElems * sizeof(T));
    }
}

/**
 * @brief Copy memory from srcPtr to dstPtr
 * Given the device and cudaStream will perform a copy asyncronously. Pay attention to variable lifetimes!
 *
 * @param dstPtr destination pointer
 * @param srcPtr source pointer
 * @param sizeInBytes size in bytes
 * @param kind cudaMemcpyKind to perform
 * @param cudaDevice device ID
 * @param cudaStream stream to run copy on
 * @return NV_HOST
 */
inline NV_HOST void cpyMem(void* dstPtr,
                           void* srcPtr,
                           const size_t sizeInBytes,
                           const cudaMemcpyKind kind,
                           const int32_t cudaDevice = -1,
                           const cudaStream_t cudaStream = 0)
{
    if (cudaDevice >= 0)
    {
        if (cudaStream)
        {
            if (kind == cudaMemcpyHostToHost)
            {
                MemcpyData* data = new MemcpyData{ dstPtr, srcPtr, sizeInBytes };
                cudaLaunchHostFunc(
                    cudaStream,
                    [](void* userData)
                    {
                        MemcpyData* data = (MemcpyData*)userData;
                        memcpy(data->dstPtr, data->srcPtr, data->sizeInBytes);
                        delete (data);
                    },
                    (void*)data);
            }
            else
            {
                CUDA_CALL(cudaMemcpyAsync((void*)dstPtr, (void*)srcPtr, sizeInBytes, kind, cudaStream),
                          "dstPtr = %p, srcPtr = %p, sizeInBytes = %zu, kind = %d, cudaStream = %p", dstPtr, srcPtr,
                          sizeInBytes, (int)kind, cudaStream);
            }
        }
        else
        {
            CUDA_CALL(cudaMemcpy((void*)dstPtr, (void*)srcPtr, sizeInBytes, kind));
        }
    }
    else
    {
        memcpy((void*)dstPtr, (void*)srcPtr, sizeInBytes);
    }
}

} // namespace cuda
} // namespace sensors
} // namespace omni
