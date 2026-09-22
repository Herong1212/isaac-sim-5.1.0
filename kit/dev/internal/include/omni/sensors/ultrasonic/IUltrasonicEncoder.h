// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
#include <carb/dictionary/IDictionary.h>

#include <omni/Function.h>
#include <omni/String.h>
#include <omni/sensors/SensorBinFileHeaders.h>
#include <omni/sensors/SensorBinFileUtils.h>
#include <omni/sensors/ultrasonic/IUltrasonicCycleConverter.h>

#include <memory>
#include <string>

namespace omni
{
namespace sensors
{
namespace ultrasonic
{


enum MessageType : uint16_t
{
    MESSAGE_ENVELOPE = 0,
    MESSAGE_DIAGNOSTIC = 1,
    MESSAGE_END_RECORD = 255,
};

/**
 * @brief Structure encompassing the data produce by the encoder
 *
 */
struct SendData
{
    uint64_t timeStampNs{ 0 };
    uint64_t packetSize{ 0 };
    uint8_t* data{ nullptr };
    size_t dataSize{ 0 };

public:
    SendData() = default;

    SendData(const uint64_t inTimeStampNs, const uint64_t inPacketSize, uint8_t* dataIn, const size_t inDataSize)
    {
        dataSize = inDataSize;
        if (dataSize > 0)
        {
            data = (uint8_t*)malloc(inDataSize);
            memcpy(data, dataIn, dataSize);
        }
        timeStampNs = inTimeStampNs;
        packetSize = inPacketSize;
    }

    SendData(SendData&& orig) : SendData(orig.timeStampNs, orig.packetSize, orig.data, orig.dataSize)
    {
    }

    SendData(const SendData& orig) : SendData(orig.timeStampNs, orig.packetSize, orig.data, orig.dataSize)
    {
    }

    void resize(const size_t size)
    {
        if (data)
        {
            free(data);
            data = nullptr;
        }
        data = (uint8_t*)malloc(size);
        dataSize = size;
    }


    SendData& operator=(const SendData& other)
    {
        if (this == &other)
            return *this;
        this->timeStampNs = other.timeStampNs;
        this->packetSize = other.packetSize;
        this->dataSize = other.dataSize;
        if (this->data)
            free(this->data);
        this->data = (uint8_t*)malloc(dataSize);
        memcpy(this->data, other.data, dataSize);
        return *this;
    }

    SendData& operator=(SendData&& other)
    {
        if (this == &other)
            return *this;
        this->timeStampNs = other.timeStampNs;
        this->packetSize = other.packetSize;
        this->dataSize = other.dataSize;
        if (this->data)
            free(this->data);
        this->data = (uint8_t*)malloc(dataSize);
        memcpy(this->data, other.data, dataSize);
        return *this;
    }

    ~SendData()
    {
        if (data)
        {
            free(data);
        }
    };
};

struct USSEncoderCfg
{
    omni::string vendorStr{ "" };
    omni::string format{ "" };
    omni::string timestampMode{ "VENDOR" };
    float signalScaler{ 1.0 };
};

//-----------------------------------------------------------------------------
// Base class for all encoder with base utility -> Maybe re-write it to pure interface?
class IUltrasonicEncoder : public carb::IObject
{
public:
    virtual ~IUltrasonicEncoder(){};
    virtual void init(USSEncoderCfg* cfg) = 0;

    /**
     * @brief Process a new ProviderCycle and put into the send buffer queue
     *
     * @param outDataSize
     * @param pf
     * @param timestampNs
     * @param signalScaler
     * @param txBuf
     */
    virtual SendData* processNewData(size_t& outDataSize,
                                     const omni::sensors::GenericModelOutput& gpc,
                                     const uint64_t timestampNs,
                                     const float signalScaler,
                                     const MessageType type) = 0;
    /**
     * @brief Adds a DW bin file header to the channel description (for recording)
     *
     * @param header
     * @param dict
     * @param item
     * @param channelName
     */
    virtual void extendChannelDescWithHeader(const omni::sensors::USSBinFileHeader& header,
                                             carb::dictionary::IDictionary* dict,
                                             carb::dictionary::Item* item,
                                             const omni::string& channelName) = 0;

    /**
     * @brief Fill the DW bin file header with appropriate data
     *
     * @param header
     */
    virtual void fillBinFileHeader(sensors::USSBinFileHeader& header) = 0;
};

using IUltrasonicEncoderPtr = carb::ObjectPtr<IUltrasonicEncoder>;

/**
 * @brief an interface for a lidar pc converter factory
 *
 */
class IUltrasonicEncoderFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::ultrasonic::IUltrasonicEncoderFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual IUltrasonicEncoderPtr createInstance() = 0;
};


} // namespace ultrasonic
} // namespace sensors
} // namespace omni
