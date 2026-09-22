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

/// @file usdGeom/gprim.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/boundable.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"


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
// GPRIM                                                                       //
// -------------------------------------------------------------------------- //

/// @class UsdGeomGprim
///
/// Base class for all geometric primitives.
///
/// Gprim encodes basic graphical properties such as \em doubleSided and
/// \em orientation, and provides primvars for "display color" and "display
/// opacity" that travel with geometry to be used as shader overrides.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomGprim : public UsdGeomBoundable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdGeomGprim on UsdPrim @p prim.
    /// Equivalent to UsdGeomGprim::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomGprim(const UsdPrim& prim = UsdPrim()) : UsdGeomBoundable(prim)
    {
    }

    /// Construct a UsdGeomGprim on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomGprim(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomGprim(const UsdSchemaBase& schemaObj) : UsdGeomBoundable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomGprim()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DISPLAYCOLOR
    // --------------------------------------------------------------------- //
    /// It is useful to have an "official" colorSet that can be used
    /// as a display or modeling color, even in the absence of any specified
    /// shader for a gprim.  DisplayColor serves this role; because it is a
    /// UsdGeomPrimvar, it can also be used as a gprim override for any shader
    /// that consumes a \em displayColor parameter.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `color3f[] primvars:displayColor` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Color3fArray |

    UsdAttribute GetDisplayColorAttr() const;

    /// See GetDisplayColorAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisplayColorAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DISPLAYOPACITY
    // --------------------------------------------------------------------- //
    /// Companion to \em displayColor that specifies opacity, broken
    /// out as an independent attribute rather than an rgba color, both so that
    /// each can be independently overridden, and because shaders rarely consume
    /// rgba parameters.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] primvars:displayOpacity` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetDisplayOpacityAttr() const;

    /// See GetDisplayOpacityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDisplayOpacityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // DOUBLESIDED
    // --------------------------------------------------------------------- //
    /// Although some renderers treat all parametric or polygonal
    /// surfaces as if they were effectively laminae with outward-facing
    /// normals on both sides, some renderers derive significant optimizations
    /// by considering these surfaces to have only a single outward side,
    /// typically determined by control-point winding order and/or
    /// \em orientation.  By doing so they can perform "backface culling" to
    /// avoid drawing the many polygons of most closed surfaces that face away
    /// from the viewer.
    ///
    /// However, it is often advantageous to model thin objects such as paper
    /// and cloth as single, open surfaces that must be viewable from both
    /// sides, always.  Setting a gprim's \em doubleSided attribute to
    /// \c true instructs all renderers to disable optimizations such as
    /// backface culling for the gprim, and attempt (not all renderers are able
    /// to do so, but the USD reference GL renderer always will) to provide
    /// forward-facing normals on each side of the surface for lighting
    /// calculations.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool doubleSided = 0` |
    /// | C++ Type | bool |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Bool |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetDoubleSidedAttr() const;

    /// See GetDoubleSidedAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateDoubleSidedAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ORIENTATION
    // --------------------------------------------------------------------- //
    /// Orientation specifies whether the gprim's surface normal
    /// should be computed using the right hand rule, or the left hand rule.
    /// Please see \ref UsdGeom_WindingOrder for a deeper explanation and
    /// generalization of orientation to composed scenes with transformation
    /// hierarchies.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token orientation = "rightHanded"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | rightHanded, leftHanded |

    UsdAttribute GetOrientationAttr() const;

    /// See GetOrientationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateOrientationAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomGprim::_GetStaticTfType()
{
    const static TfToken token("UsdGeomGprim");
    return token;
}

/* virtual */
inline const TfToken UsdGeomGprim::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomGprim");
    return token;
}


inline UsdAttribute UsdGeomGprim::GetDisplayColorAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->primvarsDisplayColor));
}

inline UsdAttribute UsdGeomGprim::CreateDisplayColorAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->primvarsDisplayColor), SdfValueTypeNames->Color3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomGprim::GetDisplayOpacityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->primvarsDisplayOpacity));
}

inline UsdAttribute UsdGeomGprim::CreateDisplayOpacityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->primvarsDisplayOpacity), SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomGprim::GetDoubleSidedAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->doubleSided));
}

inline UsdAttribute UsdGeomGprim::CreateDoubleSidedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->doubleSided), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomGprim::GetOrientationAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->orientation));
}

inline UsdAttribute UsdGeomGprim::CreateOrientationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->orientation), SdfValueTypeNames->Token,
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
