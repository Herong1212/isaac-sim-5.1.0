// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<type_traits>` library.
#pragma once

#include "../detail/NoexceptType.h"
#include "detail/ImplInvoke.h"

#include <type_traits>
#include <utility>

namespace carb
{

namespace cpp
{

CARB_DETAIL_PUSH_IGNORE_NOEXCEPT_TYPE()

//! \cond DEV
namespace detail
{

// Base case matches where either `To` or `From` is void or if `is_convertible<From, To>` is false. The conversion in
// this case is only non-throwing if both `From` and `To` are `void`.
template <typename From, typename To, typename = void>
struct is_nothrow_convertible_impl : std::conjunction<std::is_void<From>, std::is_void<To>>
{
};

// If neither `From` nor `To` are void and `From` is convertible to `To`, then we test that such a conversion is
// non-throwing.
template <typename From, typename To>
struct is_nothrow_convertible_impl<
    From,
    To,
    std::enable_if_t<
        std::conjunction<std::negation<std::is_void<From>>, std::negation<std::is_void<To>>, std::is_convertible<From, To>>::value>>
{
    static void test(To) noexcept;

    static constexpr bool value = noexcept(test(std::declval<From>()));
};

} // namespace detail
//! \endcond

//! Determine if \c From can be implicitly-converted to \c To without throwing an exception.
//!
//! This is equivalent to the C++20 \c std::is_nothrow_convertible meta query. While added in C++20, it is required for
//! the C++17 \ref is_nothrow_invocable_r meta query.
template <typename From, typename To>
struct is_nothrow_convertible : std::bool_constant<detail::is_nothrow_convertible_impl<From, To>::value>
{
};

//! \cond DEV
namespace detail
{

// The base case is matched in cases where `invoke_uneval` is an invalid expression. The `Qualify` is always set to void
// by users.
template <typename Qualify, typename Func, typename... TArgs>
struct invoke_result_impl
{
};

template <typename Func, typename... TArgs>
struct invoke_result_impl<decltype(void(invoke_uneval(std::declval<Func>(), std::declval<TArgs>()...))), Func, TArgs...>
{
    using type = decltype(invoke_uneval(std::declval<Func>(), std::declval<TArgs>()...));
};

template <typename Qualify, typename Func, typename... TArgs>
struct is_invocable_impl : std::false_type
{
};

template <typename Func, typename... TArgs>
struct is_invocable_impl<std::void_t<typename invoke_result_impl<void, Func, TArgs...>::type>, Func, TArgs...>
    : std::true_type
{
};

template <typename Qualify, typename Func, typename... TArgs>
struct is_nothrow_invocable_impl : std::false_type
{
};

template <typename Func, typename... TArgs>
struct is_nothrow_invocable_impl<std::void_t<typename invoke_result_impl<void, Func, TArgs...>::type>, Func, TArgs...>
    : std::bool_constant<noexcept(invoke_uneval(std::declval<Func>(), std::declval<TArgs>()...))>
{
};

} // namespace detail
//! \endcond

//! Get the result type of calling \c Func with the \c TArgs pack.
//!
//! If \c Func is callable with the given \c TArgs pack, then this structure has a member typedef named \c type with the
//! return of that call. If \c Func is not callable, then the member typedef does not exist.
//!
//! \code
//! static_assert(std::is_same<int, typename invoke_result<int(*)(char), char>::type>::value);
//! \endcode
//!
//! This is equivalent to the C++17 \c std::invoke_result meta transformation.
//!
//! \see carb::cpp::invoke_result_t
template <typename Func, typename... TArgs>
struct invoke_result : detail::invoke_result_impl<void, Func, TArgs...>
{
};

//! Helper for \ref carb::cpp::invoke_result which accesses the \c type member.
//!
//! \code
//! // Get the proper return type and SFINAE-safe disqualify `foo` when `f(10)` is not valid.
//! template <typename Func>
//! invoke_result_t<Func, int> foo(Func&& f)
//! {
//!     return invoke(std::forward<Func>(f), 10);
//! }
//! \endcode
//!
//! This is equivalent to the C++ \c std::invoke_result_t helper typedef.
template <typename Func, typename... TArgs>
using invoke_result_t = typename invoke_result<Func, TArgs...>::type;

//! Check if the \c Func is invocable with the \c TArgs pack.
//!
//! If \c Func is callable with the given \c TArgs pack, then this structure will derive from \c true_type; otherwise,
//! it will be \c false_type. If \c value is \c true, then `invoke(func, args...)` is a valid expression.
//!
//! \code
//! static_assert(is_invocable<void(*)()>::value);
//! static_assert(!is_invocable<void(*)(int)>::value);
//! static_assert(is_invocable<void(*)(int), int>::value);
//! static_assert(is_invocable<void(*)(long), int>::value);
//! \endcode
//!
//! This is equivalent to the C++20 \c std::is_invocable meta query. The query was added in C++17, but this additionally
//! supports invoking a pointer to a `const&` member function on an rvalue reference.
template <typename Func, typename... TArgs>
struct is_invocable : detail::is_invocable_impl<void, Func, TArgs...>
{
};

//! Check if invoking \c Func with the \c TArgs pack will not throw.
//!
//! If \c Func called with the given \c TArgs pack is callable and marked \c noexcept, then this structure will derive
//! from \c true_type; otherwise, it will be \c false_type. If \c Func is not callable at all, then this will also be
//! \c false_type.
//!
//! This is equivalent to the C++17 \c is_nothrow_invocable meta query.
template <typename Func, typename... TArgs>
struct is_nothrow_invocable : detail::is_nothrow_invocable_impl<void, Func, TArgs...>
{
};

//! \cond DEV
namespace detail
{

template <typename Qualify, typename R, typename Func, typename... TArgs>
struct invocable_r_impl
{
    using invocable_t = std::false_type;

    using invocable_nothrow_t = std::false_type;
};

template <typename Func, typename... TArgs>
struct invocable_r_impl<std::enable_if_t<is_invocable<Func, TArgs...>::value>, void, Func, TArgs...>
{
    using invocable_t = std::true_type;

    using invocable_nothrow_t = is_nothrow_invocable<Func, TArgs...>;
};

// The std::is_void as part of the qualifier is to workaround an MSVC issue where it thinks this partial specialization
// and the one which explicitly lists `R` as void are equally-qualified.
template <typename R, typename Func, typename... TArgs>
struct invocable_r_impl<std::enable_if_t<is_invocable<Func, TArgs...>::value && !std::is_void<R>::value>, R, Func, TArgs...>
{
private:
    // Can't use declval for conversion checks, as it adds an rvalue ref to the type. We want to make sure the result of
    // a returned function can be converted.
    static invoke_result_t<Func, TArgs...> get_val() noexcept;

    template <typename Target>
    static void convert_to(Target) noexcept;

    template <typename TR, typename = decltype(convert_to<TR>(get_val()))>
    static std::true_type test(int) noexcept;

    template <typename TR>
    static std::false_type test(...) noexcept;

    template <typename TR, typename = decltype(convert_to<TR>(get_val()))>
    static std::bool_constant<noexcept(convert_to<TR>(get_val()))> test_nothrow(int) noexcept;

    template <typename TR>
    static std::false_type test_nothrow(...) noexcept;

public:
    using invocable_t = decltype(test<R>(0));

    using invocable_nothrow_t = decltype(test_nothrow<R>(0));
};

} // namespace detail
//! \endcond

//! Check if invoking \c Func with the \c TArgs pack will return \c R.
//!
//! Similar to \ref is_invocable, but additionally checks that the result type is convertible to \c R and that the
//! conversion does not bind a reference to a temporary object. If \c R is \c void, the result can be any type (as any
//! type can be converted to \c void by discarding it). If \c value is \c true, then `invoke_r<R>(func, args...)` is a
//! valid expression.
//!
//! This is equivalent to the C++23 definition of \c is_invocable_r. The function was originally added in C++17, but the
//! specification was altered in C++23 to avoid undefined behavior.
template <typename R, typename Func, typename... TArgs>
struct is_invocable_r : detail::invocable_r_impl<void, R, Func, TArgs...>::invocable_t
{
};

//! Check that invoking \c Func with the \c TArgs pack and converting it to \c R will not throw.
//!
//! This is equivalent to the C++23 definition of \c is_nothrow_invocable_r. The function was originally added in C++17,
//! but the specification was altered in C++23 to avoid undefined behavior.
template <typename R, typename Func, typename... TArgs>
struct is_nothrow_invocable_r : detail::invocable_r_impl<void, R, Func, TArgs...>::invocable_nothrow_t
{
};

CARB_DETAIL_POP_IGNORE_NOEXCEPT_TYPE()

//! Provides the member typedef type that names T (i.e. the identity transformation).
//! This can be used to establish non-deduced contexts in template argument deduction.
template <class T>
struct type_identity
{
    //! The identity transformation.
    using type = T;
};

//! Helper type for \ref type_identity
template <class T>
using type_identity_t = typename type_identity<T>::type;

//! If the type T is a reference type, provides the member typedef type which is the type referred to by T with its
//! topmost cv-qualifiers removed. Otherwise type is T with its topmost cv-qualifiers removed.
template <class T>
struct remove_cvref
{
    //! The type `T` or referred to by `T` (in the case of a reference) with topmost cv-qualifiers removed.
    using type = std::remove_cv_t<std::remove_reference_t<T>>;
};

//! Helper type for \ref remove_cvref
template <class T>
using remove_cvref_t = typename remove_cvref<T>::type;

//! \cond DEV
namespace detail
{
template <class T, class P, class = void>
struct IsConvertibleRange : public std::false_type
{
};

template <class T, class P>
struct IsConvertibleRange<T,
                          P,
                          std::void_t<decltype(std::declval<T>().size()),
                                      std::enable_if_t<std::is_convertible<decltype(std::declval<T>().data()), P>::value>>>
    : public std::true_type
{
};

template <class T, class P>
constexpr bool IsConvertibleRange_v = IsConvertibleRange<T, P>::value;

template <class T>
using IsLegacyInputIterator = std::conjunction<std::is_copy_constructible<T>,
                                               std::is_copy_assignable<T>,
                                               std::is_destructible<T>,
                                               std::is_swappable<T>,
                                               std::is_reference<decltype(*std::declval<T>())>,
                                               std::is_same<decltype(std::declval<T&>()++), T>,
                                               std::is_same<bool, decltype(std::declval<T>() == std::declval<T>())>>;

} // namespace detail
//! \endcond DEV

//! Checks whether T is an array of known bounds.
template <class T>
struct is_bounded_array : std::false_type
{
};

//! Checks whether T is an array of known bounds.
template <class T, std::size_t N>
struct is_bounded_array<T[N]> : std::true_type
{
};

//! Checks whether T is an array of unknown bounds.
template <class T>
struct is_unbounded_array : std::false_type
{
};

//! Checks whether T is an array of unknown bounds.
template <class T>
struct is_unbounded_array<T[]> : std::true_type
{
};

//! Alias for the value member of the `is_bounded_array` template.
template <class T>
constexpr bool is_bounded_array_v = is_bounded_array<T>::value;

//! Alias for the value member of the `is_unbounded_array` template.
template <class T>
constexpr bool is_unbounded_array_v = is_unbounded_array<T>::value;

} // namespace cpp
} // namespace carb
