//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

//! @file
//!
//! @brief TODO

// GENERATED FILE DO NOT EDIT

/// \file usdLux/light.h

#include "usdrt/scenegraph/usd/usdGeom/xformable.h"
#include "usdrt/scenegraph/usd/usdLux/tokens.h"
/* Extra Includes
TODO revisit extra includes metadata
#include "usdrt/scenegraph/usd/usd/collectionAPI.h"
*/

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
// LIGHT                                                                       //
// -------------------------------------------------------------------------- //


/// \class UsdLuxLight
///
/// Base class for all lights.
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
///

class UsdLuxLight : public UsdGeomXformable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// \sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdLuxLight on UsdPrim \p prim .
    /// Equivalent to UsdLuxLight::Get(prim.GetStage(), prim.GetPath())
    /// for a \em valid \p prim, but will not immediately throw an error for
    /// an invalid \p prim
    explicit UsdLuxLight(const UsdPrim& prim = UsdPrim()) : UsdGeomXformable(prim)
    {
    }

    /// Construct a UsdLuxLight on the prim held by \p schemaObj .
    /// Should be preferred over UsdLuxLight(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxLight(const UsdSchemaBase& schemaObj) : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxLight()
    {
    }

    static const TfToken _GetStaticTfType();


public:
    // --------------------------------------------------------------------- //
    // INTENSITY
    // --------------------------------------------------------------------- //
    /// Scales the power of the light linearly.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float intensity = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetIntensityAttr() const;

    /// See GetIntensityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
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
    /// | Declaration | `float exposure = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetExposureAttr() const;

    /// See GetExposureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
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
    /// | Declaration | `float diffuse = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetDiffuseAttr() const;

    /// See GetDiffuseAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
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
    /// | Declaration | `float specular = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetSpecularAttr() const;

    /// See GetSpecularAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
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
    /// | Declaration | `bool normalize = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetNormalizeAttr() const;

    /// See GetNormalizeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    UsdAttribute CreateNormalizeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // COLOR
    // --------------------------------------------------------------------- //
    /// The color of emitted light, in energy-linear terms.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `color3f color = (1, 1, 1)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Color3f |

    UsdAttribute GetColorAttr() const;

    /// See GetColorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
    UsdAttribute CreateColorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ENABLECOLORTEMPERATURE
    // --------------------------------------------------------------------- //
    /// Enables using colorTemperature.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool enableColorTemperature = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetEnableColorTemperatureAttr() const;

    /// See GetEnableColorTemperatureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
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
    /// | Declaration | `float colorTemperature = 6500` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetColorTemperatureAttr() const;

    /// See GetColorTemperatureAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author \p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if \p writeSparsely is \c true -
    /// the default for \p writeSparsely is \c false.
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
    UsdRelationship CreateFiltersRel() const;
};

inline const TfToken UsdLuxLight::_GetStaticTfType()
{
    return TfToken("UsdLuxLight");
}


inline UsdAttribute UsdLuxLight::GetIntensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->intensity));
}

inline UsdAttribute UsdLuxLight::CreateIntensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->intensity), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLight::GetExposureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->exposure));
}

inline UsdAttribute UsdLuxLight::CreateExposureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->exposure), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLight::GetDiffuseAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->diffuse));
}

inline UsdAttribute UsdLuxLight::CreateDiffuseAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->diffuse), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLight::GetSpecularAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->specular));
}

inline UsdAttribute UsdLuxLight::CreateSpecularAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->specular), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLight::GetNormalizeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->normalize));
}

inline UsdAttribute UsdLuxLight::CreateNormalizeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->normalize), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLight::GetColorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->color));
}

inline UsdAttribute UsdLuxLight::CreateColorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->color), SdfValueTypeNames->Color3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLight::GetEnableColorTemperatureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->enableColorTemperature));
}

inline UsdAttribute UsdLuxLight::CreateEnableColorTemperatureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->enableColorTemperature), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxLight::GetColorTemperatureAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->colorTemperature));
}

inline UsdAttribute UsdLuxLight::CreateColorTemperatureAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->colorTemperature), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}


inline UsdRelationship UsdLuxLight::GetFiltersRel() const
{
    return GetPrim().GetRelationship(UsdLuxTokens->filters);
}

inline UsdRelationship UsdLuxLight::CreateFiltersRel() const
{
    return GetPrim().CreateRelationship(UsdLuxTokens->filters,
                                        /* custom = */ false);
}


}

// ===================================================================== //
// Feel free to add custom code below this line. It will be preserved by
// the code generator.
//
// Just remember to wrap code in the appropriate delimiters:
// 'namespace usdrt {', '}'.
// ===================================================================== //
// --(BEGIN CUSTOM CODE)--
