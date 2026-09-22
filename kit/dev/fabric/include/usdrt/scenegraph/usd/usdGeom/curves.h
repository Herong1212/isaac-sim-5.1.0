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

/// @file usdGeom/curves.h

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
// CURVES                                                                      //
// -------------------------------------------------------------------------- //

/// @class UsdGeomCurves
///
/// Base class for UsdGeomBasisCurves, UsdGeomNurbsCurves, and
/// UsdGeomHermiteCurves.  The BasisCurves schema is designed to be
/// analagous to offline renderers' notion of batched curves (such as
/// the classical RIB definition via Basis and Curves statements),
/// while the NurbsCurve schema is designed to be analgous to the
/// NURBS curves found in packages like Maya and Houdini while
/// retaining their consistency with the RenderMan specification for
/// NURBS Patches. HermiteCurves are useful for the
/// interchange of animation guides and paths.
///
/// It is safe to use the length of the curve vertex count to derive
/// the number of curves and the number and layout of curve vertices,
/// but this schema should NOT be used to derive the number of curve
/// points. While vertex indices are implicit in all shipped
/// descendent types of this schema, one should not assume that all
/// internal or future shipped schemas will follow this pattern. Be
/// sure to key any indexing behavior off the concrete type, not this
/// abstract type.
///

class UsdGeomCurves : public UsdGeomPointBased
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdGeomCurves on UsdPrim @p prim.
    /// Equivalent to UsdGeomCurves::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomCurves(const UsdPrim& prim = UsdPrim()) : UsdGeomPointBased(prim)
    {
    }

    /// Construct a UsdGeomCurves on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomCurves(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomCurves(const UsdSchemaBase& schemaObj) : UsdGeomPointBased(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomCurves()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // CURVEVERTEXCOUNTS
    // --------------------------------------------------------------------- //
    /// Curves-derived primitives can represent multiple distinct,
    /// potentially disconnected curves.  The length of 'curveVertexCounts'
    /// gives the number of such curves, and each element describes the
    /// number of vertices in the corresponding curve
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] curveVertexCounts` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetCurveVertexCountsAttr() const;

    /// See GetCurveVertexCountsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCurveVertexCountsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WIDTHS
    // --------------------------------------------------------------------- //
    /// Provides width specification for the curves, whose application
    /// will depend on whether the curve is oriented (normals are defined for
    /// it), in which case widths are "ribbon width", or unoriented, in which
    /// case widths are cylinder width.  'widths' is not a generic Primvar,
    /// but the number of elements in this attribute will be determined by
    /// its 'interpolation'.  See \ref SetWidthsInterpolation() .  If 'widths'
    /// and 'primvars:widths' are both specified, the latter has precedence.
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

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomCurves::_GetStaticTfType()
{
    const static TfToken token("UsdGeomCurves");
    return token;
}

/* virtual */
inline const TfToken UsdGeomCurves::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomCurves");
    return token;
}


inline UsdAttribute UsdGeomCurves::GetCurveVertexCountsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->curveVertexCounts));
}

inline UsdAttribute UsdGeomCurves::CreateCurveVertexCountsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->curveVertexCounts), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomCurves::GetWidthsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->widths));
}

inline UsdAttribute UsdGeomCurves::CreateWidthsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->widths), SdfValueTypeNames->FloatArray,
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
