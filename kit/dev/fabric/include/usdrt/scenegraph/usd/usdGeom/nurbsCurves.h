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

/// @file usdGeom/nurbsCurves.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/curves.h"
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
// NURBSCURVES                                                                 //
// -------------------------------------------------------------------------- //

/// @class UsdGeomNurbsCurves
///
/// This schema is analagous to NURBS Curves in packages like Maya
/// and Houdini, often used for interchange of rigging and modeling curves.
/// Unlike Maya, this curve spec supports batching of multiple curves into a
/// single prim, widths, and normals in the schema.  Additionally, we require
/// 'numSegments + 2 * degree + 1' knots (2 more than maya does).  This is to
/// be more consistent with RenderMan's NURBS patch specification.
///
/// To express a periodic curve:
/// - knot[0] = knot[1] - (knots[-2] - knots[-3];
/// - knot[-1] = knot[-2] + (knot[2] - knots[1]);
///
/// To express a nonperiodic curve:
/// - knot[0] = knot[1];
/// - knot[-1] = knot[-2];
///
/// In spite of these slight differences in the spec, curves generated in Maya
/// should be preserved when roundtripping.
///
/// \em order and \em range, when representing a batched NurbsCurve should be
/// authored one value per curve.  \em knots should be the concatentation of
/// all batched curves.
///
/// \anchor UsdGeom_NurbsCurve_Form
/// <b> NurbsCurve Form </b>
///
/// <b>Form</b> is provided as an aid to interchange between modeling and
/// animation applications so that they can robustly identify the intent with
/// which the surface was modelled, and take measures (if they are able) to
/// preserve the continuity/concidence constraints as the surface may be rigged
/// or deformed.
/// \li An \em open-form NurbsCurve has no continuity constraints.
/// \li A \em closed-form NurbsCurve expects the first and last control points
/// to overlap
/// \li A \em periodic-form NurbsCurve expects the first and last
/// \em order - 1 control points to overlap.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomNurbsCurves : public UsdGeomCurves
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomNurbsCurves on UsdPrim @p prim.
    /// Equivalent to UsdGeomNurbsCurves::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomNurbsCurves(const UsdPrim& prim = UsdPrim()) : UsdGeomCurves(prim)
    {
    }

    /// Construct a UsdGeomNurbsCurves on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomNurbsCurves(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomNurbsCurves(const UsdSchemaBase& schemaObj) : UsdGeomCurves(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomNurbsCurves()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomNurbsCurves Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ORDER
    // --------------------------------------------------------------------- //
    /// Order of the curve.  Order must be positive and is
    /// equal to the degree of the polynomial basis to be evaluated, plus 1.
    /// Its value for the 'i'th curve must be less than or equal to
    /// curveVertexCount[i]
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] order = []` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetOrderAttr() const;

    /// See GetOrderAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateOrderAttr() const;

public:
    // --------------------------------------------------------------------- //
    // KNOTS
    // --------------------------------------------------------------------- //
    /// Knot vector providing curve parameterization.
    /// The length of the slice of the array for the ith curve
    /// must be ( curveVertexCount[i] + order[i] ), and its
    /// entries must take on monotonically increasing values.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double[] knots` |
    /// | C++ Type | VtArray<double> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->DoubleArray |

    UsdAttribute GetKnotsAttr() const;

    /// See GetKnotsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateKnotsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RANGES
    // --------------------------------------------------------------------- //
    /// Provides the minimum and maximum parametric values (as defined
    /// by knots) over which the curve is actually defined.  The minimum must
    /// be less than the maximum, and greater than or equal to the value of the
    /// knots['i'th curve slice][order[i]-1]. The maxium must be less
    /// than or equal to the last element's value in knots['i'th curve slice].
    /// Range maps to (vmin, vmax) in the RenderMan spec.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double2[] ranges` |
    /// | C++ Type | VtArray<GfVec2d> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double2Array |

    UsdAttribute GetRangesAttr() const;

    /// See GetRangesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRangesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // POINTWEIGHTS
    // --------------------------------------------------------------------- //
    /// Optionally provides "w" components for each control point,
    /// thus must be the same length as the points attribute.  If authored,
    /// the patch will be rational.  If unauthored, the patch will be
    /// polynomial, i.e. weight for all points is 1.0.
    /// \note Some DCC's pre-weight the \em points, but in this schema,
    /// \em points are not pre-weighted.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double[] pointWeights` |
    /// | C++ Type | VtArray<double> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->DoubleArray |

    UsdAttribute GetPointWeightsAttr() const;

    /// See GetPointWeightsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePointWeightsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FORM
    // --------------------------------------------------------------------- //
    /// Interpret the control grid and knot vectors as representing
    /// an open, geometrically closed, or geometrically closed and C2 continuous
    /// curve.
    /// \sa \ref UsdGeom_NurbsCurve_Form "NurbsCurve Form"
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token form = "open"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | open, closed, periodic |

    UsdAttribute GetFormAttr() const;

    /// See GetFormAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFormAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomNurbsCurves::_GetStaticTfType()
{
    const static TfToken token("UsdGeomNurbsCurves");
    return token;
}

/* virtual */
inline const TfToken UsdGeomNurbsCurves::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomNurbsCurves");
    return token;
}

/* static */
inline UsdGeomNurbsCurves UsdGeomNurbsCurves::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomNurbsCurves();
    }
    return UsdGeomNurbsCurves(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomNurbsCurves::GetOrderAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->order));
}

inline UsdAttribute UsdGeomNurbsCurves::CreateOrderAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->order), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsCurves::GetKnotsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->knots));
}

inline UsdAttribute UsdGeomNurbsCurves::CreateKnotsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->knots), SdfValueTypeNames->DoubleArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsCurves::GetRangesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->ranges));
}

inline UsdAttribute UsdGeomNurbsCurves::CreateRangesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->ranges), SdfValueTypeNames->Double2Array,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsCurves::GetPointWeightsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->pointWeights));
}

inline UsdAttribute UsdGeomNurbsCurves::CreatePointWeightsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->pointWeights), SdfValueTypeNames->DoubleArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsCurves::GetFormAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->form));
}

inline UsdAttribute UsdGeomNurbsCurves::CreateFormAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->form), SdfValueTypeNames->Token,
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
