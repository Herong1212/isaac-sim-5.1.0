// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#ifdef __INTELLISENSE__
#    include "Vector.h"
#endif

#include <algorithm>
#include <limits>
#include <type_traits>

#include "../carb/detail/ExceptionProlog.h"

namespace omni
{

template <class T>
inline CARB_CPP20_CONSTEXPR vector<T>::vector() noexcept : m_first(pointer()), m_last(pointer()), m_end(pointer())
{
}

template <class T>
inline CARB_CPP20_CONSTEXPR vector<T>::vector(size_type count, const T& value, const allocator_type&)
{
    if (_purchase(count))
    {
        CARBLOCAL_TRY_BEGIN
        {
            m_last = ::omni::detail::uninitFillN(m_first, count, value, _get_allocator());
        }
        CARBLOCAL_CATCH_ALL
        {
            _reset();
            CARBLOCAL_RETHROW;
        }
    }
}

template <class T>
inline CARB_CPP20_CONSTEXPR vector<T>::vector(size_type count, const allocator_type&)
{
    if (_purchase(count))
    {
        CARBLOCAL_TRY_BEGIN
        {
            m_last = ::omni::detail::uninitDefaultConstruct(m_first, count, _get_allocator());
        }
        CARBLOCAL_CATCH_ALL
        {
            _reset();
            CARBLOCAL_RETHROW;
        }
    }
}

template <class T>
inline CARB_CPP20_CONSTEXPR vector<T>::vector(const vector& other)
{
    if (_purchase(other.size()))
    {
        CARBLOCAL_TRY_BEGIN
        {
            m_last = ::omni::detail::uninitCopy(other.m_first, other.m_last, m_first, _get_allocator());
        }
        CARBLOCAL_CATCH_ALL
        {
            _reset();
            CARBLOCAL_RETHROW;
        }
    }
}

template <class T>
inline CARB_CPP20_CONSTEXPR vector<T>::vector(vector&& other) noexcept
{
    _move_from(std::move(other));
}

template <class T>
inline CARB_CPP20_CONSTEXPR vector<T>::vector(std::initializer_list<T> init, const allocator_type&)
{
    _ranged_construct_or_reset(init.begin(), init.end(), std::random_access_iterator_tag{});
}

template <class T>
inline CARB_CPP20_CONSTEXPR vector<T>::~vector()
{
    _reset();
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::operator=(const vector& other) -> vector&
{
    if (this != std::addressof(other))
    {
        assign(other.m_first, other.m_last);
    }
    return *this;
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::operator=(vector&& other) noexcept -> vector&
{
    if (this != std::addressof(other))
    {
        _reset();
        _move_from(std::move(other));
    }
    return *this;
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::operator=(std::initializer_list<T> init) -> vector&
{
    _ranged_assign(init.begin(), init.end(), std::random_access_iterator_tag{});
    return *this;
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::assign(size_type count, const T& value)
{
    _orphan_all();

    const size_type oldSize = size();
    const size_type oldCapacity = capacity();

    if (count > oldCapacity)
    {
        // Must reallocate
        if (count > max_size())
            _length_error();

        const size_type newCapacity = _calculate_growth(count);

        if (m_first != pointer())
        {
            ::omni::detail::destroyRange(m_first, m_last, _get_allocator());
            _get_allocator().deallocate(m_first, oldCapacity);
        }

        _purchase(newCapacity);

        m_last = ::omni::detail::uninitFillN(m_first, count, value, _get_allocator());
    }
    else if (count > oldSize)
    {
        std::fill(m_first, m_last, value);
        m_last = ::omni::detail::uninitFillN(m_last, count - oldSize, value, _get_allocator());
    }
    else
    {
        const pointer newLast = m_first + count;
        std::fill(m_first, newLast, value);
        ::omni::detail::destroyRange(newLast, m_last, _get_allocator());
        m_last = newLast;
    }
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::assign(std::initializer_list<T> init)
{
    _ranged_assign(init.begin(), init.end(), std::random_access_iterator_tag{});
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::get_allocator() const noexcept -> allocator_type
{
    return _get_allocator();
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::at(size_type pos) -> reference
{
    if (pos >= size())
        _range_error();

    return m_first[pos];
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::at(size_type pos) const -> const_reference
{
    if (pos >= size())
        _range_error();

    return m_first[pos];
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::operator[](size_type pos) -> reference
{
    CARB_ASSERT(pos < size());
    return m_first[pos];
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::operator[](size_type pos) const -> const_reference
{
    CARB_ASSERT(pos < size());
    return m_first[pos];
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::front() -> reference
{
    CARB_ASSERT(!empty());
    return *m_first;
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::front() const -> const_reference
{
    CARB_ASSERT(!empty());
    return *m_first;
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::back() -> reference
{
    CARB_ASSERT(!empty());
    return m_last[-1];
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::back() const -> const_reference
{
    CARB_ASSERT(!empty());
    return m_last[-1];
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::data() noexcept -> pointer
{
    return m_first;
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::data() const noexcept -> const_pointer
{
    return m_first;
}

template <class T>
inline CARB_CPP20_CONSTEXPR bool vector<T>::empty() const noexcept
{
    return m_last == m_first;
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::size() const noexcept -> size_type
{
    return size_type(m_last - m_first);
}

#pragma push_macro("max")
#undef max

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::max_size() const noexcept -> size_type
{
    return size_type(std::numeric_limits<ptrdiff_t>::max());
}

#pragma pop_macro("max")

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::reserve(size_type new_cap)
{
    if (new_cap > capacity())
    {
        if (new_cap > max_size())
            _length_error();

        _reallocate_exactly(new_cap);
    }
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::capacity() const noexcept -> size_type
{
    return (size_type)(m_end - m_first);
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::shrink_to_fit()
{
    if (_has_unused_capacity())
    {
        if (empty())
        {
            _reset();
        }
        else
        {
            _reallocate_exactly(size());
        }
    }
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::clear() noexcept
{
    _orphan_all();
    ::omni::detail::destroyRange(m_first, m_last, _get_allocator());
    m_last = m_first;
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::insert(const_iterator pos, const T& value) -> iterator
{
    return emplace(pos, value);
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::insert(const_iterator pos, T&& value) -> iterator
{
    return emplace(pos, std::move(value));
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::insert(const_iterator pos, size_type count, const T& value) -> iterator
{
    _verify_iterator(pos, true);

    pointer wherePtr = const_cast<pointer>(pos.operator->());
    const size_type whereOffset = size_type(wherePtr - m_first);
    const bool oneAtBack = (count == 1 && wherePtr == m_last);

    if (count == 0)
    {
        // Nothing happens.
    }
    else if (count > _unused_capacity())
    {
        const size_type oldSize = size();

        if (count > (max_size() - oldSize))
            _length_error();

        const size_type newSize = oldSize + count;
        const size_type newCapacity = _calculate_growth(newSize);

        const pointer newVec = _get_allocator().allocate(newCapacity);
        const pointer constructedLast = newVec + whereOffset + count;
        pointer constructedFirst = constructedLast;

        CARBLOCAL_TRY_BEGIN
        {
            ::omni::detail::uninitFillN(newVec + whereOffset, count, value, _get_allocator());
            constructedFirst = newVec + whereOffset;

            if (oneAtBack)
            {
                // Provide strong exception guarantee
                _uninit_noexcept_move_or_copy(m_first, m_last, newVec);
            }
            else
            {
                ::omni::detail::uninitMove(m_first, wherePtr, newVec, _get_allocator());
                constructedFirst = newVec;
                ::omni::detail::uninitMove(wherePtr, m_last, newVec + whereOffset + count, _get_allocator());
            }
        }
        CARBLOCAL_CATCH_ALL
        {
            ::omni::detail::destroyRange(constructedFirst, constructedLast, _get_allocator());
            _get_allocator().deallocate(newVec, newCapacity);
            CARBLOCAL_RETHROW;
        }

        _reset(newVec, newSize, newCapacity);
    }
    else if (oneAtBack)
    {
        // Provide strong exception guarantee
        _emplace_back_no_realloc(value);
    }
    else
    {
        const value_type temp = value; // handle aliasing
        const pointer oldLast = m_last;
        const size_type affected = size_type(oldLast - wherePtr);
        _orphan_range(wherePtr, oldLast);

        if (count > affected)
        {
            m_last = ::omni::detail::uninitFillN(oldLast, count - affected, temp, _get_allocator());
            m_last = ::omni::detail::uninitMove(wherePtr, oldLast, m_last, _get_allocator());
            std::fill(wherePtr, oldLast, temp);
        }
        else
        {
            m_last = ::omni::detail::uninitMove(oldLast - count, oldLast, oldLast, _get_allocator());
            std::move_backward(wherePtr, oldLast - count, oldLast);
            std::fill(wherePtr, wherePtr + count, temp);
        }
    }

    return iterator(m_first + whereOffset);
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::insert(const_iterator pos, std::initializer_list<T> init) -> iterator
{
    return insert(pos, init.begin(), init.end());
}

template <class T>
template <class... Args>
inline CARB_CPP20_CONSTEXPR auto vector<T>::emplace(const_iterator pos, Args&&... args) -> iterator
{
    _verify_iterator(pos, true);

    const pointer wherePtr = const_cast<pointer>(pos.operator->());
    const pointer oldLast = m_last;

    if (_has_unused_capacity())
    {
        if (wherePtr == oldLast)
        {
            _emplace_back_no_realloc(std::forward<Args>(args)...);
        }
        else
        {
            value_type temp(std::forward<Args>(args)...); // handle aliasing
            _orphan_range(wherePtr, oldLast);
            std::allocator_traits<allocator_type>::construct(
                _get_allocator(), ::omni::detail::resolvePtr(oldLast), std::move(oldLast[-1]));
            ++m_last;
            std::move_backward(wherePtr, oldLast - 1, oldLast);
            *wherePtr = std::move(temp);
        }
        return iterator(wherePtr);
    }
    return iterator(_emplace_reallocate(wherePtr, std::forward<Args>(args)...));
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::erase(const_iterator pos) -> iterator
{
    _verify_iterator(pos, false);

    const pointer wherePtr = const_cast<pointer>(pos.operator->());
    _orphan_range(wherePtr, m_last);

    std::move(wherePtr + 1, m_last, wherePtr);
    std::allocator_traits<allocator_type>::destroy(_get_allocator(), ::omni::detail::resolvePtr(m_last - 1));
    --m_last;
    return iterator(wherePtr);
}

template <class T>
inline CARB_CPP20_CONSTEXPR auto vector<T>::erase(const_iterator first, const_iterator last) -> iterator
{
    _verify_iterator(last, true);
    const pointer firstPtr = const_cast<pointer>(first.operator->());
    const pointer lastPtr = const_cast<pointer>(last.operator->());
    if (firstPtr == lastPtr)
        return iterator(lastPtr);

    _verify_iterator(first, false);
    _orphan_range(firstPtr, m_last);
    const pointer newLast = std::move(lastPtr, m_last, firstPtr);
    ::omni::detail::destroyRange(newLast, m_last, _get_allocator());
    m_last = newLast;
    return iterator(firstPtr);
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::push_back(const T& value)
{
    emplace_back(value);
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::push_back(T&& value)
{
    emplace_back(std::move(value));
}

template <class T>
template <class... Args>
inline CARB_CPP20_CONSTEXPR auto vector<T>::emplace_back(Args&&... args) -> value_type&
{
    if (_has_unused_capacity())
    {
        return _emplace_back_no_realloc(std::forward<Args>(args)...);
    }

    return *_emplace_reallocate(m_last, std::forward<Args>(args)...);
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::pop_back()
{
    std::allocator_traits<allocator_type>::destroy(_get_allocator(), ::omni::detail::resolvePtr(m_last - 1));
    --m_last;
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::resize(size_type count)
{
    _internal_resize(count, [](pointer dest, const size_type count) {
        return ::omni::detail::uninitDefaultConstruct(dest, count, _get_allocator());
    });
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::resize(size_type count, const T& value)
{
    _internal_resize(count, [&value](pointer dest, const size_type count) {
        return ::omni::detail::uninitFillN(dest, count, value, _get_allocator());
    });
}

template <class T>
inline CARB_CPP20_CONSTEXPR void vector<T>::swap(vector& other) noexcept
{
    if (this != std::addressof(other))
    {
        std::swap(m_first, other.m_first);
        std::swap(m_last, other.m_last);
        std::swap(m_end, other.m_end);
    }
}


template <class T>
inline bool vector<T>::_has_unused_capacity() const noexcept
{
    return m_end != m_last;
}

template <class T>
inline auto vector<T>::_unused_capacity() const noexcept -> size_type
{
    return size_type(m_end - m_last);
}

template <class T>
inline void vector<T>::_move_from(vector&& other) noexcept
{
    _swap_all(other);

    m_first = other.m_first;
    m_last = other.m_last;
    m_end = other.m_end;

    other.m_first = pointer();
    other.m_last = pointer();
    other.m_end = pointer();
}

template <class T>
inline auto vector<T>::_calculate_growth(const size_type newSize) const -> size_type
{
    const size_type oldCapacity = capacity();

    if (oldCapacity > (max_size() - oldCapacity / 2))
    {
        return newSize; // avoid overflow
    }

    const size_type geometricGrowth = oldCapacity + oldCapacity / 2;
    return geometricGrowth < newSize ? newSize : geometricGrowth;
}

template <class T>
inline bool vector<T>::_purchase(const size_type cap)
{
    m_first = m_last = m_end = pointer();

    if (cap == 0)
        return false;

    if (cap > max_size())
        _length_error();

    m_first = _get_allocator().allocate(cap);
    m_last = m_first;
    m_end = m_first + cap;
    return true;
}

template <class T>
inline void vector<T>::_reset()
{
    _orphan_all();

    if (m_first != pointer())
    {
        ::omni::detail::destroyRange(m_first, m_last, _get_allocator());
        _get_allocator().deallocate(m_first, capacity());

        m_first = m_last = m_end = pointer();
    }
}

template <class T>
inline void vector<T>::_reset(const pointer newVec, const size_type newSize, const size_type newCapacity)
{
    _orphan_all();

    if (m_first != pointer())
    {
        ::omni::detail::destroyRange(m_first, m_last, _get_allocator());
        _get_allocator().deallocate(m_first, capacity());
    }

    m_first = newVec;
    m_last = newVec + newSize;
    m_end = newVec + newCapacity;
}

template <class T>
inline void vector<T>::_reallocate_exactly(const size_type newCapacity)
{
    const size_type oldSize = size();

    const pointer newVec = _get_allocator().allocate(newCapacity);

    CARBLOCAL_TRY_BEGIN
    {
        _uninit_noexcept_move_or_copy(m_first, m_last, newVec);
    }
    CARBLOCAL_CATCH_ALL
    {
        _get_allocator().deallocate(newVec, newCapacity);
        CARBLOCAL_RETHROW;
    }

    _reset(newVec, oldSize, newCapacity);
}

template <class T>
inline auto vector<T>::_get_allocator() noexcept -> allocator_type&
{
    static allocator_type al;
    return al;
}

template <class T>
inline void vector<T>::_verify_iterator(const_iterator mine, bool allowEnd)
{
    CARB_UNUSED(mine, allowEnd);
    CARB_ASSERT(mine.operator->() >= m_first);
    CARB_ASSERT(allowEnd ? (mine.operator->() <= m_last) : (mine.operator->() < m_last));
}

template <class T>
template <class Iter>
inline void vector<T>::_ranged_construct_or_reset(Iter first, Iter last, std::input_iterator_tag)
{
    m_first = m_last = m_end = pointer();

    CARBLOCAL_TRY_BEGIN
    {
        for (; first != last; ++first)
        {
            emplace_back(*first);
        }
    }
    CARBLOCAL_CATCH_ALL
    {
        _reset();
        CARBLOCAL_RETHROW;
    }
}

template <class T>
template <class Iter>
inline void vector<T>::_ranged_construct_or_reset(Iter first, Iter last, std::forward_iterator_tag)
{
    if (_purchase(size_type(std::distance(first, last))))
    {
        CARBLOCAL_TRY_BEGIN
        {
            m_last = ::omni::detail::uninitCopy(first, last, m_first, _get_allocator());
        }
        CARBLOCAL_CATCH_ALL
        {
            _reset();
            CARBLOCAL_RETHROW;
        }
    }
}

template <class T>
template <class Iter>
inline void vector<T>::_ranged_assign(Iter first, Iter last, std::input_iterator_tag)
{
    _orphan_all();

    pointer next = m_first;

    for (; first != last && next != m_last; ++first, (void)++next)
    {
        *next = *first;
    }

    ::omni::detail::destroyRange(next, m_last, _get_allocator());
    m_last = next;

    for (; first != last; ++first)
    {
        emplace_back(*first);
    }
}

template <class T>
template <class Iter>
inline void vector<T>::_ranged_assign(Iter first, Iter last, std::forward_iterator_tag)
{
    const size_type newSize = size_type(std::distance(first, last));

    _orphan_all();

    const size_type oldSize = size();
    const size_type oldCapacity = capacity();

    if (newSize > oldCapacity)
    {
        // Need to reallocate
        if (newSize > max_size())
            _length_error();

        const size_type newCapacity = _calculate_growth(newSize);

        if (m_first != pointer())
        {
            ::omni::detail::destroyRange(m_first, m_last, _get_allocator());
            _get_allocator().deallocate(m_first, oldCapacity);
        }

        _purchase(newCapacity);

        m_last = ::omni::detail::uninitCopy(first, last, m_first, _get_allocator());
    }
    else if (newSize > oldSize)
    {
        const Iter mid = std::next(first, difference_type(oldSize));
        std::copy(first, mid, m_first);
        m_last = ::omni::detail::uninitCopy(mid, last, m_last, _get_allocator());
    }
    else
    {
        const pointer newLast = m_first + newSize;
        std::copy(first, last, m_first);
        ::omni::detail::destroyRange(newLast, m_last, _get_allocator());
        m_last = newLast;
    }
}

template <class T>
template <class Iter>
inline auto vector<T>::_ranged_insert(const_iterator pos, Iter first, Iter last, std::input_iterator_tag) -> iterator
{
    _verify_iterator(pos, true);
    pointer wherePtr = const_cast<pointer>(pos.operator->());

    if (first == last)
    {
        // Nothing to do (empty range)
        return iterator(wherePtr);
    }

    const size_type whereOff = size_type(wherePtr - m_first);
    const size_type oldSize = size();

    for (; first != last; ++first)
        emplace_back(*first);

    _orphan_range(m_first + whereOff, m_first + oldSize);

    std::rotate(m_first + whereOff, m_first + oldSize, m_last);
    return iterator(m_first + whereOff);
}

template <class T>
template <class Iter>
inline auto vector<T>::_ranged_insert(const_iterator pos, Iter first, Iter last, std::forward_iterator_tag) -> iterator
{
    _verify_iterator(pos, true);
    pointer wherePtr = const_cast<pointer>(pos.operator->());

    const size_type count = size_type(std::distance(first, last));
    const size_type whereOffset = size_type(wherePtr - m_first);
    const bool oneAtBack = count == 1 && wherePtr == m_last;

    if (count == 0)
    {
        // Nothing to do (empty range)
    }
    else if (count > _unused_capacity())
    {
        // Reallocate
        const size_type oldSize = size();

        if (count > (max_size() - oldSize))
            _length_error();

        const size_type newSize = oldSize + count;
        const size_type newCapacity = _calculate_growth(newSize);

        const pointer newVec = _get_allocator().allocate(newCapacity);
        const pointer constructedLast = newVec + whereOffset + count;
        pointer constructedFirst = constructedLast;

        CARBLOCAL_TRY_BEGIN
        {
            ::omni::detail::uninitCopy(first, last, newVec + whereOffset, _get_allocator());
            constructedFirst = newVec + whereOffset;

            if (oneAtBack)
            {
                // Provide strong exception guarantee
                _uninit_noexcept_move_or_copy(m_first, m_last, newVec);
            }
            else
            {
                ::omni::detail::uninitMove(m_first, wherePtr, newVec, _get_allocator());
                constructedFirst = newVec;
                ::omni::detail::uninitMove(wherePtr, m_last, newVec + whereOffset + count, _get_allocator());
            }
        }
        CARBLOCAL_CATCH_ALL
        {
            ::omni::detail::destroyRange(constructedFirst, constructedLast, _get_allocator());
            _get_allocator().deallocate(newVec, newCapacity);
            CARBLOCAL_RETHROW;
        }

        _reset(newVec, newSize, newCapacity);
    }
    else
    {
        // Attempt to provide strong guarantee for EmplaceConstructible failure, falling back to a basic guarantee
        // for copy/move/copy-assign/move-assign failure, except for the one-at-back case.

        const pointer oldLast = m_last;
        const size_type affected = size_type(oldLast - wherePtr);

        if (count < affected)
        {
            m_last = ::omni::detail::uninitMove(oldLast - count, oldLast, oldLast, _get_allocator());
            std::move_backward(wherePtr, oldLast - count, oldLast);
            ::omni::detail::destroyRange(wherePtr, wherePtr + count, _get_allocator());

            CARBLOCAL_TRY_BEGIN
            {
                ::omni::detail::uninitCopy(first, last, wherePtr, _get_allocator());
            }
            CARBLOCAL_CATCH_ALL
            {
                // Attempt to undo since an exception was thrown during copy
                CARBLOCAL_TRY_BEGIN
                {
                    ::omni::detail::uninitMove(wherePtr + count, wherePtr + 2 * count, wherePtr, _get_allocator());
                }
                CARBLOCAL_CATCH_ALL
                {
                    _orphan_range(wherePtr, oldLast);
                    ::omni::detail::destroyRange(wherePtr + count, m_last, _get_allocator());
                    m_last = wherePtr;
                    CARBLOCAL_RETHROW;
                }

                std::move(wherePtr + 2 * count, m_last, wherePtr + count);
                ::omni::detail::destroyRange(oldLast, m_last, _get_allocator());
                m_last = oldLast;
                CARBLOCAL_RETHROW;
            }
        }
        else
        {
            // No overlap of affected elements
            const pointer reloc = wherePtr + count;
            m_last = ::omni::detail::uninitMove(wherePtr, oldLast, reloc, _get_allocator());
            ::omni::detail::destroyRange(wherePtr, oldLast, _get_allocator());

            CARBLOCAL_TRY_BEGIN
            {
                ::omni::detail::uninitCopy(first, last, wherePtr, _get_allocator());
            }
            CARBLOCAL_CATCH_ALL
            {
                // Attempt to undo since an exception was thrown during copy
                CARBLOCAL_TRY_BEGIN
                {
                    ::omni::detail::uninitMove(reloc, m_last, wherePtr, _get_allocator());
                }
                CARBLOCAL_CATCH_ALL
                {
                    _orphan_range(wherePtr, oldLast);
                    ::omni::detail::destroyRange(reloc, m_last, _get_allocator());
                    m_last = wherePtr;
                    CARBLOCAL_RETHROW;
                }
                ::omni::detail::destroyRange(reloc, m_last, _get_allocator());
                m_last = oldLast;
                CARBLOCAL_RETHROW;
            }
        }

        _orphan_range(wherePtr, oldLast);
    }

    return iterator(m_first + whereOffset);
}

template <class T>
template <class... Args>
inline auto vector<T>::_emplace_back_no_realloc(Args&&... args) -> value_type&
{
    CARB_ASSERT(_has_unused_capacity());
    std::allocator_traits<allocator_type>::construct(
        _get_allocator(), ::omni::detail::resolvePtr(m_last), std::forward<Args>(args)...);
    _orphan_range(m_last, m_last);
    return *(m_last++);
}

template <class T>
template <class... Args>
inline auto vector<T>::_emplace_reallocate(const pointer where, Args&&... args) -> pointer
{
    const size_type offset = size_type(where - m_first);
    const size_type oldSize = size();

    if (oldSize == max_size())
        _length_error();

    const size_type newSize = oldSize + 1;
    const size_type newCapacity = _calculate_growth(newSize);

    const pointer newVec = _get_allocator().allocate(newCapacity);
    const pointer constructedLast = newVec + offset + 1;
    pointer constructedFirst = constructedLast;

    CARBLOCAL_TRY_BEGIN
    {
        std::allocator_traits<allocator_type>::construct(
            _get_allocator(), ::omni::detail::resolvePtr(newVec + offset), std::forward<Args>(args)...);
        constructedFirst = newVec + offset;

        if (where == m_last)
        {
            _uninit_noexcept_move_or_copy(m_first, m_last, newVec);
        }
        else
        {
            ::omni::detail::uninitMove(m_first, where, newVec, _get_allocator());
            constructedFirst = newVec;
            ::omni::detail::uninitMove(where, m_last, newVec + offset + 1, _get_allocator());
        }
    }
    CARBLOCAL_CATCH_ALL
    {
        ::omni::detail::destroyRange(constructedFirst, constructedLast, _get_allocator());
        _get_allocator().deallocate(newVec, newCapacity);
        CARBLOCAL_RETHROW;
    }

    _reset(newVec, newSize, newCapacity);
    return m_first + offset;
}

template <class T>
template <class Pred>
inline void vector<T>::_internal_resize(const size_type count, Pred&& pred)
{
    const size_type oldSize = size();
    const size_type oldCapacity = capacity();

    if (count > oldCapacity)
    {
        // Must reallocate
        if (count > max_size())
            _length_error();

        const size_type newCapacity = _calculate_growth(count);

        const pointer newVec = _get_allocator().allocate(newCapacity);
        const pointer appendedFirst = newVec + oldSize;
        pointer appendedLast = appendedFirst;

        CARBLOCAL_TRY_BEGIN
        {
            appendedLast = pred(appendedFirst, count - oldSize);
            _uninit_noexcept_move_or_copy(m_first, m_last, newVec);
        }
        CARBLOCAL_CATCH_ALL
        {
            ::omni::detail::destroyRange(appendedFirst, appendedLast, _get_allocator());
            _get_allocator().deallocate(newVec, newCapacity);
            CARBLOCAL_RETHROW;
        }

        _reset(newVec, count, newCapacity);
    }
    else if (count > oldSize)
    {
        const pointer oldLast = m_last;
        m_last = pred(oldLast, count - oldSize);
        _orphan_range(oldLast, oldLast);
    }
    else if (count != oldSize)
    {
        const pointer newLast = m_first + count;
        _orphan_range(newLast, m_last);
        ::omni::detail::destroyRange(newLast, m_last, _get_allocator());
        m_last = newLast;
    }
    else
    {
        // no-op
    }
}

template <class T>
inline void vector<T>::_impl_uninit_noexcept_move_or_copy(pointer first, pointer last, pointer dest, std::true_type)
{
    ::omni::detail::uninitMove(first, last, dest, _get_allocator());
}

template <class T>
inline void vector<T>::_impl_uninit_noexcept_move_or_copy(pointer first, pointer last, pointer dest, std::false_type)
{
    ::omni::detail::uninitCopy(first, last, dest, _get_allocator());
}

template <class T>
inline void vector<T>::_uninit_noexcept_move_or_copy(pointer first, pointer last, pointer dest)
{
    _impl_uninit_noexcept_move_or_copy(
        first, last, dest,
        std::bool_constant<std::disjunction<std::is_nothrow_move_constructible<T>,
                                            std::negation<std::is_copy_constructible<T>>>::value>{});
}

template <class T>
[[noreturn]] inline void vector<T>::_length_error()
{
    CARBLOCAL_THROW(std::length_error, "vector<T> too long");
}

template <class T>
[[noreturn]] inline void vector<T>::_range_error()
{
    CARBLOCAL_THROW(std::out_of_range, "invalid vector<T> subscript");
}

} // namespace omni

#include "../carb/detail/ExceptionEpilog.h"
