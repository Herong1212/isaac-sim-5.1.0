// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <carb/IObject.h>

#include <omni/String.h>
#include <omni/sensors/radar/IRadarPCConverter.h>

#include <cstdint>
#include <vector>

namespace omni
{
namespace sensors
{
namespace radar
{

struct EncoderBuffer
{

    void resize(const size_t size)
    {
        payloadSize = size;

        if (payloadSize <= maxPayloadSize)
            return;

        if (payload)
        {
            free(payload);
            payload = nullptr;
        }
        payload = (uint8_t*)malloc(payloadSize);
        maxPayloadSize = payloadSize;
    }

    ~EncoderBuffer()
    {
        if (payload)
        {
            free(payload);
            payload = nullptr;
        }
    }

    uint8_t* payload{ nullptr };
    size_t maxPayloadSize{ 0UL };
    size_t payloadSize{ 0UL };
    bool send{ false };
    uint64_t timeNs{ 0 };
};

enum class RadarPCProcessorType
{
    Encoder = 0,
    Consumer = 1
};

struct EncoderCfg
{
    size_t numBuffs{ 0UL };
    EncoderBuffer* txBuffs{ nullptr };
    uint16_t serviceID{ 0U };
    size_t numElements{ 0UL };
    int32_t* eventIDs{ nullptr };
    int32_t* eventTypes{ nullptr };
    int32_t* messageTypes{ nullptr };
};

struct RadarPCProcessorCfg
{
    RadarPCProcessorType type{ RadarPCProcessorType::Encoder };
    omni::string format{ "" };
    omni::string formatVersion{ "" };
    omni::string instance{ "" };
};

class IRadarPCProcessor : public carb::IObject
{
public:
    virtual ~IRadarPCProcessor()
    {
    }
    virtual void init(const RadarPCProcessorCfg& cfg, void* initData) = 0;
    virtual void ProcessNewData(GenericModelOutput& gmo) = 0;
    virtual void UpdateTxBuffs(EncoderBuffer* txBuffs, const size_t numBuffers) = 0;
    virtual uint16_t GetThreadRateHz() const = 0;
};

using IRadarPCProcessorPtr = carb::ObjectPtr<IRadarPCProcessor>;

/**
 * @brief an interface for a radar pc converter factory
 *
 */
class IRadarPCProcessorFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::radar::IRadarPCProcessorFactory", 0, 1)

    /**
     * @brief
     *
     * @return IRadarPCProcessorPtr
     */
    virtual IRadarPCProcessorPtr createInstance() = 0;
};


} // namespace radar
} // namespace sensors
} // namespace omni
