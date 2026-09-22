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

/// @file usdLux/volumeLightAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
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
// VOLUMELIGHTAPI                                                              //
// -------------------------------------------------------------------------- //

/// @class UsdLuxVolumeLightAPI
///
/// This is the preferred API schema to apply to
/// \ref UsdVolVolume "Volume" type prims when adding light behaviors to a
/// volume. At its base, this API schema has the built-in behavior of applying
/// LightAPI to the volume and overriding the default materialSyncMode to allow
/// the emission/glow of the bound material to affect the color of the light.
/// But, it additionally serves as a hook for plugins to attach additional
/// properties to "volume lights" through the creation of API schemas which are
/// authored to auto-apply to VolumeLightAPI.
/// \see \ref Usd_AutoAppliedAPISchemas
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdLuxTokens.
/// So to set an attribute to the value "rightHanded", use UsdLuxTokens->rightHanded
/// as the value.

class UsdLuxVolumeLightAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdLuxVolumeLightAPI on UsdPrim @p prim.
    /// Equivalent to UsdLuxVolumeLightAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdLuxVolumeLightAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdLuxVolumeLightAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdLuxVolumeLightAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdLuxVolumeLightAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdLuxVolumeLightAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "VolumeLightAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdLuxVolumeLightAPI object is returned upon success.
    /// An invalid (or empty) UsdLuxVolumeLightAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdLuxVolumeLightAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdLuxVolumeLightAPI>())
        {
            return UsdLuxVolumeLightAPI(prim);
        }
        return UsdLuxVolumeLightAPI();
    }

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
    /// | Declaration | `uniform token light:shaderId = "VolumeLight"` |
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
    // LIGHTMATERIALSYNCMODE
    // --------------------------------------------------------------------- //
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token light:materialSyncMode = "materialGlowTintsLight"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetLightMaterialSyncModeAttr() const;

    /// See GetLightMaterialSyncModeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLightMaterialSyncModeAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdLuxVolumeLightAPI::_GetStaticTfType()
{
    const static TfToken token("UsdLuxVolumeLightAPI");
    return token;
}

/* virtual */
inline const TfToken UsdLuxVolumeLightAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdLuxVolumeLightAPI");
    return token;
}


inline UsdAttribute UsdLuxVolumeLightAPI::GetLightShaderIdAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightShaderId));
}

inline UsdAttribute UsdLuxVolumeLightAPI::CreateLightShaderIdAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightShaderId), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdLuxVolumeLightAPI::GetLightMaterialSyncModeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdLuxTokens->lightMaterialSyncMode));
}

inline UsdAttribute UsdLuxVolumeLightAPI::CreateLightMaterialSyncModeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdLuxTokens->lightMaterialSyncMode), SdfValueTypeNames->Token,
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
