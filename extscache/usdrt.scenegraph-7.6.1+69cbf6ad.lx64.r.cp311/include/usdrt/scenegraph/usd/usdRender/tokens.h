// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

/// \file usdRender/tokens.h

// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
//
// This is an automatically generated file (by usdGenSchema.py).
// Do not hand-edit!
//
// XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{


/// \class UsdRenderTokensType

/// Provides standard set of public tokens for UsdRender schema.
/// Access via the RtTokens helper accessor.
///
/// These tokens are auto-generated from the module's schema, representing
/// property names, for when you need to fetch an attribute or relationship
/// directly by name, e.g. UsdPrim::GetAttribute(), in the most efficient
/// manner, and allow the compiler to verify that you spelled the name
/// correctly.
///
/// UsdRenderTokens also contains all of the \em allowedTokens values
/// declared for schema builtin attributes of 'token' scene description type.

/// Use UsdRenderTokens like so:
///
/// \code
///     prim.GetAttribute(RtTokens->worldPosition);
/// \endcode


struct UsdRenderTokensType
{
    UsdRenderTokensType();
    /// @brief "adjustApertureHeight"
    ///
    /// Possible value for UsdRenderSettingsBase::GetAspectRatioConformPolicyAttr()
    const TfToken adjustApertureHeight;
    /// @brief "adjustApertureWidth"
    ///
    /// Possible value for UsdRenderSettingsBase::GetAspectRatioConformPolicyAttr()
    const TfToken adjustApertureWidth;
    /// @brief "adjustPixelAspectRatio"
    ///
    /// Possible value for UsdRenderSettingsBase::GetAspectRatioConformPolicyAttr()
    const TfToken adjustPixelAspectRatio;
    /// @brief "aspectRatioConformPolicy"
    ///
    /// UsdRenderSettingsBase
    const TfToken aspectRatioConformPolicy;
    /// @brief "camera"
    ///
    /// UsdRenderSettingsBase
    const TfToken camera;
    /// @brief "color3f"
    ///
    /// Default value for UsdRenderVar::GetDataTypeAttr()
    const TfToken color3f;
    /// @brief "command"
    ///
    /// UsdRenderPass
    const TfToken command;
    /// @brief "cropAperture"
    ///
    /// Possible value for UsdRenderSettingsBase::GetAspectRatioConformPolicyAttr()
    const TfToken cropAperture;
    /// @brief "dataType"
    ///
    /// UsdRenderVar
    const TfToken dataType;
    /// @brief "dataWindowNDC"
    ///
    /// UsdRenderSettingsBase
    const TfToken dataWindowNDC;
    /// @brief "denoise:enable"
    ///
    /// UsdRenderPass
    const TfToken denoiseEnable;
    /// @brief "denoise:pass"
    ///
    /// UsdRenderPass
    const TfToken denoisePass;
    /// @brief "disableMotionBlur"
    ///
    /// UsdRenderSettingsBase
    const TfToken disableMotionBlur;
    /// @brief "expandAperture"
    ///
    /// Possible value for UsdRenderSettingsBase::GetAspectRatioConformPolicyAttr(), Default value for
    /// UsdRenderSettingsBase::GetAspectRatioConformPolicyAttr()
    const TfToken expandAperture;
    /// @brief "fileName"
    ///
    /// UsdRenderPass
    const TfToken fileName;
    /// @brief "full"
    ///
    /// Possible value for UsdRenderSettings::GetMaterialBindingPurposesAttr()
    const TfToken full;
    /// @brief "includedPurposes"
    ///
    /// UsdRenderSettings
    const TfToken includedPurposes;
    /// @brief "inputPasses"
    ///
    /// UsdRenderPass
    const TfToken inputPasses;
    /// @brief "instantaneousShutter"
    ///
    /// UsdRenderSettingsBase
    const TfToken instantaneousShutter;
    /// @brief "intrinsic"
    ///
    /// Possible value for UsdRenderVar::GetSourceTypeAttr()
    const TfToken intrinsic;
    /// @brief "lpe"
    ///
    /// Possible value for UsdRenderVar::GetSourceTypeAttr()
    const TfToken lpe;
    /// @brief "materialBindingPurposes"
    ///
    /// UsdRenderSettings
    const TfToken materialBindingPurposes;
    /// @brief "orderedVars"
    ///
    /// UsdRenderProduct
    const TfToken orderedVars;
    /// @brief "passType"
    ///
    /// UsdRenderPass
    const TfToken passType;
    /// @brief "pixelAspectRatio"
    ///
    /// UsdRenderSettingsBase
    const TfToken pixelAspectRatio;
    /// @brief "preview"
    ///
    /// Possible value for UsdRenderSettings::GetMaterialBindingPurposesAttr()
    const TfToken preview;
    /// @brief "primvar"
    ///
    /// Possible value for UsdRenderVar::GetSourceTypeAttr()
    const TfToken primvar;
    /// @brief "productName"
    ///
    /// UsdRenderProduct
    const TfToken productName;
    /// @brief "products"
    ///
    /// UsdRenderSettings
    const TfToken products;
    /// @brief "productType"
    ///
    /// UsdRenderProduct
    const TfToken productType;
    /// @brief "raster"
    ///
    /// RenderProduct productType value that indicates a 2D raster image of pixels., Default value for
    /// UsdRenderProduct::GetProductTypeAttr()
    const TfToken raster;
    /// @brief "raw"
    ///
    /// Possible value for UsdRenderVar::GetSourceTypeAttr(), Default value for UsdRenderVar::GetSourceTypeAttr()
    const TfToken raw;
    /// @brief "renderingColorSpace"
    ///
    /// UsdRenderSettings
    const TfToken renderingColorSpace;
    /// @brief "renderSettingsPrimPath"
    ///
    /// Stage-level metadata that encodes the path to UsdRenderSettingsPrim to use for rendering.
    const TfToken renderSettingsPrimPath;
    /// @brief "renderSource"
    ///
    /// UsdRenderPass
    const TfToken renderSource;
    /// @brief "resolution"
    ///
    /// UsdRenderSettingsBase
    const TfToken resolution;
    /// @brief "sourceName"
    ///
    /// UsdRenderVar
    const TfToken sourceName;
    /// @brief "sourceType"
    ///
    /// UsdRenderVar
    const TfToken sourceType;
    /// A vector of all of the tokens listed above.
    const std::vector<TfToken> allTokens;
};

inline UsdRenderTokensType::UsdRenderTokensType()
    : adjustApertureHeight("adjustApertureHeight"),
      adjustApertureWidth("adjustApertureWidth"),
      adjustPixelAspectRatio("adjustPixelAspectRatio"),
      aspectRatioConformPolicy("aspectRatioConformPolicy"),
      camera("camera"),
      color3f("color3f"),
      command("command"),
      cropAperture("cropAperture"),
      dataType("dataType"),
      dataWindowNDC("dataWindowNDC"),
      denoiseEnable("denoise:enable"),
      denoisePass("denoise:pass"),
      disableMotionBlur("disableMotionBlur"),
      expandAperture("expandAperture"),
      fileName("fileName"),
      full("full"),
      includedPurposes("includedPurposes"),
      inputPasses("inputPasses"),
      instantaneousShutter("instantaneousShutter"),
      intrinsic("intrinsic"),
      lpe("lpe"),
      materialBindingPurposes("materialBindingPurposes"),
      orderedVars("orderedVars"),
      passType("passType"),
      pixelAspectRatio("pixelAspectRatio"),
      preview("preview"),
      primvar("primvar"),
      productName("productName"),
      products("products"),
      productType("productType"),
      raster("raster"),
      raw("raw"),
      renderingColorSpace("renderingColorSpace"),
      renderSettingsPrimPath("renderSettingsPrimPath"),
      renderSource("renderSource"),
      resolution("resolution"),
      sourceName("sourceName"),
      sourceType("sourceType")
{
}

struct UsdRenderTokensTypeAccessor
{
    const UsdRenderTokensType* operator->()
    {
        static const UsdRenderTokensType tokens;
        return &tokens;
    }
};


inline UsdRenderTokensTypeAccessor UsdRenderTokens;


} // namespace usdrt
