// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<span>` library.
#pragma once

#include "../Defines.h"
#include "TypeTraits.h"
#include "detail/ImplData.h"
#include "StdDef.h"
#include "Memory.h"
#include "../../omni/detail/PointerIterator.h"

#include <array>
#include <stdexcept>

#if CARB_HAS_CPP20
#    include <ranges>
#endif

namespace carb::cpp
{

//! A constant of type size_t that is used to differentiate carb::cpp::span of static and dynamic extent
//! @see span
constexpr size_t dynamic_extent = size_t(-1);

template <class T, size_t Extent>
class span;

//! \cond DEV
namespace detail
{

template <size_t Extent, size_t Offset, size_t Count>
struct DetermineSubspanExtent
{
    constexpr static size_t value = Count;
};

template <size_t Extent, size_t Offset>
struct DetermineSubspanExtent<Extent, Offset, dynamic_extent>
{
    constexpr static size_t value = Extent - Offset;
};

template <size_t Offset>
struct DetermineSubspanExtent<dynamic_extent, Offset, dynamic_extent>
{
    constexpr static size_t value = dynamic_extent;
};

template <class T>
struct IsStdArray : public std::false_type
{
};

template <class T, size_t N>
struct IsStdArray<std::array<T, N>> : public std::true_type
{
};

template <class T>
struct IsSpan : public std::false_type
{
};

template <class T, size_t N>
struct IsSpan<span<T, N>> : public std::true_type
{
};

template <typename T>
struct always_false
{
    static constexpr bool value = false;
};

#if CARB_EXCEPTIONS_ENABLED
#    define CARBLOCAL_THROW_OR_FATAL(check, msg)                                                                       \
        if (!CARB_LIKELY(check))                                                                                       \
            CARB_CPP20_UNLIKELY                                                                                        \
        throw std::out_of_range(msg)
#else
#    define CARBLOCAL_THROW_OR_FATAL(check, msg) CARB_FATAL_UNLESS((check), msg)
#endif

} // namespace detail
//! \endcond

/**
 * An object that refers to a contiguous sequence of objects.
 *
 * The class template span describes an object that can refer to a contiguous sequence of objects with the first element
 * of the sequence at position zero. A span can either have a \a static extent, in which case the number of elements in
 * the sequence is known at compile-time and encoded in the type, or a \a dynamic extent.
 *
 * If a span has \a dynamic extent, this implementation holds two members: a pointer to T and a size. A span with
 * \a static extent has only one member: a pointer to T.
 *
 * Every specialization of \c span is a \a TriviallyCopyable type.
 *
 * This implementation of \c span is a C++14-compatible implementation of the
 * [C++20 std::span](https://en.cppreference.com/w/cpp/container/span), as such certain constructors that involve
 * `ranges` or `concepts` are either not implemented or are implemented using C++14 paradigms.
 *
 * This implementation of \c span is a guaranteed @rstref{ABI- and interop-safe <abi-compatibility>} type.
 *
 * @note For function definitions below the following definitions are used: An ill-formed program will generate a
 *   compiler error via `static_assert`. Undefined behavior is typically caught by \ref CARB_ASSERT if enabled. The
 *   \ref span::at() function does bounds-checking and will throw `std::out_of_range` if exceptions are enabled,
 *   however, if exceptions are disabled a \ref CARB_FATAL_UNLESS will occur (this also disables `constexpr` as
 *   \ref CARB_FATAL_UNLESS is not `constexpr`).
 * @tparam T Element type; must be a complete object type that is not an abstract class type
 * @tparam Extent The number of elements in the sequence, or \ref dynamic_extent if dynamic
 */
template <class T, size_t Extent = dynamic_extent>
class span
{
    // NOTE: This implementation is used for Extent != 0 && Extent != dynamic_extent, both of which have specializations
public:
    using element_type = T; //!< The element type `T`
    using value_type = std::remove_cv_t<T>; //!< The value type; const/volatile is removed from `T`
    using size_type = std::size_t; //!< The size type `size_t`
    using difference_type = std::ptrdiff_t; //!< The difference type `ptrdiff_t`
    using pointer = T*; //!< The pointer type `T*`
    using const_pointer = const T*; //!< The const pointer type `const T*`
    using reference = T&; //!< The reference type `T&`
    using const_reference = const T&; //!< The const reference type `const T&`

    //! The iterator type \ref omni::detail::PointerIterator
    using iterator = omni::detail::PointerIterator<pointer, span>;
    //! The reverse iterator type `std::reverse_iterator<iterator>`
    using reverse_iterator = std::reverse_iterator<iterator>;

    //! The number of elements in the sequence, or \ref dynamic_extent if dynamic
    constexpr static size_type extent = Extent;

#ifdef DOXYGEN_BUILD
    //! Default constructor
    //!
    //! Constructs an empty span whose \ref data() is `nullptr` and \ref size() is `0`. This constructor participates in
    //! overload resolution only if `extent == 0 || extent == dynamic_extent`.
    constexpr span() noexcept
    {
    }
#endif

    //! Constructs a \ref span that is a view over the range `[first, first + count)`.
    //!
    //! Behavior is undefined if `count != extent` (for static extent) or \p first does not model `contiguous_iterator`.
    //! However, since `contiguous_iterator` is not available until C++20, instead this function does not participate in
    //! overload resolution unless `std::iterator_traits<It>::iterator_category == std::random_access_iterator_tag`.
    //! @param first An iterator or pointer type that models C++20 `contiguous_iterator`
    //! @param count The number of elements from \p first to include in the span. If `extent != dynamic_extent` then
    //!   this must match \ref extent.
    template <class It CARB_NO_DOC(
        ,
        std::enable_if_t<std::is_same<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>::value,
                         bool> = false)>
    constexpr explicit span(It first, size_type count) : m_p(to_address(first))
    {
        CARB_ASSERT(extent == count, "Behavior is undefined if count != extent");
    }

    //! Constructs a \ref span that is a view over the range `[first, last)`.
    //!
    //! Behavior is undefined if `(last - first) != extent` (for static extent) or if `[first, last)` does not represent
    //! a contiguous range. This function differs significantly from the C++20 definition since the concepts of
    //! `contiguous_iterator` and `sized_sentinel_for` are not available. Since these concepts are not available until
    //! C++20, instead this function does not participate in overload resolution unless
    //! `std::iterator_traits<It>::iterator_category == std::random_access_iterator_tag`. Also \p first and \p last must
    //! be a matching iterator type.
    //! @param first An iterator or pointer type that represents the first element in the span.
    //! @param last An iterator or pointer type that represents the past-the-end element in the span.
    template <class It CARB_NO_DOC(
        ,
        std::enable_if_t<std::is_same<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>::value,
                         bool> = false)>
    constexpr explicit span(It first, It last) : m_p(to_address(first))
    {
        CARB_ASSERT((last - first) == extent, "Behavior is undefined if (last - first) != extent");
    }

    //! Constructs a span that is a view over an array.
    //!
    //! Behavior is undefined if `extent != dynamic_extent && N != extent`.
    //! @param arr The array to view
    template <std::size_t N>
    constexpr span(type_identity_t<element_type> (&arr)[N]) noexcept : m_p(cpp::data(arr))
    {
        static_assert(N == extent, "Undefined if N != extent");
    }

    //! Constructs a span that is a view over an array.
    //!
    //! Behavior is undefined if `extent != dynamic_extent && N != extent`.
    //! @param arr The array to view
    template <class U, std::size_t N CARB_NO_DOC(, std::enable_if_t<std::is_convertible<U, element_type>::value, bool> = false)>
    constexpr span(std::array<U, N>& arr) noexcept : m_p(cpp::data(arr))
    {
        static_assert(N == extent, "Undefined if N != extent");
    }

    //! Constructs a span that is a view over an array.
    //!
    //! Behavior is undefined if `extent != dynamic_extent && N != extent`.
    //! @param arr The array to view
    template <class U, std::size_t N CARB_NO_DOC(, std::enable_if_t<std::is_convertible<U, element_type>::value, bool> = false)>
    constexpr span(const std::array<U, N>& arr) noexcept : m_p(cpp::data(arr))
    {
        static_assert(N == extent, "Undefined if N != extent");
    }

    // template< class R >
    // explicit(extent != dynamic_extent)
    // constexpr span( R&& range );
    // (Constructor not available without ranges, but approximate constructor follows)

    //! Constructs a span that is a view over a range.
    //!
    //! The behavior is undefined if any of the following are true:
    //! * `R` does not actually model `contiguous_range` and `sized_range`
    //! * if `R` does not model `borrowed_range` while `element_type` is non-const
    //! * `extent` is not `dynamic_extent` and the size of the range != `extent`
    //!
    //! @tparam R A range type. Since this implementation is for pre-C++20 and ranges are not available, this is an
    //!   approximation of a `range`: This type must have `data()` and `size()` member functions that must be
    //!   convertible to the \ref pointer and \ref size_type types respectively.
    //! @param range The range to view. Behavior is undefined if `[range.data(), range.data() + range.size())` is not a
    //!   contiguous range or cannot be borrowed (i.e. it is a temporary that will expire leaving a danging pointer).
    template <class R CARB_NO_DOC(
        ,
        std::enable_if_t<detail::IsConvertibleRange<cpp::remove_cvref_t<R>, pointer>::value &&
                             // These types have a separate constructor
                             !detail::IsStdArray<cpp::remove_cvref_t<R>>::value &&
                             !detail::IsSpan<cpp::remove_cvref_t<R>>::value && !std::is_array<cpp::remove_cvref_t<R>>::value,
                         bool> = false)>
    constexpr explicit span(R&& range) : m_p(range.data())
    {
        CARB_ASSERT(range.size() == extent, "Behavior is undefined if R.size() != extent");
    }

#ifndef DOXYGEN_BUILD
    template <class U,
              std::size_t N,
              std::enable_if_t<N == dynamic_extent && std::is_convertible<U, element_type>::value, bool> = false>
    constexpr explicit span(const span<U, N>& source) noexcept : m_p(source.data())
    {
        CARB_ASSERT(source.size() == extent, "Behavior is undefined if source.size() != extent");
    }

    template <class U,
              std::size_t N,
              std::enable_if_t<N != dynamic_extent && std::is_convertible<U, element_type>::value, bool> = false>
#else
    //! Converting constructor from another span.
    //!
    //! Behavior is undefined if `extent != dynamic_extent && source.size() != extent`.
    //! @tparam U `element_type` of \p source; must be convertible to `element_type`
    //! @tparam N `extent` of \p source
    //! @param source The span to convert from
    template <class U, std::size_t N>
#endif
    constexpr span(const span<U, N>& source) noexcept : m_p(source.data())
    {
        static_assert(N == extent, "Undefined if N != extent");
    }

    //! Copy constructor
    //! @param other A span to copy from
    constexpr span(const span& other) noexcept = default;

    //! Assignment operator
    //!
    //! @param other A span to copy from
    //! @returns *this
    constexpr span& operator=(const span& other) noexcept = default;

    //! Returns an iterator to the first element of the span.
    //!
    //! If the span is empty, the returned iterator will be equal to \ref end().
    //! @returns an \ref iterator to the first element of the span
    constexpr iterator begin() const noexcept
    {
        return iterator(m_p);
    }

    //! Returns an iterator to the element following the last element of the span.
    //!
    //! This element acts as a placeholder; attempting to access it results in undefined behavior.
    //! @returns an \ref iterator to the element following the last element of the span
    constexpr iterator end() const noexcept
    {
        return iterator(m_p + extent);
    }

    //! Returns a reverse iterator to the first element of the reversed span.
    //!
    //! It corresponds to the last element of the non-reversed span. If the span is empty, the returned iterator is
    //! equal to \ref rend().
    //! @returns a \ref reverse_iterator to the first element of the reversed span
    constexpr reverse_iterator rbegin() const noexcept
    {
        return reverse_iterator(end());
    }

    //! Reverse a reverse iterator to the element following the last element of the reversed span.
    //!
    //! It corresponds to the element preceding the first element of the non-reversed span. This element acts as a
    //! placeholder, attempting to access it results in undefined behavior.
    //! @returns a \ref reverse_iterator to the element following the last element of the reversed span
    constexpr reverse_iterator rend() const noexcept
    {
        return reverse_iterator(begin());
    }

    //! Returns a reference to the first element in the span.
    //!
    //! Calling this on an empty span results in undefined behavior.
    //! @returns a reference to the first element
    constexpr reference front() const noexcept /*strengthened*/
    {
        return data()[0];
    }

    //! Returns a reference to the last element in a span.
    //!
    //! Calling this on an empty span results in undefined behavior.
    //! @returns a reference to the last element
    constexpr reference back() const noexcept /*strengthened*/
    {
        return data()[extent - 1];
    }

    //! Returns a reference to the element at the specified location, with bounds checking.
    //!
    //! If \p index is not within the range of the span, `std::out_of_range` is thrown if exceptions are enabled,
    //! or a \ref CARB_FATAL_UNLESS occurs if exceptions are not enabled.
    //! @param index The index of the element to access.
    //! @returns a reference to the element at position \p index.
    //! @throws std::out_of_range if \p index is not within the range of the span, and exceptions are enabled.
    constexpr reference at(size_type index) const
    {
        CARBLOCAL_THROW_OR_FATAL(index < extent, "Given index is not within the extent of the span");
        return data()[index];
    }

    //! Returns a reference to the element in the span at the given index, without bounds checking.
    //!
    //! The behavior is undefined if \p index is out of range (i.e. if it is greater than or equal to \ref size() or
    //! the span is \ref empty()).
    //! @param index The index of the element to access
    //! @returns a reference to the element at position \p index
    constexpr reference operator[](size_type index) const noexcept /*strengthened*/
    {
        CARB_ASSERT(index < extent);
        return data()[index];
    }

    //! Returns a pointer to the beginning of the sequence.
    //! @returns a pointer to the beginning of the sequence
    constexpr pointer data() const noexcept
    {
        return m_p;
    }

    //! Returns the number of elements in the span.
    //! @returns the number of elements in the span
    constexpr size_type size() const noexcept
    {
        return extent;
    }

    //! Returns the size of the sequence in bytes.
    //! @returns the size of the sequence in bytes
    constexpr size_type size_bytes() const noexcept
    {
        return sizeof(element_type) * extent;
    }

    //! Checks if the span is empty.
    //! @returns \c true if the span is empty (i.e. \ref size() == 0); \c false otherwise
    [[nodiscard]] constexpr bool empty() const noexcept
    {
        return false;
    }

    //! Obtains a subspan consisting of the first N elements of the sequence.
    //!
    //! The program is ill-formed if `Count > extent`. The behavior is undefined if `Count > size()`.
    //! @tparam Count the number of elements of the subspan
    //! @returns a span that is a view over the first `Count` elements of `*this`
    template <std::size_t Count>
    constexpr span<element_type, Count> first() const noexcept /*strengthened*/
    {
        static_assert(Count <= extent, "Program ill-formed if Count > extent");
        return span<element_type, Count>{ data(), Count };
    }

    //! Obtains a subspan consisting of the first N elements of the sequence.
    //!
    //! The program is ill-formed if `Count > extent`. The behavior is undefined if `Count > size()`.
    //! @param Count the number of elements of the subspan
    //! @returns a span of dynamic extent that is a view over the first `Count` elements of `*this`
    constexpr span<element_type, dynamic_extent> first(size_type Count) const noexcept /*strengthened*/
    {
        CARB_ASSERT(Count <= size(), "Behavior is undefined if Count > size()");
        return span<element_type, dynamic_extent>{ data(), Count };
    }

    //! Obtains a subspan consisting of the last N elements of the sequence.
    //!
    //! The program is ill-formed if `Count > Extent`. The behavior is undefined if `Count > size()`.
    //! @tparam Count the number of elements of the subspan
    //! @returns a span that is a view over the last `Count` elements of `*this`
    template <std::size_t Count>
    constexpr span<element_type, Count> last() const noexcept /*strengthened*/
    {
        static_assert(Count <= extent, "Program ill-formed if Count > extent");
        return span<element_type, Count>{ data() + (extent - Count), Count };
    }

    //! Obtains a subspan consisting of the last N elements of the sequence.
    //!
    //! The program is ill-formed if `Count > extent`. The behavior is undefined if `Count > size()`.
    //! @param Count the number of elements of the subspan
    //! @returns a span of dynamic extent that is a view over the last `Count` elements of `*this`
    constexpr span<element_type, dynamic_extent> last(size_type Count) const noexcept /*strengthened*/
    {
        CARB_ASSERT(Count <= size(), "Behavior is undefined if Count > extent");
        return span<element_type, dynamic_extent>{ m_p + (extent - Count), Count };
    }

    //! Obtains a subspan that is a view over Count elements of this span starting at Offset.
    //!
    //! If `Count` is \ref dynamic_extent, the number of elements in the subspan is \ref size() - `Offset` (i.e. it ends
    //! at the end of `*this`).
    //! Ill-formed if `Offset` is greater than \ref extent, or `Count` is not \ref dynamic_extent and `Count` is greater
    //! than \ref extent - `Offset`.
    //! Behavior is undefined if either `Offset` or `Count` is out of range. This happens if `Offset` is greater than
    //! \ref size(), or `Count` is not \ref dynamic_extent and `Count` is greater than \ref size() - `Offset`.
    //! The \ref extent of the returned span is determined as follows: if `Count` is not \ref dynamic_extent, `Count`;
    //! otherwise, if `Extent` is not \ref dynamic_extent, `Extent - Offset`; otherwise \ref dynamic_extent.
    //! @tparam Offset The offset within `*this` to start the subspan
    //! @tparam Count The length of the subspan, or \ref dynamic_extent to indicate the rest of the span.
    //! @returns A subspan of the given range
    template <std::size_t Offset, std::size_t Count = dynamic_extent>
    constexpr span<element_type, detail::DetermineSubspanExtent<extent, Offset, Count>::value> subspan() const noexcept /*strengthened*/
    {
        static_assert(!(Offset > extent), "Ill-formed if Offset > extent");
        static_assert(!(Count != dynamic_extent && Count > (extent - Offset)),
                      "Ill-formed if Count is not dynamic_extent and Count is greater than (extent - Offset)");
        return span<element_type, detail::DetermineSubspanExtent<extent, Offset, Count>::value>{
            data() + Offset, carb_min(size() - Offset, Count)
        };
    }

    //! Obtains a subspan that is a view over Count elements of this span starting at Offset.
    //!
    //! If \p Count is \ref dynamic_extent, the number of elements in the subspan is \ref size() - `Offset` (i.e. it
    //! ends at the end of `*this`).
    //! Behavior is undefined if either \p Offset or \p Count is out of range. This happens if \p Offset is greater than
    //! \ref size(), or \p Count is not \ref dynamic_extent and \p Count is greater than \ref size() - \p Offset.
    //! The extent of the returned span is always \ref dynamic_extent.
    //! @param Offset The offset within `*this` to start the subspan
    //! @param Count The length of the subspan, or \ref dynamic_extent to indicate the rest of the span.
    //! @returns A subspan of the given range
    constexpr span<element_type, dynamic_extent> subspan(size_type Offset,
                                                         size_type Count = dynamic_extent) const noexcept /*strengthened*/
    {
        CARB_ASSERT(!(Offset > extent), "Behavior is undefined if Offset > extent");
        CARB_ASSERT(!(Count != dynamic_extent && Count > (extent - Offset)),
                    "Behavior is undefined if Count is not dynamic_extent and is greater than Extent - Offset");
        return { data() + Offset, carb_min(size() - Offset, Count) };
    }

private:
    pointer m_p;
};

CARB_ASSERT_INTEROP_SAFE(span<int, 1>);

// Doxygen can ignore the specializations
#ifndef DOXYGEN_BUILD
// Specialization for dynamic_extent
template <class T>
class span<T, dynamic_extent>
{
    // NOTE: This specialization is for Extent == dynamic_extent
public:
    using element_type = T;
    using value_type = std::remove_cv_t<T>;
    using size_type = std::size_t;
    using difference_type = std::ptrdiff_t;
    using pointer = T*;
    using const_pointer = const T*;
    using reference = T&;
    using const_reference = const T&;
    using iterator = omni::detail::PointerIterator<pointer, span>;
    using reverse_iterator = std::reverse_iterator<iterator>;

    constexpr static size_type extent = dynamic_extent;

    constexpr span() noexcept = default;

    template <class It,
              std::enable_if_t<std::is_same<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>::value,
                               bool> = false>
    constexpr span(It first, size_type count) noexcept(noexcept(to_address(first))) /*strengthened*/
        : m_p(to_address(first)), m_size(count)
    {
    }

    template <class It,
              std::enable_if_t<std::is_same<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>::value,
                               bool> = false>
    constexpr span(It first, It last) noexcept(noexcept(to_address(first))) /*strengthened*/
        : m_p(to_address(first)), m_size(last - first)
    {
    }

    template <std::size_t N>
    constexpr span(type_identity_t<element_type> (&arr)[N]) noexcept : m_p(cpp::data(arr)), m_size(N)
    {
    }

    template <class U, std::size_t N, std::enable_if_t<std::is_convertible<U, element_type>::value, bool> = false>
    constexpr span(std::array<U, N>& arr) noexcept : m_p(cpp::data(arr)), m_size(N)
    {
    }

    template <class U, std::size_t N, std::enable_if_t<std::is_convertible<U, element_type>::value, bool> = false>
    constexpr span(const std::array<U, N>& arr) noexcept : m_p(cpp::data(arr)), m_size(N)
    {
    }

    // template< class R >
    // explicit(extent != dynamic_extent)
    // constexpr span( R&& range );
    // (Constructor not available without ranges, but approximate constructor follows)

    template <class R,
              std::enable_if_t<detail::IsConvertibleRange<cpp::remove_cvref_t<R>, pointer>::value &&
                                   !detail::IsStdArray<cpp::remove_cvref_t<R>>::value && // has separate constructor
                                   !detail::IsSpan<cpp::remove_cvref_t<R>>::value && // has separate constructor
                                   !std::is_array<cpp::remove_cvref_t<R>>::value, // has separate constructor
                               bool> = false>
    constexpr span(R&& range) : m_p(range.data()), m_size(range.size())
    {
    }

    template <class U, std::size_t N, std::enable_if_t<std::is_convertible<U, element_type>::value, bool> = false>
    constexpr span(const span<U, N>& source) noexcept : m_p(source.data()), m_size(source.size())
    {
    }

    constexpr span(const span& other) noexcept = default;

    constexpr span& operator=(const span& other) noexcept = default;

    constexpr iterator begin() const noexcept
    {
        return iterator(data());
    }

    constexpr iterator end() const noexcept
    {
        return iterator(data() + size());
    }

    constexpr reverse_iterator rbegin() const noexcept
    {
        return reverse_iterator(end());
    }

    constexpr reverse_iterator rend() const noexcept
    {
        return reverse_iterator(begin());
    }

    constexpr reference front() const
    {
        CARB_ASSERT(!empty(), "Behavior is undefined when calling front() on an empty span");
        return data()[0];
    }

    constexpr reference back() const
    {
        CARB_ASSERT(!empty(), "Behavior is undefined when calling back() on an empty span");
        return data()[size() - 1];
    }

    constexpr reference at(size_type index) const
    {
        CARBLOCAL_THROW_OR_FATAL(index < m_size, "Given index is not within the extent of the span");
        return data()[index];
    }

    constexpr reference operator[](size_type index) const noexcept /*strengthened*/
    {
        CARB_ASSERT(index < size());
        return data()[index];
    }

    constexpr pointer data() const noexcept
    {
        return m_p;
    }

    constexpr size_type size() const noexcept
    {
        return m_size;
    }

    constexpr size_type size_bytes() const noexcept
    {
        CARB_ASSERT(size() <= (dynamic_extent / sizeof(element_type)), "size_bytes() exceeds maximum value of size_type");
        return sizeof(element_type) * size();
    }

    [[nodiscard]] constexpr bool empty() const noexcept
    {
        return size() == 0;
    }

    template <std::size_t Count>
    constexpr span<element_type, Count> first() const
    {
        CARB_ASSERT(!(Count > size()), "Behavior is undefined when Count > size()");
        return span<element_type, Count>{ data(), Count };
    }

    constexpr span<element_type, dynamic_extent> first(size_type Count) const
    {
        CARB_ASSERT(!(Count > size()), "Behavior is undefined when Count > size()");
        return span<element_type, dynamic_extent>{ data(), Count };
    }

    template <std::size_t Count>
    constexpr span<element_type, Count> last() const
    {
        CARB_ASSERT(!(Count > size()), "Behavior is undefined when Count > size()");
        return span<element_type, Count>{ data() + (size() - Count), Count };
    }

    constexpr span<element_type, dynamic_extent> last(size_type Count) const
    {
        CARB_ASSERT(!(Count > size()), "Behavior is undefined when Count > size()");
        return span<element_type, dynamic_extent>{ data() + (size() - Count), Count };
    }

    template <std::size_t Offset, std::size_t Count = dynamic_extent>
    constexpr span<element_type, detail::DetermineSubspanExtent<extent, Offset, Count>::value> subspan() const
    {
        CARB_ASSERT(!(Offset > size()), "Behavior is undefined when Offset > size()");
        CARB_ASSERT(!(Count != dynamic_extent && Count > (size() - Offset)),
                    "Behavior is undefined when Count != dynamic_extent and Count > (size() - Offset)");
        return span<element_type, detail::DetermineSubspanExtent<extent, Offset, Count>::value>{
            data() + Offset, carb_min(size() - Offset, Count)
        };
    }

    constexpr span<element_type, dynamic_extent> subspan(size_type Offset, size_type Count = dynamic_extent) const
    {
        CARB_ASSERT(!(Offset > size()), "Behavior is undefined when Offset > size()");
        CARB_ASSERT(!(Count != dynamic_extent && Count > (size() - Offset)),
                    "Behavior is undefined when Count != dynamic_extent and (Offset + Count) > size()");
        return { data() + Offset, carb_min(size() - Offset, Count) };
    }

private:
    pointer m_p = nullptr;
    size_type m_size = 0;
};

// Specialization for zero
template <class T>
class span<T, 0>
{
    // NOTE: This specialization is for Extent == 0
public:
    using element_type = T;
    using value_type = std::remove_cv_t<T>;
    using size_type = std::size_t;
    using difference_type = std::ptrdiff_t;
    using pointer = T*;
    using const_pointer = const T*;
    using reference = T&;
    using const_reference = const T&;
    using iterator = omni::detail::PointerIterator<pointer, span>;
    using reverse_iterator = std::reverse_iterator<iterator>;

    constexpr static size_type extent = 0;

    constexpr span() noexcept = default;

    template <class It,
              std::enable_if_t<std::is_same<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>::value,
                               bool> = false>
    constexpr explicit span(It first, size_type count) : m_p(to_address(first))
    {
        CARB_UNUSED(count);
        CARB_ASSERT(count == 0, "Behavior is undefined if count != extent");
    }

    template <class It,
              std::enable_if_t<std::is_same<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>::value,
                               bool> = false>
    constexpr explicit span(It first, It last) : m_p(to_address(first))
    {
        CARB_UNUSED(last);
        CARB_ASSERT(first == last, "Behavior is undefined if (last - first) != extent");
    }

    template <std::size_t N>
    constexpr span(type_identity_t<element_type> (&arr)[N]) noexcept : m_p(cpp::data(arr))
    {
        static_assert(N == extent, "Undefined if N != extent");
    }

    template <class U, std::size_t N, std::enable_if_t<std::is_convertible<U, element_type>::value, bool> = false>
    constexpr span(std::array<U, N>& arr) noexcept : m_p(cpp::data(arr))
    {
        static_assert(N == extent, "Undefined if N != extent");
    }

    template <class U, std::size_t N, std::enable_if_t<std::is_convertible<U, element_type>::value, bool> = false>
    constexpr span(const std::array<U, N>& arr) noexcept : m_p(cpp::data(arr))
    {
        static_assert(N == extent, "Undefined if N != extent");
    }

    // template< class R >
    // explicit(extent != dynamic_extent)
    // constexpr span( R&& range );
    // (Constructor not available without ranges, but approximate constructor follows)

    template <class R,
              std::enable_if_t<detail::IsConvertibleRange<cpp::remove_cvref_t<R>, pointer>::value &&
                                   !detail::IsStdArray<cpp::remove_cvref_t<R>>::value && // has separate constructor
                                   !detail::IsSpan<cpp::remove_cvref_t<R>>::value && // has separate constructor
                                   !std::is_array<cpp::remove_cvref_t<R>>::value, // has separate constructor
                               bool> = false>
    constexpr explicit span(R&& range) : m_p(range.data())
    {
        CARB_ASSERT(range.size() == extent, "Behavior is undefined if R.size() != extent");
    }

    template <class U,
              std::size_t N,
              std::enable_if_t<N == dynamic_extent && std::is_convertible<U, element_type>::value, bool> = false>
    constexpr explicit span(const span<U, N>& source) noexcept : m_p(source.data())
    {
        CARB_ASSERT(source.size() == extent, "Behavior is undefined if source.size() != extent");
    }

    template <class U,
              std::size_t N,
              std::enable_if_t<N != dynamic_extent && std::is_convertible<U, element_type>::value, bool> = false>
    constexpr span(const span<U, N>& source) noexcept : m_p(source.data())
    {
        CARB_ASSERT(N == extent, "Behavior is undefined if N != extent");
    }

    constexpr span(const span& other) noexcept = default;

    constexpr span& operator=(const span& other) noexcept = default;

    constexpr iterator begin() const noexcept
    {
        return end();
    }

    constexpr iterator end() const noexcept
    {
        return iterator(m_p);
    }

    constexpr reverse_iterator rbegin() const noexcept
    {
        return rend();
    }

    constexpr reverse_iterator rend() const noexcept
    {
        return reverse_iterator(begin());
    }

    constexpr reference front() const noexcept /*strengthened*/
    {
        CARB_ASSERT(!empty(), "Behavior is undefined if front() is called on an empty span");
        return data()[0];
    }

    constexpr reference back() const noexcept /*strengthened*/
    {
        CARB_ASSERT(!empty(), "Behavior is undefined if back() is called on an empty span");
        return data()[size() - 1];
    }

    constexpr reference at(size_type index) const
    {
        CARBLOCAL_THROW_OR_FATAL(index < size(), "Given index is not within the extent of the span");
        return data()[index];
    }

    constexpr reference operator[](size_type index) const noexcept /*strengthened*/
    {
        CARB_ASSERT(false, "Behavior is undefined if given index is not within the extent of the span");
        return data()[index];
    }

    constexpr pointer data() const noexcept
    {
        return m_p;
    }

    constexpr size_type size() const noexcept
    {
        return 0;
    }

    constexpr size_type size_bytes() const noexcept
    {
        return 0;
    }

    [[nodiscard]] constexpr bool empty() const noexcept
    {
        return true;
    }

    template <std::size_t Count>
    constexpr span<element_type, Count> first() const noexcept /*strengthened*/
    {
        static_assert(Count <= extent, "Program ill-formed if Count > extent");
        return span<element_type, Count>{ data(), Count };
    }

    constexpr span<element_type, dynamic_extent> first(size_type Count) const noexcept /*strengthened*/
    {
        CARB_UNUSED(Count);
        CARB_ASSERT(!(Count > extent), "Behavior is undefined if Count > extent");
        return span<element_type, dynamic_extent>{ data(), Count };
    }

    template <std::size_t Count>
    constexpr span<element_type, Count> last() const noexcept /*strengthened*/
    {
        static_assert(Count == 0, "Program ill-formed if Count > extent");
        return span<element_type, Count>{ data() + (extent - Count), Count };
    }

    constexpr span<element_type, dynamic_extent> last(size_type Count) const noexcept /*strengthened*/
    {
        CARB_UNUSED(Count);
        CARB_ASSERT(!(Count > extent), "Behavior is undefined if Count > extent");
        return span<element_type, dynamic_extent>{ data() + (extent - Count), Count };
    }

    template <std::size_t Offset, std::size_t Count = dynamic_extent>
    constexpr span<element_type, detail::DetermineSubspanExtent<extent, Offset, Count>::value> subspan() const noexcept /*strengthened*/
    {
        static_assert(!(Offset > extent), "Ill-formed if Offset > extent");
        static_assert(!(Count != dynamic_extent && Count > (extent - Offset)),
                      "Ill-formed if Count is not dynamic_extent and Count is greater than (extent - Offset)");
        return span<element_type, detail::DetermineSubspanExtent<extent, Offset, Count>::value>{
            data() + Offset, carb_min(size() - Offset, Count)
        };
    }

    constexpr span<element_type, dynamic_extent> subspan(size_type Offset,
                                                         size_type Count = dynamic_extent) const noexcept /*strengthened*/
    {
        CARB_UNUSED(Offset, Count);
        CARB_ASSERT(!(Offset > extent), "Behavior is undefined if Offset > extent");
        CARB_ASSERT(!(Count != dynamic_extent && Count > (extent - Offset)),
                    "Behavior is undefined if Count is not dynamic_extent and is greater than (extent - Offset)");
        return { data() + Offset, carb_min(size() - Offset, Count) };
    }

private:
    pointer m_p = nullptr;
};

CARB_ASSERT_INTEROP_SAFE(span<int, 0>);
CARB_ASSERT_INTEROP_SAFE(span<int, dynamic_extent>);
#endif

#ifndef DOXYGEN_BUILD
template <class T, std::size_t N, std::enable_if_t<N == dynamic_extent, bool> = false>
span<const cpp::byte, dynamic_extent> as_bytes(span<T, N> s) noexcept
{
    return { reinterpret_cast<const cpp::byte*>(s.data()), s.size_bytes() };
}

template <class T, std::size_t N, std::enable_if_t<N != dynamic_extent, bool> = false>
span<const cpp::byte, sizeof(T) * N> as_bytes(span<T, N> s) noexcept
#else
//! Obtains a view ot the object representation of the elements of the given span
//! @tparam T the `element_type` of the span
//! @tparam N the `extent` of the span
//! @param s The span
//! @returns A \ref span of type `span<const cpp::byte, E>` where `E` is \ref dynamic_extent if `N` is also
//!   \ref dynamic_extent, otherwise `E` is `sizeof(T) * N`.
template <class T, std::size_t N>
auto as_bytes(span<T, N> s) noexcept
#endif
{
    return span<const cpp::byte, sizeof(T) * N>{ reinterpret_cast<const cpp::byte*>(s.data()), s.size_bytes() };
}

#ifndef DOXYGEN_BUILD
template <class T, std::size_t N, std::enable_if_t<N == dynamic_extent, bool> = false>
span<cpp::byte, dynamic_extent> as_writable_bytes(span<T, N> s) noexcept
{
    return { reinterpret_cast<cpp::byte*>(s.data()), s.size_bytes() };
}

template <class T, std::size_t N, std::enable_if_t<N != dynamic_extent, bool> = false>
span<cpp::byte, sizeof(T) * N> as_writable_bytes(span<T, N> s) noexcept
#else
//! Obtains a writable view to the object representation of the elements of the given span
//! @tparam T the `element_type` of the span
//! @tparam N the `extent` of the span
//! @param s The span
//! @returns A \ref span of type `span<cpp::byte, E>` where `E` is \ref dynamic_extent if `N` is also
//!   \ref dynamic_extent, otherwise `E` is `sizeof(T) * N`.
template <class T, std::size_t N>
auto as_writable_bytes(span<T, N> s) noexcept
#endif
{
    return span<cpp::byte, sizeof(T) * N>{ reinterpret_cast<cpp::byte*>(s.data()), s.size_bytes() };
}

#undef CARBLOCAL_THROW_OR_FATAL

#ifndef DOXYGEN_BUILD
// Deduction guides
#    if CARB_HAS_CPP20
template <class It, class EndOrSize>
span(It, EndOrSize) -> span<std::remove_reference_t<std::iter_reference_t<It>>>;

template <class R>
span(R&&) -> span<std::remove_reference_t<std::ranges::range_reference_t<R>>>;
#    endif

template <class T, std::size_t N>
span(T (&)[N]) -> span<T, N>;

template <class T, std::size_t N>
span(std::array<T, N>&) -> span<T, N>;

template <class T, std::size_t N>
span(const std::array<T, N>&) -> span<const T, N>;
#endif

} // namespace carb::cpp

#if CARB_HAS_CPP20 && !defined(DOXYGEN_BUILD)
// Satisfy borrowed_range
template <class T, std::size_t Extent>
constexpr bool std::ranges::enable_borrowed_range<carb::cpp::span<T, Extent>> = true;

// Satisfy view
template <class T, std::size_t Extent>
constexpr bool std::ranges::enable_view<carb::cpp::span<T, Extent>> = true;
#endif
