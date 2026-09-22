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
//! @brief WPM (wave propagation model) Factory

#include <carb/Interface.h>

#include <omni/sensors/wpm_dev/IWpm.h>


namespace omni
{
namespace sensors
{
namespace wpm
{

/**
 * @brief an interface for a wave propagation models factory
 *
 */
class IWpmFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::nv::wpm::Iwpm_devFactory", 0, 1)

    /**
     * @brief creates a wave propagation model object instance
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual IWpmPtr createInstance() = 0;
};

} // namespace wpm
} // namespace sensors
} // namespace omni
