// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ElementAt.h
//!
//! @brief Defines helper classes to access iteratable items via an ABI.
#pragma once

#include <cstdint>
#include <iterator>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{
namespace detail
{

//! Provides iterator access to an interface that defines per-element access.
//!
//! Use this object to wrap an interface that defines random element access.  The resulting wrapper object can be passed
//! to any algorithm that can iterate over an iterable object (e.g. C++'s built-in range-based `for`).
//!
//! @tparam OwnerType The interface type (e.g. `IMyArray`).
//!
//! @tparam ValueType The type of the value returned from the getter.
//!
//! @tparam GetterType A struct that defines a static `getAt(OwnerType* owner, uint64_t index, ValueType* out)` method.
//!                    This method is used to access the element at the given index.  The struct must also define a
//!                    static `getCount(OwnerType*)` method which returns the number of items to iterate over.
template <typename OwnerType, typename ValueType, typename GetterType>
struct ElementAt
{
    //! Iterator pointing to an element in the iterable range.
    struct Iterator
    {
        //! Type of the iterator
        using iterator_category = std::forward_iterator_tag;

        //! Type of the value to which the iterator points.
        using value_type = ValueType;

        //! Pointer to the type of the value to which the iterator points.
        using pointer = value_type*;

        //! Reference to the type of the value to which the iterator  points.
        using reference = value_type&;

        //! Constructor.
        Iterator(OwnerType* owner_, uint64_t index_, uint64_t count_) noexcept
            : m_owner(owner_), m_index(index_), m_count(count_)
        {
            _get();
        }

        //! Dereference operator.
        reference operator*() noexcept
        {
            return m_element;
        }

        //! Dereference operator.
        pointer operator->() noexcept
        {
            return &m_element;
        }

        //! Move to the next item in the container.
        Iterator& operator++() noexcept
        {
            m_index++;
            _get();
            return *this;
        }

        //! Move to the next item in the container.
        Iterator operator++(int) noexcept
        {
            Iterator tmp = *this;
            ++(*this);
            return tmp;
        }

        //! Check if the iterators are equal.
        friend bool operator==(const Iterator& a, const Iterator& b) noexcept
        {
            return ((a.m_owner == b.m_owner) && (a.m_index == b.m_index));
        };

        //! Check if the iterators are not equal.
        friend bool operator!=(const Iterator& a, const Iterator& b) noexcept
        {
            return ((a.m_owner != b.m_owner) || (a.m_index != b.m_index));
        };

    private:
        void _get()
        {
            if (m_index < m_count)
            {
                GetterType::getAt(m_owner, m_index, &m_element);
            }
        }

        OwnerType* m_owner;
        ValueType m_element;
        uint64_t m_index;
        uint64_t m_count;
    };

    //! Constructor
    ElementAt(OwnerType* owner) noexcept : m_owner(owner)
    {
    }

    //! Returns an iterator to the first element.
    Iterator begin() const noexcept
    {
        return Iterator(m_owner, 0, GetterType::getCount(m_owner));
    }

    //! Returns an invalid iterator past the last element.
    Iterator end() const noexcept
    {
        auto count = GetterType::getCount(m_owner);
        return Iterator(m_owner, count, count);
    }

    //! Returns element count
    uint64_t getCount() const noexcept
    {
        return GetterType::getCount(m_owner);
    }

private:
    OwnerType* m_owner;
};

} // namespace detail
} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
