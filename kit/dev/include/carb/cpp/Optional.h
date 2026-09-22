// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// Implements std::optional from C++17 using C++14 paradigms.
// Heavily borrowed from MS STL: https://github.com/microsoft/STL/blob/master/stl/inc/optional

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<optional>` library.
#pragma once

#include "../Defines.h"

#define CARB_IMPLOPTIONAL
#include "detail/ImplOptional.h"
#undef CARB_IMPLOPTIONAL

#include <utility>
#include <type_traits>

namespace carb
{
namespace cpp
{

//! Identifies an empty optional object.  This can be used to initialize or reinitialize an
//! empty optional object as needed.
struct nullopt_t
{
    //! @private
    struct Tag
    {
    };
    //! @private
    explicit constexpr nullopt_t(Tag)
    {
    }
};

//! Constant that identifies an empty optional object.  This can be used to initialize or
//! reinitialize an empty optional object as needed.
static constexpr nullopt_t nullopt{ nullopt_t::Tag{} };

//! Exception object identifying that an invalid use of an optional object was made.
class bad_optional_access final : public std::exception
{
public:
#ifndef DOXYGEN_BUILD
    bad_optional_access() noexcept = default;
    bad_optional_access(const bad_optional_access&) noexcept = default;
    bad_optional_access& operator=(const bad_optional_access&) noexcept = default;
    virtual const char* what() const noexcept override
    {
        return "bad optional access";
    }
#endif
};

/** Template class to identify an optional value.  This object may either contain a specific
 *  value of type `T`, or be empty.  The object can be queried to first see if it is empty or
 *  not, then if not empty dereferenced to retrieve the contained value.  Attempting to
 *  dereference an empty optional object is considered an error and will thrown an exception
 *  or terminate if exceptions are not enabled.
 *
 *  This template is intended to be a drop-in replacement for `std::optional` when building
 *  with C++14.  For builds using C++17 and up, `std::optional` should be used instead.
 */
template <class T>
class CARB_VIZ optional : private detail::SelectHierarchy<detail::OptionalConstructor<T>, T>
{
    //! @private
    using BaseClass = detail::SelectHierarchy<detail::OptionalConstructor<T>, T>;

    static_assert(!std::is_same<std::remove_cv_t<T>, nullopt_t>::value &&
                      !std::is_same<std::remove_cv_t<T>, std::in_place_t>::value,
                  "T may not be nullopt_t or inplace_t");
    static_assert(std::is_object<T>::value && std::is_destructible<T>::value && !std::is_array<T>::value,
                  "T does not meet Cpp17Destructible requirements");

    // Essentially: !is_same(U, optional) && !is_same(U, in_place_t) && is_constructible(T from U)
    //! @private
    template <class U>
    using AllowDirectConversion = std::bool_constant<std::conjunction<
        std::negation<std::is_same<typename std::remove_reference_t<typename std::remove_cv_t<U>>, optional>>,
        std::negation<std::is_same<typename std::remove_reference_t<typename std::remove_cv_t<U>>, std::in_place_t>>,
        std::is_constructible<T, U>>::value>;

    // Essentially: !(is_same(T, U) || is_constructible(T from optional<U>) || is_convertible(optional<U> to T))
    //! @private
    template <class U>
    struct AllowUnwrapping : std::bool_constant<!std::disjunction<std::is_same<T, U>,
                                                                  std::is_constructible<T, optional<U>&>,
                                                                  std::is_constructible<T, const optional<U>&>,
                                                                  std::is_constructible<T, const optional<U>>,
                                                                  std::is_constructible<T, optional<U>>,
                                                                  std::is_convertible<optional<U>&, T>,
                                                                  std::is_convertible<const optional<U>&, T>,
                                                                  std::is_convertible<const optional<U>, T>,
                                                                  std::is_convertible<optional<U>, T>>::value>
    {
    };

    // Essentially: !(is_same(T, U) || is_assignable(T& from optional<U>))
    //! @private
    template <class U>
    struct AllowUnwrappingAssignment : std::bool_constant<!std::disjunction<std::is_same<T, U>,
                                                                            std::is_assignable<T&, optional<U>&>,
                                                                            std::is_assignable<T&, const optional<U>&>,
                                                                            std::is_assignable<T&, const optional<U>>,
                                                                            std::is_assignable<T&, optional<U>>>::value>
    {
    };

    //! Unconditionally throws a @ref bad_optional_access exception.  Does not return.
    [[noreturn]] static void onBadAccess()
    {
#if CARB_EXCEPTIONS_ENABLED
        throw bad_optional_access();
#else
        CARB_FATAL_UNLESS(0, "bad optional access");
#endif
    }

public:
    //! Type alias for the data type stored in this optional object.
    using value_type = T;

    //! Constructor: constructs an empty optional object.  The value in this object cannot be
    //! dereferenced.
    constexpr optional() noexcept
    {
    }
    //! Constructor: constructs an empty optional object.  The value in this object cannot be
    //! dereferenced.  This constructor variant allows for `nullopt` to be assigned to this
    //! object as a way of resetting or emptying it.
    constexpr optional(nullopt_t) noexcept
    {
    }

    //! Copy constructor: constructs a new optional value by copying the state from another optional
    //! object.
    //!
    //! @param[in] other    The other optional object to copy the value or lack of value from.
    optional(const optional& other) : BaseClass(static_cast<const BaseClass&>(other))
    {
    }

    //! Move constructor: constructs a new optional value by moving the state from another optional
    //! object.
    //!
    //! @param[in] other    The other optional object to move the value or lack of value from.
    //!                     The value contained in @p other must be move constructible to the data
    //!                     type expected in this object.  The @p other object will be left in a
    //!                     valid but undefined state upon return.
    optional(optional&& other) noexcept(std::is_nothrow_move_constructible<T>::value)
        : BaseClass(static_cast<BaseClass&&>(std::move(other)))
    {
    }

    //! Copy-assignment operator.
    //!
    //! @param[in] other    The other optional object to copy the value or lack of value from.
    //! @returns A reference to this object.
    optional& operator=(const optional& other)
    {
        if (other)
            this->assign(*other);
        else
            reset();
        return *this;
    }

    //! Move-assignment operator.
    //!
    //! @param[in] other    The other optional object to move the value or lack of value from.
    //!                     The value contained in @p other must be move constructible to the data
    //!                     type expected in this object.  The @p other object will be left in a
    //!                     valid but undefined state upon return.
    //! @returns A reference to this object.
    optional& operator=(optional&& other) noexcept(
        std::is_nothrow_move_assignable<T>::value&& std::is_nothrow_move_constructible<T>::value)
    {
        if (other)
            this->assign(std::move(*other));
        else
            reset();
        return *this;
    }

    // The spec states that this is conditionally-explicit, which is a C++20 feature, so we have to work around it by
    // having two functions with SFINAE
    //! Copy constructor: copies the value or lack of value from another optional object.
    //!
    //! @param[in] other    The other optional object to move the value or lack of value from.
    //!                     The value contained in @p other must be copy constructible to the data
    //!                     type expected in this object.  The @p other object will be left
    //!                     unmodified.
    template <class U,
              typename std::enable_if_t<
                  std::conjunction<AllowUnwrapping<U>, std::is_constructible<T, const U&>, std::is_convertible<const U&, T>>::value,
                  int> = 0>
    optional(const optional<U>& other)
    {
        if (other)
            this->construct(*other);
    }
#ifndef DOXYGEN_BUILD
    // Note: this constructor is excluded from the docs build because the `rebreather` tool
    //       sees this constructor as a duplicate of the one above and generates an error.
    //! Copy constructor: copies the value or lack of value from another optional object.
    //!
    //! @param[in] other    The other optional object to copy the value or lack of value from.
    //!                     The value contained in @p other must be copy constructible to the data
    //!                     type expected in this object.  The @p other object will be left
    //!                     unmodified.
    template <class U,
              typename std::enable_if_t<std::conjunction<AllowUnwrapping<U>,
                                                         std::is_constructible<T, const U&>,
                                                         std::negation<std::is_convertible<const U&, T>>>::value,
                                        int> = 0>
    explicit optional(const optional<U>& other)
    {
        if (other)
            this->construct(*other);
    }
#endif

    // The spec states that this is conditionally-explicit, which is a C++20 feature, so we have to work around it by
    // having two functions with SFINAE
    //! Move constructor: moves the state from another optional object into this one.
    //!
    //! @param[in] other    The other optional object to move the value or lack of value from.
    //!                     The value contained in @p other must be move constructible to the data
    //!                     type expected in this object.  The @p other object will be left in a
    //!                     valid but undefined state upon return.
    template <class U,
              typename std::enable_if_t<
                  std::conjunction<AllowUnwrapping<U>, std::is_constructible<T, U>, std::is_convertible<U, T>>::value,
                  int> = 0>
    optional(optional<U>&& other)
    {
        if (other)
            this->construct(std::move(*other));
    }
#ifndef DOXYGEN_BUILD
    // Note: this constructor is excluded from the docs build because the `rebreather` tool
    //       sees this constructor as a duplicate of the one above and generates an error.
    //! Move constructor: moves the state from another optional object into this one.
    //!
    //! @param[in] other    The other optional object to move the value or lack of value from.
    //!                     The value contained in @p other must be move constructible to the data
    //!                     type expected in this object.  The @p other object will be left in a
    //!                     valid but undefined state upon return.
    template <class U,
              typename std::enable_if_t<
                  std::conjunction<AllowUnwrapping<U>, std::is_constructible<T, U>, std::negation<std::is_convertible<U, T>>>::value,
                  int> = 0>
    explicit optional(optional<U>&& other)
    {
        if (other)
            this->construct(std::move(*other));
    }
#endif

    //! Constructor: piecewise constructs a new optional object from multiple arguments.
    //!
    //! @param[in] args The arguments used to contruct the value contained in the new object.
    //!                 These arguments will be forwarded unmodified to the contained type's
    //!                 constructor.
    template <class... Args, typename std::enable_if_t<std::is_constructible<T, Args...>::value, int> = 0>
    optional(std::in_place_t, Args&&... args) : BaseClass(std::in_place, std::forward<Args>(args)...)
    {
    }

    //! Constructor: piecewise constructs a new optional object from multiple arguments.
    //!
    //! @param[in] ilist    The initializer list used to construct the new object.
    //! @param[in] args     The arguments used to satisfy the initializer list @p ilist.
    template <class U,
              class... Args,
              typename std::enable_if_t<std::is_constructible<T, std::initializer_list<U>&, Args...>::value, int> = 0>
    optional(std::in_place_t, std::initializer_list<U> ilist, Args&&... args)
        : BaseClass(std::in_place, ilist, std::forward<Args>(args)...)
    {
    }

    // The spec states that this is conditionally-explicit, which is a C++20 feature, so we have to work around it by
    // having two functions with SFINAE
    //! Move constructor: moves a value into this object.
    //!
    //! @param[in] value    The new value to assign to this object.  This value must be move
    //!                     constructible to the data type expected in this object.  The @p value
    //!                     object will be left in a vaid but undefined state upon return.
    template <class U = value_type,
              typename std::enable_if_t<std::conjunction<AllowDirectConversion<U>, std::is_convertible<U, T>>::value, int> = 0>
    constexpr optional(U&& value) : BaseClass(std::in_place, std::forward<U>(value))
    {
    }
#ifndef DOXYGEN_BUILD
    // Note: this constructor is excluded from the docs build because the `rebreather` tool
    //       sees this constructor as a duplicate of the one above and generates an error.
    //! Move constructor: moves a value into this object.
    //!
    //! @param[in] value    The new value to assign to this object.  This value must be move
    //!                     constructible to the data type expected in this object.  The @p value
    //!                     object will be left in a valid but undefined state upon return.
    template <class U = value_type,
              typename std::enable_if_t<std::conjunction<AllowDirectConversion<U>, std::negation<std::is_convertible<U, T>>>::value,
                                        int> = 0>
    constexpr explicit optional(U&& value) : BaseClass(std::in_place, std::forward<U>(value))
    {
    }
#endif

    ~optional() = default;

    //! Null assignment operator.  This will clear out any value stored in this object and reset
    //! it to its default constructed state.
    //!
    //! @returns A reference to this object.
    optional& operator=(nullopt_t) noexcept
    {
        reset();
        return *this;
    }

    //! Value assignment operator.
    //!
    //! @param[in] value    The new raw value to assign to this object.  This value may be of any
    //!                     type that can be implicitly converted to this object's contained type.
    //! @returns A reference to this object.
    template <class U = T,
              typename std::enable_if_t<
                  std::conjunction<
                      std::negation<std::is_same<optional, typename std::remove_cv_t<typename std::remove_reference_t<U>>>>,
                      std::negation<std::conjunction<std::is_scalar<T>, std::is_same<T, typename std::decay_t<U>>>>,
                      std::is_constructible<T, U>,
                      std::is_assignable<T&, U>>::value,
                  int> = 0>
    optional& operator=(U&& value)
    {
        this->assign(std::forward<U>(value));
        return *this;
    }

    //! Value assignment operator.
    //!
    //! @param[in] other    The optional value containing the new value (or lack of value) to
    //!                     assign to this object.  The contained value may be of any type that
    //!                     can be implicitly converted to this object's contained type.
    //! @returns A reference to this object.
    template <class U,
              typename std::enable_if_t<std::conjunction<AllowUnwrappingAssignment<U>,
                                                         std::is_constructible<T, const U&>,
                                                         std::is_assignable<T&, const U&>>::value,
                                        int> = 0>
    optional& operator=(const optional<U>& other)
    {
        if (other)
            this->assign(*other);
        else
            reset();
        return *this;
    }

    //! Move assignment operator.
    //!
    //! @param[in] other    The optional value containing the new value (or lack of value) to
    //!                     assign to this object.  The contained value may be of any type that
    //!                     can be implicitly converted to this object's contained type.  The
    //!                     @p other object will be in a valid but undefined state upon return.
    //! @returns A reference to this object.
    template <class U,
              typename std::enable_if_t<
                  std::conjunction<AllowUnwrappingAssignment<U>, std::is_constructible<T, U>, std::is_assignable<T&, U>>::value,
                  int> = 0>
    optional& operator=(optional<U>&& other)
    {
        if (other)
            this->assign(std::move(*other));
        else
            reset();
        return *this;
    }

    //! Access operator.  This operation is considered undefined behavior if no value is currently
    //! contained in this object.
    //!
    //! @returns The address of the contained value.
    constexpr const T* operator->() const
    {
        return std::addressof(this->val());
    }
    //! Access operator.  This operation is considered undefined behavior if no value is currently
    //! contained in this object.
    //!
    //! @returns The address of the contained value.
    constexpr T* operator->()
    {
        return std::addressof(this->val());
    }

    //! Dereference operator for the contained value.  This operation is considered undefined
    //! behavior if no value is currently contained in this object.
    //!
    //! @returns A const reference to the contained value.
    constexpr const T& operator*() const&
    {
        return this->val();
    }

    //! Dereference operator for the contained value.  This operation is considered undefined
    //! behavior if no value is currently contained in this object.
    //!
    //! @returns A reference to the contained value.
    constexpr T& operator*() &
    {
        return this->val();
    }

    //! Dereference-and-move operator for the contained value.  This operation is considered
    //! undefined behavior if no value is currently contained in this object.
    //!
    //! @returns A const reference to the contained value.
    constexpr const T&& operator*() const&&
    {
        return std::move(this->val());
    }

    //! Dereference-and-move operator for the contained value.  This operation is considered
    //! undefined behavior if no value is currently contained in this object.
    //!
    //! @returns A reference to the contained value.
    constexpr T&& operator*() &&
    {
        return std::move(this->val());
    }

    //! Value test operator.  Checks if this object currently contains a value.
    //!
    //! @returns `true` if a value is currently contained in this object and `false` otherwise.
    constexpr explicit operator bool() const noexcept
    {
        return this->hasValue;
    }
    //! Value test operator.  Checks if this object currently contains a value.
    //!
    //! @returns `true` if a value is currently contained in this object and `false` otherwise.
    constexpr bool has_value() const noexcept
    {
        return this->hasValue;
    }

    //! Value retrieval accessor.  This will throw `bad_optional_access` if no value is contained
    //! in this object (or terminate if exceptions are disabled).
    //!
    //! @returns A reference to the value contained in this object.
    constexpr const T& value() const&
    {
        if (!this->hasValue)
            onBadAccess();
        return this->val();
    }

    //! Value retrieval accessor.  This will throw `bad_optional_access` if no value is contained
    //! in this object (or terminate if exceptions are disabled).
    //!
    //! @returns A reference to the value contained in this object.
    constexpr T& value() &
    {
        if (!this->hasValue)
            onBadAccess();
        return this->val();
    }

    //! Value move accessor.  This will throw `bad_optional_access` if no value is contained
    //! in this object (or terminate if exceptions are disabled).  This object will be left
    //! in a valid but undefined state.
    //!
    //! @returns An rvalue-reference to the contained value.
    constexpr const T&& value() const&&
    {
        if (!this->hasValue)
            onBadAccess();
        return std::move(this->val());
    }

    //! Value move accessor.  This will throw `bad_optional_access` if no value is contained
    //! in this object (or terminate if exceptions are disabled).  This object will be left
    //! in a valid but undefined state.
    //!
    //! @returns An rvalue-reference to the contained value.
    constexpr T&& value() &&
    {
        if (!this->hasValue)
            onBadAccess();
        return std::move(this->val());
    }

    //! Returns the contained value if `*this` has a value, otherwise returns `default_value`.
    //!
    //! @param[in] default_value    The value to use in case `*this` is empty.
    //!
    //! @returns The current value if `*this` has a value, or @p default_value otherwise.
    template <class U>
    constexpr typename std::remove_cv_t<T> value_or(U&& default_value) const&
    {
        static_assert(
            std::is_convertible<const T&, typename std::remove_cv_t<T>>::value,
            "The const overload of optional<T>::value_or() requires const T& to be convertible to std::remove_cv_t<T>");
        static_assert(std::is_convertible<U, T>::value, "optional<T>::value_or() requires U to be convertible to T");

        if (this->hasValue)
            return this->val();

        return static_cast<typename std::remove_cv_t<T>>(std::forward<U>(default_value));
    }

    //! Returns the contained value if `*this` has a value, otherwise returns `default_value`.
    //!
    //! @param[in] default_value    The value to use in case `*this` is empty.
    //!
    //! @returns The current value if `*this` has a value, or @p default_value otherwise.
    template <class U>
    constexpr typename std::remove_cv_t<T> value_or(U&& default_value) &&
    {
        static_assert(
            std::is_convertible<T, typename std::remove_cv_t<T>>::value,
            "The rvalue overload of optional<T>::value_or() requires T to be convertible to std::remove_cv_t<T>");
        static_assert(std::is_convertible<U, T>::value, "optional<T>::value_or() requires U to be convertible to T");

        if (this->hasValue)
            return this->val();

        return static_cast<typename std::remove_cv_t<T>>(std::forward<U>(default_value));
    }

    //! Swaps the values or lack of value between this object and another object.
    //!
    //! @param[in] other    The object to swap the state with this object.  If @p other did not
    //!                     contain a value, this object will not contain a value upon return.
    //!                     If this object does not contain a value, @p other will not contain
    //!                     a value upon return.  If both contain a value, those values will be
    //!                     swapped upon return.  The contained type must be move constructible
    //!                     and swappable.
    void swap(optional& other) noexcept(std::is_nothrow_move_constructible<T>::value&& std::is_nothrow_swappable<T>::value)
    {
        static_assert(std::is_move_constructible<T>::value, "T must be move constructible");
        static_assert(std::is_swappable<T>::value, "T must be swappable");

        const bool engaged = this->hasValue;
        if (engaged == other.hasValue)
        {
            if (engaged)
            {
                using std::swap; // Enable ADL
                swap(**this, *other);
            }
        }
        else
        {
            optional& source = engaged ? *this : other;
            optional& target = engaged ? other : *this;
            target.construct(std::move(*source));
            source.reset();
        }
    }

    using BaseClass::reset;

    //! Piecewise constructs a new value in this object.  Any previous contained value will be
    //! destructed and discarded.
    //!
    //! @param[in] args     Argument list needed to construct the new object.
    //! @returns A reference to this object.
    template <class... Args>
    T& emplace(Args&&... args)
    {
        reset();
        return this->construct(std::forward<Args>(args)...);
    }
    //! Piecewise constructs a new value in this object.  Any previous contained value will be
    //! destructed and discarded.
    //!
    //! @param[in] ilist    Initializer list used to construct the new value.
    //! @param[in] args     Argument list needed to satisfy the initializer list @p ilist.
    //! @returns A reference to this object.
    template <class U,
              class... Args,
              typename std::enable_if_t<std::is_constructible<T, std::initializer_list<U>&, Args...>::value, int> = 0>
    T& emplace(std::initializer_list<U> ilist, Args&&... args)
    {
        reset();
        return this->construct(ilist, std::forward<Args>(args)...);
    }
};

#ifndef DOXYGEN_BUILD
//! Deduction guides.
template <class T>
optional(T) -> optional<T>;

template <class T, class U>
constexpr bool operator==(const optional<T>& lhs, const optional<U>& rhs)
{
    const bool lhv = lhs.has_value();
    return lhv == rhs.has_value() && (!lhv || *lhs == *rhs);
}
template <class T, class U>
constexpr bool operator!=(const optional<T>& lhs, const optional<U>& rhs)
{
    const bool lhv = lhs.has_value();
    return lhv != rhs.has_value() || (lhv && *lhs != *rhs);
}
template <class T, class U>
constexpr bool operator<(const optional<T>& lhs, const optional<U>& rhs)
{
    return rhs.has_value() && (!lhs.has_value() || *lhs < *rhs);
}
template <class T, class U>
constexpr bool operator<=(const optional<T>& lhs, const optional<U>& rhs)
{
    return !lhs.has_value() || (rhs.has_value() && *lhs <= *rhs);
}
template <class T, class U>
constexpr bool operator>(const optional<T>& lhs, const optional<U>& rhs)
{
    return lhs.has_value() && (!rhs.has_value() || *lhs > *rhs);
}
template <class T, class U>
constexpr bool operator>=(const optional<T>& lhs, const optional<U>& rhs)
{
    return !rhs.has_value() || (lhs.has_value() && *lhs >= *rhs);
}

template <class T>
constexpr bool operator==(const optional<T>& opt, nullopt_t) noexcept
{
    return !opt.has_value();
}
template <class T>
constexpr bool operator==(nullopt_t, const optional<T>& opt) noexcept
{
    return !opt.has_value();
}
template <class T>
constexpr bool operator!=(const optional<T>& opt, nullopt_t) noexcept
{
    return opt.has_value();
}
template <class T>
constexpr bool operator!=(nullopt_t, const optional<T>& opt) noexcept
{
    return opt.has_value();
}
template <class T>
constexpr bool operator<(const optional<T>& opt, nullopt_t) noexcept
{
    CARB_UNUSED(opt);
    return false;
}
template <class T>
constexpr bool operator<(nullopt_t, const optional<T>& opt) noexcept
{
    return opt.has_value();
}
template <class T>
constexpr bool operator<=(const optional<T>& opt, nullopt_t) noexcept
{
    return !opt.has_value();
}
template <class T>
constexpr bool operator<=(nullopt_t, const optional<T>& opt) noexcept
{
    CARB_UNUSED(opt);
    return true;
}
template <class T>
constexpr bool operator>(const optional<T>& opt, nullopt_t) noexcept
{
    return opt.has_value();
}
template <class T>
constexpr bool operator>(nullopt_t, const optional<T>& opt) noexcept
{
    CARB_UNUSED(opt);
    return false;
}
template <class T>
constexpr bool operator>=(const optional<T>& opt, nullopt_t) noexcept
{
    CARB_UNUSED(opt);
    return true;
}
template <class T>
constexpr bool operator>=(nullopt_t, const optional<T>& opt) noexcept
{
    return !opt.has_value();
}

template <class T, class U, detail::EnableIfComparableWithEqual<T, U> = 0>
constexpr bool operator==(const optional<T>& opt, const U& value)
{
    return opt ? *opt == value : false;
}
template <class T, class U, detail::EnableIfComparableWithEqual<T, U> = 0>
constexpr bool operator==(const T& value, const optional<U>& opt)
{
    return opt ? *opt == value : false;
}
template <class T, class U, detail::EnableIfComparableWithNotEqual<T, U> = 0>
constexpr bool operator!=(const optional<T>& opt, const U& value)
{
    return opt ? *opt != value : true;
}
template <class T, class U, detail::EnableIfComparableWithNotEqual<T, U> = 0>
constexpr bool operator!=(const T& value, const optional<U>& opt)
{
    return opt ? *opt != value : true;
}
template <class T, class U, detail::EnableIfComparableWithLess<T, U> = 0>
constexpr bool operator<(const optional<T>& opt, const U& value)
{
    return opt ? *opt < value : true;
}
template <class T, class U, detail::EnableIfComparableWithLess<T, U> = 0>
constexpr bool operator<(const T& value, const optional<U>& opt)
{
    return opt ? value < *opt : false;
}
template <class T, class U, detail::EnableIfComparableWithLessEqual<T, U> = 0>
constexpr bool operator<=(const optional<T>& opt, const U& value)
{
    return opt ? *opt <= value : true;
}
template <class T, class U, detail::EnableIfComparableWithLessEqual<T, U> = 0>
constexpr bool operator<=(const T& value, const optional<U>& opt)
{
    return opt ? value <= *opt : false;
}
template <class T, class U, detail::EnableIfComparableWithGreater<T, U> = 0>
constexpr bool operator>(const optional<T>& opt, const U& value)
{
    return opt ? *opt > value : false;
}
template <class T, class U, detail::EnableIfComparableWithGreater<T, U> = 0>
constexpr bool operator>(const T& value, const optional<U>& opt)
{
    return opt ? value > *opt : true;
}
template <class T, class U, detail::EnableIfComparableWithGreaterEqual<T, U> = 0>
constexpr bool operator>=(const optional<T>& opt, const U& value)
{
    return opt ? *opt >= value : false;
}
template <class T, class U, detail::EnableIfComparableWithGreaterEqual<T, U> = 0>
constexpr bool operator>=(const T& value, const optional<U>& opt)
{
    return opt ? value >= *opt : true;
}

template <class T, typename std::enable_if_t<std::is_move_constructible<T>::value && std::is_swappable<T>::value, int> = 0>
void swap(optional<T>& lhs, optional<T>& rhs) noexcept(noexcept(lhs.swap(rhs)))
{
    lhs.swap(rhs);
}

template <class T>
constexpr optional<typename std::decay_t<T>> make_optional(T&& value)
{
    return optional<typename std::decay_t<T>>{ std::forward<T>(value) };
}
template <class T, class... Args>
constexpr optional<T> make_optional(Args&&... args)
{
    return optional<T>{ std::in_place, std::forward<Args>(args)... };
}
template <class T, class U, class... Args>
constexpr optional<T> make_optional(std::initializer_list<U> il, Args&&... args)
{
    return optional<T>{ std::in_place, il, std::forward<Args>(args)... };
}
#endif

} // namespace cpp
} // namespace carb
