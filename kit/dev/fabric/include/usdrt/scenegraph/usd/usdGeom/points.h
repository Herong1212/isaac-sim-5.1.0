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

/// @file usdGeom/points.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/pointBased.h"
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
// POINTS                                                                      //
// -------------------------------------------------------------------------- //

/// @class UsdGeomPoints
///
/// Points are analogous to the <A
/// HREF="https://renderman.pixar.com/resources/current/RenderMan/appnote.18.html">RiPoints spec</A>.
///
/// Points can be an efficient means of storing and rendering particle
/// effects comprised of thousands or millions of small particles.  Points
/// generally receive a single shading sample each, which should take
/// \em normals into account, if present.
///
/// While not technically UsdGeomPrimvars, the widths and normals also
/// have interpolation metadata.  It's common for authored widths and normals
/// to have constant or varying interpolation.

class UsdGeomPoints : public UsdGeomPointBased
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomPoints on UsdPrim @p prim.
    /// Equivalent to UsdGeomPoints::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomPoints(const UsdPrim& prim = UsdPrim()) : UsdGeomPointBased(prim)
    {
    }

    /// Construct a UsdGeomPoints on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomPoints(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomPoints(const UsdSchemaBase& schemaObj) : UsdGeomPointBased(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomPoints()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomPoints Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // WIDTHS
    // --------------------------------------------------------------------- //
    /// Widths are defined as the \em diameter of the points, in
    /// object space.  'widths' is not a generic Primvar, but
    /// the number of elements in this attribute will be determined by
    /// its 'interpolation'.  See \ref SetWidthsInterpolation() .  If
    /// 'widths' and 'primvars:widths' are both specified, the latter
    /// has precedence.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] widths` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetWidthsAttr() const;

    /// See GetWidthsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWidthsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // IDS
    // --------------------------------------------------------------------- //
    /// Ids are optional; if authored, the ids array should be the same
    /// length as the points array, specifying (at each timesample if
    /// point identities are changing) the id of each point. The
    /// type is signed intentionally, so that clients can encode some
    /// binary state on Id'd points without adding a separate
    /// primvar.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int64[] ids` |
    /// | C++ Type | VtArray<int64_t> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int64Array |

    UsdAttribute GetIdsAttr() const;

    /// See GetIdsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIdsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomPoints::_GetStaticTfType()
{
    const static TfToken token("UsdGeomPoints");
    return token;
}

/* virtual */
inline const TfToken UsdGeomPoints::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomPoints");
    return token;
}

/* static */
inline UsdGeomPoints UsdGeomPoints::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomPoints();
    }
    return UsdGeomPoints(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomPoints::GetWidthsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->widths));
}

inline UsdAttribute UsdGeomPoints::CreateWidthsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->widths), SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPoints::GetIdsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->ids));
}

inline UsdAttribute UsdGeomPoints::CreateIdsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->ids), SdfValueTypeNames->Int64Array,
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
