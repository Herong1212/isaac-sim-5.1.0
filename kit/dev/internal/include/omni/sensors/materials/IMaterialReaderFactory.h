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
//! @brief Factory to instantiate the material reader.

#include <carb/Interface.h>

#include <omni/sensors/materials/IMaterialReader.h>


namespace omni
{
namespace sensors
{
namespace materials
{

/**
 * @brief an interface for a lidar profile reader factory
 *
 */
class IMaterialReaderFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::materials::IMaterialReaderFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual IMaterialReaderPtr createInstance() = 0;
};

} // namespace materials
} // namespace sensors
} // namespace omni
