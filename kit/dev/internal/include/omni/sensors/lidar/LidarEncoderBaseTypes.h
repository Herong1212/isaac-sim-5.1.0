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


#include <carb/Defines.h>
#include <carb/tokens/TokensUtils.h>

#include <omni/String.h>
#include <omni/sensors/lidar/LidarProfileTypes.h>

#include <memory>

namespace omni
{
namespace sensors
{
namespace lidar
{

enum class ReturnType : uint8_t
{
    FIRST = 0,
    LAST = 1,
    STRONGEST = 2,
    MULTIPLE_RETURNS = 3,
    DUAL_LAST_STRONGEST = 4, // Dual modes are used for Hesai
    DUAL_LAST_FIRST = 5,
    DUAL_FIRST_STRONGEST = 6
};


struct CapsuleData
{
    CapsuleData() = default;
    CapsuleData(size_t size, int64_t inTimestamp)
    {
        capsule.resize(size);
        timestamp = inTimestamp;
    }

    uint8_t* data()
    {
        return capsule.data();
    }

    size_t size() const
    {
        return capsule.size();
    }

    int64_t timestamp{ 0 }; // can be us or ns depending on the packet
    std::vector<uint8_t> capsule;
};
using CapsuleDataPtr = std::shared_ptr<CapsuleData>;


struct LidarEncoderCfg
{
    LidarProfile* profile{ nullptr };
    omni::string ip{ "127.0.0.1" };
    omni::string ifaceIp{ "127.0.0.1" };
    int32_t port{ 0 };
    int32_t commandPort{ 0 };
    ReturnType returnType{ ReturnType::STRONGEST };
    omni::string encoderType{ "" };
    bool sendPackets{ true };
    bool dumpPackets{ false };
    uint32_t serviceId{ 0 };
    omni::string decoderPath{ "" };
    uint8_t numThreads{ 8 };
    uint32_t numPacketsPerScan{ 0 };
    uint32_t numTicksPerScan{ 0 };
    uint32_t deltaTimePerPacketNs{ 0 };
    uint32_t ticksPerPacket{ 1 }; // This is the minimum (VLS128 or HesaiP128 dual return)
    uint8_t numEchos{ 0 };
    float scanFrequency{ 0.f };
    omni::string fileName{ "" };
};


// Overload pattern to pass different lambdas into std::visit
template <class... Ts>
struct overload : Ts...
{
    using Ts::operator()...;
};
template <class... Ts>
overload(Ts...) -> overload<Ts...>;


inline ReturnType getReturnType(const std::string& returnTypeStr)
{
    // This will only be done once so the copy doesn't affect performance
    std::string lowerString{ returnTypeStr };
    std::transform(
        lowerString.begin(), lowerString.end(), lowerString.begin(), [](unsigned char c) { return std::tolower(c); });

    const uint64_t hash = carb::hashString(lowerString.c_str());

    ReturnType out{ ReturnType::FIRST };
    switch (hash)
    {
    case CARB_HASH_STRING("last"):
        out = ReturnType::LAST;
        break;

    case CARB_HASH_STRING("strongest"):
        out = ReturnType::STRONGEST;
        break;
    case CARB_HASH_STRING("multiple_returns"):
        out = ReturnType::MULTIPLE_RETURNS;
        break;
    case CARB_HASH_STRING("dual_last_strongest"):
        out = ReturnType::DUAL_LAST_STRONGEST;
        break;
    case CARB_HASH_STRING("dual_last_first"):
        out = ReturnType::DUAL_LAST_FIRST;
        break;
    case CARB_HASH_STRING("dual_first_strongest"):
        out = ReturnType::DUAL_FIRST_STRONGEST;
        break;
    case CARB_HASH_STRING("first"):
    default:
        out = ReturnType::FIRST;
        break;
    }
    return out;
}


} // namespace lidar
} // namespace sensors
} // namespace omni
