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

#include <omni/Vector.h>

#include <cstdint>

namespace omni::sensors
{

struct TimedDataBuffer
{
    int64_t timestampNs{ -1 }; // negative means invalid
    omni::vector<uint8_t> dataBuffer;
};

} // namespace omni::sensors
