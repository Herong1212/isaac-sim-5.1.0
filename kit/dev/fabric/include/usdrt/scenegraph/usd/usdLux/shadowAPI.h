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

/// @file usdLux/shadowAPI.h

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
// SHADOWAPI                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdLuxShadowAPI
///
/// Controls to refine a light's shadow behavior.  These are
/// non-physical controls that are valuable for visual lighting work.

class UsdLuxShadowAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdLuxShadowAPI on UsdPrim @p prim.
    /// Equivalent to UsdLuxShadowAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxShadowAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdLuxShadowAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxShadowAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxShadowAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxShadowAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "ShadowAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdLuxShadowAPI object is returned upon success.
    /// An invalid (or empty) UsdLuxShadowAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdLuxShadowAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdLuxShadowAPI>())
        {
            return UsdLuxShadowAPI(prim);
        }
        return UsdLuxShadowAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SHADOW:ENABLE
    // --------------------------------------------------------------------- //
    /// Enables shadows to be cast by this light.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `bool inputs:shadow:enable = 1` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |

    UsdAttribute GetShadowEnableAttr() const;

    /// See GetShadowEnableAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShadowEnableAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHADOW:COLOR
    // --------------------------------------------------------------------- //
    /// The color of shadows cast by the light.  This is a
    /// non-physical control.  The default is to cast black shadows.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `color3f inputs:shadow:color = (0, 0, 0)` |
    /// | C++ Type | GfVec3f |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Color3f |

    UsdAttribute GetShadowColorAttr() const;

    /// See GetShadowColorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShadowColorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHADOW:DISTANCE
    // --------------------------------------------------------------------- //
    /// The maximum distance shadows are cast.
    /// The default value (-1) indicates no limit.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:shadow:distance = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetShadowDistanceAttr() const;

    /// See GetShadowDistanceAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShadowDistanceAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHADOW:FALLOFF
    // --------------------------------------------------------------------- //
    /// The near distance at which shadow falloff begins.
    /// The default value (-1) indicates no falloff.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:shadow:falloff = -1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetShadowFalloffAttr() const;

    /// See GetShadowFalloffAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShadowFalloffAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SHADOW:FALLOFFGAMMA
    // --------------------------------------------------------------------- //
    /// A gamma (i.e., exponential) control over shadow strength
    /// with linear distance within the falloff zone.
    /// This requires the use of shadowDistance and shadowFalloff.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float inputs:shadow:falloffGamma = 1` |
    /// | C++ Type | float |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float |

    UsdAttribute GetShadowFalloffGammaAttr() const;

    /// See GetShadowFalloffGammaAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateShadowFalloffGammaAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxShadowAPI::_GetStaticTfType()
{
    const static TfToken token("UsdLuxShadowAPI");
    return token;
}

/* virtual */
inline const TfToken UsdLuxShadowAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxShadowAPI");
    return token;
}


inline UsdAttribute UsdLuxShadowAPI::GetShadowEnableAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShadowEnable));
}

inline UsdAttribute UsdLuxShadowAPI::CreateShadowEnableAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShadowEnable), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShadowAPI::GetShadowColorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShadowColor));
}

inline UsdAttribute UsdLuxShadowAPI::CreateShadowColorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShadowColor), SdfValueTypeNames->Color3f,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShadowAPI::GetShadowDistanceAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShadowDistance));
}

inline UsdAttribute UsdLuxShadowAPI::CreateShadowDistanceAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShadowDistance), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShadowAPI::GetShadowFalloffAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShadowFalloff));
}

inline UsdAttribute UsdLuxShadowAPI::CreateShadowFalloffAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShadowFalloff), SdfValueTypeNames->Float,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxShadowAPI::GetShadowFalloffGammaAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->inputsShadowFalloffGamma));
}

inline UsdAttribute UsdLuxShadowAPI::CreateShadowFalloffGammaAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->inputsShadowFalloffGamma), SdfValueTypeNames->Float,
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
