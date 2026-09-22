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

/// @file usdGeom/basisCurves.h

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
// BASISCURVES                                                                 //
// -------------------------------------------------------------------------- //

/// @class UsdGeomBasisCurves
///
/// BasisCurves are a batched curve representation analogous to the
/// classic RIB definition via Basis and Curves statements. BasisCurves are
/// often used to render dense aggregate geometry like hair or grass.
///
/// A 'matrix' and 'vstep' associated with the \em basis are used to
/// interpolate the vertices of a cubic BasisCurves. (The basis attribute
/// is unused for linear BasisCurves.)
///
/// A single prim may have many curves whose count is determined implicitly by
/// the length of the \em curveVertexCounts vector.  Each individual curve is
/// composed of one or more segments. Each segment is defined by four vertices
/// for cubic curves and two vertices for linear curves. See the next section
/// for more information on how to map curve vertex counts to segment counts.
///
/// \section UsdGeomBasisCurves_Segment Segment Indexing
/// Interpolating a curve requires knowing how to decompose it into its
/// individual segments.
///
/// The segments of a cubic curve are determined by the vertex count,
/// the \em wrap (periodicity), and the vstep of the basis. For linear
/// curves, the basis token is ignored and only the vertex count and
/// wrap are needed.
///
/// cubic basis   | vstep
/// ------------- | ------
/// bezier        | 3
/// catmullRom    | 1
/// bspline       | 1
///
/// The first segment of a cubic (nonperiodic) curve is always defined by its
/// first four points. The vstep is the increment used to determine what
/// vertex indices define the next segment.  For a two segment (nonperiodic)
/// bspline basis curve (vstep = 1), the first segment will be defined by
/// interpolating vertices [0, 1, 2, 3] and the second segment will be defined
/// by [1, 2, 3, 4].  For a two segment bezier basis curve (vstep = 3), the
/// first segment will be defined by interpolating vertices [0, 1, 2, 3] and
/// the second segment will be defined by [3, 4, 5, 6].  If the vstep is not
/// one, then you must take special care to make sure that the number of cvs
/// properly divides by your vstep. (The indices described are relative to
/// the initial vertex index for a batched curve.)
///
/// For periodic curves, at least one of the curve's initial vertices are
/// repeated to close the curve. For cubic curves, the number of vertices
/// repeated is '4 - vstep'. For linear curves, only one vertex is repeated
/// to close the loop.
///
/// Pinned curves are a special case of nonperiodic curves that only affects
/// the behavior of cubic Bspline and Catmull-Rom curves. To evaluate or render
/// pinned curves, a client must effectively add 'phantom points' at the
/// beginning and end of every curve in a batch.  These phantom points
/// are injected to ensure that the interpolated curve begins at P[0] and
/// ends at P[n-1].
///
/// For a curve with initial point P[0] and last point P[n-1], the phantom
/// points are defined as.
/// P[-1]  = 2 * P[0] - P[1]
/// P[n] = 2 * P[n-1] - P[n-2]
///
/// Pinned cubic curves will (usually) have to be unpacked into the standard
/// nonperiodic representation before rendering. This unpacking can add some
/// additional overhead. However, using pinned curves reduces the amount of
/// data recorded in a scene and (more importantly) better records the
/// authors' intent for interchange.
///
/// \note The additional phantom points mean that the minimum curve vertex
/// count for cubic bspline and catmullRom curves is 2.
///
/// Linear curve segments are defined by two vertices.
/// A two segment linear curve's first segment would be defined by
/// interpolating vertices [0, 1]. The second segment would be defined by
/// vertices [1, 2]. (Again, for a batched curve, indices are relative to
/// the initial vertex index.)
///
/// When validating curve topology, each renderable entry in the
/// curveVertexCounts vector must pass this check.
///
/// type    | wrap                        | validitity
/// ------- | --------------------------- | ----------------
/// linear  | nonperiodic                 | curveVertexCounts[i] > 2
/// linear  | periodic                    | curveVertexCounts[i] > 3
/// cubic   | nonperiodic                 | (curveVertexCounts[i] - 4) % vstep == 0
/// cubic   | periodic                    | (curveVertexCounts[i]) % vstep == 0
/// cubic   | pinned (catmullRom/bspline) | (curveVertexCounts[i] - 2) >= 0
///
/// \section UsdGeomBasisCurves_BasisMatrix Cubic Vertex Interpolation
///
/// \image html USDCurveBasisMatrix.png width=750
///
/// \section UsdGeomBasisCurves_Linear Linear Vertex Interpolation
///
/// Linear interpolation is always used on curves of type linear.
/// 't' with domain [0, 1], the curve is defined by the equation
/// P0 * (1-t) + P1 * t. t at 0 describes the first point and t at 1 describes
/// the end point.
///
/// \section UsdGeomBasisCurves_PrimvarInterpolation Primvar Interpolation
///
/// For cubic curves, primvar data can be either interpolated cubically between
/// vertices or linearly across segments.  The corresponding token
/// for cubic interpolation is 'vertex' and for linear interpolation is
/// 'varying'.  Per vertex data should be the same size as the number
/// of vertices in your curve.  Segment varying data is dependent on the
/// wrap (periodicity) and number of segments in your curve.  For linear curves,
/// varying and vertex data would be interpolated the same way.  By convention
/// varying is the preferred interpolation because of the association of
/// varying with linear interpolation.
///
/// \image html USDCurvePrimvars.png
///
/// To convert an entry in the curveVertexCounts vector into a segment count
/// for an individual curve, apply these rules.  Sum up all the results in
/// order to compute how many total segments all curves have.
///
/// The following tables describe the expected segment count for the 'i'th
/// curve in a curve batch as well as the entire batch. Python syntax
/// like '[:]' (to describe all members of an array) and 'len(...)'
/// (to describe the length of an array) are used.
///
/// type    | wrap                        | curve segment count                    | batch segment count
/// ------- | --------------------------- | -------------------------------------- | --------------------------
/// linear  | nonperiodic                 | curveVertexCounts[i] - 1               | sum(curveVertexCounts[:]) -
/// len(curveVertexCounts) linear  | periodic                    | curveVertexCounts[i]                   |
/// sum(curveVertexCounts[:]) cubic   | nonperiodic                 | (curveVertexCounts[i] - 4) / vstep + 1 |
/// sum(curveVertexCounts[:] - 4) / vstep + len(curveVertexCounts) cubic   | periodic                    |
/// curveVertexCounts[i] / vstep           | sum(curveVertexCounts[:]) / vstep cubic   | pinned (catmullRom/bspline) |
/// (curveVertexCounts[i] - 2) + 1         | sum(curveVertexCounts[:] - 2) + len(curveVertexCounts)
///
/// The following table descrives the expected size of varying
/// (linearly interpolated) data, derived from the segment counts computed
/// above.
///
/// wrap                | curve varying count          | batch varying count
/// ------------------- | ---------------------------- | ------------------------------------------------
/// nonperiodic/pinned  | segmentCounts[i] + 1         | sum(segmentCounts[:]) + len(curveVertexCounts)
/// periodic            | segmentCounts[i]             | sum(segmentCounts[:])
///
/// Both curve types additionally define 'constant' interpolation for the
/// entire prim and 'uniform' interpolation as per curve data.
///
///
/// \note Take care when providing support for linearly interpolated data for
/// cubic curves. Its shape doesn't provide a one to one mapping with either
/// the number of curves (like 'uniform') or the number of vertices (like
/// 'vertex') and so it is often overlooked. This is the only primitive in
/// UsdGeom (as of this writing) where this is true. For meshes, while they
/// use different interpolation methods, 'varying' and 'vertex' are both
/// specified per point. It's common to assume that curves follow a similar
/// pattern and build in structures and language for per primitive, per
/// element, and per point data only to come upon these arrays that don't
/// quite fit into either of those categories. It is
/// also common to conflate 'varying' with being per segment data and use the
/// segmentCount rules table instead of its neighboring varying data table
/// rules. We suspect that this is because for the common case of
/// nonperiodic cubic curves, both the provided segment count and varying data
/// size formula end with '+ 1'. While debugging, users may look at the double
/// '+ 1' as a mistake and try to remove it.  We take this time to enumerate
/// these issues because we've fallen into them before and hope that we save
/// others time in their own implementations.
///
/// As an example of deriving per curve segment and varying primvar data counts from
/// the wrap, type, basis, and curveVertexCount, the following table is provided.
///
/// wrap          | type    | basis   | curveVertexCount  | curveSegmentCount  | varyingDataCount
/// ------------- | ------- | ------- | ----------------- | ------------------ | -------------------------
/// nonperiodic   | linear  | N/A     | [2 3 2 5]         | [1 2 1 4]          | [2 3 2 5]
/// nonperiodic   | cubic   | bezier  | [4 7 10 4 7]      | [1 2 3 1 2]        | [2 3 4 2 3]
/// nonperiodic   | cubic   | bspline | [5 4 6 7]         | [2 1 3 4]          | [3 2 4 5]
/// periodic      | cubic   | bezier  | [6 9 6]           | [2 3 2]            | [2 3 2]
/// periodic      | linear  | N/A     | [3 7]             | [3 7]              | [3 7]
///
/// \section UsdGeomBasisCurves_TubesAndRibbons Tubes and Ribbons
///
/// The strictest definition of a curve as an infinitely thin wire is not
/// particularly useful for describing production scenes. The additional
/// \em widths and \em normals attributes can be used to describe cylindrical
/// tubes and or flat oriented ribbons.
///
/// Curves with only widths defined are imaged as tubes with radius
/// 'width / 2'. Curves with both widths and normals are imaged as ribbons
/// oriented in the direction of the interpolated normal vectors.
///
/// While not technically UsdGeomPrimvars, widths and normals
/// also have interpolation metadata. It's common for authored widths to have
/// constant, varying, or vertex interpolation
/// (see UsdGeomCurves::GetWidthsInterpolation()).  It's common for
/// authored normals to have varying interpolation
/// (see UsdGeomPointBased::GetNormalsInterpolation()).
///
/// \image html USDCurveHydra.png
///
/// The file used to generate these curves can be found in
/// pxr/extras/examples/usdGeomExamples/basisCurves.usda.  It's provided
/// as a reference on how to properly image both tubes and ribbons. The first
/// row of curves are linear; the second are cubic bezier. (We aim in future
/// releases of HdSt to fix the discontinuity seen with broken tangents to
/// better match offline renderers like RenderMan.) The yellow and violet
/// cubic curves represent cubic vertex width interpolation for which there is
/// no equivalent for linear curves.
///
/// \note How did this prim type get its name?  This prim is a portmanteau of
/// two different statements in the original RenderMan specification:
/// 'Basis' and 'Curves'.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomBasisCurves : public UsdGeomCurves
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomBasisCurves on UsdPrim @p prim.
    /// Equivalent to UsdGeomBasisCurves::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomBasisCurves(const UsdPrim& prim = UsdPrim()) : UsdGeomCurves(prim)
    {
    }

    /// Construct a UsdGeomBasisCurves on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomBasisCurves(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomBasisCurves(const UsdSchemaBase& schemaObj) : UsdGeomCurves(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomBasisCurves()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomBasisCurves Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // TYPE
    // --------------------------------------------------------------------- //
    /// Linear curves interpolate linearly between two vertices.
    /// Cubic curves use a basis matrix with four vertices to interpolate a segment.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token type = "cubic"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | linear, cubic |

    UsdAttribute GetTypeAttr() const;

    /// See GetTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BASIS
    // --------------------------------------------------------------------- //
    /// The basis specifies the vstep and matrix used for cubic
    /// interpolation.  \note The 'hermite' and 'power' tokens have been
    /// removed. We've provided UsdGeomHermiteCurves
    /// as an alternative for the 'hermite' basis.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token basis = "bezier"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | bezier, bspline, catmullRom |

    UsdAttribute GetBasisAttr() const;

    /// See GetBasisAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBasisAttr() const;

public:
    // --------------------------------------------------------------------- //
    // WRAP
    // --------------------------------------------------------------------- //
    /// If wrap is set to periodic, the curve when rendered will
    /// repeat the initial vertices (dependent on the vstep) to close the
    /// curve. If wrap is set to 'pinned', phantom points may be created
    /// to ensure that the curve interpolation starts at P[0] and ends at P[n-1].
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token wrap = "nonperiodic"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | nonperiodic, periodic, pinned |

    UsdAttribute GetWrapAttr() const;

    /// See GetWrapAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateWrapAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomBasisCurves::_GetStaticTfType()
{
    const static TfToken token("UsdGeomBasisCurves");
    return token;
}

/* virtual */
inline const TfToken UsdGeomBasisCurves::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomBasisCurves");
    return token;
}

/* static */
inline UsdGeomBasisCurves UsdGeomBasisCurves::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomBasisCurves();
    }
    return UsdGeomBasisCurves(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomBasisCurves::GetTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->type));
}

inline UsdAttribute UsdGeomBasisCurves::CreateTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->type), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomBasisCurves::GetBasisAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->basis));
}

inline UsdAttribute UsdGeomBasisCurves::CreateBasisAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->basis), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomBasisCurves::GetWrapAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->wrap));
}

inline UsdAttribute UsdGeomBasisCurves::CreateWrapAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->wrap), SdfValueTypeNames->Token,
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
