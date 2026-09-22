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

/// @file usdGeom/plane.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/gprim.h"
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
// PLANE                                                                       //
// -------------------------------------------------------------------------- //

/// @class UsdGeomPlane
///
/// Defines a primitive plane, centered at the origin, and is defined by
/// a cardinal axis, width, and length. The plane is double-sided by default.
///
/// The axis of width and length are perpendicular to the plane's \em axis:
///
/// axis  | width  | length
/// ----- | ------ | -------
/// X     | z-axis | y-axis
/// Y     | x-axis | z-axis
/// Z     | x-axis | y-axis
///
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomPlane : public UsdGeomGprim
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomPlane on UsdPrim @p prim.
    /// Equivalent to UsdGeomPlane::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomPlane(const UsdPrim& prim = UsdPrim()) : UsdGeomGprim(prim)
    {
    }

    /// Construct a UsdGeomPlane on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomPlane(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomPlane(const UsdSchemaBase& schemaObj) : UsdGeomGprim(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomPlane()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomPlane Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // DOUBLESIDED
    // --------------------------------------------------------------------- //
    /// Planes are double-sided by default. Clients may also support
    /// single-sided planes.
    ///
    /// \sa UsdGeomGprim::GetDoubleSidedAttr()
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform bool doubleSided = 1` |
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
    // WIDTH
    // --------------------------------------------------------------------- //
    /// The width of the plane, which aligns to the x-axis when \em axis is
    /// 'Z' or 'Y', or to the z-axis when \em axis is 'X'.  If you author \em width
    /// you must also author \em extent.
    ///
    /// \sa UsdGeomGprim::GetExtentAttr()
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double width = 2` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetWidthAttr() const;

    /// See GetWidthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWidthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // LENGTH
    // --------------------------------------------------------------------- //
    /// The length of the plane, which aligns to the y-axis when \em axis is
    /// 'Z' or 'X', or to the z-axis when \em axis is 'Y'.  If you author \em length
    /// you must also author \em extent.
    ///
    /// \sa UsdGeomGprim::GetExtentAttr()
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double length = 2` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetLengthAttr() const;

    /// See GetLengthAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateLengthAttr() const;

public:
    // --------------------------------------------------------------------- //
    // AXIS
    // --------------------------------------------------------------------- //
    /// The axis along which the surface of the plane is aligned. When set
    /// to 'Z' the plane is in the xy-plane; when \em axis is 'X' the plane is in
    /// the yz-plane, and when \em axis is 'Y' the plane is in the xz-plane.
    ///
    /// \sa UsdGeomGprim::GetAxisAttr().
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token axis = "Z"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | X, Y, Z |

    UsdAttribute GetAxisAttr() const;

    /// See GetAxisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAxisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // EXTENT
    // --------------------------------------------------------------------- //
    /// Extent is re-defined on Plane only to provide a fallback
    /// value. \sa UsdGeomGprim::GetExtentAttr().
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3[] extent = [(-1, -1, 0), (1, 1, 0)]` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3Array |

    UsdAttribute GetExtentAttr() const;

    /// See GetExtentAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateExtentAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomPlane::_GetStaticTfType()
{
    const static TfToken token("UsdGeomPlane");
    return token;
}

/* virtual */
inline const TfToken UsdGeomPlane::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomPlane");
    return token;
}

/* static */
inline UsdGeomPlane UsdGeomPlane::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomPlane();
    }
    return UsdGeomPlane(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomPlane::GetDoubleSidedAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->doubleSided));
}

inline UsdAttribute UsdGeomPlane::CreateDoubleSidedAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->doubleSided), SdfValueTypeNames->Bool,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPlane::GetWidthAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->width));
}

inline UsdAttribute UsdGeomPlane::CreateWidthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->width), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPlane::GetLengthAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->length));
}

inline UsdAttribute UsdGeomPlane::CreateLengthAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->length), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPlane::GetAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->axis));
}

inline UsdAttribute UsdGeomPlane::CreateAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->axis), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPlane::GetExtentAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->extent));
}

inline UsdAttribute UsdGeomPlane::CreateExtentAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->extent), SdfValueTypeNames->Float3Array,
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
