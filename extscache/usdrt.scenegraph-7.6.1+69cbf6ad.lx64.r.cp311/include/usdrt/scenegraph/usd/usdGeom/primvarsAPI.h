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

/// @file usdGeom/primvarsAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usdGeom/primvar.h" */
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--

#include "usdrt/scenegraph/usd/usdGeom/primvar.h"
#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

#include <vector>

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
// PRIMVARSAPI                                                                 //
// -------------------------------------------------------------------------- //

/// @class UsdGeomPrimvarsAPI
///
/// UsdGeomPrimvarsAPI encodes geometric "primitive variables",
/// as UsdGeomPrimvar, which interpolate across a primitive's topology,
/// can override shader inputs, and inherit down namespace.
///
/// \section usdGeom_PrimvarFetchingAPI Which Method to Use to Retrieve Primvars
///
/// While creating primvars is unambiguous (CreatePrimvar()), there are quite
/// a few methods available for retrieving primvars, making it potentially
/// confusing knowing which one to use.  Here are some guidelines:
///
/// \li If you are populating a GUI with the primvars already available for
/// authoring values on a prim, use GetPrimvars().
/// \li If you want all of the "useful" (e.g. to a renderer) primvars
/// available at a prim, including those inherited from ancestor prims, use
/// FindPrimvarsWithInheritance().  Note that doing so individually for many
/// prims will be inefficient.
/// \li To find a particular primvar defined directly on a prim, which may
/// or may not provide a value, use GetPrimvar().
/// \li To find a particular primvar defined on a prim or inherited from
/// ancestors, which may or may not provide a value, use
/// FindPrimvarWithInheritance().
/// \li To *efficiently* query for primvars using the overloads of
/// FindPrimvarWithInheritance() and FindPrimvarsWithInheritance(), one
/// must first cache the results of FindIncrementallyInheritablePrimvars() for
/// each non-leaf prim on the stage.

class UsdGeomPrimvarsAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::NonAppliedAPI;


    /// Construct a UsdGeomPrimvarsAPI on UsdPrim @p prim.
    /// Equivalent to UsdGeomPrimvarsAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdGeomPrimvarsAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdGeomPrimvarsAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdGeomPrimvarsAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdGeomPrimvarsAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdGeomPrimvarsAPI()
    {
    }

    /// @private
    static const TfToken _GetStaticTfType();

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

    /// Author scene description to create an attribute on this prim that
    /// will be recognized as Primvar (i.e. will present as a valid
    /// UsdGeomPrimvar).
    ///
    /// The name of the created attribute may or may not be the specified
    /// \p name, due to the possible need to apply property namespacing
    /// for primvars.  See \ref Usd_Creating_and_Accessing_Primvars
    /// for more information.  Creation may fail and return an invalid
    /// Primvar if \p name contains a reserved keyword, such as the 
    /// "indices" suffix we use for indexed primvars.
    ///
    /// The behavior with respect to the provided \p typeName
    /// is the same as for UsdAttributes::Create(), and
    /// \p interpolation is as described in UsdGeomPrimvar::GetInterpolation().
    ///
    /// If \p interpolation is left unspecified, we
    /// will author no opinions for them, which means any (strongest) opinion
    /// already authored in any contributing layer for these fields will
    /// become the Primvar's values, or the fallbacks if no opinions
    /// have been authored.
    ///
    /// \return an invalid UsdGeomPrimvar if we failed to create a valid
    /// attribute, a valid UsdGeomPrimvar otherwise.  It is not an
    /// error to create over an existing, compatible attribute.
    ///
    /// \sa UsdPrim::CreateAttribute(), UsdGeomPrimvar::IsPrimvar()
    UsdGeomPrimvar CreatePrimvar(const TfToken& name,
                                 const SdfValueTypeName &typeName,
                                 const TfToken& interpolation = TfToken()) const;

    /// Return the Primvar object named by \p name, which will
    /// be valid if a Primvar attribute definition already exists.
    ///
    /// Name lookup will account for Primvar namespacing, which means
    /// that this method will succeed in some cases where
    /// \code
    /// UsdGeomPrimvar(prim->GetAttribute(name))
    /// \endcode
    /// will not, unless \p name is properly namespace prefixed.
    ///
    /// \note Just because a Primvar is valid and defined, and *even if* its
    /// underlying UsdAttribute (GetAttr()) answers HasValue() affirmatively,
    /// one must still check the return value of Get(), due to the potential
    /// of time-varying value blocks (see \ref Usd_AttributeBlocking).
    ///
    /// \sa HasPrimvar(), \ref usdGeom_PrimvarFetchingAPI
    UsdGeomPrimvar GetPrimvar(const TfToken& name) const;

    /// Return valid UsdGeomPrimvar objects for all defined Primvars on
    /// this prim, similarly to UsdPrim::GetAttributes().
    ///
    /// The returned primvars may not possess any values, and therefore not
    /// be useful to some clients. For the primvars useful for inheritance
    /// computations, see GetPrimvarsWithAuthoredValues(), and for primvars
    /// useful for direct consumption, see GetPrimvarsWithValues().
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> GetPrimvars() const;

    /// Like GetPrimvars(), but include only primvars that have some
    /// authored scene description (though not necessarily a value).
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> GetAuthoredPrimvars() const;

    /// Like GetPrimvars(), but include only primvars that have some
    /// value, whether it comes from authored scene description or a schema
    /// fallback.
    ///
    /// For most purposes, this method is more useful than GetPrimvars().
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> GetPrimvarsWithValues() const;

    /// Like GetPrimvars(), but include only primvars that have an **authored**
    /// value.
    ///
    /// This is the query used when computing inheritable primvars, and is
    /// generally more useful than GetAuthoredPrimvars().
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> GetPrimvarsWithAuthoredValues() const;

    /// Compute the primvars that can be inherited from this prim by its
    /// child prims, including the primvars that **this** prim inherits from
    /// ancestor prims.  Inherited primvars will be bound to attributes on
    /// the corresponding ancestor prims.
    ///
    /// Only primvars with **authored**, **non-blocked**,
    /// **constant interpolation** values are inheritable;
    /// fallback values are not inherited.   The order of the returned
    /// primvars is undefined.
    ///
    /// It is not generally useful to call this method on UsdGeomGprim leaf
    /// prims, and furthermore likely to be expensive since *most* primvars
    /// are defined on Gprims.
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> FindInheritablePrimvars() const;

    /// Compute the primvars that can be inherited from this prim by its
    /// child prims, starting from the set of primvars inherited from
    /// this prim's ancestors.  If this method returns an empty vector, then
    /// this prim's children should inherit the same set of primvars available
    /// to this prim, i.e. the input `inheritedFromAncestors` .
    ///
    /// As opposed to FindInheritablePrimvars(), which always recurses up
    /// through all of the prim's ancestors, this method allows more
    /// efficient computation of inheritable primvars by starting with the
    /// list of primvars inherited from this prim's ancestors, and returning
    /// a newly allocated vector only when this prim makes a change to the
    /// set of inherited primvars.  This enables O(n) inherited primvar
    /// computation for all prims on a Stage, with potential to share
    /// computed results that are identical (i.e. when this method returns an
    /// empty vector, its parent's result can (and must!) be reused for all
    /// of the prim's children.
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> FindIncrementallyInheritablePrimvars(
        const std::vector<UsdGeomPrimvar>& inheritedFromAncestors) const;

    /// Like GetPrimvar(), but if the named primvar does not exist or has no
    /// authored value on this prim, search for the named, value-producing
    /// primvar on ancestor prims.
    /// 
    /// The returned primvar will be bound to the attribute on the 
    /// corresponding ancestor prim on which it was found (if any).  If neither
    /// this prim nor any ancestor contains a value-producing primvar, then
    /// the returned primvar will be the same as that returned by GetPrimvar().
    ///
    /// This is probably the method you want to call when needing to consume
    /// a primvar of a particular name.
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    UsdGeomPrimvar FindPrimvarWithInheritance(const TfToken& name) const;

    /// \overload
    /// 
    /// This version of FindPrimvarWithInheritance() takes the pre-computed
    /// set of primvars inherited from this prim's ancestors, as computed
    /// by FindInheritablePrimvars() or FindIncrementallyInheritablePrimvars()
    /// on the prim's parent.
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    UsdGeomPrimvar FindPrimvarWithInheritance(const TfToken& name,
        const std::vector<UsdGeomPrimvar> &inheritedFromAncestors) const;

    /// Find all of the value-producing primvars either defined on this prim,
    /// or inherited from ancestor prims.
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> FindPrimvarsWithInheritance() const;

    /// \overload
    /// 
    /// This version of FindPrimvarsWithInheritance() takes the pre-computed
    /// set of primvars inherited from this prim's ancestors, as computed
    /// by FindInheritablePrimvars() or FindIncrementallyInheritablePrimvars()
    /// on the prim's parent.
    ///
    /// \sa \ref usdGeom_PrimvarFetchingAPI
    std::vector<UsdGeomPrimvar> FindPrimvarsWithInheritance(
        const std::vector<UsdGeomPrimvar>& inheritedFromAncestors) const;

    /// Find all primvars inherited from ancestor prims.
    ///
    std::vector<UsdGeomPrimvar> FindInheritedPrimvars() const;

    /// Find primvar with given name inherited from ancestor prims.
    ///
    UsdGeomPrimvar FindInheritedPrimvar(const TfToken& name) const;

    /// Is there a Primvar named \p name with an authored value on this
    /// prim or any of its ancestors?
    ///
    /// This is probably the method you want to call when wanting to know
    /// whether or not the prim "has" a primvar of a particular name.
    ///
    /// \sa FindPrimvarWithInheritance()
    bool HasPossiblyInheritedPrimvar(const TfToken& name) const;

    /// Test whether a given \p name contains the "primvars:" prefix
    ///
    static bool CanContainPropertyName(const TfToken& name);

    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdGeomPrimvarsAPI::_GetStaticTfType()
{
    const static TfToken token("UsdGeomPrimvarsAPI");
    return token;
}

/* virtual */
inline const TfToken UsdGeomPrimvarsAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdGeomPrimvarsAPI");
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

/// Make list of primvars by filtering given list of attributes.
inline std::vector<UsdGeomPrimvar> _MakePrimvars(const std::vector<UsdAttribute>& attributes, bool (*filterPass)(const UsdGeomPrimvar&))
{
    std::vector<UsdGeomPrimvar> primvars;
    primvars.reserve(attributes.size());
    for (const UsdAttribute& attr : attributes) {
        // All prefixed properties except the ones that contain extra
        // namespaces (eg. the ":indices" attributes belonging to indexed
        // primvars) will be valid primvars.
        UsdGeomPrimvar primvar = UsdGeomPrimvar(attr);
        if (primvar && filterPass(primvar)){
            primvars.push_back(std::move(primvar));
        }
    }
    return primvars;
}

/// Check and add the primvars of the prim to the list of inherited primvars.
inline void _AddPrimToInheritedPrimvars(const UsdPrim& prim,
                                        const std::vector<UsdGeomPrimvar>* inputPrimvars,
                                        std::vector<UsdGeomPrimvar>* outputPrimvars,
                                        bool acceptAll = false) 
{
    auto copyPrimvars = [&inputPrimvars, &outputPrimvars]()
    {
        if (inputPrimvars != outputPrimvars) {
            *outputPrimvars = *inputPrimvars;
            inputPrimvars = outputPrimvars;
        }
    };

    const auto& attributes = prim.GetAuthoredAttributes();
    for(auto attr: attributes) {
        if (UsdGeomPrimvar pv = UsdGeomPrimvar(attr)) {
            if (!pv.HasAuthoredValue()) {
                continue;
            }

            // If pv is constant it will replace an instance already on the list;
            // if non-constant we'll just remove it.
            const TfToken& name = pv.GetName();
            const bool pvIsConstant = (pv.GetInterpolation() == UsdGeomTokens->constant);
            bool foundMatch = false;
            for (size_t j = 0; j < inputPrimvars->size(); ++j) {
                if (name == (*inputPrimvars)[j].GetName()) {
                    copyPrimvars();
                    foundMatch = true;
                    if (pvIsConstant || acceptAll) {
                        (*outputPrimvars)[j] = std::move(pv); 
                    }
                    else {
                        // Swap to the end and truncate the vector.
                        // Don't bother to preserve order.
                        std::swap((*outputPrimvars)[j], outputPrimvars->back());
                        outputPrimvars->pop_back();
                    }
                    break;
                }
            }
            if (!foundMatch && (pvIsConstant || acceptAll)) {
                copyPrimvars();
                outputPrimvars->push_back(std::move(pv));
            }
        }
    }
}

inline void _RecurseForInheritablePrimvars(const UsdPrim& prim,
                                           std::vector<UsdGeomPrimvar>* primvars,
                                           bool acceptAll = false) 
{
    if(!prim || prim.GetPath().IsAbsoluteRootPath()) {
        return;
    }

    // The `acceptAll` override is only useful for the prim we are actually
    // querying, i.e. the *first* prim on which this function is called
    _RecurseForInheritablePrimvars(prim.GetParent(false), primvars);
    _AddPrimToInheritedPrimvars(prim, primvars, primvars, acceptAll);
}

inline UsdGeomPrimvar UsdGeomPrimvarsAPI::CreatePrimvar(const TfToken& name,
                                                        const SdfValueTypeName& typeName,
                                                        const TfToken& interpolation) const 
{
    const UsdPrim& prim = GetPrim();

    UsdGeomPrimvar primvar(prim, name, typeName);

    if (primvar)
    {
        if (!interpolation.IsEmpty()) 
        {
            primvar.SetInterpolation(interpolation);
        }
    }
    return primvar;
}

inline UsdGeomPrimvar UsdGeomPrimvarsAPI::GetPrimvar(const TfToken& name) const 
{
    return UsdGeomPrimvar(GetPrim().GetAttribute(UsdGeomPrimvar::MakeNamespaced(name)));
}

std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::GetPrimvars() const 
{
    const UsdPrim& prim = GetPrim();
    if(!prim) {
        return {};
    }

    return _MakePrimvars(prim.GetAttributes(), [](UsdGeomPrimvar const &) { return true; });
}

std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::GetAuthoredPrimvars() const
{
    const UsdPrim& prim = GetPrim();
    if(!prim) {
        return {};
    }

    return _MakePrimvars(prim.GetAuthoredAttributes(), [](UsdGeomPrimvar const &) { return true; });
}
    
std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::GetPrimvarsWithValues() const 
{
    const UsdPrim& prim = GetPrim();
    if(!prim) {
        return {};
    }

    return _MakePrimvars(prim.GetAuthoredAttributes(), [](const UsdGeomPrimvar& pv) { return pv.HasValue(); });
}

std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::GetPrimvarsWithAuthoredValues() const
{
    const UsdPrim& prim = GetPrim();
    if(!prim) {
        return {};
    }

    return _MakePrimvars(prim.GetAuthoredAttributes(), [](const UsdGeomPrimvar& pv) { return pv.HasAuthoredValue(); });
}

inline std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::FindInheritablePrimvars() const 
{    
    UsdPrim prim = GetPrim();
    if(!prim) {
        return {};
    }

    std::vector<UsdGeomPrimvar> primvars;
    _RecurseForInheritablePrimvars(prim, &primvars);

    return primvars;
}

inline std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::FindIncrementallyInheritablePrimvars(
        const std::vector<UsdGeomPrimvar>& inheritedFromAncestors) const 
{
    UsdPrim prim = GetPrim();
    if(!prim) {
        return {};
    }

    std::vector<UsdGeomPrimvar> primvars;
    _AddPrimToInheritedPrimvars(prim, &inheritedFromAncestors, &primvars);
    return primvars;
}

inline UsdGeomPrimvar UsdGeomPrimvarsAPI::FindPrimvarWithInheritance(const TfToken& name) const 
{
    UsdPrim prim = GetPrim();
    if(!prim) {
        return {};
    }

    UsdGeomPrimvar localPv = GetPrimvar(name);
    if(localPv.HasAuthoredValue()){
        return localPv;
    }

    const TfToken attrName = UsdGeomPrimvar::MakeNamespaced(name);   
    for(prim = prim.GetParent(false); prim && !prim.GetPath().IsAbsoluteRootPath(); prim = prim.GetParent(false)) {
        UsdAttribute attr = prim.GetAttribute(attrName);
        if(attr.HasAuthoredValue()) {
            if(UsdGeomPrimvar pv = UsdGeomPrimvar(attr)) {
                // Only constant primvars can be inherited.
                if(pv.GetInterpolation() == UsdGeomTokens->constant) {
                    return pv;
                } else {
                    // Non-constant interpolation blocks inheritance.
                    return UsdGeomPrimvar();
                }
            }
        }
    }
    return localPv;
}

inline UsdGeomPrimvar UsdGeomPrimvarsAPI::FindPrimvarWithInheritance(const TfToken& name,
                                                                     const std::vector<UsdGeomPrimvar>& inheritedFromAncestors) const 
{
    const UsdPrim &prim = GetPrim();
    if(!prim) {
        return {};
    }

    const TfToken attrName = UsdGeomPrimvar::MakeNamespaced(name);
    UsdGeomPrimvar pv = GetPrimvar(attrName);
    if (pv.HasAuthoredValue()){
        return pv;
    }
    
    for (const UsdGeomPrimvar& inherited: inheritedFromAncestors) {
        if (inherited.GetName() == attrName){
            return inherited;
        }
    }

    return pv;
}

inline std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::FindPrimvarsWithInheritance() const 
{
    UsdPrim prim = GetPrim();
    if(!prim) {
        return {};
    }

    std::vector<UsdGeomPrimvar> primvars;
    _RecurseForInheritablePrimvars(prim, &primvars, true);

    return primvars;
}

inline std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::FindPrimvarsWithInheritance(const std::vector<UsdGeomPrimvar>& inheritedFromAncestors) const 
{
    UsdPrim prim = GetPrim();
    if(!prim) {
        return {};
    }

    std::vector<UsdGeomPrimvar> primvars;
    _AddPrimToInheritedPrimvars(prim, &inheritedFromAncestors, &primvars, true);

    // If this prim contributed no primvars, then `primvars` won't have
    // gotten a copy of `inheritedFromAncestors`, so ensure we compensate
    return primvars.empty() ? inheritedFromAncestors : primvars;
}

inline std::vector<UsdGeomPrimvar> UsdGeomPrimvarsAPI::FindInheritedPrimvars() const 
{
    UsdPrim prim = GetPrim();
    if(!prim) {
        return {};
    }

    std::vector<UsdGeomPrimvar> inheritedPrimvars;
    _RecurseForInheritablePrimvars(prim.GetParent(false), &inheritedPrimvars);

    const auto primvars = GetAuthoredPrimvars();

    auto it = std::remove_if(inheritedPrimvars.begin(), inheritedPrimvars.end(), [&primvars] (const auto& inheritedPrimvar) {
        return std::find_if(primvars.begin(), primvars.end(), [&inheritedPrimvar] (const auto& primvar) {
            return inheritedPrimvar.GetName() == primvar.GetName();
        }) != primvars.end();
    });
    inheritedPrimvars.erase(it, inheritedPrimvars.end());

    return inheritedPrimvars;
}

inline UsdGeomPrimvar UsdGeomPrimvarsAPI::FindInheritedPrimvar(const TfToken& name) const 
{
    UsdPrim prim = GetPrim();
    if(!prim) {
        return {};
    }
    
    UsdGeomPrimvar localPv = GetPrimvar(name);
    if(localPv.HasAuthoredValue()) {
        return {};
    }

    auto parent = prim.GetParent(false);
    if(!parent || parent.GetPath().IsAbsoluteRootPath()) {
        return {};
    }

    UsdGeomPrimvarsAPI parentPrimvarsAPI {parent};
    return parentPrimvarsAPI.FindPrimvarWithInheritance(name);
}

inline bool UsdGeomPrimvarsAPI::HasPossiblyInheritedPrimvar(const TfToken& name) const 
{
    UsdPrim prim = GetPrim();
    if (!prim) {
        return false;
    }
    UsdGeomPrimvar pv = GetPrimvar(name);
    if (pv.HasAuthoredValue()) {
        return true;
    }

    const TfToken attrName = UsdGeomPrimvar::MakeNamespaced(name);
    if (attrName.IsEmpty()) {
        return false;
    }
    for (prim = prim.GetParent(false); prim && !prim.GetPath().IsAbsoluteRootPath(); prim = prim.GetParent(false)) {
        UsdAttribute attr = prim.GetAttribute(attrName);
        if (attr.HasAuthoredValue() && UsdGeomPrimvar::IsPrimvar(attr)) {
            // Only constant primvars can be inherited.
            // Non-constant interpolation blocks inheritance.
            return UsdGeomPrimvar(attr).GetInterpolation() == UsdGeomTokens->constant;
        }
    }
    return false;
}

inline bool UsdGeomPrimvarsAPI::CanContainPropertyName(const TfToken& name) 
{
    return TfStringStartsWith(name.GetString(), USDRT_POPULATION_PRIMVARS_PREFIX);
}

} // namespace usdrt