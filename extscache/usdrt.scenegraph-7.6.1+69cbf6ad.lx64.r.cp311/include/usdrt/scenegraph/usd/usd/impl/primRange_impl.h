// Copyright (c) 2021-2023, NVIDIA CORPORATION. All rights reserved.
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

inline UsdPrimRange::iterator::iterator()
{
    m_primRange = nullptr;
    m_startPrim = UsdPrim{ nullptr };
    m_currentPrim = UsdPrim{ nullptr };
    m_atEnd = true;
}

inline UsdPrimRange::iterator::iterator(omni::core::ObjectPtr<usdrt::IRtPrimRange> primRange)
{
    m_primRange = primRange;
    m_startPrim = UsdPrim{ m_primRange->get() };
    m_currentPrim = m_startPrim;
    m_atEnd = false;
}

inline void UsdPrimRange::iterator::PruneChildren()
{
    m_primRange->pruneChildren();
}

inline UsdPrimRange::iterator::reference UsdPrimRange::iterator::operator*()
{
    return m_currentPrim;
}

inline UsdPrimRange::iterator::pointer UsdPrimRange::iterator::operator->()
{
    return &m_currentPrim;
}

inline UsdPrimRange::iterator& UsdPrimRange::iterator::operator++()
{
    if (m_primRange->next())
    {
        // iterator is not at the end yet
        m_currentPrim = UsdPrim{ m_primRange->get() };
    }
    else
    {
        m_atEnd = true;
    }

    return *this;
}

inline UsdPrimRange::iterator UsdPrimRange::iterator::operator++(int)
{
    iterator tmp = *this;
    ++(*this);
    return tmp;
}

inline bool operator==(const UsdPrimRange::iterator& lhs, const UsdPrimRange::iterator& rhs)
{
    const bool lValid = lhs.m_currentPrim.IsValid();
    const bool rValid = rhs.m_currentPrim.IsValid();

    if (!lValid && !rValid)
    {
        // two invalid current prims is a match
        return true;
    }
    if (lhs.m_atEnd && rhs.m_atEnd)
    {
        return true;
    }
    if (lValid && rValid)
    {
        if (lhs.m_startPrim.GetPath() != rhs.m_startPrim.GetPath())
        {
            return false;
        }
        // TODO need to account for post-visit iterators once that support is added here
        return lhs.m_currentPrim.GetPath() == rhs.m_currentPrim.GetPath();
    }

    return false;
}

inline bool operator!=(const UsdPrimRange::iterator& lhs, const UsdPrimRange::iterator& rhs)
{
    return !(lhs == rhs);
};

inline UsdPrimRange::UsdPrimRange(const UsdPrim& start) : m_startPrim(start)
{
}

inline UsdPrimRange::iterator UsdPrimRange::begin() const
{
    if (!m_startPrim.IsValid())
    {
        return UsdPrimRange::iterator();
    }

    return UsdPrimRange::iterator(omni::core::createType<usdrt::IRtPrimRange>()->create(m_startPrim.m_prim));
}

inline UsdPrimRange::iterator UsdPrimRange::end() const
{
    return UsdPrimRange::iterator();
}

inline bool UsdPrimRange::empty() const
{
    if (!m_startPrim.IsValid())
    {
        return true;
    }

    return begin() == end();
}

inline UsdPrimRange::operator bool() const
{
    return !empty();
}

} // namespace usdrt
