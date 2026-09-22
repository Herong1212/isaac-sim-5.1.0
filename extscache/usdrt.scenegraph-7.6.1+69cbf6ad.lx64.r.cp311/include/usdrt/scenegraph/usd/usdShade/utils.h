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

#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/usd/sdf/path.h>
#include <usdrt/scenegraph/usd/usdShade/connectableAPI.h>
#include <usdrt/scenegraph/usd/usdShade/input.h>
#include <usdrt/scenegraph/usd/usdShade/output.h>
#include <usdrt/scenegraph/usd/usdShade/tokens.h>
#include <usdrt/scenegraph/usd/usdShade/types.h>

#include <utility>

/// @file usdShade/utils.h

namespace usdrt
{

/// \class UsdShadeUtils
///
/// This class contains a set of utility functions used when authoring and
/// querying shading networks.
///
class UsdShadeUtils
{
public:
    /// Returns the namespace prefix of the USD attribute associated with the
    /// given shading attribute type.
    static std::string GetPrefixForAttributeType(UsdShadeAttributeType sourceType);

    /// Given the full name of a shading attribute, returns it's base name and
    /// shading attribute type.
    static std::pair<TfToken, UsdShadeAttributeType> GetBaseNameAndType(const TfToken& fullName);

    /// \brief Find what is connected to an Input or Output recursively
    ///
    /// GetValueProducingAttributes implements the UsdShade connectivity rules
    /// described in \ref UsdShadeAttributeResolution .
    ///
    /// When tracing connections within networks that contain containers like
    /// UsdShadeNodeGraph nodes, the actual output(s) or value(s) at the end of
    /// an input or output might be multiple connections removed. The methods
    /// below resolves this across multiple physical connections.
    ///
    /// An UsdShadeInput is getting its value from one of these sources:
    /// - If the input is not connected the UsdAttribute for this input is
    /// returned, but only if it has an authored value. The input attribute
    /// itself carries the value for this input.
    /// - If the input is connected we follow the connection(s) until we reach
    /// a valid output of a UsdShadeShader node or if we reach a valid
    /// UsdShadeInput attribute of a UsdShadeNodeGraph or UsdShadeMaterial that
    /// has an authored value.
    ///
    /// An UsdShadeOutput on a container can get its value from the same
    /// type of sources as a UsdShadeInput on either a UsdShadeShader or
    /// UsdShadeNodeGraph. Outputs on non-containers (UsdShadeShaders) cannot be
    /// connected.
    ///
    /// This function returns a vector of UsdAttributes. The vector is empty if
    /// no valid attribute was found. The type of each attribute can be
    /// determined with the \p UsdShadeUtils::GetType function.
    ///
    /// If \p shaderOutputsOnly is true, it will only report attributes that are
    /// outputs of non-containers (UsdShadeShaders). This is a bit faster and
    /// what is need when determining the connections for Material terminals.
    ///
    /// \note This will return the last attribute along the connection chain
    /// that has an authored value, which might not be the last attribute in the
    /// chain itself.
    /// \note When the network contains multi-connections, this function can
    /// return multiple attributes for a single input or output. The list of
    /// attributes is build by a depth-first search, following the underlying
    /// connection paths in order. The list can contain both UsdShadeOutput and
    /// UsdShadeInput attributes. It is up to the caller to decide how to
    /// process such a mixture.
    /// \note These functions work recursively, but that is not supported
    static UsdShadeAttributeVector GetValueProducingAttributes(UsdShadeInput const& input,
                                                               bool shaderOutputsOnly = false);
    /// \overload
    static UsdShadeAttributeVector GetValueProducingAttributes(UsdShadeOutput const& output,
                                                               bool shaderOutputsOnly = false);
};

inline std::string UsdShadeUtils::GetPrefixForAttributeType(UsdShadeAttributeType sourceType)
{
    return UsdShadeConnectableAPI::_GetPrefixForAttributeType(sourceType);
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

inline std::pair<TfToken, UsdShadeAttributeType> UsdShadeUtils::GetBaseNameAndType(const TfToken& fullName)
{
    return UsdShadeConnectableAPI::_GetBaseNameAndType(fullName);
}

}
