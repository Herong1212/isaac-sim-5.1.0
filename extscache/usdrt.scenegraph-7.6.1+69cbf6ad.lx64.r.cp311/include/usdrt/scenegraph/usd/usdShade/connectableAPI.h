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

/// @file usdShade/connectableAPI.h

// GENERATED FILE DO NOT EDIT

#include "usdrt/scenegraph/usd/usd/apiSchemaBase.h"

// clang-format off
/* Extra Includes
// USDRT NOTE: Use custom includes below instead to allow for
// implementation differences in the custom code. This section comes
// from the pxr schema.usda files which we may not have in usdrt.
//#include "usdrt/scenegraph/usd/usd/typed.h"
#include "usdrt/scenegraph/usd/usdShade/input.h"
#include "usdrt/scenegraph/usd/usdShade/output.h"
#include "usdrt/scenegraph/usd/usdShade/tokens.h"
#include "usdrt/scenegraph/usd/usdShade/types.h"*/
// clang-format on

// ===================================================================== //
// Feel free to add custom includes between BEGIN and END CUSTOM INCLUDES
// below this line. It will be preserved by the code generator.
// We are using this instead of the `extraIncludes` in the pxr schema.usda
// files to allow for implementation differences in the custom code.
// ===================================================================== //
// --(BEGIN CUSTOM INCLUDES)--
#include <usdrt/scenegraph/usd/usdShade/input.h>
#include <usdrt/scenegraph/usd/usdShade/output.h>
#include <usdrt/scenegraph/usd/usdShade/types.h>

namespace usdrt
{

struct UsdShadeConnectionSourceInfo;
class UsdShadeUtils;

} // namespace usdrt
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
// CONNECTABLEAPI                                                              //
// -------------------------------------------------------------------------- //

/// @class UsdShadeConnectableAPI
///
/// UsdShadeConnectableAPI is an API schema that provides a common
/// interface for creating outputs and making connections between shading
/// parameters and outputs. The interface is common to all UsdShade schemas
/// that support Inputs and Outputs, which currently includes UsdShadeShader,
/// UsdShadeNodeGraph, and UsdShadeMaterial .
///
/// One can construct a UsdShadeConnectableAPI directly from a UsdPrim, or
/// from objects of any of the schema classes listed above.  If it seems
/// onerous to need to construct a secondary schema object to interact with
/// Inputs and Outputs, keep in mind that any function whose purpose is either
/// to walk material/shader networks via their connections, or to create such
/// networks, can typically be written entirely in terms of
/// UsdShadeConnectableAPI objects, without needing to care what the underlying
/// prim type is.
///
/// Additionally, the most common UsdShadeConnectableAPI behaviors
/// (creating Inputs and Outputs, and making connections) are wrapped as
/// convenience methods on the prim schema classes (creation) and
/// UsdShadeInput and UsdShadeOutput.
///

class UsdShadeConnectableAPI : public UsdAPISchemaBase
{

public:
    /// Compile time constant representing what kind of schema this class is.
    ///
    /// @sa UsdSchemaType
    static const UsdSchemaType schemaType = UsdSchemaType::NonAppliedAPI;


    /// Construct a UsdShadeConnectableAPI on UsdPrim @p prim.
    /// Equivalent to UsdShadeConnectableAPI::Get(prim.GetStage(), prim.GetPath())
    /// for a @em valid @p prim , but will not immediately throw an error for
    /// an invalid @p prim
    explicit UsdShadeConnectableAPI(const UsdPrim& prim = UsdPrim()) : UsdAPISchemaBase(prim)
    {
    }

    /// Construct a UsdShadeConnectableAPI on the prim held by @p schemaObj .
    /// Should be preferred over UsdShadeConnectableAPI(schemaObj.GetPrim()),
    /// as it preserves SchemaBase state.
    explicit UsdShadeConnectableAPI(const UsdSchemaBase& schemaObj) : UsdAPISchemaBase(schemaObj)
    {
    }

    /// Destructor.
    virtual ~UsdShadeConnectableAPI()
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
    /// \name Outputs
    /// @{

    /// Create an output, which represents and externally computed, typed value.
    /// Outputs on node-graphs can be connected.
    ///
    /// The attribute representing an output is created in the "outputs:"
    /// namespace.
    ///
    UsdShadeOutput CreateOutput(const TfToken& name, const SdfValueTypeName& typeName) const;

    /// Return the requested output if it exists.
    ///
    /// \p name is the unnamespaced base name.
    ///
    UsdShadeOutput GetOutput(const TfToken& name) const;

    /// Returns all outputs on the connectable prim (i.e. shader or node-graph).
    /// Outputs are represented by attributes in the "outputs:" namespace.
    /// If \p onlyAuthored is true (the default), then only return authored
    /// attributes; otherwise, this also returns un-authored builtins.
    ///
    std::vector<UsdShadeOutput> GetOutputs(bool onlyAuthored = true) const;

    /// @}

    /// \name Inputs
    /// @{

    /// Create an input which can both have a value and be connected.
    /// The attribute representing the input is created in the "inputs:"
    /// namespace.
    ///
    UsdShadeInput CreateInput(const TfToken& name, const SdfValueTypeName& typeName) const;

    /// Return the requested input if it exists.
    ///
    /// \p name is the unnamespaced base name.
    ///
    UsdShadeInput GetInput(const TfToken& name) const;

    /// Returns all inputs on the connectable prim (i.e. shader or node-graph).
    /// Inputs are represented by attributes in the "inputs:" namespace.
    /// If \p onlyAuthored is true (the default), then only return authored
    /// attributes; otherwise, this also returns un-authored builtins.
    ///
    std::vector<UsdShadeInput> GetInputs(bool onlyAuthored = true) const;

    /// @}

    using ConnectionModification = UsdShadeConnectionModification;

    /// Authors a connection for a given shading attribute \p shadingAttr.
    ///
    /// \p shadingAttr can represent a parameter, an input or an output.
    /// \p source is a struct that describes the upstream source attribute
    /// with all the information necessary to make a connection. See the
    /// documentation for UsdShadeConnectionSourceInfo.
    /// \p mod describes the operation that should be applied to the list of
    /// connections. By default the new connection will replace any existing
    /// connections, but it can add to the list of connections to represent
    /// multiple input connections.
    ///
    /// \return
    /// \c true if a connection was created successfully.
    /// \c false if \p shadingAttr or \p source is invalid.
    ///
    /// \note This method does not verify the connectability of the shading
    /// attribute to the source. Clients must invoke CanConnect() themselves
    /// to ensure compatibility.
    /// \note The source shading attribute is created if it doesn't exist
    /// already.
    ///
    static bool ConnectToSource(const UsdAttribute& shadingAttr,
                                const UsdShadeConnectionSourceInfo& source,
                                const ConnectionModification mod = ConnectionModification::Replace);

    /// \overload
    static bool ConnectToSource(const UsdShadeInput& input,
                                const UsdShadeConnectionSourceInfo& source,
                                const ConnectionModification mod = ConnectionModification::Replace);

    /// \overload
    static bool ConnectToSource(const UsdShadeOutput& output,
                                const UsdShadeConnectionSourceInfo& source,
                                const ConnectionModification mod = ConnectionModification::Replace);

    /// \deprecated Please use the versions that take a
    /// UsdShadeConnectionSourceInfo to describe the upstream source
    /// \overload
    static bool ConnectToSource(const UsdAttribute& shadingAttr,
                                const UsdShadeConnectableAPI& source,
                                const TfToken& sourceName,
                                const UsdShadeAttributeType sourceType = UsdShadeAttributeType::Output,
                                SdfValueTypeName typeName = SdfValueTypeName());

    /// \overload
    ///
    /// Connect the given shading attribute to the given source input.
    ///
    static bool ConnectToSource(const UsdAttribute& shadingAttr, const UsdShadeInput& sourceInput);

    /// \overload
    static bool ConnectToSource(const UsdShadeInput& input, const UsdShadeInput& sourceInput);

    /// \overload
    static bool ConnectToSource(const UsdShadeOutput& output, const UsdShadeInput& sourceInput);

    static bool ConnectToSource(const UsdAttribute& shadingAttr, const UsdShadeOutput& sourceOutput);

    /// \overload
    static bool ConnectToSource(const UsdShadeInput& input, const UsdShadeOutput& sourceOutput);

    /// \overload
    static bool ConnectToSource(const UsdShadeOutput& output, const UsdShadeOutput& sourceOutput);

private:
    static UsdAttribute _GetOrCreateSourceAttr(UsdShadeConnectionSourceInfo const& sourceInfo,
                                               SdfValueTypeName fallbackTypeName);

    // To work around not having source files we are implementing UsdShadeUtils functions here.
    friend class UsdShadeUtils;
    friend struct UsdShadeConnectionSourceInfo;

    /// Returns the namespace prefix of the USD attribute associated with the
    /// given shading attribute type.
    static std::string _GetPrefixForAttributeType(UsdShadeAttributeType sourceType);

    /// Given the full name of a shading attribute, returns it's base name and
    /// shading attribute type.
    static std::pair<TfToken, UsdShadeAttributeType> _GetBaseNameAndType(const TfToken& fullName);
    // --(END CUSTOM DECLARATION CODE)--
};

inline const TfToken UsdShadeConnectableAPI::_GetStaticTfType()
{
    const static TfToken token("UsdShadeConnectableAPI");
    return token;
}

/* virtual */
inline const TfToken UsdShadeConnectableAPI::_GetTfTypeToken() const
{
    const static TfToken token("UsdShadeConnectableAPI");
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

/// A compact struct to represent a bundle of information about an upstream
/// source attribute
struct UsdShadeConnectionSourceInfo
{
    /// \p source is the connectable prim that produces or contains a value
    /// for the given shading attribute.
    UsdShadeConnectableAPI source;
    /// \p sourceName is the name of the shading attribute that is the target
    /// of the connection. This excludes any namespace prefix that determines
    /// the type of the source (eg, output).
    TfToken sourceName;
    /// \p sourceType is used to indicate the type of the shading attribute
    /// that is the target of the connection. The source type is used to
    /// determine the namespace prefix that must be attached to \p sourceName
    /// to determine the source full attribute name.
    UsdShadeAttributeType sourceType = UsdShadeAttributeType::Invalid;
    /// \p typeName, if specified, is the typename of the attribute to create
    /// on the source if it doesn't exist when creating a connection
    SdfValueTypeName typeName;

    UsdShadeConnectionSourceInfo() = default;
    explicit UsdShadeConnectionSourceInfo(const UsdShadeConnectableAPI& source_,
                                          const TfToken& sourceName_,
                                          UsdShadeAttributeType sourceType_,
                                          SdfValueTypeName typeName_ = SdfValueTypeName())
        : source(source_), sourceName(sourceName_), sourceType(sourceType_), typeName(typeName_)
    {
    }

    explicit UsdShadeConnectionSourceInfo(const UsdShadeInput& input)
        : source(input.GetPrim()),
          sourceName(input.GetBaseName()),
          sourceType(UsdShadeAttributeType::Input),
          typeName(input.GetAttr().GetTypeName())
    {
    }

    explicit UsdShadeConnectionSourceInfo(const UsdShadeOutput& output)
        : source(output.GetPrim()),
          sourceName(output.GetBaseName()),
          sourceType(UsdShadeAttributeType::Output),
          typeName(output.GetAttr().GetTypeName())
    {
    }

    /// Construct the information for this struct from a property path. The
    /// source attribute does not have to exist, but the \p sourcePath needs to
    /// have a valid prefix to identify the sourceType. The source prim needs
    /// to exist and be UsdShadeConnectableAPI compatible
    explicit UsdShadeConnectionSourceInfo(const UsdStageRefPtr& stage, const SdfPath& sourcePath)
    {
        if (!stage)
        {
            return;
        }

        if (!sourcePath.IsPropertyPath())
        {
            return;
        }

        std::tie(sourceName, sourceType) = UsdShadeConnectableAPI::_GetBaseNameAndType(sourcePath.GetNameToken());

        // Check if the prim can be found on the stage and is a
        // UsdShadeConnectableAPI compatible prim
        source = UsdShadeConnectableAPI(stage->GetPrimAtPath(sourcePath.GetPrimPath()));

        // Note, initialization of typeName is optional, since the target attribute
        // might not exist (yet)
        // XXX try to get attribute from source.GetPrim()?
        UsdAttribute sourceAttr = stage->GetAttributeAtPath(sourcePath);
        if (sourceAttr)
        {
            typeName = sourceAttr.GetTypeName();
        }
    }

    /// Return true if this source info is valid for setting up a connection
    bool IsValid() const
    {
        // typeName can be invalid, so we don't check it. Order of checks is in
        // order of cost (cheap to expensive).
        // Note, for the source we only check that the prim is valid. We do not
        // verify that the prim is compatibel with UsdShadeConnectableAPI. This
        // makes it possible to target pure overs
        return (sourceType != UsdShadeAttributeType::Invalid) && !sourceName.IsEmpty() && (bool)source.GetPrim();
    }

    explicit operator bool() const
    {
        return IsValid();
    }

    bool operator==(const UsdShadeConnectionSourceInfo& other) const
    {
        // We don't compare the typeName, since it is optional
        return sourceName == other.sourceName && sourceType == other.sourceType &&
               // No equality operator is implemented for usdrt::UsdPrim
               source.GetPrim().GetPath() == other.source.GetPrim().GetPath();
    }

    bool operator!=(const UsdShadeConnectionSourceInfo& other) const
    {
        return !(*this == other);
    }
};

inline UsdShadeOutput UsdShadeConnectableAPI::CreateOutput(const TfToken& name, const SdfValueTypeName& typeName) const
{
    return UsdShadeOutput(GetPrim(), name, typeName);
}

inline UsdShadeOutput UsdShadeConnectableAPI::GetOutput(const TfToken& name) const
{
    TfToken outputAttrName(UsdShadeTokens->outputs.GetString() + name.GetString());
    if (GetPrim().HasAttribute(outputAttrName))
    {
        return UsdShadeOutput(GetPrim().GetAttribute(outputAttrName));
    }

    return UsdShadeOutput();
}

inline std::vector<UsdShadeOutput> UsdShadeConnectableAPI::GetOutputs(bool onlyAuthored) const
{
    // No UsdProperty like in pixar USD.
    std::vector<UsdAttribute> attributes = onlyAuthored ? GetPrim().GetAuthoredAttributes() : GetPrim().GetAttributes();

    // Filter for attributes and convert them to inputs
    std::vector<UsdShadeOutput> outputs;
    outputs.reserve(attributes.size());
    for (const auto& attr : attributes)
    {
        if (TfStringStartsWith(attr.GetName().GetString(), UsdShadeTokens->outputs.GetString()))
        {
            outputs.emplace_back(attr);
        }
    }
    return outputs;
}

inline UsdShadeInput UsdShadeConnectableAPI::CreateInput(const TfToken& name, const SdfValueTypeName& typeName) const
{
    return UsdShadeInput(GetPrim(), name, typeName);
}

inline UsdShadeInput UsdShadeConnectableAPI::GetInput(const TfToken& name) const
{
    TfToken inputAttrName(UsdShadeTokens->inputs.GetString() + name.GetString());

    if (GetPrim().HasAttribute(inputAttrName))
    {
        return UsdShadeInput(GetPrim().GetAttribute(inputAttrName));
    }

    return UsdShadeInput();
}

inline std::vector<UsdShadeInput> UsdShadeConnectableAPI::GetInputs(bool onlyAuthored) const
{
    // No UsdProperty like in pixar USD.
    std::vector<UsdAttribute> attributes = onlyAuthored ? GetPrim().GetAuthoredAttributes() : GetPrim().GetAttributes();

    // Filter for attributes and convert them to inputs
    std::vector<UsdShadeInput> inputs;
    inputs.reserve(attributes.size());
    for (const auto& attr : attributes)
    {
        if (TfStringStartsWith(attr.GetName().GetString(), UsdShadeTokens->inputs.GetString()))
        {
            inputs.emplace_back(attr);
        }
    }
    return inputs;
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdAttribute& shadingAttr,
                                                    const UsdShadeConnectionSourceInfo& source,
                                                    const ConnectionModification mod)
{
    if (!source)
    {
        return false;
    }

    UsdAttribute sourceAttr = _GetOrCreateSourceAttr(source, shadingAttr.GetTypeName());
    if (!sourceAttr)
    {
        // _GetOrCreateSourceAttr can only fail if CreateAttribute fails, which
        // will issue an appropriate error
        return false;
    }

    if (mod == ConnectionModification::Replace)
    {
        return shadingAttr.SetConnections(SdfPathVector{ sourceAttr.GetPath() });
    }
    else if (mod == ConnectionModification::Prepend)
    {
        return shadingAttr.AddConnection(sourceAttr.GetPath(), UsdListPositionFrontOfPrependList);
    }
    else if (mod == ConnectionModification::Append)
    {
        return shadingAttr.AddConnection(sourceAttr.GetPath(), UsdListPositionBackOfAppendList);
    }

    return false;
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdShadeInput& input,
                                                    const UsdShadeConnectionSourceInfo& source,
                                                    const ConnectionModification mod)
{
    return ConnectToSource(input.GetAttr(), source, mod);
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdShadeOutput& output,
                                                    const UsdShadeConnectionSourceInfo& source,
                                                    const ConnectionModification mod)
{
    return ConnectToSource(output.GetAttr(), source, mod);
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdAttribute& shadingAttr,
                                                    const UsdShadeConnectableAPI& source,
                                                    const TfToken& sourceName,
                                                    const UsdShadeAttributeType sourceType,
                                                    SdfValueTypeName typeName)
{
    return ConnectToSource(shadingAttr, UsdShadeConnectionSourceInfo(source, sourceName, sourceType, typeName));
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdAttribute& shadingAttr, const UsdShadeInput& sourceInput)
{
    return ConnectToSource(shadingAttr, UsdShadeConnectableAPI(sourceInput.GetPrim()), sourceInput.GetBaseName(),
                           UsdShadeAttributeType::Input, sourceInput.GetTypeName());
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdShadeInput& input, const UsdShadeInput& sourceInput)
{
    return ConnectToSource(input.GetAttr(), sourceInput);
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdShadeOutput& output, const UsdShadeInput& sourceInput)
{
    return ConnectToSource(output.GetAttr(), sourceInput);
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdAttribute& shadingAttr, const UsdShadeOutput& sourceOutput)
{
    return ConnectToSource(shadingAttr, UsdShadeConnectableAPI(sourceOutput.GetPrim()), sourceOutput.GetBaseName(),
                           UsdShadeAttributeType::Output, sourceOutput.GetTypeName());
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdShadeInput& input, const UsdShadeOutput& sourceOutput)
{
    return ConnectToSource(input.GetAttr(), sourceOutput);
}

inline bool UsdShadeConnectableAPI::ConnectToSource(const UsdShadeOutput& output, const UsdShadeOutput& sourceOutput)
{
    return ConnectToSource(output.GetAttr(), sourceOutput);
}

// These are implemented here to avoid circular dependencies?

inline bool UsdShadeOutput::ConnectToSource(const UsdShadeInput& sourceInput) const
{
    return UsdShadeConnectableAPI::ConnectToSource(*this, sourceInput);
}

inline bool UsdShadeOutput::ConnectToSource(const UsdShadeOutput& sourceOutput) const
{
    return UsdShadeConnectableAPI::ConnectToSource(*this, sourceOutput);
}

inline bool UsdShadeInput::ConnectToSource(const UsdShadeInput& sourceInput) const
{
    return UsdShadeConnectableAPI::ConnectToSource(*this, sourceInput);
}

inline bool UsdShadeInput::ConnectToSource(const UsdShadeOutput& sourceOutput) const
{
    return UsdShadeConnectableAPI::ConnectToSource(*this, sourceOutput);
}

inline UsdAttribute UsdShadeConnectableAPI::_GetOrCreateSourceAttr(UsdShadeConnectionSourceInfo const& sourceInfo,
                                                                   SdfValueTypeName fallbackTypeName)
{
    // Note, the validity of sourceInfo has been checked in ConnectToSource and
    // SetConnectedSources, which includes a check of source, sourceType and
    // sourceName
    UsdPrim sourcePrim = sourceInfo.source.GetPrim();

    std::string prefix = _GetPrefixForAttributeType(sourceInfo.sourceType);
    TfToken sourceAttrName(prefix + sourceInfo.sourceName.GetString());

    UsdAttribute sourceAttr = sourcePrim.GetAttribute(sourceAttrName);

    // If a source attribute doesn't exist on the sourcePrim we create one with
    // the proper type
    if (!sourceAttr)
    {
        sourceAttr = sourcePrim.CreateAttribute(
            sourceAttrName,
            // If typeName isn't valid use
            // the fallback
            // Operator bool is missing from SdfValueTypeName, which is implemented by comparing the tpye to an empty
            // (default) typename.
            sourceInfo.typeName == SdfValueTypeName() ? sourceInfo.typeName : fallbackTypeName,
            /* custom = */ false);
    }

    return sourceAttr;
}

inline std::string UsdShadeConnectableAPI::_GetPrefixForAttributeType(UsdShadeAttributeType sourceType)
{
    switch (sourceType)
    {
    case UsdShadeAttributeType::Input:
        return UsdShadeTokens->inputs.GetString();
    case UsdShadeAttributeType::Output:
        return UsdShadeTokens->outputs.GetString();
    default:
        return {};
    }
}

inline std::pair<TfToken, UsdShadeAttributeType> UsdShadeConnectableAPI::_GetBaseNameAndType(const TfToken& fullName)
{
    std::pair<std::string, bool> res =
        SdfPath::StripPrefixNamespace(fullName.GetString(), UsdShadeTokens->inputs.GetString());
    if (res.second)
    {
        return std::make_pair(TfToken(res.first), UsdShadeAttributeType::Input);
    }

    res = SdfPath::StripPrefixNamespace(fullName.GetString(), UsdShadeTokens->outputs.GetString());
    if (res.second)
    {
        return std::make_pair(TfToken(res.first), UsdShadeAttributeType::Output);
    }

    return std::make_pair(fullName, UsdShadeAttributeType::Invalid);
}

} // namespace usdrt
