// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <usdrt/scenegraph/interface/Common.h>
#include <usdrt/scenegraph/usd/sdf/valueTypeName.h>

//! @file common.h
//!
//! @brief Shared enums and structs

namespace usdrt
{


//! @enum UsdListPosition
//! Specifies a position to add items to lists.
//! @note Current support adds to the front for either
//! `Front` enum and appends for either `Back` enum.
enum UsdListPosition
{
    //! The position at the front of the prepend list.
    UsdListPositionFrontOfPrependList,
    //! The position at the back of the prepend list.
    UsdListPositionBackOfPrependList,
    //! The position at the front of the append list.
    UsdListPositionFrontOfAppendList,
    //! The position at the back of the append list.
    UsdListPositionBackOfAppendList,
};

//! Specifies an attribute to be accessed, and the type of that access (read-only, read-write, overwrite).
struct AttrSpec
{
    //! Attribute type
    usdrt::SdfValueTypeName type;
    //! Attribute name
    usdrt::TfToken name;
    //! The type of access requested, read-only, read-write, or overwrite.
    //!
    //! USDRT uses this information to mirror data between CPU and GPU when
    //! necessary, and to use the minimum number of CPU<->GPU copies when it
    //! does so. For example, if data is valid on CPU and is then requested on
    //! GPU with eOverwrite, USDRT doesn't have to copy the data from CPU to
    //! GPU because it knows the GPU is about to overwrite it.
    AccessType accessType;
};

} // namespace usdrt
