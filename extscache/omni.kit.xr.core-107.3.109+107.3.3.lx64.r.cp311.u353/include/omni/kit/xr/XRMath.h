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

// Math and utilities for XR

#include <carb/Types.h>
#include <carb/logging/Log.h>

#include <cmath>

#ifdef _WIN32
#    pragma warning(push)
#    pragma warning(disable : 4267)
#endif

#include <usdrt/gf/matrix.h>
#include <usdrt/gf/rotation.h>

#ifdef _WIN32
#    pragma warning(pop)
#endif

namespace omni
{
namespace kit
{
namespace xr
{

enum class XRMatrixValidity : uint32_t
{
    eValidityNone = 0,
    eValidityOrigin = 1,
    eValidityForward = 2,
    eValidityUp = 4,
    eValidityRight = 8,
    eValidityOrientation = eValidityForward | eValidityUp | eValidityRight,
    eValidityAll = eValidityOrigin | eValidityOrientation,
};

inline XRMatrixValidity operator|(XRMatrixValidity left, XRMatrixValidity right)
{
    return static_cast<XRMatrixValidity>(static_cast<uint32_t>(left) | static_cast<uint32_t>(right));
}

inline XRMatrixValidity& operator|=(XRMatrixValidity& left, XRMatrixValidity right)
{
    return left = left | right;
}

inline XRMatrixValidity operator&(XRMatrixValidity left, XRMatrixValidity right)
{
    return static_cast<XRMatrixValidity>(static_cast<uint32_t>(left) & static_cast<uint32_t>(right));
}

inline XRMatrixValidity& operator&=(XRMatrixValidity& left, XRMatrixValidity right)
{
    return left = left & right;
}

inline XRMatrixValidity operator~(XRMatrixValidity validity)
{
    return static_cast<XRMatrixValidity>(static_cast<uint32_t>(XRMatrixValidity::eValidityAll) &
                                         ~static_cast<uint32_t>(validity));
}


struct XRMatrix
{
    float m[16];

    XRMatrixValidity validity;

    inline carb::Float3 getOrigin() const
    {
        return carb::Float3{ m[12] / m[15], m[13] / m[15], m[14] / m[15] };
    }

    inline carb::Float3 getRight() const
    {
        return carb::Float3{ m[0], m[1], m[2] };
    };

    inline carb::Float3 getUp() const
    {
        return carb::Float3{ m[4], m[5], m[6] };
    };

    inline carb::Float3 getForward() const
    {
        return carb::Float3{ -m[8], -m[9], -m[10] };
    };

    inline XRMatrix& setIdentity()
    {
        m[0] = 1.0f;
        m[1] = 0.0f;
        m[2] = 0.0f;
        m[3] = 0.0f;
        m[4] = 0.0f;
        m[5] = 1.0f;
        m[6] = 0.0f;
        m[7] = 0.0f;
        m[8] = 0.0f;
        m[9] = 0.0f;
        m[10] = 1.0f;
        m[11] = 0.0f;
        m[12] = 0.0f;
        m[13] = 0.0f;
        m[14] = 0.0f;
        m[15] = 1.0f;

        return *this;
    }

    inline XRMatrix& setOrigin(const carb::Float3& value)
    {
        m[12] = value.x;
        m[13] = value.y;
        m[14] = value.z;
        m[15] = 1.0f;

        return *this;
    }

    inline XRMatrix& setRight(const carb::Float3& value)
    {
        m[0] = value.x;
        m[1] = value.y;
        m[2] = value.z;
        m[3] = 0.0f;

        return *this;
    }

    inline XRMatrix& setUp(const carb::Float3& value)
    {
        m[4] = value.x;
        m[5] = value.y;
        m[6] = value.z;
        m[7] = 0.0f;

        return *this;
    }

    inline XRMatrix& setForward(const carb::Float3& value)
    {
        m[8] = -value.x;
        m[9] = -value.y;
        m[10] = -value.z;
        m[11] = 0.0f;

        return *this;
    }

    template <class U>
    inline U toUSDMatrix() const
    {
        U matrix;
        matrix[0][0] = static_cast<typename U::ScalarType>(m[0]);
        matrix[0][1] = static_cast<typename U::ScalarType>(m[1]);
        matrix[0][2] = static_cast<typename U::ScalarType>(m[2]);
        matrix[0][3] = static_cast<typename U::ScalarType>(m[3]);

        matrix[1][0] = static_cast<typename U::ScalarType>(m[4]);
        matrix[1][1] = static_cast<typename U::ScalarType>(m[5]);
        matrix[1][2] = static_cast<typename U::ScalarType>(m[6]);
        matrix[1][3] = static_cast<typename U::ScalarType>(m[7]);

        matrix[2][0] = static_cast<typename U::ScalarType>(m[8]);
        matrix[2][1] = static_cast<typename U::ScalarType>(m[9]);
        matrix[2][2] = static_cast<typename U::ScalarType>(m[10]);
        matrix[2][3] = static_cast<typename U::ScalarType>(m[11]);

        matrix[3][0] = static_cast<typename U::ScalarType>(m[12]);
        matrix[3][1] = static_cast<typename U::ScalarType>(m[13]);
        matrix[3][2] = static_cast<typename U::ScalarType>(m[14]);
        matrix[3][3] = static_cast<typename U::ScalarType>(m[15]);

        return matrix;
    }

    template <class U>
    inline void toArray(U* matrix)
    {
        for (size_t idx = 0; idx < 16; ++idx)
        {
            matrix[idx] = static_cast<U>(m[idx]);
        }
    }

    template <class U>
    static inline XRMatrix fromUSDMatrix(const U& matrix)
    {
        XRMatrix xrMatrix;

        xrMatrix.m[0] = static_cast<float>(matrix[0][0]);
        xrMatrix.m[1] = static_cast<float>(matrix[0][1]);
        xrMatrix.m[2] = static_cast<float>(matrix[0][2]);
        xrMatrix.m[3] = static_cast<float>(matrix[0][3]);

        xrMatrix.m[4] = static_cast<float>(matrix[1][0]);
        xrMatrix.m[5] = static_cast<float>(matrix[1][1]);
        xrMatrix.m[6] = static_cast<float>(matrix[1][2]);
        xrMatrix.m[7] = static_cast<float>(matrix[1][3]);

        xrMatrix.m[8] = static_cast<float>(matrix[2][0]);
        xrMatrix.m[9] = static_cast<float>(matrix[2][1]);
        xrMatrix.m[10] = static_cast<float>(matrix[2][2]);
        xrMatrix.m[11] = static_cast<float>(matrix[2][3]);

        xrMatrix.m[12] = static_cast<float>(matrix[3][0]);
        xrMatrix.m[13] = static_cast<float>(matrix[3][1]);
        xrMatrix.m[14] = static_cast<float>(matrix[3][2]);
        xrMatrix.m[15] = static_cast<float>(matrix[3][3]);

        xrMatrix.validity = XRMatrixValidity::eValidityAll;

        return xrMatrix;
    }

    template <class U>
    static inline XRMatrix fromArray(const U& array)
    {
        XRMatrix xrMatrix;

        for (size_t idx = 0; idx < 16; ++idx)
        {
            xrMatrix.m[idx] = static_cast<float>(array[idx]);
        }

        xrMatrix.validity = XRMatrixValidity::eValidityAll;

        return xrMatrix;
    }

    inline XRMatrix operator*(const XRMatrix& mat)
    {
        return fromUSDMatrix(toUSDMatrix<usdrt::GfMatrix4f>() * mat.toUSDMatrix<usdrt::GfMatrix4f>());
    }

    inline void print(const char* label) const
    {
        CARB_LOG_INFO(
            "%s = (%s) [ %5.3f %5.3f %5.3f %5.3f | %5.3f %5.3f %5.3f %5.3f | %5.3f %5.3f %5.3f %5.3f | %5.3f %5.3f %5.3f %5.3f]",
            label, validity == XRMatrixValidity::eValidityAll ? "valid" : "invalid", m[0], m[1], m[2], m[3], m[4], m[5],
            m[6], m[7], m[8], m[9], m[10], m[11], m[12], m[13], m[14], m[15]);
    }

    inline void printWarn(const char* label) const
    {
        CARB_LOG_WARN(
            "%s = (%s) [ %5.3f %5.3f %5.3f %5.3f | %5.3f %5.3f %5.3f %5.3f | %5.3f %5.3f %5.3f %5.3f | %5.3f %5.3f %5.3f %5.3f]",
            label, validity == XRMatrixValidity::eValidityAll ? "valid" : "invalid", m[0], m[1], m[2], m[3], m[4], m[5],
            m[6], m[7], m[8], m[9], m[10], m[11], m[12], m[13], m[14], m[15]);
    }

    inline XRMatrix scaleOrigin(float scale) const
    {
        XRMatrix xrMatrix = *this;
        xrMatrix.m[12] = scale * xrMatrix.m[12];
        xrMatrix.m[13] = scale * xrMatrix.m[13];
        xrMatrix.m[14] = scale * xrMatrix.m[14];

        return xrMatrix;
    }

    inline XRMatrix normalizeOrientation(float finalLength = 1.0f) const
    {
        XRMatrix xrMatrix = *this;

        float rightFactor =
            1.0f /
            std::sqrt(xrMatrix.m[0] * xrMatrix.m[0] + xrMatrix.m[1] * xrMatrix.m[1] + xrMatrix.m[2] * xrMatrix.m[2]) *
            finalLength;
        xrMatrix.m[0] *= rightFactor;
        xrMatrix.m[1] *= rightFactor;
        xrMatrix.m[2] *= rightFactor;

        float upFactor =
            1.0f /
            std::sqrt(xrMatrix.m[4] * xrMatrix.m[4] + xrMatrix.m[5] * xrMatrix.m[5] + xrMatrix.m[6] * xrMatrix.m[6]) *
            finalLength;
        xrMatrix.m[4] *= upFactor;
        xrMatrix.m[5] *= upFactor;
        xrMatrix.m[6] *= upFactor;

        float forwardFactor =
            1.0f /
            std::sqrt(xrMatrix.m[8] * xrMatrix.m[8] + xrMatrix.m[9] * xrMatrix.m[9] + xrMatrix.m[10] * xrMatrix.m[10]) *
            finalLength;
        xrMatrix.m[8] *= forwardFactor;
        xrMatrix.m[9] *= forwardFactor;
        xrMatrix.m[10] *= forwardFactor;

        return xrMatrix;
    }
};

constexpr XRMatrix kXRMatrixIdentity = { { 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1 },
                                         XRMatrixValidity::eValidityAll };

constexpr XRMatrix kXRMatrixInvalid = { { 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1 },
                                        XRMatrixValidity::eValidityNone };


inline bool operator==(const XRMatrix& a, const XRMatrix& b)
{
    for (uint32_t idx = 0; idx < 16; ++idx)
    {
        if (a.m[idx] != b.m[idx])
        {
            return false;
        }
    }

    return true;
}

inline bool operator!=(const XRMatrix& a, const XRMatrix& b)
{
    return !(a == b);
}


struct XRCamera
{
    // Location and direction the camera is watching
    XRMatrix pose;

    // Left and Right field of view (view frustum is not symmetric, so left is .x and right is .y)
    carb::Float2 tangentX;

    // Top and Bottom field of view (view frustum is not symmetric, so top is .x and bottom is .y)
    carb::Float2 tangentY;
};

inline bool operator==(XRCamera a, XRCamera b)
{
    return a.pose == b.pose && a.tangentX.x == b.tangentX.x && a.tangentX.y == b.tangentX.y &&
           a.tangentY.x == b.tangentY.x && a.tangentY.y == b.tangentY.y;
}

inline bool operator!=(XRCamera a, XRCamera b)
{
    return !(a == b);
}


// validity check functions
/**
 * Check if a vector is valid (has no NaN's)
 */
inline bool isValid(carb::Float3 vec)
{
    return (!std::isnan(vec.x)) && (!std::isnan(vec.y)) && (!std::isnan(vec.z));
}

/**
 * Check if a resolution is valid (size != 0)
 */
inline bool isValidResolution(carb::Uint2 res)
{
    return res.x != 0 && res.y != 0;
}

/**
 * Check if the desired XRMatrixValidity flags include all of the requested components
 */
inline bool isValid(XRMatrixValidity inValidity, XRMatrixValidity componentsToCheck = XRMatrixValidity::eValidityAll)
{
    return (inValidity & componentsToCheck) == componentsToCheck;
}

/**
 * Check if the desired XRMatrix validity flags include all of the requested components
 */
inline bool isValid(const XRMatrix& matrix, XRMatrixValidity componentsToCheck = XRMatrixValidity::eValidityAll)
{
    return (matrix.validity & componentsToCheck) == componentsToCheck;
}

/**
 * Normalizes the orientation vectors (basis) of an XRMatrix
 *
 * Does not ensure they're orthogonal, does not effect the position vector
 */


/**
 * Takes a Y-up or Z-up matrix and switches to the other
 *
 * This is for standard matrices where X, Y, Z and pose are all column vectors.
 */
inline XRMatrix flipYZ(const XRMatrix& matrix)
{
    XRMatrix res = matrix;

    res.m[4] = -matrix.m[8];
    res.m[5] = -matrix.m[9];
    res.m[6] = -matrix.m[10];
    res.m[7] = -matrix.m[11];

    res.m[8] = matrix.m[4];
    res.m[9] = matrix.m[5];
    res.m[10] = matrix.m[6];
    res.m[11] = matrix.m[7];

    return res;
}

/**
 * Computes a non-symmetric projection matrix given an XRCamera and clipping planes.
 */
inline XRMatrix getProjMatrixFromCamera(const XRCamera& camera, float zNear, float zFar)
{
    // See source/plugins/omni.kit/FreeCamera.cpp, where it explains reverse Z:
    //
    // NOTE: this creates normalized clip coordinates with values between 0 (far) and 1 (near). Reversed Z.
    // The reason for this is that reversed Z gives better Z resolution esp when the far plane, is large.
    // https://developer.nvidia.com/content/depth-precision-visualized
    //
    // This only effects elements [2][2] (10) and [3][2] (14)


    float idx = 1.0f / (camera.tangentX.y - camera.tangentX.x);
    float idy = 1.0f / (camera.tangentY.y - camera.tangentY.x);
    float idz = 1.0f / (zFar - zNear);
    float sx = camera.tangentX.y + camera.tangentX.x;
    float sy = camera.tangentY.y + camera.tangentY.x;

    XRMatrix mat;
    mat.m[0] = 2.0f * idx;
    mat.m[1] = 0.0f;
    mat.m[2] = 0.0f;
    mat.m[3] = 0.0f;

    mat.m[4] = 0.0f;
    mat.m[5] = 2.0f * idy;
    mat.m[6] = 0.0f;
    mat.m[7] = 0.0f;

    mat.m[8] = sx * idx;
    mat.m[9] = sy * idy;
    mat.m[10] = zNear * idz;
    mat.m[11] = -1.0f;

    mat.m[12] = 0.0f;
    mat.m[13] = 0.0f;
    mat.m[14] = zFar * zNear * idz;
    mat.m[15] = 0.0f;

    mat.validity = XRMatrixValidity::eValidityAll;
    return mat;
}

/**
 * Checks if a pose is valid (that it has no NaN or zero columns or other problematic aspects)
 */
template <class U>
bool checkUSDMatrixIsSafe(const U& mat)
{
    if (mat.GetRow(0)[0] == 0. && (mat.GetRow(0)[1]) == 0. && mat.GetRow(0)[2] == 0. && mat.GetRow(0)[3] == 0.)
    {
        return false;
    }
    if (mat.GetRow(1)[0] == 0. && mat.GetRow(1)[1] == 0. && mat.GetRow(1)[2] == 0. && mat.GetRow(1)[3] == 0.)
    {
        return false;
    }
    if (mat.GetRow(2)[0] == 0. && mat.GetRow(2)[1] == 0. && mat.GetRow(2)[2] == 0. && mat.GetRow(2)[3] == 0.)
    {
        return false;
    }

    return true;
}

/**
 * Checks if a pose is valid (that it has no NaN or zero columns or other problematic aspects)
 */
inline XRMatrixValidity checkMatrixValidity(const XRMatrix& matrix, bool allowZeroColumns = false)
{
    XRMatrixValidity ret = XRMatrixValidity::eValidityAll;

    carb::Float3 right = matrix.getRight();
    carb::Float3 up = matrix.getUp();
    carb::Float3 forward = matrix.getForward();
    carb::Float3 origin = matrix.getOrigin();

    if (!allowZeroColumns)
    {

        if (forward.x == 0.0f && forward.y == 0.0f && forward.z == 0.0f)
        {
            ret &= ~XRMatrixValidity::eValidityForward;
        }

        if (up.x == 0.0f && up.y == 0.0f && up.z == 0.0f)
        {
            ret &= ~XRMatrixValidity::eValidityUp;
        }

        if (right.x == 0.0f && right.y == 0.0f && right.z == 0.0f)
        {
            ret &= ~XRMatrixValidity::eValidityRight;
        }
        // origin is ok if zero
    }

    // check NaN's
    {
        if (std::isnan(forward.x) || std::isnan(forward.y) || std::isnan(forward.z))
        {
            ret &= ~XRMatrixValidity::eValidityForward;
        }
        if (std::isnan(up.x) || std::isnan(up.y) || std::isnan(up.z))
        {
            ret &= ~XRMatrixValidity::eValidityUp;
        }
        if (std::isnan(right.x) || std::isnan(right.y) || std::isnan(right.z))
        {
            ret &= ~XRMatrixValidity::eValidityRight;
        }
        if (std::isnan(origin.x) || std::isnan(origin.y) || std::isnan(origin.z))
        {
            ret &= ~XRMatrixValidity::eValidityOrigin;
        }
    }

    return ret;
}

/**
 * Checks if a pose is valid (that it has no NaN or zero columns or other problematic aspects)
 */
inline bool checkMatrixIsSafe(const XRMatrix matrix, bool allowZeroColumns = false)
{
    return checkMatrixValidity(matrix, allowZeroColumns) == XRMatrixValidity::eValidityAll;
}

} // namespace xr
} // namespace kit
} // namespace omni
