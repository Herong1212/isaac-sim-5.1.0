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

/// @file usdLux/lightAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdLux/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/collectionAPI.h"
#include "usdrt/scenegraph/usd/usdShade/input.h"
#include "usdrt/scenegraph/usd/usdShade/output.h" */
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
#include <usdrt/scenegraph/usd/usd/collectionAPI.h>
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
// LIGHTAPI                                                                    //
// -------------------------------------------------------------------------- //

/// @class UsdLuxLightAPI
///
/// API schema that imparts the quality of being a light onto a prim.
///
/// A light is any prim that has this schema applied to it.  This is true
/// regardless of whether LightAPI is included as a built-in API of the prim
/// type (e.g. RectLight or DistantLight) or is applied directly to a Gprim
/// that should be treated as a light.
///
/// <b>Linking</b>
///
/// Lights can be linked to geometry.  Linking controls which geometry
/// a light illuminates, and which geometry casts shadows from the light.
///
/// Linking is specified as collections (UsdCollectionAPI) which can
/// be accessed via GetLightLinkCollection() and GetShadowLinkCollection().
/// Note that these collections have their includeRoot set to true,
/// so that lights will illuminate and cast shadows from all objects
/// by default.  To illuminate only a specific set of objects, there
/// are two options.  One option is to modify the collection paths
/// to explicitly exclude everything else, assuming it is known;
/// the other option is to set includeRoot to false and explicitly
/// include the desired objects.  These are complementary approaches
/// that may each be preferable depending on the scenario and how
/// to best express the intent of the light setup.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxLightAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdLuxLightAPI on UsdPrim @p prim.
    /// Equivalent to UsdLuxLightAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxLightAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdLuxLightAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxLightAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxLightAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxLightAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "LightAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdLuxLightAPI object is returned upon success.
    /// An invalid (or empty) UsdLuxLightAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdLuxLightAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdLuxLightAPI>())
        {
            return UsdLuxLightAPI(prim);
        }
        return UsdLuxLightAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // COLLECTIONLIGHTLINKINCLUDEROOT
    // --------------------------------------------------------------------- //
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool collection:lightLink:includeRoot = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetCollectionLightLinkIncludeRootAttr() const;

    /// See GetCollectionLightLinkIncludeRootAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollectionLightLinkIncludeRootAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLLECTIONSHADOWLINKINCLUDEROOT
    // --------------------------------------------------------------------- //
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool collection:shadowLink:includeRoot = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetCollectionShadowLinkIncludeRootAttr() const;

    /// See GetCollectionShadowLinkIncludeRootAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCollectionShadowLinkIncludeRootAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHADERID
    // --------------------------------------------------------------------- //
    /// Default ID for the light's shader.
    /// This defines the shader ID for this light when a render context specific
    /// shader ID is not available.
    ///
    /// The default shaderId for the intrinsic UsdLux lights (RectLight,
    /// DistantLight, etc.) are set to default to the light's type name. For
    /// each intrinsic UsdLux light, we will always register an SdrShaderNode in
    /// the SdrRegistry, with the identifier matching the type name and the
    /// source type "USD", that corresponds to the light's inputs.
    /// \see GetShaderId
    /// \see GetShaderIdAttrForRenderContext
    /// \see SdrRegistry::GetShaderNodeByIdentifier
    /// \see SdrRegistry::GetShaderNodeByIdentifierAndType
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token light:shaderId = ""` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetShaderIdAttr() const;

    /// See GetShaderIdAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShaderIdAttr() const;

public:
    // --------------------------------------------------------------------- //
    // MATERIALSYNCMODE
    // --------------------------------------------------------------------- //
    /// For a LightAPI applied to geometry that has a bound Material,
    /// which is entirely or partly emissive, this specifies the relationship
    /// of the Material response to the lighting response.
    /// Valid values are:
    /// - materialGlowTintsLight: All primary and secondary rays see the
    /// emissive/glow response as dictated by the bound Material while the
    /// base color seen by light rays (which is then modulated by all of the
    /// other LightAPI controls) is the multiplication of the color feeding
    /// the emission/glow input of the Material (i.e. its surface or volume
    /// shader) with the scalar or pattern input to *inputs:color*.
    /// This allows the light's color to tint the geometry's glow color while
    /// preserving access to intensity and other light controls as ways to
    /// further modulate the illumination.
    /// - independent: All primary and secondary rays see the emissive/glow
    /// response as dictated by the bound Material, while the base color seen
    /// by light rays is determined solely by *inputs:color*. Note that for
    /// partially emissive geometry (in which some parts are reflective
    /// rather than emissive), a suitable pattern must be connected to the
    /// light's color input, or else the light will radiate uniformly from
    /// the geometry.
    /// - noMaterialResponse: The geometry behaves as if there is no Material
    /// bound at all, i.e. there is no diffuse, specular, or transmissive
    /// response. The base color of light rays is entirely controlled by the
    /// *inputs:color*. This is the standard mode for "canonical" lights in
    /// UsdLux and indicates to renderers that a Material will either never
    /// be bound or can always be ignored.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token light:materialSyncMode = "noMaterialResponse"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdLuxTokens "Allowed Values" | materialGlowTintsLight, independent, noMaterialResponse |

    UsdAttribute GetMaterialSyncModeAttr() const;

    /// See GetMaterialSyncModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateMaterialSyncModeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INTENSITY
    // --------------------------------------------------------------------- //
    /// Scales the power of the light linearly.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:intensity = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetIntensityAttr() const;

    /// See GetIntensityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIntensityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // EXPOSURE
    // --------------------------------------------------------------------- //
    /// Scales the power of the light exponentially as a power
    /// of 2 (similar to an F-stop control over exposure).  The result
    /// is multiplied against the intensity.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:exposure = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetExposureAttr() const;

    /// See GetExposureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateExposureAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DIFFUSE
    // --------------------------------------------------------------------- //
    /// A multiplier for the effect of this light on the diffuse
    /// response of materials.  This is a non-physical control.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:diffuse = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDiffuseAttr() const;

    /// See GetDiffuseAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDiffuseAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SPECULAR
    // --------------------------------------------------------------------- //
    /// A multiplier for the effect of this light on the specular
    /// response of materials.  This is a non-physical control.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:specular = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpecularAttr() const;

    /// See GetSpecularAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSpecularAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NORMALIZE
    // --------------------------------------------------------------------- //
    /// Normalizes power by the surface area of the light.
    /// This makes it easier to independently adjust the power and shape
    /// of the light, by causing the power to not vary with the area or
    /// angular size of the light.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool inputs:normalize = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetNormalizeAttr() const;

    /// See GetNormalizeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNormalizeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLOR
    // --------------------------------------------------------------------- //
    /// The color of emitted light, in energy-linear terms.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `color3f inputs:color = (1, 1, 1)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Color3f |

    UsdAttribute GetColorAttr() const;

    /// See GetColorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateColorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLECOLORTEMPERATURE
    // --------------------------------------------------------------------- //
    /// Enables using colorTemperature.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool inputs:enableColorTemperature = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableColorTemperatureAttr() const;

    /// See GetEnableColorTemperatureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateEnableColorTemperatureAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLORTEMPERATURE
    // --------------------------------------------------------------------- //
    /// Color temperature, in degrees Kelvin, representing the
    /// white point.  The default is a common white point, D65.  Lower
    /// values are warmer and higher values are cooler.  The valid range
    /// is from 1000 to 10000. Only takes effect when
    /// enableColorTemperature is set to true.  When active, the
    /// computed result multiplies against the color attribute.
    /// See UsdLuxBlackbodyTemperatureAsRgb().
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:colorTemperature = 6500` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetColorTemperatureAttr() const;

    /// See GetColorTemperatureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateColorTemperatureAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FILTERS
    // --------------------------------------------------------------------- //
    /// Relationship to the light filters that apply to this light.
    ///
    UsdRelationship GetFiltersRel() const;

    /// See GetFiltersRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateFiltersRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--

    /// Return the UsdCollectionAPI interface used for examining and
    /// modifying the light-linking of this light.  Light-linking
    /// controls which geometry this light illuminates.
    UsdCollectionAPI GetLightLinkCollectionAPI() const;

    /// Return the UsdCollectionAPI interface used for examining and
    /// modifying the shadow-linking of this light.  Shadow-linking
    /// controls which geometry casts shadows from this light.
    UsdCollectionAPI GetShadowLinkCollectionAPI() const;

    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxLightAPI::_GetStaticTfType()
{
    const static TfToken token("UsdLuxLightAPI");
    return token;
}

/* virtual */
inline const TfToken UsdLuxLightAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxLightAPI");
    return token;
}


inline UsdAttribute UsdLuxLightAPI::GetCollectionLightLinkIncludeRootAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->collectionLightLinkIncludeRoot));
}

inline UsdAttribute UsdLuxLightAPI::CreateCollectionLightLinkIncludeRootAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->collectionLightLinkIncludeRoot), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetCollectionShadowLinkIncludeRootAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->collectionShadowLinkIncludeRoot));
}

inline UsdAttribute UsdLuxLightAPI::CreateCollectionShadowLinkIncludeRootAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->collectionShadowLinkIncludeRoot), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightShaderId));
}

inline UsdAttribute UsdLuxLightAPI::CreateShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightShaderId), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetMaterialSyncModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightMaterialSyncMode));
}

inline UsdAttribute UsdLuxLightAPI::CreateMaterialSyncModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightMaterialSyncMode), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetIntensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsIntensity));
}

inline UsdAttribute UsdLuxLightAPI::CreateIntensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsIntensity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetExposureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsExposure));
}

inline UsdAttribute UsdLuxLightAPI::CreateExposureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsExposure), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetDiffuseAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsDiffuse));
}

inline UsdAttribute UsdLuxLightAPI::CreateDiffuseAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsDiffuse), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetSpecularAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsSpecular));
}

inline UsdAttribute UsdLuxLightAPI::CreateSpecularAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsSpecular), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetNormalizeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsNormalize));
}

inline UsdAttribute UsdLuxLightAPI::CreateNormalizeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsNormalize), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetColorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsColor));
}

inline UsdAttribute UsdLuxLightAPI::CreateColorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsColor), SdfValueTypeNames->Color3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetEnableColorTemperatureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsEnableColorTemperature));
}

inline UsdAttribute UsdLuxLightAPI::CreateEnableColorTemperatureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsEnableColorTemperature), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLightAPI::GetColorTemperatureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsColorTemperature));
}

inline UsdAttribute UsdLuxLightAPI::CreateColorTemperatureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsColorTemperature), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship UsdLuxLightAPI::GetFiltersRel() const
{
    return GetPrim().GetRelationship(UsdLuxTokens->lightFilters);
}

inline UsdRelationship UsdLuxLightAPI::CreateFiltersRel() const
{
    return GetPrim().CreateRelationship(UsdLuxTokens->lightFilters,
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

namespace usdrt {

UsdCollectionAPI
UsdLuxLightAPI::GetLightLinkCollectionAPI() const
{
    return UsdCollectionAPI(GetPrim(), UsdLuxTokens->lightLink);
}

UsdCollectionAPI
UsdLuxLightAPI::GetShadowLinkCollectionAPI() const
{
    return UsdCollectionAPI(GetPrim(), UsdLuxTokens->shadowLink);
}

}
