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

namespace omni
{
namespace sensors
{
namespace lidar
{

// #pragma pack(push, 1) // Make sure we have consistent structure packing

struct LidarMetaData
{
    uint64_t dataSize{ 0 };
    uint64_t numPoints{ 0 };
    uint64_t maxPoints{ 0 };
    uint64_t scanStartTimeNs{ 0 };
    uint64_t startTimeNs{ 0 };
    uint64_t endTimeNs{ 0 };
    bool scanComplete{ false };
    void* syncHandler{ nullptr }; // passing pointer to memhandler of model -- normally, not used except with frames in
                                  // flight = 1
};

// #pragma pack(pop)


} // namespace lidar
} // namespace sensors
} // namespace omni
