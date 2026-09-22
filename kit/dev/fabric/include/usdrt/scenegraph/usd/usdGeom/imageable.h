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

/// @file usdGeom/imageable.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/schemaBase.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/pxr/base/gf/bbox3d.h"
#include "usdrt/scenegraph/usd/usdGeom/primvar.h" */
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
// IMAGEABLE                                                                   //
// -------------------------------------------------------------------------- //

/// @class UsdGeomImageable
///
/// Base class for all prims that may require rendering or
/// visualization of some sort. The primary attributes of Imageable
/// are \em visibility and \em purpose, which each provide instructions for
/// what geometry should be included for processing by rendering and other
/// computations.
///
/// \deprecated Imageable also provides API for accessing primvars, which
/// has been moved to the UsdGeomPrimvarsAPI schema, because primvars can now
/// be applied on non-Imageable prim types.  This API is planned
/// to be removed, UsdGeomPrimvarsAPI should be used directly instead.
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomImageable : public UsdTyped
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::AbstractTyped;


    /// Construct a UsdGeomImageable on UsdPrim @p prim.
    /// Equivalent to UsdGeomImageable::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomImageable(const UsdPrim& prim = UsdPrim()) : UsdTyped(prim)
    {
    }

    /// Construct a UsdGeomImageable on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomImageable(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomImageable(const UsdSchemaBase& schemaObj) : UsdTyped(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomImageable()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // VISIBILITY
    // --------------------------------------------------------------------- //
    /// Visibility is meant to be the simplest form of "pruning"
    /// visibility that is supported by most DCC apps.  Visibility is
    /// animatable, allowing a sub-tree of geometry to be present for some
    /// segment of a shot, and absent from others; unlike the action of
    /// deactivating geometry prims, invisible geometry is still
    /// available for inspection, for positioning, for defining volumes, etc.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `token visibility = "inherited"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref UsdGeomTokens "Allowed Values" | inherited, invisible |

    UsdAttribute GetVisibilityAttr() const;

    /// See GetVisibilityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateVisibilityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PURPOSE
    // --------------------------------------------------------------------- //
    /// Purpose is a classification of geometry into categories that
    /// can each be independently included or excluded from traversals of prims
    /// on a stage, such as rendering or bounding-box computation traversals.
    ///
    /// See \ref UsdGeom_ImageablePurpose for more detail about how
    /// \em purpose is computed and used.
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token purpose = "default"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | default, render, proxy, guide |

    UsdAttribute GetPurposeAttr() const;

    /// See GetPurposeAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreatePurposeAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PROXYPRIM
    // --------------------------------------------------------------------- //
    /// The \em proxyPrim relationship allows us to link a
    /// prim whose \em purpose is "render" to its (single target)
    /// purpose="proxy" prim.  This is entirely optional, but can be
    /// useful in several scenarios:
    ///
    /// \li In a pipeline that does pruning (for complexity management)
    /// by deactivating prims composed from asset references, when we
    /// deactivate a purpose="render" prim, we will be able to discover
    /// and additionally deactivate its associated purpose="proxy" prim,
    /// so that preview renders reflect the pruning accurately.
    ///
    /// \li DCC importers may be able to make more aggressive optimizations
    /// for interactive processing and display if they can discover the proxy
    /// for a given render prim.
    ///
    /// \li With a little more work, a Hydra-based application will be able
    /// to map a picked proxy prim back to its render geometry for selection.
    ///
    /// \note It is only valid to author the proxyPrim relationship on
    /// prims whose purpose is "render".
    ///
    UsdRelationship GetProxyPrimRel() const;

    /// See GetProxyPrimRel(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create
    ///
    UsdRelationship CreateProxyPrimRel() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomImageable::_GetStaticTfType()
{
    const static TfToken token("UsdGeomImageable");
    return token;
}

/* virtual */
inline const TfToken UsdGeomImageable::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomImageable");
    return token;
}


inline UsdAttribute UsdGeomImageable::GetVisibilityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->visibility));
}

inline UsdAttribute UsdGeomImageable::CreateVisibilityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->visibility), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomImageable::GetPurposeAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->purpose));
}

inline UsdAttribute UsdGeomImageable::CreatePurposeAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->purpose), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}


inline UsdRelationship UsdGeomImageable::GetProxyPrimRel() const
{
    return GetPrim().GetRelationship(UsdGeomTokens->proxyPrim);
}

inline UsdRelationship UsdGeomImageable::CreateProxyPrimRel() const
{
    return GetPrim().CreateRelationship(UsdGeomTokens->proxyPrim,
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
