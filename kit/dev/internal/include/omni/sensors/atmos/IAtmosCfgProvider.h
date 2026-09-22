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

#include "AtmosCfg.h"

#include <carb/IObject.h>

#include <cstdint>

namespace omni
{
namespace sensors
{
namespace atmos
{

/**
 * IAtmosCfgProvider, calculates the atmosphere configuration based on mie scattergin
 */
class IAtmosCfgProvider : public carb::IObject
{
public:
    virtual ~IAtmosCfgProvider(){};

    /**
     * calculate atmos config
     */
    virtual WeatherCfg calcWeatherCfg(const float rainRate,
                                      const float waveLengthNm,
                                      const uint32_t numSteps,
                                      const float alpha = 2.f,
                                      const float beta = 10.f) const = 0;

    virtual AerosolCfg calcAerosolCfg(const float waveLengthNm,
                                      const uint32_t numSteps,
                                      const float alpha = 2.f,
                                      const float beta = 10.f,
                                      const float aerosolModel = -1.f) const = 0;

    virtual void calcRefrIndexOfWater(float& real, float& imag, const float waveLengthNm) const = 0;
};

/**
 * @brief a carb object pointer for an object that implements the IAtmosCfgProvider interface
 *
 */
using IAtmosCfgProviderPtr = carb::ObjectPtr<IAtmosCfgProvider>;

} // namespace atmos
} // namespace sensors
} // namespace omni
