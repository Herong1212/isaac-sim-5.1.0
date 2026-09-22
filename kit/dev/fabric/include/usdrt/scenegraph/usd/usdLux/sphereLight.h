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

/// @file usdLux/sphereLight.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdLux/boundableLightBase.h"
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
// SPHERELIGHT                                                                 //
// -------------------------------------------------------------------------- //

/// @class UsdLuxSphereLight
///
/// Light emitted outward from a sphere.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxSphereLight : public UsdLuxBoundableLightBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxSphereLight on UsdPrim @p prim.
    /// Equivalent to UsdLuxSphereLight::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxSphereLight(const UsdPrim& prim = UsdPrim()) : UsdLuxBoundableLightBase(prim)
    {
    }

    /// Construct a UsdLuxSphereLight on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxSphereLight(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxSphereLight(const UsdSchemaBase& schemaObj) : UsdLuxBoundableLightBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxSphereLight()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdLuxSphereLight Define(const UsdStageRefPtr& stage, const SdfPath& path);

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
    /// | Declaration | `uniform token light:shaderId = "SphereLight"` |
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
    // RADIUS
    // --------------------------------------------------------------------- //
    /// Radius of the sphere.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:radius = 0.5` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetRadiusAttr() const;

    /// See GetRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRadiusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TREATASPOINT
    // --------------------------------------------------------------------- //
    /// A hint that this light can be treated as a 'point'
    /// light (effectively, a zero-radius sphere) by renderers that
    /// benefit from non-area lighting. Renderers that only support
    /// area lights can disregard this.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool treatAsPoint = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetTreatAsPointAttr() const;

    /// See GetTreatAsPointAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTreatAsPointAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxSphereLight::_GetStaticTfType()
{
    const static TfToken token("UsdLuxSphereLight");
    return token;
}

/* virtual */
inline const TfToken UsdLuxSphereLight::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxSphereLight");
    return token;
}

/* static */
inline UsdLuxSphereLight UsdLuxSphereLight::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdLuxSphereLight();
    }
    return UsdLuxSphereLight(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdLuxSphereLight::GetLightShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightShaderId));
}

inline UsdAttribute UsdLuxSphereLight::CreateLightShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightShaderId), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxSphereLight::GetRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsRadius));
}

inline UsdAttribute UsdLuxSphereLight::CreateRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsRadius), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxSphereLight::GetTreatAsPointAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->treatAsPoint));
}

inline UsdAttribute UsdLuxSphereLight::CreateTreatAsPointAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->treatAsPoint), SdfValueTypeNames->Bool,
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
