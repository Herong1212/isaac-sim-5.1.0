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

//! @file
//!
//! @brief Types and helper functions for beams utility

#include <omni/sensors/cuda/CudaHelperDecl.h>
#include <omni/sensors/cuda/CudaHelperMath.h>
#include <omni/sensors/materials/MaterialDefines.h>
#include <rtx/rtsensor/RtxSensorModel.h>

#include <cstdint>

namespace omni
{
namespace sensors
{
namespace beams
{


#pragma pack(push, 1)

//! 1 central base ray -- 4 secondary waist rays -- 4 secondary divergence rays
constexpr const uint32_t NUM_RAYS_PER_BEAM = 9;


enum BeamTypes
{
    GAUSSIAN = 0,
    UNIFORM = 1,
    NUM_ELEMENTS = 2
};

/**
 * @brief Beam waist parameter.
 */
struct BeamWaist
{
    float horizM{ 0.f }; /**< Horizontal beam waist in meter */
    float vertM{ 0.f }; /**< Vertical beam waist in meter */
};

/**
 * @brief Beam divergence parameter.
 */
struct BeamDivergence
{
    float horizRad{ 0.f }; /**< Horizontal beam divergence in rad */
    float vertRad{ 0.f }; /**< Vertical beam divergence in rad */
};

/**
 * @brief Rayleigh range of beam.
 */
struct RayleighRange
{
    float horizM{ 0.f }; /**< Horizontal Rayleigh range in meter */
    float vertM{ 0.f }; /**< Vertical Rayleigh range in meter */
};

struct BaseConfig
{
    BeamTypes beamType{ BeamTypes::GAUSSIAN };
    uint32_t maxNumBeams{ 0 }; /**< Maximum expected number of beams in the simulation */
    float waveLengthNm{ 0.f }; /**< Wave length of emitter in nanometer */
    float Msquared{ 1.f }; /**< beam quality parameter */
    uint32_t sizeCustomInRayProps{ sizeof(omni::sensors::materials::NvMatRayProps) }; /**< Data size of custom input ray
                                                                                         properties */
    uint32_t sizeCustomOutRayProps{ sizeof(omni::sensors::materials::NvMatRayProps) }; /**< Data size of custom output
                                                                                          ray properties */
};

/**
 * @brief Config struct of beams utility.
 */
struct Config
{
    BaseConfig base;
    BeamWaist waist; /**< Beam waist, consisting of a horizontal and vertical part */
    BeamDivergence div; /**< Beam divergence, consisting of a horizontal and vertical part */
    RayleighRange rRange; /**< Rayleigh range, consisting of a horizontal and vertical part */
    float rangeOffset; /**< Range offset in meters to be applied to the ray origin */
    bool cullBackFace; /**< control flag for back face culling */
};

/**
 * @brief The base ray corresponding to the idealized ray of the emitter.
 */
struct CentralBaseRay
{
    float3 origin; /**< Origin of the ray in meter */
    float azimuthDeg; /**< Azimuth deviation in degree */
    float elevationDeg; /**< Elevation deviation in degree */
    float powerW; /**< Overall emitted power of beam in watt */
    uint64_t firingTimeNs; /**< Firing time in nanoseconds  */
};

/**
 * @brief Inputs for the beams utility. The additional in ray properties are optional.
 */
struct BeamInputs
{
    CentralBaseRay* baseRays;
    omni::sensors::materials::NvMatRayProps* inRayProps;
};

/**
 * @brief Hit information of beam rays.
 */
struct HitInformation
{
    float range{ 0.f }; /**< range of hit point in meter */
    float irradiance{ 0.f }; /**< irradiance portion of hit point -- can be raw irradiance or normalized */
    uint32_t hitId{ 0 }; /**<(CentalBaseRay-id * NUM_RAYS+hit id) corresponds to rtxsensor ray id */
};


/**
 * @brief Beam utility results including material processing outputs.
 */
struct BatchResult
{
    // BeamResult* beamResults;
    HitInformation* hits; /**< Hit informations -- numbeams*NUM_RAYS_PER_BEAM */
    omni::sensors::materials::NvMatOutput* matOutputs;
};

#pragma pack(pop)


/**
 * @brief Calculates the needed Rtx rays for given number of base rays
 * @param numBaseRays number of base rays
 * @return uint32_t
 */
inline uint32_t numRtxRays(uint32_t numBaseRays) noexcept
{
    return numBaseRays * NUM_RAYS_PER_BEAM;
}

inline Config createConfigWithDivergence(const BeamDivergence& div, const BaseConfig& base)
{
    Config cfg;
    cfg.base = base;
    cfg.div = div;
    // *1000.f for precision
    cfg.waist.horizM = (base.waveLengthNm * static_cast<float>(1E-06)) / (PI * cfg.div.horizRad * 1000.f);
    cfg.waist.vertM = (base.waveLengthNm * static_cast<float>(1E-06)) / (PI * cfg.div.vertRad * 1000.f);

    cfg.rRange.horizM = cfg.waist.horizM / cfg.div.horizRad;
    cfg.rRange.vertM = cfg.waist.vertM / cfg.div.vertRad;
    return cfg;
}

inline Config createConfigWithWaist(const BeamWaist& waist, const BaseConfig& base)
{
    Config cfg;
    cfg.waist = waist;
    cfg.base = base;
    // *1000.f for precision
    cfg.div.horizRad = (base.waveLengthNm * static_cast<float>(1E-06)) / (PI * cfg.waist.horizM * 1000.f);
    cfg.div.vertRad = (base.waveLengthNm * static_cast<float>(1E-06)) / (PI * cfg.waist.vertM * 1000.f);

    cfg.rRange.horizM = cfg.waist.horizM / cfg.div.horizRad;
    cfg.rRange.vertM = cfg.waist.vertM / cfg.div.vertRad;
    return cfg;
}


} // namespace beams
} // namespace sensors
} // namespace omni
