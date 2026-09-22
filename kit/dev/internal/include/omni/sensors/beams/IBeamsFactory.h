// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Factory to instantiate beams utility

#include "IBeams.h"

#include <carb/Interface.h>

namespace omni
{
namespace sensors
{
namespace beams
{

/**
 * @brief an interface for a beams factory
 *
 */
class IBeamsFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::beams::IBeamsFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual IBeamsPtr createInstance() = 0;
};

} // namespace beams
} // namespace sensors
} // namespace omni
