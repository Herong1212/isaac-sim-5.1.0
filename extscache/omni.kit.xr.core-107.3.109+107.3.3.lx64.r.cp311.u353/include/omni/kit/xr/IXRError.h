// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

// Error/exception reporting for XR utilities

#include <carb/Defines.h>
#include <carb/Interface.h>

#include <omni/kit/xr/XRTypes.h>

namespace omni
{
namespace kit
{
namespace xr
{

class IXRError_v1
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::xr::IXRError_v1", 1, 0)

    /**
     * @brief Get description for an XRError return code
     *
     * @param xrError  error Code
     * @return string with error description
     */
    const char*(CARB_ABI* getXRErrorString_abi)(XRError xrError);

    /**
     * @brief Get description for an XRError return code
     *
     * @param xrError  error Code
     * @return string with error description
     */
    inline const char* getXRErrorString(XRError xrError)
    {
        return getXRErrorString_abi(xrError);
    }
};

using IXRError = IXRError_v1;

} // namespace xr
} // namespace kit
} // namespace omni
