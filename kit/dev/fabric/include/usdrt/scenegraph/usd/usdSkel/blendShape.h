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

/// @file usdSkel/blendShape.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
#include "usdrt/scenegraph/usd/usdSkel/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/pxr/base/tf/span.h"
#include "usdrt/scenegraph/usd/usdSkel/inbetweenShape.h" */
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
// BLENDSHAPE                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdSkelBlendShape
///
/// Describes a target blend shape, possibly containing inbetween
/// shapes.
///
/// See the extended \ref UsdSkel_BlendShape "Blend Shape Schema
/// documentation for information.
///

class UsdSkelBlendShape : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdSkelBlendShape on UsdPrim @p prim.
    /// Equivalent to UsdSkelBlendShape::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdSkelBlendShape(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdSkelBlendShape on the prim held by @p schemaObj .
    /// Should be preferred over UsdSkelBlendShape(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdSkelBlendShape(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdSkelBlendShape()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdSkelBlendShape Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // OFFSETS
    // --------------------------------------------------------------------- //
    /// **Required property**. Position offsets which, when added to the
    /// base pose, provides the target shape.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform vector3f[] offsets` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3fArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetOffsetsAttr() const;

    /// See GetOffsetsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateOffsetsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // NORMALOFFSETS
    // --------------------------------------------------------------------- //
    /// **Required property**. Normal offsets which, when added to the
    /// base pose, provides the normals of the target shape.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform vector3f[] normalOffsets` |
    /// | C++ Type | VtArray<GfVec3f> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Vector3fArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetNormalOffsetsAttr() const;

    /// See GetNormalOffsetsAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateNormalOffsetsAttr() const;

public:
    // --------------------------------------------------------------------- //
    // POINTINDICES
    // --------------------------------------------------------------------- //
    /// **Optional property**. Indices into the original mesh that
    /// correspond to the values in *offsets* and of any inbetween shapes. If
    /// authored, the number of elements must be equal to the number of elements
    /// in the *offsets* array.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform int[] pointIndices` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetPointIndicesAttr() const;

    /// See GetPointIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePointIndicesAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdSkelBlendShape::_GetStaticTfType()
{
    const static TfToken token("UsdSkelBlendShape");
    return token;
}

/* virtual */
inline const TfToken UsdSkelBlendShape::_GetTfTypeToken() const
{
    const static TfToken token("UsdSkelBlendShape");
    return token;
}

/* static */
inline UsdSkelBlendShape UsdSkelBlendShape::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdSkelBlendShape();
    }
    return UsdSkelBlendShape(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdSkelBlendShape::GetOffsetsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->offsets));
}

inline UsdAttribute UsdSkelBlendShape::CreateOffsetsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->offsets), SdfValueTypeNames->Vector3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBlendShape::GetNormalOffsetsAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->normalOffsets));
}

inline UsdAttribute UsdSkelBlendShape::CreateNormalOffsetsAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->normalOffsets), SdfValueTypeNames->Vector3fArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdSkelBlendShape::GetPointIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdSkelTokens->pointIndices));
}

inline UsdAttribute UsdSkelBlendShape::CreatePointIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdSkelTokens->pointIndices), SdfValueTypeNames->IntArray,
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
