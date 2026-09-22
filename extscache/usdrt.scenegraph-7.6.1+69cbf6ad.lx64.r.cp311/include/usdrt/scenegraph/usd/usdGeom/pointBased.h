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

/// @file usdGeom/pointBased.h

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
// POINTBASED                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdGeomPointBased
///
/// Base class for all UsdGeomGprims that possess points,
/// providing common attributes such as normals and velocities.

class UsdGeomPointBased : public UsdGeomGprim
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdGeomPointBased on UsdPrim @p prim.
    /// Equivalent to UsdGeomPointBased::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomPointBased(const UsdPrim& prim = UsdPrim()) : UsdGeomGprim(prim)
    {
    }

    /// Construct a UsdGeomPointBased on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomPointBased(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomPointBased(const UsdSchemaBase& schemaObj) : UsdGeomGprim(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomPointBased()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // POINTS
    // --------------------------------------------------------------------- //
    /// The primary geometry attribute for all PointBased
    /// primitives, describes points in (local) space.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `point3f[] points` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Point3fArray |

    UsdAttribute GetPointsAttr() const;

    /// See GetPointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePointsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // VELOCITIES
    // --------------------------------------------------------------------- //
    /// If provided, 'velocities' should be used by renderers to
    ///
    /// compute positions between samples for the 'points' attribute, rather
    /// than interpolating between neighboring 'points' samples.  This is the
    /// only reasonable means of computing motion blur for topologically
    /// varying PointBased primitives.  It follows that the length of each
    /// 'velocities' sample must match the length of the corresponding
    /// 'points' sample.  Velocity is measured in position units per second,
    /// as per most simulation software. To convert to position units per
    /// UsdTimeCode, divide by UsdStage::GetTimeCodesPerSecond().
    ///
    /// See also \ref UsdGeom_VelocityInterpolation .
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f[] velocities` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3fArray |

    UsdAttribute GetVelocitiesAttr() const;

    /// See GetVelocitiesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVelocitiesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ACCELERATIONS
    // --------------------------------------------------------------------- //
    /// If provided, 'accelerations' should be used with
    /// velocities to compute positions between samples for the 'points'
    /// attribute rather than interpolating between neighboring 'points'
    /// samples. Acceleration is measured in position units per second-squared.
    /// To convert to position units per squared UsdTimeCode, divide by the
    /// square of UsdStage::GetTimeCodesPerSecond().
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `vector3f[] accelerations` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3fArray |

    UsdAttribute GetAccelerationsAttr() const;

    /// See GetAccelerationsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateAccelerationsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NORMALS
    // --------------------------------------------------------------------- //
    /// Provide an object-space orientation for individual points,
    /// which, depending on subclass, may define a surface, curve, or free
    /// points.  Note that 'normals' should not be authored on any Mesh that
    /// is subdivided, since the subdivision algorithm will define its own
    /// normals. 'normals' is not a generic primvar, but the number of elements
    /// in this attribute will be determined by its 'interpolation'.  See
    /// \ref SetNormalsInterpolation() . If 'normals' and 'primvars:normals'
    /// are both specified, the latter has precedence.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `normal3f[] normals` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Normal3fArray |

    UsdAttribute GetNormalsAttr() const;

    /// See GetNormalsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNormalsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomPointBased::_GetStaticTfType()
{
    const static TfToken token("UsdGeomPointBased");
    return token;
}

/* virtual */
inline const TfToken UsdGeomPointBased::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomPointBased");
    return token;
}


inline UsdAttribute UsdGeomPointBased::GetPointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->points));
}

inline UsdAttribute UsdGeomPointBased::CreatePointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->points), SdfValueTypeNames->Point3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPointBased::GetVelocitiesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->velocities));
}

inline UsdAttribute UsdGeomPointBased::CreateVelocitiesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->velocities), SdfValueTypeNames->Vector3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPointBased::GetAccelerationsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->accelerations));
}

inline UsdAttribute UsdGeomPointBased::CreateAccelerationsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->accelerations), SdfValueTypeNames->Vector3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomPointBased::GetNormalsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->normals));
}

inline UsdAttribute UsdGeomPointBased::CreateNormalsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->normals), SdfValueTypeNames->Normal3fArray,
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
