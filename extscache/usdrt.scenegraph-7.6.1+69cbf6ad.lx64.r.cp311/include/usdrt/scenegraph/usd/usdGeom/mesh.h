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

/// @file usdGeom/mesh.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/pointBased.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/timeCode.h" */
// clang-format on

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
// MESH                                                                        //
// -------------------------------------------------------------------------- //

/// @class UsdGeomMesh
///
/// Encodes a mesh with optional subdivision properties and features.
///
/// As a point-based primitive, meshes are defined in terms of points that
/// are connected into edges and faces. Many references to meshes use the
/// term 'vertex' in place of or interchangeably with 'points', while some
/// use 'vertex' to refer to the 'face-vertices' that define a face.  To
/// avoid confusion, the term 'vertex' is intentionally avoided in favor of
/// 'points' or 'face-vertices'.
///
/// The connectivity between points, edges and faces is encoded using a
/// common minimal topological description of the faces of the mesh.  Each
/// face is defined by a set of face-vertices using indices into the Mesh's
/// _points_ array (inherited from UsdGeomPointBased) and laid out in a
/// single linear _faceVertexIndices_ array for efficiency.  A companion
/// _faceVertexCounts_ array provides, for each face, the number of
/// consecutive face-vertices in _faceVertexIndices_ that define the face.
/// No additional connectivity information is required or constructed, so
/// no adjacency or neighborhood queries are available.
///
/// A key property of this mesh schema is that it encodes both subdivision
/// surfaces and simpler polygonal meshes. This is achieved by varying the
/// _subdivisionScheme_ attribute, which is set to specify Catmull-Clark
/// subdivision by default, so polygonal meshes must always be explicitly
/// declared. The available subdivision schemes and additional subdivision
/// features encoded in optional attributes conform to the feature set of
/// OpenSubdiv
/// (https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html).
///
/// \anchor UsdGeom_Mesh_Primvars
/// __A Note About Primvars__
///
/// The following list clarifies the number of elements for and the
/// interpolation behavior of the different primvar interpolation types
/// for meshes:
///
/// - __constant__: One element for the entire mesh; no interpolation.
/// - __uniform__: One element for each face of the mesh; elements are
/// typically not interpolated but are inherited by other faces derived
/// from a given face (via subdivision, tessellation, etc.).
/// - __varying__: One element for each point of the mesh;
/// interpolation of point data is always linear.
/// - __vertex__: One element for each point of the mesh;
/// interpolation of point data is applied according to the
/// _subdivisionScheme_ attribute.
/// - __faceVarying__: One element for each of the face-vertices that
/// define the mesh topology; interpolation of face-vertex data may
/// be smooth or linear, according to the _subdivisionScheme_ and
/// _faceVaryingLinearInterpolation_ attributes.
///
/// Primvar interpolation types and related utilities are described more
/// generally in \ref Usd_InterpolationVals.
///
/// \anchor UsdGeom_Mesh_Normals
/// __A Note About Normals__
///
/// Normals should not be authored on a subdivision mesh, since subdivision
/// algorithms define their own normals. They should only be authored for
/// polygonal meshes (_subdivisionScheme_ = "none").
///
/// The _normals_ attribute inherited from UsdGeomPointBased is not a generic
/// primvar, but the number of elements in this attribute will be determined by
/// its _interpolation_.  See \ref UsdGeomPointBased::GetNormalsInterpolation() .
/// If _normals_ and _primvars:normals_ are both specified, the latter has
/// precedence.  If a polygonal mesh specifies __neither__ _normals_ nor
/// _primvars:normals_, then it should be treated and rendered as faceted,
/// with no attempt to compute smooth normals.
///
/// The normals generated for smooth subdivision schemes, e.g. Catmull-Clark
/// and Loop, will likewise be smooth, but others, e.g. Bilinear, may be
/// discontinuous between faces and/or within non-planar irregular faces.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomMesh : public UsdGeomPointBased
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomMesh on UsdPrim @p prim.
    /// Equivalent to UsdGeomMesh::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomMesh(const UsdPrim& prim = UsdPrim()) : UsdGeomPointBased(prim)
    {
    }

    /// Construct a UsdGeomMesh on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomMesh(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomMesh(const UsdSchemaBase& schemaObj) : UsdGeomPointBased(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomMesh()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomMesh Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // FACEVERTEXINDICES
    // --------------------------------------------------------------------- //
    /// Flat list of the index (into the _points_ attribute) of each
    /// vertex of each face in the mesh.  If this attribute has more than
    /// one timeSample, the mesh is considered to be topologically varying.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] faceVertexIndices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetFaceVertexIndicesAttr() const;

    /// See GetFaceVertexIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFaceVertexIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FACEVERTEXCOUNTS
    // --------------------------------------------------------------------- //
    /// Provides the number of vertices in each face of the mesh,
    /// which is also the number of consecutive indices in _faceVertexIndices_
    /// that define the face.  The length of this attribute is the number of
    /// faces in the mesh.  If this attribute has more than
    /// one timeSample, the mesh is considered to be topologically varying.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] faceVertexCounts` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetFaceVertexCountsAttr() const;

    /// See GetFaceVertexCountsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFaceVertexCountsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SUBDIVISIONSCHEME
    // --------------------------------------------------------------------- //
    /// The subdivision scheme to be applied to the surface.
    /// Valid values are:
    ///
    /// - __catmullClark__: The default, Catmull-Clark subdivision; preferred
    /// for quad-dominant meshes (generalizes B-splines); interpolation
    /// of point data is smooth (non-linear)
    /// - __loop__: Loop subdivision; preferred for purely triangular meshes;
    /// interpolation of point data is smooth (non-linear)
    /// - __bilinear__: Subdivision reduces all faces to quads (topologically
    /// similar to "catmullClark"); interpolation of point data is bilinear
    /// - __none__: No subdivision, i.e. a simple polygonal mesh; interpolation
    /// of point data is linear
    ///
    /// Polygonal meshes are typically lighter weight and faster to render,
    /// depending on renderer and render mode.  Use of "bilinear" will produce
    /// a similar shape to a polygonal mesh and may offer additional guarantees
    /// of watertightness and additional subdivision features (e.g. holes) but
    /// may also not respect authored normals.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token subdivisionScheme = "catmullClark"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | catmullClark, loop, bilinear, none |

    UsdAttribute GetSubdivisionSchemeAttr() const;

    /// See GetSubdivisionSchemeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSubdivisionSchemeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INTERPOLATEBOUNDARY
    // --------------------------------------------------------------------- //
    /// Specifies how subdivision is applied for faces adjacent to
    /// boundary edges and boundary points. Valid values correspond to choices
    /// available in OpenSubdiv:
    ///
    /// - __none__: No boundary interpolation is applied and boundary faces are
    /// effectively treated as holes
    /// - __edgeOnly__: A sequence of boundary edges defines a smooth curve to
    /// which the edges of subdivided boundary faces converge
    /// - __edgeAndCorner__: The default, similar to "edgeOnly" but the smooth
    /// boundary curve is made sharp at corner points
    ///
    /// These are illustrated and described in more detail in the OpenSubdiv
    /// documentation:
    /// https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#boundary-interpolation-rules
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token interpolateBoundary = "edgeAndCorner"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdGeomTokens "Allowed Values" | none, edgeOnly, edgeAndCorner |

    UsdAttribute GetInterpolateBoundaryAttr() const;

    /// See GetInterpolateBoundaryAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateInterpolateBoundaryAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FACEVARYINGLINEARINTERPOLATION
    // --------------------------------------------------------------------- //
    /// Specifies how elements of a primvar of interpolation type
    /// "faceVarying" are interpolated for subdivision surfaces. Interpolation
    /// can be as smooth as a "vertex" primvar or constrained to be linear at
    /// features specified by several options.  Valid values correspond to
    /// choices available in OpenSubdiv:
    ///
    /// - __none__: No linear constraints or sharpening, smooth everywhere
    /// - __cornersOnly__: Sharpen corners of discontinuous boundaries only,
    /// smooth everywhere else
    /// - __cornersPlus1__: The default, same as "cornersOnly" plus additional
    /// sharpening at points where three or more distinct face-varying
    /// values occur
    /// - __cornersPlus2__: Same as "cornersPlus1" plus additional sharpening
    /// at points with at least one discontinuous boundary corner or
    /// only one discontinuous boundary edge (a dart)
    /// - __boundaries__: Piecewise linear along discontinuous boundaries,
    /// smooth interior
    /// - __all__: Piecewise linear everywhere
    ///
    /// These are illustrated and described in more detail in the OpenSubdiv
    /// documentation:
    /// https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#face-varying-interpolation-rules
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token faceVaryingLinearInterpolation = "cornersPlus1"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdGeomTokens "Allowed Values" | none, cornersOnly, cornersPlus1, cornersPlus2, boundaries, all |

    UsdAttribute GetFaceVaryingLinearInterpolationAttr() const;

    /// See GetFaceVaryingLinearInterpolationAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFaceVaryingLinearInterpolationAttr() const;

public:
    // --------------------------------------------------------------------- //
    // TRIANGLESUBDIVISIONRULE
    // --------------------------------------------------------------------- //
    /// Specifies an option to the subdivision rules for the
    /// Catmull-Clark scheme to try and improve undesirable artifacts when
    /// subdividing triangles.  Valid values are "catmullClark" for the
    /// standard rules (the default) and "smooth" for the improvement.
    ///
    /// See https://graphics.pixar.com/opensubdiv/docs/subdivision_surfaces.html#triangle-subdivision-rule
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token triangleSubdivisionRule = "catmullClark"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdGeomTokens "Allowed Values" | catmullClark, smooth |

    UsdAttribute GetTriangleSubdivisionRuleAttr() const;

    /// See GetTriangleSubdivisionRuleAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTriangleSubdivisionRuleAttr() const;

public:
    // --------------------------------------------------------------------- //
    // HOLEINDICES
    // --------------------------------------------------------------------- //
    /// The indices of all faces that should be treated as holes,
    /// i.e. made invisible. This is traditionally a feature of subdivision
    /// surfaces and not generally applied to polygonal meshes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] holeIndices = []` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetHoleIndicesAttr() const;

    /// See GetHoleIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateHoleIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CORNERINDICES
    // --------------------------------------------------------------------- //
    /// The indices of points for which a corresponding sharpness
    /// value is specified in _cornerSharpnesses_ (so the size of this array
    /// must match that of _cornerSharpnesses_).
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] cornerIndices = []` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetCornerIndicesAttr() const;

    /// See GetCornerIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCornerIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CORNERSHARPNESSES
    // --------------------------------------------------------------------- //
    /// The sharpness values associated with a corresponding set of
    /// points specified in _cornerIndices_ (so the size of this array must
    /// match that of _cornerIndices_). Use the constant `SHARPNESS_INFINITE`
    /// for a perfectly sharp corner.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] cornerSharpnesses = []` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetCornerSharpnessesAttr() const;

    /// See GetCornerSharpnessesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCornerSharpnessesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CREASEINDICES
    // --------------------------------------------------------------------- //
    /// The indices of points grouped into sets of successive pairs
    /// that identify edges to be creased. The size of this array must be
    /// equal to the sum of all elements of the _creaseLengths_ attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] creaseIndices = []` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetCreaseIndicesAttr() const;

    /// See GetCreaseIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCreaseIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CREASELENGTHS
    // --------------------------------------------------------------------- //
    /// The length of this array specifies the number of creases
    /// (sets of adjacent sharpened edges) on the mesh. Each element gives
    /// the number of points of each crease, whose indices are successively
    /// laid out in the _creaseIndices_ attribute. Since each crease must
    /// be at least one edge long, each element of this array must be at
    /// least two.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] creaseLengths = []` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetCreaseLengthsAttr() const;

    /// See GetCreaseLengthsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCreaseLengthsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // CREASESHARPNESSES
    // --------------------------------------------------------------------- //
    /// The per-crease or per-edge sharpness values for all creases.
    /// Since _creaseLengths_ encodes the number of points in each crease,
    /// the number of elements in this array will be either len(creaseLengths)
    /// or the sum over all X of (creaseLengths[X] - 1). Note that while
    /// the RI spec allows each crease to have either a single sharpness
    /// or a value per-edge, USD will encode either a single sharpness
    /// per crease on a mesh, or sharpnesses for all edges making up
    /// the creases on a mesh.  Use the constant `SHARPNESS_INFINITE` for a
    /// perfectly sharp crease.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] creaseSharpnesses = []` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetCreaseSharpnessesAttr() const;

    /// See GetCreaseSharpnessesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateCreaseSharpnessesAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomMesh::_GetStaticTfType()
{
    const static TfToken token("UsdGeomMesh");
    return token;
}

/* virtual */
inline const TfToken UsdGeomMesh::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomMesh");
    return token;
}

/* static */
inline UsdGeomMesh UsdGeomMesh::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomMesh();
    }
    return UsdGeomMesh(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomMesh::GetFaceVertexIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->faceVertexIndices));
}

inline UsdAttribute UsdGeomMesh::CreateFaceVertexIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->faceVertexIndices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetFaceVertexCountsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->faceVertexCounts));
}

inline UsdAttribute UsdGeomMesh::CreateFaceVertexCountsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->faceVertexCounts), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetSubdivisionSchemeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->subdivisionScheme));
}

inline UsdAttribute UsdGeomMesh::CreateSubdivisionSchemeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->subdivisionScheme), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetInterpolateBoundaryAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->interpolateBoundary));
}

inline UsdAttribute UsdGeomMesh::CreateInterpolateBoundaryAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->interpolateBoundary), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetFaceVaryingLinearInterpolationAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->faceVaryingLinearInterpolation));
}

inline UsdAttribute UsdGeomMesh::CreateFaceVaryingLinearInterpolationAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->faceVaryingLinearInterpolation), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetTriangleSubdivisionRuleAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->triangleSubdivisionRule));
}

inline UsdAttribute UsdGeomMesh::CreateTriangleSubdivisionRuleAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->triangleSubdivisionRule), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetHoleIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->holeIndices));
}

inline UsdAttribute UsdGeomMesh::CreateHoleIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->holeIndices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetCornerIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->cornerIndices));
}

inline UsdAttribute UsdGeomMesh::CreateCornerIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->cornerIndices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetCornerSharpnessesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->cornerSharpnesses));
}

inline UsdAttribute UsdGeomMesh::CreateCornerSharpnessesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->cornerSharpnesses), SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetCreaseIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->creaseIndices));
}

inline UsdAttribute UsdGeomMesh::CreateCreaseIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->creaseIndices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetCreaseLengthsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->creaseLengths));
}

inline UsdAttribute UsdGeomMesh::CreateCreaseLengthsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->creaseLengths), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomMesh::GetCreaseSharpnessesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->creaseSharpnesses));
}

inline UsdAttribute UsdGeomMesh::CreateCreaseSharpnessesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->creaseSharpnesses), SdfValueTypeNames->FloatArray,
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
