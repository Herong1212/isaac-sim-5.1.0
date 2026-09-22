// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++17-compatible implementation of select functionality from proposed C++ `<zstring_view>` library.
#pragma once

#include "../Defines.h"

#include "../../omni/detail/PointerIterator.h"
#include "TypeTraits.h"
#include "Memory.h"
#include "StringView.h"

#include <cstddef>
#include <iterator>
#include <string> // for std::string and std::hash
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace carb
{
namespace cpp
{

template <class CharT, class Traits>
class basic_zstring_view;

// GCC instantiates some functions always so they cannot use static_assert, but throwing an exception is allowed from a
// constexpr function (which will act as a compile failure if constexpr) so fall back to that.
#ifndef DOXYGEN_BUILD
#    if CARB_EXCEPTIONS_ENABLED
#        define CARB_ALWAYS_FAIL(msg) throw std::out_of_range(msg)
#        define CARB_THROW_OR_CHECK(check, msg)                                                                        \
            if (!CARB_LIKELY(check))                                                                                   \
            throw std::out_of_range(msg)
#    else
#        define CARB_THROW_OR_CHECK(check, msg) CARB_CHECK((check), msg)
#        if CARB_COMPILER_MSC
#            define CARB_ALWAYS_FAIL(msg) static_assert(false, msg)
#        else
#            define CARB_ALWAYS_FAIL(msg) CARB_FATAL_UNLESS(false, msg)
#        endif
#    endif
#endif

/**
 * The class template basic_zstring_view describes an object that can refer to a constant contiguous sequence of
 * elements with the first element of the sequence at position zero, and where a null-terminator can be found after the
 * last element.
 *
 * This implementation of \c zstring_view is a guaranteed @rstref{ABI- and interop-safe <abi-compatibility>} type.
 * \warning This implementation treats cases where null-terminated strings would be iterated without bound as a
 *  security risk and some functions from `std::basic_string_view` are either not present in this implementation or
 * require passing \ref unsafe_length. The following functions are deleted or changed in this implementation:
 * * `basic_zstring_view(const CharT*)` is deleted, however `basic_zstring_view(const CharT (&)[N])` exists to allow
 *   both literal and bounded arrays to be use in a similar fashion. There also exists
 *   `basic_zstring_view(unsafe_length_t, const CharT*)` to opt in to unsafe behavior.
 * * `find_first_of(const CharT*, size_type = 0)` is deleted, however `find_first_of(basic_zstring_view, size_type = 0)`
 *   will be implicitly invoked for literal strings and bounded arrays. There also exists
 *   `find_first_of(unsafe_length_t, const CharT*, size_type = 0)` to opt in to unsafe behavior.
 * * `find_last_of(const CharT*, size_type = 0)` is deleted, however `find_last_of(basic_zstring_view, size_type = 0)`
 *   will be implicitly invoked for literal strings and bounded arrays. There also exists
 *   `find_last_of(unsafe_length_t, const CharT*, size_type = 0)` to opt in to unsafe behavior.
 * * `find_first_not_of(const CharT*, size_type = 0)` is deleted, however
 *   `find_first_not_of(basic_zstring_view, size_type = 0)`
 *   will be implicitly invoked for literal strings and bounded arrays. There also exists
 *   `find_first_not_of(unsafe_length_t, const CharT*, size_type = 0)` to opt in to unsafe behavior.
 * * `find_last_not_of(const CharT*, size_type = 0)` is deleted, however
 *   `find_last_not_of(basic_zstring_view, size_type = 0)`
 *   will be implicitly invoked for literal strings and bounded arrays. There also exists
 *   `find_last_not_of(unsafe_length_t, const CharT*, size_type = 0)` to opt in to unsafe behavior.
 *
 * While similar to \ref basic_string_view and `std::basic_string_view`, there are a few changes to enforce that views
 * are always null-terminated:
 * * Constructors will `throw` or \ref CARB_CHECK if the view is not null-terminated.
 * * The iterator constructor and Ranges constructor are deleted.
 * * The \ref basic_zstring_view::c_str() function is provided to explicitly indicate support for C-style strings.
 * * \ref basic_string_view::remove_suffix() is not present in `basic_zstring_view`.
 * * \ref substr(size_t)const is distinct from \ref substr(size_t,size_t)const; the former
 *   can return a `basic_zstring_view` but the latter must return a \ref basic_string_view.
 * * Added conversion operators to `std::basic_string_view` and \ref basic_string_view.
 *
 * \note For purposes of this class, "null terminator" refers to a default-initialized `CharT` (e.g. `CharT{}`).
 * @tparam CharT character type
 * @tparam Traits A traits class specifying the operations on the character type. Like for `std::basic_string`,
 *   `Traits::char_type` must name the same type as `CharT` or the program is ill-formed.
 */
template <class CharT, class Traits = std::char_traits<CharT>>
class CARB_VIZ basic_zstring_view
{
    static_assert(!std::is_array_v<CharT>, "CharT must not be an array type");
    static_assert(std::is_trivial_v<CharT> && std::is_standard_layout_v<CharT>,
                  "CharT must be trivial and standard layout");
    static_assert(std::is_same_v<CharT, typename Traits::char_type>, "CharT and Traits::char_type must be the same");

    //! empty string for default constructor
    static inline constexpr CharT nullTerminator = CharT{};

public:
    //! `Traits`
    using traits_type = Traits;
    //! `CharT`
    using value_type = CharT;
    //! `CharT*`
    using pointer = CharT*;
    //! `const CharT*`
    using const_pointer = const CharT*;
    //! `CharT&`
    using reference = CharT&;
    //! `const CharT&`
    using const_reference = const CharT&;
    //! implementation defined constant LegacyRandomAccessIterator and LegacyContiguousIterator whose value_type
    //! is CharT.
    using const_iterator = omni::detail::PointerIterator<const_pointer, basic_zstring_view>;
    //! `const_iterator`
    //! \note `iterator` and `const_iterator` are the same type because string views are views into constant character
    //! sequences.
    using iterator = const_iterator;
    //! `std::reverse_iterator<const_iterator>`
    using const_reverse_iterator = std::reverse_iterator<const_iterator>;
    //! `const_reverse_iterator`
    using reverse_iterator = const_reverse_iterator;
    //! `std::size_t`
    using size_type = std::size_t;
    //! `std::ptrdiff_t`
    using difference_type = std::ptrdiff_t;

    //! Special value. The exact meaning depends on the context.
    static constexpr size_type npos = size_type(-1);

    //! Constructs a basic_zstring_view.
    //! \details Constructs an empty basic_zstring_view. After construction, \ref data() is equal to a pointer to a
    //! null terminator and \ref size() is equal to `0`.
    constexpr basic_zstring_view() noexcept = default;

    //! Constructs a basic_zstring_view.
    //! \details Constructs a view of the same content as \p other. After construction, \ref data() is equal to
    //! `other.data()` and \ref size() is equal to `other.size()`.
    //! @param other The string view to copy.
    constexpr basic_zstring_view(const basic_zstring_view& other) noexcept = default;

    //! Constructs a basic_zstring_view.
    //! \details Constructs a view of the first count characters of the character array starting with the element
    //! pointed by \p s. \p s can contain null characters. The behavior is undefined if `[s, s + count]` is not a valid
    //! range. If exceptions are disabled and `s[count]` is not a null terminator, a \ref CARB_CHECK will occur. After
    //! construction, \ref data() is equal to \p s, and \ref size() is equal to \p count.
    //! @throws std::out_of_range if `s[count]` is not a null terminator and exceptions are enabled.
    //! @param s The character array to view.
    //! @param count The number of characters in \p s to view. `s[count]` must be a null terminator.
    constexpr basic_zstring_view(const CharT* s, size_type count) : m_data(s ? s : &nullTerminator), m_count(count)
    {
        CARB_THROW_OR_CHECK(traits_type::eq(m_data[count], CharT{}), "no null terminator at count");
    }

    //! Constructs a basic_zstring_view.
    //! \details Constructs a view of a string contained in a fixed-size character array \p s, not including the
    //! terminating null character. The length of the view is determined by the count of characters preceding the first
    //! null-terminator. After construction, \ref data() is equal to \p s, and \ref size() is equal to the count of
    //! characters preceding the first null-terminator.
    //! \note This constructor is a Carbonite extension and provided for additional security.
    //! \warning If no null terminator is present in in `[s, s + N)`, this function will throw `std::out_of_range` if
    //!    exceptions are enabled. If exceptions are not enabled, a \ref CARB_CHECK will occur.
    //! @throws std::out_of_range if exceptions are enabled and a null terminator is not found in `[s, s + N)`.
    //! @param s A fixed-size array containing a string. A null terminator must be present in `[s, s + N)`.
    template <size_t N>
    constexpr basic_zstring_view(const CharT (&s)[N]) : m_data(s), m_count(N - 1)
    {
        for (size_type i = 0; i < N - 1; ++i)
        {
            if (traits_type::eq(s[i], CharT{}))
            {
                m_count = i;
                return;
            }
        }
        CARB_THROW_OR_CHECK(traits_type::eq(s[m_count], CharT{}), "no null terminator");
    }

    //! Constructs a basic_zstring_view.
    //! \details Constructs a view of the null-terminated character string pointed to by \p s, not including the
    //! terminating null character. The length of the view is determined as if by `Traits::length(s)`. If \p s is
    //! `nullptr`, the result is an empty string (with \ref data() pointing to a null terminator, as with the default
    //! constructor and \ref size() `0`); otherwise, the behavior is undefined if `[s, s + Traits::length(s)]` is not a
    //! valid range. If \p s is not `nullptr`, after construction \ref data() is equal to \p s, and \ref size() is equal
    //! to `Traits::length(s)`.
    //! \note `basic_zstring_view(const CharT*)` does not exist for security purposes; this constructor exists in its
    //!   place to specifically opt-in to unsafe string lengths.
    //! @param s The null-terminated character string to view.
    constexpr basic_zstring_view(unsafe_length_t, const CharT* s) noexcept
        : m_data(s ? s : &nullTerminator), m_count(s ? traits_type::length(s) : 0)
    {
    }

    /**
     * Iterator constructor is deleted for zstring_view.
     *
     * The rationale behind this is two-fold:
     * * The iteration range would need to include a null terminator that is not at or beyond `end`.
     * * The constructor would need to be O(n) to find the null terminator.
     *
     * Both of these points are a significant departure from string_view and violate our 'no surprises' rule. Instead it
     * is preferred to use a different constructor such as \ref basic_zstring_view(const CharT*,size_type).
     */
    template <class It CARB_NO_DOC(
        ,
        std::enable_if_t<std::is_same_v<typename std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag> &&
                             !detail::IsReverseIterator_v<It>,
                         bool> = false)>
    constexpr basic_zstring_view(It, It) = delete;

    /**
     * Ranges constructor is deleted for zstring_view.
     *
     * The rationale behind this is two-fold:
     * * The range would need to include a null terminator.
     * * The constructor would need to be O(n) to find the null terminator.
     *
     * Both of these points are a significant departure from string_view and violate our 'no surprises' rule. Instead it
     * is preferred to use a different constructor such as \ref basic_zstring_view(const CharT*,size_type).
     */
    template <class R CARB_NO_DOC(
        ,
        std::enable_if_t<cpp::detail::IsConvertibleRange_v<remove_cvref_t<R>, const_pointer> &&
                             !detail::IsBasicStringView_v<remove_cvref_t<R>> && !is_bounded_array_v<remove_cvref_t<R>> &&
                             !detail::IsStdBasicString_v<remove_cvref_t<R>> && !std::is_convertible_v<R, const CharT*> &&
                             !detail::HasOperator_v<remove_cvref_t<R>, basic_string_view<CharT, Traits>> &&
                             !detail::HasOperator_v<remove_cvref_t<R>, basic_zstring_view>,
                         bool> = false)>
    constexpr explicit basic_zstring_view(R&&) = delete;

    //! Implicit conversion from `std::basic_string` to basic_zstring_view.
    //!
    //! \details Construct a basic_zstring_view from a `std::basic_string`.  The construction is implicit to mimic the
    //! behavior of <a
    //! href="https://en.cppreference.com/w/cpp/string/basic_string/operator_basic_string_view">std::basic_string<CharT,Traits,Allocator>::operator
    //! basic_string_view</a>.
    //!
    //! @param s An instance of `std::basic_string`.
    template <typename T,
              typename = std::enable_if_t<!std::is_pointer_v<T> && std::is_same_v<T, std::basic_string<CharT, Traits>>>>
    constexpr basic_zstring_view(const T& s) : m_data(s.data()), m_count(s.size())
    {
    }

    //! basic_zstring_view cannot be constructed from nullptr.
    constexpr basic_zstring_view(std::nullptr_t) = delete;

    //! Assigns a view.
    //! @param view The view to replace `*this` with.
    //! @returns `*this`
    constexpr basic_zstring_view& operator=(const basic_zstring_view& view) noexcept = default;

    //! Returns an iterator to the beginning.
    //! @returns A \ref const_iterator to the first character of the view.
    constexpr const_iterator begin() const noexcept
    {
        return const_iterator(m_data);
    }

    //! Returns an iterator to the beginning.
    //! @returns A \ref const_iterator to the first character of the view.
    constexpr const_iterator cbegin() const noexcept
    {
        return const_iterator(m_data);
    }

    //! Returns an iterator to the end.
    //! @returns A \ref const_iterator to the character following the last character of the view. This character acts as
    //!   a placeholder, attempting to access it results in undefined behavior.
    constexpr const_iterator end() const noexcept
    {
        return const_iterator(m_data + m_count);
    }

    //! Returns an iterator to the end.
    //! @returns A \ref const_iterator to the character following the last character of the view. This character acts as
    //!   a placeholder, attempting to access it results in undefined behavior.
    constexpr const_iterator cend() const noexcept
    {
        return const_iterator(m_data + m_count);
    }

    //! Returns a reverse iterator to the beginning.
    //! @returns A \ref const_reverse_iterator to the first character of the reversed view. It corresponds to the last
    //! character of the non-reversed view.
    constexpr const_reverse_iterator rbegin() const noexcept
    {
        return const_reverse_iterator(end());
    }

    //! Returns a reverse iterator to the beginning.
    //! @returns A \ref const_reverse_iterator to the first character of the reversed view. It corresponds to the last
    //! character of the non-reversed view.
    constexpr const_reverse_iterator crbegin() const noexcept
    {
        return const_reverse_iterator(cend());
    }

    //! Returns a reverse iterator to the end.
    //! @returns a \ref const_reverse_iterator to the character following the last character of the reversed view. It
    //! corresponds to the character preceding the first character of the non-reversed view. This character acts as a
    //! placeholder, attempting to access it results in undefined behavior.
    constexpr const_reverse_iterator rend() const noexcept
    {
        return const_reverse_iterator(begin());
    }

    //! Returns a reverse iterator to the end.
    //! @returns a \ref const_reverse_iterator to the character following the last character of the reversed view. It
    //! corresponds to the character preceding the first character of the non-reversed view. This character acts as a
    //! placeholder, attempting to access it results in undefined behavior.
    constexpr const_reverse_iterator crend() const noexcept
    {
        return const_reverse_iterator(cbegin());
    }

    //! Accesses the specified character.
    //! \details Returns a const reference to the character at the specified position. No bounds checking is performed:
    //! the behavior is undefined if `pos >= size()`.
    //! @param pos The position of the character to return.
    //! @returns A \ref const_reference to the requested character.
    constexpr const_reference operator[](size_type pos) const noexcept /*strengthened*/
    {
        // Though the standard says no bounds checking we do assert
        CARB_ASSERT(pos < m_count);
        return m_data[pos];
    }

    //! Accesses the specified character with bounds checking.
    //! \details Returns a const reference to the character at the specified position. Bounds checking is performed.
    //! \throws std::out_of_range Invalid access: \p pos is at or after \ref size().
    //! @param pos The position of the character to return.
    //! @returns A \ref const_reference to the requested character
    constexpr const_reference at(size_type pos) const
    {
        CARB_THROW_OR_CHECK(pos < m_count, "pos >= size()");
        return m_data[pos];
    }

    //! Accesses the first character.
    //! @returns A \ref const_reference to the first character in the view. The behavior is undefined if empty() is
    //! `true`.
    constexpr const_reference front() const noexcept /*strengthened*/
    {
        CARB_ASSERT(!empty(), "Undefined since empty()");
        return *m_data;
    }

    //! Accesses the last character.
    //! @returns A \ref const_reference to the last character in the view. The behavior is undefined if empty() is
    //! `true`.
    constexpr const_reference back() const noexcept /*strengthened*/
    {
        CARB_ASSERT(!empty(), "Undefined since empty()");
        return m_data[m_count - 1];
    }

    //! Returns a pointer to the first character of a view.
    //! \details Returns a pointer to the underlying null-terminated character array. The pointer is such that the range
    //!   `[data(), data() + size()]` is valid and the values in it correspond to the values of the view.
    //!   `data()[size()]` is guaranteed to be a null terminator.
    //! @returns A \ref const_pointer to the underlying null-terminated character array.
    constexpr const_pointer data() const noexcept
    {
        return m_data;
    }

    //! Returns a pointer to the first character of a view.
    //! \details Returns a pointer to the underlying null-terminated character array. The pointer is such that the range
    //!   `[data(), data() + size()]` is valid and the values in it correspond to the values of the view.
    //!   `data()[size()]` is guaranteed to be a null terminator.
    //! @returns A \ref const_pointer to the underlying null-terminated character array.
    constexpr const_pointer c_str() const noexcept
    {
        return m_data;
    }

    //! Returns the number of characters in the view, not including the null terminator.
    //! \details Returns the number of `CharT` characters in the view, i.e. `std::distance(begin(), end())`.
    //! @returns The number of `CharT` elements in the view.
    constexpr size_type size() const noexcept
    {
        return m_count;
    }

    //! Returns the number of characters in the view, not including the null terminator.
    //! \details Returns the number of `CharT` characters in the view, i.e. `std::distance(begin(), end())`.
    //! @returns The number of `CharT` elements in the view.
    constexpr size_type length() const noexcept
    {
        return m_count;
    }

    //! Returns the maximum number of characters.
    //! \details The largest possible number of char-like objects that can be referred to by a basic_zstring_view.
    //! @returns Maximum number of characters.
    constexpr size_type max_size() const noexcept
    {
        return npos - 1;
    }

    //! Checks whether the view is empty.
    //! \details Checks if the view has no characters, i.e. whether \ref size() is `​0`​.
    //! @returns `true` if the view is empty, `false` otherwise.
    [[nodiscard]] constexpr bool empty() const noexcept
    {
        return m_count == 0;
    }

    //! Shrinks the view by moving its start forward.
    //! \details Moves the start of the view forward by \p n characters. The behavior is undefined if `n > size()`.
    //! @param n Number of characters to remove from the start of the view.
    constexpr void remove_prefix(size_type n) noexcept /*strengthened*/
    {
        CARB_ASSERT(n <= size(), "Undefined since n > size()");
        m_data += n;
        m_count -= n;
    }

    //! Swaps the contents.
    //! \details Exchanges the view with that of \p v.
    //! @param v View to swap with.
    constexpr void swap(basic_zstring_view& v) noexcept
    {
        std::swap(m_data, v.m_data);
        std::swap(m_count, v.m_count);
    }

    //! Copies characters.
    //! \details Copies the substring `[pos, pos + rcount)` to the character array pointed to by \p dest, where `rcount`
    //! is the smaller of \p count and `size() - pos`. Equivalent to `Traits::copy(dest, data() + pos, rcount)`.
    //! \throws std::out_of_range if `pos > size()`.
    //! @param dest Pointer to the destination character string.
    //! @param count Requested substring length.
    //! @param pos Position of first character.
    //! @returns Number of characters copied.
    constexpr size_type copy(CharT* dest, size_type count, size_type pos = 0) const
    {
        CARB_THROW_OR_CHECK(pos <= size(), "pos > size()");
        size_type rcount = ::carb_min(count, size() - pos);
        Traits::copy(dest, m_data + pos, rcount);
        return rcount;
    }

    //! Returns a null-terminated substring.
    //! \details Returns a view of the substring `[pos, size())`.
    //! \throws std::out_of_range if `pos > size()`.
    //! @param pos Position of the first character.
    //! @returns A \ref basic_zstring_view (null terminated) of the substring `[pos, size())`.
    constexpr basic_zstring_view substr(size_t pos) const
    {
        CARB_THROW_OR_CHECK(pos <= size(), "pos > size()");
        return { m_data + pos, size() - pos };
    }

    //! Returns a substring.
    //! \details Returns a view of the substring `[pos, pos + rcount)`, where `rcount` is the smaller of \p count and
    //! `size() - pos.`
    //! \throws std::out_of_range if `pos > size()`.
    //! @param pos Position of the first character.
    //! @param count Requested length.
    //! @returns A \ref basic_string_view (not null-terminated) of the substring
    //!   `[pos, pos + std::min(size() - pos, count))`.
    constexpr basic_string_view<CharT, Traits> substr(size_t pos, size_t count) const
    {
        CARB_THROW_OR_CHECK(pos <= size(), "pos > size()");
        size_t rcount = ::carb_min(count, size() - pos);
        return { m_data + pos, rcount };
    }

    //! Compares two views.
    //! \details The length rlen of the sequences to compare is the smaller of \ref size() and `v.size()`. The function
    //! compares the two views by calling `traits::compare(data(), v.data(), rlen)`, and returns as follows:
    //! * A value less than zero (`<0`) if:
    //!   * `Traits::compare(data(), v.data(), rlen) < 0`, or
    //!   * `Traits::compare(data(), v.data(), rlen) == 0` and `size() < v.size()`.
    //! * A value of zero (`0`) if:
    //!   * `Traits::compare(data(), v.data(), rlen) == 0` and `size() == v.size()`.
    //! * A value greater than zero (`>0`) if:
    //!   * `Traits::compare(data(), v.data(), rlen) > 0`, or
    //!   * `Traits::compare(data(), v.data(), rlen) == 0` and `size() > v.size()`.
    //! @param v View to compare
    //! @returns A negative value if `*this` is less than the other character sequence, `0` if both character sequences
    //!   are equal, positive value if `*this` is greater than the other character sequence. See above.
    constexpr int compare(basic_string_view<CharT, Traits> v) const noexcept
    {
        size_type rlen = ::carb_min(size(), v.size());
        int result = traits_type::compare(data(), v.data(), rlen);
        if (result != 0 || size() == v.size())
            return result;
        return size() < v.size() ? -1 : 1;
    }

    //! Compares a view with a null terminated string.
    //! \details Accepts a null-terminated string.  See \ref compare(basic_string_view<CharT, Traits>) const noexcept
    //! for details. \note This function is not considered harmful, as the memory accessed is bounded by the size of
    //! this string.
    //! @param s A null terminated string to compare. Behavior is undefined if \p s is not a pointer to a
    //!   null-terminated string of \c value_type characters and `size() + 1` is greater than the size of the character
    //!   array.
    //! @returns A negative value if `*this` is less than the other character sequence, `0` if both character sequences
    //!   are equal, positive value if `*this` is greater than the other character sequence. See above.
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr int compare(T&& s) const noexcept
    {
        const_pointer terminator = traits_type::find(std::forward<T>(s), size(), CharT{});
        size_type rlen = terminator ? size_type(terminator - s) : size();
        int result = traits_type::compare(data(), std::forward<T>(s), rlen);
        if (result == 0)
        {
            if (rlen < size())
                return 1;
            else if (traits_type::eq(s[rlen], CharT{}))
                return 0;
            else
                return -1;
        }
        return result;
    }

    //! Compares two views.
    //! \details Equivalent to `substr(pos1, count1).compare(v)`.
    //! \see compare(basic_string_view<CharT, Traits>) const noexcept, substr()
    //! \throws std::out_of_range if `pos1 > size()`.
    //! @param pos1 Position of the first character in this view to compare.
    //! @param count1 Number of characters of this view to compare.
    //! @param v View to compare.
    //! @returns see \ref compare(basic_string_view<CharT, Traits>) const noexcept
    constexpr int compare(size_type pos1, size_type count1, basic_string_view<CharT, Traits> v) const
    {
        return substr(pos1, count1).compare(v);
    }

    //! Compares a substring of \c *this with a null terminated string.
    //! \details Equivalent to `substr(pos1, count1).compare(unsafe_length, v)`.
    //! \see compare(basic_string_view<CharT, Traits>) const noexcept, substr()
    //! \throws std::out_of_range if `pos1 > size()`.
    //! @param pos1 Position of the first character in this view to compare.
    //! @param count1 Number of characters of this view to compare.
    //! @param s A null terminated string to compare. Behavior is undefined if \p s is not a pointer to a null-
    //!   terminated string of \c value_type characters and `count1 + 1` is greater than the size of the character
    //!   array.
    //! @returns see \ref compare(basic_string_view<CharT, Traits>) const noexcept
    constexpr int compare(size_type pos1, size_type count1, const CharT* s) const
    {
        return substr(pos1, count1).compare(s);
    }

    //! Compares two views.
    //! \details Equivalent to `substr(pos1, count1).compare(v.substr(pos2, count2))`.
    //! \see compare(basic_string_view<CharT, Traits>) const noexcept, substr()
    //! \throws std::out_of_range if `pos1 > size()` or if `pos2 > v.size()`.
    //! @param pos1 Position of the first character in this view to compare.
    //! @param count1 Number of characters of this view to compare.
    //! @param v View to compare.
    //! @param pos2 Position of the first character of the given view to compare.
    //! @param count2 Number of characters of the given view to compare.
    //! @returns see \ref compare(basic_string_view<CharT, Traits>) const noexcept
    constexpr int compare(
        size_type pos1, size_type count1, basic_string_view<CharT, Traits> v, size_type pos2, size_type count2) const
    {
        return substr(pos1, count1).compare(v.substr(pos2, count2));
    }

    //! Compares two views.
    //! \details Equivalent to `substr(pos1, count1).compare(basic_string_view<CharT, Traits>(s, count2))`. Behavior is
    //! undefined if
    //! `[s, s+count2)` is not a valid contiguous range.
    //! \see compare(basic_string_view<CharT, Traits>) const noexcept, substr()
    //! \throws std::out_of_range if `pos1 > size()`.
    //! @param pos1 Position of the first character in this view to compare.
    //! @param count1 Number of characters of this view to compare.
    //! @param s Pointer to the character string to compare to.
    //! @param count2 Number of characters of \p s to compare.
    //! @returns see \ref compare(basic_string_view<CharT, Traits>) const noexcept
    constexpr int compare(size_type pos1, size_type count1, const CharT* s, size_type count2) const
    {
        return substr(pos1, count1).compare(basic_string_view<CharT, Traits>(s, count2));
    }

    //! Checks if the string view starts with the given prefix.
    //! \details Effectively returns `substr(0, sv.size()) == sv`.
    //! @param sv A string view which may be a result of implicit conversion from `std::basic_string`.
    //! @returns `true` if the string view begins with the provided prefix, `false` otherwise.
    constexpr bool starts_with(basic_string_view<CharT, Traits> sv) const noexcept
    {
        return substr(0, sv.size()) == sv;
    }

    //! Checks if the string view starts with the given prefix.
    //! \details Effectively returns `!empty() && Traits::eq(front(), ch)`.
    //! @param ch A single character.
    //! @returns `true` if the string view begins with the provided prefix, `false` otherwise.
    constexpr bool starts_with(CharT ch) const noexcept
    {
        return !empty() && traits_type::eq(front(), ch);
    }

    //! Checks if the string view starts with the given prefix.
    //! \details Effectively returns `starts_with(basic_string_view(s, traits_type::length(s, size() + 1)))`.
    //! @param s A null terminated string to compare. Behavior is undefined if \p s is not a pointer to a null-
    //!   terminated string of \c value_type characters and `size() + 1` is greater than the size of the character
    //!   array.
    //! @returns `true` if the string view begins with the provided prefix, `false` otherwise.
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr bool starts_with(T&& s) const noexcept
    {
        size_type i = 0;
        while (i < size())
        {
            if (traits_type::eq(s[i], CharT{}))
            {
                return true;
            }
            if (!traits_type::eq(s[i], m_data[i]))
            {
                return false;
            }
            ++i;
        }
        return traits_type::eq(s[i], CharT{});
    }

    //! Checks if the string view ends with the given suffix.
    //! \details Effectively returns `size() >= sv.size() && compare(size() - sv.size(), npos, sv) == 0`.
    //! @param sv A string view which may be a result of implicit conversion from `std::basic_string`.
    //! @returns `true` if the string view ends with the provided suffix, `false` otherwise.
    constexpr bool ends_with(basic_string_view<CharT, Traits> sv) const noexcept
    {
        return size() >= sv.size() && compare(size() - sv.size(), npos, sv) == 0;
    }

    //! Checks if the string view ends with the given suffix.
    //! \details Effectively returns `!empty() && Traits::eq(back(), ch)`.
    //! @param ch A single character.
    //! @returns `true` if the string view ends with the provided suffix, `false` otherwise.
    constexpr bool ends_with(CharT ch) const noexcept
    {
        return !empty() && traits_type::eq(back(), ch);
    }

    //! Checks if the string view ends with the given prefix. (Unsafe)
    //! \details Effectively returns `ends_with(basic_string_view(s, traits_type::length(s)))`, but it will
    //!   not check more that size() + 1 when looking for a terminator in \p s.
    //! @param s A null terminated string to compare. Behavior is undefined if \p s is not a pointer to a null-
    //!   terminated string of \c value_type characters and `size() + 1` is greater than the size of the character
    //!   array.
    //! @returns `true` if the string view ends with the provided prefix, `false` otherwise.
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr bool ends_with(T&& s) const noexcept
    {
        const CharT* end = traits_type::find(std::forward<T>(s), size() + 1, CharT{});
        if (!end)
            return false;
        auto suffix_size = size_type(end - s);
        return traits_type::compare(m_data + size() - suffix_size, std::forward<T>(s), suffix_size) == 0;
    }

    //! Checks if the string view contains the given substring or character.
    //! \details Effectively `find(sv) != npos`.
    //! @param sv A string view.
    //! @returns `true` if the string view contains the provided substring, `false` otherwise.
    constexpr bool contains(basic_string_view<CharT, Traits> sv) const noexcept
    {
        return find(sv) != npos;
    }

    //! Checks if the string view contains the given substring or character.
    //! \details Effectively `find(c) != npos`.
    //! @param c A single character.
    //! @returns `true` if the string view contains the provided substring, `false` otherwise.
    constexpr bool contains(CharT c) const noexcept
    {
        return find(c) != npos;
    }

    //! Checks if the string view contains the given substring or character.
    //! \details Effectively `find(basic_string_view(s, traits_type::length(size() + 1))) != npos`.
    //! @param s A null terminated string to compare. Behavior is undefined if \p s is not a pointer to a null-
    //!   terminated string of \c value_type characters and `size() + 1` is greater than the size of the character
    //!   array.
    //! @returns `true` if the string view contains the provided substring, `false` otherwise.
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr bool contains(T&& s) const noexcept
    {
        return find(std::forward<T>(s)) != npos;
    }

    //! Find characters in the view.
    //! \details Finds the first substring equal to the given character sequence. Complexity is `O(size()^2)`
    //! at worst.
    //! @param v View to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    constexpr size_type find(basic_string_view<CharT, Traits> v, size_type pos = 0) const noexcept
    {
        for (size_type xpos = pos; xpos + v.size() <= size(); ++xpos)
        {
            if (substr(xpos).starts_with(v))
            {
                return xpos;
            }
        }
        return npos;
    }

    //! Find characters in the view.
    //! \details Finds the first substring equal to the given character sequence. Equivalent to
    //! `find(basic_string_view(std::addressof(ch), 1))`. Complexity is `O(size())` at worst.
    //! @param ch Character to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    constexpr size_type find(CharT ch, size_type pos = 0) const noexcept
    {
        for (size_type xpos = pos; xpos < size(); ++xpos)
        {
            if (traits_type::eq(m_data[xpos], ch))
            {
                return xpos;
            }
        }
        return npos;
    }

    //! Find characters in the view.
    //! \details Finds the first substring equal to the given character sequence. Equivalent to
    //! `find(basic_string_view<CharT, Traits>(s, count), pos)`. Complexity is `O(size()^2)` at worst.
    //! @param s Pointer to a character string to search for.
    //! @param pos Position at which to start the search.
    //! @param count Length of substring to search for.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    constexpr size_type find(const CharT* s, size_type pos, size_type count) const noexcept
    {
        return find(basic_string_view<CharT, Traits>(s, count), pos);
    }

    //! Find characters in the view.
    //! \details Finds the first substring equal to the given character sequence. Equivalent to
    //! `find(basic_string_view(s, traits_type::length(s, size() + 1)), pos)`. Complexity is `O(size()^2)` at worst.
    //! @param s A null terminated string to compare. Behavior is undefined if \p s is not a pointer to a null-
    //!   terminated string of \c value_type characters and `size() + 1` is greater than the size of the character
    //!   array.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr size_type find(T&& s, size_type pos = 0) const noexcept
    {
        // NOTE: We really want to have <= here, because it will handle the case where s is an empty string.
        for (size_type xpos = pos; xpos <= size(); ++xpos)
        {
            if (substr(xpos).starts_with(std::forward<T>(s)))
            {
                return xpos;
            }
        }
        return npos;
    }

    //! Find the last occurrence of a substring.
    //! \details Finds the last substring equal to the given character sequence. Search begins at \p pos, i.e. the found
    //! substring must not being is a position following \p pos. If \ref npos or any value not smaller than `size()-1`
    //! is passed as pos, the whole string will be searched. Complexity is `O(size()^2)` at worst.
    //! @param v View to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    constexpr size_type rfind(basic_string_view<CharT, Traits> v, size_type pos = npos) const noexcept
    {
        if (v.size() > size())
        {
            return npos;
        }

        // Clip the position to our string length.
        for (size_type xpos = ::carb_min(pos, size() - v.size());; xpos--)
        {
            if (substr(xpos).starts_with(v))
            {
                return xpos;
            }
            if (xpos == 0)
            {
                break;
            }
        }
        return npos;
    }

    //! Find the last occurrence of a substring.
    //! \details Finds the last substring equal to the given character sequence. Search begins at \p pos, i.e. the found
    //! substring must not being is a position following \p pos. If \ref npos or any value not smaller than `size()-1`
    //! is passed as pos, the whole string will be searched. Equivalent to
    //! `rfind(basic_string_view(std::addressof(ch), 1), pos)`. Complexity is `O(size())` at worst.
    //! @param ch Character to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    constexpr size_type rfind(CharT ch, size_type pos = npos) const noexcept
    {
        if (empty())
        {
            return npos;
        }

        // Clip the position to our string length.
        for (size_type xpos = ::carb_min(pos, size() - 1);; xpos--)
        {
            if (traits_type::eq(ch, m_data[xpos]))
            {
                return xpos;
            }
            if (xpos == 0)
            {
                break;
            }
        }
        return npos;
    }

    //! Find the last occurrence of a substring.
    //! \details Finds the last substring equal to the given character sequence. Search begins at \p pos, i.e. the found
    //! substring must not being is a position following \p pos. If \ref npos or any value not smaller than `size()-1`
    //! is passed as pos, the whole string will be searched. Equivalent to `rfind(basic_string_view(s, count), pos)`.
    //! Complexity is `O(size()^2)` at worst.
    //! @param s Pointer to a character string to search for.
    //! @param pos Position at which to start the search.
    //! @param count Length of substring to search for.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    constexpr size_type rfind(const CharT* s, size_type pos, size_type count) const noexcept
    {
        return rfind(basic_string_view<CharT, Traits>(s, count), pos);
    }

    //! Find the last occurrence of a substring.
    //! \details Finds the last substring equal to the given character sequence. Search begins at \p pos, i.e. the found
    //! substring must not being is a position following \p pos. If \ref npos or any value not smaller than `size()-1`
    //! is passed as pos, the whole string will be searched. Equivalent to
    //! `rfind(basic_string_view(s, traits_type::length(s, size() + 1)), pos)`.
    //! Complexity is `O(size()^2)` at worst.
    //! @param s A null terminated string to compare. Behavior is undefined if \p s is not a pointer to a null-
    //!   terminated string of \c value_type characters and `size() + 1` is greater than the size of the character
    //!   array.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character of the found substring, or \ref npos if no such substring is found.
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr size_type rfind(T&& s, size_type pos = npos) const noexcept
    {
        // Clip the position to our string length.
        for (size_type xpos = ::carb_min(pos, size());; xpos--)
        {
            if (substr(xpos).starts_with(std::forward<T>(s)))
            {
                return xpos;
            }
            if (xpos == 0)
            {
                break;
            }
        }
        return npos;
    }

    //! Find first occurrence of characters.
    //! \details Finds the first occurrence of any of the characters of \p v in this view, starting as position \p pos.
    //! Complexity is `O(size() * v.size())` at worst.
    //! @param v View to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first occurrence of any character of the substring, or \ref npos if no such character
    //!   is found.
    constexpr size_type find_first_of(basic_string_view<CharT, Traits> v, size_type pos = 0) const noexcept
    {
        if (v.empty())
        {
            return npos;
        }
        for (size_type xpos = pos; xpos < size(); ++xpos)
        {
            if (v.find(m_data[xpos]) != npos)
            {
                return xpos;
            }
        }
        return npos;
    }

    //! Find first occurrence of characters.
    //! \details Equivalent to `find_first_of(basic_string_view(std::addressof(ch), 1), pos)`.
    //! Complexity is `O(size())` at worst.
    //! \see find_first_of(basic_string_view,size_type) const noexcept
    //! @param ch Character to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first occurrence of any character of the substring, or \ref npos if no such character
    //!   is found.
    constexpr size_type find_first_of(CharT ch, size_type pos = 0) const noexcept
    {
        return find(ch, pos);
    }

    //! Find first occurrence of characters.
    //! \details Equivalent to `find_first_of(basic_string_view(s, count), pos)`. Complexity is `O(size() * count)` at
    //! worst.
    //! \see find_first_of(basic_string_view<CharT,Traits>,size_type) const noexcept
    //! @param s Pointer to a string of characters to search for.
    //! @param pos Position at which to start the search.
    //! @param count Length of the string of characters to search for.
    //! @returns Position of the first occurrence of any character of the substring, or \ref npos if no such character
    //!   is found.
    constexpr size_type find_first_of(const CharT* s, size_type pos, size_type count) const noexcept
    {
        return find_first_of(basic_string_view<CharT, Traits>(s, count), pos);
    }

    //! Find first occurrence of characters. (Unsafe)
    //! \details Finds the first occurrence of any of the characters of \p v in this view, starting as position \p pos.
    //! Complexity is `O(size() * traits_type::length(s))` at worst.
    //! @param s Pointer to a null-terminated string of characters to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first occurrence of any character of the substring, or \ref npos if no such character
    //!   is found.
    constexpr size_type find_first_of(unsafe_length_t, const CharT* s, size_type pos = 0) const noexcept
    {
        return find_first_of(basic_string_view<CharT, Traits>(unsafe_length, s), pos);
    }

#ifndef DOXYGEN_BUILD
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr size_type find_first_of(T&& s, size_type pos = 0) const = delete;
#endif

    //! Find last occurrence of characters.
    //! \details Finds the last character equal to one of characters in the given character sequence. Exact search
    //! algorithm is not specified. The search considers only the interval `[0, pos]`. If the character is not present
    //! in the interval, \ref npos will be returned. Complexity is `O(size() * v.size())` at worst.
    //! @param v View to search for.
    //! @param pos Position at which the search is to finish.
    //! @returns Position of the last occurrence of any character of the substring, or \ref npos if no such character
    //! is found.
    constexpr size_type find_last_of(basic_string_view<CharT, Traits> v, size_type pos = npos) const noexcept
    {
        if (v.empty() || empty())
        {
            return npos;
        }

        // Clip the position to our string length.
        for (size_type xpos = ::carb_min(pos, size() - 1);; xpos--)
        {
            if (v.find(m_data[xpos]) != npos)
            {
                return xpos;
            }
            if (xpos == 0)
            {
                break;
            }
        }
        return npos;
    }

    //! Find last occurrence of characters.
    //! \details Finds the last character equal to one of characters in the given character sequence. Exact search
    //! algorithm is not specified. The search considers only the interval `[0, pos]`. If the character is not present
    //! in the interval, \ref npos will be returned. Equivalent to
    //! `find_last_of(basic_string_view(std::addressof(ch), 1), pos)`. Complexity is `O(size())` at worst.
    //! \see find_last_of(basic_string_view<CharT,Traits>,size_type) const noexcept
    //! @param ch Character to search for.
    //! @param pos Position at which the search is to finish.
    //! @returns Position of the last occurrence of any character of the substring, or \ref npos if no such character
    //! is found.
    constexpr size_type find_last_of(CharT ch, size_type pos = npos) const noexcept
    {
        return rfind(ch, pos);
    }

    //! Find last occurrence of characters.
    //! \details Finds the last character equal to one of characters in the given character sequence. Exact search
    //! algorithm is not specified. The search considers only the interval `[0, pos]`. If the character is not present
    //! in the interval, \ref npos will be returned. Equivalent to
    //! `find_last_of(basic_string_view(s, count), pos)`. Complexity is `O(size() * count)` at worst.
    //! \see find_last_of(basic_string_view<CharT,Traits>,size_type) const noexcept
    //! @param s Pointer to a string of characters to search for.
    //! @param pos Position at which the search is to finish.
    //! @param count Length of the string of characters to search for.
    //! @returns Position of the last occurrence of any character of the substring, or \ref npos if no such character
    //! is found.
    constexpr size_type find_last_of(const CharT* s, size_type pos, size_type count) const noexcept
    {
        return find_last_of(basic_string_view<CharT, Traits>(s, count), pos);
    }

    //! Find last occurrence of characters. (Unsafe)
    //! \details Finds the last character equal to one of characters in the given character sequence. Exact search
    //! algorithm is not specified. The search considers only the interval `[0, pos]`. If the character is not present
    //! in the interval, \ref npos will be returned. Complexity is `O(size() * traits_type::length(s))` at worst.
    //! @param s Pointer to a null-terminated string of characters to search for.
    //! @param pos Position at which the search is to finish.
    //! @returns Position of the last occurrence of any character of the substring, or \ref npos if no such character
    //! is found.
    constexpr size_type find_last_of(unsafe_length_t, const CharT* s, size_type pos = npos) const noexcept
    {
        return find_last_of(basic_string_view<CharT, Traits>(unsafe_length, s), pos);
    }

#ifndef DOXYGEN_BUILD
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr size_type find_last_of(T&& s, size_type pos = npos) const = delete;
#endif

    //! Find first absence of characters.
    //! \details Finds the first character not equal to any of the characters in the given character sequence.
    //! Complexity is `O(size() * v.size())` at worst.
    //! @param v View to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_first_not_of(basic_string_view<CharT, Traits> v, size_type pos = 0) const noexcept
    {
        for (size_type xpos = pos; xpos < size(); ++xpos)
        {
            if (v.find(m_data[xpos]) == npos)
            {
                return xpos;
            }
        }
        return npos;
    }

    //! Find first absence of characters.
    //! \details Finds the first character not equal to any of the characters in the given character sequence.
    //! Equivalent to `find_first_not_of(basic_string_view(std::addressof(ch), 1), pos)`. Complexity is `O(size())` at
    //! worst.
    //! \see find_first_not_of(basic_string_view<CharT,Traits>,size_type) const noexcept
    //! @param ch Character to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_first_not_of(CharT ch, size_type pos = 0) const noexcept
    {
        size_type xpos = pos;

        while (xpos < size())
        {
            if (!traits_type::eq(ch, m_data[xpos]))
            {
                return xpos;
            }
            xpos++;
        }
        return npos;
    }

    //! Find first absence of characters.
    //! \details Finds the first character not equal to any of the characters in the given character sequence.
    //! Equivalent to `find_first_not_of(basic_string_view(s, count), pos)`. Complexity is `O(size() * count)` at worst.
    //! \see find_first_not_of(basic_string_view<CharT, Traits>,size_type) const noexcept
    //! @param s Pointer to a string of characters to search for.
    //! @param pos Position at which to start the search.
    //! @param count Length of the string of characters to compare.
    //! @returns Position of the first character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_first_not_of(const CharT* s, size_type pos, size_type count) const noexcept
    {
        return find_first_not_of(basic_string_view<CharT, Traits>(s, count), pos);
    }
    //! Find first absence of characters. (Unsafe)
    //! \details Finds the first character not equal to any of the characters in the given character sequence.
    //! Complexity is `O(size() * traits_type::length(s))` at worst.
    //! @param s Pointer to a null-terminated string of characters to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the first character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_first_not_of(unsafe_length_t, const CharT* s, size_type pos = 0) const noexcept
    {
        return find_first_not_of(basic_string_view<CharT, Traits>(unsafe_length, s), pos);
    }

#ifndef DOXYGEN_BUILD
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr size_type find_first_not_of(T&& s, size_type pos = 0) const = delete;
#endif

    //! Find last absence of characters.
    //! \details Finds the last character not equal to any of the characters in the given character sequence. The search
    //! considers only the interval `[0, pos]`. Complexity is `O(size() * v.size())` at worst.
    //! @param v View to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the last character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_last_not_of(basic_string_view<CharT, Traits> v, size_type pos = 0) const noexcept
    {
        if (empty())
        {
            return npos;
        }

        // Clip the position to our string length.
        for (size_type xpos = ::carb_min(pos, size() - 1);; xpos--)
        {
            if (v.find(m_data[xpos]) == npos)
            {
                return xpos;
            }
            if (xpos == 0)
            {
                break;
            }
        }
        return npos;
    }

    //! Find last absence of characters.
    //! \details Finds the last character not equal to any of the characters in the given character sequence. The search
    //! considers only the interval `[0, pos]`. Equivalent to
    //! `find_last_not_of(basic_string_view(std::addressof(ch), 1), pos)`, Complexity is `O(size())` at worst.
    //! \see find_last_not_of(basic_string_view<CharT,Traits>,size_type) const noexcept
    //! @param ch Character to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the last character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_last_not_of(CharT ch, size_type pos = 0) const noexcept
    {
        if (empty())
        {
            return npos;
        }

        // Clip the position to our string length.
        for (size_type xpos = ::carb_min(pos, size() - 1);; xpos--)
        {
            if (!traits_type::eq(m_data[xpos], ch))
            {
                return xpos;
            }
            if (xpos == 0)
            {
                break;
            }
        }
        return npos;
    }

    //! Find last absence of characters.
    //! \details Finds the last character not equal to any of the characters in the given character sequence. The search
    //! considers only the interval `[0, pos]`. Equivalent to
    //! `find_last_not_of(basic_string_view(s, count), pos)`, Complexity is `O(size() * count)` at worst.
    //! \see find_last_not_of(basic_string_view<CharT,Traits>,size_type) const noexcept
    //! @param s Pointer to a string of characters to compare.
    //! @param pos Position at which to start the search.
    //! @param count Length of the string of characters to compare.
    //! @returns Position of the last character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_last_not_of(const CharT* s, size_type pos, size_type count) const noexcept
    {
        return find_last_not_of(basic_string_view<CharT, Traits>(s, count), pos);
    }

    //! Find last absence of characters. (Unsafe)
    //! \details Finds the last character not equal to any of the characters in the given character sequence. The search
    //! considers only the interval `[0, pos]`. Complexity is `O(size() * traits_type::length(s))` at worst.
    //! @param s Pointer to a null-terminated string of characters to search for.
    //! @param pos Position at which to start the search.
    //! @returns Position of the last character not equal to any of the characters in the given string, or \ref npos if
    //! no such character is found.
    constexpr size_type find_last_not_of(unsafe_length_t, const CharT* s, size_type pos = 0) const noexcept
    {
        return find_last_not_of(basic_string_view<CharT, Traits>(unsafe_length, s), pos);
    }

#ifndef DOXYGEN_BUILD
    template <class T,
              std::enable_if_t<!is_bounded_array_v<remove_cvref_t<T>> && std::is_convertible_v<T, const_pointer>, bool> = false>
    constexpr size_type find_last_not_of(T&& s, size_type pos = 0) const = delete;
#endif

    //! Conversion operator to std::basic_string_view.
    //! This will make `basic_zstring_view` a \a StringViewLike object, which enables conversion to
    //! `std::basic_string<CharT, Traits>` (among other things).
    //! @returns A copy of the string view as a `std::basic_string_view<CharT, Traits>`.
    operator std::basic_string_view<CharT, Traits>() const noexcept
    {
        return { m_data, m_count };
    }

    //! Conversion operator to \ref basic_string_view.
    //! This will make `basic_zstring_view` a \a StringViewLike object, which enables conversion to \ref omni::string
    //! (among other things).
    //! @returns A copy of the string view as a \ref basic_string_view.
    operator basic_string_view<CharT, Traits>() const noexcept
    {
        return { m_data, m_count };
    }

private:
    CARB_VIZ const_pointer m_data = &nullTerminator;
    CARB_VIZ size_type m_count = 0;
};

//! basic_zstring_view<char>
//! @see basic_zstring_view
using zstring_view = basic_zstring_view<char>;
//! basic_zstring_view<wchar_t>
//! @see basic_zstring_view
using wzstring_view = basic_zstring_view<wchar_t>;

#if CARB_HAS_CPP20 && defined(__cpp_char8_t)
//! basic_zstring_view<char8_t>
//! @see basic_zstring_view
using u8zstring_view = basic_zstring_view<char8_t>;
#endif

//! basic_zstring_view<char16_t>
//! @see basic_zstring_view
using u16zstring_view = basic_zstring_view<char16_t>;
//! basic_zstring_view<char32_t>
//! @see basic_zstring_view
using u32zstring_view = basic_zstring_view<char32_t>;

// Ensure these for ABI safety
//! \cond SKIP
#define CARB_IMPL_ENSURE_ABI(cls)                                                                                      \
    static_assert(std::is_standard_layout_v<cls>, #cls " must be standard layout");                                    \
    static_assert(std::is_trivially_copyable_v<cls>, #cls " must be trivially copyable"); /* C++23 requirement */      \
    static_assert(sizeof(cls) == (2 * sizeof(size_t)), #cls "ABI change violation")
CARB_IMPL_ENSURE_ABI(zstring_view);
CARB_IMPL_ENSURE_ABI(wzstring_view);
#if CARB_HAS_CPP20 && defined(__cpp_char8_t)
CARB_IMPL_ENSURE_ABI(u8string_view);
#endif
CARB_IMPL_ENSURE_ABI(u16zstring_view);
CARB_IMPL_ENSURE_ABI(u32zstring_view);
#undef CARB_IMPL_ENSURE_ABI
//! \endcond SKIP

//! @defgroup zstring_view_compare Lexicographically compare two string views.
//! \details. All comparisons are done via the \ref basic_zstring_view::compare() member function (which itself is
//! defined in terms of `Traits::compare()`):
//! * Two views are equal if both the size of \p a and \p b are equal and each character in \p a has an equivalent
//!   character in \p b at the same position.
//! * The ordering comparisons are done lexicographically -- the comparison is performed by a function equivalent to
//!   `std::lexicographical_compare`.
//! Complexity is linear in the size of the views.
//! @{

// [string.view.comparison]

// type_identity_t is used to create a non-deduced context so that one argument participates
// in template argument deduction and the other one gets implicitly converted.
// To overcome an MSVC issue with name mangling some overloads have a dummy default parameter.

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator==(basic_zstring_view<CharT, Traits> a, const CharT* b)
{
    return a.compare(b) == 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator==(const CharT* a, basic_zstring_view<CharT, Traits> b)
{
    return b.compare(a) == 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator!=(basic_zstring_view<CharT, Traits> a, const CharT* b)
{
    return !(a == b);
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator!=(const CharT* a, basic_zstring_view<CharT, Traits> b)
{
    return !(a == b);
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator<(basic_zstring_view<CharT, Traits> a, const CharT* b)
{
    return a.compare(b) < 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator<(const CharT* a, basic_zstring_view<CharT, Traits> b)
{
    return b.compare(a) > 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator>(basic_zstring_view<CharT, Traits> a, const CharT* b)
{
    return b < a;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator>(const CharT* a, basic_zstring_view<CharT, Traits> b)
{
    return b < a;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator<=(basic_zstring_view<CharT, Traits> a, const CharT* b)
{
    return !(a > b);
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator<=(const CharT* a, basic_zstring_view<CharT, Traits> b)
{
    return !(a > b);
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator>=(basic_zstring_view<CharT, Traits> a, const CharT* b)
{
    return !(a < b);
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator>=(const CharT* a, basic_zstring_view<CharT, Traits> b)
{
    return !(a < b);
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator==(basic_zstring_view<CharT, Traits> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) == 0;
}

#ifndef DOXYGEN_BUILD

template <class CharT, class Traits, int = 1>
constexpr bool operator==(basic_zstring_view<CharT, Traits> a, type_identity_t<basic_zstring_view<CharT, Traits>> b)
{
    return a.compare(b) == 0;
}

#endif

#if !CARB_HAS_CPP20 || defined DOXYGEN_BUILD

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator!=(basic_zstring_view<CharT, Traits> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) != 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator<(basic_zstring_view<CharT, Traits> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) < 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator>(basic_zstring_view<CharT, Traits> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) > 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator<=(basic_zstring_view<CharT, Traits> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) <= 0;
}

//! Lexicographically compare two string views.
template <class CharT, class Traits>
constexpr bool operator>=(basic_zstring_view<CharT, Traits> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) >= 0;
}

#    ifndef DOXYGEN_BUILD

template <class CharT, class Traits, int = 1>
constexpr bool operator!=(basic_zstring_view<CharT, Traits> a, type_identity_t<basic_zstring_view<CharT, Traits>> b)
{
    return a.compare(b) != 0;
}

template <class CharT, class Traits, int = 1>
constexpr bool operator<(basic_zstring_view<CharT, Traits> a, type_identity_t<basic_zstring_view<CharT, Traits>> b)
{
    return a.compare(b) < 0;
}

template <class CharT, class Traits, int = 1>
constexpr bool operator>(basic_zstring_view<CharT, Traits> a, type_identity_t<basic_zstring_view<CharT, Traits>> b)
{
    return a.compare(b) > 0;
}

template <class CharT, class Traits, int = 1>
constexpr bool operator<=(basic_zstring_view<CharT, Traits> a, type_identity_t<basic_zstring_view<CharT, Traits>> b)
{
    return a.compare(b) <= 0;
}

template <class CharT, class Traits, int = 1>
constexpr bool operator>=(basic_zstring_view<CharT, Traits> a, type_identity_t<basic_zstring_view<CharT, Traits>> b)
{
    return a.compare(b) >= 0;
}

template <class CharT, class Traits, int = 2>
constexpr bool operator==(type_identity_t<basic_zstring_view<CharT, Traits>> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) == 0;
}

template <class CharT, class Traits, int = 2>
constexpr bool operator!=(type_identity_t<basic_zstring_view<CharT, Traits>> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) != 0;
}

template <class CharT, class Traits, int = 2>
constexpr bool operator<(type_identity_t<basic_zstring_view<CharT, Traits>> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) < 0;
}

template <class CharT, class Traits, int = 2>
constexpr bool operator>(type_identity_t<basic_zstring_view<CharT, Traits>> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) > 0;
}

template <class CharT, class Traits, int = 2>
constexpr bool operator<=(type_identity_t<basic_zstring_view<CharT, Traits>> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) <= 0;
}

template <class CharT, class Traits, int = 2>
constexpr bool operator>=(type_identity_t<basic_zstring_view<CharT, Traits>> a, basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) >= 0;
}


#    endif

#else

template <class CharT, class Traits>
constexpr auto operator<=>(const basic_zstring_view<CharT, Traits> a, const basic_zstring_view<CharT, Traits> b)
{
    return a.compare(b) <=> 0;
}

template <class CharT, class Traits>
constexpr auto operator<=>(const basic_zstring_view<CharT, Traits> a, type_identity_t<basic_zstring_view<CharT, Traits>> b)
{
    return a.compare(b) <=> 0;
}

template <class CharT, class Traits>
constexpr auto operator<=>(const CharT* a, const basic_zstring_view<CharT, Traits> b)
{
    return -b.compare(a) <=> 0;
}

template <class CharT, class Traits>
constexpr auto operator<=>(const basic_zstring_view<CharT, Traits> a, const CharT* b)
{
    return a.compare(b) <=> 0;
}

#endif

//! @}

inline namespace literals
{
inline namespace string_view_literals
{

// Note that literal suffixes that don't start with _ are reserved, in addition we probably don't want to compete with
// the C++17 suffix either.
//! Creates a string view of a character array literal.
//! \note The literal suffix operator `sv` is reserved by C++, so this is `_sv`.
//! @param str Pointer to the beginning of the raw character array literal.
//! @param len Length of the raw character array literal.
//! @returns The \ref basic_zstring_view literal.
constexpr zstring_view operator""_zsv(const char* str, std::size_t len) noexcept
{
    return zstring_view(str, len);
}

// C++ 20 and above have char8_t.
#if CARB_HAS_CPP20 && defined(__cpp_char8_t)
//! \copydoc operator""_sv(const char*,std::size_t) noexcept
constexpr u8zstring_view operator""_zsv(const char8_t* str, std::size_t len) noexcept
{
    return u8zstring_view(str, len);
}
#endif

//! \copydoc operator""_sv(const char*,std::size_t) noexcept
constexpr u16zstring_view operator""_zsv(const char16_t* str, std::size_t len) noexcept
{
    return u16zstring_view(str, len);
}

//! \copydoc operator""_sv(const char*,std::size_t) noexcept
constexpr u32zstring_view operator""_zsv(const char32_t* str, std::size_t len) noexcept
{
    return u32zstring_view(str, len);
}

//! \copydoc operator""_sv(const char*,std::size_t) noexcept
constexpr wzstring_view operator""_zsv(const wchar_t* str, std::size_t len) noexcept
{
    return wzstring_view(str, len);
}

} // namespace string_view_literals
} // namespace literals

} // namespace cpp
} // namespace carb

//! Hash support for string views.
template <class CharT, class Traits>
struct std::hash<carb::cpp::basic_zstring_view<CharT, Traits>>
{
    //! @private
    size_t operator()(const carb::cpp::basic_zstring_view<CharT, Traits>& v) const
    {
        return carb::hashBuffer(v.data(), (uintptr_t)(v.data() + v.size()) - (uintptr_t)(v.data()));
    }
};

#undef CARB_ALWAYS_FAIL
#undef CARB_THROW_OR_CHECK
