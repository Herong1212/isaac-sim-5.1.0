// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//!
//! @brief ABI safe std::vector implementation
#pragma once

#include "detail/PointerIterator.h"
#include "detail/VectorDetail.h"
#include "../carb/Memory.h"

#include <memory>

namespace omni
{

/**
 * Implementation of an ABI-safe vector container. It is intended to be a drop-in replacement for std::vector.
 *
 * Unlike `std::vector<>`, the Allocator is not a template parameter and will always use Carbonite allocation functions,
 * such as \ref carb::allocate(), \ref carb::deallocate(), etc.
 *
 * See <a href="https://en.cppreference.com/w/cpp/container/vector">std::vector</a> for further documentation.
 *
 * @note @rstref{ABI-safety <abi-compatibility>} is only as strong as the contained type `T`. If the contained type is
 *   not also ABI-safe, then guarantees are voided. Also note that `iterator`, `const_iterator`, `reverse_iterator` and
 *   `const_reverse_iterator` are not guaranteed to be ABI-safe.
 *
 * @note If exceptions are disabled, \ref CARB_FATAL_UNLESS will be triggered instead of throwing.
 *
 * @note If exceptions are enabled, most functions provide a strong exception guarantee. If any exception is thrown, the
 *   function it is thrown from has no effect. See documentation for individual functions for specifics.
 */
template <class T>
class CARB_VIZ vector
{
public:
    //! Alias for the vector's contained type.
    using value_type = T;
    //! A reference to the allocator used by this class.
    using allocator_type = typename ::carb::Allocator<T>;
    //! Alias for size_t.
    using size_type = std::size_t;
    //! Alias for ptrdiff_t.
    using difference_type = std::ptrdiff_t;
    //! Reference to contained type.
    using reference = value_type&;
    //! Const reference to contained type.
    using const_reference = const value_type&;
    //! Pointer to contained type.
    using pointer = typename std::allocator_traits<allocator_type>::pointer;
    //! Const pointer to contained type.
    using const_pointer = typename std::allocator_traits<allocator_type>::const_pointer;
    //! Iterator type. Not guaranteed to be ABI-safe.
    using iterator = ::omni::detail::PointerIterator<pointer, vector>;
    //! Const iterator type. Not guaranteed to be ABI-safe.
    using const_iterator = ::omni::detail::PointerIterator<const_pointer, vector>;
    //! Reverse iterator type. Not guaranteed to be ABI-safe.
    using reverse_iterator = std::reverse_iterator<iterator>;
    //! Const reverse iterator type. Not guaranteed to be ABI-safe.
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;

    //! Default constructor.
    CARB_CPP20_CONSTEXPR vector() noexcept;

    //! Allocator copy constructor.
    CARB_CPP20_CONSTEXPR explicit vector(const allocator_type&) noexcept : vector()
    {
    }

    //! Constructs a vector with \p count copies elements of value \p value.
    //! @throws std::length_error if `count > max_size()`.
    //! @param count The number of elements to construct.
    //! @param value The value to copy for all constructed elements.
    //! @param alloc Optional allocator to copy.
    CARB_CPP20_CONSTEXPR vector(size_type count, const T& value, const allocator_type& alloc = allocator_type());

    //! Constructs a vector with \p count default-inserted instances of `T`. No copies of values are made.
    //! @throws std::length_error if `count > max_size()`.
    //! @param count The number of elements to default-insert.
    //! @param alloc Optional allocator to copy.
    CARB_CPP20_CONSTEXPR vector(size_type count, const allocator_type& alloc = allocator_type());

    //! Constructs the container with the contents `[first, last)`.
    //! @note This overload participates in overload resolution only if `InputIt` satisfies *LegacyInputIterator* to
    //!   avoid ambiguity with other constructors.
    //! @param first Iterator of the first element to copy into the vector.
    //! @param last Iterator of the last element (first element *not* copied into the vector).
    //! @param alloc Optional allocator to copy.
    template <class InputIt CARB_NO_DOC(
        , std::enable_if_t<carb::cpp::detail::IsLegacyInputIterator<InputIt>::value, bool> = false)>
    CARB_CPP20_CONSTEXPR vector(InputIt first, InputIt last, const allocator_type& alloc = allocator_type())
    {
        _ranged_construct_or_reset(first, last, typename std::iterator_traits<InputIt>::iterator_category{});
        CARB_UNUSED(alloc);
    }

    //! Copy constructor.
    //! @param other Vector to copy elements from.
    CARB_CPP20_CONSTEXPR vector(const vector& other);

    //! Copy constructor with allocator.
    //! @param other Vector to copy elements from.
    //! @param alloc Allocator to copy.
    CARB_CPP20_CONSTEXPR vector(const vector& other, const allocator_type& alloc) : vector(other)
    {
        CARB_UNUSED(alloc);
    }

    //! Move constructor.
    //!
    //! Post-condition: \p other is guaranteed to be `empty()`.
    //! @param other Vector to move elements from.
    CARB_CPP20_CONSTEXPR vector(vector&& other) noexcept;

    //! Move constructor with allocator.
    //!
    //! Post-condition: \p other is guaranteed to be `empty()`.
    //! @param other Vector to move elements from.
    //! @param alloc Allocator to copy.
    CARB_CPP20_CONSTEXPR vector(vector&& other, const allocator_type& alloc) noexcept : vector(std::move(other))
    {
        CARB_UNUSED(alloc);
    }

    //! Constructs the container with the contents of the given initializer list.
    //! @param init `std::initializer_list` that is copied into the newly constructed vector.
    //! @param alloc Optional allocator to copy.
    CARB_CPP20_CONSTEXPR vector(std::initializer_list<T> init, const allocator_type& alloc = allocator_type());

    //! Destructor.
    CARB_CPP20_CONSTEXPR ~vector();

    //! Copy-assign operator. Replaces the contents of `*this` with a copy of the contents of \p other.
    //! @param other Another container to use as a data source.
    //! @returns `*this`
    CARB_CPP20_CONSTEXPR vector& operator=(const vector& other);

    //! Move-assign operator. Replaces the contents of `*this` with those of \p other using move semantics.
    //! Other is in a valid but unspecified state afterwards.
    //! @param other Another container to use as a data source.
    //! @returns `*this`
    CARB_CPP20_CONSTEXPR vector& operator=(vector&& other) noexcept;

    //! Replaces the contents with those in a given `initializer_list`.
    //! @param init `std::initializer_list` to use as a data source.
    //! @returns `*this`
    CARB_CPP20_CONSTEXPR vector& operator=(std::initializer_list<T> init);

    //! Assigns values to the container.
    //!
    //! Replaces the contents of the container with \p count copies of \p value.
    //! All iterators, pointers and references to the elements of the container are invalidated. The past-the-end
    //! iterator is also invalidated.
    //! @throws std::length_error if `count > max_size()`.
    //! @param count The new size of the container.
    //! @param value The value to initialize elements of the container with.
    CARB_CPP20_CONSTEXPR void assign(size_type count, const T& value);

    //! Assigns values to the container.
    //!
    //! Replaces the contents of the container with copies of those in the range `[first, last)`. The behavior is
    //! undefined if either argument is an iterator into `*this`. This overload participates in overload resolution only
    //! if `InputIt` satisfies \a LegacyInputIterator.
    //! All iterators, pointers and references to the elements of the container are invalidated. The past-the-end
    //! iterator is also invalidated.
    //! @param first The beginning of the range to copy elements from.
    //! @param last The end of the range to copy elements from (note that this element is not copied).
    template <class InputIt CARB_NO_DOC(
        , std::enable_if_t<carb::cpp::detail::IsLegacyInputIterator<InputIt>::value, bool> = false)>
    CARB_CPP20_CONSTEXPR void assign(InputIt first, InputIt last)
    {
        _ranged_assign(first, last, typename std::iterator_traits<InputIt>::iterator_category{});
    }

    //! Assigns values to the container.
    //!
    //! Replaces the contents of the container with the elements from the initializer list \p init.
    //! All iterators, pointers and references to the elements of the container are invalidated. The past-the-end
    //! iterator is also invalidated.
    //! @param init Initializer list to copy the values from.
    CARB_CPP20_CONSTEXPR void assign(std::initializer_list<T> init);

    //! Returns the allocator associated with the container.
    //! @returns The allocator associated with the container.
    CARB_CPP20_CONSTEXPR allocator_type get_allocator() const noexcept;

    //! Access specified element with bounds checking.
    //!
    //! Returns a reference to the element at specified location \p pos, with bounds checking.
    //! If \p pos is not within the range of the container, an exception of type `std::out_of_range` is thrown.
    //! @throws std::out_of_range if `pos >= size()`.
    //! @param pos Position of the element to return.
    //! @returns Reference to the requested element.
    CARB_CPP20_CONSTEXPR reference at(size_type pos);

    //! @copydoc at(size_type)
    CARB_CPP20_CONSTEXPR const_reference at(size_type pos) const;

    //! Access specified element.
    //!
    //! Returns a reference to the element at specified location \p pos. No bounds checking is performed.
    //! Unlike `std::map::operator[]` this operator never inserts a new element into the container. Accessing a
    //! non-existent element through this operator is undefined behavior.
    //! @param pos Position of the element to return.
    //! @returns Reference to the requested element.
    CARB_CPP20_CONSTEXPR reference operator[](size_type pos);

    //! @copydoc operator[](size_type)
    CARB_CPP20_CONSTEXPR const_reference operator[](size_type pos) const;

    //! Access the first element.
    //!
    //! Calling front() on an empty container causes undefined behavior.
    //! @returns Reference to the first element.
    CARB_CPP20_CONSTEXPR reference front();

    //! @copydoc front()
    CARB_CPP20_CONSTEXPR const_reference front() const;

    //! Access the last element.
    //!
    //! Calling back() on an empty container causes undefined behavior.
    CARB_CPP20_CONSTEXPR reference back();

    //! @copydoc back()
    CARB_CPP20_CONSTEXPR const_reference back() const;

    //! Direct access to the underlying data.
    //!
    //! Returns pointer to the underlying array serving as element storage. The pointer is such that range
    //! `[data(), data() + size())` is always a valid range, even if the container is empty (`data()` is not
    //! dereferenceable in that case).
    //! @returns pointer to the underlying element storage. For non-empty containers, the returned pointer compares
    //! equal to the address of the first element.
    CARB_CPP20_CONSTEXPR pointer data() noexcept;

    //! @copydoc data()
    CARB_CPP20_CONSTEXPR const_pointer data() const noexcept;

    //! Returns an iterator to the beginning.
    //! @returns an iterator to the first element.
    CARB_CPP20_CONSTEXPR iterator begin() noexcept
    {
        return iterator(m_first);
    }

    //! Returns an iterator to the beginning.
    //! @returns an iterator to the first element.
    CARB_CPP20_CONSTEXPR const_iterator begin() const noexcept
    {
        return const_iterator(m_first);
    }

    //! Returns an iterator to the beginning.
    //! @returns an iterator to the first element.
    CARB_CPP20_CONSTEXPR const_iterator cbegin() const noexcept
    {
        return begin();
    }

    //! Returns an iterator to the end.
    //! @returns an interator to the element following the last element.
    CARB_CPP20_CONSTEXPR iterator end() noexcept
    {
        return iterator(m_last);
    }

    //! Returns an iterator to the end.
    //! @returns an interator to the element following the last element.
    CARB_CPP20_CONSTEXPR const_iterator end() const noexcept
    {
        return const_iterator(m_last);
    }

    //! Returns an iterator to the end.
    //! @returns an interator to the element following the last element.
    CARB_CPP20_CONSTEXPR const_iterator cend() const noexcept
    {
        return end();
    }

    //! Returns a reverse iterator to the beginning.
    //! @returns a reverse iterator to the first element.
    CARB_CPP20_CONSTEXPR reverse_iterator rbegin() noexcept
    {
        return std::make_reverse_iterator(end());
    }

    //! Returns a reverse iterator to the beginning.
    //! @returns a reverse iterator to the first element.
    CARB_CPP20_CONSTEXPR const_reverse_iterator rbegin() const noexcept
    {
        return std::make_reverse_iterator(end());
    }

    //! Returns a reverse iterator to the beginning.
    //! @returns a reverse iterator to the first element.
    CARB_CPP20_CONSTEXPR const_reverse_iterator crbegin() const noexcept
    {
        return rbegin();
    }

    //! Returns a reverse iterator to the end.
    //! @returns a reverse iterator to the element following the last element.
    CARB_CPP20_CONSTEXPR reverse_iterator rend() noexcept
    {
        return std::make_reverse_iterator(begin());
    }

    //! Returns a reverse iterator to the end.
    //! @returns a reverse iterator to the element following the last element.
    CARB_CPP20_CONSTEXPR const_reverse_iterator rend() const noexcept
    {
        return std::make_reverse_iterator(begin());
    }

    //! Returns a reverse iterator to the end.
    //! @returns a reverse iterator to the element following the last element.
    CARB_CPP20_CONSTEXPR const_reverse_iterator crend() const noexcept
    {
        return rend();
    }

    //! Checks whether the container is empty.
    //! @returns \c true if the container is empty; \c false otherwise.
    [[nodiscard]] CARB_CPP20_CONSTEXPR bool empty() const noexcept;

    //! Returns the number of elements.
    //! @returns The number of elements in the container.
    [[nodiscard]] CARB_CPP20_CONSTEXPR size_type size() const noexcept;

    //! Returns the maximum possible number of elements.
    //!
    //! Returns the maximum number of elements the container is able to hold due to system or library implementation
    //! limitations, i.e. `std::distance(begin(), end())` for the largest container.
    //! @returns The maximum possible number of elements.
    [[nodiscard]] CARB_CPP20_CONSTEXPR size_type max_size() const noexcept;

    //! Reserves storage.
    //!
    //! Increases the capacity of the vector (the total number of elements that the vector can hold without requiring
    //! reallocation) to a value that's greater or equal to \p new_cap. If \p new_cap is greater than the current
    //! \ref capacity(), new storage is allocated, otherwise this function does nothing.
    //!
    //! `reserve()` does not change the \ref size() of the vector.
    //!
    //! If \p new_cap is greater than \ref capacity(), all iterators (including the \ref end() iterator), and all
    //! pointers and references to the elements are invalidated. Otherwise no iterators, pointers or references are
    //! invalidated.
    //!
    //! After a call to `reserve()` insertions will not trigger reallocation unless the insertion would make the size of
    //! the vector greater than the value of \ref capacity().
    //!
    //! If an exception is thrown, this function has no effect (strong exception guarantee).
    //! If `T`'s move constructor is not `noexcept` and `T` is not *CopyInsertable* into `*this`, vector will use the
    //! throwing move constructor. If it throws, the guarantee is waived and the effects are unspecified.
    //! @note This function requires that `T` meet the requirements of *MoveInsertable* into `*this`.
    //! @throws std::length_error if `new_cap > max_size()`.
    //! @param new_cap New capacity of the vector, in number of elements.
    CARB_CPP20_CONSTEXPR void reserve(size_type new_cap);

    //! Returns the number of elements that can be held in currently allocated storage.
    //! @returns Capacity of the currently allocated storage.
    [[nodiscard]] CARB_CPP20_CONSTEXPR size_type capacity() const noexcept;

    //! Reduces memory usage by freeing unused memory.
    //!
    //! Requests the removal of unused capacity. It is a non-binding request to reduce \ref capacity() to \ref size().
    //! For `std::vector<>`, it depends on the implementation whether the request is fulfilled. This implementation will
    //! always reallocate if `size() != capacity()`. If reallocation occurs, all iterators (including the \ref end()
    //! iterator) and all pointers and references to elements are invalidated. If no reallocation occurs, no iterators,
    //! pointers or references are invalidated.
    //! @note `T` must meet te requirements of *MoveInsertable* into `*this`.
    //! @note If an exception is thrown other than by the move constructor of a non-*CopyInsertable* `T`, there are no
    //! effects.
    CARB_CPP20_CONSTEXPR void shrink_to_fit();

    //! Clears the contents.
    //!
    //! Erases all elements from the container. After this call \ref size() returns zero. Invalidates any references,
    //! pointers or iterators referring to contained elements. Any past-the-end iterators are also invalidated.
    //!
    //! Leaves the \ref capacity() of the vector unchanged.
    CARB_CPP20_CONSTEXPR void clear() noexcept;

    //! Inserts elements.
    //!
    //! Inserts \p value before \p pos.
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to elements are
    //! invalidated. Otherwise, only the iterators, pointers and references before the insertion point remain valid.
    //!
    //! This function has no effect (strong exception guarantee) if exceptions are thrown other than by the copy or move
    //! constructors of `T`, or the copy-assign or move-assign operators of `T`.
    //! If an exception is thrown when inserting a single element at the end, and `T` is *CopyInsertable* or
    //! `std::is_nothrow_move_constructible_v<T>` is `true`, this function has no effect (strong exception guarantee).
    //! Otherwise, if an exception is thrown by the move constructor of a non-*CopyInsertable* `T`, the effects are
    //! unspecified.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param pos Iterator before which the content will be inserted (may be the \ref end() iterator).
    //! @param value Element value to insert.
    //! @note `T` must meet the requirements of *CopyAssignable* and *CopyInsertable*.
    //! @returns Iterator pointing to the inserted value.
    CARB_CPP20_CONSTEXPR iterator insert(const_iterator pos, const T& value);

    //! Inserts elements.
    //!
    //! Inserts \p value before \p pos.
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to elements are
    //! invalidated. Otherwise, only the iterators, pointers and references before the insertion point remain valid.
    //!
    //! This function has no effect (strong exception guarantee) if exceptions are thrown other than by the copy or move
    //! constructors of `T`, or the copy-assign or move-assign operators of `T`.
    //! If an exception is thrown when inserting a single element at the end, and `T` is *CopyInsertable* or
    //! `std::is_nothrow_move_constructible_v<T>` is `true`, this function has no effect (strong exception guarantee).
    //! Otherwise, if an exception is thrown by the move constructor of a non-*CopyInsertable* `T`, the effects are
    //! unspecified.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param pos Iterator before which the content will be inserted (may be the \ref end() iterator).
    //! @param value Element value to insert.
    //! @note `T` must meet the requirements of *MoveAssignable* and *MoveInsertable*.
    //! @returns Iterator pointing to the inserted value.
    CARB_CPP20_CONSTEXPR iterator insert(const_iterator pos, T&& value);

    //! Inserts elements.
    //!
    //! Inserts \p count copies of \p value before \p pos.
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to elements are
    //! invalidated. Otherwise, only the iterators, pointers and references before the insertion point remain valid.
    //!
    //! This function has no effect (strong exception guarantee) if exceptions are thrown other than by the copy or move
    //! constructors of `T`, or the copy-assign or move-assign operators of `T`.
    //! If an exception is thrown when inserting a single element at the end, and `T` is *CopyInsertable* or
    //! `std::is_nothrow_move_constructible_v<T>` is `true`, this function has no effect (strong exception guarantee).
    //! Otherwise, if an exception is thrown by the move constructor of a non-*CopyInsertable* `T`, the effects are
    //! unspecified.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param pos Iterator before which the content will be inserted (may be the \ref end() iterator).
    //! @param count Number of elements to insert.
    //! @param value Element value to insert.
    //! @note `T` must meet the requirements of *CopyAssignable* and *CopyInsertable*.
    //! @returns Iterator pointing to the first element inserted, or \p pos if \p count is zero.
    CARB_CPP20_CONSTEXPR iterator insert(const_iterator pos, size_type count, const T& value);

    //! Inserts elements.
    //!
    //! Inserts elements from range `[first, last)` before \p pos.
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to elements are
    //! invalidated. Otherwise, only the iterators, pointers and references before the insertion point remain valid.
    //!
    //! This function has no effect (strong exception guarantee) if exceptions are thrown other than by the copy or move
    //! constructors of `T`, the copy-assign or move-assign operators of `T`, or any `Iter` operation.
    //! If an exception is thrown when inserting a single element at the end, and `T` is *CopyInsertable* or
    //! `std::is_nothrow_move_constructible_v<T>` is `true`, this function has no effect (strong exception guarantee).
    //! Otherwise, if an exception is thrown by the move constructor of a non-*CopyInsertable* `T`, the effects are
    //! unspecified.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param pos Iterator before which the content will be inserted (may be the \ref end() iterator).
    //! @param first First iterator in a range of elements to insert, cannot be iterators into `*this`.
    //! @param last Last iterator in a range of elements to insert, cannot be iterators into `*this` (this iterator
    //!   terminates the range and is not inserted).
    //! @note `T` must meet the requirements of *EmplaceConstructible*, *Swappable*, *MoveAssignable*,
    //!   *MoveConstructible* and *MoveInsertable*.
    //! @note This overload participates in overload resolution only if `Iter` qualifies as *LegacyInputIterator* to
    //!   avoid ambiguity with other overloads.
    //! @returns Iterator pointing to the first element inserted, or \p pos if \p first is equal to \p last.
    template <class Iter CARB_NO_DOC(, std::enable_if_t<carb::cpp::detail::IsLegacyInputIterator<Iter>::value, bool> = false)>
    CARB_CPP20_CONSTEXPR iterator insert(const_iterator pos, Iter first, Iter last)
    {
        return _ranged_insert(pos, first, last, typename std::iterator_traits<Iter>::iterator_category{});
    }

    //! Inserts elements.
    //!
    //! Inserts elements from initializer list \p init before \p pos.
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to elements are
    //! invalidated. Otherwise, only the iterators, pointers and references before the insertion point remain valid.
    //!
    //! This function has no effect (strong exception guarantee) if exceptions are thrown other than by the copy or move
    //! constructors of `T`, or the copy-assign or move-assign operators of `T`.
    //! If an exception is thrown when inserting a single element at the end, and `T` is *CopyInsertable* or
    //! `std::is_nothrow_move_constructible_v<T>` is `true`, this function has no effect (strong exception guarantee).
    //! Otherwise, if an exception is thrown by the move constructor of a non-*CopyInsertable* `T`, the effects are
    //! unspecified.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param pos Iterator before which the content will be inserted (may be the \ref end() iterator).
    //! @param init Initializer list to insert the values from.
    //! @note `T` must meet the requirements of *EmplaceConstructible*, *Swappable*, *MoveAssignable*,
    //!   *MoveConstructible* and *MoveInsertable*.
    //! @returns Iterator pointing to the first element inserted, or \p pos if \p init is empty.
    CARB_CPP20_CONSTEXPR iterator insert(const_iterator pos, std::initializer_list<T> init);

    //! Constructs element in place.
    //!
    //! Inserts a new element into the container directly before \p pos.
    //!
    //! The element is constructed using placement new. If the required location has been occupied by an existing
    //! element, the inserted element is constructed at another location first and the move-assigned into the required
    //! position.
    //!
    //! The arguments `args...` are forwarded to the constructed with `std::forward<Args>(args)...`. `args...` may
    //! directly or indirectly refer to a value in the container.
    //!
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to the elements are
    //! invalidated. Otherwise, only the iterators, pointers and references before the insertion point remain valid.
    //! @note `T` must meet the requirements of *MoveAssignable*, *MoveInsertable*, and *EmplaceConstructible*.
    //! @note If an exception is thrown other than by the copy constructor, move constructor, copy-assign operator, or
    //!   move-assign operator of \ref value_type, or if an exception is thrown while `emplace()` is used to insert a
    //!   single element at the end and the \ref value_type is either *CopyInsertable* or nothrow-move-constructible,
    //!   there are no effects (strong exception guarantee). Otherwise, the effects are unspecified.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param pos Iterator before which the new element will be constructed.
    //! @param args Arguments to forward to the constructor of the element.
    //! @returns Iterator pointing to the emplaced element.
    template <class... Args>
    CARB_CPP20_CONSTEXPR iterator emplace(const_iterator pos, Args&&... args);

    //! Erases the specified elements.
    //!
    //! Removes the element at \p pos.
    //! Iterators (including the \ref end() iterator) and pointers and references to the elements at or after the point
    //! of the erasure are invalidated. The iterator \p pos must be valid and dereferenceable. Thus the \ref end()
    //! iterator (which is valid but not dereferenceable) cannot be used as a value for \p pos.
    //! @note `T` must meet the requirements of *MoveAssignable*.
    //! @note Does not throw unless an exception is thrown by the assignment operator of T.
    //! @param pos Iterator to the element to remove.
    //! @returns Iterator following the element removed. If \p pos refers to the last element, then the \ref end()
    //!   iterator is returned.
    CARB_CPP20_CONSTEXPR iterator erase(const_iterator pos);

    //! Erases the specified elements.
    //!
    //! Removes the elements in the range `[first, last)`.
    //! Iterators (including the \ref end() iterator) and pointers and references to the elements at or after the point
    //! of the erasure are invalidated. The iterator \p first does not need to be dereferenceable if `first == last`;
    //! erasing an empty range is a no-op.
    //! @note `T` must meet the requirements of *MoveAssignable*.
    //! @note Does not throw unless an exception is thrown by the assignment operator of T.
    //! @param first First iterator in the range of elements to remove.
    //! @param last Last iterator in the range of elements to remove. This iterator is not actually removed and can be
    //!   \ref end().
    //! @returns Iterator following the element removed. If `last == end()` prior to removal, then the updated
    //!   \ref end() iterator is returned. If `first == last` (empty range) then \p last is returned.
    CARB_CPP20_CONSTEXPR iterator erase(const_iterator first, const_iterator last);

    //! Adds an element to the end.
    //!
    //! Appends the given element \p value to the end of the container. The new element is initialized as a copy of
    //! \p value.
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to the elements are
    //! invalidated. Otherwise only the \ref end() iterator is invalidated.
    //! @note `T` must meet the requirements of *CopyInsertable*.
    //! @note If an exception is thrown (which can be due to allocation or element copy construction/copy assignment),
    //!   this function has no effect (strong exception guarantee).
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param value The value of the element to append.
    CARB_CPP20_CONSTEXPR void push_back(const T& value);

    //! Adds an element to the end.
    //!
    //! Appends the given element \p value to the end of the container. \p value is moved into the new element.
    //! If after the operation the new \ref size() is greater than old \ref capacity() a reallocation takes place, in
    //! which case all iterators (including the \ref end() iterator) and all pointers and references to the elements are
    //! invalidated. Otherwise only the \ref end() iterator is invalidated.
    //! @note `T` must meet the requirements of *MoveInsertable*.
    //! @note If an exception is thrown (which can be due to allocation or element move construction/move assignment),
    //!   this function has no effect (strong exception guarantee). If `T`'s move constructor is not `noexcept` and `T`
    //!   is not *CopyInsertable* into `*this`, vector will use the throwing move constructor. If it throws, the
    //!   guarantee is waived and the effects are unspecified.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param value The value of the element to append.
    CARB_CPP20_CONSTEXPR void push_back(T&& value);

    //! Constructs an element in-place at the end.
    //!
    //! Appends a new element to the end of the container using placement new to construct in-place. The arguments are
    //! forwarded to the constructor. If after the operation the new \ref size() is greater than the old \ref capacity()
    //! a reallocation takes place, in which case all iterators (including the \ref end() iterator) and all references
    //! to the elements are invalidated. Otherwise only the \ref end() iterator is invalidated.
    //! @throws std::length_error if the new \ref size() would exceed \ref max_size().
    //! @param args Arguments to forward to the constructor of the element.
    //! @returns A reference to the inserted element.
    template <class... Args>
    CARB_CPP20_CONSTEXPR value_type& emplace_back(Args&&... args);

    //! Removes the last element.
    //!
    //! Removes the last element of the container. Calling pop_back() on an empty container results in undefined
    //! behavior. The \ref end() iterator and iterators, pointers and references to the last element are invalidated.
    CARB_CPP20_CONSTEXPR void pop_back();

    //! Changes the number of elements stored.
    //!
    //! Resizes the container to \p count elements, does nothing if `count == size()`. If the current size is greater
    //! than \p count, the container is reduced to the first \p count elements. If the current size is less than
    //! \p count, additional default-inserted elements are appended.
    //! @note If an exception is thrown for any reason, these functions have no effect (strong exception safety
    //!   guarantee). If `T`'s move constructor is not `noexcept` and `T` is not *CopyInsertable* into `*this`, vector
    //!   will use the throwing move constructor. If it throws, the guarantee is waived and the effects are unspecified.
    //! @throws std::length_error If the capacity required by the new vector would exceed \ref max_size().
    //! @param count New size of the container.
    //! @note `T` must meet the requirements of *MoveInsertable* and *DefaultInsertable*.
    CARB_CPP20_CONSTEXPR void resize(size_type count);

    //! Changes the number of elements stored.
    //!
    //! Resizes the container to \p count elements, does nothing if `count == size()`. If the current size is greater
    //! than \p count, the container is reduced to the first \p count elements. If the current size is less than
    //! \p count, additional copies of \p value are appended.
    //! @note If an exception is thrown for any reason, these functions have no effect (strong exception safety
    //!   guarantee). If `T`'s move constructor is not `noexcept` and `T` is not *CopyInsertable* into `*this`, vector
    //!   will use the throwing move constructor. If it throws, the guarantee is waived and the effects are unspecified.
    //! @throws std::length_error If the capacity required by the new vector would exceed \ref max_size().
    //! @param count New size of the container.
    //! @param value The value to initialize the new elements with.
    //! @note `T` must meet the requirements of *CopyInsertable*.
    CARB_CPP20_CONSTEXPR void resize(size_type count, const value_type& value);

    //! Swaps the contents.
    //!
    //! Exchanges the contents and capacity of `*this` with those of \p other. Does not invoke any move, copy, or swap
    //! operations on individual elements. All iterators and references remain valid, except that the \ref end()
    //! iterator is invalidated.
    //! @param other Container to exchange contents with.
    CARB_CPP20_CONSTEXPR void swap(vector& other) noexcept;

private:
    bool _has_unused_capacity() const noexcept;
    size_type _unused_capacity() const noexcept;

    void _move_from(vector&& other) noexcept;

    size_type _calculate_growth(const size_type newSize) const;
    bool _purchase(const size_type cap);
    void _reset();
    void _reset(const pointer newVec, const size_type newSize, const size_type newCapacity);
    void _reallocate_exactly(const size_type newCapacity);

    static allocator_type& _get_allocator() noexcept;

    void _swap_all(vector&)
    {
        // Iterator debugging: Swap all iterators with another vector
    }
    void _orphan_all()
    {
        // Iterator debugging: all of our iterators are invalid
    }
    void _orphan_range(pointer, pointer)
    {
        // Iterator debugging: items in range (inclusive) are invalid
    }
    void _verify_iterator(const_iterator mine, bool allowEnd);

    template <class Iter>
    void _ranged_construct_or_reset(Iter first, Iter last, std::input_iterator_tag);
    template <class Iter>
    void _ranged_construct_or_reset(Iter first, Iter last, std::forward_iterator_tag);

    template <class Iter>
    void _ranged_assign(Iter first, Iter last, std::input_iterator_tag);
    template <class Iter>
    void _ranged_assign(Iter first, Iter last, std::forward_iterator_tag);

    template <class Iter>
    iterator _ranged_insert(const_iterator pos, Iter first, Iter last, std::input_iterator_tag);
    template <class Iter>
    iterator _ranged_insert(const_iterator pos, Iter first, Iter last, std::forward_iterator_tag);

    template <class... Args>
    value_type& _emplace_back_no_realloc(Args&&... args);

    template <class... Args>
    pointer _emplace_reallocate(const pointer where, Args&&... args);

    template <class Pred>
    void _internal_resize(const size_type count, Pred&& pred);

    static void _impl_uninit_noexcept_move_or_copy(pointer first, pointer last, pointer dest, std::true_type);
    static void _impl_uninit_noexcept_move_or_copy(pointer first, pointer last, pointer dest, std::false_type);
    static void _uninit_noexcept_move_or_copy(pointer first, pointer last, pointer dest);

    [[noreturn]] static void _length_error();
    [[noreturn]] static void _range_error();

    pointer m_first; // Beginning of array
    pointer m_last; // End of array
    pointer m_end; // End of allocated memory
};

//! Compares the contents of two vectors for equality.
//!
//! Vectors must have the same number of elements and each element in \p lhs compares equal with the element in \p rhs
//! at the same position.
//! @param lhs Vector whose contents to compare.
//! @param rhs Vector whose contents to compare.
//! @returns true if the contents of the vectors are equal, false otherwise.
template <class T>
[[nodiscard]] inline bool operator==(const vector<T>& lhs, const vector<T>& rhs)
{
    return (lhs.size() == rhs.size() && std::equal(lhs.begin(), lhs.end(), rhs.begin()));
}

//! Compares the contents of two vectors for inequality.
//!
//! Vectors must have differing number of elements or at least one element in \p lhs compares in-equal with the element
//! in \p rhs at the same position.
//! @param lhs Vector whose contents to compare.
//! @param rhs Vector whose contents to compare.
//! @returns false if the contents of the vectors are equal, true otherwise.
template <class T>
[[nodiscard]] inline bool operator!=(const vector<T>& lhs, const vector<T>& rhs)
{
    return !(lhs == rhs);
}

//! Compares the contents of two vectors lexicographically.
//!
//! Compares the contents of \p lhs and \p rhs lexicographically. The comparison is performed as if by
//! `std::lexicographical_compare`.
//! @param lhs Vector whose contents to compare.
//! @param rhs Vector whose contents to compare.
//! @returns true if contents of \p lhs are lexicographically *less than* the contents of \p rhs; false otherwise.
template <class T>
[[nodiscard]] inline bool operator<(const vector<T>& lhs, const vector<T>& rhs)
{
    return std::lexicographical_compare(lhs.begin(), lhs.end(), rhs.begin(), rhs.end());
}

//! Compares the contents of two vectors lexicographically.
//!
//! Compares the contents of \p lhs and \p rhs lexicographically. The comparison is performed as if by
//! `std::lexicographical_compare`.
//! @param lhs Vector whose contents to compare.
//! @param rhs Vector whose contents to compare.
//! @returns true if contents of \p lhs are lexicographically *greater than* the contents of \p rhs; false otherwise.
template <class T>
[[nodiscard]] inline bool operator>(const vector<T>& lhs, const vector<T>& rhs)
{
    return (rhs < lhs);
}

//! Compares the contents of two vectors lexicographically.
//!
//! Compares the contents of \p lhs and \p rhs lexicographically. The comparison is performed as if by
//! `std::lexicographical_compare`.
//! @param lhs Vector whose contents to compare.
//! @param rhs Vector whose contents to compare.
//! @returns true if contents of \p lhs are lexicographically *less than or equal to* the contents of \p rhs; false
//!   otherwise.
template <class T>
[[nodiscard]] inline bool operator<=(const vector<T>& lhs, const vector<T>& rhs)
{
    return !(rhs < lhs);
}

//! Compares the contents of two vectors lexicographically.
//!
//! Compares the contents of \p lhs and \p rhs lexicographically. The comparison is performed as if by
//! `std::lexicographical_compare`.
//! @param lhs Vector whose contents to compare.
//! @param rhs Vector whose contents to compare.
//! @returns true if contents of \p lhs are lexicographically *greater than or equal to* the contents of \p rhs; false
//!   otherwise.
template <class T>
[[nodiscard]] inline bool operator>=(const vector<T>& lhs, const vector<T>& rhs)
{
    return !(lhs < rhs);
}

//! For now, the bool specialization is defined so as to not be used. This way we can decide later if we want to
//! provide an ABI-safe version or not.
template <>
class vector<bool>
{
private:
    vector() = default;
};

} // namespace omni

//! \cond DEV
namespace std
{

template <class T>
void swap(omni::vector<T>& lhs, omni::vector<T>& rhs) noexcept
{
    lhs.swap(rhs);
}

} // namespace std
//! \endcond

CARB_INCLUDE_PURIFY_TEST({
    using namespace omni;
    vector<vector<int>> v(5);
    vector<vector<int>> v2 = v;
    v.assign(v2.begin(), v2.end());
    v2.assign(5, {});
    v2.assign({});
    CARB_UNUSED(v.front(), v.back(), v.at(0), v[0], v.data(), v.cbegin(), v.cend(), v.rend(), v.rbegin(), v.crend());
    CARB_UNUSED(v.crbegin(), v.empty(), v.size(), v.max_size(), v.capacity());
    v.reserve(0);
    v.shrink_to_fit();
    v.clear();
    v.insert(v.begin(), decltype(v)::value_type{});
    v.insert(v.begin(), 5, decltype(v)::value_type{});
    v.insert(v.begin(), v2.begin(), v2.end());
    v.insert(v.begin(), std::initializer_list<decltype(v)::value_type>{});
    v.emplace(v.begin(), 5u);
    v.erase(v.begin());
    v2.erase(v2.begin(), v2.end());
    v.push_back({});
    v.pop_back();
    v.resize(1);
    v.resize(2, {});
    v.swap(v2);
});

#if !defined __INTELLISENSE__
#    include "Vector.inl"
#endif
