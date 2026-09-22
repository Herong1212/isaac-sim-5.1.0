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

// ASCI code for NGMO
static const uint32_t MAGIC_NUMBER_GMO = 0x4E474D4F;
#pragma pack(push, 1) // Make sure we have consistent structure packing

struct FrameAtTime
{
    uint64_t timestampNs{ 0UL };
    float orientation[4];
    float posM[3];
    uint8_t padding[4];
};

enum class FrameOfReference : uint16_t
{
    SENSOR = 0,
    WORLD = 1,
    CUSTOM = 2,
    PARENT = 3,
};

enum class MotionCompensationState : uint16_t
{
    NONCOMPENSATED = 0,
    COMPENSATED = 1, // Needed for lidar but could also be auxiliary
    NOT_APPLICABLE = 2
};

enum class CoordsType : uint32_t
{
    CARTESIAN = 0,
    SPHERICAL = 1, // x,y,z of BasicPoints contains: azimuth, elevation, distance
    NOT_APPLICABLE = 2 // Pixels?
};

enum ElementFlags : uint8_t
{
    FLAG_1 = 0,
    FLAG_2 = 1 << 0,
    FLAG_3 = 1 << 1,
    FLAG_4 = 1 << 2,
    FLAG_5 = 1 << 3,
    FLAG_6 = 1 << 4,
    FLAG_7 = 1 << 5,
    VALID = 1 << 6,
};

struct BasicElements
{
    int32_t* timeOffsetNs{ nullptr }; // Time offset from the start of the point cloud
    float* x{ nullptr }; // azimuth in degree [-180,180] or cartesian x in m
    float* y{ nullptr }; // elevation in degree or cartesian y in m
    float* z{ nullptr }; // distance in m or cartesian z in m
    float* scalar{ nullptr }; // sensor specific scalar
    uint8_t* flags{ nullptr }; // sensor specific flags
};


enum class OutputType : uint32_t
{
    POINTCLOUD = 0 // For now only coint cloud is supported
};

enum class AuxType : uint32_t
{
    NONE = 0,
    BASIC = 1,
    EXTRA = 2,
    FULL = 3
};

enum class Modality : uint32_t
{
    UNDEFINED = 0,
    LIDAR = 1,
    RADAR = 2,
    USS = 3,
    IDS = 4
};

struct GenericModelOutput
{
    uint32_t magicNumber{ MAGIC_NUMBER_GMO };
    uint32_t majorVersion{ 1 };
    uint32_t minorVersion{ 0 };
    uint32_t patchVersion{ 0 };
    uint64_t sizeInBytes{ 0UL };
    uint32_t numElements{ 0 };
    FrameOfReference frameOfReference{ FrameOfReference::SENSOR }; // 2bytes
    MotionCompensationState motionCompensationState{ MotionCompensationState::NOT_APPLICABLE }; // 2bytes
    uint64_t frameId{ 0 };
    uint64_t timestampNs{ 0 };
    CoordsType elementsCoordsType{ CoordsType::SPHERICAL };
    OutputType outputType{ OutputType::POINTCLOUD };
    float modelToAppTransform[16];
    FrameAtTime frameStart;
    FrameAtTime frameEnd;
    AuxType auxType{ AuxType::NONE };
    Modality modality{ Modality::UNDEFINED };
    BasicElements elements{}; // Always filled
    //
    void* auxiliaryData{ nullptr }; // Potentially not filled
};

#pragma pack(pop)

} // namespace omni::sensors
