// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file usdrt/scenegraph/usd/rt/tokens.h
//!
//! @brief Provides public tokens for RT schema

#include <usdrt/scenegraph/base/tf/token.h>

namespace usdrt
{

//! @class RtTokensType
//!
//! Provides standard set of public tokens for Rt schema.
//! Access via the RtTokens helper accessor.
//!
//! @code
//!     prim.GetAttribute(RtTokens->worldPosition);
//! @endcode
struct RtTokensType
{
    RtTokensType();

    //! @brief "_worldPosition"
    //!
    //! RtXformable attribute
    const TfToken worldPosition;

    //! \brief "_worldOrientation"
    //!
    //! RtXformable attribute
    const TfToken worldOrientation;

    //! @brief "_worldScale"
    //!
    //! RtXformable attribute
    const TfToken worldScale;

    //! @brief "_localMatrix"
    //!
    //! RtXformable attribute
    const TfToken localMatrix;

    //! @brief "_worldExtent"
    //!
    //! RtBoundable attribute
    const TfToken worldExtent;

    //! @brief "omni:fabric:localMatrix"
    //!
    //! RtXformable attribute
    const TfToken fabricHierarchyLocalMatrix;

    //! @brief "omni:fabric:worldMatrix"
    //!
    //! RtXformable attribute
    const TfToken fabricHierarchyWorldMatrix;
};

inline RtTokensType::RtTokensType()
    : worldPosition("_worldPosition"),
      worldOrientation("_worldOrientation"),
      worldScale("_worldScale"),
      localMatrix("_localMatrix"),
      worldExtent("_worldExtent"),
      fabricHierarchyLocalMatrix("omni:fabric:localMatrix"),
      fabricHierarchyWorldMatrix("omni:fabric:worldMatrix")
{
}

struct RtTokensTypeAccessor
{
    const RtTokensType* operator->()
    {
        static const RtTokensType tokens;
        return &tokens;
    }
};

// This is not great
static RtTokensTypeAccessor RtTokens;


} // namespace usdrt
