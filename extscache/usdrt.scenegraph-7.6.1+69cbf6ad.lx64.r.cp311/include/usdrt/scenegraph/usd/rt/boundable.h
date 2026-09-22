// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file usdrt/scenegraph/usd/rt/boundable.h
//!
//! @brief Provides RtBoundable class, for manipulating extents in Fabric

#include "tokens.h"

#include <usdrt/gf/range.h>
#include <usdrt/scenegraph/interface/IRtBoundable.h>
#include <usdrt/scenegraph/usd/rt/xformable.h>

namespace usdrt
{

//! The RtBoundable class provides a schema for reading and writing
//! the Fabric Scene Delegate extent attributes. It also inherits
//! from RtXformable, and can be used for authoring Fabric transform data as well.
//!
//! The Fabric Scene Delegate (available in Create and all other Kit-based applications)
//! will query Fabric for these special
//! attributes when adding geometry to the Hydra render index. A world extent
//! attribute is currently required by Fabric Scene Delegate for any
//! geometry in Fabric to be considered for rendering.
//!
//! This API currently allows you to author a world extent attribute for a prim.
//!
//! |     Name     |    Fabric Attribute Name   |    Type     |        APIs                        |
//! | ------------ | -------------------------- | ----------- | ---------------------------------- |
//! | worldExtent  | _worldExtent               | range3d     | Create/GetWorldExtentAttr          |
//!
//!
//! A helper methods are provided to set either the world-space extent
//! value in Fabric using the computed values from the USD prim:
//!   - SetWorldExtentFromUsd()
//!
class RtBoundable : public RtXformable
{
public:
    //! Construct a RtBoundable instance from a UsdPrim.
    //! Providing an invalid UsdPrim will result in an
    //! invalid RtBoundable
    //!
    //! @param prim The prim to use to construct the RtBoundable
    RtBoundable(const UsdPrim& prim = UsdPrim());

    //! Copy constructor
    RtBoundable(const RtBoundable& boundable) = default;

    //! World extent is the absolute, world-space extent of the
    //! prim. This attribute is required by Fabric Scene Delegate
    //! to render geometry with Hydra.
    //!
    //! | ||
    //! | -- | -- |
    //! | C++ Type | GfRange3d |
    //! | ValueTypeName | Range3d |
    UsdAttribute GetWorldExtentAttr() const;

    //! Create or get the existing world extent attribute.
    //!
    //! @param defaultValue The value to set when creating the world extent attribute in Fabric
    UsdAttribute CreateWorldExtentAttr(const GfRange3d& defaultValue = GfRange3d()) const;

    //! Check if the Fabric prim has a world extent attribute
    //!
    //! @returns true if any world extent attribute exists in Fabric
    bool HasWorldExtent() const;

    //! Remove the world extent attribute from the Fabric prim
    //!
    //! @returns true if a world extent attribute existed and was removed
    bool ClearWorldExtent();

    //! Set the world extent from the underlying USD prim
    //!
    //! @returns true if the world extent attribute was created and set or updated from USD
    bool SetWorldExtentFromUsd();
};

inline RtBoundable::RtBoundable(const UsdPrim& prim) : RtXformable(prim)
{
}

inline UsdAttribute RtBoundable::GetWorldExtentAttr() const
{
    return m_prim.GetAttribute(RtTokens->worldExtent);
}

inline UsdAttribute RtBoundable::CreateWorldExtentAttr(const GfRange3d& defaultValue) const
{
    UsdAttribute created = m_prim.CreateAttribute(RtTokens->worldExtent, SdfValueTypeNames->Range3d);
    created.Set(defaultValue);
    return created;
}

inline bool RtBoundable::HasWorldExtent() const
{
    return GetWorldExtentAttr().IsValid();
}

inline bool RtBoundable::ClearWorldExtent()
{
    if (HasWorldExtent())
    {
        return m_prim.RemoveProperty(RtTokens->worldExtent);
    }

    return false;
}

inline bool RtBoundable::SetWorldExtentFromUsd()
{
    auto iBoundable = omni::core::createType<usdrt::IRtBoundable>();
    if (!iBoundable)
    {
        return false;
    }

    return iBoundable->setWorldExtentFromUsd(m_prim.m_prim);
}

} // namespace usdrt
