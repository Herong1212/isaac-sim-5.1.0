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

/// @file usdGeom/sphere.h

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
// SPHERE                                                                      //
// -------------------------------------------------------------------------- //

/// @class UsdGeomSphere
///
/// Defines a primitive sphere centered at the origin.
///
/// The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
/// they all pack into the same volume/bounds.

class UsdGeomSphere : public UsdGeomGprim
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomSphere on UsdPrim @p prim.
    /// Equivalent to UsdGeomSphere::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomSphere(const UsdPrim& prim = UsdPrim()) : UsdGeomGprim(prim)
    {
    }

    /// Construct a UsdGeomSphere on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomSphere(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomSphere(const UsdSchemaBase& schemaObj) : UsdGeomGprim(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomSphere()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomSphere Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // RADIUS
    // --------------------------------------------------------------------- //
    /// Indicates the sphere's radius.  If you
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
    // EXTENT
    // --------------------------------------------------------------------- //
    /// Extent is re-defined on Sphere only to provide a fallback
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

inline const TfToken UsdGeomSphere::_GetStaticTfType()
{
    const static TfToken token("UsdGeomSphere");
    return token;
}

/* virtual */
inline const TfToken UsdGeomSphere::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomSphere");
    return token;
}

/* static */
inline UsdGeomSphere UsdGeomSphere::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomSphere();
    }
    return UsdGeomSphere(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomSphere::GetRadiusAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->radius));
}

inline UsdAttribute UsdGeomSphere::CreateRadiusAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->radius), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomSphere::GetExtentAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->extent));
}

inline UsdAttribute UsdGeomSphere::CreateExtentAttr() const
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
