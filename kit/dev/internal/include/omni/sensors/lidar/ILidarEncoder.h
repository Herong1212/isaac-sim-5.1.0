// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//!
//! @brief LidarEncoder: This class encodes lidar buffer to packets
//! plugin


#pragma once

#include <carb/IObject.h>

#include <omni/Function.h>
#include <omni/sensors/SensorBinFileHeaders.h>
#include <omni/sensors/lidar/LidarEncoderBaseTypes.h>

#include <memory>
#include <string>

namespace omni
{
namespace sensors
{
namespace lidar
{

//-----------------------------------------------------------------------------
// Base class for all encoder with base utility -> Maybe re-write it to pure interface?
class ILidarEncoder : public carb::IObject
{
public:
    virtual ~ILidarEncoder(){};
    virtual void init(LidarEncoderCfg* encoderParameter) = 0;
    virtual CapsuleDataPtr* processNewData(size_t& outDataSize,
                                           uint8_t* lidarData,
                                           const size_t dataSize,
                                           const omni::function<int64_t(const int64_t&)>& timeCallback) = 0;
    virtual void fillBinFileHeader(omni::sensors::LidarBinFileHeader& header) = 0;
    virtual void getPODTrackHeaderData(void* trackHeaderData) = 0;
    virtual uint32_t getNumPacketsForDeltaTimeNs(int64_t deltaTimeNs) = 0;
};

using ILidarEncoderPtr = carb::ObjectPtr<ILidarEncoder>;

/**
 * @brief an interface for a lidar pc converter factory
 *
 */
class ILidarEncoderFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::lidar::ILidarEncoderFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual ILidarEncoderPtr createInstance() = 0;
};


} // namespace lidar
} // namespace sensors
} // namespace omni
