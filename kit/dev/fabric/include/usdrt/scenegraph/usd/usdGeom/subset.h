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

/// @file usdGeom/subset.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/pxr/base/tf/token.h"
#include "usdrt/scenegraph/usd/usdGeom/imageable.h"*/
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
// GEOMSUBSET                                                                  //
// -------------------------------------------------------------------------- //

/// @class UsdGeomSubset
///
/// Encodes a subset of a piece of geometry (i.e. a UsdGeomImageable)
/// as a set of indices. Currently only supports encoding of face-subsets, but
/// could be extended in the future to support subsets representing edges,
/// segments, points etc.
///
/// To apply to a geometric prim, a GeomSubset prim must be the prim's direct
/// child in namespace, and possess a concrete defining specifier (i.e. def).
/// This restriction makes it easy and efficient to discover subsets of a prim.
/// We might want to relax this restriction if it's common to have multiple
/// <b>families</b> of subsets on a gprim and if it's useful to be able to
/// organize subsets belonging to a </b>family</b> under a common scope. See
/// 'familyName' attribute for more info on defining a family of subsets.
///
/// Note that a GeomSubset isn't an imageable (i.e. doesn't derive from
/// UsdGeomImageable). So, you can't author <b>visibility</b> for it or
/// override its <b>purpose</b>.
///
/// Materials are bound to GeomSubsets just as they are for regular
/// geometry using API available in UsdShade (UsdShadeMaterial::Bind).
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomSubset : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::ConcreteTyped;


    /// Construct a UsdGeomSubset on UsdPrim @p prim.
    /// Equivalent to UsdGeomSubset::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomSubset(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdGeomSubset on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomSubset(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomSubset(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomSubset()
    {
    }

    /// Attempt to ensure a @a UsdPrim adhering to this schema at @p path
    /// is defined (according to UsdPrim::IsDefined()) on this stage.
    static UsdGeomSubset Define(const UsdStageRefPtr& stage, const SdfPath& path);

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // ELEMENTTYPE
    // --------------------------------------------------------------------- //
    /// The type of element that the indices target. Currently only
    /// allows "face" and defaults to it.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token elementType = "face"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | face |

    UsdAttribute GetElementTypeAttr() const;

    /// See GetElementTypeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateElementTypeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // INDICES
    // --------------------------------------------------------------------- //
    /// The set of indices included in this subset. The indices need not
    /// be sorted, but the same index should not appear more than once.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `int[] indices = []` |
    /// | C++ Type | VtArray<int> |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->IntArray |

    UsdAttribute GetIndicesAttr() const;

    /// See GetIndicesAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateIndicesAttr() const;

public:
    // --------------------------------------------------------------------- //
    // FAMILYNAME
    // --------------------------------------------------------------------- //
    /// The name of the family of subsets that this subset belongs to.
    /// This is optional and is primarily useful when there are multiple
    /// families of subsets under a geometric prim. In some cases, this could
    /// also be used for achieving proper roundtripping of subset data between
    /// DCC apps.
    /// When multiple subsets belonging to a prim have the same familyName, they
    /// are said to belong to the family. A <i>familyType</i> value can be
    /// encoded on the owner of a family of subsets as a token using the static
    /// method UsdGeomSubset::SetFamilyType(). "familyType" can have one of the
    /// following values:
    /// <ul><li><b>UsdGeomTokens->partition</b>: implies that every element of
    /// the whole geometry appears exactly once in only one of the subsets
    /// belonging to the family.</li>
    /// <li><b>UsdGeomTokens->nonOverlapping</b>: an element that appears in one
    /// subset may not appear in any other subset belonging to the family.</li>
    /// <li><b>UsdGeomTokens->unrestricted</b>: implies that there are no
    /// restrictions w.r.t. the membership of elements in the subsets. They
    /// could be overlapping and the union of all subsets in the family may
    /// not represent the whole.</li>
    /// </ul>
    /// \note The validity of subset data is not enforced by the authoring
    /// APIs, however they can be checked using UsdGeomSubset::ValidateFamily().
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token familyName = ""` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |

    UsdAttribute GetFamilyNameAttr() const;

    /// See GetFamilyNameAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateFamilyNameAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomSubset::_GetStaticTfType()
{
    const static TfToken token("UsdGeomSubset");
    return token;
}

/* virtual */
inline const TfToken UsdGeomSubset::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomSubset");
    return token;
}

/* static */
inline UsdGeomSubset UsdGeomSubset::Define(const UsdStageRefPtr& stage, const SdfPath& path)
{
    if (!stage)
    {
        // TODO error
        return UsdGeomSubset();
    }
    return UsdGeomSubset(stage->DefinePrim(path, _GetStaticTfType()));
}


inline UsdAttribute UsdGeomSubset::GetElementTypeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->elementType));
}

inline UsdAttribute UsdGeomSubset::CreateElementTypeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->elementType), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomSubset::GetIndicesAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->indices));
}

inline UsdAttribute UsdGeomSubset::CreateIndicesAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->indices), SdfValueTypeNames->IntArray,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomSubset::GetFamilyNameAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->familyName));
}

inline UsdAttribute UsdGeomSubset::CreateFamilyNameAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->familyName), SdfValueTypeNames->Token,
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
