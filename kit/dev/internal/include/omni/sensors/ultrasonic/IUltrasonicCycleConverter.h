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

#include <carb/Interface.h>

#include <GenericModelOutput.h>
#include <cstdint>

namespace omni
{
namespace sensors
{
namespace ultrasonic
{

static constexpr int NUM_SENSORS = 12;
static constexpr int SGWS_PER_CYCLE = 16;
static constexpr int MAX_NUM_SAMPLES_ENVELOPE = 320;

/**
  \brief Defines the return structure for a single uss signalway
 */
struct SignalWay
{
    float samples[MAX_NUM_SAMPLES_ENVELOPE];
    uint64_t timestampNs;
    uint16_t numSamples;
    uint8_t txSensorID;
    uint8_t rxSensorID;
    uint8_t channel;
};

struct ProviderMetadata
{
    float sensorMounts[NUM_SENSORS * 3];
    float sensorOrientations[NUM_SENSORS * 3];
    void* syncData;
    void* taskingCounter;
    uint64_t bufferSize;
};

/**
 * @brief an interface for uss point cloud converter
 *
 */
class IUltrasonicCycleConverter
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::ultrasonic::IUltrasonicCycleConverter", 0, 1)

    /**
     * @brief converts ultrasonic output raw buffer (raw AOV) to a point cloud
     *
     * @param buffer raw ultrasonic output buffer (AOV)
     * @return GenericPointCloud Generic point cloud initialized with data from the buffer
     */
    omni::sensors::GenericModelOutput(CARB_ABI* convertBuffer)(void* buffer);
};

} // namespace ultrasonic
} // namespace sensors
} // namespace omni
