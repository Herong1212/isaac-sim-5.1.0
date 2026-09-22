// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Utility for non-idealized beams, e.g., usable for simulating partial beam coverage

#include "BeamTypes.h"

#include <carb/IObject.h>

#include <omni/sensors/cuda/CudaHelperDecl.h>
#include <omni/sensors/materials/MaterialManager.h>

namespace omni
{
namespace sensors
{
namespace beams
{

/**
 * @brief Beams interface. Users can create objects that implement this interface by acquiring the
 * IBeamsFactory carbonite interface and using the createInstance() method. The Beams utility can be used for modeling
 * non-idealized beams.
 */
class IBeams : public carb::IObject
{
public:
    virtual ~IBeams(){};

    /**
     * @brief Sets the cudaDevice and, potentially, handles the gpu migration
     * @param cudaDevice current cuda device id
     */
    virtual void setCudaDevice(int32_t cudaDevice) = 0;

    /**
     * @brief Sets the cudaStream
     * @param cudaStream current cudaStream
     */
    virtual void setCudaStream(void* cudaStream) = 0;

    /**
     * @brief Initializes the utility and returns the pointer to device side config
     * @param div Beam divergence parameter
     * @param base BaseConfig
     * @return Config*
     */
    virtual Config* init(const BeamDivergence& div, const BaseConfig& base) = 0;

    /**
     * @brief Initializes the utility and returns the pointer to device side config
     * @param waist Beam waist parameter
     * @param base BaseConfig
     * @return Config*
     */
    virtual Config* init(const BeamWaist& waist, const BaseConfig& base) = 0;

    /**
     * @brief Returns the data pointer to the device side array of base rays
     * @return CentralBaseRay*
     */
    virtual BeamInputs* getBeamInputs() const = 0;

    /**
     * @brief Returns true if utility is initialized
     * @return bool
     */
    virtual bool initialized() const = 0;

    /**
     * @brief sets up a material map, with this interface the user can map specific RtxSensor MaterialIds, to
     * specific material names.
     *
     * @param matId an array of RtxSensor Material Ids
     * @param matDesc an array of MaterialDesc structs
     * @param numMats number of elements n the arrays (both arrays should match in length)
     * @return bool
     */
    virtual bool setupMaterials(const uint32_t* matId,
                                const omni::sensors::materials::MaterialDesc* matDesc,
                                uint32_t numMats) = 0;

    /**
     * @brief fills Rtx sensor firings
     * @param firings pointer to device side firings array
     * @param numBeams current number of emitters to be filled
     * @return void
     */
    virtual void fillFirings(rtx::rtxsensor::RtxSensorFiring* firings, uint32_t numBeams) = 0;

    /**
     * @brief processes Rtx sensor returns and returns the beam results
     * @param returns pointer to device side returns array
     * @return BatchResult*
     */
    virtual BatchResult* getResults(rtx::rtxsensor::RtxSensorReturn* returns) = 0;
};


using IBeamsPtr = carb::ObjectPtr<IBeams>;

} // namespace beams
} // namespace sensors
} // namespace omni
