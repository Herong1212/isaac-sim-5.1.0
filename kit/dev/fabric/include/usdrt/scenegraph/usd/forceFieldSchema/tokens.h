// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file forceFieldSchema/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class ForceFieldSchemaTokensType

/// Provides standard set of public tokens for ForceFieldSchema schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// ForceFieldSchemaTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use ForceFieldSchemaTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct ForceFieldSchemaTokensType
{
    ForceFieldSchemaTokensType();
    /// @brief "forceFieldBodies"
    ///
    /// This token is the instance name used to label all of the PhysxForceField collecitonAPI's.
    const TfToken forceFieldBodies;
    /// @brief "physxForceField"
    ///
    /// Property namespace prefix for the ForceFieldSchemaPhysxForceFieldRingAPI schema., Property namespace prefix for
    /// the ForceFieldSchemaPhysxForceFieldSpinAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldWindAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldNoiseAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldDragAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldLinearAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldPlanarAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldConicalAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldSphericalAPI schema., Property namespace prefix for the
    /// ForceFieldSchemaPhysxForceFieldAPI schema.
    const TfToken physxForceField;
    /// @brief "physxForceFieldConical:angle"
    ///
    /// ForceFieldSchemaPhysxForceFieldConicalAPI
    const TfToken physxForceFieldConicalAngle;
    /// @brief "physxForceFieldConical:constant"
    ///
    /// ForceFieldSchemaPhysxForceFieldConicalAPI
    const TfToken physxForceFieldConicalConstant;
    /// @brief "physxForceFieldConical:inverseSquare"
    ///
    /// ForceFieldSchemaPhysxForceFieldConicalAPI
    const TfToken physxForceFieldConicalInverseSquare;
    /// @brief "physxForceFieldConical:linear"
    ///
    /// ForceFieldSchemaPhysxForceFieldConicalAPI
    const TfToken physxForceFieldConicalLinear;
    /// @brief "physxForceFieldConical:linearFalloff"
    ///
    /// ForceFieldSchemaPhysxForceFieldConicalAPI
    const TfToken physxForceFieldConicalLinearFalloff;
    /// @brief "physxForceFieldConical:powerFalloff"
    ///
    /// ForceFieldSchemaPhysxForceFieldConicalAPI
    const TfToken physxForceFieldConicalPowerFalloff;
    /// @brief "physxForceFieldDrag:linear"
    ///
    /// ForceFieldSchemaPhysxForceFieldDragAPI
    const TfToken physxForceFieldDragLinear;
    /// @brief "physxForceFieldDrag:minimumSpeed"
    ///
    /// ForceFieldSchemaPhysxForceFieldDragAPI
    const TfToken physxForceFieldDragMinimumSpeed;
    /// @brief "physxForceFieldDrag:square"
    ///
    /// ForceFieldSchemaPhysxForceFieldDragAPI
    const TfToken physxForceFieldDragSquare;
    /// @brief "physxForceField:enabled"
    ///
    /// ForceFieldSchemaPhysxForceFieldAPI
    const TfToken physxForceFieldEnabled;
    /// @brief "physxForceFieldLinear:constant"
    ///
    /// ForceFieldSchemaPhysxForceFieldLinearAPI
    const TfToken physxForceFieldLinearConstant;
    /// @brief "physxForceFieldLinear:direction"
    ///
    /// ForceFieldSchemaPhysxForceFieldLinearAPI, ForceFieldSchemaPhysxForceFieldConicalAPI
    const TfToken physxForceFieldLinearDirection;
    /// @brief "physxForceFieldLinear:inverseSquare"
    ///
    /// ForceFieldSchemaPhysxForceFieldLinearAPI
    const TfToken physxForceFieldLinearInverseSquare;
    /// @brief "physxForceFieldLinear:linear"
    ///
    /// ForceFieldSchemaPhysxForceFieldLinearAPI
    const TfToken physxForceFieldLinearLinear;
    /// @brief "physxForceFieldNoise:amplitude"
    ///
    /// ForceFieldSchemaPhysxForceFieldNoiseAPI
    const TfToken physxForceFieldNoiseAmplitude;
    /// @brief "physxForceFieldNoise:drag"
    ///
    /// ForceFieldSchemaPhysxForceFieldNoiseAPI
    const TfToken physxForceFieldNoiseDrag;
    /// @brief "physxForceFieldNoise:frequency"
    ///
    /// ForceFieldSchemaPhysxForceFieldNoiseAPI
    const TfToken physxForceFieldNoiseFrequency;
    /// @brief "physxForceFieldPlanar:constant"
    ///
    /// ForceFieldSchemaPhysxForceFieldPlanarAPI
    const TfToken physxForceFieldPlanarConstant;
    /// @brief "physxForceFieldPlanar:inverseSquare"
    ///
    /// ForceFieldSchemaPhysxForceFieldPlanarAPI
    const TfToken physxForceFieldPlanarInverseSquare;
    /// @brief "physxForceFieldPlanar:linear"
    ///
    /// ForceFieldSchemaPhysxForceFieldPlanarAPI
    const TfToken physxForceFieldPlanarLinear;
    /// @brief "physxForceFieldPlanar:normal"
    ///
    /// ForceFieldSchemaPhysxForceFieldPlanarAPI
    const TfToken physxForceFieldPlanarNormal;
    /// @brief "physxForceField:position"
    ///
    /// ForceFieldSchemaPhysxForceFieldAPI
    const TfToken physxForceFieldPosition;
    /// @brief "physxForceField:range"
    ///
    /// ForceFieldSchemaPhysxForceFieldAPI
    const TfToken physxForceFieldRange;
    /// @brief "physxForceFieldRing:constant"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingConstant;
    /// @brief "physxForceFieldRing:inverseSquare"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingInverseSquare;
    /// @brief "physxForceFieldRing:linear"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingLinear;
    /// @brief "physxForceFieldRing:normalAxis"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingNormalAxis;
    /// @brief "physxForceFieldRing:radius"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingRadius;
    /// @brief "physxForceFieldRing:spinConstant"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingSpinConstant;
    /// @brief "physxForceFieldRing:spinInverseSquare"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingSpinInverseSquare;
    /// @brief "physxForceFieldRing:spinLinear"
    ///
    /// ForceFieldSchemaPhysxForceFieldRingAPI
    const TfToken physxForceFieldRingSpinLinear;
    /// @brief "physxForceFieldSpherical:constant"
    ///
    /// ForceFieldSchemaPhysxForceFieldSphericalAPI
    const TfToken physxForceFieldSphericalConstant;
    /// @brief "physxForceFieldSpherical:inverseSquare"
    ///
    /// ForceFieldSchemaPhysxForceFieldSphericalAPI
    const TfToken physxForceFieldSphericalInverseSquare;
    /// @brief "physxForceFieldSpherical:linear"
    ///
    /// ForceFieldSchemaPhysxForceFieldSphericalAPI
    const TfToken physxForceFieldSphericalLinear;
    /// @brief "physxForceFieldSpin:constant"
    ///
    /// ForceFieldSchemaPhysxForceFieldSpinAPI
    const TfToken physxForceFieldSpinConstant;
    /// @brief "physxForceFieldSpin:inverseSquare"
    ///
    /// ForceFieldSchemaPhysxForceFieldSpinAPI
    const TfToken physxForceFieldSpinInverseSquare;
    /// @brief "physxForceFieldSpin:linear"
    ///
    /// ForceFieldSchemaPhysxForceFieldSpinAPI
    const TfToken physxForceFieldSpinLinear;
    /// @brief "physxForceFieldSpin:spinAxis"
    ///
    /// ForceFieldSchemaPhysxForceFieldSpinAPI
    const TfToken physxForceFieldSpinSpinAxis;
    /// @brief "physxForceField:surfaceAreaScaleEnabled"
    ///
    /// ForceFieldSchemaPhysxForceFieldAPI
    const TfToken physxForceFieldSurfaceAreaScaleEnabled;
    /// @brief "physxForceField:surfaceSampleDensity"
    ///
    /// ForceFieldSchemaPhysxForceFieldAPI
    const TfToken physxForceFieldSurfaceSampleDensity;
    /// @brief "physxForceFieldWind:averageDirection"
    ///
    /// ForceFieldSchemaPhysxForceFieldWindAPI
    const TfToken physxForceFieldWindAverageDirection;
    /// @brief "physxForceFieldWind:averageSpeed"
    ///
    /// ForceFieldSchemaPhysxForceFieldWindAPI
    const TfToken physxForceFieldWindAverageSpeed;
    /// @brief "physxForceFieldWind:directionVariation"
    ///
    /// ForceFieldSchemaPhysxForceFieldWindAPI
    const TfToken physxForceFieldWindDirectionVariation;
    /// @brief "physxForceFieldWind:directionVariationFrequency"
    ///
    /// ForceFieldSchemaPhysxForceFieldWindAPI
    const TfToken physxForceFieldWindDirectionVariationFrequency;
    /// @brief "physxForceFieldWind:drag"
    ///
    /// ForceFieldSchemaPhysxForceFieldWindAPI
    const TfToken physxForceFieldWindDrag;
    /// @brief "physxForceFieldWind:speedVariation"
    ///
    /// ForceFieldSchemaPhysxForceFieldWindAPI
    const TfToken physxForceFieldWindSpeedVariation;
    /// @brief "physxForceFieldWind:speedVariationFrequency"
    ///
    /// ForceFieldSchemaPhysxForceFieldWindAPI
    const TfToken physxForceFieldWindSpeedVariationFrequency;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline ForceFieldSchemaTokensType::ForceFieldSchemaTokensType()
    : forceFieldBodies("forceFieldBodies"),
      physxForceField("physxForceField"),
      physxForceFieldConicalAngle("physxForceFieldConical:angle"),
      physxForceFieldConicalConstant("physxForceFieldConical:constant"),
      physxForceFieldConicalInverseSquare("physxForceFieldConical:inverseSquare"),
      physxForceFieldConicalLinear("physxForceFieldConical:linear"),
      physxForceFieldConicalLinearFalloff("physxForceFieldConical:linearFalloff"),
      physxForceFieldConicalPowerFalloff("physxForceFieldConical:powerFalloff"),
      physxForceFieldDragLinear("physxForceFieldDrag:linear"),
      physxForceFieldDragMinimumSpeed("physxForceFieldDrag:minimumSpeed"),
      physxForceFieldDragSquare("physxForceFieldDrag:square"),
      physxForceFieldEnabled("physxForceField:enabled"),
      physxForceFieldLinearConstant("physxForceFieldLinear:constant"),
      physxForceFieldLinearDirection("physxForceFieldLinear:direction"),
      physxForceFieldLinearInverseSquare("physxForceFieldLinear:inverseSquare"),
      physxForceFieldLinearLinear("physxForceFieldLinear:linear"),
      physxForceFieldNoiseAmplitude("physxForceFieldNoise:amplitude"),
      physxForceFieldNoiseDrag("physxForceFieldNoise:drag"),
      physxForceFieldNoiseFrequency("physxForceFieldNoise:frequency"),
      physxForceFieldPlanarConstant("physxForceFieldPlanar:constant"),
      physxForceFieldPlanarInverseSquare("physxForceFieldPlanar:inverseSquare"),
      physxForceFieldPlanarLinear("physxForceFieldPlanar:linear"),
      physxForceFieldPlanarNormal("physxForceFieldPlanar:normal"),
      physxForceFieldPosition("physxForceField:position"),
      physxForceFieldRange("physxForceField:range"),
      physxForceFieldRingConstant("physxForceFieldRing:constant"),
      physxForceFieldRingInverseSquare("physxForceFieldRing:inverseSquare"),
      physxForceFieldRingLinear("physxForceFieldRing:linear"),
      physxForceFieldRingNormalAxis("physxForceFieldRing:normalAxis"),
      physxForceFieldRingRadius("physxForceFieldRing:radius"),
      physxForceFieldRingSpinConstant("physxForceFieldRing:spinConstant"),
      physxForceFieldRingSpinInverseSquare("physxForceFieldRing:spinInverseSquare"),
      physxForceFieldRingSpinLinear("physxForceFieldRing:spinLinear"),
      physxForceFieldSphericalConstant("physxForceFieldSpherical:constant"),
      physxForceFieldSphericalInverseSquare("physxForceFieldSpherical:inverseSquare"),
      physxForceFieldSphericalLinear("physxForceFieldSpherical:linear"),
      physxForceFieldSpinConstant("physxForceFieldSpin:constant"),
      physxForceFieldSpinInverseSquare("physxForceFieldSpin:inverseSquare"),
      physxForceFieldSpinLinear("physxForceFieldSpin:linear"),
      physxForceFieldSpinSpinAxis("physxForceFieldSpin:spinAxis"),
      physxForceFieldSurfaceAreaScaleEnabled("physxForceField:surfaceAreaScaleEnabled"),
      physxForceFieldSurfaceSampleDensity("physxForceField:surfaceSampleDensity"),
      physxForceFieldWindAverageDirection("physxForceFieldWind:averageDirection"),
      physxForceFieldWindAverageSpeed("physxForceFieldWind:averageSpeed"),
      physxForceFieldWindDirectionVariation("physxForceFieldWind:directionVariation"),
      physxForceFieldWindDirectionVariationFrequency("physxForceFieldWind:directionVariationFrequency"),
      physxForceFieldWindDrag("physxForceFieldWind:drag"),
      physxForceFieldWindSpeedVariation("physxForceFieldWind:speedVariation"),
      physxForceFieldWindSpeedVariationFrequency("physxForceFieldWind:speedVariationFrequency")
{
}

struct ForceFieldSchemaTokensTypeAccessor
{
    const ForceFieldSchemaTokensType* operator->()
    {
        static const ForceFieldSchemaTokensType tokens;
        return &tokens;
    }
};


inline ForceFieldSchemaTokensTypeAccessor ForceFieldSchemaTokens;


} // namespace usdrt
