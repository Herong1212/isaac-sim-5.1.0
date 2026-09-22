// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/Types.h>

// Avoid including USD Headers as they come from UsdPCH.h included in .cpp files
PXR_NAMESPACE_OPEN_SCOPE
class UsdPrim;
PXR_NAMESPACE_CLOSE_SCOPE

namespace omni
{
namespace usd
{
namespace hydra
{

struct Transform
{
    carb::Double3 position;
    carb::Float4 orientation;
    carb::Float3 scale;
};

struct TimestampedTransform
{
    int64_t wakeupTimeNumerator;
    uint64_t wakeupTimeDenominator;
    int64_t sampleTimeNumerator;
    uint64_t sampleTimeDenominator;

    bool transformPresent;
    omni::usd::hydra::Transform transform;
};

struct BufferDesc
{
    BufferDesc() = default;
    BufferDesc(const void* _data, uint32_t _elementStride, uint32_t _elementSize)
        : data(_data), elementStride(_elementStride), elementSize(_elementSize)
    {
    }
    const void* data = nullptr; // float elements, vec2, vec3 or vec4
    uint32_t elementStride = 0; // in bytes
    uint32_t elementSize = 0; // in bytes

    size_t count = 0; // vertex count, ...
    bool isGPUBuffer = false; // TODO - add GPU interop later
    bool isSafeToRender = false; // true if the data is safe to use from the render thread
    bool isDataRpResource = false;
};

using SkelMeshGraphCallback = void(*)(const pxr::UsdPrim&);

} // namespace hydra
} // namespace usd
} // namespace omni
