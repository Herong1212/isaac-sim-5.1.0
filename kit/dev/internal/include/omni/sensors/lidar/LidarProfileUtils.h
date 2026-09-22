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

#include "LidarProfileTypes.h"

#include <omni/sensors/cuda/CudaHelperDecl.h>


namespace omni
{
namespace sensors
{
namespace lidar
{

// Arrays need to be 8 byte aligned in order to work on GPU
#define ROUND_UP_TO_8(num) (((num) + 7) & ~7)

NV_HOSTDEVICE
inline void setPtrOfLidarProfile(LidarProfile* profile)
{
    uint8_t* buffer = reinterpret_cast<uint8_t*>(profile);
    size_t offset = ROUND_UP_TO_8(sizeof(LidarProfile));
    if (profile->intensityMapping.elCountEnc > 0)
    {
        profile->intensityMapping.encoding = reinterpret_cast<float*>(buffer + offset);
        offset += ROUND_UP_TO_8(sizeof(float) * profile->intensityMapping.elCountEnc);
    }
    if (profile->intensityMapping.elCountDec > 0)
    {
        profile->intensityMapping.decoding = reinterpret_cast<float*>(buffer + offset);
        offset += ROUND_UP_TO_8(sizeof(float) * profile->intensityMapping.elCountDec);
    }
    profile->emitterProfileSoA.azimuthDeg = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.elevationDeg = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.vertOffsetM = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.horOffsetM = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.distanceCorrectionM = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.focalDistM = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.focalSlope = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.fireTimeNs = reinterpret_cast<uint32_t*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.reportRateDiv = reinterpret_cast<uint32_t*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.bank = reinterpret_cast<uint32_t*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.channelId = reinterpret_cast<uint32_t*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.rangeId = reinterpret_cast<uint32_t*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    profile->emitterProfileSoA.isROI = reinterpret_cast<bool*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(bool) * profile->emitterStateCount * profile->numberOfEmitters);

    profile->emitterProfileSoA.minRange = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->rangeCount);
    profile->emitterProfileSoA.maxRange = reinterpret_cast<float*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(float) * profile->rangeCount);
    if (profile->numLines > 0)
    {
        profile->emitterProfileSoA.numRaysPerLine = reinterpret_cast<uint16_t*>(buffer + offset);
        offset += ROUND_UP_TO_8(sizeof(uint16_t) * profile->numLines);
    }
    profile->emitterProfileSoA.isROIState = reinterpret_cast<bool*>(buffer + offset);
    offset += ROUND_UP_TO_8(sizeof(bool) * profile->emitterStateCount);
    // offset += ROUND_UP_TO_8(sizeof(float) * profile->intensityMapping.elCountDec);
}

NV_HOSTDEVICE
inline LidarProfile* getLidarProfileFromBuffer(uint8_t* buffer)
{
    LidarProfile* profile = reinterpret_cast<LidarProfile*>(buffer);
    setPtrOfLidarProfile(profile);
    return profile;
}


inline uint64_t sizeOfLidarProfile(const uint32_t elCountEnc,
                                   const uint32_t elCountDec,
                                   const uint32_t emitterStateCount,
                                   const uint32_t numberOfEmitters,
                                   const uint32_t rangeCount,
                                   const uint32_t numLines)
{
    size_t dataSize = ROUND_UP_TO_8(sizeof(LidarProfile));

    dataSize += ROUND_UP_TO_8(sizeof(float) * elCountEnc); // encoding
    dataSize += ROUND_UP_TO_8(sizeof(float) * elCountDec); // decoding
    dataSize += ROUND_UP_TO_8(sizeof(float) * emitterStateCount * numberOfEmitters); // azimuthDeg
    dataSize += ROUND_UP_TO_8(sizeof(float) * emitterStateCount * numberOfEmitters); // elevationDeg
    dataSize += ROUND_UP_TO_8(sizeof(float) * emitterStateCount * numberOfEmitters); // vertOffsetM
    dataSize += ROUND_UP_TO_8(sizeof(float) * emitterStateCount * numberOfEmitters); // horizOffsetM
    dataSize += ROUND_UP_TO_8(sizeof(float) * emitterStateCount * numberOfEmitters); // distanceCorrectionM
    dataSize += ROUND_UP_TO_8(sizeof(float) * emitterStateCount * numberOfEmitters); // focalDistM
    dataSize += ROUND_UP_TO_8(sizeof(float) * emitterStateCount * numberOfEmitters); // focalSlope
    dataSize += ROUND_UP_TO_8(sizeof(uint32_t) * emitterStateCount * numberOfEmitters); // fireTimeNs
    dataSize += ROUND_UP_TO_8(sizeof(uint32_t) * emitterStateCount * numberOfEmitters); // reportRateDiv
    dataSize += ROUND_UP_TO_8(sizeof(uint32_t) * emitterStateCount * numberOfEmitters); // bank
    dataSize += ROUND_UP_TO_8(sizeof(uint32_t) * emitterStateCount * numberOfEmitters); // channelId
    dataSize += ROUND_UP_TO_8(sizeof(uint32_t) * emitterStateCount * numberOfEmitters); // rangeId
    dataSize += ROUND_UP_TO_8(sizeof(bool) * emitterStateCount * numberOfEmitters); // roi
    //
    dataSize += ROUND_UP_TO_8(sizeof(bool) * emitterStateCount);
    //
    dataSize += ROUND_UP_TO_8(sizeof(float) * rangeCount); // minRange for range interval
    dataSize += ROUND_UP_TO_8(sizeof(float) * rangeCount); // maxRange for range interval
    // maybe not filled
    dataSize += ROUND_UP_TO_8(sizeof(float) * numLines); // numRaysPerLine
    return dataSize;
}

inline uint64_t sizeOfLidarProfile(const LidarProfile* profile)
{
    return sizeOfLidarProfile(profile->intensityMapping.elCountEnc, profile->intensityMapping.elCountDec,
                              profile->emitterStateCount, profile->numberOfEmitters, profile->rangeCount,
                              profile->numLines);
}

inline void cpyProfileToBuffer(const LidarProfile* profile, void* buffer)
{
    memcpy(buffer, profile, sizeof(LidarProfile));
    LidarProfile* profileBuffer = reinterpret_cast<LidarProfile*>(buffer);
    // *profileBuffer = *profile;
    setPtrOfLidarProfile(profileBuffer);
    if (profile->intensityMapping.elCountEnc > 0)
    {
        memcpy(profileBuffer->intensityMapping.encoding, profile->intensityMapping.encoding,
               sizeof(float) * profile->intensityMapping.elCountEnc);
    }
    if (profile->intensityMapping.elCountDec > 0)
    {
        memcpy(profileBuffer->intensityMapping.decoding, profile->intensityMapping.decoding,
               sizeof(float) * profile->intensityMapping.elCountDec);
    }
    if(profile->emitterProfileSoA.azimuthDeg)
    {
        memcpy(profileBuffer->emitterProfileSoA.azimuthDeg, profile->emitterProfileSoA.azimuthDeg,
               sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.elevationDeg)
    {
        memcpy(profileBuffer->emitterProfileSoA.elevationDeg, profile->emitterProfileSoA.elevationDeg,
               sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.vertOffsetM)
    {
        memcpy(profileBuffer->emitterProfileSoA.vertOffsetM, profile->emitterProfileSoA.vertOffsetM,
           sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.horOffsetM)
    {
        memcpy(profileBuffer->emitterProfileSoA.horOffsetM, profile->emitterProfileSoA.horOffsetM,
               sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.distanceCorrectionM)
    {
        memcpy(profileBuffer->emitterProfileSoA.distanceCorrectionM, profile->emitterProfileSoA.distanceCorrectionM,
               sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.focalDistM)
    {
        memcpy(profileBuffer->emitterProfileSoA.focalDistM, profile->emitterProfileSoA.focalDistM,
               sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.focalSlope)
    {
        memcpy(profileBuffer->emitterProfileSoA.focalSlope, profile->emitterProfileSoA.focalSlope,
               sizeof(float) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.fireTimeNs)
    {
        memcpy(profileBuffer->emitterProfileSoA.fireTimeNs, profile->emitterProfileSoA.fireTimeNs,
               sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.reportRateDiv)
    {
        memcpy(profileBuffer->emitterProfileSoA.reportRateDiv, profile->emitterProfileSoA.reportRateDiv,
               sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.bank)
    {
        memcpy(profileBuffer->emitterProfileSoA.bank, profile->emitterProfileSoA.bank,
               sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.channelId)
    {
        memcpy(profileBuffer->emitterProfileSoA.channelId, profile->emitterProfileSoA.channelId,
               sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.rangeId)
    {
        memcpy(profileBuffer->emitterProfileSoA.rangeId, profile->emitterProfileSoA.rangeId,
               sizeof(uint32_t) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.isROI)
    {
        memcpy(profileBuffer->emitterProfileSoA.isROI, profile->emitterProfileSoA.isROI,
               sizeof(bool) * profile->emitterStateCount * profile->numberOfEmitters);
    }
    if(profile->emitterProfileSoA.minRange)
    {
        memcpy(profileBuffer->emitterProfileSoA.minRange, profile->emitterProfileSoA.minRange,
               sizeof(float) * profile->rangeCount);
    }
    if(profile->emitterProfileSoA.maxRange)
    {
        memcpy(profileBuffer->emitterProfileSoA.maxRange, profile->emitterProfileSoA.maxRange,
               sizeof(float) * profile->rangeCount);
    }
    if(profile->emitterProfileSoA.numRaysPerLine)
    {
        memcpy(profileBuffer->emitterProfileSoA.numRaysPerLine, profile->emitterProfileSoA.numRaysPerLine,
               sizeof(uint16_t) * profile->numLines);
    }
    if(profile->emitterProfileSoA.isROIState)
    {
        memcpy(profileBuffer->emitterProfileSoA.isROIState, profile->emitterProfileSoA.isROIState,
               sizeof(bool) * profile->emitterStateCount);
    }
}


} // namespace lidar
} // namespace sensors
} // namespace omni
