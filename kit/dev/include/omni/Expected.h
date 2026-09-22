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
//! \brief Implementation of \c omni::expected and related functions and structures.

#pragma once

#include "detail/ExpectedImpl.h"

#include <utility>

namespace omni
{

template <typename TValue, typename TError>
class expected;

//! The unexpected value of an \ref expected monad. This is used as a convenient mechanism to report the error case when
//! constructing an \c expected return.
//!
//! \code
//! expected<string, Result> foo(bool x)
//! {
//!     // C++17: TError is deduced as `Result`
//!     return unexpected(kResultNotImplemented);
//! }
//! \endcode
template <typename TError>
class unexpected : public omni::detail::UnexpectedImpl<TError>
{
    using base_impl = omni::detail::UnexpectedImpl<TError>;

    template <typename UError>
    friend class unexpected;

public:
    using base_impl::base_impl;

    //! Swap the contents of this instance with \a other.
    //!
    //! If \c TError is \c noexcept swappable or if it is \c void, this operation is also \c noexcept.
    //!
    //! \note
    //! This function only participates in overload resolution if \c TError is swappable or is \c void.
    template <
        typename UError,
        typename IsNoexcept = std::enable_if_t<
            std::conjunction<std::is_same<TError, UError>,
                             typename omni::detail::ExpectedTransformIfNonVoid<std::is_swappable, UError, std::true_type>::type>::value,
            typename omni::detail::ExpectedTransformIfNonVoid<std::is_nothrow_swappable, UError, std::true_type>::type>>
    constexpr void swap(unexpected& other) noexcept(IsNoexcept::value)
    {
        base_impl::swap(static_cast<base_impl&>(other));
    }

    //! Swap the contents of \a lhs with \a rhs.
    //!
    //! If \c UError is \c noexcept swappable or if it is \c void, this operation is also \c noexcept.
    template <typename UError,
              typename IsNoexcept = std::enable_if_t<
                  omni::detail::ExpectedTransformIfNonVoid<std::is_swappable, UError, std::true_type>::type::value,
                  typename omni::detail::ExpectedTransformIfNonVoid<std::is_nothrow_swappable, UError, std::true_type>::type>>
    friend constexpr void swap(unexpected& lhs, unexpected<UError>& rhs) noexcept(IsNoexcept::value)
    {
        lhs.swap(rhs);
    }

    //! If \c TError and \c UError are not \c void, then return `this->error() == other.error()` if they are equality
    //! comparable (it is a compilation failure if they are not). If both \c TError and \c UError are \c void, then
    //! return \c true. If one is \c void and the other is not, this is a compilation failure.
    template <typename UError>
    constexpr bool operator==(unexpected<UError> const& other) const
    {
        static_assert(std::is_void<TError>::value == std::is_void<UError>::value, "Can not compare void and non-void");

        return base_impl::operator==(other);
    }

    //! If \c TError and \c UError are not \c void, then return `lhs.error() == rhs.error()` if they are equality
    //! comparable (it is a compilation failure if they are not). If both \c TError and \c UError are \c void, then
    //! return \c true. If one is \c void and the other is not, this is a compilation failure.
    template <typename UError>
    friend constexpr bool operator==(unexpected const& lhs, unexpected<UError> const& rhs)
    {
        return lhs.operator==(rhs);
    }
};

//! Allow deduction of \c TError from the `unexpected(t)` expression.
template <typename T>
unexpected(T) -> unexpected<T>;

//! An empty `unexpected()` constructor call implies `TError = void`.
unexpected()->unexpected<void>;

//! Used in \ref expected constructors to designate that the error type should be constructed.
struct unexpect_t;

//! A monad which holds either an expected value (the success case) or an unexpected value (the error case).
//!
//! \tparam TValue The type of expected value, returned in the success case.
//! \tparam TError The type of unexpected value, returned in the error case.
//!
//! Simple use of \c expected instances involve checking if an instance \c has_value() before accessing either the
//! \c value() or \c error() member.
//!
//! \code
//! expected<int, string> foo();
//!
//! int main()
//! {
//!     auto ex = foo();
//!     if (ex)
//!         std::cout << "Successfully got " << ex.value() << std::endl;
//!     else
//!         std::cout << "Error: " << ex.error() << std::endl;
//! }
//! \endcode
//!
//! Advanced usage of \c expected involves using the monadic operations, which act on the stored value. This example is
//! equivalent to the above:
//!
//! \code
//! expected<int, string> foo();
//!
//! int main()
//! {
//!     foo()
//!         .transform([](int value) { std::cout << "Successfully got " << value << std::endl; })
//!         .transform_error([](string const& err) { std::cout << "Error: " << err << std::endl; });
//! }
//! \endcode
template <typename TValue, typename TError>
class [[nodiscard]] expected : public omni::detail::ExpectedImpl<TValue, TError>
{
private:
    using base_impl = omni::detail::ExpectedImpl<TValue, TError>;

public:
    //! The type used in success case.
    using value_type = TValue;

    //! The type used in error cases. Unlike the C++23 definition of \c std::expected, this is allowed to be \c void to
    //! match parity with other languages with result monads.
    using error_type = TError;

    //! The \c unexpected type which contains this monad's \ref error_type.
    using unexpected_type = unexpected<error_type>;

    //! Get an \c expected type with \c UValue as the \ref value_type and the same \ref error_type as this.
    template <typename UValue>
    using rebind = expected<UValue, error_type>;

public:
    using base_impl::base_impl;

    //! Create a valued instance through default construction.
    //!
    //! This constructor is only enabled if \ref value_type is default-constructable or \c void.
    //!
    //! This function is \c noexcept if \ref value_type has a \c noexcept default constructor or if it is \c void.
    expected() = default;

    //! Copy an expected instance from another. After this call, `this->has_value() == src.has_value()` and either the
    //! \c value or \c error will have been constructed from the \a src instance.
    //!
    //! This operation is only enabled if both \ref value_type and \ref error_type are copy-constructible or \c void.
    //! This operation is trivial if both \ref value_type and \ref error_type have trivial copy constructors or are
    //! \c void.
    //!
    //! This function is \c noexcept if both \ref value_type and \ref error_type have \c noexcept copy constructors or
    //! are \c void.
    //!
    //! \param src The source to copy from. It will remain unchanged by this operation.
    expected(expected const& src) = default;

    //! Move an expected instance from another. After this call, `this->has_value() == src.has_value()` and either the
    //! \c value or \c error will have been constructed from `std::move(src).value()` or `std::move(src).error()`. Note
    //! that the \c has_value state is unchanged, but the \a src instance will be moved-from.
    //!
    //! This operation is only enabled if both \ref value_type and \ref error_type are move-constructible or \c void.
    //! This operation is trivial if both \ref value_type and \ref error_type have trivial move constructors or are
    //! \c void.
    //!
    //! This function is \c noexcept if both \ref value_type and \ref error_type have \c noexcept move constructors or
    //! are \c void.
    //!
    //! \param src The source to move from. While the \ref has_value state will remain unchanged, the active \a src
    //!            instance will have been moved-from.
    expected(expected&& src) = default;

    //! Copy-assign this instance from another. After this call, `this->has_value() == src.has_value()`.
    //!
    //! Assignment can happen in one of two ways. In the simple case, `this->has_value() == src.has_value()` before the
    //! call, so the copy assignment operator of the underlying type is used. If `this->has_value() != src.has_value()`
    //! before the call, then the active instance of \c this gets the destructor called, then the other type is copy
    //! constructed (generally -- see the "exceptions" section for more info). Note that this destruct-then-construct
    //! process happens even when \ref value_type and \ref error_type are the same.
    //!
    //! This operation is only enabled if both \ref value_type and \ref error_type are copy-assignable or \c void. This
    //! operation is trivial if both \ref value_type and \ref error_type have trivial copy assignment operators and
    //! trivial destructors or are \c void.
    //!
    //! This function is \c noexcept if both \ref value_type and \ref error_type have \c noexcept copy constructors,
    //! copy assignment operators, and \c noexcept destructors or are \c void.
    //!
    //! \note
    //! On type-changing assignment with exceptions enabled, care is taken to ensure the contents of the monad are valid
    //! for use when exceptions are thrown. The "simple" destruct-then-construct process is only followed when copy
    //! construction of the type of the created instance is non-throwing. The exact algorithm used depends on the
    //! available \c noexcept operations (if any), but they involve a stack-based temporary and rollback. Note that a
    //! new instance \e might be constructed before the destruction of the old, so the ordering of these operations
    //! should not be relied on.
    //!
    //! \param src The source to copy from. It will remain unchanged by this operation.
    expected& operator=(expected const& src) = default;

    //! Move-assign this instance from another. After this call, `this->has_value() == src.has_value()`.
    //!
    //! Assignment can happen in one of two ways. In the simple case, `this->has_value() == src.has_value()` before the
    //! call, so the move assignment operator of the underlying type is used. If `this->has_value() != src.has_value()`
    //! before the call, then the active instance of \c this gets the destructor called, then the other type is move
    //! constructed (generally -- see the "exceptions" section for more info). Note that this destruct-then-construct
    //! process happens even when \ref value_type and \ref error_type are the same.
    //!
    //! This operation is only enabled if both \ref value_type and \ref error_type are move-assignable or \c void. This
    //! operation is trivial if both \ref value_type and \ref error_type have trivial move assignment operators and
    //! trivial destructors or are \c void.
    //!
    //! This function is \c noexcept if both \ref value_type and \ref error_type have \c noexcept move constructors,
    //! move assignment operators, and \c noexcept destructors or are \c void.
    //!
    //! \note
    //! On type-changing assignment with exceptions enabled, care is taken to ensure the contents of the monad are valid
    //! for use when exceptions are thrown. The "simple" destruct-then-construct process is only followed when move
    //! construction of the type of the created instance is non-throwing. The exact algorithm used depends on the
    //! available \c noexcept operations (if any), but they involve a stack-based temporary and rollback. Note that a
    //! new instance \e might be constructed before the destruction of the old, so the ordering of these operations
    //! should not be relied on.
    //!
    //! \param src The source to move from. While the \ref has_value will remain unchanged, the active \a src instance
    //!            will have been moved-from.
    expected& operator=(expected&& src) = default;

    //! Destroy this instance by calling the destructor of the active value.
    //!
    //! This operation is trivial if both \ref value_type and \ref error_type are trivially destructible. This function
    //! is \c noexcept if both \ref value_type and \ref error_type have \c noexcept destructors.
    ~expected() = default;

    //! Construct an instance by forwarding \a src to construct the \ref value_type by direct initialization. After this
    //! call, `this->has_value()` will be true.
    //!
    //! This constructor is only enabled when all of the following criteria is met:
    //!
    //! 1. \ref value_type is constructible from \c UValue
    //! 2. \ref value_type is not \c void
    //! 3. `remove_cvref_t<UValue>` is not \c in_place_t
    //! 4. `remove_cvref_t<UValue>` is not `expected<TValue, TError>` (the copy or move constructor is used instead)
    //! 5. `remove_cvref_t<UValue>` is not a specialization of \c unexpected
    //! 6. if \ref value_type is \c bool, then \c UValue can not be a specialization of \c expected
    //!
    //! This constructor is \c explicit if conversion from \c UValue to \ref value_type is \c explicit.
    template <typename UValue = TValue,
              std::enable_if_t<omni::detail::IsExpectedDirectConstructibleFrom<UValue, expected>::is_explicit, bool> = true>
    constexpr explicit expected(UValue&& src) : base_impl(std::in_place, std::forward<UValue>(src))
    {
    }

#ifndef DOXYGEN_BUILD
    template <typename UValue = TValue,
              std::enable_if_t<!omni::detail::IsExpectedDirectConstructibleFrom<UValue, expected>::is_explicit, bool> = false>
    constexpr expected(UValue&& src) : base_impl(std::in_place, std::forward<UValue>(src))
    {
    }
#endif

    //! Convert from \a src by direct initialization from the active element. If `src.has_value()`, then this instance
    //! will have a value constructed from `src.value()`; otherwise, this instance will have an error constructed from
    //! `src.error()`. After this call, `this->has_value() == src.has_value()`.
    //!
    //! This converting constructor is not \c explicit if conversion from \c UValue to \c TValue and \c UError to
    //! \c TError are not \c explicit. Conversion from \c void to \c void is also considered a non \c explicit
    //! conversion. Stated differently, a \c UExpected is implicitly convertible to a \c TExpected if both of its
    //! components are implicitly convertible.
    //!
    //! \note
    //! The rules for this are almost identical to \c std::expected, but they are expanded to support \c void as the
    //! \ref error_type. Any case where the C++ Standard makes an exception when \ref value_type is \c void, that same
    //! exception has been extended to \ref error_type of \c void.
    template <typename UValue,
              typename UError,
              std::enable_if_t<omni::detail::IsExpectedCopyConstructibleFrom<expected<UValue, UError>, expected>::is_explicit,
                               bool> = true>
    constexpr explicit expected(expected<UValue, UError> const& src)
        : base_impl(::omni::detail::ExpectedCtorBypass{}, src)
    {
    }

#ifndef DOXYGEN_BUILD
    template <typename UValue,
              typename UError,
              std::enable_if_t<!omni::detail::IsExpectedCopyConstructibleFrom<expected<UValue, UError>, expected>::is_explicit,
                               bool> = false>
    constexpr expected(expected<UValue, UError> const& src) : base_impl(::omni::detail::ExpectedCtorBypass{}, src)
    {
    }
#endif

    //! Convert from \a src by direct initialization from the active element. If `src.has_value()`, then this instance
    //! will have a value constructed from `move(src).value()`; otherwise, this instance will have an error constructed
    //! from `move(src).error()`. After this call, `this->has_value() == src.has_value()`. Note that the contents of
    //! \a src are moved-from, but not destructed, so the instances is still accessable.
    //!
    //! This converting constructor is not \c explicit if conversion from \c UValue to \c TValue and \c UError to
    //! \c TError are not \c explicit. Conversion from \c void to \c void is also considered a non \c explicit
    //! conversion. Stated differently, a \c UExpected is implicitly convertible to a \c TExpected if both of its
    //! components are implicitly convertible.
    //!
    //! \note
    //! The rules for this are almost identical to \c std::expected, but they are expanded to support \c void as the
    //! \ref error_type. Any case where the C++ Standard makes an exception when \ref value_type is \c void, that same
    //! exception has been extended to \ref error_type of \c void.
    template <typename UValue,
              typename UError,
              std::enable_if_t<omni::detail::IsExpectedMoveConstructibleFrom<expected<UValue, UError>, expected>::is_explicit,
                               bool> = true>
    constexpr explicit expected(expected<UValue, UError>&& src)
        : base_impl(::omni::detail::ExpectedCtorBypass{}, std::move(src))
    {
    }

#ifndef DOXYGEN_BUILD
    template <typename UValue,
              typename UError,
              std::enable_if_t<!omni::detail::IsExpectedMoveConstructibleFrom<expected<UValue, UError>, expected>::is_explicit,
                               bool> = false>
    constexpr expected(expected<UValue, UError>&& src) : base_impl(::omni::detail::ExpectedCtorBypass{}, std::move(src))
    {
    }
#endif

    //! Construct an instance using \a src as the error value. The constructed instance `!this->has_value()` and the
    //! `this->error()` will have been constructed by `src.error()`.
    //!
    //! This constructor is not \c explicit if the conversion from the source \c UError to \c TError is not explicit.
    //! Stated differently, an `unexpected<UError>` is implicitly convertible to a `expected<TValue, TError>` (of
    //! arbitrary `TValue`) if `UError` is implicitly convertible to a `TError`.
    //!
    //! If \c TError is \c void, then \c UError must also be \c void to construct an instance.
    template <typename UError,
              std::enable_if_t<std::conjunction<std::is_constructible<TError, UError const&>,
                                                std::negation<std::is_convertible<UError const&, TError>>>::value,
                               bool> = true>
    constexpr explicit expected(unexpected<UError> const& src) : base_impl(unexpect, src.error())
    {
    }

#ifndef DOXYGEN_BUILD
    template <typename UError,
              std::enable_if_t<std::conjunction<std::is_constructible<TError, UError const&>,
                                                std::is_convertible<UError const&, TError>>::value,
                               bool> = false>
    constexpr expected(unexpected<UError> const& src) : base_impl(unexpect, src.error())
    {
    }
#endif

    //! Construct an instance using \a src as the error value. The constructed instance `!this->has_value()` and the
    //! `this->error()` will have been constructed by `std::move(src).error()`.
    //!
    //! This constructor is not \c explicit if the conversion from the source \c UError to \c TError is not explicit.
    //! Stated differently, an `unexpected<UError>` is implicitly convertible to a `expected<TValue, TError>` (of
    //! arbitrary `TValue`) if `UError` is implicitly convertible to a `TError`.
    //!
    //! If \c TError is \c void, then \c UError must also be \c void to construct an instance.
    template <typename UError,
              std::enable_if_t<std::conjunction<std::is_constructible<TError, UError&&>,
                                                std::negation<std::is_convertible<UError&&, TError>>>::value,
                               bool> = true>
    constexpr explicit expected(unexpected<UError>&& src) : base_impl(unexpect, std::move(src).error())
    {
    }

#ifndef DOXYGEN_BUILD
    template <typename UError,
              std::enable_if_t<std::conjunction<std::is_constructible<TError, UError&&>, std::is_convertible<UError&&, TError>>::value,
                               bool> = false>
    constexpr expected(unexpected<UError>&& src) : base_impl(unexpect, std::move(src).error())
    {
    }
#endif

    //! Test if this instance has a \c value. If this returns \c true, then a call to \c value() will succeed, while a
    //! call to \c error() would not. If this returns \c false, a call to \c error() will succeed, while a call to
    //! \c value() would not.
    constexpr bool has_value() const noexcept
    {
        return this->m_state == ::omni::detail::ExpectedState::eSUCCESS;
    }

    //! \copydoc expected::has_value() const
    //!
    //! \see has_value
    constexpr explicit operator bool() const noexcept
    {
        return this->has_value();
    }

#ifdef DOXYGEN_BUILD
    //! If this instance \c has_value(), the value is returned by `&`.
    //!
    //! If this instance does not have a value, this call will not succeed. If exceptions are enabled, then a
    //! \c bad_expected_access exception is thrown containing the copied contents of \c error(). If exceptions are
    //! disabled, then the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, the return type is exactly \c void instead of `void&` (which is illegal).
    constexpr value_type& value() &;

    //! If this instance \c has_value(), the value is returned by `const&`.
    //!
    //! If this instance does not have a value, this call will not succeed. If exceptions are enabled, then a
    //! \c bad_expected_access exception is thrown containing the copied contents of \c error(). If exceptions are
    //! disabled, then the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, the return type is exactly \c void instead of `void const&` (which is illegal).
    constexpr value_type const& value() const&;

    //! If this instance \c has_value(), the value is returned by `&&`.
    //!
    //! If this instance does not have a value, this call will not succeed. If exceptions are enabled, then a
    //! \c bad_expected_access exception is thrown containing the moved contents of \c error(). If exceptions are
    //! disabled, then the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, the return type is exactly \c void instead of `void&&` (which is illegal).
    constexpr value_type&& value() &&;

    //! If this instance \c has_value(), the value is returned by `const&&`.
    //!
    //! If this instance does not have a value, this call will not succeed. If exceptions are enabled, then a
    //! \c bad_expected_access exception is thrown containing the copied contents of \c error(). If exceptions are
    //! disabled, then the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, the return type is exactly \c void instead of `void const&&` (which is illegal).
    constexpr value_type const&& value() const&&;

    //! If this instance \c has_value(), the value is copied and returned; otherwise, a \ref value_type instance is
    //! constructed from \a default_value.
    //!
    //! \note
    //! If \ref value_type is \c void, this member function does not exist. If \ref value_type is not copy
    //! constructible, this will fail to compile in the immediate context (not SFINAE-safe).
    //!
    //! \tparam UValue Must be convertible to \ref value_type.
    template <typename UValue>
    constexpr value_type value_or(UValue&& default_value) const&;

    //! If this instance \c has_value(), the value is moved and returned; otherwise, a \ref value_type instance is
    //! constructed from \a default_value.
    //!
    //! \note
    //! If \ref value_type is \c void, this member function does not exist. If \ref value_type is not move
    //! constructible, this will fail to compile in the immediate context (not SFINAE-safe).
    //!
    //! \tparam UValue Must be convertible to \ref value_type.
    template <typename UValue>
    constexpr value_type value_or(UValue&& default_value) &&;

    //! If this instance \c !has_value(), the error is returned by `&`.
    //!
    //! \pre
    //! `!this->has_value()`: if this instance is not in the unexpected state, the program will terminate.
    //!
    //! \note
    //! If \ref error_type is \c void, the return type is exactly \c void instead of `void&` (which is illegal).
    constexpr error_type& error() & noexcept;

    //! If this instance \c !has_value(), the error is returned by `const&`.
    //!
    //! \pre
    //! `!this->has_value()`: if this instance is not in the unexpected state, the program will terminate.
    //!
    //! \note
    //! If \ref error_type is \c void, the return type is exactly \c void instead of `void const&` (which is illegal).
    constexpr error_type const& error() const& noexcept;

    //! If this instance \c !has_value(), the error is returned by `&&`.
    //!
    //! \pre
    //! `!this->has_value()`: if this instance is not in the unexpected state, the program will terminate.
    //!
    //! \note
    //! If \ref error_type is \c void, the return type is exactly \c void instead of `void&&` (which is illegal).
    constexpr error_type&& error() && noexcept;

    //! If this instance \c !has_value(), the error is returned by `const&&`.
    //!
    //! \pre
    //! `!this->has_value()`: if this instance is not in the unexpected state, the program will terminate.
    //!
    //! \note
    //! If \ref error_type is \c void, the return type is exactly \c void instead of `void const&&` (which is illegal).
    constexpr error_type const&& error() const&& noexcept;

    //! Access the underlying value instance. If \c has_value() is \c false, the program will terminate.
    //!
    //! This function is only available if \ref value_type is not \c void.
    constexpr value_type* operator->() noexcept;

    //! \copydoc expected::operator->()
    constexpr value_type const* operator->() const noexcept;

    //! If this instance \c has_value(), the value is returned by `&`.
    //!
    //! If this instance does not have a value, the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, this overload is not enabled (only the `const&` is accessible).
    constexpr value_type& operator*() & noexcept;

    //! If this instance \c has_value(), the value is returned by `const&`.
    //!
    //! If this instance does not have a value, the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, the return type is exactly \c void instead of `void const&` (which is illegal).
    constexpr value_type const& operator*() const& noexcept;

    //! If this instance \c has_value(), the value is returned by `&&`.
    //!
    //! If this instance does not have a value, the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, this overload is not enabled (only the `const&` is accessible).
    constexpr value_type&& operator*() && noexcept;

    //! If this instance \c has_value(), the value is returned by `const&&`.
    //!
    //! If this instance does not have a value, the program will terminate.
    //!
    //! \note
    //! If \ref value_type is \c void, this overload is not enabled (only the `const&` is accessible).
    constexpr value_type const&& operator*() const&& noexcept;

    //! Destroy the current contents of this instance and construct the \ref value_type of this instance through
    //! direct-initialization.
    //!
    //! If \ref value_type is not \c void, this function accepts two overloads:
    //!
    //! 1. `template <typename... TArgs> value_type& emplace(TArgs&&... args) noexcept` (only enabled if
    //!    `std::is_nothrow_constructible<value_type, TArgs...>::value` is \c true)
    //! 2. `template <typename U, typename... TArgs> value_type& emplace(std::initializer_list<U>& il, TArgs&&... args)
    //!    noexcept` (only enabled if `std::is_nothrow_constructible<value_type, std::initializer_list<U>&,
    //!    TArgs...>::value` is \c true)
    //!
    //! After calling this function, \c has_value() will return \c true.
    template <typename... TArgs>
    value_type& emplace(TArgs&&... args) noexcept;

    //! If \ref value_type is \c void, then \c emplace is a no argument function that returns \c void.
    //!
    //! After calling this function, \c has_value() will return \c true.
    void emplace() noexcept;
#endif

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature `UValue (value_type const&)`; if
    //!           \ref value_type is \c void, \c F has the signature `UValue ()`.
    //!
    //! \returns
    //! An `expected<UValue, error_type>`, where the returned value has been transformed by \a f. The \ref value_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform(F&& f) const&
    {
        return ::omni::detail::ExpectedOpTransform<F, expected, expected const&>::transform(std::forward<F>(f), *this);
    }

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature `UValue (value_type&)`; if \ref value_type
    //!           is \c void, \c F has the signature `UValue ()`.
    //!
    //! \returns
    //! An `expected<UValue, error_type>`, where the returned value has been transformed by \a f. The \ref value_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform(F&& f) &
    {
        return ::omni::detail::ExpectedOpTransform<F, expected, expected&>::transform(std::forward<F>(f), *this);
    }

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature `UValue (value_type&&)`; if \ref value_type
    //!           is \c void, \c F has the signature `UValue ()`.
    //!
    //! \returns
    //! An `expected<UValue, error_type>`, where the returned value has been transformed by \a f. The \ref value_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform(F&& f) &&
    {
        return ::omni::detail::ExpectedOpTransform<F, expected, expected&&>::transform(
            std::forward<F>(f), std::move(*this));
    }

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature `UValue (value_type const&&)`; if
    //!           \ref value_type is \c void, \c F has the signature `UValue ()`.
    //!
    //! \returns
    //! An `expected<UValue, error_type>`, where the returned value has been transformed by \a f. The \ref value_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform(F&& f) const&&
    {
        return ::omni::detail::ExpectedOpTransform<F, expected, expected const&&>::transform(
            std::forward<F>(f), std::move(*this));
    }

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature
    //!           `expected<UValue, UError> (value_type const&)`; if \ref value_type is \c void, \c F has the signature
    //!           `expected<UValue, UError> ()`. In both cases, \c UError must be constructible from \ref error_type or
    //!           \c void.
    template <typename F>
    constexpr auto and_then(F&& f) const&
    {
        return ::omni::detail::ExpectedOpAndThen<F, expected, expected const&>::and_then(std::forward<F>(f), *this);
    }

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature `expected<UValue, UError> (value_type&)`; if
    //!           \ref value_type is \c void, \c F has the signature `expected<UValue, UError> ()`. In both cases,
    //!           \c UError must be constructible from \ref error_type or \c void.
    template <typename F>
    constexpr auto and_then(F&& f) &
    {
        return ::omni::detail::ExpectedOpAndThen<F, expected, expected&>::and_then(std::forward<F>(f), *this);
    }

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature `expected<UValue, UError> (value_type&&)`;
    //!           if \ref value_type is \c void, \c F has the signature `expected<UValue, UError> ()`. In both cases,
    //!           \c UError must be constructible from \ref error_type or \c void.
    template <typename F>
    constexpr auto and_then(F&& f) &&
    {
        return ::omni::detail::ExpectedOpAndThen<F, expected, expected&&>::and_then(std::forward<F>(f), std::move(*this));
    }

    //! Transform the value by \a f if this \c has_value() or return the error if it does not.
    //!
    //! \tparam F If \ref value_type is not \c void, \c F has the signature
    //!           `expected<UValue, UError> (value_type const&&)`; if \ref value_type is \c void, \c F has the signature
    //!           `expected<UValue, UError> ()`. In both cases, \c UError must be constructible from \ref error_type or
    //!           \c void.
    template <typename F>
    constexpr auto and_then(F&& f) const&&
    {
        return ::omni::detail::ExpectedOpAndThen<F, expected, expected const&&>::and_then(
            std::forward<F>(f), std::move(*this));
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature `UError (error_type const&)`; if
    //!           \ref error_type is \c void, \c F has the signature `UError ()`.
    //!
    //! \returns
    //! An `expected<value_type, UError>`, where the returned error has been transformed by \a f. The \ref error_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform_error(F&& f) const&
    {
        return ::omni::detail::ExpectedOpTransformError<F, expected, expected const&>::transform_error(
            std::forward<F>(f), *this);
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature `UError (error_type&)`; if \ref error_type
    //!           is \c void, \c F has the signature `UError ()`.
    //!
    //! \returns
    //! An `expected<value_type, UError>`, where the returned error has been transformed by \a f. The \ref error_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform_error(F&& f) &
    {
        return ::omni::detail::ExpectedOpTransformError<F, expected, expected&>::transform_error(
            std::forward<F>(f), *this);
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature `UError (error_type&&)`; if \ref error_type
    //!           is \c void, \c F has the signature `UError ()`.
    //!
    //! \returns
    //! An `expected<value_type, UError>`, where the returned error has been transformed by \a f. The \ref error_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform_error(F&& f) &&
    {
        return ::omni::detail::ExpectedOpTransformError<F, expected, expected&&>::transform_error(
            std::forward<F>(f), std::move(*this));
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature `UError (error_type const&&)`; if
    //!           \ref error_type is \c void, \c F has the signature `UError ()`.
    //!
    //! \returns
    //! An `expected<value_type, UError>`, where the returned error has been transformed by \a f. The \ref error_type of
    //! the returned instance is the result type of \c F.
    template <typename F>
    constexpr auto transform_error(F&& f) const&&
    {
        return ::omni::detail::ExpectedOpTransformError<F, expected, expected const&&>::transform_error(
            std::forward<F>(f), std::move(*this));
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature
    //!           `expected<UValue, UError> (error_type const&)`; if \ref error_type is \c void, \c F has the signature
    //!           `expected<UValue, UError> ()`. In both cases, \c UValue must be constructible from \ref value_type or
    //!           \c void.
    template <typename F>
    constexpr auto or_else(F&& f) const&
    {
        return ::omni::detail::ExpectedOpOrElse<F, expected, expected const&>::or_else(std::forward<F>(f), *this);
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature `expected<UValue, UError> (error_type&)`; if
    //!           \ref error_type is \c void, \c F has the signature `expected<UValue, UError> ()`. In both cases,
    //!           \c UValue must be constructible from \ref value_type or \c void.
    template <typename F>
    constexpr auto or_else(F&& f) &
    {
        return ::omni::detail::ExpectedOpOrElse<F, expected, expected&>::or_else(std::forward<F>(f), *this);
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature `expected<UValue, UError> (error_type&&)`;
    //!           if \ref error_type is \c void, \c F has the signature `expected<UValue, UError> ()`. In both cases,
    //!           \c UValue must be constructible from \ref value_type or \c void.
    template <typename F>
    constexpr auto or_else(F&& f) &&
    {
        return ::omni::detail::ExpectedOpOrElse<F, expected, expected&&>::or_else(std::forward<F>(f), std::move(*this));
    }

    //! Transform the error by \a f if this \c has_value() is \c false or return the value if it does not.
    //!
    //! \tparam F If \ref error_type is not \c void, \c F has the signature
    //!           `expected<UValue, UError> (error_type const&&)`; if \ref error_type is \c void, \c F has the signature
    //!           `expected<UValue, UError> ()`. In both cases, \c UValue must be constructible from \ref value_type or
    //!           \c void.
    template <typename F>
    constexpr auto or_else(F&& f) const&&
    {
        return ::omni::detail::ExpectedOpOrElse<F, expected, expected const&&>::or_else(
            std::forward<F>(f), std::move(*this));
    }
};

//! Compare the contents of \a lhs and \a rhs for equality.
//!
//! 1. If `lhs.has_value() != rhs.has_value()`, then \c false is returned.
//! 2. If `lhs.has_value() && rhs.has_value()`, then their `.value()`s are compared; if both are \c void, the
//!    comparison is always equal.
//! 3. If `!lhs.has_value() && !rhs.has_value()`, then their `.error()`s are compared; if they are both \c void, the
//!    comparison is always equal.
//!
//! \par Comparability of Template Parameters
//! When provided with \p lhs and \p rhs, their \ref expected::value_type and \ref expected::error_type parameters must
//! either be equality comparable or \c void. If this is not the case, an error will occur in the immediate context
//! (testing for equality comparison of \c expected types is not SFINAE-safe). It is not legal to compare a non-`void`
//! type to a \c void type.
template <typename TValueLhs, typename TErrorLhs, typename TValueRhs, typename TErrorRhs>
constexpr bool operator==(expected<TValueLhs, TErrorLhs> const& lhs, expected<TValueRhs, TErrorRhs> const& rhs)
{
    static_assert(std::is_void<TValueLhs>::value == std::is_void<TValueRhs>::value,
                  "Can not compare expected of non-void `value_type` with one of void `value_type`");
    static_assert(std::is_void<TErrorLhs>::value == std::is_void<TErrorRhs>::value,
                  "Can not compare expected of non-void `error_type` with one of void `error_type`");
    return ::omni::detail::ExpectedComparer<expected<TValueLhs, TErrorLhs>, expected<TValueRhs, TErrorRhs>>::eq(lhs, rhs);
}

//! Compare the contents of \a lhs and \a rhs for inequality.
//! @param lhs An \ref omni::expected of one type.
//! @param rhs An \ref omni::expected of a potentially different type.
//! @returns \c true if the expected types are not equal, \c false if they are equal.
template <typename TValueLhs, typename TErrorLhs, typename TValueRhs, typename TErrorRhs>
constexpr bool operator!=(expected<TValueLhs, TErrorLhs> const& lhs, expected<TValueRhs, TErrorRhs> const& rhs)
{
    return !(lhs == rhs);
}

//! Compare the contents of \a lhs with the non \c expected type \a rhs.
//!
//! \tparam TValueLhs A value which is comparable to \c TValueRhs. If it is either \c void or a non-comparable type, it
//!         is an error in the immediate context (not SFINAE-safe).
template <typename TValueLhs, typename TErrorLhs, typename TValueRhs>
constexpr bool operator==(expected<TValueLhs, TErrorLhs> const& lhs, TValueRhs const& rhs)
{
    static_assert(!std::is_void<TValueLhs>::value, "Can not compare void-valued expected with value");
    return lhs.has_value() && static_cast<bool>(lhs.value() == rhs);
}

//! Compare the contents of \p lhs and \p rhs for inequality.
//! @param lhs An \ref omni::expected.
//! @param rhs A value that is comparable with the \c TValue type of \p lhs.
//! @returns \c true if the expected types are not equal, \c false if they are equal.
template <typename TValueLhs, typename TErrorLhs, typename TValueRhs>
constexpr bool operator!=(expected<TValueLhs, TErrorLhs> const& lhs, TValueRhs const& rhs)
{
    return !(lhs == rhs);
}

//! Compare the error contents of \a lhs with \a rhs.
//!
//! \returns \c true if `lhs.has_value() && (lhs.error() == rhs.error())`; the second clause is omitted if the error
//!          type is \c void.
template <typename TValueLhs, typename TErrorLhs, typename TErrorRhs>
constexpr bool operator==(expected<TValueLhs, TErrorLhs> const& lhs, unexpected<TErrorRhs> const& rhs)
{
    static_assert(std::is_void<TErrorLhs>::value == std::is_void<TErrorRhs>::value,
                  "Cannot compare expected and unexpected if the error types have mismatched `void`");
    return ::omni::detail::ExpectedUnexpectedComparer<TErrorLhs, TErrorRhs>::eq(lhs, rhs);
}

//! Compare the contents of \p lhs and \p rhs for inequality.
//! @param lhs An \ref omni::expected.
//! @param rhs An \ref omni::unexpected.
//! @returns \c true if the expected types are not equal, \c false if they are equal.
template <typename TValueLhs, typename TErrorLhs, typename TErrorRhs>
constexpr bool operator!=(expected<TValueLhs, TErrorLhs> const& lhs, unexpected<TErrorRhs> const& rhs)
{
    return !(lhs == rhs);
}

} // namespace omni
