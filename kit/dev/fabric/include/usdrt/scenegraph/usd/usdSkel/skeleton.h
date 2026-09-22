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

/// @file usdSkel/skeleton.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usdGeom/boundable.h"
#include "usdrt/scenegraph/usd/usdSkel/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdSkel/topology.h" */
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
// SKELETON                                                                    //
// -------------------------------------------------------------------------- //

/// @class UsdSkelSkeleton
///
/// Describes a skeleton.
///
/// See the extended \ref UsdSkel_Skeleton "Skeleton Schema" documentation for
/// more information.
///

class UsdSkelSkeleton : public UsdGeomBoundable
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdSkelSkeleton on UsdPrim @p prim.
    /// Equivalent to UsdSkelSkeleton::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdSkelSkeleton(const UsdPrim& prim = UsdPrim()) : UsdGeomBoundable(prim)
    {
    }

    /// Construct a UsdSkelSkeleton on the prim held by @p schemaObj .
    /// Should be preferred over UsdSkelSkeleton(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdSkelSkeleton(const UsdSchemaBase& schemaObj) : UsdGeomBoundable(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdSkelSkeleton()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdSkelSkeleton Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // JOINTS
    // --------------------------------------------------------------------- //
    /// An array of path tokens identifying the set of joints that make
    /// up the skeleton, and their order. Each token in the array must be valid
    /// when parsed as an SdfPath. The parent-child relationships of the
    /// corresponding paths determine the parent-child relationships of each
    /// joint. It is not required that the name at the end of each path be
    /// unique, but rather only that the paths themselves be unique.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] joints` |
    /// | C++ Type | VtArray<TfToken> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TokenArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetJointsAttr() const;

    /// See GetJointsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateJointsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // JOINTNAMES
    // --------------------------------------------------------------------- //
    /// If authored, provides a unique name per joint. This may be
    /// optionally set to provide better names when translating to DCC apps
    /// that require unique joint names.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] jointNames` |
    /// | C++ Type | VtArray<TfToken> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TokenArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetJointNamesAttr() const;

    /// See GetJointNamesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateJointNamesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BINDTRANSFORMS
    // --------------------------------------------------------------------- //
    /// Specifies the bind-pose transforms of each joint in
    /// **world space**, in the ordering imposed by *joints*.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform matrix4d[] bindTransforms` |
    /// | C++ Type | VtArray<GfMatrix4d> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Matrix4dArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetBindTransformsAttr() const;

    /// See GetBindTransformsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBindTransformsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RESTTRANSFORMS
    // --------------------------------------------------------------------- //
    /// Specifies the rest-pose transforms of each joint in
    /// **local space**, in the ordering imposed by *joints*. This provides
    /// fallback values for joint transforms when a Skeleton either has no
    /// bound animation source, or when that animation source only contains
    /// animation for a subset of a Skeleton's joints.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform matrix4d[] restTransforms` |
    /// | C++ Type | VtArray<GfMatrix4d> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Matrix4dArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetRestTransformsAttr() const;

    /// See GetRestTransformsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRestTransformsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdSkelSkeleton::_GetStaticTfType()
{
    const static TfToken token("UsdSkelSkeleton");
    return token;
}

/* virtual */
inline const TfToken UsdSkelSkeleton::_GetTfTypeToken() const
{
    const static TfToken token("UsdSkelSkeleton");
    return token;
}

/* static */
inline UsdSkelSkeleton UsdSkelSkeleton::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdSkelSkeleton();
    }
    return UsdSkelSkeleton(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdSkelSkeleton::GetJointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->joints));
}

inline UsdAttribute UsdSkelSkeleton::CreateJointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->joints), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelSkeleton::GetJointNamesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->jointNames));
}

inline UsdAttribute UsdSkelSkeleton::CreateJointNamesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->jointNames), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelSkeleton::GetBindTransformsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->bindTransforms));
}

inline UsdAttribute UsdSkelSkeleton::CreateBindTransformsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->bindTransforms), SdfValueTypeNames->Matrix4dArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelSkeleton::GetRestTransformsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->restTransforms));
}

inline UsdAttribute UsdSkelSkeleton::CreateRestTransformsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->restTransforms), SdfValueTypeNames->Matrix4dArray,
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
