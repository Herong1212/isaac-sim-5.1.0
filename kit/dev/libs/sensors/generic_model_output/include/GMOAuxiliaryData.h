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

#include "GMOAuxiliaryDataTypes.h"
#include "GenericModelOutputTypes.h"
#include <omni/sensors/cuda/CudaHelperMem.h>

#include <cstdint>

namespace omni::sensors
{

////////////// Lidar //////////////////////
NV_HOSTDEVICE
inline LidarAuxHas operator|(LidarAuxHas lhs, LidarAuxHas rhs)
{
    return static_cast<LidarAuxHas>(static_cast<std::underlying_type<LidarAuxHas>::type>(lhs) |
                                    static_cast<std::underlying_type<LidarAuxHas>::type>(rhs));
}

NV_HOSTDEVICE
inline LidarAuxHas operator&(LidarAuxHas lhs, LidarAuxHas rhs)
{
    return static_cast<LidarAuxHas>(static_cast<std::underlying_type<LidarAuxHas>::type>(lhs) &
                                    static_cast<std::underlying_type<LidarAuxHas>::type>(rhs));
}


//// Helper functions
NV_HOSTDEVICE
inline size_t sizeLidarAuxiliaryData(const GenericModelOutput& pointCloud) noexcept
{
    auto lidAux = reinterpret_cast<LidarAuxiliaryData*>(pointCloud.auxiliaryData);
    // use fill size with pointer so that we can reset it without having to malloc pointer values
    size_t size{ sizeof(LidarAuxiliaryData) };


    if ((lidAux->filledAuxMembers & LidarAuxHas::EMITTER_ID) == LidarAuxHas::EMITTER_ID)
    {
        size += sizeof(uint32_t) * pointCloud.numElements;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::CHANNEL_ID) == LidarAuxHas::CHANNEL_ID)
    {
        size += sizeof(uint32_t) * pointCloud.numElements;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::ECHO_ID) == LidarAuxHas::ECHO_ID)
    {
        size += sizeof(uint8_t) * pointCloud.numElements;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::MAT_ID) == LidarAuxHas::MAT_ID)
    {
        size += sizeof(uint32_t) * pointCloud.numElements;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::OBJ_ID) == LidarAuxHas::OBJ_ID)
    {
        size += sizeof(uint8_t) * pointCloud.numElements * 16;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::TICK_ID) == LidarAuxHas::TICK_ID)
    {
        size += sizeof(uint32_t) * pointCloud.numElements;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::TICK_STATES) == LidarAuxHas::TICK_STATES)
    {
        size += sizeof(uint8_t) * pointCloud.numElements;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::HIT_NORMALS) == LidarAuxHas::HIT_NORMALS)
    {
        size += sizeof(float) * 3 * pointCloud.numElements;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::VELOCITIES) == LidarAuxHas::VELOCITIES)
    {
        size += sizeof(float) * pointCloud.numElements * 3;
    }
    return size;
}

NV_HOSTDEVICE
inline void setLidarAuxiliaryDataToPC(omni::sensors::GenericModelOutput* pointCloud) noexcept
{
    uint8_t* data = reinterpret_cast<uint8_t*>(pointCloud->auxiliaryData);
    LidarAuxiliaryData* auxData = reinterpret_cast<LidarAuxiliaryData*>(pointCloud->auxiliaryData);
    size_t offset{ sizeof(LidarAuxiliaryData) };
    if ((auxData->filledAuxMembers & LidarAuxHas::EMITTER_ID) == LidarAuxHas::EMITTER_ID)
    {
        auxData->emitterId = reinterpret_cast<uint32_t*>(data + offset);
        offset += sizeof(uint32_t) * pointCloud->numElements;
    }
    else
    {
        auxData->emitterId = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::CHANNEL_ID) == LidarAuxHas::CHANNEL_ID)
    {
        auxData->channelId = reinterpret_cast<uint32_t*>(data + offset);
        offset += sizeof(uint32_t) * pointCloud->numElements;
    }
    else
    {
        auxData->channelId = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::MAT_ID) == LidarAuxHas::MAT_ID)
    {
        auxData->matId = reinterpret_cast<uint32_t*>(data + offset);
        offset += sizeof(uint32_t) * pointCloud->numElements;
    }
    else
    {
        auxData->matId = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::TICK_ID) == LidarAuxHas::TICK_ID)
    {
        auxData->tickId = reinterpret_cast<uint32_t*>(data + offset);
        offset += sizeof(uint32_t) * pointCloud->numElements;
    }
    else
    {
        auxData->tickId = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::HIT_NORMALS) == LidarAuxHas::HIT_NORMALS)
    {
        auxData->hitNormals = reinterpret_cast<float*>(data + offset);
        offset += sizeof(float) * 3 * pointCloud->numElements;
    }
    else
    {
        auxData->hitNormals = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::VELOCITIES) == LidarAuxHas::VELOCITIES)
    {
        auxData->velocities = reinterpret_cast<float*>(data + offset);
        offset += sizeof(float) * pointCloud->numElements * 3;
    }
    else
    {
        auxData->velocities = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::OBJ_ID) == LidarAuxHas::OBJ_ID)
    {
        auxData->objId = reinterpret_cast<uint8_t*>(data + offset);
        offset += sizeof(uint8_t) * pointCloud->numElements * 16;
    }
    else
    {
        auxData->objId = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::ECHO_ID) == LidarAuxHas::ECHO_ID)
    {
        auxData->echoId = reinterpret_cast<uint8_t*>(data + offset);
        offset += sizeof(uint8_t) * pointCloud->numElements;
    }
    else
    {
        auxData->echoId = nullptr;
    }

    if ((auxData->filledAuxMembers & LidarAuxHas::TICK_STATES) == LidarAuxHas::TICK_STATES)
    {
        auxData->tickStates = reinterpret_cast<uint8_t*>(data + offset);
        offset += sizeof(uint8_t) * pointCloud->numElements;
    }
    else
    {
        auxData->tickStates = nullptr;
    }
}

inline void cpyLidAuxToBuffer(uint8_t* buffer,
                              const omni::sensors::GenericModelOutput* gpc,
                              size_t& offset,
                              const cudaMemcpyKind soaKind,
                              const cudaMemcpyKind kind,
                              const int32_t cudaDevice = -1,
                              const cudaStream_t stream = 0)
{
    size_t sizeInBytes{ sizeof(LidarAuxiliaryData) };
    auto lidAux = reinterpret_cast<LidarAuxiliaryData*>(gpc->auxiliaryData);
    omni::sensors::cuda::cpyMem((void*)(buffer + offset), (void*)(lidAux), sizeInBytes, soaKind, cudaDevice, stream);
    offset += sizeInBytes;
    sizeInBytes = sizeof(uint32_t) * gpc->numElements;
    if ((lidAux->filledAuxMembers & LidarAuxHas::EMITTER_ID) == LidarAuxHas::EMITTER_ID)
    {
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->emitterId), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::CHANNEL_ID) == LidarAuxHas::CHANNEL_ID)
    {
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->channelId), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::MAT_ID) == LidarAuxHas::MAT_ID)
    {
        sizeInBytes = sizeof(uint32_t) * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->matId), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::TICK_ID) == LidarAuxHas::TICK_ID)
    {
        sizeInBytes = sizeof(uint32_t) * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->tickId), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::HIT_NORMALS) == LidarAuxHas::HIT_NORMALS)
    {
        sizeInBytes = sizeof(float) * 3 * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->hitNormals), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::VELOCITIES) == LidarAuxHas::VELOCITIES)
    {
        sizeInBytes = sizeof(float) * 3 * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->velocities), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::OBJ_ID) == LidarAuxHas::OBJ_ID)
    {
        sizeInBytes = sizeof(uint8_t) * gpc->numElements * 16;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->objId), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::ECHO_ID) == LidarAuxHas::ECHO_ID)
    {
        sizeInBytes = sizeof(uint8_t) * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->echoId), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
    if ((lidAux->filledAuxMembers & LidarAuxHas::TICK_STATES) == LidarAuxHas::TICK_STATES)
    {
        sizeInBytes = sizeof(uint8_t) * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(lidAux->tickStates), sizeInBytes, kind, cudaDevice, stream);
        offset += sizeInBytes;
    }
}

////////////// USS //////////////////////

NV_HOSTDEVICE
inline size_t sizeUSSAuxiliaryData(const GenericModelOutput& pointCloud) noexcept
{
    return sizeof(USSAuxiliaryData);
}

NV_HOSTDEVICE
inline void cpyUSSAuxToBuffer(uint8_t* buffer,
                              const omni::sensors::GenericModelOutput* gpc,
                              size_t& offset,
                              const cudaMemcpyKind soaKind,
                              const cudaMemcpyKind kind,
                              const int32_t cudaDevice = -1,
                              const cudaStream_t stream = 0)
{
    size_t sizeInBytes{ sizeof(USSAuxiliaryData) };
    auto ussAux = reinterpret_cast<USSAuxiliaryData*>(gpc->auxiliaryData);

    omni::sensors::cuda::cpyMem((void*)(buffer + offset), (void*)(ussAux), sizeInBytes, soaKind, cudaDevice, stream);
}


NV_HOSTDEVICE
inline void setUSSAuxiliaryDataToPC(omni::sensors::GenericModelOutput* pointCloud) noexcept
{
    // uint8_t* data = reinterpret_cast<uint8_t*>(pointCloud->auxiliaryData);
    // USSAuxiliaryData* auxData = reinterpret_cast<USSAuxiliaryData*>(pointCloud->auxiliaryData);
    // size_t offset {sizeof(USSAuxiliaryData)};
}

////////////// Radar //////////////////////

NV_HOSTDEVICE
inline size_t sizeRadarAuxiliaryData(const GenericModelOutput& pointCloud) noexcept
{
    size_t size{ sizeof(RadarAuxiliaryData) };

    // Add sizes of arrays in aux data
    size += sizeof(float) * pointCloud.numElements; // rv_ms is always filled

    return size;
}

NV_HOSTDEVICE
inline void cpyRadarAuxToBuffer(uint8_t* buffer,
                                const omni::sensors::GenericModelOutput* gpc,
                                size_t& offset,
                                const cudaMemcpyKind soaKind,
                                const cudaMemcpyKind kind,
                                const int32_t cudaDevice = -1,
                                const cudaStream_t stream = 0)
{
    size_t sizeInBytes{ sizeof(RadarAuxiliaryData) };
    auto radarAux = reinterpret_cast<RadarAuxiliaryData*>(gpc->auxiliaryData);

    omni::sensors::cuda::cpyMem((void*)(buffer + offset), (void*)(radarAux), sizeInBytes, soaKind, cudaDevice, stream);
    offset += sizeInBytes;

    // Copy velocity which is not optional
    sizeInBytes = sizeof(float) * gpc->numElements;
    omni::sensors::cuda::cpyMem(
        (void*)(buffer + offset), (void*)(radarAux->rv_ms), sizeInBytes, kind, cudaDevice, stream);
    offset += sizeInBytes;
}

NV_HOSTDEVICE
inline void setRadarAuxiliaryDataToPC(omni::sensors::GenericModelOutput* pointCloud) noexcept
{
    uint8_t* data = reinterpret_cast<uint8_t*>(pointCloud->auxiliaryData);
    RadarAuxiliaryData* auxData = reinterpret_cast<RadarAuxiliaryData*>(pointCloud->auxiliaryData);
    size_t offset{ sizeof(RadarAuxiliaryData) };

    auxData->rv_ms = reinterpret_cast<float*>(data + offset);
    offset += sizeof(float) * pointCloud->numElements;
}

////////////// IDS //////////////////////

NV_HOSTDEVICE
inline IDSAuxHas operator|(IDSAuxHas lhs, IDSAuxHas rhs)
{
    return static_cast<IDSAuxHas>(static_cast<std::underlying_type<IDSAuxHas>::type>(lhs) |
                                  static_cast<std::underlying_type<IDSAuxHas>::type>(rhs));
}

NV_HOSTDEVICE
inline IDSAuxHas operator&(IDSAuxHas lhs, IDSAuxHas rhs)
{
    return static_cast<IDSAuxHas>(static_cast<std::underlying_type<IDSAuxHas>::type>(lhs) &
                                  static_cast<std::underlying_type<IDSAuxHas>::type>(rhs));
}

NV_HOSTDEVICE
inline size_t sizeIDSAuxiliaryData(const GenericModelOutput& pointCloud) noexcept
{
    auto idsAux = reinterpret_cast<IDSAuxiliaryData*>(pointCloud.auxiliaryData);
    size_t size{ sizeof(IDSAuxiliaryData) };
    // Origin x, y, z
    size += sizeof(float) * pointCloud.numElements * 3;
    // Object id
    size += sizeof(uint32_t) * pointCloud.numElements;
    // Mat id
    size += sizeof(uint32_t) * pointCloud.numElements;
    // Velocities (if enabled)
    if ((idsAux->filledAuxMembers & IDSAuxHas::VELOCITIES) == IDSAuxHas::VELOCITIES)
    {
        size += sizeof(float) * pointCloud.numElements * 3;
    }
    return size;
}


NV_HOSTDEVICE
inline void cpyIDSAuxToBuffer(uint8_t* buffer,
                              const omni::sensors::GenericModelOutput* gpc,
                              size_t& offset,
                              const cudaMemcpyKind soaKind,
                              const cudaMemcpyKind kind,
                              const int32_t cudaDevice = -1,
                              const cudaStream_t stream = 0)
{
    size_t sizeInBytes{ sizeof(IDSAuxiliaryData) };
    auto idsAux = reinterpret_cast<IDSAuxiliaryData*>(gpc->auxiliaryData);
    omni::sensors::cuda::cpyMem((void*)(buffer + offset), (void*)(idsAux), sizeInBytes, soaKind, cudaDevice, stream);
    offset += sizeInBytes;
    sizeInBytes = sizeof(float) * gpc->numElements;
    omni::sensors::cuda::cpyMem(
        (void*)(buffer + offset), (void*)(idsAux->originX), sizeInBytes, kind, cudaDevice, stream);
    offset += sizeInBytes;
    omni::sensors::cuda::cpyMem(
        (void*)(buffer + offset), (void*)(idsAux->originY), sizeInBytes, kind, cudaDevice, stream);
    offset += sizeInBytes;
    omni::sensors::cuda::cpyMem(
        (void*)(buffer + offset), (void*)(idsAux->originZ), sizeInBytes, kind, cudaDevice, stream);
    offset += sizeInBytes;
    sizeInBytes = sizeof(uint32_t) * gpc->numElements;
    omni::sensors::cuda::cpyMem(
        (void*)(buffer + offset), (void*)(idsAux->objectId), sizeInBytes, kind, cudaDevice, stream);
    offset += sizeInBytes;
    omni::sensors::cuda::cpyMem(
        (void*)(buffer + offset), (void*)(idsAux->materialId), sizeInBytes, kind, cudaDevice, stream);
    offset += sizeInBytes;
    if ((idsAux->filledAuxMembers & IDSAuxHas::VELOCITIES) == IDSAuxHas::VELOCITIES)
    {
        sizeInBytes = sizeof(float) * 3 * gpc->numElements;
        omni::sensors::cuda::cpyMem(
            (void*)(buffer + offset), (void*)(idsAux->velocities), sizeInBytes, kind, cudaDevice, stream);

        offset += sizeInBytes;
    }
}

NV_HOSTDEVICE
inline void setIDSAuxiliaryDataToPC(omni::sensors::GenericModelOutput* pointCloud) noexcept
{
    uint8_t* data = reinterpret_cast<uint8_t*>(pointCloud->auxiliaryData);
    IDSAuxiliaryData* auxData = reinterpret_cast<IDSAuxiliaryData*>(pointCloud->auxiliaryData);
    size_t offset{ sizeof(IDSAuxiliaryData) };

    auxData->originX = reinterpret_cast<float*>(data + offset);
    offset += sizeof(float) * pointCloud->numElements;
    auxData->originY = reinterpret_cast<float*>(data + offset);
    offset += sizeof(float) * pointCloud->numElements;
    auxData->originZ = reinterpret_cast<float*>(data + offset);
    offset += sizeof(float) * pointCloud->numElements;
    auxData->objectId = reinterpret_cast<uint32_t*>(data + offset);
    offset += sizeof(uint32_t) * pointCloud->numElements;
    auxData->materialId = reinterpret_cast<uint32_t*>(data + offset);
    offset += sizeof(uint32_t) * pointCloud->numElements;
    if ((auxData->filledAuxMembers & IDSAuxHas::VELOCITIES) == IDSAuxHas::VELOCITIES)
    {
        auxData->velocities = reinterpret_cast<float*>(data + offset);
        offset += sizeof(float) * pointCloud->numElements * 3;
    }
}


///////////// OTHER SENSORS /////////////////


} // namespace omni::sensors
