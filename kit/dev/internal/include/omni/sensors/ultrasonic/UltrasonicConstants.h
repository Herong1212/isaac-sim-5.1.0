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

namespace omni
{
namespace sensors
{
namespace ultrasonic
{

/**
 * @brief Speed of sound (m/s)
 * Speed of sound at normal conditions (P = 101.5 kPa, T = 293.15 K)
 */
static constexpr float SPEED_OF_SOUND = 343.21f;

/**
 * @brief Air density (kg/m^3)
 * Density of air at normal conditions (P = 101.5 kPa, T = 293.15 K)
 */
static constexpr float AIR_DENSITY = 1.2041f;

/**
 * @brief Air impedance (kg/(m^2 * s))
 * Impedance of air at normal conditions
 */
static constexpr float AIR_IMPEDANCE = SPEED_OF_SOUND * AIR_DENSITY;

} // namespace ultrasonic
} // namespace sensors
} // namespace omni
