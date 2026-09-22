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

/// @file usdLux/cylinderLight.h

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
// CYLINDERLIGHT                                                               //
// -------------------------------------------------------------------------- //

/// @class UsdLuxCylinderLight
///
/// Light emitted outward from a cylinder.
/// The cylinder is centered at the origin and has its major axis on the X axis.
/// The cylinder does not emit light from the flat end-caps.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxCylinderLight : public UsdLuxBoundableLightBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxCylinderLight on UsdPrim @p prim.
    /// Equivalent to UsdLuxCylinderLight::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxCylinderLight(const UsdPrim& prim = UsdPrim()) : UsdLuxBoundableLightBase(prim)
    {
    }

    /// Construct a UsdLuxCylinderLight on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxCylinderLight(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxCylinderLight(const UsdSchemaBase& schemaObj) : UsdLuxBoundableLightBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxCylinderLight()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdLuxCylinderLight Define(const UsdStageRefPtr& stage, const SdfPath& path);

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
    /// | Declaration | `uniform token light:shaderId = "CylinderLight"` |
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
    // LENGTH
    // --------------------------------------------------------------------- //
    /// Width of the rectangle, in the local X axis.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:length = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetLengthAttr() const;

    /// See GetLengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLengthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RADIUS
    // --------------------------------------------------------------------- //
    /// Radius of the cylinder.
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
    // TREATASLINE
    // --------------------------------------------------------------------- //
    /// A hint that this light can be treated as a 'line'
    /// light (effectively, a zero-radius cylinder) by renderers that
    /// benefit from non-area lighting. Renderers that only support
    /// area lights can disregard this.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool treatAsLine = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetTreatAsLineAttr() const;

    /// See GetTreatAsLineAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTreatAsLineAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxCylinderLight::_GetStaticTfType()
{
    const static TfToken token("UsdLuxCylinderLight");
    return token;
}

/* virtual */
inline const TfToken UsdLuxCylinderLight::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxCylinderLight");
    return token;
}

/* static */
inline UsdLuxCylinderLight UsdLuxCylinderLight::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdLuxCylinderLight();
    }
    return UsdLuxCylinderLight(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdLuxCylinderLight::GetLightShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightShaderId));
}

inline UsdAttribute UsdLuxCylinderLight::CreateLightShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightShaderId), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxCylinderLight::GetLengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsLength));
}

inline UsdAttribute UsdLuxCylinderLight::CreateLengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsLength), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxCylinderLight::GetRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsRadius));
}

inline UsdAttribute UsdLuxCylinderLight::CreateRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsRadius), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxCylinderLight::GetTreatAsLineAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->treatAsLine));
}

inline UsdAttribute UsdLuxCylinderLight::CreateTreatAsLineAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->treatAsLine), SdfValueTypeNames->Bool,
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
