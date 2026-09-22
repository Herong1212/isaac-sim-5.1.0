// Copyright (c) 2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
// TODO USD COPYRIGHT AS WELL?
#pragma once

/// @file usdShade/input.h

#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usdShade/tokens.h>

namespace usdrt
{

class UsdShadeConnectableAPI;
class UsdShadeOutput;

/// \class UsdShadeInput
///
/// This class encapsulates a shader or node-graph input, which is a
/// connectable attribute representing a typed value.
///
class UsdShadeInput
{
public:
    /// Default constructor returns an invalid Input.  Exists for the sake of
    /// container classes
    UsdShadeInput() = default;

    /// Get the name of the attribute associated with the Input.
    ///
    TfToken GetFullName() const;

    /// Returns the name of the input.
    ///
    /// We call this the base name since it strips off the "inputs:" namespace
    /// prefix from the attribute name, and returns it.
    ///
    TfToken GetBaseName() const;

    /// Get the "scene description" value type name of the attribute associated
    /// with the Input.
    ///
    SdfValueTypeName GetTypeName() const;

    /// Speculative constructor that will produce a valid UsdShadeInput when
    /// \p attr already represents a shade Input, and produces an \em invalid
    /// UsdShadeInput otherwise (i.e. the explicit bool conversion operator will
    /// return false).
    explicit UsdShadeInput(const UsdAttribute& attr);

    /// Get the prim that the input belongs to.
    UsdPrim GetPrim() const;

    /// Convenience wrapper for the templated UsdAttribute::Get().
    template <typename T>
    bool Get(T* value, UsdTimeCode time = UsdTimeCode::Default()) const;

    /// \overload
    /// Set a value of the Input at \p time.
    ///
    template <typename T>
    bool Set(const T& value, UsdTimeCode time = UsdTimeCode::Default());

    /// Test whether a given UsdAttribute represents a valid Input, which
    /// implies that creating a UsdShadeInput from the attribute will succeed.
    ///
    /// Success implies that \c attr.IsDefined() is true.
    static bool IsInput(const UsdAttribute& attr);

    /// Explicit UsdAttribute extractor.
    const UsdAttribute& GetAttr() const;

    /// Allow UsdShadeInput to auto-convert to UsdAttribute, so you can
    /// pass a UsdShadeInput to any function that accepts a UsdAttribute or
    /// const-ref thereto.
    operator const UsdAttribute&() const;

    /// Return true if the wrapped UsdAttribute is defined, and in addition the
    /// attribute is identified as an input.
    bool IsDefined() const;

    /// Return true if this Input is valid for querying and authoring
    /// values and metadata, which is identically equivalent to IsDefined().
    explicit operator bool() const;

    /// Connects this Input to the given input, \p sourceInput.
    ///
    /// \sa UsdShadeConnectableAPI::ConnectToSource
    ///
    bool ConnectToSource(const UsdShadeInput& sourceInput) const;


    /// Connects this Input to the given output, \p sourceOutput.
    ///
    /// \sa UsdShadeConnectableAPI::ConnectToSource
    ///
    bool ConnectToSource(const UsdShadeOutput& sourceOutput) const;

private:
    friend class UsdShadeConnectableAPI;

    // Constructor that creates a UsdShadeInput with the given name on the
    // given prim.
    // \p name here is the unnamespaced name of the input.
    UsdShadeInput(UsdPrim prim, const TfToken& name, const SdfValueTypeName& typeName);

    static TfToken _GetInputAttrName(const TfToken inputName);

    UsdAttribute _attr;
};

inline UsdShadeInput::UsdShadeInput(const UsdAttribute& attr) : _attr(attr)
{
}

inline UsdShadeInput::UsdShadeInput(UsdPrim prim, const TfToken& name, const SdfValueTypeName& typeName)
{
    auto inputAttrName = _GetInputAttrName(name);
    if (prim.HasAttribute(inputAttrName))
    {
        _attr = prim.GetAttribute(inputAttrName);
    }

    if (!_attr)
    {
        _attr = prim.CreateAttribute(inputAttrName, typeName,
                                     /* custom = */ false);
    }
}

inline TfToken UsdShadeInput::GetFullName() const
{
    return _attr.GetName();
}

inline TfToken UsdShadeInput::GetBaseName() const
{
    auto name = GetFullName().GetString();
    if (TfStringStartsWith(name, UsdShadeTokens->inputs.GetString()))
    {
        return TfToken(name.substr(UsdShadeTokens->inputs.GetString().size()));
    }

    return GetFullName();
}

inline SdfValueTypeName UsdShadeInput::GetTypeName() const
{
    return _attr.GetTypeName();
}

inline UsdPrim UsdShadeInput::GetPrim() const
{
    return _attr.GetPrim();
}

template <typename T>
inline bool UsdShadeInput::Get(T* value, UsdTimeCode time) const
{
    return GetAttr().Get(value, time);
}

template <typename T>
inline bool UsdShadeInput::Set(const T& value, UsdTimeCode time)
{
    return _attr.Set(value, time);
}

inline bool UsdShadeInput::IsInput(const UsdAttribute& attr)
{
    if (!attr)
    {
        return false;
    }
    const auto nameString = attr.GetName().GetString();
    const auto inputString = UsdShadeTokens->inputs.GetString();
    return nameString.size() >= inputString.size() && nameString.compare(0, inputString.size(), inputString) == 0;
}

inline const UsdAttribute& UsdShadeInput::GetAttr() const
{
    return _attr;
}

inline UsdShadeInput::operator const UsdAttribute&() const
{
    return GetAttr();
}

inline bool UsdShadeInput::IsDefined() const
{
    return _attr && IsInput(_attr);
}

inline UsdShadeInput::operator bool() const
{
    return IsDefined();
}

inline TfToken UsdShadeInput::_GetInputAttrName(const TfToken inputName)
{
    return TfToken(UsdShadeTokens->inputs.GetString() + inputName.GetString());
}

}
