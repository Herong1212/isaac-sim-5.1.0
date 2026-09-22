// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

// Getters for shared OpenXR-related singletons

#include <carb/Defines.h>
#include <carb/Interface.h>
#include <carb/Types.h>

#include <omni/kit/xr/system/openxr/IOpenXRComponent.h>

namespace omni
{
namespace kit
{
namespace xr
{
namespace openxr
{

class IOpenXRExtension_v1
{
public:
    CARB_PLUGIN_INTERFACE("omni::kit::xr::openxr::IOpenXRExtension_v1", 1, 0)

    /**
     * @brief This function gets the OpenXR component registry singleton
     *
     * @return pointer to OpenXR component registry singleton
     *
     * Note: use the function below to get reference counted singleton object
     */
    IOpenXRComponentRegistry_v1*(CARB_ABI* getComponentRegistry_abi)();

    /**
     * @brief This function gets the OpenXR component registry singleton
     *
     * @return pointer to OpenXR component registry singleton
     */
    inline IOpenXRComponentRegistryPtr getComponentRegistry()
    {
        return omni::core::steal(getComponentRegistry_abi());
    }
};

} // namespace openxr
} // namespace xr
} // namespace kit
} // namespace omni
