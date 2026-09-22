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

/// @file usdGeom/visibilityAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
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
// VISIBILITYAPI                                                               //
// -------------------------------------------------------------------------- //

/// @class UsdGeomVisibilityAPI
///
/// /// UsdGeomVisibilityAPI introduces properties that can be used to author
/// visibility opinions.
///
/// \note
/// Currently, this schema only introduces the attributes that are used to
/// control purpose visibility. Later, this schema will define _all_
/// visibility-related properties and UsdGeomImageable will no longer define
/// those properties.
///
/// The purpose visibility attributes added by this schema,
/// _guideVisibility_, _proxyVisibility_, and _renderVisibility_ can each be
/// used to control visibility for geometry of the corresponding purpose
/// values, with the overall _visibility_ attribute acting as an
/// override. I.e., if _visibility_ evaluates to "invisible", purpose
/// visibility is invisible; otherwise, purpose visibility is determined by
/// the corresponding purpose visibility attribute.
///
/// Note that the behavior of _guideVisibility_ is subtly different from the
/// _proxyVisibility_ and _renderVisibility_ attributes, in that "guide"
/// purpose visibility always evaluates to either "invisible" or "visible",
/// whereas the other attributes may yield computed values of "inherited" if
/// there is no authored opinion on the attribute or inherited from an
/// ancestor. This is motivated by the fact that, in Pixar"s user workflows,
/// we have never found a need to have all guides visible in a scene by
/// default, whereas we do find that flexibility useful for "proxy" and
/// "render" geometry.
///
/// This schema can only be applied to UsdGeomImageable prims. The
/// UseGeomImageable schema provides API for computing the purpose visibility
/// values that result from the attributes introduced by this schema.
///
/// For any described attribute @em Fallback @em Value or @em Allowed @em Values below
/// that are text/tokens, the actual token is published and defined in @ref UsdGeomTokens.
/// So to set an attribute to the value "rightHanded", use UsdGeomTokens->rightHanded
/// as the value.

class UsdGeomVisibilityAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdGeomVisibilityAPI on UsdPrim @p prim.
    /// Equivalent to UsdGeomVisibilityAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomVisibilityAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdGeomVisibilityAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomVisibilityAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomVisibilityAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomVisibilityAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "VisibilityAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdGeomVisibilityAPI object is returned upon success.
    /// An invalid (or empty) UsdGeomVisibilityAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdGeomVisibilityAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdGeomVisibilityAPI>())
        {
            return UsdGeomVisibilityAPI(prim);
        }
        return UsdGeomVisibilityAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

public:
    // --------------------------------------------------------------------- //
    // GUIDEVISIBILITY
    // --------------------------------------------------------------------- //
    /// /// This attribute controls visibility for geometry with purpose "guide".
    ///
    /// Unlike overall _visibility_, _guideVisibility_ is uniform, and
    /// therefore cannot be animated.
    ///
    /// Also unlike overall _visibility_, _guideVisibility_ is tri-state, in
    /// that a descendant with an opinion of "visible" overrides an ancestor
    /// opinion of "invisible".
    ///
    /// The _guideVisibility_ attribute works in concert with the overall
    /// _visibility_ attribute: The visibility of a prim with purpose "guide"
    /// is determined by the inherited values it receives for the _visibility_
    /// and _guideVisibility_ attributes. If _visibility_ evaluates to
    /// "invisible", the prim is invisible. If _visibility_ evaluates to
    /// "inherited" and _guideVisibility_ evaluates to "visible", then the
    /// prim is visible. __Otherwise, it is invisible.__
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token guideVisibility = "invisible"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | inherited, invisible, visible |

    UsdAttribute GetGuideVisibilityAttr() const;

    /// See GetGuideVisibilityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateGuideVisibilityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // PROXYVISIBILITY
    // --------------------------------------------------------------------- //
    /// /// This attribute controls visibility for geometry with purpose "proxy".
    ///
    /// Unlike overall _visibility_, _proxyVisibility_ is uniform, and
    /// therefore cannot be animated.
    ///
    /// Also unlike overall _visibility_, _proxyVisibility_ is tri-state, in
    /// that a descendant with an opinion of "visible" overrides an ancestor
    /// opinion of "invisible".
    ///
    /// The _proxyVisibility_ attribute works in concert with the overall
    /// _visibility_ attribute: The visibility of a prim with purpose "proxy"
    /// is determined by the inherited values it receives for the _visibility_
    /// and _proxyVisibility_ attributes. If _visibility_ evaluates to
    /// "invisible", the prim is invisible. If _visibility_ evaluates to
    /// "inherited" then: If _proxyVisibility_ evaluates to "visible", then
    /// the prim is visible; if _proxyVisibility_ evaluates to "invisible",
    /// then the prim is invisible; if _proxyVisibility_ evaluates to
    /// "inherited", then the prim may either be visible or invisible,
    /// depending on a fallback value determined by the calling context.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token proxyVisibility = "inherited"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | inherited, invisible, visible |

    UsdAttribute GetProxyVisibilityAttr() const;

    /// See GetProxyVisibilityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateProxyVisibilityAttr() const;

public:
    // --------------------------------------------------------------------- //
    // RENDERVISIBILITY
    // --------------------------------------------------------------------- //
    /// /// This attribute controls visibility for geometry with purpose
    /// "render".
    ///
    /// Unlike overall _visibility_, _renderVisibility_ is uniform, and
    /// therefore cannot be animated.
    ///
    /// Also unlike overall _visibility_, _renderVisibility_ is tri-state, in
    /// that a descendant with an opinion of "visible" overrides an ancestor
    /// opinion of "invisible".
    ///
    /// The _renderVisibility_ attribute works in concert with the overall
    /// _visibility_ attribute: The visibility of a prim with purpose "render"
    /// is determined by the inherited values it receives for the _visibility_
    /// and _renderVisibility_ attributes. If _visibility_ evaluates to
    /// "invisible", the prim is invisible. If _visibility_ evaluates to
    /// "inherited" then: If _renderVisibility_ evaluates to "visible", then
    /// the prim is visible; if _renderVisibility_ evaluates to "invisible",
    /// then the prim is invisible; if _renderVisibility_ evaluates to
    /// "inherited", then the prim may either be visible or invisible,
    /// depending on a fallback value determined by the calling context.
    ///
    ///
    /// | ||
    /// | -- | -- |
    /// | Declaration | `uniform token renderVisibility = "inherited"` |
    /// | C++ Type | TfToken |
    /// | \ref Usd_Datatypes "Usd Type" | SdfValueTypeNames->Token |
    /// | \ref SdfVariability "Variability" | SdfVariabilityUniform |
    /// | \ref UsdGeomTokens "Allowed Values" | inherited, invisible, visible |

    UsdAttribute GetRenderVisibilityAttr() const;

    /// See GetRenderVisibilityAttr(), and also
    /// \ref Usd_Create_Or_Get_Property for when to use Get vs Create.
    /// If specified, author @p defaultValue as the attribute's default,
    /// sparsely (when it makes sense to do so) if @p writeSparsely is \c true -
    /// the default for @p writeSparsely is \c false.
    UsdAttribute CreateRenderVisibilityAttr() const;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomVisibilityAPI::_GetStaticTfType()
{
    const static TfToken token("UsdGeomVisibilityAPI");
    return token;
}

/* virtual */
inline const TfToken UsdGeomVisibilityAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomVisibilityAPI");
    return token;
}


inline UsdAttribute UsdGeomVisibilityAPI::GetGuideVisibilityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->guideVisibility));
}

inline UsdAttribute UsdGeomVisibilityAPI::CreateGuideVisibilityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->guideVisibility), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomVisibilityAPI::GetProxyVisibilityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->proxyVisibility));
}

inline UsdAttribute UsdGeomVisibilityAPI::CreateProxyVisibilityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->proxyVisibility), SdfValueTypeNames->Token,
                                     /* custom = */ false);
}

inline UsdAttribute UsdGeomVisibilityAPI::GetRenderVisibilityAttr() const
{

    return GetPrim().GetAttribute(TfToken(UsdGeomTokens->renderVisibility));
}

inline UsdAttribute UsdGeomVisibilityAPI::CreateRenderVisibilityAttr() const
{
    return GetPrim().CreateAttribute(TfToken(UsdGeomTokens->renderVisibility), SdfValueTypeNames->Token,
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
