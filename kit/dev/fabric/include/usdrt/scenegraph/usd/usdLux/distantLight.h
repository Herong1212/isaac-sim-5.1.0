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

/// @file usdLux/distantLight.h

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
// DISTANTLIGHT                                                                //
// -------------------------------------------------------------------------- //

/// @class UsdLuxDistantLight
///
/// Light emitted from a distant source along the -Z axis.
/// Also known as a directional light.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxDistantLight : public UsdLuxNonboundableLightBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxDistantLight on UsdPrim @p prim.
    /// Equivalent to UsdLuxDistantLight::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxDistantLight(const UsdPrim& prim = UsdPrim()) : UsdLuxNonboundableLightBase(prim)
    {
    }

    /// Construct a UsdLuxDistantLight on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxDistantLight(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxDistantLight(const UsdSchemaBase& schemaObj) : UsdLuxNonboundableLightBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxDistantLight()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdLuxDistantLight Define(const UsdStageRefPtr& stage, const SdfPath& path);

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
    /// | Declaration | `uniform token light:shaderId = "DistantLight"` |
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
    // ANGLE
    // --------------------------------------------------------------------- //
    /// Angular size of the light in degrees.
    /// As an example, the Sun is approximately 0.53 degrees as seen from Earth.
    /// Higher values broaden the light and therefore soften shadow edges.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:angle = 0.53` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetAngleAttr() const;

    /// See GetAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INTENSITY
    // --------------------------------------------------------------------- //
    /// Scales the emission of the light linearly.
    /// The DistantLight has a high default intensity to approximate the Sun.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:intensity = 50000` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetIntensityAttr() const;

    /// See GetIntensityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIntensityAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxDistantLight::_GetStaticTfType()
{
    const static TfToken token("UsdLuxDistantLight");
    return token;
}

/* virtual */
inline const TfToken UsdLuxDistantLight::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxDistantLight");
    return token;
}

/* static */
inline UsdLuxDistantLight UsdLuxDistantLight::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdLuxDistantLight();
    }
    return UsdLuxDistantLight(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdLuxDistantLight::GetLightShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightShaderId));
}

inline UsdAttribute UsdLuxDistantLight::CreateLightShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightShaderId), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxDistantLight::GetAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsAngle));
}

inline UsdAttribute UsdLuxDistantLight::CreateAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsAngle), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxDistantLight::GetIntensityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsIntensity));
}

inline UsdAttribute UsdLuxDistantLight::CreateIntensityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsIntensity), SdfValueTypeNames->Float,
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
