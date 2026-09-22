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
//! @brief MaterialReader: This class reads the different materials (json) for the generic material simulation support
//! plugin


#pragma once

#include <carb/IObject.h>

#include <omni/String.h>
#include <omni/sensors/materials/MaterialDefines.h>
#include <omni/sensors/materials/MaterialManager.h>
#include <omni/sensors/materials/MaterialProperties.h>

#include <memory>
#include <string>
#include <vector>

namespace omni
{
namespace sensors
{
namespace materials
{

/**
 * MaterialReader, reads the json sensor profile
 */
class IMaterialReader : public carb::IObject
{
public:
    virtual ~IMaterialReader(){};

    /**
     * initialize document
     */
    virtual void initialize() = 0;

    /**
     * return the material name
     */
    virtual omni::string readMaterialName() const = 0;

    /**
     * readJsonFile document
     * @param filePath [in] read json file name with path
     */
    virtual omni::string readJsonFile(const omni::string& filePath) const = 0;

    /**
     * readandParseJsonFile document
     * @param filePath [in] read json file name with path
     */
    virtual void readAndParseJsonFile(const omni::string& filePath) const = 0;

    /**
     * readandParseCoatingVariantJsonFile document
     * @param filePath [in] read a coating variant json file name with path
     */
    virtual void readAndParseCoatingVariantJsonFile(const omni::string& filePath) const = 0;

    /**
     * readandParsePaintVariantJsonFile document
     * @param filePath [in] read a paint variant json file name with path
     */
    virtual void readAndParsePaintVariantJsonFile(const omni::string& filePath) const = 0;

    /**
     * parseJson document
     * @param json [in] parse the json string
     */
    virtual void parseJson(const omni::string& json) const = 0;

    /**
     * parseCoatingVariantJson document
     * @param json [in] parse the coating variant json string
     */
    virtual void parseCoatingVariantJson(const omni::string& json) const = 0;

    /**
     * parsePaintVariantJson document
     * @param json [in] parse the paint variant json string
     */
    virtual void parsePaintVariantJson(const omni::string& json) const = 0;

    /**
     * returns a specific entry within the json file
     */
    virtual bool readEntryValue(void* returnValue, const std::vector<omni::string>& nestedTokens) const = 0;

    /**
     * returns a bulk and spectral properties within the material json file
     */
    virtual bool readMaterialProperties(BulkProperties& bulkProperties,
                                        SpectralProperties& spectralProperties,
                                        const double wavelength,
                                        const float bandwidth,
                                        WaveType type) const = 0;

    /**
     * returns a coating and paint variant properties
     */
    virtual bool readVariantProperties(CoatingVariantProperties& coatingProperties,
                                       PaintVariantProperties& paintProperties,
                                       const double wavelength,
                                       const float bandwidth,
                                       WaveType type) const = 0;

    /**
     * returns the attribute material properties
     */
    virtual bool readAttributeProperties(AttributeProperties& attributeProperties,
                                         const double wavelength,
                                         const float bandwidth,
                                         WaveType type) const = 0;

    /**
     * returns a non visual material mapping
     */
    virtual bool readMaterialMapping(MaterialMap& materialMap,
                                     const SpectralRange& spectralRange,
                                     omni::string baseRemapping = omni::string(),
                                     omni::string bsdfRemapping = omni::string()) const = 0;

    /**
     * updates elements of an existing non visual material mapping
     */
    virtual bool updateMaterialMapping(MaterialMap& materialMap,
                                     const SpectralRange& spectralRange,
                                     omni::string baseRemapping = omni::string(),
                                     omni::string bsdfRemapping = omni::string()) const = 0;

    /**
     * returns the number of paint variants for a given spectrum
     */
    virtual uint32_t getNumPaintVariantProperties(const double wavelength, const float bandwidth) const = 0;
};

/**
 * @brief a carb object pointer for an object that implements the IMaterialReaderPtr interface
 *
 */
using IMaterialReaderPtr = carb::ObjectPtr<IMaterialReader>;

} // namespace materials
} // namespace sensors
} // namespace omni
