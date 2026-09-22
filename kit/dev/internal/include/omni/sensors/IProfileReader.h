// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//!
//! @brief ProfileReader: This class reads the different profiles (json) for the generic sensor simulation
//! plugins


#pragma once

#include <carb/IObject.h>

#include <omni/String.h>

#include <memory>
#include <string>

namespace omni
{
namespace sensors
{


enum class ProfileType : int
{
    LIDAR = 0,
    USS = 1,
    USS_INTERFERENCE = 2,
    RADAR = 3,
    WPM_RADAR = 4,
    IDS = 5
};

/**
 * IProfileReader, reads the json sensor profile
 */
class IProfileReader : public carb::IObject
{
public:
    virtual ~IProfileReader(){};

    /**
     * init document
     * @param json [in] json file name with path
     */
    virtual void init(const char* json, const ProfileType type) = 0;

    // TODO: maybe pass in init the profile name as a string and use the getProfile internally
    // Then, we don't need an extra call to getProfileJsonAtPaths -- but we lose the flexibility to pass just a read
    // json

    /**
     * get json from given filename -- looking at internal path or at given paths
     * @param json [in] json file name with path
     */
    virtual omni::string getProfileJsonAtPaths(const char* fileName, const ProfileType type) = 0;

    /**
     * returns if the document is valid
     */
    virtual bool isValid() const = 0;

    /**
     * returns the name of the sensor
     */
    virtual const char* name() const = 0;

    /**
     * returns the data size of the profile
     */
    virtual size_t dataSizeProfile() const = 0;

    /**
     * updates the given lidar profile object and returns if it was successful
     * @param profile pointer pointing to profile data blob
     */
    virtual bool update(void* profile) = 0;
};

/**
 * @brief a carb object pointer for an object that implements the IProfileReader interface
 *
 */
using IProfileReaderPtr = carb::ObjectPtr<IProfileReader>;


/**
 * @brief an interface for profile reader factory
 *
 */
class IProfileReaderFactory
{
public:
    CARB_PLUGIN_INTERFACE("omni::sensors::IProfileReaderFactory", 0, 1)

    /**
     * @brief
     * @return a model object pointer if successful, empty/nullptr otherwise
     *
     * @note the caller owns the model
     */
    virtual IProfileReaderPtr createInstance() = 0;
};


} // namespace sensors
} // namespace omni
