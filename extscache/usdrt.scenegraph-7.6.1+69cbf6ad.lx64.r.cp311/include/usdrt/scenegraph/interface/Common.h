// Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "AccessType.h"

#include <omni/core/IObject.h>
#include <omni/fabric/IFabric.h>

//! @file interface/Common.h
//!
//! @brief Shared enums and structs for interfaces

namespace usdrt
{

//! @enum UsdSchemaType
//! An enum representing which type of schema a given schema class belongs to
enum class UsdSchemaType
{
    //! Represents abstract or base schema types that are interface-only
    //! and cannot be instantiated. These are reserved for core base classes
    //! known to the usdGenSchema system, so this should never be assigned to
    //! generated schema classes.
    AbstractBase,
    //! Represents a non-concrete typed schema
    AbstractTyped,
    //! Represents a concrete typed schema
    ConcreteTyped,
    //! Non-applied API schema
    NonAppliedAPI,
    //! Single Apply API schema
    SingleApplyAPI,
    //! Multiple Apply API Schema
    MultipleApplyAPI

};

//! @enum TimeChange
//! Specifies how to dirty time-sampled attributes when synchronizing USD
//! to Fabric.
enum class TimeChange : uint32_t
{
    LazyUpdate, //!< Dirty only if a new time value was passed
    ForceUpdate, //!< Always update (override) time-sampled data
    NoUpdate //!< Do not update time-sampled data
};

//! @private Don't include this in docs build
enum class OMNI_ATTR("prefix=e") ListPosition : uint32_t
{
    eFrontOfPrepend,
    eBackOfPrepend,
    eFrontOfAppend,
    eBackOfAppend
};

//! @private Don't include this in docs build
struct AttrSpecC
{
    omni::fabric::Type type;
    omni::fabric::TokenC name;
    AccessType accessType;
};

} // namespace usdrt
