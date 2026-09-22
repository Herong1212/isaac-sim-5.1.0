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

/// @file usdShade/materialBindingAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"
#include "usdrt/scenegraph/usd/usdShade/tokens.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/collectionAPI.h"
#include "usdrt/scenegraph/usd/usdGeom/subset.h"
#include "usdrt/scenegraph/usd/usdShade/material.h"
#include <tbb/concurrent_unordered_map.h>*/
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
#include <usdrt/scenegraph/usd/usdShade/material.h>
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
// MATERIALBINDINGAPI                                                          //
// -------------------------------------------------------------------------- //

/// @class UsdShadeMaterialBindingAPI
///
/// UsdShadeMaterialBindingAPI is an API schema that provides an
/// interface for binding materials to prims or collections of prims
/// (represented by UsdCollectionAPI objects).
///
/// In the USD shading model, each renderable gprim computes a single
/// <b>resolved Material</b> that will be used to shade the gprim (exceptions,
/// of course, for gprims that possess UsdGeomSubsets, as each subset can be
/// shaded by a different Material).  A gprim <b>and each of its ancestor
/// prims</b> can possess, through the MaterialBindingAPI, both a
/// <b>direct</b> binding to a Material, and any number of
/// <b>collection-based</b> bindings to Materials; each binding can be generic
/// or declared for a particular <b>purpose</b>, and given a specific <b>binding
/// strength</b>. It is the process of "material resolution" (see
/// \ref UsdShadeMaterialBindingAPI_MaterialResolution) that examines all of
/// these bindings, and selects the one Material that best matches the
/// client's needs.
///
/// The intent of <b>purpose</b> is that each gprim should be able to resolve a
/// Material for any given purpose, which implies it can have differently bound
/// materials for different purposes. There are two <i>special</i> values of
/// <b>purpose</b> defined in UsdShade, although the API fully supports
/// specifying arbitrary values for it, for the sake of extensibility:
/// <ul><li><b>UsdShadeTokens->full</b>: to be used when the purpose of the
/// render is entirely to visualize the truest representation of a scene,
/// considering all lighting and material information, at highest fidelity.</li>
/// <li><b>UsdShadeTokens->preview</b>: to be used when the render is in
/// service of a goal other than a high fidelity "full" render (such as scene
/// manipulation, modeling, or realtime playback). Latency and speed are
/// generally of greater concern for preview renders, therefore preview
/// materials are generally designed to be "lighterweight" compared to full
/// materials.</li></ul>
/// A binding can also have no specific purpose at all, in which
/// case, it is considered to be the fallback or all-purpose binding (denoted
/// by the empty-valued token <b>UsdShadeTokens->allPurpose</b>).
///
/// The <b>purpose</b> of a material binding is encoded in the name of the
/// binding relationship.
/// <ul><li>
/// In the case of a direct binding, the <i>allPurpose</i> binding is
/// represented by the relationship named <b>"material:binding"</b>.
/// Special-purpose direct bindings are represented by relationships named
/// <b>"material:binding:<i>purpose</i></b>. A direct binding relationship
/// must have a single target path that points to a <b>UsdShadeMaterial</b>.</li>
/// <li>
/// In the case of a collection-based binding, the <i>allPurpose</i> binding is
/// represented by a relationship named
/// "material:binding:collection:<i>bindingName</i>", where
/// <b>bindingName</b> establishes an identity for the binding that is unique
/// on the prim. Attempting to establish two collection bindings of the same
/// name on the same prim will result in the first binding simply being
/// overridden. A special-purpose collection-based binding is represented by a
/// relationship named "material:binding:collection:<i>purpose:bindingName</i>".
/// A collection-based binding relationship must have exacly two targets, one of
/// which should be a collection-path (see
/// ef UsdCollectionAPI::GetCollectionPath()) and the other should point to a
/// <b>UsdShadeMaterial</b>. In the future, we may allow a single collection
/// binding to target multiple collections, if we can establish a reasonable
/// round-tripping pattern for applications that only allow a single collection
/// to be associated with each Material.
/// </li>
/// </ul>
///
/// <b>Note:</b> Both <b>bindingName</b> and <b>purpose</b> must be
/// non-namespaced tokens. This allows us to know the role of a binding
/// relationship simply from the number of tokens in it.
/// <ul><li><b>Two tokens</b>: the fallback, "all purpose", direct binding,
/// <i>material:binding</i></li>
/// <li><b>Three tokens</b>: a purpose-restricted, direct, fallback binding,
/// e.g. material:binding:preview</li>
/// <li><b>Four tokens</b>: an all-purpose, collection-based binding, e.g.
/// material:binding:collection:metalBits</li>
/// <li><b>Five tokens</b>: a purpose-restricted, collection-based binding,
/// e.g. material:binding:collection:full:metalBits</li>
/// </ul>
///
/// A <b>binding-strength</b> value is used to specify whether a binding
/// authored on a prim should be weaker or stronger than bindings that appear
/// lower in namespace. We encode the binding strength with as token-valued
/// metadata <b>'bindMaterialAs'</b> for future flexibility, even though for
/// now, there are only two possible values:
/// <i>UsdShadeTokens->weakerThanDescendants</i> and
/// <i>UsdShadeTokens->strongerThanDescendants</i>. When binding-strength is
/// not authored (i.e. empty) on a binding-relationship, the default behavior
/// matches UsdShadeTokens->weakerThanDescendants.
///
/// \note If a material binding relationship is a built-in property defined as
/// part of a typed prim's schema, a fallback value should not be provided for
/// it. This is because the "material resolution" algorithm only conisders
/// <i>authored</i> properties.
///

class UsdShadeMaterialBindingAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::SingleApplyAPI;


    /// Construct a UsdShadeMaterialBindingAPI on UsdPrim @p prim.
    /// Equivalent to UsdShadeMaterialBindingAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdShadeMaterialBindingAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdShadeMaterialBindingAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdShadeMaterialBindingAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdShadeMaterialBindingAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdShadeMaterialBindingAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();


    /// Applies this <b>single-apply</b> API schema to the given @p prim.
    /// This information is stored by adding "MaterialBindingAPI" to the
    /// token-valued, listOp metadata @em apiSchemas on the prim.
    ///
    /// @return A valid UsdShadeMaterialBindingAPI object is returned upon success.
    /// An invalid (or empty) UsdShadeMaterialBindingAPI object is returned upon
    /// failure. See @ref UsdPrim::ApplyAPI() for conditions
    /// resulting in failure.
    ///
    /// @sa UsdPrim::GetAppliedSchemas()
    /// @sa UsdPrim::HasAPI()
    /// @sa UsdPrim::ApplyAPI()
    /// @sa UsdPrim::RemoveAPI()
    static UsdShadeMaterialBindingAPI Apply(const UsdPrim& prim)
    {
        if (prim.ApplyAPI<UsdShadeMaterialBindingAPI>())
        {
            return UsdShadeMaterialBindingAPI(prim);
        }
        return UsdShadeMaterialBindingAPI();
    }

private:
    /* virtual */
    const TfToken _GetTfTypeToken() const override;

    // ===================================================================== //
    // Feel free to add custom code for the class definition between BEGIN
    // and END CUSTOM DECLARATION CODE below this line. It will be preserved by
    // the code generator.
    // ===================================================================== //
    // --(BEGIN CUSTOM DECLARATION CODE)--

public:
    /// Authors a direct binding to the given \p material on this prim.
    ///
    /// If \p bindingStrength is UsdShadeTokens->fallbackStrength, the value
    /// UsdShadeTokens->weakerThanDescendants is authored sparsely.
    /// To stamp out the bindingStrength value explicitly, clients can pass in
    /// UsdShadeTokens->weakerThanDescendants or
    /// UsdShadeTokens->strongerThanDescendants directly.
    ///
    /// If \p materialPurpose is specified and isn't equal to
    /// UsdShadeTokens->allPurpose, the binding only applies to the specified
    /// material purpose.
    ///
    /// Note that UsdShadeMaterialBindingAPI is a SingleAppliedAPI schema which
    /// when applied updates the prim definition accordingly. This information
    /// on the prim definition is helpful in multiple queries and more
    /// performant. Hence its recommended to call
    /// UsdShadeMaterialBindingAPI::Apply() when Binding a material.
    ///
    ///
    /// At the moment bindingStrength and materialPurpose is not supported.
    ///
    /// Returns true on success, false otherwise.
    bool Bind(const UsdShadeMaterial& material,
              const TfToken& bindingStrength = UsdShadeTokens->fallbackStrength,
              const TfToken& materialPurpose = UsdShadeTokens->allPurpose) const;

    /// Unbinds all direct and collection-based bindings on this prim.
    bool UnbindAllBindings() const;

    /// \overload
    /// Computes the resolved bound material for this prim, for the given
    /// material purpose.
    ///
    /// This overload does not utilize cached MembershipQuery object. However,
    /// it only computes the MembershipQuery of every collection that bound
    /// in the ancestor chain at most once.
    ///
    /// If \p bindingRel is not null, then it is set to the winning binding
    /// relationship.
    ///
    /// See \ref UsdShadeMaterialBindingAPI_MaterialResolution "Bound Material Resolution"
    /// for details on the material resolution process.
    ///
    /// The python version of this method returns a tuple containing the
    /// bound material and the "winning" binding relationship.
    UsdShadeMaterial ComputeBoundMaterial(const TfToken& materialPurpose = UsdShadeTokens->allPurpose,
                                          UsdRelationship* bindingRel = nullptr) const;
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdShadeMaterialBindingAPI::_GetStaticTfType()
{
    const static TfToken token("UsdShadeMaterialBindingAPI");
    return token;
}

/* virtual */
inline const TfToken UsdShadeMaterialBindingAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdShadeMaterialBindingAPI");
    return token;
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

namespace usdrt
{

inline bool UsdShadeMaterialBindingAPI::Bind(const UsdShadeMaterial& material,
                                             const TfToken& bindingStrength,
                                             const TfToken& materialPurpose) const
{
    if (auto relationship = GetPrim().CreateRelationship(UsdShadeTokens->materialBinding, /* custom = */ false))
    {
        return relationship.SetTargets({ material.GetPath() });
    }
    return false;
}

inline bool UsdShadeMaterialBindingAPI::UnbindAllBindings() const
{
    bool success = true;
    if (auto relationship = GetPrim().GetRelationship(UsdShadeTokens->materialBinding))
    {
        success = relationship.ClearTargets(/* removeSpec = */ false);
    }
    return success;
}

inline UsdShadeMaterial UsdShadeMaterialBindingAPI::ComputeBoundMaterial(const TfToken& materialPurpose,
                                                                         UsdRelationship* bindingRel) const
{
    if (auto relationship = GetPrim().GetRelationship(UsdShadeTokens->materialBinding))
    {
        if (bindingRel != nullptr)
        {
            *bindingRel = relationship;
        }
        SdfPathVector targets;
        if (relationship.GetTargets(&targets) && !targets.empty())
        {
            return UsdShadeMaterial(GetPrim().GetStage()->GetPrimAtPath(targets[0]));
        }
    }
    return UsdShadeMaterial();
}

} // namespace usdrt
