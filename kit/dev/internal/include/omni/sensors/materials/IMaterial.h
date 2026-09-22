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
//! @brief IMaterial interface


#include <carb/Interface.h>

#include <cstdint>

namespace omni
{
namespace sensors
{
namespace materials
{

/**
 * @brief For materials that allow extended parameterization, configuration structs can inherit from this interface.
 * This is only *slightly* more typesafe than void pointers but IMaterialConfig is a polymorphic type which will allow
 * custom material implementations to `dynamic_cast` to their supported configuration types.
 */
struct IMaterialConfig
{
    // Allows materials to leverage dynamic_cast.
    /** @private */
    virtual void _unused()
    {
    }
};

struct IMaterial
{
    CARB_PLUGIN_INTERFACE("omni::sensors::materials::IMaterial", 0, 2);


    /**
     * @brief returns a hash of the material name that should uniquely identifies the material,
     * use carb::hashString as a way to get the hash
     *
     */
    uint64_t(CARB_ABI* getHash)();

    /**
     * @brief returns the size in bytes of the material context/parameters
     *
     */
    size_t(CARB_ABI* getContextSize)(const IMaterialConfig* materialConfig);

    /**
     * @brief gets the initialized material context
     * @param context pointer to a context that the material needs to init with its values
     * @param materialConfig material config for any specific parameterization
     */
    void(CARB_ABI* getContext)(void* context, const IMaterialConfig* materialConfig);

    /**
     * @brief gets the size info about the BSDF program supplied by this material
     * @param programSize size of the PTX string that represents the BSDF program
     * @param entrPointNameSize size of the name of the BSDF program
     */
    void(CARB_ABI* getBSDFProgramSizeInfo)(size_t& programSize, size_t& entryPointNameSize);

    /**
     * @brief gets the BSDF program itself
     * @param ptxString the PTX string that represents the BSDF program
     * @param entryPointName the name of the entrypoint of the BSDF program
     */
    void(CARB_ABI* getBSDFProgram)(char* const ptxString, char* const entryPointName);
};

} // namespace materials
} // namespace sensors
} // namespace omni
