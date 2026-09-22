// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <omni/sensors/cuda/CudaHelperMath.h>

#include <cstdint>
#include <memory>
#include <vector>

namespace omni
{
namespace sensors
{

#pragma pack(push, 1)

enum ObjectType : uint8_t
{
    POINT = 0,
    LINE = 1,
    BBOX = 2,
    USS_VIZ = 3,
    TRANSFORM = 4,
    CONTROL_PACKET = 5,
    IMAGE = 6,
};

enum ColorMapType : uint8_t
{
    CONTINUOUS = 0,
    STEP = 1,
    HARD_CODED = 2,
};

struct Point
{
    float3 pos;
    float value;
};

struct Line
{
    float3 start;
    float3 end;
    union
    {
        float value;
        uchar4 color;
    };
};

struct BBox
{
    // 0 - back top left, 1 - back top right, 2 - back bottom left, 3 - back bottom right, 4 - front top left, 5 - front
    // top right, 6 - front bottom left, 7 - front bottom right
    float3 corner[8];
    float value;
};

struct Transform
{
    float4 r0;
    float4 r1;
    float4 r2;
    float4 r3;
};

struct CommonPacketHeader // keep synchronized with BufferData struct to ensure binary compatibility
{
    uint32_t numObjects{ 0 };
    uint8_t objectType{ 0 };
};

struct BufferData
{
    uint32_t numObjects{ 0 };
    uint8_t objectType{ 0 };
    ColorMapType colorMapType{ 0 };
    uint8_t dataId{ 0 };
    float maxValue{ 1.f };
    uint32_t maxObjects{ 0 };
    uint64_t timeStampNs{ 0 };
    void* data{ nullptr };
};

enum ControlPacketType : uint8_t
{
    QUERY = 0,
    INFO = 1,
    PARAMETER_INFO = 2,
    PARAMETER_CHANGE = 3,
};

struct ControlPacketHeader
{
    CommonPacketHeader commonHeader{ 0, ObjectType::CONTROL_PACKET };
    ControlPacketType packetType{ 0 };
    uint8_t dataId{ 0 }; // Depending on packet type either receiver or sender
};

struct ControlPacketQuery
{
    ControlPacketHeader header{ { 0, ObjectType::CONTROL_PACKET }, ControlPacketType::QUERY };
};

struct ControlPacketInfo
{
    ControlPacketHeader header{ { 0, ObjectType::CONTROL_PACKET }, ControlPacketType::INFO };
    char name[255]; // Name of the viz provider
    uint32_t realmProcessIdx; // Realm process index of the viz provider
};

enum ControlPacketParameterType : uint8_t
{
    FLOAT = 0,
    UINT32 = 1,
    INT32 = 2,
    BOOL = 3,
    ACTION = 4,
    OPTION = 5,
};

struct ControlPacketParameterInfo
{
    ControlPacketHeader header{ { 0, ObjectType::CONTROL_PACKET }, ControlPacketType::PARAMETER_INFO };
    uint8_t parameterId{ 0 }; // Sensor/viz provider internal id of the settable parameter
    ControlPacketParameterType parameterType{ 0 }; // Type of the settable parameter
    char name[255]; // Name of the settable parameter
    union // Current parameter value
    {
        float valueFloat;
        uint32_t valueUInt32;
        int32_t valueInt32;
        bool valueBool;
    };
    uint32_t numOptions{ 0 }; // Number of options for OPTION type parameters
    char optionList[16][255]; // List of options for OPTION type parameters
};

struct ControlPacketParameterChange
{
    ControlPacketHeader header{ { 0, ObjectType::CONTROL_PACKET }, ControlPacketType::PARAMETER_CHANGE };
    uint8_t parameterId{ 0 }; // Sensor/viz provider internal id of the settable parameter
    union // Actual value the parameter should be set to
    {
        float valueFloat;
        uint32_t valueUInt32;
        int32_t valueInt32;
        bool valueBool;
    };
};


namespace visualizer
{
enum ImagePacketPixelSemanticType : uint8_t
{
    eRGB,
    eRGBA,
    eRGGB,
};

enum ImagePacketDataType : uint8_t
{
    eUINT8,
    eUINT16,
    eFLOAT16,
    eFLOAT32,
};
} // namespace visualizer

struct ImagePacketHeader
{
    CommonPacketHeader commonHeader{ 0, ObjectType::IMAGE };
    // Note: next two lines to keep in sync with BufferData struct
    ColorMapType colorMapType{ 0 };
    uint8_t dataId{ 0 };
    char name[200];
    visualizer::ImagePacketDataType dataType{ 0 };
    visualizer::ImagePacketPixelSemanticType pixelSemanticType{ 0 };
    uint32_t width{ 0 };
    uint32_t height{ 0 };
    uint64_t timeStampNs{ 0 };
    void* data{ nullptr };
};


#pragma pack(pop)

inline size_t dataSize(const uint32_t numObjects, const ObjectType type)
{
    size_t size{ 0 };
    if (type == ObjectType::POINT)
    {
        size = sizeof(uint32_t) + sizeof(uint8_t) + sizeof(uint8_t) + sizeof(uint8_t) + sizeof(float) +
               sizeof(uint64_t) + sizeof(uint32_t) + numObjects * sizeof(Point);
    }
    else if (type == ObjectType::LINE)
    {
        size = sizeof(uint32_t) + sizeof(uint8_t) + sizeof(uint8_t) + sizeof(uint8_t) + sizeof(float) +
               sizeof(uint64_t) + sizeof(uint32_t) + numObjects * sizeof(Line);
    }
    else if (type == ObjectType::BBOX)
    {
        size = sizeof(uint32_t) + sizeof(uint8_t) + sizeof(uint8_t) + sizeof(uint8_t) + sizeof(float) +
               sizeof(uint64_t) + sizeof(uint32_t) + numObjects * sizeof(BBox);
    }
    return size;
}

} // namespace sensors
} // namespace omni
