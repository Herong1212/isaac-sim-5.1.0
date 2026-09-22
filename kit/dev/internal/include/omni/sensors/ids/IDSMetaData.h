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
namespace ids
{

struct IDSMetaData
{
    std::size_t dataSize{ 0 };
    std::size_t numElements{ 0 };
    std::uint64_t startTimeNs{ 0 };
    std::uint64_t endTimeNs{ 0 };
    void* syncData{ nullptr }; // passing pointer to memhandler of model -- normally, not used except with frames in
                               // flight = 1
};


} // namespace ids
} // namespace sensors
} // namespace omni
