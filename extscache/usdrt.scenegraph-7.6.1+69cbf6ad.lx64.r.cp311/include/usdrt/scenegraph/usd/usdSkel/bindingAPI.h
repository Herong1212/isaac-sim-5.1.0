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

/// @file usdSkel/bindingAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdSkel/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/pxr/base/tf/span.h"
#include "usdrt/scenegraph/usd/usdGeom/primvar.h"
#include "usdrt/scenegraph/usd/usdSkel/skeleton.h" */
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
// SKELBINDINGAPI                                                              //
// -------------------------------------------------------------------------- //

/// @class UsdSkelBindingAPI
///
/// Provides API for authoring and extracting all the skinning-related
/// data that lives in the "geometry hierarchy" of prims and models that want
/// to be skeletally deformed.
///
/// See the extended \ref UsdSkel_BindingAPI "UsdSkelBindingAPI schema"
/// documentation for more about bindings and how they apply in a scene graph.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdSkelTokens.
/// So to set an attribute to the value "rightHanded", use UsdSkelTokens->rightHanded
/// as the value.

class UsdSkelBindingAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdSkelBindingAPI on UsdPrim @p prim.
    /// Equivalent to UsdSkelBindingAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdSkelBindingAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdSkelBindingAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdSkelBindingAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdSkelBindingAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdSkelBindingAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "SkelBindingAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdSkelBindingAPI object is returned upon success.
    /// An invalid (or empty) UsdSkelBindingAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdSkelBindingAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdSkelBindingAPI>())
        {
            return UsdSkelBindingAPI(prim);
        }
        return UsdSkelBindingAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // GEOMBINDTRANSFORM
    // --------------------------------------------------------------------- //
    /// Encodes the bind-time world space transforms of the prim.
    /// If the transform is identical for a group of gprims that share a common
    /// ancestor, the transform may be authored on the ancestor, to "inherit"
    /// down to all the leaf gprims. If this transform is unset, an identity
    /// transform is used instead.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `matrix4d primvars:skel:geomBindTransform` |
    /// | C++ Type | GfMatrix4d |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Matrix4d |

    UsdAttribute GetGeomBindTransformAttr() const;

    /// See GetGeomBindTransformAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGeomBindTransformAttr() const;

public:
    // --------------------------------------------------------------------- //
    // JOINTS
    // --------------------------------------------------------------------- //
    /// An (optional) array of tokens defining the list of
    /// joints to which jointIndices apply. If not defined, jointIndices applies
    /// to the ordered list of joints defined in the bound Skeleton's *joints*
    /// attribute. If undefined on a primitive, the primitive inherits the
    /// value of the nearest ancestor prim, if any.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] skel:joints` |
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
    // JOINTINDICES
    // --------------------------------------------------------------------- //
    /// Indices into the *joints* attribute of the closest
    /// (in namespace) bound Skeleton that affect each point of a PointBased
    /// gprim. The primvar can have either *constant* or *vertex* interpolation.
    /// This primvar's *elementSize* will determine how many joint influences
    /// apply to each point. Indices must point be valid. Null influences should
    /// be defined by setting values in jointWeights to zero.
    /// See UsdGeomPrimvar for more information on interpolation and
    /// elementSize.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] primvars:skel:jointIndices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetJointIndicesAttr() const;

    /// See GetJointIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateJointIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // JOINTWEIGHTS
    // --------------------------------------------------------------------- //
    /// Weights for the joints that affect each point of a PointBased
    /// gprim. The primvar can have either *constant* or *vertex* interpolation.
    /// This primvar's *elementSize* will determine how many joints influences
    /// apply to each point. The length, interpolation, and elementSize of
    /// *jointWeights* must match that of *jointIndices*. See UsdGeomPrimvar
    /// for more information on interpolation and elementSize.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] primvars:skel:jointWeights` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetJointWeightsAttr() const;

    /// See GetJointWeightsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateJointWeightsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SKINNINGMETHOD
    // --------------------------------------------------------------------- //
    /// Different calculation method for skinning. LBS, DQ, and blendWeight
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token skel:skinningMethod = "ClassicLinear"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdSkelTokens "Allowed Values" | ClassicLinear, DualQuaternion, WeightedBlend |

    UsdAttribute GetSkinningMethodAttr() const;

    /// See GetSkinningMethodAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSkinningMethodAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SKINNINGBLENDWEIGHTS
    // --------------------------------------------------------------------- //
    /// Weights for weighted blend skinning method. The primvar can have either
    /// *constant* or *vertex* interpolation.
    /// Constant interpolation means every vertex share the same single blend weight.
    /// Vertex interpolation means every vertex has their own blend weight. The element
    /// size should match the vertices count in this case.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform float[] primvars:skel:skinningBlendWeights` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetSkinningBlendWeightsAttr() const;

    /// See GetSkinningBlendWeightsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateSkinningBlendWeightsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BLENDSHAPES
    // --------------------------------------------------------------------- //
    /// An array of tokens defining the order onto which blend shape
    /// weights from an animation source map onto the *skel:blendShapeTargets*
    /// rel of a binding site. If authored, the number of elements must be equal
    /// to the number of targets in the _blendShapeTargets_ rel. This property
    /// is not inherited hierarchically, and is expected to be authored directly
    /// on the skinnable primitive to which the blend shapes apply.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] skel:blendShapes` |
    /// | C++ Type | VtArray<TfToken> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->TokenArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetBlendShapesAttr() const;

    /// See GetBlendShapesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBlendShapesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ANIMATIONSOURCE
    // --------------------------------------------------------------------- //
    /// Animation source to be bound to Skeleton primitives at or
    /// beneath the location at which this property is defined.
    ///
    ///
    UsdRelationship GetAnimationSourceRel() const;

    /// See GetAnimationSourceRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateAnimationSourceRel() const;

public:
    // --------------------------------------------------------------------- //
    // SKELETON
    // --------------------------------------------------------------------- //
    /// Skeleton to be bound to this prim and its descendents that
    /// possess a mapping and weighting to the joints of the identified
    /// Skeleton.
    ///
    UsdRelationship GetSkeletonRel() const;

    /// See GetSkeletonRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateSkeletonRel() const;

public:
    // --------------------------------------------------------------------- //
    // BLENDSHAPETARGETS
    // --------------------------------------------------------------------- //
    /// Ordered list of all target blend shapes. This property is not
    /// inherited hierarchically, and is expected to be authored directly on
    /// the skinnable primitive to which the the blend shapes apply.
    ///
    UsdRelationship GetBlendShapeTargetsRel() const;

    /// See GetBlendShapeTargetsRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateBlendShapeTargetsRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdSkelBindingAPI::_GetStaticTfType()
{
    const static TfToken token("UsdSkelBindingAPI");
    return token;
}

/* virtual */
inline const TfToken UsdSkelBindingAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdSkelBindingAPI");
    return token;
}


inline UsdAttribute UsdSkelBindingAPI::GetGeomBindTransformAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->primvarsSkelGeomBindTransform));
}

inline UsdAttribute UsdSkelBindingAPI::CreateGeomBindTransformAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->primvarsSkelGeomBindTransform), SdfValueTypeNames->Matrix4d,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBindingAPI::GetJointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->skelJoints));
}

inline UsdAttribute UsdSkelBindingAPI::CreateJointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->skelJoints), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBindingAPI::GetJointIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->primvarsSkelJointIndices));
}

inline UsdAttribute UsdSkelBindingAPI::CreateJointIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->primvarsSkelJointIndices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBindingAPI::GetJointWeightsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->primvarsSkelJointWeights));
}

inline UsdAttribute UsdSkelBindingAPI::CreateJointWeightsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->primvarsSkelJointWeights), SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBindingAPI::GetSkinningMethodAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->skelSkinningMethod));
}

inline UsdAttribute UsdSkelBindingAPI::CreateSkinningMethodAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->skelSkinningMethod), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBindingAPI::GetSkinningBlendWeightsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->primvarsSkelSkinningBlendWeights));
}

inline UsdAttribute UsdSkelBindingAPI::CreateSkinningBlendWeightsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->primvarsSkelSkinningBlendWeights),
                                     SdfValueTypeNames->FloatArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBindingAPI::GetBlendShapesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->skelBlendShapes));
}

inline UsdAttribute UsdSkelBindingAPI::CreateBlendShapesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->skelBlendShapes), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}


inline UsdRelationship UsdSkelBindingAPI::GetAnimationSourceRel() const
{
    return GetPrim().GetRelationship(UsdSkelTokens->skelAnimationSource);
}

inline UsdRelationship UsdSkelBindingAPI::CreateAnimationSourceRel() const
{
    return GetPrim().CreateRelationship(UsdSkelTokens->skelAnimationSource,
                                        /* custom = */ false);
}
inline UsdRelationship UsdSkelBindingAPI::GetSkeletonRel() const
{
    return GetPrim().GetRelationship(UsdSkelTokens->skelSkeleton);
}

inline UsdRelationship UsdSkelBindingAPI::CreateSkeletonRel() const
{
    return GetPrim().CreateRelationship(UsdSkelTokens->skelSkeleton,
                                        /* custom = */ false);
}
inline UsdRelationship UsdSkelBindingAPI::GetBlendShapeTargetsRel() const
{
    return GetPrim().GetRelationship(UsdSkelTokens->skelBlendShapeTargets);
}

inline UsdRelationship UsdSkelBindingAPI::CreateBlendShapeTargetsRel() const
{
    return GetPrim().CreateRelationship(UsdSkelTokens->skelBlendShapeTargets,
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
