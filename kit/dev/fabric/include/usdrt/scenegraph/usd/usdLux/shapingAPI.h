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

/// @file usdLux/shapingAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdLux/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdShade/input.h"
#include "usdrt/scenegraph/usd/usdShade/output.h" */
// clang-format on

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
// SHAPINGAPI                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdLuxShapingAPI
///
/// Controls for shaping a light's emission.

class UsdLuxShapingAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdLuxShapingAPI on UsdPrim @p prim.
    /// Equivalent to UsdLuxShapingAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxShapingAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdLuxShapingAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxShapingAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxShapingAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxShapingAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "ShapingAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdLuxShapingAPI object is returned upon success.
    /// An invalid (or empty) UsdLuxShapingAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdLuxShapingAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdLuxShapingAPI>())
        {
            return UsdLuxShapingAPI(prim);
        }
        return UsdLuxShapingAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SHAPING:FOCUS
    // --------------------------------------------------------------------- //
    /// A control to shape the spread of light.  Higher focus
    /// values pull light towards the center and narrow the spread.
    /// Implemented as an off-axis cosine power exponent.
    /// TODO: clarify semantics
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:shaping:focus = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetShapingFocusAttr() const;

    /// See GetShapingFocusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShapingFocusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHAPING:FOCUSTINT
    // --------------------------------------------------------------------- //
    /// Off-axis color tint.  This tints the emission in the
    /// falloff region.  The default tint is black.
    /// TODO: clarify semantics
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `color3f inputs:shaping:focusTint = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Color3f |

    UsdAttribute GetShapingFocusTintAttr() const;

    /// See GetShapingFocusTintAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShapingFocusTintAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHAPING:CONE:ANGLE
    // --------------------------------------------------------------------- //
    /// Angular limit off the primary axis to restrict the
    /// light spread.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:shaping:cone:angle = 90` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetShapingConeAngleAttr() const;

    /// See GetShapingConeAngleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShapingConeAngleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHAPING:CONE:SOFTNESS
    // --------------------------------------------------------------------- //
    /// Controls the cutoff softness for cone angle.
    /// TODO: clarify semantics
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:shaping:cone:softness = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetShapingConeSoftnessAttr() const;

    /// See GetShapingConeSoftnessAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShapingConeSoftnessAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHAPING:IES:FILE
    // --------------------------------------------------------------------- //
    /// An IES (Illumination Engineering Society) light
    /// profile describing the angular distribution of light.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `asset inputs:shaping:ies:file` |
    /// | C++ Type | SdfAssetPath |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Asset |

    UsdAttribute GetShapingIesFileAttr() const;

    /// See GetShapingIesFileAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShapingIesFileAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHAPING:IES:ANGLESCALE
    // --------------------------------------------------------------------- //
    /// Rescales the angular distribution of the IES profile.
    /// TODO: clarify semantics
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:shaping:ies:angleScale = 0` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetShapingIesAngleScaleAttr() const;

    /// See GetShapingIesAngleScaleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShapingIesAngleScaleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHAPING:IES:NORMALIZE
    // --------------------------------------------------------------------- //
    /// Normalizes the IES profile so that it affects the shaping
    /// of the light while preserving the overall energy output.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool inputs:shaping:ies:normalize = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetShapingIesNormalizeAttr() const;

    /// See GetShapingIesNormalizeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShapingIesNormalizeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxShapingAPI::_GetStaticTfType()
{
    const static TfToken token("UsdLuxShapingAPI");
    return token;
}

/* virtual */
inline const TfToken UsdLuxShapingAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxShapingAPI");
    return token;
}


inline UsdAttribute UsdLuxShapingAPI::GetShapingFocusAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShapingFocus));
}

inline UsdAttribute UsdLuxShapingAPI::CreateShapingFocusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShapingFocus), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShapingAPI::GetShapingFocusTintAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShapingFocusTint));
}

inline UsdAttribute UsdLuxShapingAPI::CreateShapingFocusTintAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShapingFocusTint), SdfValueTypeNames->Color3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShapingAPI::GetShapingConeAngleAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShapingConeAngle));
}

inline UsdAttribute UsdLuxShapingAPI::CreateShapingConeAngleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShapingConeAngle), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShapingAPI::GetShapingConeSoftnessAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShapingConeSoftness));
}

inline UsdAttribute UsdLuxShapingAPI::CreateShapingConeSoftnessAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShapingConeSoftness), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShapingAPI::GetShapingIesFileAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShapingIesFile));
}

inline UsdAttribute UsdLuxShapingAPI::CreateShapingIesFileAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShapingIesFile), SdfValueTypeNames->Asset,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShapingAPI::GetShapingIesAngleScaleAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShapingIesAngleScale));
}

inline UsdAttribute UsdLuxShapingAPI::CreateShapingIesAngleScaleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShapingIesAngleScale), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShapingAPI::GetShapingIesNormalizeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShapingIesNormalize));
}

inline UsdAttribute UsdLuxShapingAPI::CreateShapingIesNormalizeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShapingIesNormalize), SdfValueTypeNames->Bool,
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
