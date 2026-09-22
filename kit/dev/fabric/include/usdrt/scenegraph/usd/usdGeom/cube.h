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

/// @file usdGeom/cube.h

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
// for test, please do not remove this next line
#define TEST_CUSTOM_INCLUDES 1
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
// CUBE                                                                        //
// -------------------------------------------------------------------------- //

/// @class UsdGeomCube
///
/// Defines a primitive rectilinear cube centered at the origin.
///
/// The fallback values for Cube, Sphere, Cone, and Cylinder are set so that
/// they all pack into the same volume/bounds.

class UsdGeomCube : public UsdGeomGprim
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomCube on UsdPrim @p prim.
    /// Equivalent to UsdGeomCube::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomCube(const UsdPrim& prim = UsdPrim()) : UsdGeomGprim(prim)
    {
    }

    /// Construct a UsdGeomCube on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomCube(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomCube(const UsdSchemaBase& schemaObj) : UsdGeomGprim(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomCube()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomCube Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // SIZE
    // --------------------------------------------------------------------- //
    /// Indicates the length of each edge of the cube.  If you
    /// author \em size you must also author \em extent.
    ///
    /// \sa GetExtentAttr()
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double size = 2` |
    /// | C++ Type | double |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double |

    UsdAttribute GetSizeAttr() const;

    /// See GetSizeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSizeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // EXTENT
    // --------------------------------------------------------------------- //
    /// Extent is re-defined on Cube only to provide a fallback value.
    /// \sa UsdGeomGprim::GetExtentAttr().
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

inline const TfToken UsdGeomCube::_GetStaticTfType()
{
    const static TfToken token("UsdGeomCube");
    return token;
}

/* virtual */
inline const TfToken UsdGeomCube::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomCube");
    return token;
}

/* static */
inline UsdGeomCube UsdGeomCube::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomCube();
    }
    return UsdGeomCube(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomCube::GetSizeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->size));
}

inline UsdAttribute UsdGeomCube::CreateSizeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->size), SdfValueTypeNames->Double,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCube::GetExtentAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->extent));
}

inline UsdAttribute UsdGeomCube::CreateExtentAttr() const
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
