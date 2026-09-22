// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

/// @file usdRender/settingsBase.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
#include "usdrt/scenegraph/usd/usdRender/tokens.h"


// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
// --(END CUSTOM INCLUDES)--

#include <omni/core/IObject.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/base/vt/array.h>
#include <usdrt/scenegraph/interface/IRtAttribute.h>
#include <usdrt/scenegraph/interface/IRtPrim.h>
#include <usdrt/scenegraph/interface/IRtPrimRange.h>
#include <usdrt/scenegraph/interface/IRtRelationship.h>
#include <usdrt/scenegraph/interface/IRtStage.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usd/common.h>
#include <usdrt/scenegraph/usd/usd/prim.h>
#include <usdrt/scenegraph/usd/usd/timeCode.h>

namespace usdrt
{

// -------------------------------------------------------------------------- //
// RENDERSETTINGSBASE                                                          //
// -------------------------------------------------------------------------- //

/// @class UsdRenderSettingsBase
///
/// Abstract base class that defines render settings that
/// can be specified on either a RenderSettings prim or a RenderProduct
/// prim.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdRenderTokens.
/// So to set an attribute to the value "rightHanded", use UsdRenderTokens->rightHanded
/// as the value.

class UsdRenderSettingsBase : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdRenderSettingsBase on UsdPrim @p prim.
    /// Equivalent to UsdRenderSettingsBase::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdRenderSettingsBase(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdRenderSettingsBase on the prim held by @p schemaObj .
    /// Should be preferred over UsdRenderSettingsBase(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdRenderSettingsBase(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdRenderSettingsBase()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RESOLUTION
    // --------------------------------------------------------------------- //
    /// The image pixel resolution, corresponding to the
    /// camera's screen window.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int2 resolution = (2048, 1080)` |
    /// | C++ Type | GfVec2i |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int2 |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetResolutionAttr() const;

    /// See GetResolutionAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateResolutionAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PIXELASPECTRATIO
    // --------------------------------------------------------------------- //
    /// The aspect ratio (width/height) of image pixels..
    /// The default ratio 1.0 indicates square pixels.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float pixelAspectRatio = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetPixelAspectRatioAttr() const;

    /// See GetPixelAspectRatioAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePixelAspectRatioAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ASPECTRATIOCONFORMPOLICY
    // --------------------------------------------------------------------- //
    /// Indicates the policy to use to resolve an aspect
    /// ratio mismatch between the camera aperture and image settings.
    ///
    /// This policy allows a standard render setting to do something
    /// reasonable given varying camera inputs.
    ///
    /// The camera aperture aspect ratio is determined by the
    /// aperture atributes on the UsdGeomCamera.
    ///
    /// The image aspect ratio is determined by the resolution and
    /// pixelAspectRatio attributes in the render settings.
    ///
    /// - "expandAperture": if necessary, expand the aperture to
    /// fit the image, exposing additional scene content
    /// - "cropAperture": if necessary, crop the aperture to fit
    /// the image, cropping scene content
    /// - "adjustApertureWidth": if necessary, adjust aperture width
    /// to make its aspect ratio match the image
    /// - "adjustApertureHeight": if necessary, adjust aperture height
    /// to make its aspect ratio match the image
    /// - "adjustPixelAspectRatio": compute pixelAspectRatio to
    /// make the image exactly cover the aperture; disregards
    /// existing attribute value of pixelAspectRatio
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token aspectRatioConformPolicy = "expandAperture"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdRenderTokens "Allowed Values" | expandAperture, cropAperture, adjustApertureWidth,
    /// adjustApertureHeight, adjustPixelAspectRatio |

    UsdAttribute GetAspectRatioConformPolicyAttr() const;

    /// See GetAspectRatioConformPolicyAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAspectRatioConformPolicyAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DATAWINDOWNDC
    // --------------------------------------------------------------------- //
    /// dataWindowNDC specifies the axis-aligned rectangular
    /// region in the adjusted aperture window within which the renderer
    /// should produce data.
    ///
    /// It is specified as (xmin, ymin, xmax, ymax) in normalized
    /// device coordinates, where the range 0 to 1 corresponds to the
    /// aperture.  (0,0) corresponds to the bottom-left
    /// corner and (1,1) corresponds to the upper-right corner.
    ///
    /// Specifying a window outside the unit square will produce
    /// overscan data. Specifying a window that does not cover the unit
    /// square will produce a cropped render.
    ///
    /// A pixel is included in the rendered result if the pixel
    /// center is contained by the data window.  This is consistent
    /// with standard rules used by polygon rasterization engines.
    /// \ref UsdRenderRasterization
    ///
    /// The data window is expressed in NDC so that cropping and
    /// overscan may be resolution independent.  In interactive
    /// workflows, incremental cropping and resolution adjustment
    /// may be intermixed to isolate and examine parts of the scene.
    /// In compositing workflows, overscan may be used to support
    /// image post-processing kernels, and reduced-resolution proxy
    /// renders may be used for faster iteration.
    ///
    /// The dataWindow:ndc coordinate system references the
    /// aperture after any adjustments required by
    /// aspectRatioConformPolicy.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float4 dataWindowNDC = (0, 0, 1, 1)` |
    /// | C++ Type | GfVec4f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float4 |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDataWindowNDCAttr() const;

    /// See GetDataWindowNDCAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDataWindowNDCAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INSTANTANEOUSSHUTTER
    // --------------------------------------------------------------------- //
    /// Deprecated - use disableMotionBlur instead. Override
    /// the targeted _camera_'s _shutterClose_ to be equal to the
    /// value of its _shutterOpen_, to produce a zero-width shutter
    /// interval.  This gives us a convenient way to disable motion
    /// blur.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool instantaneousShutter = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetInstantaneousShutterAttr() const;

    /// See GetInstantaneousShutterAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInstantaneousShutterAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DISABLEMOTIONBLUR
    // --------------------------------------------------------------------- //
    /// Disable all motion blur by setting the shutter interval
    /// of the targeted camera to [0,0] - that is, take only one sample,
    /// namely at the current time code.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool disableMotionBlur = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDisableMotionBlurAttr() const;

    /// See GetDisableMotionBlurAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisableMotionBlurAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CAMERA
    // --------------------------------------------------------------------- //
    /// The _camera_ relationship specifies the primary
    /// camera to use in a render.  It must target a UsdGeomCamera.
    ///
    UsdRelationship GetCameraRel() const;

    /// See GetCameraRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateCameraRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdRenderSettingsBase::_GetStaticTfType()
{
    const static TfToken token("UsdRenderSettingsBase");
    return token;
}

/* virtual */
inline const TfToken UsdRenderSettingsBase::_GetTfTypeToken() const
{
    const static TfToken token("UsdRenderSettingsBase");
    return token;
}


inline UsdAttribute UsdRenderSettingsBase::GetResolutionAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->resolution));
}

inline UsdAttribute UsdRenderSettingsBase::CreateResolutionAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->resolution), SdfValueTypeNames->Int2,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderSettingsBase::GetPixelAspectRatioAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->pixelAspectRatio));
}

inline UsdAttribute UsdRenderSettingsBase::CreatePixelAspectRatioAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->pixelAspectRatio), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderSettingsBase::GetAspectRatioConformPolicyAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->aspectRatioConformPolicy));
}

inline UsdAttribute UsdRenderSettingsBase::CreateAspectRatioConformPolicyAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->aspectRatioConformPolicy), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderSettingsBase::GetDataWindowNDCAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->dataWindowNDC));
}

inline UsdAttribute UsdRenderSettingsBase::CreateDataWindowNDCAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->dataWindowNDC), SdfValueTypeNames->Float4,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderSettingsBase::GetInstantaneousShutterAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->instantaneousShutter));
}

inline UsdAttribute UsdRenderSettingsBase::CreateInstantaneousShutterAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->instantaneousShutter), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdRenderSettingsBase::GetDisableMotionBlurAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdRenderTokens->disableMotionBlur));
}

inline UsdAttribute UsdRenderSettingsBase::CreateDisableMotionBlurAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdRenderTokens->disableMotionBlur), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}


inline UsdRelationship UsdRenderSettingsBase::GetCameraRel() const
{
    return GetPrim().GetRelationship(UsdRenderTokens->camera);
}

inline UsdRelationship UsdRenderSettingsBase::CreateCameraRel() const
{
    return GetPrim().CreateRelationship(UsdRenderTokens->camera,
                                        /* custom = */ false);
}
} // namespace usdrt
// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
