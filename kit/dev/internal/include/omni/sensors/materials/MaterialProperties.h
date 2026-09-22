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

//-----------------------------------------------------------------------------
// Bulk material properties. These are wavelength independent
struct BulkProperties
{
    float solarAbsorptivity{ 0.0f }; // [1] - unitless
    float thermalConductivity{ 0.0f }; // [W/m/K]
    float specificHeat{ 0.0f }; // [J/kg/K]
    float density{ 0.0f }; // [kg/m**3]
    float compressibility{ 0.0f }; // [1/Pa]
    float thickness{ 0.0f }; // [m]
    float porosity{ 1.0f }; // [1] - unitless
};

//-----------------------------------------------------------------------------
// Spectral material properties. These are wavelength dependent
struct SpectralProperties
{
    float wavelength{ 0.0f }; // [m]
    float permittivityReal{ 1.0f }; // [1]
    float permittivityImag{ 0.0f }; // [1]
    float permeabilityReal{ 1.0f }; // [1]
    float permeabilityImag{ 0.0f }; // [1]
    float refractiveIndexReal{ 1.0f }; // [1]
    float refractiveIndexImag{ 0.0f }; // [1]
    float lobewidth{ 0.0f }; // [rad]
    float diffuseAlbedo{ 1.0f }; // [1]
    float emissivity{ 0.0f }; // [1]
    float baseRCS{ 0.0f }; // [m**2]
};

//-----------------------------------------------------------------------------
// Paint and coating for material variant properties. These are wavelength dependent
struct CoatingVariantProperties
{
    float wavelength{ 0.0f }; // [m]
    float permittivityReal{ 1.0f }; // [1]
    float permittivityImag{ 0.0f }; // [1]
    float permeabilityReal{ 1.0f }; // [1]
    float permeabilityImag{ 0.0f }; // [1]
    float refractiveIndexReal{ 1.0f }; // [1]
    float refractiveIndexImag{ 0.0f }; // [1]
    float lobewidthFraction{ 1.0f }; // [1]
    float thickness{ 0.0f }; // [m]
    float diffuseAlbedo{ 1.0f }; // [1]
};

struct PaintVariantProperties
{
    float wavelength{ 0.0f }; // [m]
    float permittivityReal{ 1.0f }; // [1]
    float permittivityImag{ 0.0f }; // [1]
    float permeabilityReal{ 1.0f }; // [1]
    float permeabilityImag{ 0.0f }; // [1]
    float refractiveIndexReal{ 1.0f }; // [1]
    float refractiveIndexImag{ 0.0f }; // [1]
    float lobewidthFraction{ 1.0f }; // [1]
    float thickness{ 0.0f }; // [m]
    unsigned int numPaintVariants{ 0 };
    float* diffuseAlbedo { nullptr }; // [1]
    float* visibleColor{ nullptr }; // [1]
};

//-----------------------------------------------------------------------------
// Spectral attribute material properties. These are wavelength dependent
struct AttributeProperties
{
    BulkProperties bulkProperties;
    SpectralProperties spectralProperties;
};
