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

/// @file usdLux/rectLight.h

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
// RECTLIGHT                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdLuxRectLight
///
/// Light emitted from one side of a rectangle.
/// The rectangle is centered in the XY plane and emits light along the -Z axis.
/// The rectangle is 1 unit in length in the X and Y axis.  In the default
/// position, a texture file's min coordinates should be at (+X, +Y) and
/// max coordinates at (-X, -Y).
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxRectLight : public UsdLuxBoundableLightBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdLuxRectLight on UsdPrim @p prim.
    /// Equivalent to UsdLuxRectLight::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxRectLight(const UsdPrim& prim = UsdPrim()) : UsdLuxBoundableLightBase(prim)
    {
    }

    /// Construct a UsdLuxRectLight on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxRectLight(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxRectLight(const UsdSchemaBase& schemaObj) : UsdLuxBoundableLightBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxRectLight()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdLuxRectLight Define(const UsdStageRefPtr& stage, const SdfPath& path);

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
    /// | Declaration | `uniform token light:shaderId = "RectLight"` |
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
    // WIDTH
    // --------------------------------------------------------------------- //
    /// Width of the rectangle, in the local X axis.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:width = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetWidthAttr() const;

    /// See GetWidthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWidthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HEIGHT
    // --------------------------------------------------------------------- //
    /// Height of the rectangle, in the local Y axis.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:height = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetHeightAttr() const;

    /// See GetHeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TEXTUREFILE
    // --------------------------------------------------------------------- //
    /// A color texture to use on the rectangle.
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

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxRectLight::_GetStaticTfType()
{
    const static TfToken token("UsdLuxRectLight");
    return token;
}

/* virtual */
inline const TfToken UsdLuxRectLight::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxRectLight");
    return token;
}

/* static */
inline UsdLuxRectLight UsdLuxRectLight::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdLuxRectLight();
    }
    return UsdLuxRectLight(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdLuxRectLight::GetLightShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightShaderId));
}

inline UsdAttribute UsdLuxRectLight::CreateLightShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightShaderId), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxRectLight::GetWidthAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsWidth));
}

inline UsdAttribute UsdLuxRectLight::CreateWidthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsWidth), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxRectLight::GetHeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsHeight));
}

inline UsdAttribute UsdLuxRectLight::CreateHeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsHeight), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxRectLight::GetTextureFileAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsTextureFile));
}

inline UsdAttribute UsdLuxRectLight::CreateTextureFileAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsTextureFile), SdfValueTypeNames->Asset,
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
