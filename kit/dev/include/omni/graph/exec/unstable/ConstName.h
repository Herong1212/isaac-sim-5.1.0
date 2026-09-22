// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file ConstName.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::ConstName.
#pragma once

#include <carb/Defines.h>
#include <carb/cpp/StringView.h>

#include <omni/String.h>
#include <omni/graph/exec/unstable/Assert.h>
#include <omni/graph/exec/unstable/Types.h>

#include <type_traits>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! An immutable name with fast hash based comparisons.
//!
//! @ref ConstName is a hash of a given string.  This hash is used for all comparisons.  The original string is also
//! stored in this object.
//!
//! Prefer using the overloaded comparison operators (e.g. ==, <, !=) rather than performing comparison operators with
//! the result of @ref toString() or @ref getString().  Using the comparison operators is considerably faster.
//!
//! Comparison of @ref ConstName with `const char*`, @c omni::string, or @c std::string is potentially slow and as such
//! no comparison operators exist to do so.  To compare a @ref ConstName with either a `const char*`, @c omni::string,
//! or @c std::string, you must first explicitly create a @ref ConstName from the string.
//!
//! Classes like `carb::RString` and `pxr::TfToken` also utilize a hash of an original string for fast string
//! comparison.  In these classes, the hash is simply passed around but the string is stored in a global lookup table.
//! When the original string is needed, the hash is used as a lookup in the global table.
//!
//! Unlike `carb::RString` and `pxr::TfToken`, @ref ConstName avoids the global table.  Rather, the original string is
//! stored alongside the hash.  The benefit of avoiding the global table is speed.  Performance testing revealed that
//! when constructing names of objects during graph traversal, the cost of multiple threads reading and writing to the
//! global tables storing `carb::RString` and `pxr::TfToken`'s strings was a bottleneck.
//!
//! If you need speed in threaded code, use @ref ConstName.  If you want to save space, use `carb::RString` or
//! `pxr::TfToken`.
//!
//! This class can safely be passed by pointer across the ABI.  However, since it is not a trivial type, it cannot be
//! passed by value across the ABI. See @ref OMNI_STATIC_ASSERT_CAN_BE_PASSED_BY_VALUE_IN_ABI() for details.
//!
//! @thread_safety Methods in this class are thread safe unless otherwise noted.
class ConstName
{
public:
    //! Construct from a static compile time string.
    template <std::size_t N>
    explicit ConstName(const char (&s)[N]) : m_hash(carb::fnv1aHash(s, N - 1)), m_name(s, N - 1)
    {
        // N-1 so that we don't hash the terminating \0.
        OMNI_STATIC_ASSERT_MUST_BE_PASSED_BY_POINTER_IN_ABI(ConstName);
    }

    //! Construct from a @ref carb::cpp::string_view.
    explicit ConstName(const carb::cpp::string_view& sv) : m_hash(carb::fnv1aHash(sv.data(), sv.size())), m_name(sv)
    {
    }

    //! Construct from a @ref carb::cpp::string_view with an already computed hash.
    explicit ConstName(const carb::cpp::string_view& sv, NameHash hash) : m_hash(hash), m_name(sv)
    {
    }

    //! Construct from empty string.
    ConstName() noexcept : m_hash(CARB_HASH_STRING(""))
    {
    }

    // LCOV_EXCL_START
    //! Implementation detail. Ignore.
    struct BogusArg
    {
    };
    // LCOV_EXCL_STOP

    //! Construct from a @c std::string.
    template <typename T>
    explicit ConstName(const T& s, std::enable_if_t<std::is_same<std::string, T>::value, BogusArg> = {})
        : m_hash(carb::fnv1aHash(s.data(), s.size())), m_name(s)
    {
        // the enable_if disambiguates which constructor a const char* arg should use.
        // the BogusArg type keeps this constructor from being confused with the one with a hash.
    }

    //! Construct from a @c std::string and a pre-computed hash.
    template <typename T>
    explicit ConstName(const T& s, NameHash hash, std::enable_if_t<std::is_same<std::string, T>::value, BogusArg> = {})
        : m_hash(hash), m_name(s)
    {
        // the enable_if disambiguates which constructor a const char* arg should use.
    }

    //! Returns the string used to generate the hash.  For debugging purposes only.
    //!
    //! @thread_safety This method is thread safe.
    const omni::string& getString() const noexcept
    {
        return m_name;
    }

    //! Returns the hash used for comparison.
    //!
    //! Prefer using the overloaded comparison operators (e.g. <, ==) rather than directly calling this method.
    //!
    //! @thread_safety This method is thread safe.
    constexpr uint64_t getHash() const noexcept
    {
        return m_hash;
    }

    //! Converts to a @c std::string.  For debugging purposes only.
    //!
    //! Prefer using @ref getString() over this method, as @ref getString() does not copy any data.
    //!
    //! @thread_safety This method is thread safe.
    std::string toString() const noexcept
    {
        return std::string(m_name.data(), m_name.size()); // may throw
    }

    //! Returns the name as a null-terminated `const char*`.
    //!
    //! @thread_safety This method is thread safe.
    const char* c_str() const noexcept
    {
        return m_name.c_str();
    }

    //! Implicit conversion to @ref carb::cpp::string_view.
    //!
    //! @thread_safety This method is thread safe.
    operator carb::cpp::string_view() const noexcept
    {
        return carb::cpp::string_view(m_name.data(), m_name.size());
    }

private:
    uint64_t m_hash;
    omni::string m_name;
};

//! Compares two @ref ConstName objects.
//!
//! Returns @c true if the hashes are the same.
constexpr bool operator==(const ConstName& lhs, const ConstName& rhs) noexcept
{
    return (lhs.getHash() == rhs.getHash());
}

//! Compares a @ref ConstName with a hash.
//!
//! Returns @c true if the hashes are the same.
constexpr bool operator==(const ConstName& lhs, NameHash rhs) noexcept
{
    return (lhs.getHash() == rhs);
}

//! Compares a hash with a @ref ConstName
//!
//! Returns @c true if the hashes are the same.
constexpr bool operator==(NameHash lhs, const ConstName& rhs) noexcept
{
    return (lhs == rhs.getHash());
}

//! Compares two @ref ConstName objects.
//!
//! Returns @c true if the hashes are not the same.
constexpr bool operator!=(const ConstName& lhs, const ConstName& rhs) noexcept
{
    return (lhs.getHash() != rhs.getHash());
}

//! Compares a @ref ConstName with a hash.
//!
//! Returns @c true if the hashes are not the same.
constexpr bool operator!=(const ConstName& lhs, NameHash rhs) noexcept
{
    return (lhs.getHash() != rhs);
}

//! Compares a hash with a @ref ConstName
//!
//! Returns @c true if the hashes are not the same.
constexpr bool operator!=(NameHash lhs, const ConstName& rhs) noexcept
{
    return (lhs != rhs.getHash());
}

//! Compares two @ref ConstName objects.
//!
//! Returns @c true if the first hash's value is less than the seconds.
constexpr bool operator<(const ConstName& lhs, const ConstName& rhs) noexcept
{
    return (lhs.getHash() < rhs.getHash());
}

//! Compares a @ref ConstName with a hash.
//!
//! Returns @c true if the first hash's value is less than the seconds.
constexpr bool operator<(const ConstName& lhs, NameHash rhs) noexcept
{
    return (lhs.getHash() < rhs);
}

//! Compares a hash with a @ref ConstName
//!
//! Returns @c true if the first hash's value is less than the seconds.
constexpr bool operator<(NameHash lhs, const ConstName& rhs) noexcept
{
    return (lhs < rhs.getHash());
}

//! Output stream operator overload. Outputs the contents of @p str to the stream @p os.
//!
//! @param os Stream to output the string to.
//! @param str The string to output.
//!
//! @return @p os.
//!
//! @throws std::ios_base::failure if an exception is thrown during output.
inline std::ostream& operator<<(std::ostream& os, const ConstName& str)
{
    return (os << str.getString());
}

//! Concatenates @c std::string with a @ref ConstName.  Returns a @c omni::string.
inline auto operator+(const std::string& lhs, const ConstName& rhs)
{
    return lhs + rhs.getString();
}

//! Concatenates @c std::string with a @ref ConstName.  Returns a @c omni::string.
//!
//! Concatenates strings.
inline auto operator+(const ConstName& lhs, const std::string& rhs)
{
    return lhs.getString() + rhs;
}

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni

namespace std
{

//! Hash specialization for std::string
template <>
struct hash<omni::graph::exec::unstable::ConstName>
{
    //! Argument type alias.
    using argument_type = omni::graph::exec::unstable::ConstName;

    //! Result type alias.
    using result_type = std::size_t;

    //! Hash operator
    result_type operator()(const argument_type& x) const noexcept
    {
        return x.getHash();
    }
};

} // namespace std
