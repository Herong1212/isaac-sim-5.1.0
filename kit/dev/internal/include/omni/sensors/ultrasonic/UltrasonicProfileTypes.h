// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#include <cuda_runtime.h>
#include <vector>

namespace omni
{
namespace sensors
{
namespace nv
{
namespace ultrasonic
{

enum SignalMode : uint8_t
{
    MODE_CHIRP = 0,
    MODE_AM = 1,
};

struct SensorMount
{
    float3 pos;
    float4 pose;
};

struct TxCfg
{
    uint64_t timeNs;
    uint8_t txId;
    uint8_t rxGroupId;
    uint8_t ch;
};

struct FiringCycle
{
    std::vector<TxCfg> txCfgs;
};

struct RxGroup
{
    std::vector<uint8_t> idxs;
};

struct UltrasonicProfile
{
    float AzSpanDeg;
    float ElSpanDeg;
    float membraneDiameter;
    float centerFrequency;
    float bandwidth;
    float pulseDuration;
    float pulsePower;
    float sampleDuration;
    float closeRange;
    float closeRangeDecay;
    float closeIndirectAmplBase;
    float closeDirectAmplBase;
    float closeIndirectAmpl;
    float closeDirectAmpl;
    float noiseMin;
    float noiseMax;
    float directivityStepH;
    float directivityStepV;
    std::vector<float> gainCoeffs;
    std::vector<float> directivityTableH;
    std::vector<float> directivityTableV;
    std::vector<float> directivityCoeffs;
    uint8_t raysPerDeg;
    uint8_t traceTreeDepth;
    std::vector<FiringCycle> firingSequnce;
    std::vector<SensorMount> sensorMounts;
    std::vector<RxGroup> rxGroups;
    SignalMode signalMode;
};

} // namespace ultrasonic
} // namespace nv
} // namespace sensors
} // namespace omni
