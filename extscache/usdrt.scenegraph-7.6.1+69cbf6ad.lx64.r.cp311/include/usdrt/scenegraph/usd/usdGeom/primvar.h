// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "usdrt/scenegraph/usd/usdGeom/tokens.h"

#include <usdrt/population/Tokens.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/base/tf/stringUtils.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>

namespace usdrt
{

class UsdGeomPrimvar 
{
public:

    // Default constructor returns an invalid Primvar.  Exists for 
    // container classes
    UsdGeomPrimvar();

    /// Speculative constructor that will produce a valid UsdGeomPrimvar when
    /// \p attr already represents an attribute that is Primvar, and
    /// produces an \em invalid Primvar otherwise (i.e. 
    /// \ref UsdGeomPrimvar_bool "operator bool()" will return false).
    ///
    /// Calling \c UsdGeomPrimvar::IsPrimvar(attr) will return the same truth
    /// value as this constructor, but if you plan to subsequently use the
    /// Primvar anyways, just use this constructor, as demonstrated in the 
    /// \ref UsdGeomPrimvar_Using_Primvar "class documentation".
    explicit UsdGeomPrimvar(const UsdAttribute &attr);

    /// Return the Primvar's interpolation, which is 
    /// \ref Usd_InterpolationVals "UsdGeomTokens->constant" if unauthored
    ///
    /// Interpolation determines how the Primvar interpolates over
    /// a geometric primitive.  See \ref Usd_InterpolationVals
    TfToken GetInterpolation() const;

    /// Set the Primvar's interpolation.
    ///
    /// Returns false if \p interpolation is out of range as
    /// defined by IsValidInterpolation().  No attempt is made to validate
    /// that the Primvar's value contains the right number of elements
    /// to match its interpolation to its topology.
    ///
    /// \sa GetInterpolation(), \ref Usd_InterpolationVals
    bool SetInterpolation(const TfToken& interpolation);

    /// Has interpolation been explicitly authored on this Primvar?
    ///
    /// \sa GetInterpolationSize()
    bool HasAuthoredInterpolation() const;

    /// Test whether a given UsdAttribute represents valid Primvar, which
    /// implies that creating a UsdGeomPrimvar from the attribute will succeed.
    ///
    /// Success implies that \c attr.IsDefined() is true.
    static bool IsPrimvar(const UsdAttribute& attr);

    /// Test whether a given \p name represents a valid name of a primvar, 
    /// which implies that creating a UsdGeomPrimvar with the given name will 
    /// succeed.
    /// 
    static bool IsValidPrimvarName(const TfToken& name);

    /// Returns the \p name, devoid of the "primvars:" token if present,
    /// otherwise returns the \p name unchanged
    static TfToken StripPrimvarsName(const TfToken& name);

    /// Returns the \p name, devoid of the ":interpolation" token if present,
    /// otherwise returns the \p name unchanged
    static TfToken StripInterpolationName(const TfToken& name);

    /// Validate that the provided \p interpolation is a valid setting for 
    /// interpolation as defined by \ref Usd_InterpolationVals.  
    static bool IsValidInterpolation(const TfToken& interpolation);

    /// Validate that the provided \p name is a valid primvar
    /// interpolation attribute name.  
    static bool IsValidInterpolationName(const TfToken& name);

    /// Get the interpolation attribute name for the provided primvar \p name.
    static TfToken GetInterpolationName(const TfToken& name);


    // ---------------------------------------------------------------
    /// \name UsdAttribute API
    // ---------------------------------------------------------------
    /// @{

    /// Allow UsdGeomPrimvar to auto-convert to UsdAttribute, so you can
    /// pass a UsdGeomPrimvar to any function that accepts a UsdAttribute or
    /// const-ref thereto.
    operator const UsdAttribute& () const;

    /// Explicit UsdAttribute extractor
    const UsdAttribute& GetAttr() const;
    
    /// Return true if the underlying UsdAttribute::IsDefined(), and in
    /// addition the attribute is identified as a Primvar.  Does not imply
    /// that the primvar provides a value
    bool IsDefined() const;

    /// Return true if the underlying attribute has a value, either from
    /// authored scene description or a fallback.
    bool HasValue() const;

    /// Return true if the underlying attribute has an unblocked, authored
    /// value.
    bool HasAuthoredValue() const;

    /// \anchor UsdGeomPrimvar_bool
    /// Return true if this Primvar is valid for querying and authoring
    /// values and metadata, which is identically equivalent to IsDefined().
    explicit operator bool() const;

    /// \sa UsdAttribute::GetName()
    const TfToken GetName() const;

    /// Get the attribute value of the Primvar at \p time .
    ///
    /// \sa Usd_Handling_Indexed_Primvars for proper handling of 
    /// \ref Usd_Handling_Indexed_Primvars "indexed primvars"
    template <typename T>
    bool Get(T* value, UsdTimeCode time = UsdTimeCode::Default()) const;

    /// Set the attribute value of the Primvar at \p time 
    template <typename T>
    bool Set(const T& value, UsdTimeCode time = UsdTimeCode::Default());

    /// Validate that the given \p name contains the primvars namespace.
    /// Does not validate name as a legal property identifier
    static bool IsNamespaced(const TfToken& name);

    /// Return \p name prepended with the proper primvars namespace, if
    /// it is not already prefixed.
    ///
    /// Does not validate name as a legal property identifier, but will
    /// verify that \p name contains no reserved keywords, and will return
    /// an empty TfToken if it does. 
    static TfToken MakeNamespaced(const TfToken& name);

private:
    friend class UsdGeomPrimvarsAPI;

    /// Factory for UsdGeomImageable's use, so that we can encapsulate the
    /// logic of what discriminates Primvar in this class, while
    /// preserving the pattern that attributes can only be created
    /// via their container objects.
    ///
    /// The name of the created attribute may or may not be the specified
    /// \p primvarName, due to the possible need to apply property namespacing
    /// for Primvar.
    ///
    /// The behavior with respect to the provided \p typeName
    /// is the same as for UsdAttributes::Create().
    ///
    /// \return an invalid UsdGeomPrimvar if we failed to create a valid
    /// attribute, a valid UsdGeomPrimvar otherwise.  It is not an
    /// error to create over an existing, compatible attribute.
    ///
    /// It is a failed verification for \p prim to be invalid/expired
    ///
    /// \sa UsdPrim::CreateAttribute()
    UsdGeomPrimvar(const UsdPrim& prim, const TfToken& primvarName, const SdfValueTypeName& typeName);

    UsdAttribute m_attr;
};


/// Equality comparison.  Return true if \a lhs and \a rhs represent the
/// same UsdGeomPrimvar, false otherwise.
inline bool operator==(const UsdGeomPrimvar &lhs, const UsdGeomPrimvar &rhs) {
    return lhs.GetAttr().GetPath() == rhs.GetAttr().GetPath();
}

/// Inequality comparison. Return false if \a lhs and \a rhs represent the
/// same UsdPrimvar, true otherwise.
inline bool operator!=(const UsdGeomPrimvar &lhs, const UsdGeomPrimvar &rhs) {
    return !(lhs == rhs);
}

inline UsdGeomPrimvar::UsdGeomPrimvar() 
{
}

inline UsdGeomPrimvar::UsdGeomPrimvar(const UsdAttribute& attr) 
: m_attr(attr) 
{
}

inline TfToken UsdGeomPrimvar::GetInterpolation() const 
{
    const TfToken interpolationToken(m_attr.GetName().GetString() + USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX);
    if(auto interpolationAttr = m_attr.GetPrim().GetAttribute(interpolationToken)) {
        TfToken value;
        if(interpolationAttr.Get(&value)) {
            return value;
        }
    }
    return UsdGeomTokens->constant;
}

inline bool UsdGeomPrimvar::SetInterpolation(const TfToken& interpolation) 
{
    if (!IsValidInterpolation(interpolation)){
        return false;
    }

    const TfToken interpolationToken(m_attr.GetName().GetString() + USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX);
    if(auto attr = m_attr.GetPrim().CreateAttribute(interpolationToken, SdfValueTypeNames->Token)) {
        if(attr.Set(interpolation)) {
            return true;
        }
    }
    return false;
}

inline bool UsdGeomPrimvar::HasAuthoredInterpolation() const 
{
    const TfToken interpolationToken(m_attr.GetName().GetString() + USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX);
    if(auto interpolationAttr = m_attr.GetPrim().GetAttribute(interpolationToken)) {
        return interpolationAttr.HasAuthoredValue();
    }
    return false;
}

inline bool UsdGeomPrimvar::IsPrimvar(const UsdAttribute& attr) 
{
    if (!attr) {
        return false;
    }
    
    return IsValidPrimvarName(attr.GetName());
}

inline bool UsdGeomPrimvar::IsValidPrimvarName(const TfToken& name) 
{
    return (TfStringStartsWith(name.GetString(), USDRT_POPULATION_PRIMVARS_PREFIX) &&
            !TfStringEndsWith(name.GetString(), USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX) &&
            !TfStringEndsWith(name.GetString(), USDRT_POPULATION_PRIMVARS_INDICES_SUFFIX));
}

inline TfToken UsdGeomPrimvar::StripPrimvarsName(const TfToken& name) 
{
    const std::string& fullName = name.GetString();

    const std::pair<std::string, bool> res = 
        SdfPath::StripPrefixNamespace(fullName, USDRT_POPULATION_PRIMVARS_PREFIX);

    return res.second ? TfToken(res.first) : name;
}

inline TfToken UsdGeomPrimvar::StripInterpolationName(const TfToken& name)
{
    const std::string& fullName = name.GetString();

    const std::pair<std::string, bool> res = 
        SdfPath::StripSuffixNamespace(fullName, USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX);

    return res.second ? TfToken(res.first) : name;
}

inline bool UsdGeomPrimvar::IsValidInterpolation(const TfToken& interpolation) 
{
    return ((interpolation == UsdGeomTokens->constant) ||
            (interpolation == UsdGeomTokens->uniform)  ||
            (interpolation == UsdGeomTokens->vertex)   ||
            (interpolation == UsdGeomTokens->varying)  ||
            (interpolation == UsdGeomTokens->faceVarying));
}

inline bool UsdGeomPrimvar::IsValidInterpolationName(const TfToken& name)
{
    return TfStringStartsWith(name.GetString(), USDRT_POPULATION_PRIMVARS_PREFIX) &&
            TfStringEndsWith(name.GetString(), USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX);
}

inline TfToken UsdGeomPrimvar::GetInterpolationName(const TfToken& name)
{
    return TfToken{name.GetString() + USDRT_POPULATION_PRIMVARS_INTERPOLATION_SUFFIX};
}

inline UsdGeomPrimvar::operator const UsdAttribute& () const 
{ 
    return m_attr; 
}

inline const UsdAttribute& UsdGeomPrimvar::GetAttr() const 
{
    return m_attr; 
}

inline bool UsdGeomPrimvar::IsDefined() const 
{
    return IsPrimvar(m_attr); 
}

inline bool UsdGeomPrimvar::HasValue() const 
{
    return m_attr.HasValue(); 
}

inline bool UsdGeomPrimvar::HasAuthoredValue() const 
{
    return m_attr.HasAuthoredValue();
}

inline UsdGeomPrimvar::operator bool() const 
{
    return IsDefined(); 
}

inline const TfToken UsdGeomPrimvar::GetName() const 
{ 
    return m_attr.GetName(); 
}

template <typename T>
inline bool UsdGeomPrimvar::Get(T* value, UsdTimeCode time) const 
{
    return m_attr.Get(value, time);
}

template <typename T>
inline bool UsdGeomPrimvar::Set(const T& value, UsdTimeCode time) 
{
    return m_attr.Set(value, time);
}

inline bool UsdGeomPrimvar::IsNamespaced(const TfToken& name) 
{
    return TfStringStartsWith(name.GetText(), USDRT_POPULATION_PRIMVARS_PREFIX);
}

inline TfToken UsdGeomPrimvar::MakeNamespaced(const TfToken& name) 
{
    TfToken  result;
    if (IsNamespaced(name))
    {
        result = name;
    }
    else {
        result = TfToken(USDRT_POPULATION_PRIMVARS_PREFIX + name.GetString());
    }

    if (!IsValidPrimvarName(result)){
        result = TfToken();
    }
    
    return result;
}

inline UsdGeomPrimvar::UsdGeomPrimvar(const UsdPrim& prim, const TfToken& primvarName, const SdfValueTypeName& typeName) 
{
    TfToken attrName = MakeNamespaced(primvarName);

    if (!attrName.IsEmpty())
    {
        m_attr = prim.CreateAttribute(attrName, typeName, /* custom = */ false);
    }
}

}