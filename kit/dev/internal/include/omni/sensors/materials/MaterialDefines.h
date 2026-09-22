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

#include <omni/String.h>
#include <omni/sensors/cuda/CudaHelperMath.h>
#include <omni/sensors/materials/IMaterial.h>
#include <omni/sensors/materials/MaterialProperties.h>

#include <cstdint>

using curandStateType = void*;


namespace omni
{
namespace sensors
{
namespace materials
{

static constexpr char MECHANICAL_STRING[11] = "mechanical";
static constexpr char ELECTROMAGNETIC_STRING[16] = "electromagnetic";

enum WaveType : uint8_t
{
    WAVE_MECHANICAL,
    WAVE_ELECTROMAGNETIC
};


struct SpectralRange
{
    float wavelengthNm;
    float bandwidthFactor;
    WaveType waveType;

public:
    // Convenience constructors to avoid update cascade
    SpectralRange() : wavelengthNm(0.0f), bandwidthFactor(0.0f), waveType(WAVE_ELECTROMAGNETIC)
    {
    }
    SpectralRange(const float wavelengthNm)
        : wavelengthNm(wavelengthNm), bandwidthFactor(0.15f), waveType(WAVE_ELECTROMAGNETIC)
    {
    }
    SpectralRange(const float wavelengthNm, const WaveType waveType)
        : wavelengthNm(wavelengthNm), bandwidthFactor(0.15f), waveType(waveType)
    {
    }
    SpectralRange(const float wavelengthNm, const WaveType waveType, const float bandwidthFactor)
        : wavelengthNm(wavelengthNm), bandwidthFactor(bandwidthFactor), waveType(waveType)
    {
    }
};

struct NvMatConfig final : public IMaterialConfig
{
    omni::string classInfo; /**< (i.e. The name of material profile: "ConcreteRough") */
    SpectralRange spectralRange;
    float factor{ 0.f }; /**< constant factor applied to the ray props vector value*/
    float defaultLobeWidth{ 0.f }; /**< default lobewidth */
    float defaultThickness{ 0.f }; /**< default thickness */
    // This constructor has been added for convenience purposes (enables make_shared/make_unique)
    NvMatConfig(omni::string classInfo_,
                SpectralRange spectralRange_,
                const float factor_ = 1.f,
                const float lobewidth = 15.0f * PI / 36.0f,
                const float thickness = 0.2f)
        : classInfo{ classInfo_ },
          spectralRange{ spectralRange_ },
          factor(factor_),
          defaultLobeWidth(lobewidth),
          defaultThickness(thickness)
    {
    }

    explicit NvMatConfig(omni::string classInfo_) : classInfo{ classInfo_ }
    {
    }
};

enum class NvMatInFlags : uint8_t
{
    CALC_R = 1, /**< compute mirror reflectance component */
    CALC_T = 2, /**< computes transmission component */
    CALC_PHASE_AND_POLARIZED = 4, /**< computes the requested reflection/transmission maintaining polarization and
                                    phase*/
    CALC_INTERNAL_TERMS = 8, /**< computes inter reflection and transmission contributions */
};

NV_HOSTDEVICE
inline std::underlying_type<NvMatInFlags>::type operator|(NvMatInFlags lhs, NvMatInFlags rhs)
{
    return static_cast<std::underlying_type<NvMatInFlags>::type>(lhs) |
           static_cast<std::underlying_type<NvMatInFlags>::type>(rhs);
}

NV_HOSTDEVICE
inline std::underlying_type<NvMatInFlags>::type operator&(NvMatInFlags lhs, NvMatInFlags rhs)
{
    return static_cast<std::underlying_type<NvMatInFlags>::type>(lhs) &
           static_cast<std::underlying_type<NvMatInFlags>::type>(rhs);
}

struct NvMatRayProps
{
    // transmissive or reflectance
    float3 vector; /**< either field vector or 0-value,1 tetm[0],2 tetm[1] */
};

struct NvPolarizedRayProps : public NvMatRayProps
{
    // transmissive or reflectance
    // float4 complex jones vector is [A B], where A = x + yi, and B = z + wi, where x, y, z, w are the fields of
    // float4. Before and after the sample material shader, x and z are in orthogonal directions in 3d space, defined
    // by:
    // - x direction is horizontal in the world xy-plane. Defined as || k x world-z ||, where k is normalized ray
    // direction.
    // - z direction is e1 x k.
    // Inside the sample material shader, the coordinate frame is rotated such that x and z are aligned with
    // the s and p polarization directions.
    float4 coherent{ make_float4(0.f, 0.f, 0.f, 0.f) }; /** complex (amplitude and phase) jones vector of specular
                                                           component */
    float4 crossCoherent{ make_float4(0.f, 0.f, 0.f, 0.f) }; /** complex jones vector specular component - in an
                                                                orthogonal direction to specular0. specular1 = 0 if
                                                                polarized */
    float2 diffuse{ make_float2(0.f, 0.f) }; /** real (amplitude only) jones vector of diffuse component */
    float2 crossDiffuse{ make_float2(0.f, 0.f) }; /** real (amplitude only) jones vector of diffuse component - in an
                                                     orthogonal direction to diffuse0 */
};

struct NvMatInput
{
    float3 matNormal; /**< unit vector defining the surface normal at incidence hit point */
    float3 lookupRayDir; /**< unit vector defining the view direction for BSDF lookup */
    float3 hitPoint; /**< hit point of the material in same coordinates like ray */
    uint32_t materialId{ 0 }; /**< Id of current material intersected */
    float thickness{ 0 }; /**< thickness of material at hit point in normal direction */
    curandStateType randomState; /**< curand state */
    uint8_t flags{ 0 }; /** <specifies the types of bsdf components to compute */
    float3 incRayDir; /**< direction of the incident ray */
    float3 diffuseRefl{ make_float3(-0.5f, -0.5f, -0.5f) }; /**< visible band diffuse reflectance */
    float roughness{ 0.f };
    NvMatRayProps* incRayProps; /**< properties of the incident ray */
    uint32_t customPropsSize{ 0 };
    uint32_t preserveMaterialFlags{ 0xff };
    float distPrevHit{ 0 };
    float sourceDivergence{ 0.f }; /**< characterize beam divergence of source radiation */
    float3 vertexNormals[3]{ 0.f }; /**< normals of each vertex */
    float3 vertices[3]{ 0.f }; /**< triangle vertex */
};


struct NvMatOutput
{
    float3 exitPoint; /**< transmitted ray exit point in same coordinates like ray */
    float distThroughCurMat{ 0.f }; /**< propagated distance within material */
    uint32_t materialId{ 0 }; /**< Id of current material intersected */
    NvMatRayProps* lookupRayProps; /**< if length(view) != 0, view ray props, else rubbish */
    float3 reflRayDir; /**< if CALC_R, reflected ray direction, else rubbish */
    NvMatRayProps* reflRayProps; /**< if CALC_R, reflected ray props, else rubbish */
    float3 transRayDir; /**< if CALC_T, transmitted ray direction, else rubbish */
    NvMatRayProps* transRayProps; /**< if CALC_T, transmitted ray props, else rubbish */
    float outDivergence{ 0.f }; /**< the output divergence from boundary interface */
};

NV_HOSTDEVICE inline void initializePaintProperties(NvMatInput* in,
                                                    PaintVariantProperties& src,
                                                    PaintVariantProperties& dst,
                                                    uint32_t offset,
                                                    const bool retroAttribute = false)
{
    uint8_t* contextBuffer = reinterpret_cast<uint8_t*>(&src);
    float* albedos = reinterpret_cast<float*>(&contextBuffer[offset]);
    float* visColors = reinterpret_cast<float*>(&contextBuffer[offset + src.numPaintVariants * sizeof(float)]);

    dst = src;
    float* srcAlbedoPtr = src.diffuseAlbedo;
    float* srcVisColorPtr = src.visibleColor;

    dst.diffuseAlbedo = albedos;
    dst.visibleColor = visColors;
    src.diffuseAlbedo = srcAlbedoPtr;
    src.visibleColor = srcVisColorPtr;

    // If no visible reflectance color is requested, set thickness to 0 and set diffuse reflectance to white
    const bool noRefl{ in->diffuseRefl.x < 0.f };
    dst.thickness = noRefl ? 0.f : in->thickness;
    in->diffuseRefl = noRefl && retroAttribute ? make_float3(1.f, 1.f, 1.f) : 
                        ( noRefl ? make_float3(0.5f, 0.5f, 0.5f) : in->diffuseRefl);
}

//! Access helper
/**
 * @brief Gets pointer to the idx-th element in mat output array
 * @param matOutputs material outputs data blob
 * @param sizeCustomMatOut sizeof custome material output
 * @param idx desired element index
 * @return NvMatOutput*
 */
/// \cond DO_NOT_DOCUMENT
NV_HOSTDEVICE
/// \endcond
inline NvMatRayProps* getMatProps(NvMatRayProps* rayProps, const uint32_t sizeCustomRayProps, const uint32_t idx)
{
    // only needed if user extended!
    return (NvMatRayProps*)((char*)rayProps + idx * sizeCustomRayProps);
}

} // namespace materials
} // namespace sensors
} // namespace omni
