// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usdLux/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdLuxTokensType

/// Provides standard set of public tokens for UsdLux schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdLuxTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdLuxTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdLuxTokensType
{
    UsdLuxTokensType();
    /// @brief "angular"
    ///
    /// Possible value for UsdLuxDomeLight::GetInputsTextureFormatAttr()
    const TfToken angular;
    /// @brief "automatic"
    ///
    /// Possible value for UsdLuxDomeLight::GetInputsTextureFormatAttr(), Default value for
    /// UsdLuxDomeLight::GetInputsTextureFormatAttr()
    const TfToken automatic;
    /// @brief "collection:filterLink:includeRoot"
    ///
    /// UsdLuxLightFilter
    const TfToken collectionFilterLinkIncludeRoot;
    /// @brief "collection:lightLink:includeRoot"
    ///
    /// UsdLuxLightAPI
    const TfToken collectionLightLinkIncludeRoot;
    /// @brief "collection:shadowLink:includeRoot"
    ///
    /// UsdLuxLightAPI
    const TfToken collectionShadowLinkIncludeRoot;
    /// @brief "consumeAndContinue"
    ///
    /// Possible value for UsdLuxListAPI::GetLightListCacheBehaviorAttr(), Possible value for
    /// UsdLuxLightListAPI::GetLightListCacheBehaviorAttr()
    const TfToken consumeAndContinue;
    /// @brief "consumeAndHalt"
    ///
    /// Possible value for UsdLuxListAPI::GetLightListCacheBehaviorAttr(), Possible value for
    /// UsdLuxLightListAPI::GetLightListCacheBehaviorAttr()
    const TfToken consumeAndHalt;
    /// @brief "cubeMapVerticalCross"
    ///
    /// Possible value for UsdLuxDomeLight::GetInputsTextureFormatAttr()
    const TfToken cubeMapVerticalCross;
    /// @brief "CylinderLight"
    ///
    /// Default value for UsdLuxCylinderLight::GetLightShaderIdAttr()
    const TfToken cylinderLight;
    /// @brief "DiskLight"
    ///
    /// Default value for UsdLuxDiskLight::GetLightShaderIdAttr()
    const TfToken diskLight;
    /// @brief "DistantLight"
    ///
    /// Default value for UsdLuxDistantLight::GetLightShaderIdAttr()
    const TfToken distantLight;
    /// @brief "DomeLight"
    ///
    /// Default value for UsdLuxDomeLight::GetLightShaderIdAttr()
    const TfToken domeLight;
    /// @brief "extent"
    ///
    /// UsdLuxPortalLight
    const TfToken extent;
    /// @brief "filterLink"
    ///
    /// This token represents the collection name to use with UsdCollectionAPI to represent filter-linking of a
    /// UsdLuxLightFilter prim.
    const TfToken filterLink;
    /// @brief "geometry"
    ///
    /// UsdLuxGeometryLight
    const TfToken geometry;
    /// @brief "GeometryLight"
    ///
    /// Default value for UsdLuxGeometryLight::GetLightShaderIdAttr()
    const TfToken geometryLight;
    /// @brief "guideRadius"
    ///
    /// UsdLuxDomeLight
    const TfToken guideRadius;
    /// @brief "ignore"
    ///
    /// Possible value for UsdLuxListAPI::GetLightListCacheBehaviorAttr(), Possible value for
    /// UsdLuxLightListAPI::GetLightListCacheBehaviorAttr()
    const TfToken ignore;
    /// @brief "independent"
    ///
    /// Possible value for UsdLuxLightAPI::GetLightMaterialSyncModeAttr()
    const TfToken independent;
    /// @brief "inputs:angle"
    ///
    /// UsdLuxDistantLight
    const TfToken inputsAngle;
    /// @brief "inputs:color"
    ///
    /// UsdLuxLightAPI
    const TfToken inputsColor;
    /// @brief "inputs:colorTemperature"
    ///
    /// UsdLuxLightAPI
    const TfToken inputsColorTemperature;
    /// @brief "inputs:diffuse"
    ///
    /// UsdLuxLightAPI
    const TfToken inputsDiffuse;
    /// @brief "inputs:enableColorTemperature"
    ///
    /// UsdLuxLightAPI
    const TfToken inputsEnableColorTemperature;
    /// @brief "inputs:exposure"
    ///
    /// UsdLuxLightAPI
    const TfToken inputsExposure;
    /// @brief "inputs:height"
    ///
    /// UsdLuxRectLight
    const TfToken inputsHeight;
    /// @brief "inputs:intensity"
    ///
    /// UsdLuxDistantLight, UsdLuxLightAPI
    const TfToken inputsIntensity;
    /// @brief "inputs:length"
    ///
    /// UsdLuxCylinderLight
    const TfToken inputsLength;
    /// @brief "inputs:normalize"
    ///
    /// UsdLuxLightAPI
    const TfToken inputsNormalize;
    /// @brief "inputs:radius"
    ///
    /// UsdLuxCylinderLight, UsdLuxSphereLight, UsdLuxDiskLight
    const TfToken inputsRadius;
    /// @brief "inputs:shadow:color"
    ///
    /// UsdLuxShadowAPI
    const TfToken inputsShadowColor;
    /// @brief "inputs:shadow:distance"
    ///
    /// UsdLuxShadowAPI
    const TfToken inputsShadowDistance;
    /// @brief "inputs:shadow:enable"
    ///
    /// UsdLuxShadowAPI
    const TfToken inputsShadowEnable;
    /// @brief "inputs:shadow:falloff"
    ///
    /// UsdLuxShadowAPI
    const TfToken inputsShadowFalloff;
    /// @brief "inputs:shadow:falloffGamma"
    ///
    /// UsdLuxShadowAPI
    const TfToken inputsShadowFalloffGamma;
    /// @brief "inputs:shaping:cone:angle"
    ///
    /// UsdLuxShapingAPI
    const TfToken inputsShapingConeAngle;
    /// @brief "inputs:shaping:cone:softness"
    ///
    /// UsdLuxShapingAPI
    const TfToken inputsShapingConeSoftness;
    /// @brief "inputs:shaping:focus"
    ///
    /// UsdLuxShapingAPI
    const TfToken inputsShapingFocus;
    /// @brief "inputs:shaping:focusTint"
    ///
    /// UsdLuxShapingAPI
    const TfToken inputsShapingFocusTint;
    /// @brief "inputs:shaping:ies:angleScale"
    ///
    /// UsdLuxShapingAPI
    const TfToken inputsShapingIesAngleScale;
    /// @brief "inputs:shaping:ies:file"
    ///
    /// UsdLuxShapingAPI
    const TfToken inputsShapingIesFile;
    /// @brief "inputs:shaping:ies:normalize"
    ///
    /// UsdLuxShapingAPI
    const TfToken inputsShapingIesNormalize;
    /// @brief "inputs:specular"
    ///
    /// UsdLuxLightAPI
    const TfToken inputsSpecular;
    /// @brief "inputs:texture:file"
    ///
    /// UsdLuxDomeLight, UsdLuxRectLight
    const TfToken inputsTextureFile;
    /// @brief "inputs:texture:format"
    ///
    /// UsdLuxDomeLight
    const TfToken inputsTextureFormat;
    /// @brief "inputs:width"
    ///
    /// UsdLuxRectLight
    const TfToken inputsWidth;
    /// @brief "latlong"
    ///
    /// Possible value for UsdLuxDomeLight::GetInputsTextureFormatAttr()
    const TfToken latlong;
    /// @brief "light:filters"
    ///
    /// UsdLuxLightAPI
    const TfToken lightFilters;
    /// @brief "lightFilter:shaderId"
    ///
    /// UsdLuxLightFilter
    const TfToken lightFilterShaderId;
    /// @brief "lightLink"
    ///
    /// This token represents the collection name to use with UsdCollectionAPI to represent light-linking of a prim with
    /// an applied UsdLuxLightAPI.
    const TfToken lightLink;
    /// @brief "lightList"
    ///
    /// UsdLuxListAPI, UsdLuxLightListAPI
    const TfToken lightList;
    /// @brief "lightList:cacheBehavior"
    ///
    /// UsdLuxListAPI, UsdLuxLightListAPI
    const TfToken lightListCacheBehavior;
    /// @brief "light:materialSyncMode"
    ///
    /// UsdLuxVolumeLightAPI, UsdLuxMeshLightAPI, UsdLuxLightAPI
    const TfToken lightMaterialSyncMode;
    /// @brief "light:shaderId"
    ///
    /// UsdLuxPortalLight, UsdLuxDomeLight, UsdLuxGeometryLight, UsdLuxCylinderLight, UsdLuxSphereLight,
    /// UsdLuxRectLight, UsdLuxDiskLight, UsdLuxDistantLight, UsdLuxVolumeLightAPI, UsdLuxMeshLightAPI, UsdLuxLightAPI
    const TfToken lightShaderId;
    /// @brief "materialGlowTintsLight"
    ///
    /// Default value for UsdLuxVolumeLightAPI::GetLightMaterialSyncModeAttr(), Default value for
    /// UsdLuxMeshLightAPI::GetLightMaterialSyncModeAttr(), Possible value for
    /// UsdLuxLightAPI::GetLightMaterialSyncModeAttr()
    const TfToken materialGlowTintsLight;
    /// @brief "MeshLight"
    ///
    /// Default value for UsdLuxMeshLightAPI::GetLightShaderIdAttr()
    const TfToken meshLight;
    /// @brief "mirroredBall"
    ///
    /// Possible value for UsdLuxDomeLight::GetInputsTextureFormatAttr()
    const TfToken mirroredBall;
    /// @brief "noMaterialResponse"
    ///
    /// Possible value for UsdLuxLightAPI::GetLightMaterialSyncModeAttr(), Default value for
    /// UsdLuxLightAPI::GetLightMaterialSyncModeAttr()
    const TfToken noMaterialResponse;
    /// @brief "orientToStageUpAxis"
    ///
    /// This token represents the suffix for a UsdGeomXformOp used to orient a light with the stage's up axis.
    const TfToken orientToStageUpAxis;
    /// @brief "PortalLight"
    ///
    /// Default value for UsdLuxPortalLight::GetLightShaderIdAttr()
    const TfToken portalLight;
    /// @brief "portals"
    ///
    /// UsdLuxDomeLight
    const TfToken portals;
    /// @brief "RectLight"
    ///
    /// Default value for UsdLuxRectLight::GetLightShaderIdAttr()
    const TfToken rectLight;
    /// @brief "shadowLink"
    ///
    /// This token represents the collection name to use with UsdCollectionAPI to represent shadow-linking of a prim
    /// with an applied UsdLuxLightAPI.
    const TfToken shadowLink;
    /// @brief "SphereLight"
    ///
    /// Default value for UsdLuxSphereLight::GetLightShaderIdAttr()
    const TfToken sphereLight;
    /// @brief "treatAsLine"
    ///
    /// UsdLuxCylinderLight
    const TfToken treatAsLine;
    /// @brief "treatAsPoint"
    ///
    /// UsdLuxSphereLight
    const TfToken treatAsPoint;
    /// @brief "VolumeLight"
    ///
    /// Default value for UsdLuxVolumeLightAPI::GetLightShaderIdAttr()
    const TfToken volumeLight;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdLuxTokensType::UsdLuxTokensType()
    : angular("angular"),
      automatic("automatic"),
      collectionFilterLinkIncludeRoot("collection:filterLink:includeRoot"),
      collectionLightLinkIncludeRoot("collection:lightLink:includeRoot"),
      collectionShadowLinkIncludeRoot("collection:shadowLink:includeRoot"),
      consumeAndContinue("consumeAndContinue"),
      consumeAndHalt("consumeAndHalt"),
      cubeMapVerticalCross("cubeMapVerticalCross"),
      cylinderLight("CylinderLight"),
      diskLight("DiskLight"),
      distantLight("DistantLight"),
      domeLight("DomeLight"),
      extent("extent"),
      filterLink("filterLink"),
      geometry("geometry"),
      geometryLight("GeometryLight"),
      guideRadius("guideRadius"),
      ignore("ignore"),
      independent("independent"),
      inputsAngle("inputs:angle"),
      inputsColor("inputs:color"),
      inputsColorTemperature("inputs:colorTemperature"),
      inputsDiffuse("inputs:diffuse"),
      inputsEnableColorTemperature("inputs:enableColorTemperature"),
      inputsExposure("inputs:exposure"),
      inputsHeight("inputs:height"),
      inputsIntensity("inputs:intensity"),
      inputsLength("inputs:length"),
      inputsNormalize("inputs:normalize"),
      inputsRadius("inputs:radius"),
      inputsShadowColor("inputs:shadow:color"),
      inputsShadowDistance("inputs:shadow:distance"),
      inputsShadowEnable("inputs:shadow:enable"),
      inputsShadowFalloff("inputs:shadow:falloff"),
      inputsShadowFalloffGamma("inputs:shadow:falloffGamma"),
      inputsShapingConeAngle("inputs:shaping:cone:angle"),
      inputsShapingConeSoftness("inputs:shaping:cone:softness"),
      inputsShapingFocus("inputs:shaping:focus"),
      inputsShapingFocusTint("inputs:shaping:focusTint"),
      inputsShapingIesAngleScale("inputs:shaping:ies:angleScale"),
      inputsShapingIesFile("inputs:shaping:ies:file"),
      inputsShapingIesNormalize("inputs:shaping:ies:normalize"),
      inputsSpecular("inputs:specular"),
      inputsTextureFile("inputs:texture:file"),
      inputsTextureFormat("inputs:texture:format"),
      inputsWidth("inputs:width"),
      latlong("latlong"),
      lightFilters("light:filters"),
      lightFilterShaderId("lightFilter:shaderId"),
      lightLink("lightLink"),
      lightList("lightList"),
      lightListCacheBehavior("lightList:cacheBehavior"),
      lightMaterialSyncMode("light:materialSyncMode"),
      lightShaderId("light:shaderId"),
      materialGlowTintsLight("materialGlowTintsLight"),
      meshLight("MeshLight"),
      mirroredBall("mirroredBall"),
      noMaterialResponse("noMaterialResponse"),
      orientToStageUpAxis("orientToStageUpAxis"),
      portalLight("PortalLight"),
      portals("portals"),
      rectLight("RectLight"),
      shadowLink("shadowLink"),
      sphereLight("SphereLight"),
      treatAsLine("treatAsLine"),
      treatAsPoint("treatAsPoint"),
      volumeLight("VolumeLight")
{
}

struct UsdLuxTokensTypeAccessor
{
    const UsdLuxTokensType* operator->()
    {
        static const UsdLuxTokensType tokens;
        return &tokens;
    }
};


inline UsdLuxTokensTypeAccessor UsdLuxTokens;


} // namespace usdrt
