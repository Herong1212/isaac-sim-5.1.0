// Copyright (c) 2022-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

//! @file usdrt/scenegraph/usd/rt/xformable.h
//!
//! @brief Provides RtXformable class, for manipulating transforms in Fabric

#include "tokens.h"

#include <usdrt/hierarchy/IFabricHierarchy.h>
#include <usdrt/scenegraph/base/gf/matrix4d.h>
#include <usdrt/scenegraph/base/gf/quatf.h>
#include <usdrt/scenegraph/base/gf/vec3d.h>
#include <usdrt/scenegraph/base/gf/vec3f.h>
#include <usdrt/scenegraph/base/tf/token.h>
#include <usdrt/scenegraph/interface/IRtPrim.h>
#include <usdrt/scenegraph/interface/IRtXformable.h>
#include <usdrt/scenegraph/usd/sdf/types.h>
#include <usdrt/scenegraph/usd/usd/attribute.h>
#include <usdrt/scenegraph/usd/usd/prim.h>

namespace usdrt
{

// clang-format off

//! # RtXformable
//!
//! The RtXformable class provides a schema for reading and writing
//! the OmniHydra and Fabric Scene Delegate transform attributes.
//!
//! ## Fabric Scene Delegate
//!
//! As of Kit 105.2, Fabric Scene Delegate (active by default in USD Explorer, can be optionally
//! enabled in any Kit-based application) leverages Fabric's Connectivity API to
//! represent scenegraph and transform hierarchies directly in Fabric without requiring a USD
//! lookback for this information. This enables changes to the transform of a prim in Fabric
//! to affect the transform of that prim's descendants in Fabric without any coordination with
//! USD stage (or without a USD stage or at all).
//!
//! The Fabric Hierarchy local and world transform values are created and populated on every
//! Imageable prim in Fabric at USD stage load time when Fabric Scene Delegate is enabled.
//!
//! The primary way to set transform data for Fabric Scene Delegate is by operating on
//! the Fabric Hierarchy local transform matrix of a prim. You can also query the
//! world transform of the prim (computed by the IFabricHierarchy interface) through
//! the world matrix attribute.
//!
//! |     Name                         |    Fabric Attribute Name   |    Type     |        APIs                                     | 
//! | -------------------------------- | -------------------------- | ----------- | ----------------------------------------------- | 
//! | fabric hierarchy local matrix    | omni:fabric:localMatrix    | matrix4d    | Create/GetFabricHierarchyLocalMatrixAttr        |
//! | fabric hierarchy world matrix    | omni:fabric:worldMatrix    | matrix4d    | Create/GetFabricHeirarchyWorldMatrixAttr        |
//!
//! ## OmniHydra Scene Delegate
//!
//! The OmniHydra scene delegate (active in Composer and all other Kit-based applications)
//! will query Fabric for changes to these special
//! attributes when discovering transform data in the Hydra render index. This enables
//! faster updates of prim transforms than USD and UsdImaging conventionally allow.
//!
//! There are two ways to set transform data with this API:
//!   - world transform
//!   - local transform
//!
//! If any world transform attribute is set on a prim in Fabric, it will take precedence over
//! any other transform data from USD or Fabric. The world transform is specified in three
//! parts.
//!
//! |     Name    |    Fabric Attribute Name   |    Type     |        APIs                        |
//! | ----------- | -------------------------- | ----------- | ---------------------------------- |
//! | position    | _worldPosition             | double3     | Create/GetWorldPositionAttr        |
//! | orientation | _worldOrientation          | quatf       | Create/GetWorldOrientationAttr     |
//! | scale       | _worldScale                | vec3f       | Create/GetWorldScaleAttr           |
//!
//! If only one or two of the world transform attributes exist in Fabric, OmniHydra will use default values
//! for the remaining attributes.
//!
//! If no world transform attributes are set in Fabric, a local transform may be specified for a prim.
//! (If any world transform attribute is specified, a local transform is ignored).
//! This local transform will take precedence over local transform data from USD for the prim, but
//! otherwise continue to participate in the transform hierarchy - changes to parent prims will
//! continue to affect the overall transform of the prim.
//!
//! |     Name    |    Fabric Attribute Name   |    Type     |        APIs                        |
//! | ----------- | -------------------------- | ----------- | ---------------------------------- |
//! | localMatrix | _localMatrix               | matrix4d    | Create/GetLocalMatrixAttr          |
//!
//! Helper methods are provided to set either the world-space transform attribute values or the local transform
//! value in Fabric using the computed values from the USD prim:
//!   - SetWorldXformFromUsd()
//!   - SetLocalXformFromUsd()
//!

// clang-format on
class RtXformable
{
public:
    //! Construct a RtXformable instance from a UsdPrim.
    //! Providing an invalid UsdPrim will result in an
    //! invalid RtXformable
    //!
    //! @param prim The prim to use to construct the RtXformable
    RtXformable(const UsdPrim& prim = UsdPrim());

    //! Copy constructor
    RtXformable(const RtXformable& xform) = default;

    //! Returns true if the underlying UsdPrim is valid, False otherwise
    operator bool() const;

    //! Return the held UsdPrim
    UsdPrim GetPrim() const;

    //! Return the SdfPath of the held UsdPrim
    SdfPath GetPath() const;

    //! Fabric Hierarchy local matrix is the local transform of the prim, relative to its parent
    //! when Fabric Scene Delegate is enabled.
    //! Changes to this attribute will cause the Fabric Hierarchy world matrix value
    //! to be updated on a subsequent call to IFabricHierarcy::updateWorldXforms -
    //! this happens automatically before each render frame when Fabric Scene Delegate is enabled.
    //!
    //! | ||
    //! | -- | -- |
    //! | C++ Type | GfMatrix4d |
    //! | ValueTypeName | Matrix4d |
    UsdAttribute GetFabricHierarchyLocalMatrixAttr() const;

    //! Create or get the existing Fabric Hierarchy local matrix attribute.
    //!
    //! @param defaultValue The value to set when creating the local matrix attribute in Fabric
    UsdAttribute CreateFabricHierarchyLocalMatrixAttr(const GfMatrix4d& defaultValue = GfMatrix4d(1)) const;

    //! Fabric Hierarchy world matrix is the local-to-world transform of the prim
    //! when Fabric Scene Delegate is enabled.
    //! Changes to this attribute will cause the Fabric Hierarchy local matrix value
    //! to be updated on a subsequent call to IFabricHierarcy::updateWorldXforms,
    //! by computing the value relative to the computed world transform of the parent prim -
    //! this happens automatically before each render frame when Fabric Scene Delegate is enabled.
    //!
    //! | ||
    //! | -- | -- |
    //! | C++ Type | GfMatrix4d |
    //! | ValueTypeName | Matrix4d |
    UsdAttribute GetFabricHierarchyWorldMatrixAttr() const;

    //! Create or get the existing Fabric Hierarchy world matrix attribute.
    //!
    //! @param defaultValue The value to set when creating the world matrix attribute in Fabric
    UsdAttribute CreateFabricHierarchyWorldMatrixAttr(const GfMatrix4d& defaultValue = GfMatrix4d(1)) const;

    //! World Position is the absolute, world-space translation of the
    //! prim. If this attribute is set in Fabric, OmniHydra will disregard all other
    //! transform data for this prim and use this and any other world transform
    //! attributes in Fabric for the Hydra rprim.
    //!
    //! | ||
    //! | -- | -- |
    //! | C++ Type | GfVec3d |
    //! | ValueTypeName | Double3 |
    UsdAttribute GetWorldPositionAttr() const;

    //! Create or get the existing world position attribute.
    //!
    //! @param defaultValue The value to set when creating the world position attribute in Fabric
    UsdAttribute CreateWorldPositionAttr(const GfVec3d& defaultValue = GfVec3d(0)) const;

    //! World Orientation is the absolute, world-space rotation of the
    //! prim. If this attribute is set in Fabric, OmniHydra will disregard all other
    //! transform data for this prim and use this and any other world transform
    //! attributes in Fabric for the Hydra rprim.
    //!
    //! | ||
    //! | -- | -- |
    //! | C++ Type | GfQuatf |
    //! | ValueTypeName | Quatf |
    UsdAttribute GetWorldOrientationAttr() const;

    //! Create or get the existing world orientation attribute.
    //!
    //! @param defaultValue The value to set when creating the world orientation attribute in Fabric
    UsdAttribute CreateWorldOrientationAttr(const GfQuatf& defaultValue = GfQuatf(1)) const;

    //! World Scale is the absolute, world-space scale of the
    //! prim. If this attribute is set in Fabric, OmniHydra will disregard all other
    //! transform data for this prim and use this and any other world transform
    //! attributes in Fabric for the Hydra rprim.
    //!
    //! | ||
    //! | -- | -- |
    //! | C++ Type | GfVec3f |
    //! | ValueTypeName | Vector3f |
    UsdAttribute GetWorldScaleAttr() const;

    //! Create or get the existing world scale attribute.
    //!
    //! @param defaultValue The value to set when creating the world scale attribute in Fabric
    UsdAttribute CreateWorldScaleAttr(const GfVec3f& defaultValue = GfVec3f(1)) const;

    //! Local Matrix is the local transform of the prim, relative to its parent.
    //! Updates to ancestor transforms will continue to affect the overall
    //! transform of this prim in OmniHydra.
    //! If this attribute is set in Fabric, OmniHydra will disregard any
    //! local transform data for this prim in USD.
    //! If any world transform attributes are set for the prim in Fabric,
    //! this attribute will be ignored by OmniHydra.
    //!
    //! | ||
    //! | -- | -- |
    //! | C++ Type | GfMatrix4d |
    //! | ValueTypeName | Matrix4d |
    UsdAttribute GetLocalMatrixAttr() const;

    //! Create or get the existing local matrix attribute.
    //!
    //! @param defaultValue The value to set when creating the local matrix attribute in Fabric
    UsdAttribute CreateLocalMatrixAttr(const GfMatrix4d& defaultValue = GfMatrix4d(1)) const;

    //! Check if the Fabric prim has any world transform attributes
    //!
    //! @returns true if any world transform attributes exist in Fabric
    bool HasWorldXform() const;

    //! Remove any world transform attributes from the Fabric prim
    //!
    //! @returns true if any world transform attributes existed and were removed
    bool ClearWorldXform();

    //! Set the world position, orientation, and scale from the underlying USD prim
    //!
    //! @returns true if all world transform attributes were created and set or updated from USD
    bool SetWorldXformFromUsd();

    //! Check if the Fabric prim has the local transform attribute set
    //!
    //! @returns true if the local transform attribute exists in Fabric
    bool HasLocalXform() const;

    //! Remove the local transform attribute from the Fabric prim
    //!
    //! @returns true if the local transform attribute existed and was removed
    bool ClearLocalXform();

    //! Set the local transform attribute in Fabric from the underlying USD prim's local transform
    //! relative to its parent.
    //!
    //! @returns true if the local transform attribute was created and set or updated from USD
    bool SetLocalXformFromUsd() const;

protected:
    UsdPrim m_prim;
};

inline RtXformable::RtXformable(const UsdPrim& prim) : m_prim(prim)
{
}

inline RtXformable::operator bool() const
{
    return m_prim.IsValid();
}

inline UsdPrim RtXformable::GetPrim() const
{
    return m_prim;
}

inline SdfPath RtXformable::GetPath() const
{
    return m_prim.GetPath();
}

inline UsdAttribute RtXformable::GetWorldPositionAttr() const
{
    return m_prim.GetAttribute(RtTokens->worldPosition);
}

inline UsdAttribute RtXformable::CreateWorldPositionAttr(const GfVec3d& defaultValue) const
{
    UsdAttribute created = m_prim.CreateAttribute(RtTokens->worldPosition, SdfValueTypeNames->Double3);
    created.Set(defaultValue);
    return created;
}

inline UsdAttribute RtXformable::GetWorldOrientationAttr() const
{
    return m_prim.GetAttribute(RtTokens->worldOrientation);
}

inline UsdAttribute RtXformable::CreateWorldOrientationAttr(const GfQuatf& defaultValue) const
{
    UsdAttribute created = m_prim.CreateAttribute(RtTokens->worldOrientation, SdfValueTypeNames->Quatf);
    created.Set(defaultValue);
    return created;
}

inline UsdAttribute RtXformable::GetWorldScaleAttr() const
{
    return m_prim.GetAttribute(RtTokens->worldScale);
}

inline UsdAttribute RtXformable::CreateWorldScaleAttr(const GfVec3f& defaultValue) const
{
    // Note, Fabric and OmniHydra expect this to have a "vector" role, so the correct type is vec3f.
    // I don't know the history of this.
    UsdAttribute created = m_prim.CreateAttribute(RtTokens->worldScale, SdfValueTypeNames->Vector3f);
    created.Set(defaultValue);
    return created;
}

inline UsdAttribute RtXformable::GetLocalMatrixAttr() const
{
    return m_prim.GetAttribute(RtTokens->localMatrix);
}

inline UsdAttribute RtXformable::CreateLocalMatrixAttr(const GfMatrix4d& defaultValue) const
{
    UsdAttribute created = m_prim.CreateAttribute(RtTokens->localMatrix, SdfValueTypeNames->Matrix4d);
    created.Set(defaultValue);
    return created;
}

inline bool RtXformable::HasWorldXform() const
{
    return GetWorldPositionAttr().IsValid() || GetWorldOrientationAttr().IsValid() || GetWorldScaleAttr().IsValid();
}

inline bool RtXformable::ClearWorldXform()
{
    UsdAttribute worldPos = GetWorldPositionAttr();
    UsdAttribute worldOr = GetWorldOrientationAttr();
    UsdAttribute worldScale = GetWorldScaleAttr();

    bool result = false;

    if (worldPos.IsValid())
    {
        result |= m_prim.RemoveProperty(RtTokens->worldPosition);
    }

    if (worldOr.IsValid())
    {
        result |= m_prim.RemoveProperty(RtTokens->worldOrientation);
    }

    if (worldScale.IsValid())
    {
        result |= m_prim.RemoveProperty(RtTokens->worldScale);
    }

    return result;
}

inline bool RtXformable::SetWorldXformFromUsd()
{
    auto iXform = omni::core::createType<usdrt::IRtXformable>();
    if (!iXform)
    {
        return false;
    }

    return iXform->setWorldXformFromUsd(m_prim.m_prim);
}

inline bool RtXformable::HasLocalXform() const
{
    return GetLocalMatrixAttr().IsValid();
}

inline bool RtXformable::ClearLocalXform()
{
    if (HasLocalXform())
    {
        return m_prim.RemoveProperty(RtTokens->localMatrix);
    }

    return false;
}

inline bool RtXformable::SetLocalXformFromUsd() const
{
    auto iXform = omni::core::createType<usdrt::IRtXformable>();
    if (!iXform)
    {
        return false;
    }

    return iXform->setLocalXformFromUsd(m_prim.m_prim);
}

inline UsdAttribute RtXformable::GetFabricHierarchyLocalMatrixAttr() const
{
    return m_prim.GetAttribute(RtTokens->fabricHierarchyLocalMatrix);
}

inline UsdAttribute RtXformable::CreateFabricHierarchyLocalMatrixAttr(const GfMatrix4d& defaultValue) const
{
    UsdAttribute created = m_prim.CreateAttribute(RtTokens->fabricHierarchyLocalMatrix, SdfValueTypeNames->Matrix4d);
    created.Set(defaultValue);
    return created;
}

inline UsdAttribute RtXformable::GetFabricHierarchyWorldMatrixAttr() const
{
    return m_prim.GetAttribute(RtTokens->fabricHierarchyWorldMatrix);
}

inline UsdAttribute RtXformable::CreateFabricHierarchyWorldMatrixAttr(const GfMatrix4d& defaultValue) const
{
    auto iFabricHierarchy = omni::core::createType<usdrt::hierarchy::IFabricHierarchy>();
    bool worldXformTrackingPaused = false;
    if (!m_prim.HasAttribute(RtTokens->fabricHierarchyWorldMatrix) && iFabricHierarchy)
    {
        iFabricHierarchy =
            iFabricHierarchy->getFabricHierarchy(m_prim.GetStage()->GetFabricId(), m_prim.GetStage()->GetStageId());
        if (iFabricHierarchy)
        {
            // Don't record changes on worldMatrix during its creation
            iFabricHierarchy->trackWorldXformChanges(false);
            worldXformTrackingPaused = true;
        }
    }

    UsdAttribute created = m_prim.CreateAttribute(RtTokens->fabricHierarchyWorldMatrix, SdfValueTypeNames->Matrix4d);
    created.Set(defaultValue);

    if (iFabricHierarchy && worldXformTrackingPaused)
    {
        iFabricHierarchy->trackWorldXformChanges(true);
    }

    return created;
}

} // namespace usdrt
