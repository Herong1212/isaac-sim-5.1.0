// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <utility>
#include <type_traits>

// ======================================================================
// Implementation of the C++20 feature to detect whether a type is a bounded array (e.g. int[2], float[3]...)
template<class T> struct is_bounded_array: std::false_type {};
template<class T, std::size_t N> struct is_bounded_array<T[N]> : std::true_type {};

// ======================================================================
// When we move to C++17 we can replace and_ with std::conjunction
// Recursively applies std::conditional to all of the template arguments.
template <typename... Conds>
struct and_ : std::true_type
{
};

template <typename Cond, typename... Conds>
struct and_<Cond, Conds...> : std::conditional<Cond::value, and_<Conds...>, std::false_type>::type
{
};

// ======================================================================
// When we move to C++17 we can replace "fold" with C++ fold expression
//   Ex: args && ...
// Recursively applies provided functor to all of the template arguments.
//   Ex: fold(std::logical_and<>(), args...)
template <class F, class A0>
auto fold(F&&, A0&& a0)
{
    return std::forward<A0>(a0);
}

template <class F, class A0, class... As>
auto fold(F&& f, A0&& a0, As&&... as)
{
    return f(std::forward<A0>(a0), fold(f, std::forward<As>(as)...));
}

// ======================================================================
// Removes const& qualifier on a type
template <typename T>
using remove_const_ref = std::remove_const<typename std::remove_reference<T>::type>;

// ======================================================================
// Check to see if a list of types are all of the named type
template <typename MembersAreThisType, typename... MemberType>
using areTypeT = and_<std::is_same<MembersAreThisType, MemberType>...>;

// ======================================================================
// Templatized version of void
template <typename... Ts>
using void_t = void;

// ======================================================================
// This set of templates is used to define a metaprogram "is_detected" that derives from
// std::true_type if the declared templated function exists and std::false_type if not
// (for use in compile-time overload selection, described below).
namespace detail
{
// Matches a call with any type, any templated type, and a variable length list of any types.
// There has to be a typename as the first parameter because another template can't be one.
// Using the void_t<> type defined above allows this parameter to be used for SFINAE selection.
template <typename, template <typename...> class, typename...>
struct is_detected : std::false_type
{
};

// This specialization of detail::is_detected triggers only when the Operation can be instantiated
// with the Arguments. For method checks the "has_X" templates above will be legal types when the
// class mentioned as the first member of "Arguments" implements the method "X". This in turn will
// make void_t<Operation<Arguments...>>> a legal type. In those situations this specialization will
// succeed and is_detected<> will be a std::true_type.
template <template <class...> class Operation, typename... Arguments>
struct is_detected<void_t<Operation<Arguments...>>, Operation, Arguments...> : std::true_type
{
};
}

// This is used only to hide the implementation detail of using the void_t<> template argument to
// guide the SFINAE substitution which detects method overrides. That way the templates below can
// use this more natural pattern:
//      is_detected<has_X, NodeTypeClass>()
// instead of this:
//      detail::is_detected<void_t<>, has_X, NodeTypeClass>()
template <template <class...> class Operation, typename... Arguments>
using is_detected = ::detail::is_detected<void_t<>, Operation, Arguments...>;
