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

/// @file usdGeom/boundable.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/xformable.h"
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
// BOUNDABLE                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdGeomBoundable
///
/// Boundable introduces the ability for a prim to persistently
/// cache a rectilinear, local-space, extent.
///
/// \section UsdGeom_Boundable_Extent Why Extent and not Bounds ?
/// Boundable introduces the notion of "extent", which is a cached computation
/// of a prim's local-space 3D range for its resolved attributes <b>at the
/// layer and time in which extent is authored</b>.  We have found that with
/// composed scene description, attempting to cache pre-computed bounds at
/// interior prims in a scene graph is very fragile, given the ease with which
/// one can author a single attribute in a stronger layer that can invalidate
/// many authored caches - or with which a re-published, referenced asset can
/// do the same.
///
/// Therefore, we limit to precomputing (generally) leaf-prim extent, which
/// avoids the need to read in large point arrays to compute bounds, and
/// provides UsdGeomBBoxCache the means to efficiently compute and
/// (session-only) cache intermediate bounds.  You are free to compute and
/// author intermediate bounds into your scenes, of course, which may work
/// well if you have sufficient locks on your pipeline to guarantee that once
/// authored, the geometry and transforms upon which they are based will
/// remain unchanged, or if accuracy of the bounds is not an ironclad
/// requisite.
///
/// When intermediate bounds are authored on Boundable parents, the child prims
/// will be pruned from BBox computation; the authored extent is expected to
/// incorporate all child bounds.

class UsdGeomBoundable : public UsdGeomXformable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdGeomBoundable on UsdPrim @p prim.
    /// Equivalent to UsdGeomBoundable::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomBoundable(const UsdPrim& prim = UsdPrim()) : UsdGeomXformable(prim)
    {
    }

    /// Construct a UsdGeomBoundable on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomBoundable(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomBoundable(const UsdSchemaBase& schemaObj) : UsdGeomXformable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomBoundable()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // EXTENT
    // --------------------------------------------------------------------- //
    /// Extent is a three dimensional range measuring the geometric
    /// extent of the authored gprim in its own local space (i.e. its own
    /// transform not applied), \em without accounting for any shader-induced
    /// displacement. If __any__ extent value has been authored for a given
    /// Boundable, then it should be authored at every timeSample at which
    /// geometry-affecting properties are authored, to ensure correct
    /// evaluation via ComputeExtent(). If __no__ extent value has been
    /// authored, then ComputeExtent() will call the Boundable's registered
    /// ComputeExtentFunction(), which may be expensive, which is why we
    /// strongly encourage proper authoring of extent.
    /// \sa ComputeExtent()
    /// \sa \ref UsdGeom_Boundable_Extent.
    ///
    /// An authored extent on a prim which has children is expected to include
    /// the extent of all children, as they will be pruned from BBox computation
    /// during traversal.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3[] extent` |
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

inline const TfToken UsdGeomBoundable::_GetStaticTfType()
{
    const static TfToken token("UsdGeomBoundable");
    return token;
}

/* virtual */
inline const TfToken UsdGeomBoundable::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomBoundable");
    return token;
}


inline UsdAttribute UsdGeomBoundable::GetExtentAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->extent));
}

inline UsdAttribute UsdGeomBoundable::CreateExtentAttr() const
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
