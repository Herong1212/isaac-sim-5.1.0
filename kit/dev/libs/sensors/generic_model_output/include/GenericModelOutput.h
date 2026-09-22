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

#include "GMOAuxiliaryData.h"
#include "GenericModelOutputTypes.h"

#include <omni/sensors/cuda/CudaHelperMem.h>

#include <cstdint>

namespace omni::sensors
{


NV_HOSTDEVICE
constexpr inline size_t sizeBasics()
{
    // use full struct type so that we can assign the pointer directly inside the buffer
    return sizeof(GenericModelOutput);

    // Non-pointer attributes : majorVersion, minorVersion, patchVersion, numElements, frameId, timestampNs,
    // frameOfReference, CoordsType, frameStart, frameEnd, auxType
}

NV_HOSTDEVICE
inline GenericModelOutput* castBufferIfValid(void* inData, const char* callerString = "castBufferIfValid")
{
    GenericModelOutput* modelOutput{ reinterpret_cast<GenericModelOutput*>(inData) };
    if (modelOutput->magicNumber != MAGIC_NUMBER_GMO)
    {
        printf("%s:: GMO magic number is not correct: %u\n", callerString, modelOutput->magicNumber);
        modelOutput = nullptr;
    }
    else
    {
        if ((modelOutput->majorVersion != 1U && modelOutput->majorVersion != 2U) || modelOutput->minorVersion != 0U ||
            modelOutput->patchVersion != 0U)
        {
            printf("%s:: GMO version is not supported: (%u,%u,%u)\n", callerString, modelOutput->majorVersion,
                   modelOutput->minorVersion, modelOutput->patchVersion);
            modelOutput = nullptr;
        }
    }

    return modelOutput;
}

NV_HOSTDEVICE
inline size_t sizeInBytes(const GenericModelOutput& output)
{
    size_t size{ 0LU };
    GenericModelOutput* modelOutput = castBufferIfValid((void*)&output, "sizeInBytes");
    if (modelOutput)
    {
        // Basics
        size = sizeBasics();
        // numElements specific
        // basic elements
        size += (sizeof(int32_t) + sizeof(float) * 4 + sizeof(uint8_t)) * output.numElements;
        // Padding to 8byte alignment
        if (size % 8 != 0)
        {
            size += 8 - (size % 8);
        }

        // aux elements
        if (output.auxType != AuxType::NONE)
        {
            if (output.modality == Modality::LIDAR)
            {
                size += sizeLidarAuxiliaryData(output);
            }
            else if (output.modality == Modality::USS)
            {
                size += sizeUSSAuxiliaryData(output);
            }
            else if (output.modality == Modality::RADAR)
            {
                size += sizeRadarAuxiliaryData(output);
            }
            else if (output.modality == Modality::IDS)
            {
                size += sizeIDSAuxiliaryData(output);
            }
        }
    }
    return size;
}

/**
 * @brief Get the Base GMO Ptr From Buffer object, it also prepares all base GMO pointers, to point to subsequent
 * contiguous memory regions in the buffer
 *
 * @param inData pointer to raw buffer
 * @return GenericModelOutput* pointer to a prepared base GMO
 */

NV_HOSTDEVICE
inline GenericModelOutput* getBaseGMOPtrFromBuffer(void* inData)
{
    GenericModelOutput* modelOutput = castBufferIfValid(inData, "getBaseGMOPtrFromBuffer");
    if (modelOutput)
    {
        uint8_t* data = reinterpret_cast<uint8_t*>(inData);
        size_t offset{ sizeBasics() };
        // Basic elements
        modelOutput->elements.timeOffsetNs = reinterpret_cast<int32_t*>(data + offset);
        offset += sizeof(int32_t) * modelOutput->numElements;
        modelOutput->elements.x = reinterpret_cast<float*>(data + offset);
        offset += sizeof(float) * modelOutput->numElements;
        modelOutput->elements.y = reinterpret_cast<float*>(data + offset);
        offset += sizeof(float) * modelOutput->numElements;
        modelOutput->elements.z = reinterpret_cast<float*>(data + offset);
        offset += sizeof(float) * modelOutput->numElements;
        modelOutput->elements.scalar = reinterpret_cast<float*>(data + offset);
        offset += sizeof(float) * modelOutput->numElements;
        modelOutput->elements.flags = reinterpret_cast<uint8_t*>(data + offset);
        offset += sizeof(uint8_t) * modelOutput->numElements;
        // Padding to 8byte alignment
        if (offset % 8 != 0)
        {
            offset += 8 - (offset % 8);
        }
        modelOutput->auxiliaryData =
            modelOutput->auxType == AuxType::NONE ? nullptr : reinterpret_cast<void*>(data + offset);
    }

    return modelOutput;
}

NV_HOSTDEVICE
inline void setBufferAuxiliaryData(void* inData)
{
    GenericModelOutput* modelOutput = castBufferIfValid(inData, "setAuxiliaryDataToPC");
    if (modelOutput && modelOutput->auxType != AuxType::NONE)
    {
        // aux elements
        if (modelOutput->modality == Modality::LIDAR)
        {
            setLidarAuxiliaryDataToPC(modelOutput);
        }
        else if (modelOutput->modality == Modality::USS)
        {
            setUSSAuxiliaryDataToPC(modelOutput);
        }
        else if (modelOutput->modality == Modality::RADAR)
        {
            setRadarAuxiliaryDataToPC(modelOutput);
        }
        else if (modelOutput->modality == Modality::IDS)
        {
            setIDSAuxiliaryDataToPC(modelOutput);
        }
    }
}

NV_HOSTDEVICE
inline GenericModelOutput* getModelOutputPtrFromBuffer(void* inData)
{
    GenericModelOutput* modelOutput = castBufferIfValid(inData, "getModelOutputPtrFromBuffer");
    if (modelOutput)
    {
        getBaseGMOPtrFromBuffer(inData);
        setBufferAuxiliaryData(inData);
    }

    return modelOutput;
}

NV_HOSTDEVICE
inline GenericModelOutput getModelOutputFromBuffer(void* inData)
{
    GenericModelOutput result;
    result.magicNumber = 0;
    auto modelOutput = getModelOutputPtrFromBuffer(inData);
    if (modelOutput)
    {
        result = *modelOutput;
    }
    return result;
}

NV_HOSTDEVICE inline size_t offsetToFlags(const uint32_t numElements,
                                          const uint32_t major,
                                          const uint32_t minor,
                                          const uint32_t patch)
{
    size_t result{ 0UL };
    if (major == 1U && minor == 0U && patch == 0U)
    {
        result = sizeBasics() + sizeof(int32_t) * numElements + sizeof(float) * 4 * numElements;
    }
    else
    {
        printf("offsetToFlags:: GMO version is not supported: (%u,%u,%u)\n", major, minor, patch);
    }
    return result;
}


inline void cpyGMOToGMO(GenericModelOutput& dst,
                        const GenericModelOutput& src,
                        const int cudaDevice = -1,
                        const cudaStream_t stream = 0)
{
    GenericModelOutput* modelOutput = castBufferIfValid((void*)&src, "cpyGMOToGMO");
    if (modelOutput)
    {
        cudaPointerAttributes srcAttrs;
        cudaPointerAttributes dstAttrs;
        cudaPointerGetAttributes(&srcAttrs, src.elements.x);
        cudaPointerGetAttributes(&dstAttrs, dst.elements.x);
        if (srcAttrs.type == cudaMemoryTypeUnregistered)
        {
            printf("Source GPC should be allocated via CudaMalloc\n");
            std::terminate();
        }
        if (dstAttrs.type == cudaMemoryTypeUnregistered)
        {
            printf("Destination GPC should be allocated via CudaMalloc\n");
            std::terminate();
        }

        cudaMemcpyKind kind;

        if (srcAttrs.type == cudaMemoryTypeHost)
        {
            if (dstAttrs.type == cudaMemoryTypeHost)
            {
                kind = cudaMemcpyHostToHost;
            }
            else
            {
                kind = cudaMemcpyHostToDevice;
            }
        }
        else
        {
            if (dstAttrs.type == cudaMemoryTypeHost)
            {
                kind = cudaMemcpyDeviceToHost;
            }
            else
            {
                kind = cudaMemcpyDeviceToDevice;
            }
        }

        dst.auxType = src.auxType;
        dst.frameId = src.frameId;
        dst.timestampNs = src.timestampNs;
        dst.frameOfReference = src.frameOfReference;
        dst.elementsCoordsType = src.elementsCoordsType;
        dst.frameStart = src.frameStart;
        dst.frameEnd = src.frameEnd;
        dst.numElements = src.numElements;

        size_t sizeInBytes = sizeof(float) * src.numElements;

        omni::sensors::cuda::cpyMem((void*)dst.elements.x, (void*)src.elements.x, sizeInBytes, kind, cudaDevice, stream);
        omni::sensors::cuda::cpyMem((void*)dst.elements.y, (void*)src.elements.y, sizeInBytes, kind, cudaDevice, stream);
        omni::sensors::cuda::cpyMem((void*)dst.elements.z, (void*)src.elements.z, sizeInBytes, kind, cudaDevice, stream);
        omni::sensors::cuda::cpyMem(
            (void*)dst.elements.scalar, (void*)src.elements.scalar, sizeInBytes, kind, cudaDevice, stream);
        omni::sensors::cuda::cpyMem(
            (void*)dst.elements.timeOffsetNs, (void*)src.elements.timeOffsetNs, sizeInBytes, kind, cudaDevice, stream);
        sizeInBytes = sizeof(uint8_t) * src.numElements;
        omni::sensors::cuda::cpyMem(
            (void*)dst.elements.flags, (void*)src.elements.flags, sizeInBytes, kind, cudaDevice, stream);

        if (src.auxType != AuxType::NONE)
        {
            switch (src.modality)
            {
            case Modality::LIDAR:
            {
                sizeInBytes = sizeLidarAuxiliaryData(src);
                break;
            }
            case Modality::USS:
            {
                sizeInBytes = sizeUSSAuxiliaryData(src);
                break;
            }
            case Modality::RADAR:
            {
                sizeInBytes = sizeRadarAuxiliaryData(src);
                break;
            }
            case Modality::IDS:
            {
                sizeInBytes = sizeIDSAuxiliaryData(src);
                break;
            }
            case Modality::UNDEFINED:
            default:
            {
                sizeInBytes = 0;
            }
            }
        }
        else
        {
            sizeInBytes = 0;
        }

        if (sizeInBytes > 0)
        {
            omni::sensors::cuda::cpyMem(dst.auxiliaryData, src.auxiliaryData, sizeInBytes, kind, cudaDevice, stream);
        }
    }
}

inline void cpyGMOToBuffer(uint8_t* buffer,
                           const omni::sensors::GenericModelOutput* gpc,
                           const bool bufferOnHost = true, // not needed for cpu only
                           const bool pointerOnHost = true, // not needed for cpu only
                           const int32_t cudaDevice = -1, // not needed for cpu only
                           const cudaStream_t stream = 0) // not needed for cpu only
{
    GenericModelOutput* modelOutput = castBufferIfValid((void*)gpc, "cpyGMOToBuffer");
    if (modelOutput)
    {
        cudaMemcpyKind kind;
        cudaMemcpyKind soaKind;
        if (bufferOnHost)
        {
            if (pointerOnHost)
            {
                kind = cudaMemcpyHostToHost;
                soaKind = cudaMemcpyHostToHost;
            }
            else
            {
                kind = cudaMemcpyDeviceToHost;
                soaKind = cudaMemcpyHostToHost;
            }
        }
        else
        {
            if (pointerOnHost)
            {
                kind = cudaMemcpyHostToDevice;
                soaKind = cudaMemcpyHostToDevice;
            }
            else
            {
                kind = cudaMemcpyDeviceToDevice;
                soaKind = cudaMemcpyHostToDevice;
            }
        }
        size_t offset{ 0 };
        size_t sizeInBytes{ sizeBasics() };
        omni::sensors::cuda::cpyMem((void*)buffer, (void*)gpc, sizeInBytes, soaKind, cudaDevice, stream);
        offset += sizeInBytes;
        // Basic elements
        sizeInBytes = sizeof(int32_t) * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(gpc->elements.timeOffsetNs), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
        sizeInBytes = sizeof(float) * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(gpc->elements.x), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(gpc->elements.y), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(gpc->elements.z), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(gpc->elements.scalar), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
        sizeInBytes = sizeof(uint8_t) * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(gpc->elements.flags), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
        // Padding to 8byte alignment
        if (offset % 8 != 0)
        {
            offset += 8 - (offset % 8);
        }
        // aux elements
        if (gpc->auxType != AuxType::NONE)
        {
            if (gpc->modality == Modality::LIDAR)
            {
                cpyLidAuxToBuffer(buffer, gpc, offset, soaKind, kind, cudaDevice, stream);
            }
            else if (gpc->modality == Modality::USS)
            {
                cpyUSSAuxToBuffer(buffer, gpc, offset, soaKind, kind, cudaDevice, stream);
            }
            else if (gpc->modality == Modality::RADAR)
            {
                cpyRadarAuxToBuffer(buffer, gpc, offset, soaKind, kind, cudaDevice, stream);
            }
            else if (gpc->modality == Modality::IDS)
            {
                cpyIDSAuxToBuffer(buffer, gpc, offset, soaKind, kind, cudaDevice, stream);
            }
        }
    }
}


// Enum conversion helper
inline CoordsType getCoordsTypeFromString(const char* coordsString)
{
    CoordsType coordsType{ CoordsType::SPHERICAL };
    if (coordsString)
    {
        if (strcmp(coordsString, "SPHERICAL") == 0)
        {
            coordsType = omni::sensors::CoordsType::SPHERICAL;
        }
        else if (strcmp(coordsString, "CARTESIAN") == 0)
        {
            coordsType = omni::sensors::CoordsType::CARTESIAN;
        }
        else
        {
            printf("Unknown output coords type: %s\n", coordsString);
        }
    }
    return coordsType;
}

inline FrameOfReference getFrameOfReferenceFromString(const char* frameString)
{
    FrameOfReference frameOfReference{ FrameOfReference::SENSOR };
    if (frameString)
    {
        if (strcmp(frameString, "SENSOR") == 0)
        {
            frameOfReference = omni::sensors::FrameOfReference::SENSOR;
        }
        else if (strcmp(frameString, "WORLD") == 0)
        {
            frameOfReference = omni::sensors::FrameOfReference::WORLD;
        }
        else if (strcmp(frameString, "CUSTOM") == 0)
        {
            frameOfReference = omni::sensors::FrameOfReference::CUSTOM;
        }
        else if (strcmp(frameString, "PARENT") == 0)
        {
            frameOfReference = omni::sensors::FrameOfReference::PARENT;
        }
        else
        {
            printf("Unknown output frame of reference: %s\n", frameString);
        }
    }
    return frameOfReference;
}

inline MotionCompensationState getMotionCompensationStateFromString(const char* frameString)
{
    MotionCompensationState frameOfReference{ MotionCompensationState::NOT_APPLICABLE };
    if (frameString)
    {
        if (strcmp(frameString, "COMPENSATED") == 0)
        {
            frameOfReference = omni::sensors::MotionCompensationState::COMPENSATED;
        }
        else if (strcmp(frameString, "NONCOMPENSATED") == 0)
        {
            frameOfReference = omni::sensors::MotionCompensationState::NONCOMPENSATED;
        }
        else if (strcmp(frameString, "NOT_APPLICABLE") == 0)
        {
            frameOfReference = omni::sensors::MotionCompensationState::NOT_APPLICABLE;
        }
        else
        {
            printf("Unknown output motion compensation state: %s wow\n", frameString);
        }
    }
    return frameOfReference;
}

} // namespace omni::sensors
