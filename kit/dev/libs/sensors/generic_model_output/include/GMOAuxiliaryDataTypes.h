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

#include <cstdint>

namespace omni::sensors
{


#pragma pack(push, 1) // Make sure we have consistent structure packing

////////////// Lidar //////////////////////
// Only fill whats desired
enum class LidarAuxHas : uint32_t
{
    NONE = 0,
    EMITTER_ID = 1 << 0,
    CHANNEL_ID = 1 << 1,
    ECHO_ID = 1 << 2,
    MAT_ID = 1 << 3,
    OBJ_ID = 1 << 4,
    TICK_ID = 1 << 5,
    TICK_STATES = 1 << 6,
    HIT_NORMALS = 1 << 7,
    VELOCITIES = 1 << 8
};


struct LidarAuxiliaryData
{
    uint32_t scanComplete{ 0U };
    float azimuthOffset{ 0.f }; // Offset to +x in degrees
    LidarAuxHas filledAuxMembers{ static_cast<LidarAuxHas>(0U) };
    uint8_t padding[4];
    uint32_t* emitterId{ nullptr };
    uint32_t* channelId{ nullptr };
    uint32_t* matId{ nullptr };
    uint32_t* tickId{ nullptr };
    // Tick azimuth = pointazimuth - emitter azimuth
    // Tick timestamp = pointtimestamp - emitter timestamp

    // Not necessarily filled
    float* hitNormals{ nullptr }; // Stride 3
    float* velocities{ nullptr };
    //
    uint8_t* objId{ nullptr }; // Stride 16 -> 128bit stable id
    uint8_t* echoId{ nullptr };
    uint8_t* tickStates{ nullptr };
};

////////////// USS //////////////////////

struct USSAuxiliaryData
{
    uint32_t numSgws;
    uint32_t numSamplesPerSgw;
};

////////////// Radar //////////////////////

struct RadarAuxiliaryData
{
    uint8_t sensorID; /**< Sensor Id for sensor that generated the scan */
    uint8_t scanIdx; /**< Scan index for sensors with multi scan support */
    uint8_t padding[6];
    uint64_t cycleCnt; /**< Scan cycle count (unique per scan idx) */
    float maxRangeM; /**< The max unambiguous range for the scan */
    float minVelMps; /**< The min unambiguous velocity for the scan */
    float maxVelMps; /**< The max unambiguous velocity for the scan */
    float minAzRad; /**< The min unambiguous azimuth for the scan */
    float maxAzRad; /**< The max unambiguous azimuth for the scan */
    float minElRad; /**< The min unambiguous elevation for the scan */
    float maxElRad; /**< The max unambiguous elevation for the scan */
    uint8_t padding2[4];
    float* rv_ms{ nullptr }; /**< Radial velocity (m/s), always filled */
};

////////////// IDS //////////////////////

// Only fill whats desired
enum class IDSAuxHas : uint32_t
{
    NONE = 0,
    VELOCITIES = 1 << 0
};

struct IDSAuxiliaryData
{
    uint32_t numRows{ 0 };
    uint32_t numCols{ 0 };
    float minColUnit{ 0.f }; /**< Minimum col unit of the specified fov */
    float maxColUnit{ 0.f }; /**< Maximum col unit of the specified fov */
    float minRowUnit{ 0.f }; /**< Minimum row unit of the specified fov */
    float maxRowUnit{ 0.f }; /**< Minimum row unit of the specified fov */
    float emitterCfgOriginX{ 0.f }; /**< Origin of emitter config */
    float emitterCfgOriginY{ 0.f }; /**< Origin of emitter config */
    float emitterCfgOriginZ{ 0.f }; /**< Origin of emitter config */
    int emitterGenType{ 0 };
    float elementSize{ 0.f }; /**< Maximum size of spatial element to generate */
    float radius{ 0.f }; /**< Radius at which elementSize is defined */
    IDSAuxHas filledAuxMembers{ static_cast<IDSAuxHas>(0U) };
    uint8_t padding[4]; // Padding bytes to have 64bit alignment
    float* originX{ nullptr };
    float* originY{ nullptr };
    float* originZ{ nullptr };
    uint32_t* objectId{ nullptr };
    uint32_t* materialId{ nullptr };
    float* velocities{ nullptr }; /**< Stride 3, not necessarily filled */
};

#pragma pack(pop)

} // namespace omni::sensors
