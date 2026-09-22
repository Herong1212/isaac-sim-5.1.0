// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "../Defines.h"

#include "Utf8Parser.h"

#include <carb/cpp/Optional.h>
#include <carb/cpp/StringView.h>
#include "StringSafe.h"

#include <cstring>
#include <numeric>
#include <string>
#include <algorithm>
#include <sstream>
#include <cctype>
#include <string_view>

namespace carb
{
namespace extras
{
//! \cond DEV
namespace detail
{

// Overload for raw (non-const) arrays.
template <typename T, std::size_t N>
constexpr T* get_data_ptr(T (&t)[N]) noexcept
{
    return std::data(t);
}

// Overload for raw const arrays.
template <typename T, std::size_t N>
constexpr const T* get_data_ptr(const T (&t)[N]) noexcept
{
    return std::data(t);
}

// Overload for pointer types.
// Note: T here is deduced exactly; an array type is not a pointer.
template <typename T>
constexpr std::enable_if_t<std::is_pointer_v<T>, T> get_data_ptr(const T& t) noexcept
{
    return t;
}

// Overload for non-pointer, non-array types (like std::string, std::string_view, containers, etc.)
template <typename T>
constexpr auto get_data_ptr(const T& t) noexcept -> decltype(std::data(t))
{
    if constexpr (std::is_integral_v<T> && sizeof(T) == 1)
        return &t; // Handle single characters
    else
        return std::data(t);
}


/**
 * Primary template for string_traits.
 *
 * For types that do not define a traits_type, we use get_data_ptr
 * to deduce the underlying character type. We remove the pointer
 * and any cv-qualifiers and default to std::char_traits<CharT>.
 */
template <typename T, typename = void>
struct string_traits
{
    using char_type = std::remove_cv_t<std::remove_pointer_t<decltype(get_data_ptr(std::declval<const T&>()))>>;
    using traits_type = std::char_traits<char_type>;
};

/**
 * Specialization for types that already define a traits_type.
 *
 * Here we also assume that the type provides a value_type.
 */
template <typename T>
struct string_traits<T, std::void_t<typename T::traits_type, typename T::value_type>>
{
    using traits_type = typename T::traits_type;
    using char_type = std::remove_cv_t<typename T::value_type>;
};

// Add a specialization for character types
template <typename T>
struct string_traits<T, std::enable_if_t<std::is_integral_v<T> && sizeof(T) == 1>>
{
    using char_type = T;
    using traits_type = std::char_traits<T>;
};

} // namespace detail
//! \endcond DEV

/**
 * Concatenates any StringViewLike objects into a single string.
 *
 * @param[in] args any non-zero number of objects implicitly convertible to carb::cpp::string_view
 *
 * @return a string containing the concatenation of all the provided objects.
 */
template <typename Ret = void, typename... Args>
auto join(const Args&... args)
{
    static_assert(sizeof...(args) > 0, "join requires at least one argument");
    static_assert(
        !std::disjunction_v<std::is_same<std::remove_cv_t<std::remove_reference_t<Args>>, cpp::unsafe_length_t>...>,
        "use join(cpp::unsafe_length, ...) overload instead");

    using First = std::tuple_element_t<0, std::tuple<Args...>>;
    using CharT = typename detail::string_traits<First>::char_type;
    using Traits = typename detail::string_traits<First>::traits_type;
    using RealRet = std::conditional_t<std::is_same_v<Ret, void>, std::basic_string<CharT, Traits>, Ret>;

    auto to_sv = [](const auto& arg) { return cpp::basic_string_view<CharT, Traits>(arg); };

    RealRet result;
    result.reserve((to_sv(args).size() + ...));
    (result.append(to_sv(args)), ...);
    return result;
}

/**
 * Concatenates any StringViewLike objects into a single string.
 *
 * @param[in] first an iterator to the first element of the range.
 * @param[in] last an iterator to the element past the last element of the range.
 * @param[in] delim an object convertible to carb::cpp::string_view to be used as a delimiter.
 *
 * @return a string containing the concatenation of all the provided objects separated by the delimiter.
 * @note Makes a single allocation but requires a double pass for forward iterators.
 */
template <typename Ret = void, typename InputIt, typename Delim>
auto join_iter(InputIt first, InputIt last, const Delim& delim)
{
    using Value = typename std::iterator_traits<InputIt>::value_type;
    using CharT = typename detail::string_traits<Value>::char_type;
    using Traits = typename detail::string_traits<Value>::traits_type;

    auto to_sv = [](const auto& arg) { return cpp::basic_string_view<CharT, Traits>(arg); };

    using IteratorCategory = typename std::iterator_traits<InputIt>::iterator_category;

    using RealRet = std::conditional_t<std::is_same_v<Ret, void>, std::basic_string<CharT, Traits>, Ret>;

    if (first == last)
    {
        return RealRet{};
    }

    RealRet result;
    auto delim_sv = to_sv(delim);
    // reserve for forward iterator, double pass
    if constexpr (std::is_base_of_v<std::forward_iterator_tag, IteratorCategory>)
    {
        auto [count, total_size] =
            std::accumulate(first, last, std::pair<size_t, size_t>{ 0, 0 }, [&](const auto& acc, const auto& x) {
                return std::make_pair(acc.first + 1, acc.second + to_sv(x).size());
            });
        total_size += (count - 1) * delim_sv.size();
        result.reserve(total_size);
    }

    result.append(to_sv(*first));
    for (auto it = std::next(first); it != last; ++it)
    {
        result.append(delim_sv);
        result.append(to_sv(*it));
    }
    return result;
}

/**
 * Concatenates any StringViewLike objects into a single string.
 *
 * @param[in] first an iterator to the first element of the range.
 * @param[in] last an iterator to the element past the last element of the range.
 *
 * @return a string containing the concatenation of all the provided objects.
 * @note Makes a single allocation but requires a double pass for forward iterators.
 */
template <typename Ret = void, typename InputIt>
auto join_iter(InputIt first, InputIt last)
{
    using Value = typename std::iterator_traits<InputIt>::value_type;
    using CharT = typename detail::string_traits<Value>::char_type;
    using Traits = typename detail::string_traits<Value>::traits_type;
    return join_iter<Ret>(first, last, cpp::basic_string_view<CharT, Traits>{});
}

/**
 * Concatenates any StringViewLike objects into a single string.
 *
 * @param[in] cont container of objects convertible to carb::cpp::string_view.
 * @param[in] delim an object convertible to carb::cpp::string_view to be used as a delimiter.

 * @return a string containing the concatenation of all the provided objects.
 * @note Makes a single allocation but requires a double pass for forward iterators.
 */
template <typename Ret = void, typename Container, typename Delim>
auto join_range(const Container& cont, const Delim& delim)
{
    return join_iter<Ret>(std::begin(cont), std::end(cont), delim);
}

/**
 * Concatenates any StringViewLike objects into a single string.
 *
 * @param[in] cont container of objects convertible to carb::cpp::string_view.
 *
 * @return a string containing the concatenation of all the provided objects.
 * @note Makes a single allocation but requires a double pass for forward iterators.
 */
template <typename Ret = void, typename Container>
auto join_range(const Container& cont)
{
    using It = decltype(std::begin(cont));
    using Value = typename std::iterator_traits<It>::value_type;
    using CharT = typename detail::string_traits<Value>::char_type;
    using Traits = typename detail::string_traits<Value>::traits_type;
    return join_range<Ret>(cont, cpp::basic_string_view<CharT, Traits>{});
}

/**
 * Concatenates any StringViewLike objects or null-terminated strings into a single string.
 *
 * @param[in] args any non-zero number of StringViewLike objects or null-terminated strings
 *
 * @return a string containing the concatenation of all the provided strings.
 */
template <typename Ret = void, typename... Args>
auto join(cpp::unsafe_length_t, const Args&... args)
{
    static_assert(sizeof...(args) > 0, "join requires at least one argument");

    using First = std::tuple_element_t<0, std::tuple<Args...>>;
    using CharT = typename detail::string_traits<First>::char_type;

    using Traits = typename detail::string_traits<First>::traits_type;
    using RealRet = std::conditional_t<std::is_same_v<Ret, void>, std::basic_string<CharT, Traits>, Ret>;

    // Here we use std::string_view, which is unsafe (as it will build from a `const char*`)
    // This is ok because this is an `unsafe_length` function
    auto to_sv = [](const auto& arg) { return std::basic_string_view<CharT, Traits>(arg); };

    RealRet result;
    result.reserve((to_sv(args).size() + ...));
    (result.append(to_sv(args)), ...);
    return result;
}

/**
 * Concatenates null-terminated strings into a single string.
 *
 * @param[in] first an iterator to the first element of the range.
 * @param[in] last an iterator to the element past the last element of the range.
 * @param[in] delim an object convertible to std::string_view to be used as a delimiter.
 *
 * @return a string containing the concatenation of all the provided strings separated by the delimiter.
 */
template <typename Ret = void,
          typename InputIt,
          typename CharT = typename detail::string_traits<typename std::iterator_traits<InputIt>::value_type>::char_type,
          typename Traits = typename detail::string_traits<typename std::iterator_traits<InputIt>::value_type>::traits_type>
auto join_iter(cpp::unsafe_length_t,
               InputIt first,
               InputIt last,
               typename cpp::type_identity_t<std::basic_string_view<CharT, Traits>> delim = {})
{
    // Here we use std::string_view, which is unsafe (as it will build from a `const char*`)
    // This is ok because this is an `unsafe_length` function
    using RealRet = std::conditional_t<std::is_same_v<Ret, void>, std::basic_string<CharT>, Ret>;

    auto to_sv = [](auto arg) { return std::basic_string_view<CharT>(arg); };

    if (first == last)
    {
        return RealRet{};
    }

    RealRet result;

    // Reserve for forward iterator, double pass
    if constexpr (std::is_base_of_v<std::forward_iterator_tag, typename std::iterator_traits<InputIt>::iterator_category>)
    {
        auto [count, total_size] =
            std::accumulate(first, last, std::pair<size_t, size_t>{ 0, 0 }, [&](const auto& acc, const auto& x) {
                return std::make_pair(acc.first + 1, acc.second + to_sv(x).size());
            });
        total_size += (count - 1) * delim.size();
        result.reserve(total_size);
    }

    result.append(to_sv(*first));
    for (auto it = std::next(first); it != last; ++it)
    {
        result.append(delim);
        result.append(to_sv(*it));
    }
    return result;
}

/**
 * Concatenates null-terminated strings into a single string.
 *
 * @param[in] cont container of null-terminated strings.
 * @param[in] delim an object convertible to std::basic_string_view to be used as a delimiter.
 *
 * @return a string containing the concatenation of all the provided strings separated by the delimiter.
 */
template <typename Ret = void,
          typename Container,
          typename It = decltype(std::begin(std::declval<Container&>())),
          typename Value = typename std::iterator_traits<It>::value_type,
          typename CharT = typename detail::string_traits<Value>::char_type,
          typename Traits = typename detail::string_traits<Value>::traits_type>
auto join_range(cpp::unsafe_length_t,
                const Container& cont,
                typename cpp::type_identity_t<std::basic_string_view<CharT, Traits>> delim = {})
{
    // Here we use std::string_view, which is unsafe (as it will build from a `const char*`)
    // This is ok because this is an `unsafe_length` function
    return join_iter<Ret>(cpp::unsafe_length, std::begin(cont), std::end(cont), delim);
}

/**
 * Checks if the string begins with the given prefix.
 *
 * @param[in] str a pointer to the null-terminated string. If null, the function will assume an empty string.
 * @param[in] prefix carb::cpp::string_view object.
 *
 * @return true if the string begins with provided prefix, false otherwise.
 */
template <typename T,
          typename = std::enable_if_t<std::is_pointer_v<T> && std::is_same_v<std::remove_const_t<std::remove_pointer_t<T>>, char>>>
inline bool startsWith(T str, const carb::cpp::string_view prefix)
{
    if (str == nullptr)
        return prefix.empty();
    return !carb::cpp::string_view::traits_type::find(str, prefix.size(), char{}) &&
           carb::cpp::string_view::traits_type::compare(str, prefix.data(), prefix.size()) == 0;
}

/**
 * Checks if the string begins with the given prefix.
 *
 * @param[in] str a pointer to the null-terminated string. If null, the function will assume an empty string.
 * @param[in] prefix a pointer to the null-terminated string. If null, the function will assume an empty string.
 *
 * @return true if the string begins with provided prefix, false otherwise.
 */
inline bool startsWith(carb::cpp::unsafe_length_t, const char* str, const char* prefix)
{
    return carb::cpp::string_view(carb::cpp::unsafe_length, str).starts_with(prefix);
}

/**
 * Checks if the string begins with the given prefix.
 *
 * @param[in] str carb::cpp::string_view object.
 * @param[in] prefix a pointer to the null-terminated prefix. If null, the function will assume an empty prefix.
 *
 * @return true if the string begins with provided prefix, false otherwise.
 */
template <typename T,
          typename = std::enable_if_t<std::is_pointer_v<T> && std::is_same_v<std::remove_const_t<std::remove_pointer_t<T>>, char>>>
inline bool startsWith(carb::cpp::string_view str, T prefix)
{
    return str.starts_with(prefix);
}

/**
 * Checks if the string begins with the given prefix.
 *
 * @param[in] str character array.
 * @param[in] prefix character array.
 *
 * @return true if the string begins with provided prefix, false otherwise.
 */
template <size_t N, size_t M>
inline bool startsWith(const char (&str)[N], const char (&prefix)[M])
{
    return carb::cpp::string_view(str).starts_with(prefix);
}

/**
 * Checks if the string begins with the given prefix.
 *
 * @param[in] str character array.
 * @param[in] prefix carb::cpp::string_view object.
 *
 * @return true if the string begins with provided prefix, false otherwise.
 */
template <size_t N>
inline bool startsWith(const char (&str)[N], carb::cpp::string_view prefix)
{
    return carb::cpp::string_view(str).starts_with(prefix);
}


/**
 * Checks if the string begins with the given prefix.
 *
 * @param[in] str carb::cpp::string_view object.
 * @param[in] prefix character array.
 *
 * @return true if the string begins with provided prefix, false otherwise.
 */
template <size_t N>
inline bool startsWith(carb::cpp::string_view str, const char (&prefix)[N])
{
    return str.starts_with(prefix);
}

/**
 * Checks if the string begins with the given prefix.
 *
 * @param[in] str carb::cpp::string_view object.
 * @param[in] prefix carb::cpp::string_view object.
 * @return true if the string begins with provided prefix, false otherwise.
 */
inline bool startsWith(carb::cpp::string_view str, carb::cpp::string_view prefix)
{
    return str.starts_with(prefix);
}

/**
 * Checks if the string ends with the given suffix.
 *
 * @param[in] str carb::cpp::string_view object.
 * @param[in] suffix a pointer to the null-terminated suffix. If null, the function will assume an empty suffix.
 *
 * @return true if the string ends with provided suffix, false otherwise.
 */
template <typename T,
          typename = std::enable_if_t<std::is_pointer_v<T> && std::is_same_v<std::remove_const_t<std::remove_pointer_t<T>>, char>>>
inline bool endsWith(carb::cpp::string_view str, T suffix)
{
    return str.ends_with(suffix);
}

/**
 * Checks if the string ends with the given suffix.
 *
 * @param[in] str a pointer to the null-terminated suffix. If null, the function will assume an empty suffix.
 * @param[in] suffix a pointer to the null-terminated suffix. If null, the function will assume an empty suffix.
 *
 * @return true if the string ends with provided suffix, false otherwise.
 */
inline bool endsWith(carb::cpp::unsafe_length_t, const char* str, const char* suffix)
{
    return carb::cpp::string_view(carb::cpp::unsafe_length, str).ends_with(suffix);
}

/**
 * Checks if the string ends with the given suffix. (Unsafe)
 *
 * @param[in] str a pointer to the null-terminated string. If null, the function will assume an empty string.
 * @param[in] suffix carb::cpp::string_view object.
 *
 * @return true if the string ends with provided suffix, false otherwise.
 */
inline bool endsWith(carb::cpp::unsafe_length_t, const char* str, carb::cpp::string_view suffix)
{
    return carb::cpp::string_view(carb::cpp::unsafe_length, str).ends_with(suffix);
}

/**
 * Checks if the string ends with the given suffix.
 *
 * @param[in] str const character array.
 * @param[in] suffix const character array.
 *
 * @return true if the string ends with provided suffix, false otherwise.
 */
template <size_t N, size_t M>
inline bool endsWith(const char (&str)[N], const char (&suffix)[M])
{
    return carb::cpp::string_view(str).ends_with(suffix);
}

/**
 * Checks if the string ends with the given suffix.
 *
 * @param[in] str carb::cpp::string_view object.
 * @param[in] suffix const character array.
 *
 * @return true if the string ends with provided suffix, false otherwise.
 */
template <size_t N>
inline bool endsWith(carb::cpp::string_view str, const char (&suffix)[N])
{
    return str.ends_with(suffix);
}

/**
 * Checks if the string ends with the given suffix.
 *
 * @param[in] str carb::cpp::string_view object.
 * @param[in] suffix carb::cpp::string_view object.
 *
 * @return true if the string ends with provided suffix, false otherwise.
 */
inline bool endsWith(const carb::cpp::string_view str, const carb::cpp::string_view suffix)
{
    return str.ends_with(suffix);
}

/**
 * Trims start of the provided string from the whitespace characters as classified by the
 * currently installed C locale in-place
 *
 * @param[in,out] str for trimming
 */
inline void trimStringStartInplace(std::string& str)
{
    // Note: using cast of val into `unsigned char` as std::isspace expects unsigned char values
    // https://en.cppreference.com/w/cpp/string/byte/isspace
    str.erase(str.begin(), std::find_if(str.begin(), str.end(), [](std::string::value_type val) {
                  return !std::isspace(static_cast<unsigned char>(val));
              }));
}

/**
 *  Replaces the first occurrence of the searchString in the string with the replaceString.
 * @param[in] string std::string that need to be modified
 * @param[in] searchString carb::cpp::string_view that need to be replaced
 * @param[in] replaceString carb::cpp::string_view that need to be replaced with
 *
 * @return true if replacement occurred, false otherwise
 */
inline bool stringReplaceOccurrence(std::string& string,
                                    carb::cpp::string_view searchString,
                                    carb::cpp::string_view replaceString)
{
    size_t timestampPos = string.find(searchString.data(), 0, searchString.size());
    if (timestampPos != std::string::npos)
    {
        string.replace(timestampPos, searchString.size(), replaceString.data(), replaceString.size());
        return true;
    }
    return false;
}

/**
 * Trims end of the provided string from the whitespace characters as classified by the
 * currently installed C locale in-place
 *
 * @param[in,out] str for trimming
 */
inline void trimStringEndInplace(std::string& str)
{
    // Note: using cast of val into `unsigned char` as std::isspace expects unsigned char values
    // https://en.cppreference.com/w/cpp/string/byte/isspace
    str.erase(std::find_if(str.rbegin(), str.rend(),
                           [](std::string::value_type val) { return !std::isspace(static_cast<unsigned char>(val)); })
                  .base(),
              str.end());
}

/**
 * Trims start and end of the provided string from the whitespace characters as classified by the
 * currently installed C locale in-place
 *
 * @param[in,out] str for trimming
 */
inline void trimStringInplace(std::string& str)
{
    trimStringStartInplace(str);
    trimStringEndInplace(str);
}

/**
 * Creates trimmed (as classified by the currently installed C locale)
 * from the start copy of the provided string
 *
 * @param[in] str string for trimming
 *
 * @return trimmed from the start copy of the provided string
 */
inline std::string trimStringStart(std::string str)
{
    trimStringStartInplace(str);
    return str;
}

/**
 * Creates trimmed (as classified by the currently installed C locale)
 * from the end copy of the provided string
 *
 * @param[in] str string for trimming
 *
 * @return trimmed from the end copy of the provided string
 */
inline std::string trimStringEnd(std::string str)
{
    trimStringEndInplace(str);
    return str;
}

/**
 * Creates trimmed (as classified by the currently installed C locale)
 * from the start and the end copy of the provided string
 *
 * @param[in] str string for trimming
 *
 * @return trimmed from the start and the end copy of the provided string
 */
inline std::string trimString(std::string str)
{
    trimStringInplace(str);
    return str;
}

/**
 * Trims start of the provided valid utf-8 string from the whitespace characters in-place
 *
 * @param[inout] str The UTF-8 string to be trimmed.
 */
inline void trimStringStartInplaceUtf8(std::string& str)
{
    if (str.empty())
    {
        return;
    }

    Utf8Parser::CodePoint decodedCodePoint = 0;
    const Utf8Parser::CodeByte* nonWhitespacePos = str.data();

    while (true)
    {
        const Utf8Parser::CodeByte* nextPos = Utf8Parser::nextCodePoint(
            nonWhitespacePos, Utf8Parser::kNullTerminated, &decodedCodePoint, Utf8Parser::fDecodeUseDefault);

        // If walked through the whole string and non-whitespace encountered then the whole string is just whitespace
        if (!nextPos)
        {
            str.clear();
            return;
        }

        if (Utf8Parser::isSpaceCodePoint(decodedCodePoint))
        {
            // If encountered a whitespace character then proceed to the next code point
            nonWhitespacePos = nextPos;
            continue;
        }

        // Not a whitespace, stop checking
        break;
    }

    const size_t removedCharsCount = (size_t)(nonWhitespacePos - str.data());
    if (removedCharsCount)
    {
        str.erase(0, removedCharsCount);
    }
}

/**
 * Trims end of the provided valid utf-8 string from the whitespace characters in-place
 *
 * @param[inout] str The string to be trimmed.
 */
inline void trimStringEndInplaceUtf8(std::string& str)
{
    if (str.empty())
    {
        return;
    }

    const Utf8Parser::CodeByte* dataBufStart = str.data();
    const Utf8Parser::CodeByte* dataBufEnd = dataBufStart + str.size();
    // Walking the provided string data in codepoints in reverse
    // Note: `Utf8Parser::lastCodePoint` checks the provided data from back to front thus the search of whitespace is
    // in linear time
    Utf8Parser::CodePoint decodedCodePoint{};
    const Utf8Parser::CodeByte* curSearchPosAtEnd = Utf8Parser::lastCodePoint(
        carb::cpp::basic_string_view<Utf8Parser::CodeByte>(dataBufStart, str.size()), &decodedCodePoint);
    const Utf8Parser::CodeByte* prevSearchPosAtEnd = dataBufEnd;
    while (curSearchPosAtEnd != nullptr)
    {
        if (!Utf8Parser::isSpaceCodePoint(decodedCodePoint))
        {
            // Non-space code point was found
            // Remove all symbols starting with the previous codepoint
            if (prevSearchPosAtEnd < dataBufEnd)
            {
                str.erase((std::string::size_type)(prevSearchPosAtEnd - dataBufStart));
            }
            return;
        }

        prevSearchPosAtEnd = curSearchPosAtEnd;
        curSearchPosAtEnd = Utf8Parser::lastCodePoint(
            carb::cpp::basic_string_view<Utf8Parser::CodeByte>(dataBufStart, (size_t)(curSearchPosAtEnd - dataBufStart)),
            &decodedCodePoint);
    }

    // Either the whole string consists from space characters or an invalid sequence was encountered
    str.clear();
}

/**
 * Trims start and end of the provided valid utf-8 string from the whitespace characters in-place
 *
 * @param[inout] str The UTF-8 string to be trimmed.
 */
inline void trimStringInplaceUtf8(std::string& str)
{
    trimStringStartInplaceUtf8(str);
    trimStringEndInplaceUtf8(str);
}

/**
 * Creates trimmed from the start copy of the provided valid utf-8 string
 *
 * @param[in] str The UTF-8 string to be trimmed.
 *
 * @return trimmed from the start copy of the provided string
 */
inline std::string trimStringStartUtf8(std::string str)
{
    trimStringStartInplaceUtf8(str);
    return str;
}

/**
 * Creates trimmed from the end copy of the provided valid utf-8 string
 *
 * @param[in] str The UTF-8 string to be trimmed.
 *
 * @return trimmed from the end copy of the provided string
 */
inline std::string trimStringEndUtf8(std::string str)
{
    trimStringEndInplaceUtf8(str);
    return str;
}

/**
 * Creates trimmed from the start and the end copy of the provided valid utf-8 string
 *
 * @param[in] str The UTF-8 string to be trimmed.
 *
 * @return trimmed from the start and the end copy of the provided string
 */
inline std::string trimStringUtf8(std::string str)
{
    trimStringInplaceUtf8(str);
    return str;
}

/**
 *  Attempts to convert a string to a boolean value.
 *
 *  @param[in] value        The value string to convert.  Only the first character of this string
 *                          will be checked.
 *  @returns An optional boolean value containing `true` if the string starts with '1', 't', 'T',
 *           'y', or 'Y.  Returns an optional boolean value containing `false` if the string
 *           starts with '0', 'f', 'F', 'n', or 'N'.  Returns `carb::cpp::nullopt` if the string
 *           @p value was `nullptr`, an empty string, or could not be converted to a boolean
 *           value.
 */
inline carb::cpp::optional<bool> convertStringToBool(const char* value)
{
    if (isNullOrEmpty(value))
        return carb::cpp::nullopt;

    switch (value[0])
    {
        case '0':
        case 'f':
        case 'F':
        case 'n':
        case 'N':
            return false;

        case '1':
        case 't':
        case 'T':
        case 'y':
        case 'Y':
            return true;

        default:
            break;
    }

    return carb::cpp::nullopt;
}

/** @copydoc convertStringToBool(const char*) */
inline carb::cpp::optional<bool> convertStringToBool(const std::string& value)
{
    return convertStringToBool(value.c_str());
}

/**
 *  Attempts to convert a string to a boolean value.
 *
 *  @param[in] value        The value string to convert.  Only the first character of this string
 *                          will be checked.
 *  @param[in] defaultValue The value to return if the string is invalid (ie: empty) or does not
 *                          contain a value that can be converted to a boolean.
 *  @returns `true` if the string starts with '1', 't', 'T', 'y', or 'Y.  Returns `false` if the
 *           string starts with '0', 'f', 'F', 'n', or 'N'.  Returns @p defaultValue if the string
 *           @p value was `nullptr`, an empty string, or could not be converted to a boolean value.
 */
inline bool convertStringToBool(const char* value, bool defaultValue)
{
    auto result = convertStringToBool(value);

    if (!result)
        return defaultValue;

    return *result;
};

/** @copydoc convertStringToBool(const char*,bool) */
inline bool convertStringToBool(const std::string& value, bool defaultValue)
{
    return convertStringToBool(value.c_str(), defaultValue);
}

/**
 *  Hashes a string and returns a string representing the hash.
 *
 *  @paramp[in] str         The string to be hashed.  This may not be `nullptr`.  This will be
 *                          hashed using the FNV-1a hashing algorithm.
 *  @paramp[in] asHex       Set to `true` to return the hashed string as a hexidecimal string.
 *                          This will not be prefixed with '0x'.  Set to `false` to return the
 *                          hashed string as a decimal string.
 *  @paramp[in] baseHash    The base hash value to start the hashing with.  This can be used to
 *                          add the new string to an existing hashed block to allow a hash
 *                          operation to be performed piecewise.  Leave this at its default value
 *                          to hash only @p str.
 *
 *  @returns A string representing the hashed string in the specified radix.
 */
inline std::string hashStringToString(const char* str, bool asHex = false, uint64_t baseHash = carb::kFnvBasis)
{
    uint64_t hash = carb::hashString(str, baseHash);

    if (asHex)
    {
        std::ostringstream oss;
        oss << std::hex << hash;
        return oss.str();
    }

    return std::to_string(hash);
}

/** @copydoc hashStringToString(const char*, bool, uint64_t) */
inline std::string hashStringToString(const std::string& str, bool asHex = false, uint64_t baseHash = carb::kFnvBasis)
{
    return hashStringToString(str.c_str(), asHex, baseHash);
}

} // namespace extras
} // namespace carb
