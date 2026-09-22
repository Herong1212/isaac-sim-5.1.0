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

/// @file usdGeom/cone.h

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
// CONE                                                                        //
// -------------------------------------------------------------------------- //

/// @class UsdGeomCone
///
/// Defines a primitive cone, centered at the origin, whose spine
/// is along the specified \em axis, with the apex of the cone pointing
/// in the direction of the positive axis.
///
/// The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
/// they all pack into the same volume/bounds.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomCone : public UsdGeomGprim
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomCone on UsdPrim @p prim.
    /// Equivalent to UsdGeomCone::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomCone(const UsdPrim& prim = UsdPrim()) : UsdGeomGprim(prim)
    {
    }

    /// Construct a UsdGeomCone on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomCone(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomCone(const UsdSchemaBase& schemaObj) : UsdGeomGprim(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomCone()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomCone Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // HEIGHT
    // --------------------------------------------------------------------- //
    /// The size of the cone's spine along the specified
    /// \em axis.  If you author \em height you must also author \em extent.
    ///
    /// \sa GetExtentAttr()
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double height = 2` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetHeightAttr() const;

    /// See GetHeightAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHeightAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RADIUS
    // --------------------------------------------------------------------- //
    /// The radius of the cone.  If you
    /// author \em radius you must also author \em extent.
    ///
    /// \sa GetExtentAttr()
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double radius = 1` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetRadiusAttr() const;

    /// See GetRadiusAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRadiusAttr() const;

public:
    // --------------------------------------------------------------------- //
    // AXIS
    // --------------------------------------------------------------------- //
    /// The axis along which the spine of the cone is aligned
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
    /// Extent is re-defined on Cone only to provide a fallback
    /// value. \sa UsdGeomGprim::GetExtentAttr().
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3[] extent = [(-1, -1, -1), (1, 1, 1)]` |
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

inline const TfToken UsdGeomCone::_GetStaticTfType()
{
    const static TfToken token("UsdGeomCone");
    return token;
}

/* virtual */
inline const TfToken UsdGeomCone::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomCone");
    return token;
}

/* static */
inline UsdGeomCone UsdGeomCone::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomCone();
    }
    return UsdGeomCone(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomCone::GetHeightAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->height));
}

inline UsdAttribute UsdGeomCone::CreateHeightAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->height), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCone::GetRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->radius));
}

inline UsdAttribute UsdGeomCone::CreateRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->radius), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCone::GetAxisAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->axis));
}

inline UsdAttribute UsdGeomCone::CreateAxisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->axis), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCone::GetExtentAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->extent));
}

inline UsdAttribute UsdGeomCone::CreateExtentAttr() const
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
