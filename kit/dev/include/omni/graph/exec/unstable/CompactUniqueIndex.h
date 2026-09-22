// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file CompactUniqueIndex.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::CompactUniqueIndex.
#pragma once

#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/Types.h>

#include <vector>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Registry of unique indexes with recycling of released indexes.
//!
//! Call @ref acquireUniqueIndex() to retrieve a unique index.  Indexes are "compact", meaning abandoned indices will be
//! reused. This means that if @ref releaseUniqueIndex() is called with a value of 6, the next call to @ref
//! acquireUniqueIndex() will return 6.
//!
//! This class is useful for assigning a stable unique index to a set of dynamic items.
//!
//! @thread_safety Methods are not thread safe unless otherwise stated.
//!
//! This object is not ABI-safe.
class CompactUniqueIndex
{
public:
    //! Invalid index is used when no free indexes are available, and as well
    //! as a value for reserved elements of the allocation array (an implementation detail)
    enum : std::size_t
    {
        kInvalidIndex = kInvalidNodeIndexInTopology
    };

    //! Constructor
    CompactUniqueIndex() noexcept = default;

    //! Destructor
    ~CompactUniqueIndex() noexcept = default;

    //! Returns a unique index.
    //!
    //! If @ref releaseUniqueIndex() was previously called, the value passed to it will be returned (i.e. the index will
    //! be recycled). Otherwise, a new index is allocated that is one greater than the current max index.
    //!
    //! @thread_safety This method is not thread safe.
    inline std::size_t acquireUniqueIndex() noexcept;

    //! Marks an index as no longer used.
    //!
    //! A subsequent call to @ref acquireUniqueIndex() will prefer reusing the index given to this method.
    //!
    //! If @p indexToFree was not previously returned by @ref acquireUniqueIndex, undefined behavior will result.
    //!
    //! @thread_safety This method is not thread safe.
    inline void releaseUniqueIndex(std::size_t indexToFree) noexcept;

    //! Returns the size of the registry.
    //!
    //! The maximum number of indices is returned, not the current number of "active" indices.  Said differently, if
    //! @ref acquireUniqueIndex() is called followed by @ref releaseUniqueIndex(), @ref size() would return 1 not 0.
    //!
    //! @thread_safety This method is not thread safe.
    std::size_t size() const noexcept
    {
        return m_allocatedIndexes.size();
    }

private:
    //! Index registry. Holds acquired and released indexes.
    std::vector<std::size_t> m_allocatedIndexes;

    //! All released indexes will form a list and m_lastFree points to the last released / first item of the list.
    std::size_t m_lastFree{ kInvalidIndex };
};

inline std::size_t CompactUniqueIndex::acquireUniqueIndex() noexcept
{
    // no free index to recycle, allocate a new one
    if (m_lastFree == kInvalidIndex)
    {
        m_allocatedIndexes.emplace_back(kInvalidIndex); // may throw
        OMNI_GRAPH_EXEC_ASSERT(m_allocatedIndexes.size() > 0);
        return m_allocatedIndexes.size() - 1;
    }
    else // recycle existing index
    {
        OMNI_GRAPH_EXEC_ASSERT(m_lastFree < m_allocatedIndexes.size());
        std::size_t recycledIndex = m_lastFree;
        m_lastFree = m_allocatedIndexes[recycledIndex];
        m_allocatedIndexes[recycledIndex] = kInvalidIndex;
        return recycledIndex;
    }
}

inline void CompactUniqueIndex::releaseUniqueIndex(std::size_t indexToFree) noexcept
{
    OMNI_GRAPH_EXEC_ASSERT(indexToFree < m_allocatedIndexes.size());
    OMNI_GRAPH_EXEC_ASSERT(m_allocatedIndexes[indexToFree] == kInvalidIndex);
    if (indexToFree < m_allocatedIndexes.size() && m_allocatedIndexes[indexToFree] == kInvalidIndex)
    {
        if (m_lastFree == kInvalidIndex)
            m_lastFree = indexToFree;
        else
        {
            m_allocatedIndexes[indexToFree] = m_lastFree;
            m_lastFree = indexToFree;
        }
    }
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
