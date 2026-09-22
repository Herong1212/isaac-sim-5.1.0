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

/// @file usdSkel/animation.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
#include "usdrt/scenegraph/usd/usdSkel/tokens.h"


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
// SKELANIMATION                                                               //
// -------------------------------------------------------------------------- //

/// @class UsdSkelAnimation
///
/// Describes a skel animation, where joint animation is stored in a
/// vectorized form.
///
/// See the extended \ref UsdSkel_SkelAnimation "Skel Animation"
/// documentation for more information.
///

class UsdSkelAnimation : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdSkelAnimation on UsdPrim @p prim.
    /// Equivalent to UsdSkelAnimation::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdSkelAnimation(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdSkelAnimation on the prim held by @p schemaObj .
    /// Should be preferred over UsdSkelAnimation(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdSkelAnimation(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdSkelAnimation()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdSkelAnimation Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // JOINTS
    // --------------------------------------------------------------------- //
    /// Array of tokens identifying which joints this animation's
    /// data applies to. The tokens for joints correspond to the tokens of
    /// Skeleton primitives. The order of the joints as listed here may
    /// vary from the order of joints on the Skeleton itself.
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
    // TRANSLATIONS
    // --------------------------------------------------------------------- //
    /// Joint-local translations of all affected joints. Array length
    /// should match the size of the *joints* attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float3[] translations` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Float3Array |

    UsdAttribute GetTranslationsAttr() const;

    /// See GetTranslationsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateTranslationsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // ROTATIONS
    // --------------------------------------------------------------------- //
    /// Joint-local unit quaternion rotations of all affected joints,
    /// in 32-bit precision. Array length should match the size of the
    /// *joints* attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `quatf[] rotations` |
    /// | C++ Type | VtArray<GfQuatf> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->QuatfArray |

    UsdAttribute GetRotationsAttr() const;

    /// See GetRotationsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRotationsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // SCALES
    // --------------------------------------------------------------------- //
    /// Joint-local scales of all affected joints, in
    /// 16 bit precision. Array length should match the size of the *joints*
    /// attribute.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `half3[] scales` |
    /// | C++ Type | VtArray<GfVec3h> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Half3Array |

    UsdAttribute GetScalesAttr() const;

    /// See GetScalesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateScalesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // BLENDSHAPES
    // --------------------------------------------------------------------- //
    /// Array of tokens identifying which blend shapes this
    /// animation's data applies to. The tokens for blendShapes correspond to
    /// the tokens set in the *skel:blendShapes* binding property of the
    /// UsdSkelBindingAPI.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token[] blendShapes` |
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
    // BLENDSHAPEWEIGHTS
    // --------------------------------------------------------------------- //
    /// Array of weight values for each blend shape. Each weight value
    /// is associated with the corresponding blend shape identified within the
    /// *blendShapes* token array, and therefore must have the same length as
    /// *blendShapes.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `float[] blendShapeWeights` |
    /// | C++ Type | VtArray<float> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->FloatArray |

    UsdAttribute GetBlendShapeWeightsAttr() const;

    /// See GetBlendShapeWeightsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateBlendShapeWeightsAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdSkelAnimation::_GetStaticTfType()
{
    const static TfToken token("UsdSkelAnimation");
    return token;
}

/* virtual */
inline const TfToken UsdSkelAnimation::_GetTfTypeToken() const
{
    const static TfToken token("UsdSkelAnimation");
    return token;
}

/* static */
inline UsdSkelAnimation UsdSkelAnimation::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdSkelAnimation();
    }
    return UsdSkelAnimation(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdSkelAnimation::GetJointsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->joints));
}

inline UsdAttribute UsdSkelAnimation::CreateJointsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->joints), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelAnimation::GetTranslationsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->translations));
}

inline UsdAttribute UsdSkelAnimation::CreateTranslationsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->translations), SdfValueTypeNames->Float3Array,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelAnimation::GetRotationsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->rotations));
}

inline UsdAttribute UsdSkelAnimation::CreateRotationsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->rotations), SdfValueTypeNames->QuatfArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelAnimation::GetScalesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->scales));
}

inline UsdAttribute UsdSkelAnimation::CreateScalesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->scales), SdfValueTypeNames->Half3Array,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelAnimation::GetBlendShapesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->blendShapes));
}

inline UsdAttribute UsdSkelAnimation::CreateBlendShapesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->blendShapes), SdfValueTypeNames->TokenArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelAnimation::GetBlendShapeWeightsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->blendShapeWeights));
}

inline UsdAttribute UsdSkelAnimation::CreateBlendShapeWeightsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->blendShapeWeights), SdfValueTypeNames->FloatArray,
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
