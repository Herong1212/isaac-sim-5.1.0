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

//! @file
//!
//! @brief Factory to instantiate lidar profile reader.

#include <carb/Interface.h>

#include <omni/sensors/atmos/IAtmosCfgProvider.h>


namespace omni
{
namespace sensors
{
namespace atmos
{

/**
 * @brief an interface for a lidar profile reader factory
 *
 */
class IAtmosCfgProviderFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::atmos::IAtmosCfgProviderFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual IAtmosCfgProviderPtr createInstance() = 0;
};

} // namespace atmos
} // namespace sensors
} // namespace omni
