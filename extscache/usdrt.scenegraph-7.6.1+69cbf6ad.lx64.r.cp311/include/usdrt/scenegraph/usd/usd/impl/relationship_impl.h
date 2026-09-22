// Copyright (c) 2021-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "usd_decl.h"

namespace usdrt
{

inline bool UsdRelationship::AddTarget(const SdfPath& target, UsdListPosition position) const
{
    if (!m_relationship)
    {
        return false;
    }

    union
    {
        UsdListPosition wrapper;
        ListPosition iface;
    };

    wrapper = position;

    return m_relationship->addTarget(omni::fabric::PathC(target), iface);
}

inline bool UsdRelationship::RemoveTarget(const SdfPath& target) const
{
    if (!m_relationship)
    {
        return false;
    }

    return m_relationship->removeTarget(omni::fabric::PathC(target));
}

inline bool UsdRelationship::SetTargets(const SdfPathVector& targets) const
{
    if (!m_relationship)
    {
        return false;
    }

    std::vector<omni::fabric::PathC> targetsC;
    targetsC.reserve(targets.size());
    for (const SdfPath& target : targets)
    {
        targetsC.push_back(omni::fabric::PathC(target));
    }

    return m_relationship->setTargets(targetsC.data(), (uint32_t)targetsC.size());
}

inline bool UsdRelationship::ClearTargets(bool removeSpec) const
{
    if (!m_relationship)
    {
        return false;
    }

    return m_relationship->clearTargets();
}

inline bool UsdRelationship::GetTargets(SdfPathVector* targets) const
{
    if (!m_relationship)
    {
        return false;
    }

    const uint32_t numTargets = m_relationship->numTargets();

    if (numTargets == 0)
    {
        targets->resize(0);
        return true;
    }

    std::vector<omni::fabric::PathC> targetsC(numTargets);
    const bool result = m_relationship->getTargets(targetsC.data(), numTargets);

    targets->resize(numTargets);
    for (size_t i = 0; i < numTargets; ++i)
    {
        (*targets)[i] = SdfPath(omni::fabric::Path(targetsC[i]));
    }

    return result;
}

inline bool UsdRelationship::GetForwardedTargets(SdfPathVector* targets) const
{
    if (!m_relationship)
    {
        return false;
    }

    // Note: I don't think Fabric resolves forwarded targets,
    // so we don't either for now
    return GetTargets(targets);
}

inline bool UsdRelationship::HasAuthoredTargets() const
{
    if (!m_relationship)
    {
        return false;
    }

    return m_relationship->hasAuthoredTargets();
}

// UsdObject methods
inline bool UsdRelationship::IsValid() const
{
    if (!m_relationship)
    {
        return false;
    }

    return m_relationship->isValid();
}

inline UsdStageRefPtr UsdRelationship::GetStage() const
{
    if (!m_relationship)
    {
        return UsdStageRefPtr{ nullptr };
    }

    UsdStageRefPtr stage(new UsdStage{ m_relationship->getStage() });
    return stage;
}

inline UsdPrim UsdRelationship::GetPrim() const
{
    if (!m_relationship)
    {
        return UsdPrim{ nullptr };
    }

    return UsdPrim{ m_relationship->getPrim() };
}

inline const TfToken UsdRelationship::GetName() const
{
    if (!m_relationship)
    {
        return TfToken();
    }

    return TfToken(m_relationship->getName());
}

inline SdfPath UsdRelationship::GetPath() const
{
    if (!m_relationship)
    {
        return SdfPath();
    }

    return SdfPath(m_relationship->getPath());
}

inline const SdfPath UsdRelationship::GetPrimPath() const
{
    if (!m_relationship)
    {
        return SdfPath();
    }

    return SdfPath(m_relationship->getPrimPath());
}

// UsdProperty methods
inline TfToken UsdRelationship::GetBaseName() const
{
    if (!m_relationship)
    {
        return TfToken();
    }

    return TfToken(m_relationship->getBaseName()->getBuffer());
}

inline TfToken UsdRelationship::GetNamespace() const
{
    if (!m_relationship)
    {
        return TfToken();
    }

    return TfToken(m_relationship->getNamespace()->getBuffer());
}

inline std::vector<std::string> UsdRelationship::SplitName() const
{
    if (!m_relationship)
    {
        return std::vector<std::string>();
    }

    return m_relationship->splitName();
}

inline UsdRelationship::operator bool() const
{
    return IsValid();
}


static_assert(std::is_standard_layout<UsdRelationship>::value, "UsdRelationship must be standard layout");


} // namespace usdrt
