// SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

// This file contains code taken from Warp for implementing noise functions.
// Once Warp is released this file will be deleted and the nodes which use
// it rewritten to use Warp.

#include <cmath>
#include <sys/types.h>
#include <omni/graph/core/ogn/UsdTypes.h>

#ifndef _EPSILON
#    define _EPSILON 1e-6
#endif

#define M_PIf 3.14159265358979323846f

namespace omni
{
namespace graph
{
namespace nodes
{

typedef pxr::GfVec2f vec2;
typedef pxr::GfVec3f vec3;
typedef pxr::GfVec4f vec4;


// Adapted from warp/warp/native/rand.h
//
inline uint32_t rand_pcg(uint32_t state)
{
    uint32_t b = state * 747796405u + 2891336453u;
    uint32_t c = ((b >> ((b >> 28u) + 4u)) ^ b) * 277803737u;
    return (c >> 22u) ^ c;
}

inline uint32_t rand_init(int seed)
{
    return rand_pcg(uint32_t(seed));
}
inline uint32_t rand_init(int seed, int offset)
{
    return rand_pcg(uint32_t(seed) + rand_pcg(uint32_t(offset)));
}

inline int randi(uint32_t& state)
{
    state = rand_pcg(state);
    return int(state);
}
inline int randi(uint32_t& state, int min, int max)
{
    state = rand_pcg(state);
    return state % (max - min) + min;
}

inline float randf(uint32_t& state)
{
    state = rand_pcg(state);
    return float(state) / 0xffffffff;
}
inline float randf(uint32_t& state, float min, float max)
{
    return (max - min) * randf(state) + min;
}

// Box-Muller method
inline float randn(uint32_t& state)
{
    return std::sqrt(-2.f * std::log(randf(state))) * std::cos(2.f * M_PIf * randf(state));
}


// Adapted from warp/warp/native/noise.h
//
inline float smootherstep(float t)
{
    return t * t * t * (t * (t * 6.f - 15.f) + 10.f);
}

inline float smootherstep_gradient(float t)
{
    return 30.f * t * t * (t * (t - 2.f) + 1.f);
}

inline float interpolate(float a0, float a1, float t)
{
    return (a1 - a0) * smootherstep(t) + a0;
}

inline float interpolate_gradient(float a0, float a1, float t, float d_a0, float d_a1, float d_t)
{
    return (d_a1 - d_a0) * smootherstep(t) + (a1 - a0) * smootherstep_gradient(t) * d_t + d_a0;
}

inline float random_gradient_1d(uint32_t seed, int ix)
{
    const uint32_t p1 = 73856093;
    uint32_t idx = ix * p1;
    uint32_t state = seed + idx;
    return randf(state, -1.f, 1.f);
}

inline vec2 random_gradient_2d(uint32_t seed, int ix, int iy)
{
    const uint32_t p1 = 73856093;
    const uint32_t p2 = 19349663;
    uint32_t idx = ix * p1 ^ iy * p2;
    uint32_t state = seed + idx;
    float phi = randf(state, 0.f, 2.f * M_PIf);
    float x = std::cos(phi);
    float y = std::sin(phi);
    return vec2(x, y);
}

inline vec3 random_gradient_3d(uint32_t seed, int ix, int iy, int iz)
{
    const uint32_t p1 = 73856093;
    const uint32_t p2 = 19349663;
    const uint32_t p3 = 53471161;
    uint32_t idx = ix * p1 ^ iy * p2 ^ iz * p3;
    uint32_t state = seed + idx;

    float x = randn(state);
    float y = randn(state);
    float z = randn(state);

    return vec3(x, y, z).GetNormalized();
}

inline vec4 random_gradient_4d(uint32_t seed, int ix, int iy, int iz, int it)
{
    const uint32_t p1 = 73856093;
    const uint32_t p2 = 19349663;
    const uint32_t p3 = 53471161;
    const uint32_t p4 = 10000019;
    uint32_t idx = ix * p1 ^ iy * p2 ^ iz * p3 ^ it * p4;
    uint32_t state = seed + idx;

    float x = randn(state);
    float y = randn(state);
    float z = randn(state);
    float t = randn(state);

    return vec4(x, y, z, t).GetNormalized();
}

inline float dot_grid_gradient_1d(uint32_t seed, int ix, float dx)
{
    float gradient = random_gradient_1d(seed, ix);
    return dx * gradient;
}

inline float dot_grid_gradient_1d_gradient(uint32_t seed, int ix, float d_dx)
{
    float gradient = random_gradient_1d(seed, ix);
    return d_dx * gradient;
}

inline float dot_grid_gradient_2d(uint32_t seed, int ix, int iy, float dx, float dy)
{
    vec2 gradient = random_gradient_2d(seed, ix, iy);
    return (dx * gradient[0] + dy * gradient[1]);
}

inline float dot_grid_gradient_2d_gradient(uint32_t seed, int ix, int iy, float d_dx, float d_dy)
{
    vec2 gradient = random_gradient_2d(seed, ix, iy);
    return (d_dx * gradient[0] + d_dy * gradient[1]);
}

inline float dot_grid_gradient_3d(uint32_t seed, int ix, int iy, int iz, float dx, float dy, float dz)
{
    vec3 gradient = random_gradient_3d(seed, ix, iy, iz);
    return (dx * gradient[0] + dy * gradient[1] + dz * gradient[2]);
}

inline float dot_grid_gradient_3d_gradient(uint32_t seed, int ix, int iy, int iz, float d_dx, float d_dy, float d_dz)
{
    vec3 gradient = random_gradient_3d(seed, ix, iy, iz);
    return (d_dx * gradient[0] + d_dy * gradient[1] + d_dz * gradient[2]);
}

inline float dot_grid_gradient_4d(uint32_t seed, int ix, int iy, int iz, int it, float dx, float dy, float dz, float dt)
{
    vec4 gradient = random_gradient_4d(seed, ix, iy, iz, it);
    return (dx * gradient[0] + dy * gradient[1] + dz * gradient[2] + dt * gradient[3]);
}

inline float dot_grid_gradient_4d_gradient(
    uint32_t seed, int ix, int iy, int iz, int it, float d_dx, float d_dy, float d_dz, float d_dt)
{
    vec4 gradient = random_gradient_4d(seed, ix, iy, iz, it);
    return (d_dx * gradient[0] + d_dy * gradient[1] + d_dz * gradient[2] + d_dt * gradient[3]);
}

inline float noise_1d(uint32_t seed, int x0, int x1, float dx)
{
    // vX
    float v0 = dot_grid_gradient_1d(seed, x0, dx);
    float v1 = dot_grid_gradient_1d(seed, x1, dx - 1.f);

    return interpolate(v0, v1, dx);
}

inline float noise_1d_gradient(uint32_t seed, int x0, int x1, float dx, float heaviside_x)
{
    float v0 = dot_grid_gradient_1d(seed, x0, dx);
    float d_v0_dx = dot_grid_gradient_1d_gradient(seed, x0, heaviside_x);

    float v1 = dot_grid_gradient_1d(seed, x1, dx - 1.f);
    float d_v1_dx = dot_grid_gradient_1d_gradient(seed, x1, heaviside_x);

    return interpolate_gradient(v0, v1, dx, d_v0_dx, d_v1_dx, heaviside_x);
}

inline float noise_2d(uint32_t seed, int x0, int y0, int x1, int y1, float dx, float dy)
{
    // vXY
    float v00 = dot_grid_gradient_2d(seed, x0, y0, dx, dy);
    float v10 = dot_grid_gradient_2d(seed, x1, y0, dx - 1.f, dy);
    float xi0 = interpolate(v00, v10, dx);

    float v01 = dot_grid_gradient_2d(seed, x0, y1, dx, dy - 1.f);
    float v11 = dot_grid_gradient_2d(seed, x1, y1, dx - 1.f, dy - 1.f);
    float xi1 = interpolate(v01, v11, dx);

    return interpolate(xi0, xi1, dy);
}

inline vec2 noise_2d_gradient(
    uint32_t seed, int x0, int y0, int x1, int y1, float dx, float dy, float heaviside_x, float heaviside_y)
{
    float v00 = dot_grid_gradient_2d(seed, x0, y0, dx, dy);
    float d_v00_dx = dot_grid_gradient_2d_gradient(seed, x0, y0, heaviside_x, 0.f);
    float d_v00_dy = dot_grid_gradient_2d_gradient(seed, x0, y0, 0.0, heaviside_y);

    float v10 = dot_grid_gradient_2d(seed, x1, y0, dx - 1.f, dy);
    float d_v10_dx = dot_grid_gradient_2d_gradient(seed, x1, y0, heaviside_x, 0.f);
    float d_v10_dy = dot_grid_gradient_2d_gradient(seed, x1, y0, 0.0, heaviside_y);

    float v01 = dot_grid_gradient_2d(seed, x0, y1, dx, dy - 1.f);
    float d_v01_dx = dot_grid_gradient_2d_gradient(seed, x0, y1, heaviside_x, 0.f);
    float d_v01_dy = dot_grid_gradient_2d_gradient(seed, x0, y1, 0.0, heaviside_y);

    float v11 = dot_grid_gradient_2d(seed, x1, y1, dx - 1.f, dy - 1.f);
    float d_v11_dx = dot_grid_gradient_2d_gradient(seed, x1, y1, heaviside_x, 0.f);
    float d_v11_dy = dot_grid_gradient_2d_gradient(seed, x1, y1, 0.0, heaviside_y);

    float xi0 = interpolate(v00, v10, dx);
    float d_xi0_dx = interpolate_gradient(v00, v10, dx, d_v00_dx, d_v10_dx, heaviside_x);
    float d_xi0_dy = interpolate_gradient(v00, v10, dx, d_v00_dy, d_v10_dy, 0.0);

    float xi1 = interpolate(v01, v11, dx);
    float d_xi1_dx = interpolate_gradient(v01, v11, dx, d_v01_dx, d_v11_dx, heaviside_x);
    float d_xi1_dy = interpolate_gradient(v01, v11, dx, d_v01_dy, d_v11_dy, 0.0);

    float gradient_x = interpolate_gradient(xi0, xi1, dy, d_xi0_dx, d_xi1_dx, 0.0);
    float gradient_y = interpolate_gradient(xi0, xi1, dy, d_xi0_dy, d_xi1_dy, heaviside_y);

    return vec2(gradient_x, gradient_y);
}

inline float noise_3d(uint32_t seed, int x0, int y0, int z0, int x1, int y1, int z1, float dx, float dy, float dz)
{
    // vXYZ
    float v000 = dot_grid_gradient_3d(seed, x0, y0, z0, dx, dy, dz);
    float v100 = dot_grid_gradient_3d(seed, x1, y0, z0, dx - 1.f, dy, dz);
    float xi00 = interpolate(v000, v100, dx);

    float v010 = dot_grid_gradient_3d(seed, x0, y1, z0, dx, dy - 1.f, dz);
    float v110 = dot_grid_gradient_3d(seed, x1, y1, z0, dx - 1.f, dy - 1.f, dz);
    float xi10 = interpolate(v010, v110, dx);

    float yi0 = interpolate(xi00, xi10, dy);

    float v001 = dot_grid_gradient_3d(seed, x0, y0, z1, dx, dy, dz - 1.f);
    float v101 = dot_grid_gradient_3d(seed, x1, y0, z1, dx - 1.f, dy, dz - 1.f);
    float xi01 = interpolate(v001, v101, dx);

    float v011 = dot_grid_gradient_3d(seed, x0, y1, z1, dx, dy - 1.f, dz - 1.f);
    float v111 = dot_grid_gradient_3d(seed, x1, y1, z1, dx - 1.f, dy - 1.f, dz - 1.f);
    float xi11 = interpolate(v011, v111, dx);

    float yi1 = interpolate(xi01, xi11, dy);

    return interpolate(yi0, yi1, dz);
}

inline vec3 noise_3d_gradient(uint32_t seed,
                              int x0,
                              int y0,
                              int z0,
                              int x1,
                              int y1,
                              int z1,
                              float dx,
                              float dy,
                              float dz,
                              float heaviside_x,
                              float heaviside_y,
                              float heaviside_z)
{
    float v000 = dot_grid_gradient_3d(seed, x0, y0, z0, dx, dy, dz);
    float d_v000_dx = dot_grid_gradient_3d_gradient(seed, x0, y0, z0, heaviside_x, 0.f, 0.f);
    float d_v000_dy = dot_grid_gradient_3d_gradient(seed, x0, y0, z0, 0.f, heaviside_y, 0.f);
    float d_v000_dz = dot_grid_gradient_3d_gradient(seed, x0, y0, z0, 0.f, 0.f, heaviside_z);

    float v100 = dot_grid_gradient_3d(seed, x1, y0, z0, dx - 1.f, dy, dz);
    float d_v100_dx = dot_grid_gradient_3d_gradient(seed, x1, y0, z0, heaviside_x, 0.f, 0.f);
    float d_v100_dy = dot_grid_gradient_3d_gradient(seed, x1, y0, z0, 0.f, heaviside_y, 0.f);
    float d_v100_dz = dot_grid_gradient_3d_gradient(seed, x1, y0, z0, 0.f, 0.f, heaviside_z);

    float v010 = dot_grid_gradient_3d(seed, x0, y1, z0, dx, dy - 1.f, dz);
    float d_v010_dx = dot_grid_gradient_3d_gradient(seed, x0, y1, z0, heaviside_x, 0.f, 0.f);
    float d_v010_dy = dot_grid_gradient_3d_gradient(seed, x0, y1, z0, 0.f, heaviside_y, 0.f);
    float d_v010_dz = dot_grid_gradient_3d_gradient(seed, x0, y1, z0, 0.f, 0.f, heaviside_z);

    float v110 = dot_grid_gradient_3d(seed, x1, y1, z0, dx - 1.f, dy - 1.f, dz);
    float d_v110_dx = dot_grid_gradient_3d_gradient(seed, x1, y1, z0, heaviside_x, 0.f, 0.f);
    float d_v110_dy = dot_grid_gradient_3d_gradient(seed, x1, y1, z0, 0.f, heaviside_y, 0.f);
    float d_v110_dz = dot_grid_gradient_3d_gradient(seed, x1, y1, z0, 0.f, 0.f, heaviside_z);

    float v001 = dot_grid_gradient_3d(seed, x0, y0, z1, dx, dy, dz - 1.f);
    float d_v001_dx = dot_grid_gradient_3d_gradient(seed, x0, y0, z1, heaviside_x, 0.f, 0.f);
    float d_v001_dy = dot_grid_gradient_3d_gradient(seed, x0, y0, z1, 0.f, heaviside_y, 0.f);
    float d_v001_dz = dot_grid_gradient_3d_gradient(seed, x0, y0, z1, 0.f, 0.f, heaviside_z);

    float v101 = dot_grid_gradient_3d(seed, x1, y0, z1, dx - 1.f, dy, dz - 1.f);
    float d_v101_dx = dot_grid_gradient_3d_gradient(seed, x1, y0, z1, heaviside_x, 0.f, 0.f);
    float d_v101_dy = dot_grid_gradient_3d_gradient(seed, x1, y0, z1, 0.f, heaviside_y, 0.f);
    float d_v101_dz = dot_grid_gradient_3d_gradient(seed, x1, y0, z1, 0.f, 0.f, heaviside_z);

    float v011 = dot_grid_gradient_3d(seed, x0, y1, z1, dx, dy - 1.f, dz - 1.f);
    float d_v011_dx = dot_grid_gradient_3d_gradient(seed, x0, y1, z1, heaviside_x, 0.f, 0.f);
    float d_v011_dy = dot_grid_gradient_3d_gradient(seed, x0, y1, z1, 0.f, heaviside_y, 0.f);
    float d_v011_dz = dot_grid_gradient_3d_gradient(seed, x0, y1, z1, 0.f, 0.f, heaviside_z);

    float v111 = dot_grid_gradient_3d(seed, x1, y1, z1, dx - 1.f, dy - 1.f, dz - 1.f);
    float d_v111_dx = dot_grid_gradient_3d_gradient(seed, x1, y1, z1, heaviside_x, 0.f, 0.f);
    float d_v111_dy = dot_grid_gradient_3d_gradient(seed, x1, y1, z1, 0.f, heaviside_y, 0.f);
    float d_v111_dz = dot_grid_gradient_3d_gradient(seed, x1, y1, z1, 0.f, 0.f, heaviside_z);

    float xi00 = interpolate(v000, v100, dx);
    float d_xi00_dx = interpolate_gradient(v000, v100, dx, d_v000_dx, d_v100_dx, heaviside_x);
    float d_xi00_dy = interpolate_gradient(v000, v100, dx, d_v000_dy, d_v100_dy, 0.f);
    float d_xi00_dz = interpolate_gradient(v000, v100, dx, d_v000_dz, d_v100_dz, 0.f);

    float xi10 = interpolate(v010, v110, dx);
    float d_xi10_dx = interpolate_gradient(v010, v110, dx, d_v010_dx, d_v110_dx, heaviside_x);
    float d_xi10_dy = interpolate_gradient(v010, v110, dx, d_v010_dy, d_v110_dy, 0.f);
    float d_xi10_dz = interpolate_gradient(v010, v110, dx, d_v010_dz, d_v110_dz, 0.f);

    float xi01 = interpolate(v001, v101, dx);
    float d_xi01_dx = interpolate_gradient(v001, v101, dx, d_v001_dx, d_v101_dx, heaviside_x);
    float d_xi01_dy = interpolate_gradient(v001, v101, dx, d_v001_dy, d_v101_dy, 0.f);
    float d_xi01_dz = interpolate_gradient(v001, v101, dx, d_v001_dz, d_v101_dz, 0.f);

    float xi11 = interpolate(v011, v111, dx);
    float d_xi11_dx = interpolate_gradient(v011, v111, dx, d_v011_dx, d_v111_dx, heaviside_x);
    float d_xi11_dy = interpolate_gradient(v011, v111, dx, d_v011_dy, d_v111_dy, 0.f);
    float d_xi11_dz = interpolate_gradient(v011, v111, dx, d_v011_dz, d_v111_dz, 0.f);

    float yi0 = interpolate(xi00, xi10, dy);
    float d_yi0_dx = interpolate_gradient(xi00, xi10, dy, d_xi00_dx, d_xi10_dx, 0.f);
    float d_yi0_dy = interpolate_gradient(xi00, xi10, dy, d_xi00_dy, d_xi10_dy, heaviside_y);
    float d_yi0_dz = interpolate_gradient(xi00, xi10, dy, d_xi00_dz, d_xi10_dz, 0.f);

    float yi1 = interpolate(xi01, xi11, dy);
    float d_yi1_dx = interpolate_gradient(xi01, xi11, dy, d_xi01_dx, d_xi11_dx, 0.f);
    float d_yi1_dy = interpolate_gradient(xi01, xi11, dy, d_xi01_dy, d_xi11_dy, heaviside_y);
    float d_yi1_dz = interpolate_gradient(xi01, xi11, dy, d_xi01_dz, d_xi11_dz, 0.f);

    float gradient_x = interpolate_gradient(yi0, yi1, dz, d_yi0_dy, d_yi1_dy, 0.f);
    float gradient_y = interpolate_gradient(yi0, yi1, dz, d_yi0_dx, d_yi1_dx, 0.f);
    float gradient_z = interpolate_gradient(yi0, yi1, dz, d_yi0_dz, d_yi1_dz, heaviside_z);

    return vec3(gradient_x, gradient_y, gradient_z);
}

inline float noise_4d(
    uint32_t seed, int x0, int y0, int z0, int t0, int x1, int y1, int z1, int t1, float dx, float dy, float dz, float dt)
{
    // vXYZT
    float v0000 = dot_grid_gradient_4d(seed, x0, y0, z0, t0, dx, dy, dz, dt);
    float v1000 = dot_grid_gradient_4d(seed, x1, y0, z0, t0, dx - 1.f, dy, dz, dt);
    float xi000 = interpolate(v0000, v1000, dx);

    float v0100 = dot_grid_gradient_4d(seed, x0, y1, z0, t0, dx, dy - 1.f, dz, dt);
    float v1100 = dot_grid_gradient_4d(seed, x1, y1, z0, t0, dx - 1.f, dy - 1.f, dz, dt);
    float xi100 = interpolate(v0100, v1100, dx);

    float yi00 = interpolate(xi000, xi100, dy);

    float v0010 = dot_grid_gradient_4d(seed, x0, y0, z1, t0, dx, dy, dz - 1.f, dt);
    float v1010 = dot_grid_gradient_4d(seed, x1, y0, z1, t0, dx - 1.f, dy, dz - 1.f, dt);
    float xi010 = interpolate(v0010, v1010, dx);

    float v0110 = dot_grid_gradient_4d(seed, x0, y1, z1, t0, dx, dy - 1.f, dz - 1.f, dt);
    float v1110 = dot_grid_gradient_4d(seed, x1, y1, z1, t0, dx - 1.f, dy - 1.f, dz - 1.f, dt);
    float xi110 = interpolate(v0110, v1110, dx);

    float yi10 = interpolate(xi010, xi110, dy);

    float zi0 = interpolate(yi00, yi10, dz);

    float v0001 = dot_grid_gradient_4d(seed, x0, y0, z0, t1, dx, dy, dz, dt - 1.f);
    float v1001 = dot_grid_gradient_4d(seed, x1, y0, z0, t1, dx - 1.f, dy, dz, dt - 1.f);
    float xi001 = interpolate(v0001, v1001, dx);

    float v0101 = dot_grid_gradient_4d(seed, x0, y1, z0, t1, dx, dy - 1.f, dz, dt - 1.f);
    float v1101 = dot_grid_gradient_4d(seed, x1, y1, z0, t1, dx - 1.f, dy - 1.f, dz, dt - 1.f);
    float xi101 = interpolate(v0101, v1101, dx);

    float yi01 = interpolate(xi001, xi101, dy);

    float v0011 = dot_grid_gradient_4d(seed, x0, y0, z1, t1, dx, dy, dz - 1.f, dt - 1.f);
    float v1011 = dot_grid_gradient_4d(seed, x1, y0, z1, t1, dx - 1.f, dy, dz - 1.f, dt - 1.f);
    float xi011 = interpolate(v0011, v1011, dx);

    float v0111 = dot_grid_gradient_4d(seed, x0, y1, z1, t1, dx, dy - 1.f, dz - 1.f, dt - 1.f);
    float v1111 = dot_grid_gradient_4d(seed, x1, y1, z1, t1, dx - 1.f, dy - 1.f, dz - 1.f, dt - 1.f);
    float xi111 = interpolate(v0111, v1111, dx);

    float yi11 = interpolate(xi011, xi111, dy);

    float zi1 = interpolate(yi01, yi11, dz);

    return interpolate(zi0, zi1, dt);
}

inline vec4 noise_4d_gradient(uint32_t seed,
                              int x0,
                              int y0,
                              int z0,
                              int t0,
                              int x1,
                              int y1,
                              int z1,
                              int t1,
                              float dx,
                              float dy,
                              float dz,
                              float dt,
                              float heaviside_x,
                              float heaviside_y,
                              float heaviside_z,
                              float heaviside_t)
{
    float v0000 = dot_grid_gradient_4d(seed, x0, y0, z0, t0, dx, dy, dz, dt);
    float d_v0000_dx = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0000_dy = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0000_dz = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0000_dt = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v1000 = dot_grid_gradient_4d(seed, x1, y0, z0, t0, dx - 1.f, dy, dz, dt);
    float d_v1000_dx = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1000_dy = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1000_dz = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1000_dt = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v0100 = dot_grid_gradient_4d(seed, x0, y1, z0, t0, dx, dy - 1.f, dz, dt);
    float d_v0100_dx = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0100_dy = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0100_dz = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0100_dt = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v1100 = dot_grid_gradient_4d(seed, x1, y1, z0, t0, dx - 1.f, dy - 1.f, dz, dt);
    float d_v1100_dx = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1100_dy = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1100_dz = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1100_dt = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v0010 = dot_grid_gradient_4d(seed, x0, y0, z1, t0, dx, dy, dz - 1.f, dt);
    float d_v0010_dx = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0010_dy = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0010_dz = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0010_dt = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v1010 = dot_grid_gradient_4d(seed, x1, y0, z1, t0, dx - 1.f, dy, dz - 1.f, dt);
    float d_v1010_dx = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1010_dy = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1010_dz = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1010_dt = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v0110 = dot_grid_gradient_4d(seed, x0, y1, z1, t0, dx, dy - 1.f, dz - 1.f, dt);
    float d_v0110_dx = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0110_dy = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0110_dz = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0110_dt = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v1110 = dot_grid_gradient_4d(seed, x1, y1, z1, t0, dx - 1.f, dy - 1.f, dz - 1.f, dt);
    float d_v1110_dx = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t0, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1110_dy = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t0, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1110_dz = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t0, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1110_dt = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t0, 0.f, 0.f, 0.f, heaviside_t);

    float v0001 = dot_grid_gradient_4d(seed, x0, y0, z0, t1, dx, dy, dz, dt - 1.f);
    float d_v0001_dx = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0001_dy = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0001_dz = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0001_dt = dot_grid_gradient_4d_gradient(seed, x0, y0, z0, t1, 0.f, 0.f, 0.f, heaviside_t);

    float v1001 = dot_grid_gradient_4d(seed, x1, y0, z0, t1, dx - 1.f, dy, dz, dt - 1.f);
    float d_v1001_dx = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1001_dy = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1001_dz = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1001_dt = dot_grid_gradient_4d_gradient(seed, x1, y0, z0, t1, 0.f, 0.f, 0.f, heaviside_t);

    float v0101 = dot_grid_gradient_4d(seed, x0, y1, z0, t1, dx, dy - 1.f, dz, dt - 1.f);
    float d_v0101_dx = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0101_dy = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0101_dz = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0101_dt = dot_grid_gradient_4d_gradient(seed, x0, y1, z0, t1, 0.f, 0.f, 0.f, heaviside_t);

    float v1101 = dot_grid_gradient_4d(seed, x1, y1, z0, t1, dx - 1.f, dy - 1.f, dz, dt - 1.f);
    float d_v1101_dx = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1101_dy = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1101_dz = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1101_dt = dot_grid_gradient_4d_gradient(seed, x1, y1, z0, t1, 0.f, 0.f, 0.f, heaviside_t);

    float v0011 = dot_grid_gradient_4d(seed, x0, y0, z1, t1, dx, dy, dz - 1.f, dt - 1.f);
    float d_v0011_dx = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0011_dy = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0011_dz = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0011_dt = dot_grid_gradient_4d_gradient(seed, x0, y0, z1, t1, 0.f, 0.f, 0.f, heaviside_t);

    float v1011 = dot_grid_gradient_4d(seed, x1, y0, z1, t1, dx - 1.f, dy, dz - 1.f, dt - 1.f);
    float d_v1011_dx = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1011_dy = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1011_dz = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1011_dt = dot_grid_gradient_4d_gradient(seed, x1, y0, z1, t1, 0.f, 0.f, 0.f, heaviside_t);

    float v0111 = dot_grid_gradient_4d(seed, x0, y1, z1, t1, dx, dy - 1.f, dz - 1.f, dt - 1.f);
    float d_v0111_dx = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v0111_dy = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v0111_dz = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v0111_dt = dot_grid_gradient_4d_gradient(seed, x0, y1, z1, t1, 0.f, 0.f, 0.f, heaviside_t);

    float v1111 = dot_grid_gradient_4d(seed, x1, y1, z1, t1, dx - 1.f, dy - 1.f, dz - 1.f, dt - 1.f);
    float d_v1111_dx = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t1, heaviside_x, 0.f, 0.f, 0.f);
    float d_v1111_dy = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t1, 0.f, heaviside_y, 0.f, 0.f);
    float d_v1111_dz = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t1, 0.f, 0.f, heaviside_z, 0.f);
    float d_v1111_dt = dot_grid_gradient_4d_gradient(seed, x1, y1, z1, t1, 0.f, 0.f, 0.f, heaviside_t);

    float xi000 = interpolate(v0000, v1000, dx);
    float d_xi000_dx = interpolate_gradient(v0000, v1000, dx, d_v0000_dx, d_v1000_dx, heaviside_x);
    float d_xi000_dy = interpolate_gradient(v0000, v1000, dx, d_v0000_dy, d_v1000_dy, 0.f);
    float d_xi000_dz = interpolate_gradient(v0000, v1000, dx, d_v0000_dz, d_v1000_dz, 0.f);
    float d_xi000_dt = interpolate_gradient(v0000, v1000, dx, d_v0000_dt, d_v1000_dt, 0.f);

    float xi100 = interpolate(v0100, v1100, dx);
    float d_xi100_dx = interpolate_gradient(v0100, v1100, dx, d_v0100_dx, d_v1100_dx, heaviside_x);
    float d_xi100_dy = interpolate_gradient(v0100, v1100, dx, d_v0100_dy, d_v1100_dy, 0.f);
    float d_xi100_dz = interpolate_gradient(v0100, v1100, dx, d_v0100_dz, d_v1100_dz, 0.f);
    float d_xi100_dt = interpolate_gradient(v0100, v1100, dx, d_v0100_dt, d_v1100_dt, 0.f);

    float xi010 = interpolate(v0010, v1010, dx);
    float d_xi010_dx = interpolate_gradient(v0010, v1010, dx, d_v0010_dx, d_v1010_dx, heaviside_x);
    float d_xi010_dy = interpolate_gradient(v0010, v1010, dx, d_v0010_dy, d_v1010_dy, 0.f);
    float d_xi010_dz = interpolate_gradient(v0010, v1010, dx, d_v0010_dz, d_v1010_dz, 0.f);
    float d_xi010_dt = interpolate_gradient(v0010, v1010, dx, d_v0010_dt, d_v1010_dt, 0.f);

    float xi110 = interpolate(v0110, v1110, dx);
    float d_xi110_dx = interpolate_gradient(v0110, v1110, dx, d_v0110_dx, d_v1110_dx, heaviside_x);
    float d_xi110_dy = interpolate_gradient(v0110, v1110, dx, d_v0110_dy, d_v1110_dy, 0.f);
    float d_xi110_dz = interpolate_gradient(v0110, v1110, dx, d_v0110_dz, d_v1110_dz, 0.f);
    float d_xi110_dt = interpolate_gradient(v0110, v1110, dx, d_v0110_dt, d_v1110_dt, 0.f);

    float xi001 = interpolate(v0001, v1001, dx);
    float d_xi001_dx = interpolate_gradient(v0001, v1001, dx, d_v0001_dx, d_v1001_dx, heaviside_x);
    float d_xi001_dy = interpolate_gradient(v0001, v1001, dx, d_v0001_dy, d_v1001_dy, 0.f);
    float d_xi001_dz = interpolate_gradient(v0001, v1001, dx, d_v0001_dz, d_v1001_dz, 0.f);
    float d_xi001_dt = interpolate_gradient(v0001, v1001, dx, d_v0001_dt, d_v1001_dt, 0.f);

    float xi101 = interpolate(v0101, v1101, dx);
    float d_xi101_dx = interpolate_gradient(v0101, v1101, dx, d_v0101_dx, d_v1101_dx, heaviside_x);
    float d_xi101_dy = interpolate_gradient(v0101, v1101, dx, d_v0101_dy, d_v1101_dy, 0.f);
    float d_xi101_dz = interpolate_gradient(v0101, v1101, dx, d_v0101_dz, d_v1101_dz, 0.f);
    float d_xi101_dt = interpolate_gradient(v0101, v1101, dx, d_v0101_dt, d_v1101_dt, 0.f);

    float xi011 = interpolate(v0011, v1011, dx);
    float d_xi011_dx = interpolate_gradient(v0011, v1011, dx, d_v0011_dx, d_v1011_dx, heaviside_x);
    float d_xi011_dy = interpolate_gradient(v0011, v1011, dx, d_v0011_dy, d_v1011_dy, 0.f);
    float d_xi011_dz = interpolate_gradient(v0011, v1011, dx, d_v0011_dz, d_v1011_dz, 0.f);
    float d_xi011_dt = interpolate_gradient(v0011, v1011, dx, d_v0011_dt, d_v1011_dt, 0.f);

    float xi111 = interpolate(v0111, v1111, dx);
    float d_xi111_dx = interpolate_gradient(v0111, v1111, dx, d_v0111_dx, d_v1111_dx, heaviside_x);
    float d_xi111_dy = interpolate_gradient(v0111, v1111, dx, d_v0111_dy, d_v1111_dy, 0.f);
    float d_xi111_dz = interpolate_gradient(v0111, v1111, dx, d_v0111_dz, d_v1111_dz, 0.f);
    float d_xi111_dt = interpolate_gradient(v0111, v1111, dx, d_v0111_dt, d_v1111_dt, 0.f);

    float yi00 = interpolate(xi000, xi100, dy);
    float d_yi00_dx = interpolate_gradient(xi000, xi100, dy, d_xi000_dx, d_xi100_dx, 0.f);
    float d_yi00_dy = interpolate_gradient(xi000, xi100, dy, d_xi000_dy, d_xi100_dy, heaviside_y);
    float d_yi00_dz = interpolate_gradient(xi000, xi100, dy, d_xi000_dz, d_xi100_dz, 0.f);
    float d_yi00_dt = interpolate_gradient(xi000, xi100, dy, d_xi000_dt, d_xi100_dt, 0.f);

    float yi10 = interpolate(xi010, xi110, dy);
    float d_yi10_dx = interpolate_gradient(xi010, xi110, dy, d_xi010_dx, d_xi110_dx, 0.f);
    float d_yi10_dy = interpolate_gradient(xi010, xi110, dy, d_xi010_dy, d_xi110_dy, heaviside_y);
    float d_yi10_dz = interpolate_gradient(xi010, xi110, dy, d_xi010_dz, d_xi110_dz, 0.f);
    float d_yi10_dt = interpolate_gradient(xi010, xi110, dy, d_xi010_dt, d_xi110_dt, 0.f);

    float yi01 = interpolate(xi001, xi101, dy);
    float d_yi01_dx = interpolate_gradient(xi001, xi101, dy, d_xi001_dx, d_xi101_dx, 0.f);
    float d_yi01_dy = interpolate_gradient(xi001, xi101, dy, d_xi001_dy, d_xi101_dy, heaviside_y);
    float d_yi01_dz = interpolate_gradient(xi001, xi101, dy, d_xi001_dz, d_xi101_dz, 0.f);
    float d_yi01_dt = interpolate_gradient(xi001, xi101, dy, d_xi001_dt, d_xi101_dt, 0.f);

    float yi11 = interpolate(xi011, xi111, dy);
    float d_yi11_dx = interpolate_gradient(xi011, xi111, dy, d_xi011_dx, d_xi111_dx, 0.f);
    float d_yi11_dy = interpolate_gradient(xi011, xi111, dy, d_xi011_dy, d_xi111_dy, heaviside_y);
    float d_yi11_dz = interpolate_gradient(xi011, xi111, dy, d_xi011_dz, d_xi111_dz, 0.f);
    float d_yi11_dt = interpolate_gradient(xi011, xi111, dy, d_xi011_dt, d_xi111_dt, 0.f);

    float zi0 = interpolate(yi00, yi10, dz);
    float d_zi0_dx = interpolate_gradient(yi00, yi10, dz, d_yi00_dx, d_yi10_dx, 0.f);
    float d_zi0_dy = interpolate_gradient(yi00, yi10, dz, d_yi00_dy, d_yi10_dy, 0.f);
    float d_zi0_dz = interpolate_gradient(yi00, yi10, dz, d_yi00_dz, d_yi10_dz, heaviside_z);
    float d_zi0_dt = interpolate_gradient(yi00, yi10, dz, d_yi00_dt, d_yi10_dt, 0.f);

    float zi1 = interpolate(yi01, yi11, dz);
    float d_zi1_dx = interpolate_gradient(yi01, yi11, dz, d_yi01_dx, d_yi11_dx, 0.f);
    float d_zi1_dy = interpolate_gradient(yi01, yi11, dz, d_yi01_dy, d_yi11_dy, 0.f);
    float d_zi1_dz = interpolate_gradient(yi01, yi11, dz, d_yi01_dz, d_yi11_dz, heaviside_z);
    float d_zi1_dt = interpolate_gradient(yi01, yi11, dz, d_yi01_dt, d_yi11_dt, 0.f);

    float gradient_x = interpolate_gradient(zi0, zi1, dt, d_zi0_dx, d_zi1_dx, 0.f);
    float gradient_y = interpolate_gradient(zi0, zi1, dt, d_zi0_dy, d_zi1_dy, 0.f);
    float gradient_z = interpolate_gradient(zi0, zi1, dt, d_zi0_dz, d_zi1_dz, 0.f);
    float gradient_t = interpolate_gradient(zi0, zi1, dt, d_zi0_dt, d_zi1_dt, heaviside_t);

    return vec4(gradient_x, gradient_y, gradient_z, gradient_t);
}

// non-periodic Perlin noise

inline float noise(uint32_t seed, float x)
{
    float dx = x - floor(x);

    int x0 = (int)floor(x);
    int x1 = x0 + 1;

    return noise_1d(seed, x0, x1, dx);
}

inline float noise(uint32_t seed, const vec2& xy)
{
    float dx = xy[0] - floor(xy[0]);
    float dy = xy[1] - floor(xy[1]);

    int x0 = (int)floor(xy[0]);
    int y0 = (int)floor(xy[1]);

    int x1 = x0 + 1;
    int y1 = y0 + 1;

    return noise_2d(seed, x0, y0, x1, y1, dx, dy);
}

inline float noise(uint32_t seed, const vec3& xyz)
{
    float dx = xyz[0] - floor(xyz[0]);
    float dy = xyz[1] - floor(xyz[1]);
    float dz = xyz[2] - floor(xyz[2]);

    int x0 = (int)floor(xyz[0]);
    int y0 = (int)floor(xyz[1]);
    int z0 = (int)floor(xyz[2]);

    int x1 = x0 + 1;
    int y1 = y0 + 1;
    int z1 = z0 + 1;

    return noise_3d(seed, x0, y0, z0, x1, y1, z1, dx, dy, dz);
}

inline float noise(uint32_t seed, const vec4& xyzt)
{
    float dx = xyzt[0] - floor(xyzt[0]);
    float dy = xyzt[1] - floor(xyzt[1]);
    float dz = xyzt[2] - floor(xyzt[2]);
    float dt = xyzt[3] - floor(xyzt[3]);

    int x0 = (int)floor(xyzt[0]);
    int y0 = (int)floor(xyzt[1]);
    int z0 = (int)floor(xyzt[2]);
    int t0 = (int)floor(xyzt[3]);

    int x1 = x0 + 1;
    int y1 = y0 + 1;
    int z1 = z0 + 1;
    int t1 = t0 + 1;

    return noise_4d(seed, x0, y0, z0, t0, x1, y1, z1, t1, dx, dy, dz, dt);
}

// periodic Perlin noise

inline float pnoise(uint32_t seed, float x, int px)
{
    float dx = x - floor(x);

    int x0 = ((int)floor(x)) % px;
    int x1 = (x0 + 1) % px;

    return noise_1d(seed, x0, x1, dx);
}

inline float pnoise(uint32_t seed, const vec2& xy, int px, int py)
{
    float dx = xy[0] - floor(xy[0]);
    float dy = xy[1] - floor(xy[1]);

    int x0 = ((int)floor(xy[0])) % px;
    int y0 = ((int)floor(xy[1])) % py;

    int x1 = (x0 + 1) % px;
    int y1 = (y0 + 1) % py;

    return noise_2d(seed, x0, y0, x1, y1, dx, dy);
}

inline float pnoise(uint32_t seed, const vec3& xyz, int px, int py, int pz)
{
    float dx = xyz[0] - floor(xyz[0]);
    float dy = xyz[1] - floor(xyz[1]);
    float dz = xyz[2] - floor(xyz[2]);

    int x0 = ((int)floor(xyz[0])) % px;
    int y0 = ((int)floor(xyz[1])) % py;
    int z0 = ((int)floor(xyz[2])) % pz;

    int x1 = (x0 + 1) % px;
    int y1 = (y0 + 1) % py;
    int z1 = (z0 + 1) % pz;

    return noise_3d(seed, x0, y0, z0, x1, y1, z1, dx, dy, dz);
}

inline float pnoise(uint32_t seed, const vec4& xyzt, int px, int py, int pz, int pt)
{
    float dx = xyzt[0] - floor(xyzt[0]);
    float dy = xyzt[1] - floor(xyzt[1]);
    float dz = xyzt[2] - floor(xyzt[2]);
    float dt = xyzt[3] - floor(xyzt[3]);

    int x0 = ((int)floor(xyzt[0])) % px;
    int y0 = ((int)floor(xyzt[1])) % py;
    int z0 = ((int)floor(xyzt[2])) % pz;
    int t0 = ((int)floor(xyzt[3])) % pt;

    int x1 = (x0 + 1) % px;
    int y1 = (y0 + 1) % py;
    int z1 = (z0 + 1) % pz;
    int t1 = (t0 + 1) % pt;

    return noise_4d(seed, x0, y0, z0, t0, x1, y1, z1, t1, dx, dy, dz, dt);
}

// curl noise

inline vec2 curlnoise(uint32_t seed, const vec2& xy)
{
    float dx = xy[0] - floor(xy[0]);
    float dy = xy[1] - floor(xy[1]);

    float heaviside_x = 1.f;
    float heaviside_y = 1.f;
    if (dx < _EPSILON)
        heaviside_x = 0.f;
    if (dy < _EPSILON)
        heaviside_y = 0.f;

    int x0 = (int)floor(xy[0]);
    int y0 = (int)floor(xy[1]);

    int x1 = x0 + 1;
    int y1 = y0 + 1;

    vec2 grad_field = noise_2d_gradient(seed, x0, y0, x1, y1, dx, dy, heaviside_x, heaviside_y);
    return vec2(-grad_field[1], grad_field[0]);
}

inline vec3 curlnoise(uint32_t seed, const vec3& xyz)
{
    float dx = xyz[0] - floor(xyz[0]);
    float dy = xyz[1] - floor(xyz[1]);
    float dz = xyz[2] - floor(xyz[2]);

    float heaviside_x = 1.f;
    float heaviside_y = 1.f;
    float heaviside_z = 1.f;
    if (dx < _EPSILON)
        heaviside_x = 0.f;
    if (dy < _EPSILON)
        heaviside_y = 0.f;
    if (dz < _EPSILON)
        heaviside_z = 0.f;

    int x0 = (int)floor(xyz[0]);
    int y0 = (int)floor(xyz[1]);
    int z0 = (int)floor(xyz[2]);

    int x1 = x0 + 1;
    int y1 = y0 + 1;
    int z1 = z0 + 1;

    vec3 grad_field_1 =
        noise_3d_gradient(seed, x0, y0, z0, x1, y1, z1, dx, dy, dz, heaviside_x, heaviside_y, heaviside_z);
    seed = rand_init(seed, 10019689);
    vec3 grad_field_2 =
        noise_3d_gradient(seed, x0, y0, z0, x1, y1, z1, dx, dy, dz, heaviside_x, heaviside_y, heaviside_z);
    seed = rand_init(seed, 13112221);
    vec3 grad_field_3 =
        noise_3d_gradient(seed, x0, y0, z0, x1, y1, z1, dx, dy, dz, heaviside_x, heaviside_y, heaviside_z);


    return vec3(grad_field_3[1] - grad_field_2[2], grad_field_1[2] - grad_field_3[0], grad_field_2[0] - grad_field_1[1]);
}

inline vec3 curlnoise(uint32_t seed, const vec4& xyzt)
{
    float dx = xyzt[0] - floor(xyzt[0]);
    float dy = xyzt[1] - floor(xyzt[1]);
    float dz = xyzt[2] - floor(xyzt[2]);
    float dt = xyzt[3] - floor(xyzt[3]);

    float heaviside_x = 1.f;
    float heaviside_y = 1.f;
    float heaviside_z = 1.f;
    float heaviside_t = 1.f;
    if (dx < _EPSILON)
        heaviside_x = 0.f;
    if (dy < _EPSILON)
        heaviside_y = 0.f;
    if (dz < _EPSILON)
        heaviside_z = 0.f;
    if (dt < _EPSILON)
        heaviside_t = 0.f;

    int x0 = (int)floor(xyzt[0]);
    int y0 = (int)floor(xyzt[1]);
    int z0 = (int)floor(xyzt[2]);
    int t0 = (int)floor(xyzt[3]);

    int x1 = x0 + 1;
    int y1 = y0 + 1;
    int z1 = z0 + 1;
    int t1 = t0 + 1;

    vec4 grad_field_1 = noise_4d_gradient(
        seed, x0, y0, z0, t0, x1, y1, z1, t1, dx, dy, dz, dt, heaviside_x, heaviside_y, heaviside_z, heaviside_t);
    seed = rand_init(seed, 10019689);
    vec4 grad_field_2 = noise_4d_gradient(
        seed, x0, y0, z0, t0, x1, y1, z1, t1, dx, dy, dz, dt, heaviside_x, heaviside_y, heaviside_z, heaviside_t);
    seed = rand_init(seed, 13112221);
    vec4 grad_field_3 = noise_4d_gradient(
        seed, x0, y0, z0, t0, x1, y1, z1, t1, dx, dy, dz, dt, heaviside_x, heaviside_y, heaviside_z, heaviside_t);

    return vec3(grad_field_3[1] - grad_field_2[2], grad_field_1[2] - grad_field_3[0], grad_field_2[0] - grad_field_1[1]);
}

} // namespace nodes
} // namespace graph
} // namespace omni
