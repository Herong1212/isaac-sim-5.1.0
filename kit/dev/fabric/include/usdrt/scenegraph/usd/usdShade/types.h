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

/// @file usdShade/types.h

namespace usdrt
{

/// \enum UsdShadeAttributeType
///
/// Specifies the type of a shading attribute.
///
enum class UsdShadeAttributeType
{
    Invalid,
    Input,
    Output,
};

/// \enum UsdShadeConnectionModification
///
/// Choice when creating a single connection with the \p ConnectToSource method
/// for a shading attribute. The new connection can replace any existing
/// connections or be added to the list of existing connections. In which case
/// there is a choice between prepending and appending to said list, which will
/// be represented by Usd's list editing operations.
///
enum class UsdShadeConnectionModification
{
    Replace,
    Prepend,
    Append
};

/// \typedef UsdShadeAttributeVector
///
/// For performance reasons we want to be extra careful when reporting
/// attributes. It is possible to have multiple connections for a shading
/// attribute, but by far the more common cases are one or no connection. So we
/// use a small vector that can be stack allocated that holds space for a single
/// attributes, but that can "spill" to the heap in the case of multiple
/// upstream attributes.
using UsdShadeAttributeVector = std::vector<UsdAttribute>;

/// \typedef UsdShadeSourceInfoVector
///
/// For performance reasons we want to be extra careful when reporting
/// connections. It is possible to have multiple connections for a shading
/// attribute, but by far the more common cases are one or no connection.
/// So we use a small vector that can be stack allocated that holds space
/// for a single source, but that can "spill" to the heap in the case
/// of a multi-connection.
///
/// /sa UsdShadeConnectionSourceInfo in connectableAPI.h
struct UsdShadeConnectionSourceInfo;
using UsdShadeSourceInfoVector = std::vector<UsdShadeConnectionSourceInfo>;

}
