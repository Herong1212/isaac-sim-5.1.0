// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include "../../carb/cpp/Functional.h"
#include "../../carb/cpp/Memory.h"
#include "../../carb/cpp/TypeTraits.h"
#include "../../carb/cpp/Memory.h"
#include "../../carb/cpp/TypeTraits.h"
#include "../core/IObject.h"
#include "ConvertsFromAnyCvRef.h"
#include "ParamPack.h"

#include <cstddef>
#include <initializer_list>
#include <type_traits>
#include <utility>

//! \cond DEV
//!
//! \file
//! Implementation details for \c omni::expected and related classes.
//!
//! \warning
//! Take \e extreme care when altering anything that can affect ABI. This is not just the obvious things like object
//! structure. ABI altering changes also include changing the trivial-ness of a destructor or copy operation based on a
//! member type.

namespace omni
{

template <typename TValue, typename TError>
class expected;

template <typename TError>
class unexpected;

struct unexpect_t
{
    explicit unexpect_t() = default;
};

constexpr unexpect_t unexpect{};

template <typename TError>
class bad_expected_access;

//! \warning
//! This is not ABI safe, since it derives from \c std::exception.
template <>
class bad_expected_access<void> : public std::exception
{
public:
    bad_expected_access() = default;

    char const* what() const noexcept override
    {
        return "Invalid access of `omni::expected`";
    }
};

//! \warning
//! This is not ABI safe, since it derives from \c std::exception through \c bad_expected_access<void>.
template <typename TError>
class bad_expected_access : public bad_expected_access<void>
{
public:
    explicit bad_expected_access(TError e) : m_error(std::move(e))
    {
    }

    TError const& error() const& noexcept
    {
        return m_error;
    }

    TError& error() & noexcept
    {
        return m_error;
    }

    TError const&& error() const&& noexcept
    {
        return std::move(m_error);
    }

    TError&& error() && noexcept
    {
        return std::move(m_error);
    }

private:
    TError m_error;
};

namespace detail
{

using carb::cpp::remove_cvref_t;
using carb::cpp::type_identity;
using omni::core::Result;
using std::bool_constant;
using std::conditional_t;
using std::conjunction;
using std::disjunction;
using std::enable_if_t;
using std::false_type;
using std::in_place;
using std::in_place_t;
using std::integral_constant;
using std::is_constructible;
using std::is_copy_constructible;
using std::is_move_constructible;
using std::is_nothrow_constructible;
using std::is_nothrow_copy_assignable;
using std::is_nothrow_copy_constructible;
using std::is_nothrow_destructible;
using std::is_nothrow_move_assignable;
using std::is_nothrow_move_constructible;
using std::is_trivially_copy_assignable;
using std::is_trivially_copy_constructible;
using std::is_trivially_destructible;
using std::is_trivially_move_assignable;
using std::is_trivially_move_constructible;
using std::is_void;
using std::negation;
using std::true_type;
using std::void_t;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Helpers                                                                                                            //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

template <typename T>
struct IsExpected : false_type
{
};

template <typename TValue, typename TError>
struct IsExpected<omni::expected<TValue, TError>> : true_type
{
};

template <typename T>
struct IsUnexpected : false_type
{
};

template <typename TError>
struct IsUnexpected<omni::unexpected<TError>> : true_type
{
};

//! This empty structure is used when an \c expected is going to store a \c void element. This is needed because \c void
//! is not a valid \c union member.
struct ExpectedStorageVoid
{
};

//! Test if \c T is a valid \c value_type for \c omni::expected or \c omni::unexpected.
template <typename T>
struct IsValidExpectedValue : conjunction<disjunction<std::is_object<T>, is_void<T>>, negation<std::is_array<T>>>
{
};

//! Test if \c T is a valid \c error_type for \c omni::expected. This is similar to \c IsValidExpectedValue with the
//! additional restrictions that it can not be CV qualified.
template <typename T>
struct IsValidExpectedError : conjunction<disjunction<std::is_object<T>, is_void<T>>,
                                          negation<std::is_array<T>>,
                                          negation<IsUnexpected<T>>,
                                          negation<std::is_const<T>>,
                                          negation<std::is_volatile<T>>>
{
};

//! Apply \c TTTransform to \c T if it is possibly cv \c void or be \c TFallback if it is \c void.
template <template <typename...> class TTTransform, typename T, typename TFallback = void, typename = void_t<>>
struct ExpectedTransformIfNonVoid
{
    using type = TFallback;
};

template <template <typename...> class TTTransform, typename T, typename TFallback>
struct ExpectedTransformIfNonVoid<TTTransform, T, TFallback, std::enable_if_t<!std::is_void<T>::value>>
{
    using type = typename TTTransform<T>::type;
};

template <typename TFromValue,
          typename TFromError,
          typename TFromValueExpr,
          typename TFromErrorExpr,
          typename TToValue,
          typename TToError,
          typename = void_t<>>
struct IsExpectedConvertibleImpl : std::false_type
{
};

template <typename TFromValue, typename TFromError, typename TFromValueExpr, typename TFromErrorExpr, typename TToValue, typename TToError>
struct IsExpectedConvertibleImpl<
    TFromValue,
    TFromError,
    TFromValueExpr,
    TFromErrorExpr,
    TToValue,
    TToError,
    std::enable_if_t<conjunction<
        // (18.1): is_constructible_v<T, UF> is true; and
        disjunction<conjunction<std::is_void<TToValue>, std::is_void<TFromValue>>, std::is_constructible<TToValue, TFromValue>>,
        // (18.2): is_constructible_v<E, GF> is true; and
        disjunction<conjunction<std::is_void<TToError>, std::is_void<TFromError>>, std::is_constructible<TToError, TFromError>>,
        // (18.3): if T is not cv bool, converts-from-any-cvref<T, expected<U, G>> is false; and
        disjunction<std::is_same<bool, std::remove_cv_t<TToValue>>,
                    negation<ConvertsFromAnyCvRef<TToValue, omni::expected<TFromValue, TFromError>>>>,
        // (18.4): is_constructible_v<unexpected<E>, expected<U, G>&> is false; and
        negation<std::is_constructible<omni::unexpected<TToError>, omni::expected<TFromValue, TFromError>&>>,
        // (18.5): is_constructible_v<unexpected<E>, expected<U, G>> is false; and
        negation<std::is_constructible<omni::unexpected<TToError>, omni::expected<TFromValue, TFromError>>>,
        // (18.6): is_constructible_v<unexpected<E>, const expected<U, G>&> is false; and
        negation<std::is_constructible<omni::unexpected<TToError>, omni::expected<TFromValue, TFromError> const&>>,
        // (18.7): is_constructible_v<unexpected<E>, const expected<U, G>> is false.
        negation<std::is_constructible<omni::unexpected<TToError>, omni::expected<TFromValue, TFromError> const>>>::value>>
    : std::true_type
{
    static constexpr bool is_explicit = disjunction<negation<std::is_convertible<TFromValueExpr, TToValue>>,
                                                    negation<std::is_convertible<TFromErrorExpr, TToError>>>::value;
};

//! Type test to determine if \c omni::expected \c TFrom is convertible to \c TTo by a converting constructor. The
//! elements are transformed by \c TTTypeTransformer for expressiion value category changes (copy vs move).
//!
//! The final structure will have either 1 or 2 member values:
//!
//! * `static constexpr bool value`: This is \c true if \c TFrom is convertible to \c TTo or \c false if it is not.
//! * `static constexpr bool is_explicit`: This is \c true if the conversion between types should be \c explicit or
//!   \c false if it is an implicit conversion. This member is only present if \c value is \c true and is safe for use
//!   in SFINAE contexts.
//!
//! This type is responsible for filtering out cases where \c TFrom is exactly equal to \c TTo. If this is the case, it
//! is not convertable, but either copyable or moveable (depending on the member types).
//!
//! \see IsExpectedCopyConstructibleFrom
//! \see IsExpectedMoveConstructibleFrom
template <typename TFrom, typename TTo, template <typename...> class TTTypeTransformer, typename = void_t<>>
struct IsExpectedConvertible : std::false_type
{
};

template <typename TFromValue, typename TFromError, typename TToValue, typename TToError, template <typename...> class TTTypeTransformer>
struct IsExpectedConvertible<
    omni::expected<TFromValue, TFromError>,
    omni::expected<TToValue, TToError>,
    TTTypeTransformer,
    std::enable_if_t<!conjunction<std::is_same<TFromValue, TToValue>, std::is_same<TFromError, TToError>>::value>>
    : IsExpectedConvertibleImpl<TFromValue,
                                TFromError,
                                typename ExpectedTransformIfNonVoid<TTTypeTransformer, TFromValue>::type,
                                typename ExpectedTransformIfNonVoid<TTTypeTransformer, TFromError>::type,
                                TToValue,
                                TToError>
{
};

template <typename T>
struct AddConstLvalueRef
{
    using type = std::add_lvalue_reference_t<std::add_const_t<T>>;
};

template <typename TFrom, typename TTo>
using IsExpectedCopyConstructibleFrom = IsExpectedConvertible<TFrom, TTo, AddConstLvalueRef>;

template <typename TFrom, typename TTo>
using IsExpectedMoveConstructibleFrom = IsExpectedConvertible<TFrom, TTo, type_identity>;

template <typename TFrom, typename TTo, typename = void_t<>>
struct IsExpectedDirectConstructibleFromImpl : std::false_type
{
};

template <typename UValue, typename TValue, typename TError>
struct IsExpectedDirectConstructibleFromImpl<
    UValue,
    omni::expected<TValue, TError>,
    std::enable_if_t<
        conjunction<negation<is_void<TValue>>,
                    negation<std::is_same<in_place_t, remove_cvref_t<UValue>>>,
                    negation<std::is_same<omni::expected<TValue, TError>, remove_cvref_t<UValue>>>,
                    is_constructible<TValue, UValue>,
                    negation<IsUnexpected<remove_cvref_t<UValue>>>,
                    disjunction<negation<std::is_same<bool, remove_cvref_t<TValue>>>, negation<IsExpected<UValue>>>>::value>>
    : std::false_type
{
    static constexpr bool is_explicit = !std::is_convertible<UValue, TValue>::value;
};

template <typename TFrom, typename TTo>
struct IsExpectedDirectConstructibleFrom : IsExpectedDirectConstructibleFromImpl<TFrom, TTo>
{
};

//! This is used by expected base classes in order to create versions of special constructors (copy and move) without
//! defining them in a way that would interfere with their trivial definition from `= default`.
struct ExpectedCtorBypass
{
};

#if CARB_EXCEPTIONS_ENABLED

//! Implementation of \c expected_reinit which optimizes the algorithm based on if the operations are potentially
//! throwing. The generic case assumes that all operations can throw.
template <typename TOld, typename TNew, typename TParamPack, typename = void_t<>>
struct ExpectedReinitImpl
{
    template <typename... TArgs>
    static void reinit(TOld* pold, TNew* pnew, TArgs&&... args)
    {
        TOld temp{ std::move(*pold) };
        carb::cpp::destroy_at(pold);
        try
        {
            carb::cpp::construct_at(pnew, std::forward<TArgs>(args)...);
        }
        catch (...)
        {
            carb::cpp::construct_at(pold, std::move(temp));
            throw;
        }
    }
};

//! If `TNew(TArgs...)` construction is non-throwing, then we don't need to back up anything.
template <typename TOld, typename TNew, typename... TArgs>
struct ExpectedReinitImpl<TOld, TNew, ParamPack<TArgs...>, std::enable_if_t<std::is_nothrow_constructible<TNew, TArgs...>::value>>
{
    static void reinit(TOld* pold, TNew* pnew, TArgs&&... args)
    {
        carb::cpp::destroy_at(pold);
        carb::cpp::construct_at(pnew, std::forward<TArgs>(args)...);
    }
};

//! If \c TNew is non-throwing move, but `TNew(TArgs...)` could throw, then create it on the stack first, then move it.
template <typename TOld, typename TNew, typename... TArgs>
struct ExpectedReinitImpl<TOld,
                          TNew,
                          ParamPack<TArgs...>,
                          std::enable_if_t<conjunction<std::is_nothrow_move_constructible<TNew>,
                                                       negation<std::is_nothrow_constructible<TNew, TArgs...>>>::value>>
{
    static void reinit(TOld* pold, TNew* pnew, TArgs&&... args)
    {
        TNew temp{ std::forward<TArgs>(args)... };
        carb::cpp::destroy_at(pold);
        carb::cpp::construct_at(pnew, std::move(temp));
    }
};

#else // !CARB_EXCEPTIONS_ENABLED

//! Without exceptions enabled, there is no mechanism for failure, so the algorithm is simple.
template <typename TOld, typename TNew, typename TParamPack>
struct ExpectedReinitImpl
{
    template <typename... TArgs>
    static void reinit(TOld* pold, TNew* pnew, TArgs&&... args) noexcept
    {
        carb::cpp::destroy_at(pold);
        carb::cpp::construct_at(pnew, std::forward<TArgs>(args)...);
    }
};

#endif // CARB_EXCEPTIONS_ENABLED

//! Used in type-changing assignment -- reinitializes the contents of an \c ExpectedStorage union from \c TOld to
//! \c TNew without allowing an uninitialized state to leak (a \c std::bad_variant_access equivalent is not allowed for
//! \c std::expected implementations).
//!
//! \exception
//! An exception raised will leave the \a pold in a non-destructed, but possibly moved-from state.
template <typename TOld, typename TNew, typename... TArgs>
constexpr void expected_reinit(TOld* pold, TNew* pnew, TArgs&&... args)
{
    ExpectedReinitImpl<TOld, TNew, ParamPack<TArgs...>>::reinit(pold, pnew, std::forward<TArgs>(args)...);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Unexpected                                                                                                         //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

template <typename TError>
class UnexpectedImpl
{
    static_assert(IsValidExpectedError<TError>::value, "Type is not valid for an expected error type");

    template <typename UError>
    friend class UnexpectedImpl;

public:
    constexpr UnexpectedImpl(UnexpectedImpl const&) = default;
    constexpr UnexpectedImpl(UnexpectedImpl&&) = default;

    template <typename UError = TError,
              typename = std::enable_if_t<conjunction<negation<IsUnexpected<remove_cvref_t<UError>>>,
                                                      negation<std::is_same<remove_cvref_t<UError>, in_place_t>>,
                                                      is_constructible<TError, UError>>::value>>
    constexpr explicit UnexpectedImpl(UError&& src) : m_error{ std::forward<UError>(src) }
    {
    }

    template <typename... TArgs, typename = std::enable_if_t<is_constructible<TError, TArgs...>::value>>
    constexpr explicit UnexpectedImpl(in_place_t, TArgs&&... args) : m_error{ std::forward<TArgs>(args)... }
    {
    }

    template <typename U,
              typename... TArgs,
              typename = std::enable_if_t<is_constructible<TError, std::initializer_list<U>&, TArgs...>::value>>
    constexpr explicit UnexpectedImpl(in_place_t, std::initializer_list<U> init_list, TArgs&&... args)
        : m_error{ init_list, std::forward<TArgs>(args)... }
    {
    }

    constexpr TError& error() & noexcept
    {
        return m_error;
    }

    constexpr TError const& error() const& noexcept
    {
        return m_error;
    }

    constexpr TError&& error() && noexcept
    {
        return std::move(m_error);
    }

    constexpr TError const&& error() const&& noexcept
    {
        return std::move(m_error);
    }

    constexpr void swap(UnexpectedImpl<TError>& other)
    {
        using std::swap;

        swap(m_error, other.m_error);
    }

    template <typename UError>
    constexpr bool operator==(UnexpectedImpl<UError> const& other) const
    {
        return m_error == other.m_error;
    }

protected:
    TError m_error;
};

template <>
class UnexpectedImpl<void>
{
public:
    constexpr UnexpectedImpl() noexcept
    {
    }

    constexpr explicit UnexpectedImpl(in_place_t) noexcept
    {
    }

    constexpr void error() const noexcept
    {
    }

    constexpr void swap(UnexpectedImpl<void>) noexcept
    {
    }

    constexpr bool operator==(UnexpectedImpl<void>) const noexcept
    {
        return true;
    }
};

//! Called from `expected::error()` overloads when the instance `has_value()`.
[[noreturn]] inline void invalid_expected_access_error() noexcept
{
    CARB_FATAL_UNLESS(false, "Call to `omni::expected::error()` on successful instance");
}

#if CARB_EXCEPTIONS_ENABLED

CARB_IGNOREWARNING_MSC_WITH_PUSH(5272) // Throwing an object of non-copyable type 'XXX' is non-standard

template <typename T>
[[noreturn]] inline enable_if_t<conjunction<negation<std::is_same<std::decay_t<T>, ExpectedStorageVoid>>,
                                            std::is_constructible<std::decay_t<T>, T>>::value>
invalid_expected_access(T&& x)
{
    throw ::omni::bad_expected_access<std::decay_t<T>>(std::forward<T>(x));
}

template <typename T>
[[noreturn]] inline enable_if_t<conjunction<negation<std::is_same<std::decay_t<T>, ExpectedStorageVoid>>,
                                            negation<std::is_constructible<std::decay_t<T>, T>>>::value>
invalid_expected_access(T&&)
{
    throw ::omni::bad_expected_access<void>();
}

[[noreturn]] inline void invalid_expected_access(ExpectedStorageVoid)
{
    throw ::omni::bad_expected_access<void>();
}

CARB_IGNOREWARNING_MSC_POP

#else // !CARB_EXCEPTIONS_ENABLED

template <typename T>
[[noreturn]] inline void invalid_expected_access(T&&)
{
    CARB_FATAL_UNLESS(false, "Invalid access of `omni::expected::value()`");
}

#endif

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Storage                                                                                                            //
// This section governs the byte layout of an `omni::excepted` and the trivialness of its special member functions    //
// (namely: copy, move, and destructor -- initialization is never trivial). All information relevant to the ABI of    //
// `expected` should be defined in this section.                                                                      //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

enum class ExpectedState : std::uint8_t
{
    //! The instance holds the success value.
    eSUCCESS = 0,
    //! The instance holds an error.
    eUNEXPECTED = 1,
};

//! The \c ExpectedStorage type stores the value or error contents of an \c expected instance.
//!
//! This is stored as a union to make \c e.value and \c e.error show up properly in debugging.
//!
//! The member \c uninit is used for the copy and move constructors, but only exists in this state inside of an
//! \c ExpectedImplBase constructor for types with non-trivial versions of these operations. While the copy or move
//! constructor needs to initialize either \c value or \c error, there is no syntax in C++ to conditionally do this
//! based on a value.
//!
//! \tparam TrivialDtor If both the \c TValue and \c TError types are either \c void or have trivial destructors, then
//!         the union itself does not need a destructor.
// clang-format off
template <typename TValue,
          typename TError,
          bool TrivialDtor = conjunction<disjunction<is_void<TValue>, is_trivially_destructible<TValue>>,
                                         disjunction<is_void<TError>, is_trivially_destructible<TError>>
                                        >::value
         >
union ExpectedStorage;
// clang-format on

template <typename TValue, typename TError>
union ExpectedStorage<TValue, TError, /*TrivialDtor=*/true>
{
    conditional_t<is_void<TValue>::value, ExpectedStorageVoid, TValue> value;
    conditional_t<is_void<TError>::value, ExpectedStorageVoid, TError> error;
    ExpectedStorageVoid uninit;

    template <typename... TArgs>
    constexpr explicit ExpectedStorage(in_place_t, TArgs&&... args) : value{ std::forward<TArgs>(args)... }
    {
    }

    template <typename... TArgs>
    constexpr explicit ExpectedStorage(unexpect_t, TArgs&&... args) : error{ std::forward<TArgs>(args)... }
    {
    }

    constexpr explicit ExpectedStorage(ExpectedCtorBypass) : uninit{}
    {
    }
};

template <typename TValue, typename TError>
union ExpectedStorage<TValue, TError, /*TrivialDtor=*/false>
{
    conditional_t<is_void<TValue>::value, ExpectedStorageVoid, TValue> value;
    conditional_t<is_void<TError>::value, ExpectedStorageVoid, TError> error;
    ExpectedStorageVoid uninit;

    template <typename... TArgs>
    constexpr explicit ExpectedStorage(in_place_t, TArgs&&... args) : value{ std::forward<TArgs>(args)... }
    {
    }

    template <typename... TArgs>
    constexpr explicit ExpectedStorage(unexpect_t, TArgs&&... args) : error{ std::forward<TArgs>(args)... }
    {
    }

    constexpr explicit ExpectedStorage(ExpectedCtorBypass) : uninit{}
    {
    }

    ~ExpectedStorage() noexcept
    {
        // Intentionally empty -- it is the responsibility of the owner to call value or error destructor, since only it
        // knows which alternative is active.
    }
};

template <typename TValue, typename TError>
class ExpectedImplBase
{
    using StoredValueType = conditional_t<is_void<TValue>::value, ExpectedStorageVoid, TValue>;
    using StoredErrorType = conditional_t<is_void<TError>::value, ExpectedStorageVoid, TError>;

    template <typename UValue, typename UError>
    friend class ExpectedImplBase;

protected:
    template <typename... TArgs, typename = enable_if_t<is_constructible<StoredValueType, TArgs...>::value>>
    explicit ExpectedImplBase(in_place_t,
                              TArgs&&... args) noexcept(is_nothrow_constructible<StoredValueType, TArgs...>::value)
        : m_state{ ExpectedState::eSUCCESS }, m_storage{ in_place, std::forward<TArgs>(args)... }
    {
    }

    template <typename... TArgs, typename = enable_if_t<is_constructible<StoredErrorType, TArgs...>::value>>
    explicit ExpectedImplBase(unexpect_t,
                              TArgs&&... args) noexcept(is_nothrow_constructible<StoredErrorType, TArgs...>::value)
        : m_state{ ExpectedState::eUNEXPECTED }, m_storage{ unexpect, std::forward<TArgs>(args)... }
    {
    }

    template <typename UValue, typename UError>
    constexpr explicit ExpectedImplBase(ExpectedCtorBypass bypass, ExpectedImplBase<UValue, UError> const& src)
        : m_state{ src.m_state }, m_storage{ bypass }
    {
        if (src.m_state == ExpectedState::eSUCCESS)
            carb::cpp::construct_at(std::addressof(m_storage.value), src.m_storage.value);
        else
            carb::cpp::construct_at(std::addressof(m_storage.error), src.m_storage.error);

        m_state = src.m_state;
    }

    template <typename UValue, typename UError>
    constexpr explicit ExpectedImplBase(ExpectedCtorBypass bypass, ExpectedImplBase<UValue, UError>&& src)
        : m_state{ src.m_state }, m_storage{ bypass }
    {
        if (src.m_state == ExpectedState::eSUCCESS)
            carb::cpp::construct_at(std::addressof(m_storage.value), std::move(src.m_storage.value));
        else
            carb::cpp::construct_at(std::addressof(m_storage.error), std::move(src.m_storage.error));

        m_state = src.m_state;
    }

    //! Destroy the contents of this instance. This is called from the destructor of types with non-trivial destructors.
    //! It \e must only be called once. See \c ExpectedPayload with \c ExpectedPayloadTag::eCALL_DTOR for usage.
    //!
    //! \pre This is either a success or unexpected
    //! \post The active alternative has been destroyed -- this implementation is in an uninitialized state
    void unsafe_destroy()
    {
        if (m_state == ExpectedState::eSUCCESS)
            carb::cpp::destroy_at(std::addressof(m_storage.value));
        else
            carb::cpp::destroy_at(std::addressof(m_storage.error));
    }

    void copy_from(ExpectedImplBase const& src)
    {
        if (m_state == src.m_state)
        {
            if (m_state == ExpectedState::eSUCCESS)
                m_storage.value = src.m_storage.value;
            else
                m_storage.error = src.m_storage.error;
        }
        else if (m_state == ExpectedState::eSUCCESS) // && src.m_state == ExpectedState::eUNEXPECTED
        {
            expected_reinit(std::addressof(m_storage.value), std::addressof(m_storage.error), src.m_storage.error);
        }
        else // m_state == ExpectedState::eUNEXPECTED && src.m_state == ExpectedState::eSUCCESS
        {
            expected_reinit(std::addressof(m_storage.error), std::addressof(m_storage.value), src.m_storage.value);
        }
        m_state = src.m_state;
    }

    void move_from(ExpectedImplBase&& src)
    {
        if (m_state == src.m_state)
        {
            if (m_state == ExpectedState::eSUCCESS)
                m_storage.value = std::move(src.m_storage.value);
            else
                m_storage.error = std::move(src.m_storage.error);
        }
        else if (m_state == ExpectedState::eSUCCESS) // && src.m_state == ExpectedState::eUNEXPECTED
        {
            expected_reinit(
                std::addressof(m_storage.value), std::addressof(m_storage.error), std::move(src.m_storage.error));
        }
        else // m_state == ExpectedState::eUNEXPECTED && src.m_state == ExpectedState::eSUCCESS
        {
            expected_reinit(
                std::addressof(m_storage.error), std::addressof(m_storage.value), std::move(src.m_storage.value));
        }
        m_state = src.m_state;
    }

protected:
    ExpectedState m_state;
    ExpectedStorage<TValue, TError> m_storage;
};

//! Special case of base class where both alternatives are \c void and we only want to store a byte.
template <>
class ExpectedImplBase<void, void>
{
protected:
    explicit ExpectedImplBase(in_place_t) noexcept : m_state{ ExpectedState::eSUCCESS }
    {
    }

    explicit ExpectedImplBase(unexpect_t) noexcept : m_state{ ExpectedState::eUNEXPECTED }
    {
    }

    //! This covers both copy and move constructor use cases, since there isn't data to move anyway.
    explicit ExpectedImplBase(ExpectedCtorBypass, ExpectedImplBase const& src) noexcept : m_state{ src.m_state }
    {
    }

    //! Fills the same role as the non-specialized version, but does nothing.
    constexpr void unsafe_destroy()
    {
    }

protected:
    ExpectedState m_state;
};

//! Used by \c ExpectedPayload in order to determine which special member functions need definitions vs which of them
//! can be defaulted.
//!
//! - \c eTRIVIAL -- copy, move, and destructor are all trivial, so nothing must be done for any operation
//! - \c eCALL_COPY -- copy is non-trivial, but move and destructor are trivial
//! - \c eCALL_MOVE -- move is non-trivial, but copy and destructor are trivial
//! - \c eCALL_BOTH -- both copy and move are non-trivial, but the destructor is
//! - \c eCALL_DTOR -- the destructor must be called, which makes both copy- and move-assignment non-trivial, as
//!   assignment from the opposite alternative can cause the destructor to be called.
//!
//! \see ExpectedPayloadTagFor
enum class ExpectedPayloadTag : std::uint8_t
{
    eTRIVIAL,
    eCALL_COPY,
    eCALL_MOVE,
    eCALL_BOTH,
    eCALL_DTOR,
};

// clang-format off

template <typename TValue,
          typename TError,
          bool TrivialCopy = conjunction<disjunction<is_void<TValue>, conjunction<is_trivially_copy_assignable<TValue>, is_trivially_copy_constructible<TValue>>>,
                                         disjunction<is_void<TError>, conjunction<is_trivially_copy_assignable<TError>, is_trivially_copy_constructible<TError>>>
                                        >::value,
          bool TrivialMove = conjunction<disjunction<is_void<TValue>, conjunction<is_trivially_move_assignable<TValue>, is_trivially_move_constructible<TValue>>>,
                                         disjunction<is_void<TError>, conjunction<is_trivially_move_assignable<TError>, is_trivially_move_constructible<TError>>>
                                        >::value,
          bool TrivialDtor = conjunction<disjunction<is_void<TValue>, is_trivially_destructible<TValue>>,
                                         disjunction<is_void<TError>, is_trivially_destructible<TError>>
                                        >::value
         >
struct ExpectedPayloadTagFor;

// clang-format on

template <typename TValue, typename TError>
struct ExpectedPayloadTagFor<TValue, TError, /*TrivialCopy=*/true, /*TrivialMove=*/true, /*TrivialDtor=*/true>
    : integral_constant<ExpectedPayloadTag, ExpectedPayloadTag::eTRIVIAL>
{
};

template <typename TValue, typename TError>
struct ExpectedPayloadTagFor<TValue, TError, /*TrivialCopy=*/false, /*TrivialMove=*/true, /*TrivialDtor=*/true>
    : integral_constant<ExpectedPayloadTag, ExpectedPayloadTag::eCALL_COPY>
{
};

template <typename TValue, typename TError>
struct ExpectedPayloadTagFor<TValue, TError, /*TrivialCopy=*/true, /*TrivialMove=*/false, /*TrivialDtor=*/true>
    : integral_constant<ExpectedPayloadTag, ExpectedPayloadTag::eCALL_MOVE>
{
};

template <typename TValue, typename TError>
struct ExpectedPayloadTagFor<TValue, TError, /*TrivialCopy=*/false, /*TrivialMove=*/false, /*TrivialDtor=*/true>
    : integral_constant<ExpectedPayloadTag, ExpectedPayloadTag::eCALL_BOTH>
{
};

template <typename TValue, typename TError, bool TrivialCopy, bool TrivialMove>
struct ExpectedPayloadTagFor<TValue, TError, TrivialCopy, TrivialMove, /*TrivialDtor=*/false>
    : integral_constant<ExpectedPayloadTag, ExpectedPayloadTag::eCALL_DTOR>
{
};

//! The payload is responsible for managing the special member functions of copy and move construction and assignment,
//! as well as the destructor.
template <typename TValue, typename TError, ExpectedPayloadTag Optimization = ExpectedPayloadTagFor<TValue, TError>::value>
class ExpectedPayload;

template <typename TValue, typename TError>
class ExpectedPayload<TValue, TError, ExpectedPayloadTag::eTRIVIAL> : public ExpectedImplBase<TValue, TError>
{
public:
    using ExpectedImplBase<TValue, TError>::ExpectedImplBase;

    ExpectedPayload(ExpectedPayload const&) = default;
    ExpectedPayload(ExpectedPayload&&) = default;

    ExpectedPayload& operator=(ExpectedPayload const&) = default;
    ExpectedPayload& operator=(ExpectedPayload&&) = default;

    ~ExpectedPayload() = default;
};

template <typename TValue, typename TError>
class ExpectedPayload<TValue, TError, ExpectedPayloadTag::eCALL_COPY> : public ExpectedImplBase<TValue, TError>
{
public:
    using ExpectedImplBase<TValue, TError>::ExpectedImplBase;

    ExpectedPayload(ExpectedPayload const&) = default;
    ExpectedPayload(ExpectedPayload&&) = default;

    // clang-format off

    ExpectedPayload& operator=(ExpectedPayload const& src)
        noexcept(conjunction<disjunction<is_void<TValue>, conjunction<is_nothrow_copy_constructible<TValue>, is_nothrow_copy_assignable<TValue>>>,
                             disjunction<is_void<TError>, conjunction<is_nothrow_copy_constructible<TError>, is_nothrow_copy_assignable<TError>>>
                            >::value
                )
    {
        this->copy_from(src);
        return *this;
    }

    // clang-format on

    ExpectedPayload& operator=(ExpectedPayload&&) = default;

    ~ExpectedPayload() = default;
};

template <typename TValue, typename TError>
class ExpectedPayload<TValue, TError, ExpectedPayloadTag::eCALL_MOVE> : public ExpectedImplBase<TValue, TError>
{
public:
    using ExpectedImplBase<TValue, TError>::ExpectedImplBase;

    ExpectedPayload(ExpectedPayload const&) = default;
    ExpectedPayload(ExpectedPayload&&) = default;
    ExpectedPayload& operator=(ExpectedPayload const&) = default;

    // clang-format off

    ExpectedPayload& operator=(ExpectedPayload&& src)
        noexcept(conjunction<disjunction<is_void<TValue>, conjunction<is_nothrow_move_constructible<TValue>, is_nothrow_move_assignable<TValue>>>,
                             disjunction<is_void<TError>, conjunction<is_nothrow_move_constructible<TError>, is_nothrow_move_assignable<TError>>>
                            >::value
                )
    {
        this->move_from(std::move(src));
        return *this;
    }

    // clang-format on

    ~ExpectedPayload() = default;
};

template <typename TValue, typename TError>
class ExpectedPayload<TValue, TError, ExpectedPayloadTag::eCALL_BOTH> : public ExpectedImplBase<TValue, TError>
{
public:
    using ExpectedImplBase<TValue, TError>::ExpectedImplBase;

    ExpectedPayload(ExpectedPayload const&) = default;
    ExpectedPayload(ExpectedPayload&&) = default;

    // clang-format off

    ExpectedPayload& operator=(ExpectedPayload const& src)
        noexcept(conjunction<disjunction<is_void<TValue>, conjunction<is_nothrow_copy_constructible<TValue>, is_nothrow_copy_assignable<TValue>>>,
                             disjunction<is_void<TError>, conjunction<is_nothrow_copy_constructible<TError>, is_nothrow_copy_assignable<TError>>>
                            >::value
                )
    {
        this->copy_from(src);
        return *this;
    }

    ExpectedPayload& operator=(ExpectedPayload&& src)
        noexcept(conjunction<disjunction<is_void<TValue>, conjunction<is_nothrow_move_constructible<TValue>, is_nothrow_move_assignable<TValue>>>,
                             disjunction<is_void<TError>, conjunction<is_nothrow_move_constructible<TError>, is_nothrow_move_assignable<TError>>>
                            >::value
                )
    {
        this->move_from(std::move(src));
        return *this;
    }

    // clang-format on

    ~ExpectedPayload() = default;
};

template <typename TValue, typename TError>
class ExpectedPayload<TValue, TError, ExpectedPayloadTag::eCALL_DTOR> : public ExpectedImplBase<TValue, TError>
{
public:
    using ExpectedImplBase<TValue, TError>::ExpectedImplBase;

    ExpectedPayload(ExpectedPayload const&) = default;
    ExpectedPayload(ExpectedPayload&&) = default;

    // clang-format off

    ExpectedPayload& operator=(ExpectedPayload const& src)
        noexcept(conjunction<disjunction<is_void<TValue>, conjunction<is_nothrow_copy_constructible<TValue>, is_nothrow_copy_assignable<TValue>>>,
                             disjunction<is_void<TError>, conjunction<is_nothrow_copy_constructible<TError>, is_nothrow_copy_assignable<TError>>>
                            >::value
                )
    {
        this->copy_from(src);
        return *this;
    }

    ExpectedPayload& operator=(ExpectedPayload&& src)
        noexcept(conjunction<disjunction<is_void<TValue>, conjunction<is_nothrow_move_constructible<TValue>, is_nothrow_move_assignable<TValue>>>,
                             disjunction<is_void<TError>, conjunction<is_nothrow_move_constructible<TError>, is_nothrow_move_assignable<TError>>>
                            >::value
                )
    {
        this->move_from(std::move(src));
        return *this;
    }

    ~ExpectedPayload()
        noexcept(conjunction<disjunction<is_void<TValue>, is_nothrow_destructible<TValue>>,
                             disjunction<is_void<TError>, is_nothrow_destructible<TError>>
                            >::value
                )
    {
        this->unsafe_destroy();
    }

    // clang-format on
};

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// API                                                                                                                //
// These classes layer the API based on the type of TValue and TError (specifically: Are they void or an object?).    //
// Definitions in this section shall not affect the ABI of an `omni::expected` type; special members are all defined  //
// by `= default` or by `using BaseType::BaseType`.                                                                   //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// clang-format off
//! This class controls the presence and trivialness of copy and move constructors.
//!
//! A copy or move constructor can be defaulted, defined, or deleted. The operation is defaulted when both \c TValue and
//! \c TError are either \c void or have that operation as trivial as well (this comes from the definition of when this
//! is allowed on \c union types). If either \c TValue or \c TError has the operation deleted, it is deleted on the
//! \c expected type as well. For the cases where the operation is non-trivial, it is defined explicitly using the
//! \c ExpectedCtorBypass trick. Since these 3 options can happen for both copy and move operations, this results in 9
//! partial specializations.
//!
//! The `= delete` overloads are not needed, as `= default`ing these will still end up with a deleted definition since
//! the \c ExpectedStorage union is deleted by default. However, this leads to awful error messages that lead people to
//! think the implementation is broken. By spelling them out, the `= delete` looks more intentional.
template <typename TValue,
          typename TError,
          bool CopyCtor = conjunction<disjunction<is_void<TValue>, is_copy_constructible<TValue>>,
                                      disjunction<is_void<TError>, is_copy_constructible<TError>>
                                     >::value,
          bool DefaultCopyCtor = conjunction<bool_constant<CopyCtor>,
                                             disjunction<is_void<TValue>, is_trivially_copy_constructible<TValue>>,
                                             disjunction<is_void<TError>, is_trivially_copy_constructible<TError>>
                                            >::value,
          bool MoveCtor = conjunction<disjunction<is_void<TValue>, is_move_constructible<TValue>>,
                                      disjunction<is_void<TError>, is_move_constructible<TError>>
                                     >::value,
          bool DefaultMoveCtor = conjunction<bool_constant<MoveCtor>,
                                             disjunction<is_void<TValue>, is_trivially_move_constructible<TValue>>,
                                             disjunction<is_void<TError>, is_trivially_move_constructible<TError>>
                                            >::value
         >
class ExpectedApiCtors;
// clang-format on

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/true, /*DefaultCopyCtor=*/true, /*MoveCtor=*/true, /*DefaultMoveCtor=*/true>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    ExpectedApiCtors(ExpectedApiCtors const&) = default;
    ExpectedApiCtors(ExpectedApiCtors&&) = default;

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/true, /*DefaultCopyCtor=*/true, /*MoveCtor=*/false, /*DefaultMoveCtor=*/false>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    ExpectedApiCtors(ExpectedApiCtors const&) = default;
    ExpectedApiCtors(ExpectedApiCtors&&) = delete;

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/true, /*DefaultCopyCtor=*/true, /*MoveCtor=*/true, /*DefaultMoveCtor=*/false>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    ExpectedApiCtors(ExpectedApiCtors const&) = default;

    constexpr ExpectedApiCtors(ExpectedApiCtors&& src) noexcept(
        conjunction<disjunction<is_void<TValue>, is_nothrow_move_constructible<TValue>>,
                    disjunction<is_void<TError>, is_nothrow_move_constructible<TError>>>::value)
        : ExpectedPayload<TValue, TError>{ ExpectedCtorBypass{}, std::move(src) }
    {
    }

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/false, /*DefaultCopyCtor=*/false, /*MoveCtor=*/true, /*DefaultMoveCtor=*/true>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    ExpectedApiCtors(ExpectedApiCtors const&) = delete;
    ExpectedApiCtors(ExpectedApiCtors&&) = default;

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/false, /*DefaultCopyCtor=*/false, /*MoveCtor=*/false, /*DefaultMoveCtor=*/false>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    ExpectedApiCtors(ExpectedApiCtors const&) = delete;
    ExpectedApiCtors(ExpectedApiCtors&&) = delete;

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/false, /*DefaultCopyCtor=*/false, /*MoveCtor=*/true, /*DefaultMoveCtor=*/false>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    ExpectedApiCtors(ExpectedApiCtors const&) = delete;

    constexpr ExpectedApiCtors(ExpectedApiCtors&& src) noexcept(
        conjunction<disjunction<is_void<TValue>, is_nothrow_move_constructible<TValue>>,
                    disjunction<is_void<TError>, is_nothrow_move_constructible<TError>>>::value)
        : ExpectedPayload<TValue, TError>{ ExpectedCtorBypass{}, std::move(src) }
    {
    }

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/true, /*DefaultCopyCtor=*/false, /*MoveCtor=*/true, /*DefaultMoveCtor=*/true>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    constexpr ExpectedApiCtors(ExpectedApiCtors const& src) noexcept(
        conjunction<disjunction<is_void<TValue>, is_nothrow_copy_constructible<TValue>>,
                    disjunction<is_void<TError>, is_nothrow_copy_constructible<TError>>>::value)
        : ExpectedPayload<TValue, TError>{ ExpectedCtorBypass{}, src }
    {
    }

    ExpectedApiCtors(ExpectedApiCtors&&) = default;

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/true, /*DefaultCopyCtor=*/false, /*MoveCtor=*/false, /*DefaultMoveCtor=*/false>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    constexpr ExpectedApiCtors(ExpectedApiCtors const& src) noexcept(
        conjunction<disjunction<is_void<TValue>, is_nothrow_copy_constructible<TValue>>,
                    disjunction<is_void<TError>, is_nothrow_copy_constructible<TError>>>::value)
        : ExpectedPayload<TValue, TError>{ ExpectedCtorBypass{}, src }
    {
    }

    ExpectedApiCtors(ExpectedApiCtors&&) = delete;

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

template <typename TValue, typename TError>
class ExpectedApiCtors<TValue, TError, /*CopyCtor=*/true, /*DefaultCopyCtor=*/false, /*MoveCtor=*/true, /*DefaultMoveCtor=*/false>
    : public ExpectedPayload<TValue, TError>
{
public:
    using ExpectedPayload<TValue, TError>::ExpectedPayload;

    constexpr ExpectedApiCtors(ExpectedApiCtors const& src) noexcept(
        conjunction<disjunction<is_void<TValue>, is_nothrow_copy_constructible<TValue>>,
                    disjunction<is_void<TError>, is_nothrow_copy_constructible<TError>>>::value)
        : ExpectedPayload<TValue, TError>{ ExpectedCtorBypass{}, src }
    {
    }

    constexpr ExpectedApiCtors(ExpectedApiCtors&& src) noexcept(
        conjunction<disjunction<is_void<TValue>, is_nothrow_move_constructible<TValue>>,
                    disjunction<is_void<TError>, is_nothrow_move_constructible<TError>>>::value)
        : ExpectedPayload<TValue, TError>{ ExpectedCtorBypass{}, std::move(src) }
    {
    }

    ExpectedApiCtors& operator=(ExpectedApiCtors const&) = default;
    ExpectedApiCtors& operator=(ExpectedApiCtors&&) = default;

    ~ExpectedApiCtors() = default;
};

//! \tparam IsObject Is the error an object type? This is false in the case where \c TError is a possibly cv-qualified
//!         \c void. The allowance of cv-qualified types is why the partial specialization operates on this extra
//!         parameter instead of simply covering the case of `class ExpectedApiError<TValue, void>`.
template <typename TValue, typename TError, bool IsObject = !is_void<TError>::value>
class ExpectedApiError : public ExpectedApiCtors<TValue, TError>
{
    using BaseType = ExpectedApiCtors<TValue, TError>;

public:
    using BaseType::BaseType;

    template <typename... TArgs, typename = enable_if_t<is_constructible<TError, TArgs...>::value>>
    explicit ExpectedApiError(unexpect_t, TArgs&&... args) noexcept(is_nothrow_constructible<TError, TArgs...>::value)
        : BaseType{ unexpect, std::forward<TArgs>(args)... }
    {
    }

    constexpr TError const& error() const& noexcept
    {
        if (CARB_UNLIKELY(this->m_state != ExpectedState::eUNEXPECTED))
            invalid_expected_access_error();

        return this->m_storage.error;
    }

    constexpr TError& error() & noexcept
    {
        if (CARB_UNLIKELY(this->m_state != ExpectedState::eUNEXPECTED))
            invalid_expected_access_error();

        return this->m_storage.error;
    }

    constexpr TError const&& error() const&& noexcept
    {
        if (CARB_UNLIKELY(this->m_state != ExpectedState::eUNEXPECTED))
            invalid_expected_access_error();

        return std::move(this->m_storage.error);
    }

    constexpr TError&& error() && noexcept
    {
        if (CARB_UNLIKELY(this->m_state != ExpectedState::eUNEXPECTED))
            invalid_expected_access_error();

        return std::move(this->m_storage.error);
    }

protected:
    //! \{
    //! Called from \c ExpectedApiValue when a caller attempts to access a \c value requiring function, but the monad is
    //! in the error state. These functions throw their errors in the exception, but when \c TError is \c void, the
    //! \c m_storage.error is invalid (if both \c TValue and \c TError are \c void, \c m_storage does not exist at all).
    //! Handling this at the \c ExpectedApiError layer seems the most elegant approach.
    //!
    //! \pre `this->m_state == ExpectedState::eUNEXPECTED`
    [[noreturn]] void invalid_value_access() const&
    {
        CARB_FATAL_UNLESS(
            this->m_state == ExpectedState::eUNEXPECTED, "internal error: omni::expected::m_state must be eUNEXPECTED");
        invalid_expected_access(this->m_storage.error);
    }

    [[noreturn]] void invalid_value_access() &
    {
        CARB_FATAL_UNLESS(
            this->m_state == ExpectedState::eUNEXPECTED, "internal error: omni::expected::m_state must be eUNEXPECTED");
        invalid_expected_access(this->m_storage.error);
    }

    [[noreturn]] void invalid_value_access() &&
    {
        CARB_FATAL_UNLESS(
            this->m_state == ExpectedState::eUNEXPECTED, "internal error: omni::expected::m_state must be eUNEXPECTED");
        invalid_expected_access(std::move(this->m_storage.error));
    }

    [[noreturn]] void invalid_value_access() const&&
    {
        CARB_FATAL_UNLESS(
            this->m_state == ExpectedState::eUNEXPECTED, "internal error: omni::expected::m_state must be eUNEXPECTED");
        invalid_expected_access(std::move(this->m_storage.error));
    }
    //! \}
};

template <typename TValue, typename TError>
class ExpectedApiError<TValue, TError, /*IsObject=*/false> : public ExpectedApiCtors<TValue, TError>
{
    using BaseType = ExpectedApiCtors<TValue, TError>;
    using BaseType::BaseType;

public:
    constexpr ExpectedApiError(unexpect_t) noexcept : BaseType{ unexpect }
    {
    }

    // NOTE: This from-unexpected constructor does not have a mirror in the `ExpectedApiError<..., IsObject=True>`
    // implementation, as that conversion constructor comes from the `expected` class.
    constexpr ExpectedApiError(unexpected<void> const&) noexcept : BaseType{ unexpect }
    {
    }

    constexpr void error() const& noexcept
    {
        if (CARB_UNLIKELY(this->m_state != ExpectedState::eUNEXPECTED))
            invalid_expected_access_error();
    }

    constexpr void error() && noexcept
    {
        if (CARB_UNLIKELY(this->m_state != ExpectedState::eUNEXPECTED))
            invalid_expected_access_error();
    }

protected:
    [[noreturn]] void invalid_value_access() const
    {
        CARB_FATAL_UNLESS(
            this->m_state == ExpectedState::eUNEXPECTED, "internal error: omni::expected::m_state must be eUNEXPECTED");
        invalid_expected_access(ExpectedStorageVoid{});
    }
};

template <typename TValue, typename TError, bool IsDefaultConstructible = std::is_default_constructible<TValue>::value>
class ExpectedApiValueDefaultConstruct : public ExpectedApiError<TValue, TError>
{
    using BaseType = ExpectedApiError<TValue, TError>;
    using BaseType::BaseType;

public:
    constexpr ExpectedApiValueDefaultConstruct() noexcept(std::is_nothrow_default_constructible<TValue>::value)
        : BaseType{ in_place }
    {
    }
};

template <typename TValue, typename TError>
class ExpectedApiValueDefaultConstruct<TValue, TError, /*IsDefaultConstructible =*/false>
    : public ExpectedApiError<TValue, TError>
{
    using BaseType = ExpectedApiError<TValue, TError>;
    using BaseType::BaseType;

    // TValue is not default constructible, so explicitly delete the constructor.
    ExpectedApiValueDefaultConstruct() = delete;
};

//! \tparam IsObject Is the value an object type? This is false in the case where \c TValue is a possibly cv-qualified
//!         \c void. The allowance of cv-qualified types is why the partial specialization operates on this extra
//!         parameter instead of simply covering the case of `class ExpectedApiValue<void, TError>`.
template <typename TValue, typename TError, bool IsObject = !is_void<TValue>::value>
class ExpectedApiValue : public ExpectedApiValueDefaultConstruct<TValue, TError>
{
    using BaseType = ExpectedApiValueDefaultConstruct<TValue, TError>;
    using BaseType::BaseType;

public:
    template <typename... TArgs, typename = enable_if_t<is_constructible<TValue, TArgs...>::value>>
    explicit ExpectedApiValue(in_place_t, TArgs&&... args) noexcept(is_nothrow_constructible<TValue, TArgs...>::value)
        : BaseType{ in_place, std::forward<TArgs>(args)... }
    {
    }

    constexpr TValue& value() &
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            this->invalid_value_access();
        else
            return this->m_storage.value;
    }

    constexpr TValue const& value() const&
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            this->invalid_value_access();
        else
            return this->m_storage.value;
    }

    constexpr TValue&& value() &&
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            std::move(*this).invalid_value_access();
        else
            return std::move(this->m_storage.value);
    }

    constexpr TValue const&& value() const&&
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            std::move(*this).invalid_value_access();
        else
            return std::move(this->m_storage.value);
    }

    template <typename UValue>
    constexpr TValue value_or(UValue&& default_value) const&
    {
        if (this->m_state == ExpectedState::eSUCCESS)
            return this->m_storage.value;
        else
            return static_cast<TValue>(std::forward<UValue>(default_value));
    }

    template <typename UValue>
    constexpr TValue value_or(UValue&& default_value) &&
    {
        if (this->m_state == ExpectedState::eSUCCESS)
            return std::move(this->m_storage.value);
        else
            return static_cast<TValue>(std::forward<UValue>(default_value));
    }

    constexpr TValue const& operator*() const& noexcept
    {
        return this->value();
    }

    constexpr TValue& operator*() & noexcept
    {
        return this->value();
    }

    constexpr TValue const&& operator*() const&& noexcept
    {
        return std::move(*this).value();
    }

    constexpr TValue&& operator*() && noexcept
    {
        return std::move(*this).value();
    }

    constexpr TValue const* operator->() const noexcept
    {
        return &this->value();
    }

    constexpr TValue* operator->() noexcept
    {
        return &this->value();
    }

    template <typename... TArgs>
    constexpr std::enable_if_t<std::is_nothrow_constructible<TValue, TArgs...>::value, TValue&> emplace(TArgs&&... args) noexcept
    {
        return this->emplace_impl(std::forward<TArgs>(args)...);
    }

    template <typename U, typename... TArgs>
    constexpr std::enable_if_t<std::is_nothrow_constructible<TValue, std::initializer_list<U>&, TArgs...>::value, TValue&> emplace(
        std::initializer_list<U>& arg0, TArgs&&... args) noexcept
    {
        return this->emplace_impl(arg0, std::forward<TArgs>(args)...);
    }

private:
    template <typename... TArgs>
    constexpr TValue& emplace_impl(TArgs&&... args)
    {
        if (this->m_state == ExpectedState::eSUCCESS)
            expected_reinit(std::addressof(this->m_storage.value), std::addressof(this->m_storage.value),
                            std::forward<TArgs>(args)...);
        else
            expected_reinit(std::addressof(this->m_storage.error), std::addressof(this->m_storage.value),
                            std::forward<TArgs>(args)...);

        this->m_state = ExpectedState::eSUCCESS;
        return this->m_storage.value;
    }
};

template <typename TValue, typename TError>
class ExpectedApiValue<TValue, TError, /*IsObject=*/false> : public ExpectedApiError<TValue, TError>
{
    using BaseType = ExpectedApiError<TValue, TError>;

public:
    using BaseType::BaseType;

    constexpr explicit ExpectedApiValue() noexcept : BaseType{ in_place }
    {
    }

    constexpr explicit ExpectedApiValue(in_place_t) noexcept : BaseType{ in_place }
    {
    }

    ExpectedApiValue(ExpectedApiValue const&) = default;
    ExpectedApiValue(ExpectedApiValue&&) = default;

    ExpectedApiValue& operator=(ExpectedApiValue const&) = default;
    ExpectedApiValue& operator=(ExpectedApiValue&&) = default;

    ~ExpectedApiValue() = default;

    constexpr void value() &
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            this->invalid_value_access();
    }

    constexpr void value() const&
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            this->invalid_value_access();
    }

    constexpr void value() &&
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            std::move(*this).invalid_value_access();
    }

    constexpr void value() const&&
    {
        if (this->m_state != ExpectedState::eSUCCESS)
            std::move(*this).invalid_value_access();
    }

    constexpr void operator*() const noexcept
    {
        value();
    }

    constexpr void emplace() noexcept
    {
        if (this->m_state != ExpectedState::eSUCCESS)
        {
            // Destroy the error state if one exists (note that if TError is also void, there is no m_storage)
            this->unsafe_destroy();
            this->m_state = ExpectedState::eSUCCESS;
        }
    }
};

template <typename TValue, typename TError>
class ExpectedImpl : public ExpectedApiValue<TValue, TError>
{
    using BaseType = ExpectedApiValue<TValue, TError>;

    static_assert(!std::is_same<in_place_t, std::remove_cv_t<TValue>>::value, "expected value can not be in_place_t");
    static_assert(!std::is_same<in_place_t, std::remove_cv_t<TError>>::value, "expected error can not be in_place_t");
    static_assert(!std::is_same<unexpect_t, std::remove_cv_t<TValue>>::value, "expected value can not be unexpect_t");
    static_assert(!std::is_same<unexpect_t, std::remove_cv_t<TError>>::value, "expected error can not be unexpect_t");

public:
    using BaseType::BaseType;
};

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Monadic Operations                                                                                                 //
// Functions like `expected::transform` are complicated by `void`, which is syntactically separate from a value type. //
// The implementation is split into separate parts: `ExpectedMonadOpImpl`, which contains the implementation of all   //
// valid monadic operations and is specialized per type transform; `ExpectedOp___` per function, which chooses the    //
// proper type transformation. The grouping of functions this way seems slightly easier to read, but it still hairy.  //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// MSC thinks some of the code branches in these implementations are unreachable. Specifically, it dislikes the use of a
// return statement after a call to `carb::cpp::invoke(f)` (with no second parameter). The invoke implementation is
// not marked `[[noreturn]]` or anything like that and the unit tests exercise that code path, so it is unclear why MSC
// thinks that. This can be removed when MS fixes the bug.
CARB_IGNOREWARNING_MSC_WITH_PUSH(4702) // unreachable code

//! Each \c ExpectedMonadOpImpl contains the four monadic operations for \c expected (22.8.6.7). The template parameters
//! represent the non-ref-qualified \c value_type and \c error_type parameters of the \c expected instance and result
//! type; \c TValue and \c TError for the instance, \c RValue and \c RError for the result. The function implementation
//! takes care of the ref-qualification of the expression category (e.g. the \c expected::transform ref-qualified as
//! `&&` passes \c TExpected as `std::move(*this)` so the values are moved).
//!
//! Partial specializations of this place \c void for the type parameters, since the syntax for invoking and returning
//! \c void is different than a non \c void value. There are 16 specializations of this template, but not all
//! specializations contain implementations for all functions, as some of them are invalid. For example, it is not legal
//! to change the type of \c error_type via the \c transform operation, so the \c ExpectedMonadOpImpl where
//! `(TError == void) != (RError == void)` do not exist.
template <typename TValue, typename TError, typename RValue, typename RError>
struct ExpectedMonadOpImpl
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, TError> transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, TError>(
                in_place, carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value()));
        else
            return omni::expected<RValue, TError>(unexpect, std::forward<TExpected>(ex).error());
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, RError> and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value());
        else
            return omni::expected<RValue, RError>(unexpect, std::forward<TExpected>(ex).error());
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, RError> transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, RError>(in_place, std::forward<TExpected>(ex).value());
        else
            return omni::expected<RValue, RError>(
                unexpect, carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error()));
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, RError> or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, RError>(in_place, std::forward<TExpected>(ex).value());
        else
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error());
    }
};

template <typename TError, typename RError>
struct ExpectedMonadOpImpl<void, TError, void, RError>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, TError> transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            carb::cpp::invoke(std::forward<FTransform>(f));
            return omni::expected<void, TError>(in_place);
        }
        else
        {
            return omni::expected<void, TError>(unexpect, std::forward<TExpected>(ex).error());
        }
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, RError> and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f));
        else
            return omni::expected<void, RError>(unexpect, std::forward<TExpected>(ex).error());
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, RError> transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<void, RError>(in_place);
        else
            return omni::expected<void, RError>(
                unexpect, carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error()));
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, RError> or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<void, RError>(in_place);
        else
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error());
    }
};

template <typename TValue, typename RValue>
struct ExpectedMonadOpImpl<TValue, void, RValue, void>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, void>(
                in_place, carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value()));
        else
            return omni::expected<RValue, void>(unexpect);
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value());
        else
            return omni::expected<RValue, void>(unexpect);
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            return omni::expected<RValue, void>(in_place, std::forward<TExpected>(ex).value());
        }
        else
        {
            carb::cpp::invoke(std::forward<FTransform>(f));
            return omni::expected<RValue, void>(unexpect);
        }
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, void>(in_place, std::forward<TExpected>(ex).value());
        else
            return carb::cpp::invoke(std::forward<FTransform>(f));
    }
};

template <typename TValue, typename TError, typename RError>
struct ExpectedMonadOpImpl<TValue, TError, void, RError>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, TError> transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value());
            return omni::expected<void, TError>(in_place);
        }
        else
        {
            return omni::expected<void, TError>(unexpect, std::forward<TExpected>(ex).error());
        }
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, RError> and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value());
        else
            return omni::expected<void, RError>(unexpect, std::forward<TExpected>(ex).error());
    }
};

template <typename TError, typename RValue, typename RError>
struct ExpectedMonadOpImpl<void, TError, RValue, RError>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, TError> transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, TError>(in_place, carb::cpp::invoke(std::forward<FTransform>(f)));
        else
            return omni::expected<RValue, TError>(unexpect, std::forward<TExpected>(ex).error());
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, RError> and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f));
        else
            return omni::expected<RValue, RError>(unexpect, std::forward<TExpected>(ex).error());
    }
};

template <typename TValue>
struct ExpectedMonadOpImpl<TValue, void, void, void>
{
    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value());
            return TReturn(in_place);
        }
        else
        {
            return TReturn(unexpect);
        }
    }

    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).value());
        else
            return TReturn(unexpect);
    }
};

template <typename RValue>
struct ExpectedMonadOpImpl<void, void, RValue, void>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, void>(in_place, carb::cpp::invoke(std::forward<FTransform>(f)));
        else
            return omni::expected<RValue, void>(unexpect);
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f));
        else
            return omni::expected<RValue, void>(unexpect);
    }
};

template <typename TValue, typename TError, typename RValue>
struct ExpectedMonadOpImpl<TValue, TError, RValue, void>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            return omni::expected<RValue, void>(in_place, std::forward<TExpected>(ex).value());
        }
        else
        {
            carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error());
            return omni::expected<RValue, void>(unexpect);
        }
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, void> or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, void>(in_place, std::forward<TExpected>(ex).value());
        else
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error());
    }
};

template <typename TError>
struct ExpectedMonadOpImpl<void, TError, void, void>
{
    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            return TReturn(in_place);
        }
        else
        {
            carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error());
            return TReturn(unexpect);
        }
    }

    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return TReturn(in_place);
        else
            return carb::cpp::invoke(std::forward<FTransform>(f), std::forward<TExpected>(ex).error());
    }
};

template <typename TValue, typename RValue, typename RError>
struct ExpectedMonadOpImpl<TValue, void, RValue, RError>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, RError> transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, RError>(in_place, std::forward<TExpected>(ex).value());
        else
            return omni::expected<RValue, RError>(unexpect, carb::cpp::invoke(std::forward<FTransform>(f)));
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<RValue, RError> or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<RValue, RError>(in_place, std::forward<TExpected>(ex).value());
        else
            return carb::cpp::invoke(std::forward<FTransform>(f));
    }
};

template <typename RError>
struct ExpectedMonadOpImpl<void, void, void, RError>
{
    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, RError> transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<void, RError>(in_place);
        else
            return omni::expected<void, RError>(unexpect, carb::cpp::invoke(std::forward<FTransform>(f)));
    }

    template <typename FTransform, typename TExpected>
    static constexpr omni::expected<void, RError> or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return omni::expected<void, RError>(in_place);
        else
            return carb::cpp::invoke(std::forward<FTransform>(f));
    }
};

template <>
struct ExpectedMonadOpImpl<void, void, void, void>
{
    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn transform(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            carb::cpp::invoke(std::forward<FTransform>(f));
            return TReturn(in_place);
        }
        else
        {
            return TReturn(unexpect);
        }
    }

    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn and_then(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return carb::cpp::invoke(std::forward<FTransform>(f));
        else
            return TReturn(unexpect);
    }

    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn transform_error(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
        {
            return TReturn(in_place);
        }
        else
        {
            carb::cpp::invoke(std::forward<FTransform>(f));
            return TReturn(unexpect);
        }
    }

    template <typename FTransform, typename TExpected, typename TReturn = omni::expected<void, void>>
    static constexpr TReturn or_else(FTransform&& f, TExpected&& ex)
    {
        if (ex.has_value())
            return TReturn(in_place);
        else
            return carb::cpp::invoke(std::forward<FTransform>(f));
    }
};

template <typename FTransform, typename TExpected, typename RefExpected, typename = void_t<>>
struct ExpectedOpTransform
{
};

template <typename FTransform, typename TValue, typename TError, typename RefExpected>
struct ExpectedOpTransform<FTransform,
                           omni::expected<TValue, TError>,
                           RefExpected,
                           void_t<carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().value())>>>
    : ExpectedMonadOpImpl<TValue, TError, carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().value())>, TError>
{
};

template <typename FTransform, typename TError, typename RefExpected>
struct ExpectedOpTransform<FTransform, omni::expected<void, TError>, RefExpected, void_t<carb::cpp::invoke_result_t<FTransform>>>
    : ExpectedMonadOpImpl<void, TError, carb::cpp::invoke_result_t<FTransform>, TError>
{
};

template <typename FTransform, typename TExpected, typename RefExpected, typename = void_t<>>
struct ExpectedOpAndThen
{
    template <typename UExpected>
    static constexpr void and_then(FTransform&&, UExpected&&)
    {
        // HELLO! If you're seeing one of these failures, that means you called `.and_then` with a callable that can't
        // be called with the `value_type` of the expected. This base template is only used through misuse of that
        // member function, so one of these `static_assert`s will always hit and give a slightly better diagnostic.
        static_assert(is_void<typename TExpected::value_type>::value,
                      "function provided to `and_then` must accept the `expected::value_type`");
        static_assert(!is_void<typename TExpected::value_type>::value,
                      "function provided to `and_then` must accept no parameters");
    }
};

template <typename TExpected, typename UExpected>
struct ExpectedOpAndThenImpl
{
    template <typename FTransform, typename VExpected>
    static constexpr void and_then(FTransform&&, VExpected&&)
    {
        // HELLO! If you're seeing this failure, it means the function provided to `.and_then` did not return an
        // `expected` when called with the `value_type`.
        static_assert(is_void<FTransform>::value, "function provided to `and_then` must return an `expected<T, E>`");
    }
};

template <typename TValue, typename TError, typename UValue, typename UError>
struct ExpectedOpAndThenImpl<omni::expected<TValue, TError>, omni::expected<UValue, UError>>
    : ExpectedMonadOpImpl<TValue, TError, UValue, UError>
{
};

template <typename FTransform, typename TValue, typename TError, typename RefExpected>
struct ExpectedOpAndThen<FTransform,
                         omni::expected<TValue, TError>,
                         RefExpected,
                         void_t<carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().value())>>>
    : ExpectedOpAndThenImpl<omni::expected<TValue, TError>,
                            carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().value())>>
{
};

template <typename FTransform, typename TError, typename RefExpected>
struct ExpectedOpAndThen<FTransform, omni::expected<void, TError>, RefExpected, void_t<carb::cpp::invoke_result_t<FTransform>>>
    : ExpectedOpAndThenImpl<omni::expected<void, TError>, carb::cpp::invoke_result_t<FTransform>>
{
};

template <typename FTransform, typename TExpected, typename RefExpected, typename = void_t<>>
struct ExpectedOpTransformError
{
};

template <typename FTransform, typename TValue, typename TError, typename RefExpected>
struct ExpectedOpTransformError<FTransform,
                                omni::expected<TValue, TError>,
                                RefExpected,
                                void_t<carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().error())>>>
    : ExpectedMonadOpImpl<TValue,
                          TError,
                          TValue,
                          carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().error())>>
{
};

template <typename FTransform, typename TValue, typename RefExpected>
struct ExpectedOpTransformError<FTransform, omni::expected<TValue, void>, RefExpected, void_t<carb::cpp::invoke_result_t<FTransform>>>
    : ExpectedMonadOpImpl<TValue, void, TValue, carb::cpp::invoke_result_t<FTransform>>
{
};

template <typename FTransform, typename TExpected, typename RefExpected, typename = void_t<>>
struct ExpectedOpOrElse
{
    template <typename UExpected>
    static constexpr void or_else(FTransform&&, UExpected&&)
    {
        // HELLO! If you're seeing one of these failures, that means you called `.or_else` with a callable that can't
        // be called with the `value_type` of the expected. This base template is only used through misuse of that
        // member function, so one of these `static_assert`s will always hit and give a slightly better diagnostic.
        static_assert(is_void<typename TExpected::error_type>::value,
                      "function provided to `or_else` must accept the `expected::value_type`");
        static_assert(!is_void<typename TExpected::error_type>::value,
                      "function provided to `or_else` must accept no parameters");
    }
};

template <typename TExpected, typename UExpected>
struct ExpectedOpOrElseImpl
{
    template <typename FTransform, typename VExpected>
    static constexpr void or_else(FTransform&&, VExpected&&)
    {
        // HELLO! If you're seeing this failure, it means the function provided to `.or_else` did not return an
        // `expected` when called with the `value_type`.
        static_assert(is_void<FTransform>::value, "function provided to `or_else` must return an `expected<T, E>`");
    }
};

template <typename TValue, typename TError, typename UValue, typename UError>
struct ExpectedOpOrElseImpl<omni::expected<TValue, TError>, omni::expected<UValue, UError>>
    : ExpectedMonadOpImpl<TValue, TError, UValue, UError>
{
};

template <typename FTransform, typename TValue, typename TError, typename RefExpected>
struct ExpectedOpOrElse<FTransform,
                        omni::expected<TValue, TError>,
                        RefExpected,
                        void_t<carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().error())>>>
    : ExpectedOpOrElseImpl<omni::expected<TValue, TError>,
                           carb::cpp::invoke_result_t<FTransform, decltype(std::declval<RefExpected>().error())>>
{
};

template <typename FTransform, typename TValue, typename RefExpected>
struct ExpectedOpOrElse<FTransform, omni::expected<TValue, void>, RefExpected, void_t<carb::cpp::invoke_result_t<FTransform>>>
    : ExpectedOpOrElseImpl<omni::expected<TValue, void>, carb::cpp::invoke_result_t<FTransform>>
{
};

CARB_IGNOREWARNING_MSC_POP

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Comparison Functions                                                                                               //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

template <typename TExpected1, typename TExpected2, typename = void_t<>>
struct ExpectedComparer
{
};

template <typename TValue1, typename TError1, typename TValue2, typename TError2>
struct ExpectedComparer<
    expected<TValue1, TError1>,
    expected<TValue2, TError2>,
    std::enable_if_t<negation<disjunction<is_void<TValue1>, is_void<TError1>, is_void<TValue2>, is_void<TError2>>>::value>>
{
    template <typename TExpectedLhs, typename TExpectedRhs>
    static constexpr bool eq(TExpectedLhs const& lhs, TExpectedRhs const& rhs)
    {
        if (lhs.has_value() && rhs.has_value())
            return lhs.value() == rhs.value();
        else if (!lhs.has_value() && !rhs.has_value())
            return lhs.error() == rhs.error();
        else
            return false;
    }
};

template <typename TValue1, typename TValue2>
struct ExpectedComparer<expected<TValue1, void>,
                        expected<TValue2, void>,
                        enable_if_t<negation<disjunction<is_void<TValue1>, is_void<TValue2>>>::value>>
{
    template <typename TExpectedLhs, typename TExpectedRhs>
    static constexpr bool eq(TExpectedLhs const& lhs, TExpectedRhs const& rhs)
    {
        if (lhs.has_value() && rhs.has_value())
            return lhs.value() == rhs.value();
        else if (!lhs.has_value() && !rhs.has_value())
            return true;
        else
            return false;
    }
};

template <typename TError1, typename TError2>
struct ExpectedComparer<expected<void, TError1>,
                        expected<void, TError2>,
                        enable_if_t<negation<disjunction<is_void<TError1>, is_void<TError2>>>::value>>
{
    template <typename TExpectedLhs, typename TExpectedRhs>
    static constexpr bool eq(TExpectedLhs const& lhs, TExpectedRhs const& rhs)
    {
        if (lhs.has_value() && rhs.has_value())
            return true;
        else if (!lhs.has_value() && !rhs.has_value())
            return lhs.error() == rhs.error();
        else
            return false;
    }
};

template <>
struct ExpectedComparer<expected<void, void>, expected<void, void>, void>
{
    template <typename TExpected>
    static constexpr bool eq(TExpected const& lhs, TExpected const& rhs)
    {
        return lhs.has_value() == rhs.has_value();
    }
};

template <typename TErrorLhs, typename TErrorRhs>
struct ExpectedUnexpectedComparer
{
    template <typename TExpected, typename TUnexpected>
    static constexpr bool eq(TExpected const& lhs, TUnexpected const& rhs)
    {
        return !lhs.has_value() && static_cast<bool>(lhs.error() == rhs.error());
    }
};

template <>
struct ExpectedUnexpectedComparer<void, void>
{
    template <typename TExpected>
    static constexpr bool eq(TExpected const& lhs, unexpected<void> const&)
    {
        return !lhs.has_value();
    }
};

} // namespace detail
} // namespace omni

//! \endcond
