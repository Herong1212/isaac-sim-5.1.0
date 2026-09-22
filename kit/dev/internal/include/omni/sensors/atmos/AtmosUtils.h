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

#include <omni/sensors/cuda/CudaHelperMath.h>

namespace omni
{
namespace sensors
{
namespace atmos
{

NV_HOSTDEVICE
inline float getTransmissionFactor(const float gammaExt, const float distance)
{
    return expf(-gammaExt * distance);
}

//-----------------------------------------------------------------------------
/**
 * calculate the background Irradiance from the sun into a sensor.
 * cfg - the Mie and particulate data pertaining to aerosols for computing the scattered component
 * lookVec - the look direction towards the center of the celestial body (e.g. the sun)
 * incDir - The incident direction of a fired ray
 * angleIndex - the returned angle index given the number of angle segments between the lookVec and incDir
 */
NV_HOSTDEVICE
inline float computeBackgroundIrradianceForDirection(const AerosolCfg& cfg,
                                                     const float3& lookVec,
                                                     const float3& incDir,
                                                     uint8_t& angleIndex)
{
    float cosTheta = dot(lookVec, incDir);
    float theta = fmaxf(fminf(acosf(cosTheta), PI), 0.f);
    float thetaIndex = theta * (omni::sensors::atmos::kMaxNumAerosolAngles - 1) / PI;
    float fraction = fracf(thetaIndex);
    angleIndex = static_cast<uint8_t>(thetaIndex);

    // Compute the scattered contribution from pre angle segments of aerosol scattered Irradiance
    float backgroundIrrad = 0.f;
    if (angleIndex >= (omni::sensors::atmos::kMaxNumAerosolAngles - 1))
        backgroundIrrad = cfg.backgroundIrradiance[angleIndex];
    else
    {
        backgroundIrrad = (1.f - fraction) * cfg.backgroundIrradiance[angleIndex] +
                          (fraction)*cfg.backgroundIrradiance[angleIndex + 1];
    }

    // Direct Irradiances are on the order of 1e5 - 1e6. The factor in the exponential ensures
    // that the background direct irradiance sufficiently falls off as a function of angle and
    // prescribed threshold.
    backgroundIrrad +=
        cfg.directIrradiance * expf(-14.f * theta / cfg.directIrradAngleThreshold) * cfg.directIrradianceFraction;

    return backgroundIrrad;
}

template <typename T>
inline T interpolate(std::vector<T>& x, std::vector<T>& y, const T& eval)
{
    T interpolate = 0.f;
    for (uint16_t i = 0; i < y.size(); ++i)
    {
        T numerator = 1.f;
        T denominator = 1.f;
        for (uint16_t j = 0; j < x.size(); ++j)
        {
            if (i == j)
                continue;
            numerator *= eval - x[j];
            denominator *= x[i] - x[j];
        }
        interpolate += numerator * y[i] / denominator;
    }
    return interpolate;
}


} // namespace atmos
} // namespace sensors
} // namespace omni
