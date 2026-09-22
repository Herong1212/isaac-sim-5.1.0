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

/// @file usdGeom/nurbsPatch.h

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
// NURBSPATCH                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdGeomNurbsPatch
///
/// Encodes a rational or polynomial non-uniform B-spline
/// surface, with optional trim curves.
///
/// The encoding mostly follows that of RiNuPatch and RiTrimCurve:
/// https://renderman.pixar.com/resources/current/RenderMan/geometricPrimitives.html#rinupatch , with some minor
/// renaming and coalescing for clarity.
///
/// The layout of control vertices in the \em points attribute inherited
/// from UsdGeomPointBased is row-major with U considered rows, and V columns.
///
/// \anchor UsdGeom_NurbsPatch_Form
/// <b>NurbsPatch Form</b>
///
/// The authored points, orders, knots, weights, and ranges are all that is
/// required to render the nurbs patch.  However, the only way to model closed
/// surfaces with nurbs is to ensure that the first and last control points
/// along the given axis are coincident.  Similarly, to ensure the surface is
/// not only closed but also C2 continuous, the last \em order - 1 control
/// points must be (correspondingly) coincident with the first \em order - 1
/// control points, and also the spacing of the last corresponding knots
/// must be the same as the first corresponding knots.
///
/// <b>Form</b> is provided as an aid to interchange between modeling and
/// animation applications so that they can robustly identify the intent with
/// which the surface was modelled, and take measures (if they are able) to
/// preserve the continuity/concidence constraints as the surface may be rigged
/// or deformed.
/// \li An \em open-form NurbsPatch has no continuity constraints.
/// \li A \em closed-form NurbsPatch expects the first and last control points
/// to overlap
/// \li A \em periodic-form NurbsPatch expects the first and last
/// \em order - 1 control points to overlap.
///
/// <b>Nurbs vs Subdivision Surfaces</b>
///
/// Nurbs are an important modeling primitive in CAD/CAM tools and early
/// computer graphics DCC's.  Because they have a natural UV parameterization
/// they easily support "trim curves", which allow smooth shapes to be
/// carved out of the surface.
///
/// However, the topology of the patch is always rectangular, and joining two
/// nurbs patches together (especially when they have differing numbers of
/// spans) is difficult to do smoothly.  Also, nurbs are not supported by
/// the Ptex texturing technology (http://ptex.us).
///
/// Neither of these limitations are shared by subdivision surfaces; therefore,
/// although they do not subscribe to trim-curve-based shaping, subdivs are
/// often considered a more flexible modeling primitive.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomNurbsPatch : public UsdGeomPointBased
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomNurbsPatch on UsdPrim @p prim.
    /// Equivalent to UsdGeomNurbsPatch::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomNurbsPatch(const UsdPrim& prim = UsdPrim()) : UsdGeomPointBased(prim)
    {
    }

    /// Construct a UsdGeomNurbsPatch on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomNurbsPatch(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomNurbsPatch(const UsdSchemaBase& schemaObj) : UsdGeomPointBased(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomNurbsPatch()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomNurbsPatch Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // UVERTEXCOUNT
    // --------------------------------------------------------------------- //
    /// Number of vertices in the U direction.  Should be at least as
    /// large as uOrder.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int uVertexCount` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetUVertexCountAttr() const;

    /// See GetUVertexCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUVertexCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VVERTEXCOUNT
    // --------------------------------------------------------------------- //
    /// Number of vertices in the V direction.  Should be at least as
    /// large as vOrder.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int vVertexCount` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetVVertexCountAttr() const;

    /// See GetVVertexCountAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVVertexCountAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UORDER
    // --------------------------------------------------------------------- //
    /// Order in the U direction.  Order must be positive and is
    /// equal to the degree of the polynomial basis to be evaluated, plus 1.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int uOrder` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetUOrderAttr() const;

    /// See GetUOrderAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUOrderAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VORDER
    // --------------------------------------------------------------------- //
    /// Order in the V direction.  Order must be positive and is
    /// equal to the degree of the polynomial basis to be evaluated, plus 1.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int vOrder` |
    /// | C++ Type | int |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Int |

    UsdAttribute GetVOrderAttr() const;

    /// See GetVOrderAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVOrderAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UKNOTS
    // --------------------------------------------------------------------- //
    /// Knot vector for U direction providing U parameterization.
    /// The length of this array must be ( uVertexCount + uOrder ), and its
    /// entries must take on monotonically increasing values.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double[] uKnots` |
    /// | C++ Type | VtArray<double> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->DoubleArray |

    UsdAttribute GetUKnotsAttr() const;

    /// See GetUKnotsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUKnotsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VKNOTS
    // --------------------------------------------------------------------- //
    /// Knot vector for V direction providing U parameterization.
    /// The length of this array must be ( vVertexCount + vOrder ), and its
    /// entries must take on monotonically increasing values.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double[] vKnots` |
    /// | C++ Type | VtArray<double> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->DoubleArray |

    UsdAttribute GetVKnotsAttr() const;

    /// See GetVKnotsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVKnotsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // UFORM
    // --------------------------------------------------------------------- //
    /// Interpret the control grid and knot vectors as representing
    /// an open, geometrically closed, or geometrically closed and C2 continuous
    /// surface along the U dimension.
    /// \sa \ref UsdGeom_NurbsPatch_Form "NurbsPatch Form"
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token uForm = "open"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | open, closed, periodic |

    UsdAttribute GetUFormAttr() const;

    /// See GetUFormAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateUFormAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VFORM
    // --------------------------------------------------------------------- //
    /// Interpret the control grid and knot vectors as representing
    /// an open, geometrically closed, or geometrically closed and C2 continuous
    /// surface along the V dimension.
    /// \sa \ref UsdGeom_NurbsPatch_Form "NurbsPatch Form"
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token vForm = "open"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | open, closed, periodic |

    UsdAttribute GetVFormAttr() const;

    /// See GetVFormAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVFormAttr() const;

public:
    // --------------------------------------------------------------------- //
    // URANGE
    // --------------------------------------------------------------------- //
    /// Provides the minimum and maximum parametric values (as defined
    /// by uKnots) over which the surface is actually defined.  The minimum
    /// must be less than the maximum, and greater than or equal to the
    /// value of uKnots[uOrder-1].  The maxium must be less than or equal
    /// to the last element's value in uKnots.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double2 uRange` |
    /// | C++ Type | GfVec2d |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double2 |

    UsdAttribute GetURangeAttr() const;

    /// See GetURangeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateURangeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VRANGE
    // --------------------------------------------------------------------- //
    /// Provides the minimum and maximum parametric values (as defined
    /// by vKnots) over which the surface is actually defined.  The minimum
    /// must be less than the maximum, and greater than or equal to the
    /// value of vKnots[vOrder-1].  The maxium must be less than or equal
    /// to the last element's value in vKnots.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double2 vRange` |
    /// | C++ Type | GfVec2d |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double2 |

    UsdAttribute GetVRangeAttr() const;

    /// See GetVRangeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVRangeAttr() const;

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
    // TRIMCURVECOUNTS
    // --------------------------------------------------------------------- //
    /// Each element specifies how many curves are present in each
    /// "loop" of the trimCurve, and the length of the array determines how
    /// many loops the trimCurve contains.  The sum of all elements is the
    /// total nuber of curves in the trim, to which we will refer as
    /// \em nCurves in describing the other trim attributes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] trimCurve:counts` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetTrimCurveCountsAttr() const;

    /// See GetTrimCurveCountsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrimCurveCountsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRIMCURVEORDERS
    // --------------------------------------------------------------------- //
    /// Flat list of orders for each of the \em nCurves curves.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] trimCurve:orders` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetTrimCurveOrdersAttr() const;

    /// See GetTrimCurveOrdersAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrimCurveOrdersAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRIMCURVEVERTEXCOUNTS
    // --------------------------------------------------------------------- //
    /// Flat list of number of vertices for each of the
    /// \em nCurves curves.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] trimCurve:vertexCounts` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetTrimCurveVertexCountsAttr() const;

    /// See GetTrimCurveVertexCountsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrimCurveVertexCountsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRIMCURVEKNOTS
    // --------------------------------------------------------------------- //
    /// Flat list of parametric values for each of the
    /// \em nCurves curves.  There will be as many knots as the sum over
    /// all elements of \em vertexCounts plus the sum over all elements of
    /// \em orders.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double[] trimCurve:knots` |
    /// | C++ Type | VtArray<double> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->DoubleArray |

    UsdAttribute GetTrimCurveKnotsAttr() const;

    /// See GetTrimCurveKnotsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrimCurveKnotsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRIMCURVERANGES
    // --------------------------------------------------------------------- //
    /// Flat list of minimum and maximum parametric values
    /// (as defined by \em knots) for each of the \em nCurves curves.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double2[] trimCurve:ranges` |
    /// | C++ Type | VtArray<GfVec2d> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double2Array |

    UsdAttribute GetTrimCurveRangesAttr() const;

    /// See GetTrimCurveRangesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrimCurveRangesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRIMCURVEPOINTS
    // --------------------------------------------------------------------- //
    /// Flat list of homogeneous 2D points (u, v, w) that comprise
    /// the \em nCurves curves.  The number of points should be equal to the
    /// um over all elements of \em vertexCounts.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `double3[] trimCurve:points` |
    /// | C++ Type | VtArray<GfVec3d> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Double3Array |

    UsdAttribute GetTrimCurvePointsAttr() const;

    /// See GetTrimCurvePointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTrimCurvePointsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomNurbsPatch::_GetStaticTfType()
{
    const static TfToken token("UsdGeomNurbsPatch");
    return token;
}

/* virtual */
inline const TfToken UsdGeomNurbsPatch::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomNurbsPatch");
    return token;
}

/* static */
inline UsdGeomNurbsPatch UsdGeomNurbsPatch::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomNurbsPatch();
    }
    return UsdGeomNurbsPatch(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomNurbsPatch::GetUVertexCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->uVertexCount));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateUVertexCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->uVertexCount), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetVVertexCountAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->vVertexCount));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateVVertexCountAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->vVertexCount), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetUOrderAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->uOrder));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateUOrderAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->uOrder), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetVOrderAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->vOrder));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateVOrderAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->vOrder), SdfValueTypeNames->Int,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetUKnotsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->uKnots));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateUKnotsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->uKnots), SdfValueTypeNames->DoubleArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetVKnotsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->vKnots));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateVKnotsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->vKnots), SdfValueTypeNames->DoubleArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetUFormAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->uForm));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateUFormAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->uForm), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetVFormAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->vForm));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateVFormAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->vForm), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetURangeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->uRange));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateURangeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->uRange), SdfValueTypeNames->Double2,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetVRangeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->vRange));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateVRangeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->vRange), SdfValueTypeNames->Double2,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetPointWeightsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->pointWeights));
}

inline UsdAttribute UsdGeomNurbsPatch::CreatePointWeightsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->pointWeights), SdfValueTypeNames->DoubleArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetTrimCurveCountsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->trimCurveCounts));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateTrimCurveCountsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->trimCurveCounts), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetTrimCurveOrdersAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->trimCurveOrders));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateTrimCurveOrdersAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->trimCurveOrders), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetTrimCurveVertexCountsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->trimCurveVertexCounts));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateTrimCurveVertexCountsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->trimCurveVertexCounts), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetTrimCurveKnotsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->trimCurveKnots));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateTrimCurveKnotsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->trimCurveKnots), SdfValueTypeNames->DoubleArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetTrimCurveRangesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->trimCurveRanges));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateTrimCurveRangesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->trimCurveRanges), SdfValueTypeNames->Double2Array,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomNurbsPatch::GetTrimCurvePointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->trimCurvePoints));
}

inline UsdAttribute UsdGeomNurbsPatch::CreateTrimCurvePointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->trimCurvePoints), SdfValueTypeNames->Double3Array,
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
