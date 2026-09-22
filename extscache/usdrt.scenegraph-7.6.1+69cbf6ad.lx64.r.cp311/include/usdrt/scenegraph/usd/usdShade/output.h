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

/// @file usdShade/output.h

#include <usdrt/scenegraph/usd/usd/attribute.h>

namespace usdrt
{

class UsdShadeConnectableAPI;
class UsdShadeInput;

/// \class UsdShadeOutput
///
/// This class encapsulates a shader or node-graph output, which is a
/// connectable attribute representing a typed, externally computed value.
///
class UsdShadeOutput
{
public:
    /// Default constructor returns an invalid Output.  Exists for
    /// container classes
    UsdShadeOutput() = default;

    /// @{

    /// Speculative constructor that will produce a valid UsdShadeOutput when
    /// \p attr already represents a shade Output, and produces an \em invalid
    /// UsdShadeOutput otherwise (i.e. the explicit bool conversion operator
    /// will return false).
    explicit UsdShadeOutput(const UsdAttribute& attr);

    /// Get the name of the attribute associated with the output.
    ///
    TfToken GetFullName() const;

    /// Returns the name of the output.
    ///
    /// We call this the base name since it strips off the "outputs:" namespace
    /// prefix from the attribute name, and returns it.
    ///
    TfToken GetBaseName() const;

    /// Get the prim that the output belongs to.
    UsdPrim GetPrim() const;

    /// Get the "scene description" value type name of the attribute associated
    /// with the output.
    ///
    SdfValueTypeName GetTypeName() const;

    /// Test whether a given UsdAttribute represents a valid Output, which
    /// implies that creating a UsdShadeOutput from the attribute will succeed.
    ///
    /// Success implies that \c attr.IsDefined() is true.
    static bool IsOutput(const UsdAttribute& attr);

    /// Explicit UsdAttribute extractor.
    const UsdAttribute& GetAttr() const;

    /// Allow UsdShadeOutput to auto-convert to UsdAttribute, so you can
    /// pass a UsdShadeOutput to any function that accepts a UsdAttribute or
    /// const-ref thereto.
    operator const UsdAttribute&() const;

    /// Return true if the wrapped UsdAttribute is defined, and in
    /// addition the attribute is identified as an output.
    ///
    bool IsDefined() const;

    /// Return true if this Output is valid for querying and authoring
    /// values and metadata, which is identically equivalent to IsDefined().
    explicit operator bool() const;

    /// @}

    /// Connects this Output to the given input, \p sourceInput.
    ///
    /// \sa UsdShadeConnectableAPI::ConnectToSource
    ///
    bool ConnectToSource(const UsdShadeInput& sourceInput) const;

    /// Connects this Output to the given output, \p sourceOutput.
    ///
    /// \sa UsdShadeConnectableAPI::ConnectToSource
    ///
    bool ConnectToSource(const UsdShadeOutput& sourceOutput) const;

private:
    friend class UsdShadeConnectableAPI;

    // Constructor that creates a UsdShadeOutput with the given name on the
    // given prim.
    // \p name here is the unnamespaced name of the output.
    UsdShadeOutput(UsdPrim prim, const TfToken& name, const SdfValueTypeName& typeName);

    static TfToken _GetOutputAttrName(const TfToken outputName);

    UsdAttribute _attr;
};

inline UsdShadeOutput::UsdShadeOutput(const UsdAttribute& attr) : _attr(attr)
{
}

inline UsdShadeOutput::UsdShadeOutput(UsdPrim prim, const TfToken& name, const SdfValueTypeName& typeName)
{
    auto attrName = _GetOutputAttrName(name);
    _attr = prim.GetAttribute(attrName);
    if (!_attr)
    {
        _attr = prim.CreateAttribute(attrName, typeName, /* custom = */ false);
    }
}

inline TfToken UsdShadeOutput::GetFullName() const
{
    return _attr.GetName();
}

inline TfToken UsdShadeOutput::GetBaseName() const
{
    return TfToken(SdfPath::StripPrefixNamespace(GetFullName().GetString(), UsdShadeTokens->outputs.GetString()).first);
}

inline UsdPrim UsdShadeOutput::GetPrim() const
{
    return _attr.GetPrim();
}

inline SdfValueTypeName UsdShadeOutput::GetTypeName() const
{
    return _attr.GetTypeName();
}

inline bool UsdShadeOutput::IsOutput(const UsdAttribute& attr)
{
    if (!attr)
    {
        return false;
    }
    const auto nameString = attr.GetName().GetString();
    const auto outputString = UsdShadeTokens->outputs.GetString();
    return nameString.size() >= outputString.size() && nameString.compare(0, outputString.size(), outputString) == 0;
}

inline const UsdAttribute& UsdShadeOutput::GetAttr() const
{
    return _attr;
}

inline UsdShadeOutput::operator const UsdAttribute&() const
{
    return GetAttr();
}

inline bool UsdShadeOutput::IsDefined() const
{
    return _attr && IsOutput(_attr);
}

inline UsdShadeOutput::operator bool() const
{
    return IsDefined();
}

inline TfToken UsdShadeOutput::_GetOutputAttrName(const TfToken outputName)
{
    return TfToken(UsdShadeTokens->outputs.GetString() + outputName.GetString());
}

}
