// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <carb/Memory.h>

#include <omni/graph/exec/unstable/Assert.h>

#include <cstdint>
#include <cstring>
#include <type_traits>
#include <utility>

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

//! ABI-aware stack with inline memory to avoid heap allocation.
//!
//! Reserved memory within the stack will be used until it is exceeded, at which heap memory will be used.
//!
//! It is assumed the items stored are `sizeof(uint64_t)`.
//!
//! This class can safely be passed by pointer across the ABI.  However, since it is not a trivial type, it cannot be
//! passed by value across the ABI. See @ref OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI for details.
template <typename T = uint64_t>
class SmallStack
{
public:
    //! Type of the item in the stack.
    using ItemType = T;

    //! Constructor.
    SmallStack() noexcept
    {
        static_assert(8 == sizeof(ItemType), "unexpected item size");
        static_assert(std::is_trivially_destructible<ItemType>::value, "items stored must be trivially destructible");
        static_assert(CARB_OFFSETOF2(SmallStack, m_external.data) == 0, "unexpected external data offset");
        static_assert(CARB_OFFSETOF2(SmallStack, m_external.count) == 8, "unexpected external count offset");
        static_assert(CARB_OFFSETOF2(SmallStack, m_external.maxCount) == 12, "unexpected external maxCount offset");

        static_assert(CARB_OFFSETOF2(SmallStack, m_internal.data) == 0, "unexpected data offset");
        static_assert(CARB_OFFSETOF2(SmallStack, m_internal.count) == 56, "unexpected count offset");
        static_assert(CARB_OFFSETOF2(SmallStack, m_internal.isInternal) == 60, "unexpected internal flag offset ");

        static_assert(sizeof(SmallStack<T>) == 64, "SmallStack has unexpected size");
        OMNI_STATIC_ASSERT_MUST_BE_PASSED_BY_POINTER_IN_ABI(SmallStack<T>);

        m_internal.count = 0;
        m_internal.isInternal = 1;
    }

    //! Constructor with a single item.
    SmallStack(ItemType item) noexcept
    {
        m_internal.count = 0;
        m_internal.isInternal = 1;
        push(item); // may throw, but wont in this case.
    }

    //! Copy constructor.
    SmallStack(const SmallStack& other) noexcept
    {
        m_internal.isInternal = 1;
        _copy(other);
    }

    //! Construct from a range.
    //!
    //! @p end must be equal or greater than @p begin.
    SmallStack(ItemType* begin, ItemType* end) noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(end >= begin);
        m_internal.isInternal = 1;
        uint32_t count = static_cast<uint32_t>(end - begin);
        _copy(begin, count, count);
    }

    //! Copies the contents of the given stack and pushes the given item.
    SmallStack(const SmallStack& other, ItemType item) noexcept
    {
        uint32_t otherCount = other.count();
        uint32_t count = otherCount + 1;
        ItemType* p;
        if (count > kMaxInternalDataItemCount)
        {
            p = _allocate(count);
            m_internal.isInternal = 0;
            m_external.data = p;
            m_external.count = count;
            m_external.maxCount = count;
        }
        else
        {
            m_internal.isInternal = 1;
            p = m_internal.data;
            m_internal.count = count;
        }

        std::memcpy(p, other.begin(), sizeof(ItemType) * otherCount);
        p[otherCount] = item;
    }

    //! Move constructor.
    SmallStack(SmallStack&& other) noexcept
    {
        m_internal.isInternal = 1;
        _move(std::move(other));
    }

    //! Destructor
    ~SmallStack() noexcept
    {
        _free();
    }

    //! Assignment operator.
    SmallStack& operator=(const SmallStack& other) noexcept
    {
        if (this != &other)
        {
            _copy(other);
        }

        return *this;
    }

    //! Assignment operator.
    SmallStack& operator=(SmallStack&& other) noexcept
    {
        if (this != &other)
        {
            _move(std::move(other));
        }

        return *this;
    }

    //! Compares two stacks, returning either a negative number, positive number, or zero.
    //!
    //! Works similar to @c std::memcmp.
    //!
    //! Returns a negative value if this stack less than @p other.
    //!
    //! Returns a positive value if this stack greater than @p other.
    //!
    //! Returns zero if the stacks are equal.
    //!
    //! The returned negative or positive values are not guaranteed to be exactly -1 or 1.
    int compare(const SmallStack& other) const noexcept
    {
        int thisCount = count();
        int otherCount = other.count();
        if (thisCount == otherCount)
        {
            return std::memcmp(begin(), other.begin(), sizeof(ItemType) * otherCount);
        }
        else
        {
            return (thisCount - otherCount);
        }
    }

    //! Return @c true if the stack is empty.
    inline bool empty() const noexcept
    {
        return (0 == count());
    }

    //! Returns the top of the stack.
    //!
    //! Reading the top of an empty stack is undefined behavior.
    inline ItemType top() const noexcept
    {
        if (_isInternal())
        {
            OMNI_GRAPH_EXEC_ASSERT(0 != m_internal.count);
            return m_internal.data[m_internal.count - 1];
        }
        else
        {
            OMNI_GRAPH_EXEC_ASSERT(0 != m_external.count);
            return m_external.data[m_external.count - 1];
        }
    }

    //! Push the given item to the top of the stack.
    inline void push(ItemType elem) noexcept
    {
        if (_isInternal())
        {
            if (m_internal.count == kMaxInternalDataItemCount)
            {
                // we've ran out of internal space
                _allocExternalAndCopyInternal();
                m_external.data[m_external.count++] = elem;
            }
            else
            {
                m_internal.data[m_internal.count++] = elem;
            }
        }
        else
        {
            if (m_external.count == m_external.maxCount)
            {
                _grow();
            }

            m_external.data[m_external.count++] = elem;
        }
    }

    //! Removes the top of the stack.
    //!
    //! Popping an empty stack is undefined behavior.
    inline void pop() noexcept
    {
        if (_isInternal())
        {
            OMNI_GRAPH_EXEC_ASSERT(m_internal.count > 0);
            m_internal.count--;
        }
        else
        {
            OMNI_GRAPH_EXEC_ASSERT(m_external.count > 0);
            m_external.count--;
        }
    }

    //! Returns the number of items in the stack.
    inline uint32_t count() const noexcept
    {
        if (_isInternal())
        {
            return m_internal.count;
        }
        else
        {
            return m_external.count;
        }
    }

    //! Returns the number of items in the stack.
    inline uint32_t size() const noexcept
    {
        return count();
    }

    //! Returns a pointer to the oldest item in the stack.
    //!
    //! If the stack is empty, the returned pointer should not be read or written though can be compared to @ref end().
    inline const ItemType* begin() const noexcept
    {
        if (_isInternal())
        {
            return m_internal.data;
        }
        else
        {
            return m_external.data;
        }
    }

    //! Returns a pointer to one past the top of the stack.
    //!
    //! If the stack is empty, the returned pointer should not be read or written though can be compared to @ref
    //! begin().
    inline const ItemType* end() const noexcept
    {
        if (_isInternal())
        {
            return m_internal.data + m_internal.count;
        }
        else
        {
            return m_external.data + m_external.count;
        }
    }

    //! Returns a pointer to the oldest item in the stack.
    //!
    //! Result are undefined if the stack is empty.
    inline const ItemType* data() const noexcept
    {
        return begin();
    }

private:
    inline bool _isInternal() const noexcept
    {
        return m_internal.isInternal;
    }

    inline uint32_t _maxCount() const noexcept
    {
        if (_isInternal())
        {
            return kMaxInternalDataItemCount;
        }
        else
        {
            return m_external.maxCount;
        }
    }

    inline void _free() noexcept
    {
        if (!_isInternal())
        {
            carb::deallocate(m_external.data);

            m_internal.count = 0;
            m_internal.isInternal = 0;
        }
    }

    // assumes _free() has already been called (when needed)
    inline void _copy(const SmallStack& other) noexcept
    {
        _copy(const_cast<ItemType*>(other.begin()), other.count(), other._maxCount());
    }

    // assumes _free() has already been called (when needed)
    inline void _copy(ItemType* data, uint32_t count, uint32_t maxCount) noexcept
    {
        if (_maxCount() < count)
        {
            // not enough storage for the copy.  we'll have to allocate more.
            OMNI_GRAPH_EXEC_ASSERT(maxCount >= count);
            _free();

            m_external.data = _allocate(maxCount);
            std::memcpy(m_external.data, data, sizeof(ItemType) * count);
            m_external.count = count;
            m_external.maxCount = maxCount;
            m_internal.isInternal = 0;
        }
        else
        {
            // data fits in our storage. simply copy it.
            if (_isInternal())
            {
                std::memcpy(m_internal.data, data, sizeof(ItemType) * count);
                m_internal.count = count;
            }
            else
            {
                std::memcpy(m_external.data, data, sizeof(ItemType) * count);
                m_external.count = count;
            }
        }
    }

    // assumes _free() has already been called (when needed)
    inline void _move(SmallStack&& other) noexcept
    {
        if (other._isInternal())
        {
            // since other is using its internal storage, we have to copy the data
            _copy(other);
            other.m_internal.count = 0;
        }
        else
        {
            // other is using external storage
            _free();

            m_internal.isInternal = 0;

            m_external.data = other.m_external.data;
            m_external.count = other.m_external.count;
            m_external.maxCount = other.m_external.maxCount;

            other.m_internal.count = 0;
            other.m_internal.isInternal = 1;
        }
    }

    inline ItemType* _allocate(uint32_t maxCount)
    {
        auto data = reinterpret_cast<ItemType*>(carb::allocate(sizeof(ItemType) * maxCount));
        OMNI_GRAPH_EXEC_FATAL_UNLESS(data);
        return data;
    }

    inline void _allocExternalAndCopyInternal() noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(_isInternal());
        constexpr uint32_t newMaxCount = kMaxInternalDataItemCount * 2;
        ItemType* data = _allocate(newMaxCount);
        std::memcpy(data, m_internal.data, sizeof(ItemType) * kMaxInternalDataItemCount);
        m_external.data = data;
        m_external.count = kMaxInternalDataItemCount;
        m_external.maxCount = newMaxCount;
        m_internal.isInternal = 0;
    }

    inline void _grow() noexcept
    {
        OMNI_GRAPH_EXEC_ASSERT(!_isInternal());
        OMNI_GRAPH_EXEC_ASSERT(m_external.maxCount > 0);

        m_external.maxCount *= 2;

        ItemType* data = _allocate(m_external.maxCount);
        std::memcpy(data, m_external.data, sizeof(ItemType) * m_external.count);

        carb::deallocate(m_external.data);
        m_external.data = data;
    }

    constexpr static uint32_t kMaxInternalDataItemCount = 7;

    struct ExternalData
    {
        ItemType* data;
        uint32_t count;
        uint32_t maxCount;
    };

    static_assert(sizeof(ExternalData) == 16, "ExternalData is unexpected size");

    struct InternalData
    {
        ItemType data[kMaxInternalDataItemCount];
        uint32_t count;
        uint32_t isInternal;
    };

    static_assert(sizeof(InternalData) == 64, "InternalData is unexpected size");

private:
    union
    {
        ExternalData m_external;
        InternalData m_internal;
    };
};

} // namespace detail
} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
