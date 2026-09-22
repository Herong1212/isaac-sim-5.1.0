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
#include <vector>

namespace omni
{
namespace sensors
{
namespace atmos
{

//-----------------------------------------------------------------------------
constexpr uint32_t kMaxNumAerosolAngles = 19;
struct MieCfg
{
    float g{ 0.f }; // the average cosine of the scattering phase function
    float Qext{ 0.f }; // mie extinction efficiency
    float Qsca{ 0.f }; // mie scattering efficiency
    float Qbsca{ 0.f }; // mie backscattering efficiency per unit
    float S1{ 0.f }; // Scattering function polarization in perpendicular plane
    float S2{ 0.f }; // Scattering function polarization in parallel plane
    float gammaExt{ 0.f }; // precalculated integrated extinction (integration of dsd over possible rain drop sizes)
    float backScatter{ 0.f }; // cross scattering based value per unit volume ( sum_dropsize sigma_sca * number_of_drops
                              // )
    float betaFValue{ 0.f }; // pre calculated Beta function value for alpha and beta parameter
    float alpha{ 2.f }; // alpha parameter of the beta distribution
    float beta{ 10.f }; // beta parameter of the beta distribution
};
struct ParticulateCfg
{
    float sigma{ 0.f }; // std deviation of rain drop parameter
    float Dg{ 0.f }; // geometric mean of diameter of drop size in mm
    float dropSizeMin{ 0.1f }; // min drop size in mm
    float dropSizeMax{ 9.f }; // max drop size in mm
    float Nt{ 0.f }; // drop number per unit volume in m^3
};
struct WeatherCfg
{
    MieCfg mieCfg; // details for the Mie parameters based from weather
    ParticulateCfg particulateCfg; // details of the particulates based from weather
    float R{ 0.f }; // rain intensity in mm/h (e.g., 0.098 mm/h) // TODO change to m?
};
struct AerosolCfg
{
    MieCfg mieCfg[kMaxNumAerosolAngles]; // details for the Mie parameters based from aerosols
    MieCfg largeCfg[kMaxNumAerosolAngles]; // details for the Mie parameters based from weather
    ParticulateCfg particulateCfg[kMaxNumAerosolAngles]; // details of the particulates based from aerosols
    ParticulateCfg largeParticleCfg[kMaxNumAerosolAngles]; // details of the large particulates based from aerosols
    float celestialLookVector[3]; // sun look vector in world space
    float celestialLookVectorLocal[3]; // sun look vector in sensor local space
    float backgroundIrradiance[kMaxNumAerosolAngles]; // computed background irradiances in W/m^2
    float directIrradiance{ 0.f }; // direct solar irradiance contribution in w/m^2
    float directIrradianceFraction{ 1.f }; // Fractional coverage of direct solar contributions
    float directIrradAngleThreshold{ 0.f }; // angle extent of celestial body (sun) in rad
};
struct AtmosCfg
{
    WeatherCfg weatherCfg; // weather configuration
    AerosolCfg aerosolCfg; // aerosol configuration
};

} // namespace atmos
} // namespace sensors
} // namespace omni
