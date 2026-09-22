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

/// @file usdGeom/hermiteCurves.h

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
// HERMITECURVES                                                               //
// -------------------------------------------------------------------------- //

/// @class UsdGeomHermiteCurves
///
/// This schema specifies a cubic hermite interpolated curve batch as
/// sometimes used for defining guides for animation. While hermite curves can
/// be useful because they interpolate through their control points, they are
/// not well supported by high-end renderers for imaging. Therefore, while we
/// include this schema for interchange, we strongly recommend the use of
/// UsdGeomBasisCurves as the representation of curves intended to be rendered
/// (ie. hair or grass). Hermite curves can be converted to a Bezier
/// representation (though not from Bezier back to Hermite in general).
///
/// \section UsdGeomHermiteCurves_Interpolation Point Interpolation
///
/// The initial cubic curve segment is defined by the first two points and
/// first two tangents. Additional segments are defined by additional
/// point / tangent pairs.  The number of segments for each non-batched hermite
/// curve would be len(curve.points) - 1.  The total number of segments
/// for the batched UsdGeomHermiteCurves representation is
/// len(points) - len(curveVertexCounts).
///
/// \section UsdGeomHermiteCurves_Primvars Primvar, Width, and Normal Interpolation
///
/// Primvar interpolation is not well specified for this type as it is not
/// intended as a rendering representation. We suggest that per point
/// primvars would be linearly interpolated across each segment and should
/// be tagged as 'varying'.
///
/// It is not immediately clear how to specify cubic or 'vertex' interpolation
/// for this type, as we lack a specification for primvar tangents. This
/// also means that width and normal interpolation should be restricted to
/// varying (linear), uniform (per curve element), or constant (per prim).
///

class UsdGeomHermiteCurves : public UsdGeomCurves
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomHermiteCurves on UsdPrim @p prim.
    /// Equivalent to UsdGeomHermiteCurves::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomHermiteCurves(const UsdPrim& prim = UsdPrim()) : UsdGeomCurves(prim)
    {
    }

    /// Construct a UsdGeomHermiteCurves on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomHermiteCurves(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomHermiteCurves(const UsdSchemaBase& schemaObj) : UsdGeomCurves(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomHermiteCurves()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomHermiteCurves Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // TANGENTS
    // --------------------------------------------------------------------- //
    /// Defines the outgoing trajectory tangent for each point.
    /// Tangents should be the same size as the points attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f[] tangents = []` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3fArray |

    UsdAttribute GetTangentsAttr() const;

    /// See GetTangentsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTangentsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomHermiteCurves::_GetStaticTfType()
{
    const static TfToken token("UsdGeomHermiteCurves");
    return token;
}

/* virtual */
inline const TfToken UsdGeomHermiteCurves::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomHermiteCurves");
    return token;
}

/* static */
inline UsdGeomHermiteCurves UsdGeomHermiteCurves::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomHermiteCurves();
    }
    return UsdGeomHermiteCurves(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomHermiteCurves::GetTangentsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->tangents));
}

inline UsdAttribute UsdGeomHermiteCurves::CreateTangentsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->tangents), SdfValueTypeNames->Vector3fArray,
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
