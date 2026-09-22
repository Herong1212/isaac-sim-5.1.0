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
namespace radar
{

static constexpr uint16_t MAX_DETS_PER_SCAN = 2500;
static constexpr size_t PC_PACKED_SIZE = 64 + MAX_DETS_PER_SCAN * 32;

// #pragma pack(push, 1)


struct RadarPointCloudMetadata
{
    void* syncData; /**< contains Sync primitives for syncing with model */
    void* taskingCounter; /**< a tasking counter for async cpu work */
    uint64_t bufferSize; /**< Size of the point cloud buffer */
};

/**
  \brief Represents debug data the optionally trails the pointcloud
 */
struct DebugData
{
    uint16_t numRBins;
    uint16_t numVBins;
    uint32_t cfarSize;
    float* cfar;
};

// #pragma pack(pop)

/**
 * @brief an interface for radar point cloud converter
 *
 */
class IRadarPCConverter
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::radar::IRadarPCConverter", 0, 1)

    /**
     * @brief converts radar output raw buffer (raw AOV) to a point cloud
     *
     * @param buffer raw radar output buffer (AOV)
     * @return RadarPointCloudPtr radar point cloud object pointer
     */
    omni::sensors::GenericModelOutput(CARB_ABI* convertBuffer)(void* buffer);

    /**
     * @brief gets debug data struct from a radar raw buffer
     *
     * @param buffer raw radar output buffer (AOV)
     * @return RadarPointCloudPtr radar point cloud object pointer
     */
    DebugData*(CARB_ABI* getDebugData)(void* buffer);
};

} // namespace radar
} // namespace sensors
} // namespace omni
