// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

// Collection of CUDA math utilities

#include "cuda_runtime.h"

using double44 = double[4][4];
using float44 = float[4][4];

// ===============================================================
// Return the dot product of two float4s
inline __host__ __device__ float dot(const float4& a, const float4& b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w;
}

// ===============================================================
// Return the elementwise sum of two float4s
inline __host__ __device__ float4 operator+(const float4& a, const float4& b)
{
    return make_float4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w);
}

// ===============================================================
// Return the vector product of two float4s
inline __host__ __device__ float4 operator*(const float4& a, const float& s)
{
    return make_float4(a.x * s, a.y * s, a.z * s, a.w * s);
}

// ===============================================================
// Return the product of a float4 vector and a 4x4 matrix
inline __host__ __device__ float4 operator*(const float4& p, const double44& m)
{
    float4 result;
    result.x = (float)((double)p.x * m[0][0] + (double)p.y * m[1][0] + (double)p.z * m[2][0] + (double)p.w * m[3][0]);
    result.y = (float)((double)p.x * m[0][1] + (double)p.y * m[1][1] + (double)p.z * m[2][1] + (double)p.w * m[3][1]);
    result.z = (float)((double)p.x * m[0][2] + (double)p.y * m[1][2] + (double)p.z * m[2][2] + (double)p.w * m[3][2]);
    result.w = (float)((double)p.x * m[0][3] + (double)p.y * m[1][3] + (double)p.z * m[2][3] + (double)p.w * m[3][3]);
    return result;
}

// ===============================================================
// Return the product of a float4 vector and a 4x4 float matrix
inline __host__ __device__ float4 operator*(const float4& p, const float44& m)
{
    float4 result;
    result.x = p.x * m[0][0] + p.y * m[1][0] + p.z * m[2][0] + p.w * m[3][0];
    result.y = p.x * m[0][1] + p.y * m[1][1] + p.z * m[2][1] + p.w * m[3][1];
    result.z = p.x * m[0][2] + p.y * m[1][2] + p.z * m[2][2] + p.w * m[3][2];
    result.w = p.x * m[0][3] + p.y * m[1][3] + p.z * m[2][3] + p.w * m[3][3];
    return result;
}

// ===============================================================
// Return a float4 with it's w-scale applied and set to 1.0
inline __host__ __device__ float4 homogenize(const float4& p)
{
    float inv = (abs(p.w)) > 1e-6f ? 1.0f / p.w : 1.0f;
    return p * inv;
}

// ===============================================================
// Return the dot product of two float3s
inline __host__ __device__ float dot(const float3& a, const float3& b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

// ===============================================================
// Return the elementwise product of two float3s
inline __host__ __device__ float3 hadamard_product(const float3& a, const float3& b)
{
    return make_float3(a.x * b.x, a.y * b.y, a.z * b.z);
}

// ===============================================================
// Return the cross product of two float3s
inline __host__ __device__ float3 cross(const float3& a, const float3& b)
{
    return make_float3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x);
}

// ===============================================================
// Return the elementwise sum of two float3s
inline __host__ __device__ float3 operator+(const float3& a, const float3& b)
{
    return make_float3(a.x + b.x, a.y + b.y, a.z + b.z);
}

// ===============================================================
// Return the elementwise difference between two float3s
inline __host__ __device__ float3 operator-(const float3& a, const float3& b)
{
    return make_float3(a.x - b.x, a.y - b.y, a.z - b.z);
}

// ===============================================================
// Return the product of a float3 and a constant
inline __host__ __device__ float3 operator*(const float3& a, const float& s)
{
    return make_float3(a.x * s, a.y * s, a.z * s);
}

// ===============================================================
// Return the dot product of two double4s
inline __host__ __device__ double dot(const double4& a, const double4& b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w;
}

// ===============================================================
// Return the elementwise sum of two double4s
inline __host__ __device__ double4 operator+(const double4& a, const double4& b)
{
    return make_double4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w);
}

// ===============================================================
// Return the vector product of two double4s
inline __host__ __device__ double4 operator*(const double4& a, const double& s)
{
    return make_double4(a.x * s, a.y * s, a.z * s, a.w * s);
}

// ===============================================================
// Return the product of a double4 vector and a 4x4 matrix
inline __host__ __device__ double4 operator*(const double4& p, const double44& m)
{
    double4 result;
    result.x = (double)((double)p.x * m[0][0] + (double)p.y * m[1][0] + (double)p.z * m[2][0] + (double)p.w * m[3][0]);
    result.y = (double)((double)p.x * m[0][1] + (double)p.y * m[1][1] + (double)p.z * m[2][1] + (double)p.w * m[3][1]);
    result.z = (double)((double)p.x * m[0][2] + (double)p.y * m[1][2] + (double)p.z * m[2][2] + (double)p.w * m[3][2]);
    result.w = (double)((double)p.x * m[0][3] + (double)p.y * m[1][3] + (double)p.z * m[2][3] + (double)p.w * m[3][3]);
    return result;
}

// ===============================================================
// Return a double4 with it's w-scale applied and set to 1.0
inline __host__ __device__ double4 homogenize(const double4& p)
{
    double inv = (abs(p.w)) > 1e-6f ? 1.0f / p.w : 1.0f;
    return p * inv;
}

// ===============================================================
// Return the dot product of two double3s
inline __host__ __device__ double dot(const double3& a, const double3& b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

// ===============================================================
// Return the elementwise product of two double3s
inline __host__ __device__ double3 hadamard_product(const double3& a, const double3& b)
{
    return make_double3(a.x * b.x, a.y * b.y, a.z * b.z);
}

// ===============================================================
// Return the cross product of two double3s
inline __host__ __device__ double3 cross(const double3& a, const double3& b)
{
    return make_double3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x);
}

// ===============================================================
// Return the elementwise sum of two double3s
inline __host__ __device__ double3 operator+(const double3& a, const double3& b)
{
    return make_double3(a.x + b.x, a.y + b.y, a.z + b.z);
}

// ===============================================================
// Return the elementwise difference between two double3s
inline __host__ __device__ double3 operator-(const double3& a, const double3& b)
{
    return make_double3(a.x - b.x, a.y - b.y, a.z - b.z);
}

// ===============================================================
// Return the product of a double3 and a constant
inline __host__ __device__ double3 operator*(const double3& a, const double& s)
{
    return make_double3(a.x * s, a.y * s, a.z * s);
}
