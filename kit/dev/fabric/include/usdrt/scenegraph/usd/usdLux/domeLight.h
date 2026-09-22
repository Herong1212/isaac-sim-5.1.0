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

/// @file usdLux/domeLight.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdLux/nonboundableLightBase.h"
#include "usdrt/scenegraph/usd/usdLux/tokens.h"


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
// DOMELIGHT                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdLuxDomeLight
///
/// Light emitted inward from a distant external environment,
/// such as a sky or IBL light probe.  The orientation of a dome light with a
/// latlong texture is expected to match the OpenEXR specification for latlong
/// environment maps.  From the OpenEXR documentation:
///
/// -------------------------------------------------------------------------
/// Latitude-Longitude Map:
///
/// The environment is projected onto the image using polar coordinates
/// (latitude and longitude).  A pixel's x coordinate corresponds to
/// its longitude, and the y coordinate corresponds to its latitude.
/// Pixel (dataWindow.min.x, dataWindow.min.y) has latitude +pi/2 and
/// longitude +pi; pixel (dataWindow.max.x, dataWindow.max.y) has
/// latitude -pi/2 and longitude -pi.
///
/// In 3D space, latitudes -pi/2 and +pi/2 correspond to the negative and
/// positive y direction.  Latitude 0, longitude 0 points into positive
/// z direction; and latitude 0, longitude pi/2 points into positive x
/// direction.
///
/// The size of the data window should be 2*N by N pixels (width by height),
/// where N can be any integer greater than 0.
/// -------------------------------------------------------------------------
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxDomeLight : public UsdLuxNonboundableLightBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxDomeLight on UsdPrim @p prim.
    /// Equivalent to UsdLuxDomeLight::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxDomeLight(const UsdPrim& prim = UsdPrim()) : UsdLuxNonboundableLightBase(prim)
    {
    }

    /// Construct a UsdLuxDomeLight on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxDomeLight(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxDomeLight(const UsdSchemaBase& schemaObj) : UsdLuxNonboundableLightBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxDomeLight()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdLuxDomeLight Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // LIGHTSHADERID
    // --------------------------------------------------------------------- //
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token light:shaderId = "DomeLight"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetLightShaderIdAttr() const;

    /// See GetLightShaderIdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLightShaderIdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TEXTUREFILE
    // --------------------------------------------------------------------- //
    /// A color texture to use on the dome, such as an HDR (high
    /// dynamic range) texture intended for IBL (image based lighting).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset inputs:texture:file` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetTextureFileAttr() const;

    /// See GetTextureFileAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTextureFileAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TEXTUREFORMAT
    // --------------------------------------------------------------------- //
    /// Specifies the parameterization of the color map file.
    /// Valid values are:
    /// - automatic: Tries to determine the layout from the file itself.
    /// For example, Renderman texture files embed an explicit
    /// parameterization.
    /// - latlong: Latitude as X, longitude as Y.
    /// - mirroredBall: An image of the environment reflected in a
    /// sphere, using an implicitly orthogonal projection.
    /// - angular: Similar to mirroredBall but the radial dimension
    /// is mapped linearly to the angle, providing better sampling
    /// at the edges.
    /// - cubeMapVerticalCross: A cube map with faces laid out as a
    /// vertical cross.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token inputs:texture:format = "automatic"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdLuxTokens "Allowed Values" | automatic, latlong, mirroredBall, angular, cubeMapVerticalCross |

    UsdAttribute GetTextureFormatAttr() const;

    /// See GetTextureFormatAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTextureFormatAttr() const;

public:
    // --------------------------------------------------------------------- //
    // GUIDERADIUS
    // --------------------------------------------------------------------- //
    /// The radius of guide geometry to use to visualize the dome light.  The default is 1 km for scenes whose
    /// metersPerUnit is the USD default of 0.01 (i.e., 1 world unit is 1 cm).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float guideRadius = 100000` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetGuideRadiusAttr() const;

    /// See GetGuideRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGuideRadiusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PORTALS
    // --------------------------------------------------------------------- //
    /// Optional portals to guide light sampling.
    ///
    UsdRelationship GetPortalsRel() const;

    /// See GetPortalsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreatePortalsRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxDomeLight::_GetStaticTfType()
{
    const static TfToken token("UsdLuxDomeLight");
    return token;
}

/* virtual */
inline const TfToken UsdLuxDomeLight::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxDomeLight");
    return token;
}

/* static */
inline UsdLuxDomeLight UsdLuxDomeLight::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdLuxDomeLight();
    }
    return UsdLuxDomeLight(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdLuxDomeLight::GetLightShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightShaderId));
}

inline UsdAttribute UsdLuxDomeLight::CreateLightShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightShaderId), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxDomeLight::GetTextureFileAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsTextureFile));
}

inline UsdAttribute UsdLuxDomeLight::CreateTextureFileAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsTextureFile), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxDomeLight::GetTextureFormatAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsTextureFormat));
}

inline UsdAttribute UsdLuxDomeLight::CreateTextureFormatAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsTextureFormat), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxDomeLight::GetGuideRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->guideRadius));
}

inline UsdAttribute UsdLuxDomeLight::CreateGuideRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->guideRadius), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship UsdLuxDomeLight::GetPortalsRel() const
{
    return GetPrim().GetRelationship(UsdLuxTokens->portals);
}

inline UsdRelationship UsdLuxDomeLight::CreatePortalsRel() const
{
    return GetPrim().CreateRelationship(UsdLuxTokens->portals,
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
