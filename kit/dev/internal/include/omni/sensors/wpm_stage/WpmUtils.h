// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Utilities for WPM (wave propagation model)

#include "IWpm.h"

#include <omni/sensors/cuda/CudaHelperDecl.h>
#include <omni/sensors/cuda/CudaHelperMath.h>

#include <cstdint>

namespace omni
{
namespace sensors
{
namespace wpm
{

/** @brief a struct that defines a Ray */
struct Ray
{
    uint64_t deltaTimeNs; /**< delta time in nano secs from parent transmitter */
    float3 origin; /**< vector defining origin point of the ray relative to transmitter frame */
    float3 direction; /**< unit vector defining ray direction relative to transmitter frame */

    uint32_t targetDetGroupIdxInRx; /**< idx of target detectors group in corresponding receiver */
};

/**
 * @brief a utility to get minimum number of batches needed to realize a specific trace, this would be called in
 * conjunction with the API openTrace() from the RtxSensor
 *
 * @param def a pointer to a trace definition
 * @return uint32_t minimum number of batches needed to realize the defined trace
 */
inline uint32_t utilGetNumBatches(TraceDefinition* def)
{
    return def->traceTreeDepth + 1;
}

/**
 * @brief returns max number of firings that will ever be needed by the wpm, this would be called in conjunction with
 * the API getMemoryRequirements() from RtxSensor to determine the size of firings and returns.
 *
 * @param cfg config of the wpm
 * @return uint32_t max number of firings
 */
inline uint32_t utilGetMaxNumFirings(const Config& cfg)
{
    const uint32_t branchFactor = cfg.enTransmission ? static_cast<uint32_t>(pow(2, cfg.maxTraceTreeDepth)) : 1;
    const uint32_t numRaysLastDepthSingleTx{ cfg.maxNumRaysPerPattern * branchFactor };
    return numRaysLastDepthSingleTx * (1 + cfg.maxNumIdxsPerTarDetGroup) * cfg.maxNumTransmitters;
}

/**
 * @brief utility to get the 1 dimensional index in a linearized multi dimensional array from the individual indicies in
 * each dimension, with the optional arguments this can be used with up to 5 dimensional arrays
 *
 * @param id1 index in first dimension
 * @param id2 index in second dimension
 * @param dim1 size/span of first dimension
 * @param id3 (mandatory for >= 3D) index in third dimension
 * @param dim2 (mandatory for >= 3D) size/span of second dimension
 * @param id4 (mandatory for >= 4D) index in fourth dimension
 * @param dim3 (mandatory for >= 4D) size/span of third dimension
 * @param id5 (mandatory for >= 5D) index in fifth dimension
 * @param dim4 (mandatory for >= 5D) size/span of fourth dimension
 * @return 1D linear index
 */
/// \cond DO_NOT_DOCUMENT
NV_HOSTDEVICE
/// \endcond
inline int64_t utilGet1DIdFromND(int64_t id1,
                                 int64_t id2,
                                 int64_t dim1,
                                 int64_t id3 = 0,
                                 int64_t dim2 = 1,
                                 int64_t id4 = 0,
                                 int64_t dim3 = 1,
                                 int64_t id5 = 0,
                                 int64_t dim4 = 1)
{
    int64_t tmp = dim1;
    int64_t i = id1 + id2 * tmp;
    tmp *= dim2;
    i += id3 * tmp;
    tmp *= dim3;
    i += id4 * tmp;
    tmp *= dim4;
    i += id5 * tmp;
    return i;
}

/**
 * @brief utility to generate rays in a uniform pattern around a bore sight (specified with a direction unit vector),
 * the FOV around the bore sight is defined by an azimuth span and an elevation span, num rays is also defined
 * independently in azimuth and elevation directions, the rays are uniform in the sense of having a constant angle step
 * in each direction
 * @note all generated rays will share the same firing deltaTime, origin and target detection group index as in the
 * bore ray definition
 *
 * @param rays the rays array that will be generated
 * @param boreRay a ray defining the bore sight and firing deltaTime, origin, target detection group index
 * @param azSpanRad span in azimuth direction in radians
 * @param elSpanRad span in elevation direction in radians
 * @param numRaysAz number of rays in azimuth direction
 * @param numRaysEl number of rays in elevation direction
 */
inline void utilSetupUniform2DRays(Rays& rays,
                                   uint32_t startIdx,
                                   const Ray& boreRay,
                                   float azSpanRad,
                                   float elSpanRad,
                                   uint32_t numRaysAz,
                                   uint32_t numRaysEl)
{
    float3 spherical = ToSpherical(boreRay.direction);
    float azStartRad = spherical.x - (azSpanRad / 2);
    float elStartRad = ((PI / 2) - spherical.y) - (elSpanRad / 2);
    float azStepRad = azSpanRad / numRaysAz;
    float elStepRad = elSpanRad / numRaysEl;

    for (uint32_t elId = 0; elId < numRaysEl; ++elId)
    {
        float elevRad = (elStartRad + elId * elStepRad);
        for (uint32_t azId = 0; azId < numRaysAz; ++azId)
        {
            auto id = utilGet1DIdFromND((int64_t)azId, (int64_t)elId, (int64_t)numRaysAz);

            // rays[id] = boreRay;
            rays.deltaTimeNs[startIdx + id] = boreRay.deltaTimeNs;
            rays.origin[startIdx + id] = boreRay.origin;
            rays.targetDetGroupIdxInRx[startIdx + id] = boreRay.targetDetGroupIdxInRx;

            float azRad = (azStartRad + azId * azStepRad);
            // rays[id].direction = { (cosf(elevRad) * cosf(azRad)), (cosf(elevRad) * sinf(azRad)), (sinf(elevRad)) };
            rays.direction[startIdx + id] = { (cosf(elevRad) * cosf(azRad)), (cosf(elevRad) * sinf(azRad)),
                                              (sinf(elevRad)) };
        }
    }
}

/**
 * Helper function to compute the cross_local product of two float3 vectors.
 */
NV_HOSTDEVICE
inline float3 cross_local(const float3& a, const float3& b)
{
    return { a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x };
}

/**
 * Helper function to determine if two vectors are nearly parallel.
 */
NV_HOSTDEVICE
inline bool areNearlyParallel(const float3& a, const float3& b)
{
    float dotProduct = a.x * b.x + a.y * b.y + a.z * b.z;
    return fabs(dotProduct) > 0.9999; // Use a threshold close to 1 to determine near parallelism
}

/**
 * @brief Utility function to set resolve basis vectors
 */
inline void resolveBasisVectors(float3& up, float3& right, const float3& forward, const float3 (&defaultUp) [3])
{
    // If 'forward' is nearly parallel or antiparallel to the default 'up', adjust 'up'
    if (areNearlyParallel(forward, defaultUp[0]))
    {
        // Use 2nd defaultUp as up if forward is parallel/antiparallel
        up = defaultUp[1];
        right = cross_local(forward, up);
        if (areNearlyParallel(forward, up))
        { // Check if new up is also parallel, then adjust
            up = defaultUp[2]; 
            right = cross_local(forward, up);
        }
    }
    else
    {
        right = cross_local(forward, defaultUp[0]);
        up = cross_local(right, forward);
    }
}

/**
 * @brief Utility function to set up parallel rays within a square field of view (FOV).
 */
inline void utilSetupUniformParallelRays(
    Rays& rays, uint32_t startIdx, const Ray& boreRay, float extent, uint32_t numRaysH, uint32_t numRaysV)
{
    const float3 defaultUp[3] = { { 0, 1, 0 }, { 0, 0, 1 }, { 1, 0, 0 } };
    float3 right, up;

    resolveBasisVectors(up, right, boreRay.direction, defaultUp);

    float hStep = extent / numRaysH;
    float vStep = extent / numRaysV;

    float hStart = -extent / 2 + hStep / 2;
    float vStart = -extent / 2 + vStep / 2;

    for (uint32_t vId = 0; vId < numRaysV; ++vId)
    {
        for (uint32_t hId = 0; hId < numRaysH; ++hId)
        {
            uint32_t id = static_cast<uint32_t>(utilGet1DIdFromND((int64_t)hId, (int64_t)vId, (int64_t)numRaysH));

            rays.direction[startIdx + id] = boreRay.direction; // All rays have the same direction

            // Calculate the origin offset for each ray within the square FOV
            float hOffset = hStart + hId * hStep;
            float vOffset = vStart + vId * vStep;

            // Set the origin of each ray
            rays.origin[startIdx + id] = boreRay.origin + hOffset * right + vOffset * up;
            rays.deltaTimeNs[startIdx + id] = boreRay.deltaTimeNs;
            rays.targetDetGroupIdxInRx[startIdx + id] = boreRay.targetDetGroupIdxInRx;
        }
    }
}


/**
 * @brief Utility function to set up a parallel direction from a source direction
 */
NV_HOSTDEVICE
inline void setupUniformParallelRays(float3& rayDir,
                                     float3& rayOrg,
                                     const float3& boreDir,
                                     const float3& boreOrg,
                                     uint32_t Idx,
                                     float extent,
                                     uint32_t numRaysH,
                                     uint32_t numRaysV)
{
    const float3 defaultUp[3] = { { 0, 0, 1 }, { 0, 1, 0 }, { 1, 0, 0 } };
    float3 right, up;

    resolveBasisVectors(up, right, boreDir, defaultUp);

    const uint32_t c{ Idx % numRaysH };
    const uint32_t r{ Idx / numRaysH };

    float hStep = extent / numRaysH;
    float vStep = extent / numRaysV;

    float hOffset = -extent / 2.f + c * hStep;
    float vOffset = -extent / 2.f + r * vStep;

    rayDir = boreDir; // All rays have the same direction

    // Set the origin of each ray
    rayOrg = boreOrg + hOffset * right + vOffset * up;
}


} // namespace wpm
} // namespace sensors
} // namespace omni
