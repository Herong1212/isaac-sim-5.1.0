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

//! @file
//!
//! @brief Factory to instantiate point cloud converter utility

#include <carb/Interface.h>
#include <carb/ObjectUtils.h>

#include <omni/String.h>
#include <omni/sensors/lidar/LidarProfileTypes.h>

#include <GenericModelOutput.h>


namespace omni
{
namespace sensors
{
namespace lidar
{

/**
 * @brief LidarGPCConverterMode -- describes the conversion mode
 *
 */
enum class LidarPCConverterMode
{
    GENERIC = 0,
    GENERIC_FILE = 1,
    PACKETS = 2
};

/**
 * @brief LidarPCConverterRunMode -- describes the run mode of the conversion
 *
 */
enum class LidarPCConverterRunMode
{
    CPU = 0, /**< converts on host */
    GPU = 1, /**< converts on device */
};

struct Transformation
{
    FrameOfReference desiredFrameOfReference{ FrameOfReference::SENSOR };
    MotionCompensationState desiredMotionCompensationState{ MotionCompensationState::NONCOMPENSATED };
    float interpolationFactor{ 1.0f };
    FrameAtTime pose{}; //
    // maybe to be removed
    FrameAtTime frameStart{};
    FrameAtTime frameEnd{};
};

struct LidarPCConverterCfg
{
    LidarPCConverterMode mode{ LidarPCConverterMode::GENERIC };
    LidarPCConverterRunMode runMode{ LidarPCConverterRunMode::CPU };
    omni::sensors::CoordsType desiredCoordsType{ CoordsType::SPHERICAL };
    bool outputOnGPU{ false };
    uint32_t maxPoints{ 0U };
    // Only needed for hdf5 file reading
    omni::string fileName{ "" };
    omni::string groupName{ "" };
    omni::string clientName{ "" };
    bool syncMode{ false }; // no async processing
    float constantValue{ 0.f };
    uint32_t scanFrequencyHz{ 10U };
    // only needed for packet conversion
    omni::string profileName{ "" };
};


class ILidarPCConverter : public carb::IObject
{
public:
    virtual ~ILidarPCConverter(){};

    virtual void init(const LidarPCConverterCfg& cfg) = 0;
    // For instance, for live post-processing
    virtual void convertBuffer(uint8_t* sensorBuffer,
                               const size_t dataSize,
                               const uint32_t numPoints,
                               const bool scanComplete,
                               void* inCudaStream = nullptr) = 0;
    virtual omni::sensors::GenericModelOutput* getPointCloud(void* stream = nullptr) = 0;
    // File reading of generic point cloud -- passing a frame means no accumulation
    virtual bool convertBuffer(const int frameId = -1) = 0;
    virtual void setTransformation(omni::sensors::lidar::Transformation& transformation, void* stream) = 0;
    virtual void setTransformation(const FrameOfReference desiredFrameOfReference,
                                   const MotionCompensationState desiredMotionCompensationState,
                                   float interpolationFactor,
                                   void* stream) = 0;
    virtual void setStaticTransformation(const float* pos, const float* rpyDeg, void* stream) = 0;

    // Packets specific
    virtual uint32_t getMaxPoints() const = 0;
    virtual void convertPacket(char* dwPacket, char* lidarBinFileHeader, const uint64_t headerDataSize = 0) = 0;
    virtual bool isPacketOfNewScan(char* dwPacket) = 0;
    virtual size_t sizeOfVendorPacket() const = 0;
    virtual uint64_t getPacketTime(char* dwPacket) = 0;
};

/**
 * @brief a carb object pointer for an object that implements the ILidarPCConverter interface
 *
 */
using ILidarPCConverterPtr = carb::ObjectPtr<ILidarPCConverter>;


/**
 * @brief an interface for a lidar pc converter factory
 *
 */
class ILidarPCConverterFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::lidar::ILidarPCConverterFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual ILidarPCConverterPtr createInstance() = 0;
};

} // namespace lidar
} // namespace sensors
} // namespace omni
