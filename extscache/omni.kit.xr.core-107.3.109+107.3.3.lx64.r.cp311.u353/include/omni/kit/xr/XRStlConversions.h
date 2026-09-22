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

// Some utilities that make life a bit easier across ABIs when working with XR

#include <carb/Types.h>
#include <carb/utils/StringHelpers.h>

#include <omni/kit/xr/XRMath.h>
#include <omni/kit/xr/XRTypes.h>

#include <sstream>
#include <string>
#include <vector>

namespace omni
{
namespace kit
{
namespace xr
{

inline std::string convertFloat3ToString(carb::Float3 v)
{
    std::stringstream ss;
    ss << std::fixed << std::setprecision(2);
    ss << "(" << v.x << ", " << v.y << ", " << v.z << ")";
    return ss.str();
}

inline std::string convertXRMatrixToString(XRMatrix matrix)
{
    if (matrix.validity == XRMatrixValidity::eValidityNone)
    {
        return "<Invalid Matrix>";
    }

    std::stringstream ss;
    bool needComma = false;


    if (isValid(matrix, XRMatrixValidity::eValidityRight))
    {
        ss << std::fixed << std::setprecision(2);
        ss << "right: "
           << "(" << matrix.m[0] << ", " << matrix.m[1] << ", " << matrix.m[2] << ")";
        needComma = true;
    }

    if (isValid(matrix, XRMatrixValidity::eValidityUp))
    {
        ss << std::fixed << std::setprecision(2);
        if (needComma)
        {
            ss << ", ";
        }
        ss << "up: "
           << "(" << matrix.m[4] << ", " << matrix.m[5] << ", " << matrix.m[6] << ")";
        needComma = true;
    }

    if (isValid(matrix, XRMatrixValidity::eValidityForward))
    {
        ss << std::fixed << std::setprecision(2);
        if (needComma)
        {
            ss << ", ";
        }
        ss << "forward: "
           << "(" << -matrix.m[8] << ", " << -matrix.m[9] << ", " << -matrix.m[10] << ")";
        needComma = true;
    }

    if (isValid(matrix, XRMatrixValidity::eValidityOrigin))
    {
        ss << std::fixed << std::setprecision(2);
        if (needComma)
        {
            ss << ", ";
        }
        ss << "origin: "
           << "(" << matrix.m[12] << ", " << matrix.m[13] << ", " << matrix.m[14] << ")";
        needComma = true;
    }
    else
    {
        ss << "<unknown origin>";
    }

    return ss.str();
}

} // namespace xr
} // namespace kit
} // namespace omni
