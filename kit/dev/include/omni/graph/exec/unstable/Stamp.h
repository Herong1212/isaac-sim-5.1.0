// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file Stamp.h
//!
//! @brief Defines omni::graph::exec::unstable::Stamp class.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>

#include <limits>
#include <string>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Low-level ABI type to represent @ref Stamp.
using Stamp_abi = int16_t;

//! Lazy, light-weight change notification system.
//!
//! The heart of the EF's invalidation system is @ref Stamp and @ref SyncStamp.
//!
//! Stamps track the state/version of a resource.  Stamps are implemented as an unsigned number.  If the state of a
//! resource changes, the stamp is incremented.
//!
//! Stamps are broken into two parts.
//!
//! The first part is implemented by the @ref Stamp class.  As a resource changes, @ref Stamp::next()| s called to
//! denote the new state of the resource.  @ref Stamp objects are owned by the resource they track.
//!
//! The second part of stamps is implemented by the @ref SyncStamp class.  @ref SyncStamp tracks/synchronizes to the
//! state of a @ref Stamp.  @ref SyncStamp objects are owned by the entities that wish to utilize the mutating resource.
//!
//! For example, consider the following example showing how a consumer of a resource can uses stamps to detect when a
//! resource has changed and update cached data:
//!
#ifdef OMNI_GRAPH_EXEC_DOC_BUILD
//! @snippet "../tests.cpp/TestStamp.cpp" ef-docs-stamp-example
#endif
//!
//! By default constructed @ref Stamp and @ref SyncStamp are never in sync, meaning reconstruction will always happen at
//! least once.
//!
//! Stamps are a lazy, light-weight alternative to heavier change notification systems such as callbacks.
//!
//! Stamps use unsigned numbers to detect changes in the tracked resource, relying on overflow behavior to wrap the
//! unsigned number.  A check for @ref Stamp::kInvalidStamp is performed during this overflow.
//!
//! Because of the limited bit depth of @ref Stamp, it is possible, though improbable, that a resource at stamp *X*,
//! wraps all the way back to *X* before a @ref SyncStamp tries to synchronize with the stamp.  In such a case, the @ref
//! SyncStamp will erroneously believe it is in sync with the resource.  Again, this is unlikely, though possible.
//!
//! EF makes extensive use of stamps to detect changes in pass registration, graph topology, and graph construction. See
//! @rstref{Graph Invalidation <ef_graph_invalidation>} to understand how @ref Stamp is used for invalidation in EF.
//!
//! This object is ABI-safe and can be passed by pointer or value through the ABI.
class Stamp
{
public:
    //! Anonymous structure to define kInvalidStamp.
    enum : Stamp_abi
    {
        kInvalidStamp = -1 //!< Value for an invalid stamp.
    };

    //! Bump the stamp
    void next() noexcept
    {
        // depending on usage, we may have to turn this into atomic operator
        // for now we don't expect this to be needed
        m_generation = (m_generation == std::numeric_limits<decltype(m_generation)>::max()) ? 0 : m_generation + 1;

        static_assert(CARB_OFFSETOF2(Stamp, m_generation) == 0, "unexpected offset");
    }

    //! Make stamp invalid
    void invalidate() noexcept
    {
        m_generation = kInvalidStamp;
    }

    //! Check if stamp is valid
    bool isValid() const noexcept
    {
        return m_generation != Stamp::kInvalidStamp;
    }

    //! Equal operator
    bool operator==(const Stamp& rhs) const noexcept
    {
        return (m_generation == rhs.m_generation);
    }

    //! Not equal operator
    bool operator!=(const Stamp& rhs) const noexcept
    {
        return (m_generation != rhs.m_generation);
    }

    //! Convert to string for debugging
    std::string toString() const noexcept
    {
        std::string str;
        if (isValid())
        {
            str = std::to_string(m_generation); // may throw
        }
        else
        {
            str = "INV";
        }

        return str;
    }

private:
    Stamp_abi m_generation{ kInvalidStamp }; //!< Stamp storage
    friend class SyncStamp;
};

#ifndef DOXYGEN_BUILD // macros called in namespaces seem to upset doxygen
OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI(Stamp);
static_assert(2 == sizeof(Stamp), "Stamp is an unexpected size");
#endif

//! Watcher of a mutating resource.  Observes a resources @ref Stamp and detects if it has changed.
//!
//! Used always in pair with @ref Stamp class to detect changes in a resource.  See @ref Stamp's docs for an explanation
//! on how this object is used during invalidation.
//!
//! This object is ABI-safe and can be passed by pointer or value through the ABI.  However, it is more common to pass
//! @ref Stamp through the ABI rather than this object.
class SyncStamp
{
public:
    enum
    {
        kInvalidStamp = Stamp::kInvalidStamp - 1
    };

    //! Constructor
    SyncStamp() noexcept = default;

    //! Construct in sync with given stamp
    SyncStamp(Stamp id) noexcept : m_syncStamp(id.m_generation)
    {
        static_assert(CARB_OFFSETOF2(SyncStamp, m_syncStamp) == 0, "unexpected offset");
    }

    //! Check if two classes are in sync. Always return false if this instance is having invalid stamp stored.
    bool inSync(const Stamp& id) const noexcept
    {
        if (m_syncStamp == SyncStamp::kInvalidStamp)
            return false;
        return (m_syncStamp == id.m_generation);
    }

    //! Check if two sync stamp are in sync
    bool inSync(const SyncStamp& syncStamp) const noexcept
    {
        return (m_syncStamp == syncStamp.m_syncStamp);
    }

    //! Synchronize this instance with given stamp
    void sync(const Stamp& id) noexcept
    {
        m_syncStamp = id.m_generation;
    }

    //! Synchronize this instance with given sync stamp
    void sync(const SyncStamp& syncStamp) noexcept
    {
        m_syncStamp = syncStamp.m_syncStamp;
    }

    //! In one call test and synchronize the stamp. After this call this instance is guaranteed to be in sync with
    //! given id.
    //!
    //! @return False if stamps were in sync and true otherwise.
    bool makeSync(const Stamp& id) noexcept
    {
        if (inSync(id))
            return false;

        sync(id);
        return true;
    }

    //! Is this sync stamp valid
    bool isValid() const noexcept
    {
        return m_syncStamp != SyncStamp::kInvalidStamp;
    }

    //! Invalidate stored stamp
    void invalidate() noexcept
    {
        m_syncStamp = SyncStamp::kInvalidStamp;
    }

    //! Explicit call to convert to Stamp class
    Stamp toStamp() const noexcept
    {
        Stamp id;
        if (isValid())
            id.m_generation = m_syncStamp;

        return id;
    }

    //! Convert to string for debugging
    std::string toString() const noexcept
    {
        std::string str;
        if (isValid())
        {
            str = std::to_string(m_syncStamp); // may throw
        }
        else
        {
            str = "INV";
        }

        return str;
    }

private:
    Stamp_abi m_syncStamp{ kInvalidStamp }; //!< Stamp storage
};

#ifndef DOXYGEN_BUILD // macros called in namespaces seem to upset doxygen
OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI(SyncStamp);
static_assert(2 == sizeof(SyncStamp), "SyncStamp is an unexpected size");
#endif

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
