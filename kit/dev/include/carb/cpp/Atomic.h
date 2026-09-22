// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// Implements the wait/notify functions from C++20-standard atomics for types that are 1, 2, 4 or 8 bytes. If this
// feature is not desired, or the type you're trying to atomic-wrap isn't supported, use std::atomic instead.
// See the following:
// https://en.cppreference.com/w/cpp/atomic/atomic/wait
// https://en.cppreference.com/w/cpp/atomic/atomic/notify_one
// https://en.cppreference.com/w/cpp/atomic/atomic/notify_all

//! \file
//! \brief C++14-compatible implementation of select functionality from C++ `<atomic>` library.
#pragma once

#include "../thread/Futex.h"
#include "../thread/Util.h"
#include "detail/AtomicOps.h"

#include <atomic>
#include <chrono>
#include <type_traits>

namespace carb
{
namespace cpp
{

template <class T>
class atomic;

namespace detail
{

constexpr inline std::memory_order drop_release(std::memory_order order) noexcept
{
    return (order == std::memory_order_release) ?
               std::memory_order_relaxed :
               ((order == std::memory_order_acq_rel || order == std::memory_order_seq_cst) ? std::memory_order_acquire :
                                                                                             order);
}

// C++20 adds fetch_add/fetch_sub and operator support for floating point types
template <class T>
class atomic_float_facade : public std::atomic<T>
{
    using Base = std::atomic<T>;
    static_assert(std::is_floating_point_v<T>);

public:
    atomic_float_facade() noexcept = default;
    constexpr atomic_float_facade(T desired) noexcept : Base(desired)
    {
    }
    atomic_float_facade(const atomic_float_facade&) = delete;

    using Base::operator=;

    T fetch_add(T arg, std::memory_order order = std::memory_order_seq_cst) noexcept
    {
        T temp = this->load(std::memory_order_relaxed);
        while (!this->compare_exchange_strong(temp, temp + arg, order, std::memory_order_relaxed))
        {
        }

        return temp;
    }
    T fetch_add(T arg, std::memory_order order = std::memory_order_seq_cst) volatile noexcept
    {
        T temp = this->load(std::memory_order_relaxed);
        while (!this->compare_exchange_strong(temp, temp + arg, order, std::memory_order_relaxed))
        {
        }

        return temp;
    }
    T fetch_sub(T arg, std::memory_order order = std::memory_order_seq_cst) noexcept
    {
        T temp = this->load(std::memory_order_relaxed);
        while (!this->compare_exchange_strong(temp, temp - arg, order, std::memory_order_relaxed))
        {
        }

        return temp;
    }
    T fetch_sub(T arg, std::memory_order order = std::memory_order_seq_cst) volatile noexcept
    {
        T temp = this->load(std::memory_order_relaxed);
        while (!this->compare_exchange_strong(temp, temp - arg, order, std::memory_order_relaxed))
        {
        }

        return temp;
    }

    T operator+=(T arg) noexcept
    {
        return this->fetch_add(arg) + arg;
    }
    T operator+=(T arg) volatile noexcept
    {
        return this->fetch_add(arg) + arg;
    }
    T operator-=(T arg) noexcept
    {
        return this->fetch_sub(arg) - arg;
    }
    T operator-=(T arg) volatile noexcept
    {
        return this->fetch_sub(arg) - arg;
    }
};

// C++26 adds fetch_min and fetch_max to integral and pointer types
// See https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p0493r5.pdf
// And the C++26 draft standard section N4981
template <class T>
class atomic_add_minmax : public std::atomic<T>
{
    using Base = std::atomic<T>;
    static_assert((std::is_integral_v<T> && !std::is_same_v<bool, std::remove_cv_t<T>>) || std::is_pointer_v<T>);

public:
    atomic_add_minmax() noexcept = default;
    constexpr atomic_add_minmax(T desired) noexcept : Base(desired)
    {
    }
    atomic_add_minmax(const atomic_add_minmax&) = delete;
    using Base::operator=;

    T fetch_max(T arg, std::memory_order order = std::memory_order_seq_cst) noexcept
    {
        auto const lo = drop_release(order);
        // if `order` has release semantics, do fetch_add to ensure a read-modify-write operation (see paper p0493r5)
        auto t = (lo != order) ? this->fetch_add(0, order) : this->load(lo);
        while (carb_max(arg, t) != t)
            if (this->compare_exchange_weak(t, arg, order, lo))
                return t;
        return t;
    }
    T fetch_max(T arg, std::memory_order order = std::memory_order_seq_cst) volatile noexcept
    {
        auto const lo = drop_release(order);
        // if `order` has release semantics, do fetch_add to ensure a read-modify-write operation (see paper p0493r5)
        auto t = (lo != order) ? this->fetch_add(0, order) : this->load(lo);
        while (carb_max(arg, t) != t)
            if (this->compare_exchange_weak(t, arg, order, lo))
                return t;
        return t;
    }
    T fetch_min(T arg, std::memory_order order = std::memory_order_seq_cst) noexcept
    {
        auto const lo = drop_release(order);
        // if `order` has release semantics, do fetch_add to ensure a read-modify-write operation (see paper p0493r5)
        auto t = (lo != order) ? this->fetch_add(0, order) : this->load(lo);
        while (carb_min(arg, t) != t)
            if (this->compare_exchange_weak(t, arg, order, lo))
                return t;
        return t;
    }
    T fetch_min(T arg, std::memory_order order = std::memory_order_seq_cst) volatile noexcept
    {
        auto const lo = drop_release(order);
        // if `order` has release semantics, do fetch_add to ensure a read-modify-write operation (see paper p0493r5)
        auto t = (lo != order) ? this->fetch_add(0, order) : this->load(lo);
        while (carb_min(arg, t) != t)
            if (this->compare_exchange_weak(t, arg, order, lo))
                return t;
        return t;
    }
};

template <class T, bool IsConst = std::is_const_v<T>>
class atomic_ref_base // IsConst = true
{
protected:
    using RawAtomicType = ::carb::cpp::atomic<std::remove_cv_t<T>>;
    using PossiblyConstType = std::conditional_t<std::is_const_v<T>, std::add_const_t<RawAtomicType>, RawAtomicType>;
    using AtomicType =
        std::conditional_t<std::is_volatile_v<T>, std::add_volatile_t<PossiblyConstType>, PossiblyConstType>;
    AtomicType& m_ref;

public:
    using value_type = std::remove_cv_t<T>;

    static constexpr bool is_always_lock_free = AtomicType::is_always_lock_free;

    static constexpr std::size_t required_alignment = alignof(T);

    explicit atomic_ref_base(T& obj) : m_ref(reinterpret_cast<AtomicType&>(const_cast<std::remove_cv_t<T>&>(obj)))
    {
    }
    atomic_ref_base(const atomic_ref_base& ref) noexcept : m_ref(ref.m_ref)
    {
    }

    atomic_ref_base& operator=(const atomic_ref_base&) = delete;

    bool is_lock_free() const noexcept
    {
        return m_ref.is_lock_free();
    }

    value_type load(std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return m_ref.load(order);
    }

    operator value_type() const noexcept
    {
        return load();
    }

    void wait(value_type old, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        m_ref.wait(old, order);
    }

    template <class Rep, class Period>
    bool wait_for(value_type old,
                  std::chrono::duration<Rep, Period> duration,
                  std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return m_ref.wait_for(old, duration, order);
    }

    template <class Clock, class Duration>
    bool wait_until(value_type old,
                    std::chrono::time_point<Clock, Duration> time_point,
                    std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return m_ref.wait_until(old, time_point, order);
    }
};

template <class T>
class atomic_ref_base<T, false> : public atomic_ref_base<T, true> // IsConst=false specialization, inherits from const
{
    using Base = atomic_ref_base<T, true>;

public:
    using value_type = typename Base::value_type;

    explicit atomic_ref_base(T& obj) : Base(obj)
    {
    }
    atomic_ref_base(const atomic_ref_base& ref) noexcept : Base(ref)
    {
    }

    using Base::operator=;

    value_type operator=(value_type desired) const noexcept
    {
        this->m_ref.store(desired);
        return desired;
    }

    void store(value_type desired, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        this->m_ref.store(desired, order);
    }

    value_type exchange(value_type desired, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.exchange(desired, order);
    }

    bool compare_exchange_weak(value_type& expected,
                               value_type desired,
                               std::memory_order success,
                               std::memory_order failure) const noexcept
    {
        return this->m_ref.compare_exchange_weak(expected, desired, success, failure);
    }
    bool compare_exchange_weak(value_type& expected,
                               value_type desired,
                               std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.compare_exchange_weak(expected, desired, order);
    }
    bool compare_exchange_strong(value_type& expected,
                                 value_type desired,
                                 std::memory_order success,
                                 std::memory_order failure) const noexcept
    {
        return this->m_ref.compare_exchange_strong(expected, desired, success, failure);
    }
    bool compare_exchange_strong(value_type& expected,
                                 value_type desired,
                                 std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.compare_exchange_strong(expected, desired, order);
    }

    void notify_one() const noexcept
    {
        this->m_ref.notify_one();
    }
    void notify_all() const noexcept
    {
        this->m_ref.notify_all();
    }
};

template <class T, class BaseClass, bool IsConst = std::is_const_v<T>>
class atomic_ref_add_minmax : public BaseClass // IsConst = true
{
    using Base = BaseClass;
    static_assert(std::is_pointer_v<T> || (std::is_integral_v<T> && !std::is_same_v<bool, T>));

public:
    using value_type = typename Base::value_type;

    explicit atomic_ref_add_minmax(T& ref) : Base(ref)
    {
    }
    atomic_ref_add_minmax(const atomic_ref_add_minmax& other) noexcept : Base(other)
    {
    }

    using Base::operator=;
};

template <class T, class NextBase>
class atomic_ref_add_minmax<T, NextBase, false> : public atomic_ref_add_minmax<T, NextBase, true> // IsConst = false
{
    using Base = atomic_ref_add_minmax<T, NextBase, true>;
    static_assert(std::is_pointer_v<T> || (std::is_integral_v<T> && !std::is_same_v<bool, T>));

public:
    using value_type = typename Base::value_type;

    explicit atomic_ref_add_minmax(T& ref) : Base(ref)
    {
    }
    atomic_ref_add_minmax(const atomic_ref_add_minmax& other) noexcept : Base(other)
    {
    }

    using Base::operator=;

    value_type fetch_max(value_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        auto const lo = drop_release(order);
        // if `order` has release semantics, do fetch_add to ensure a read-modify-write operation (see paper p0493r5)
        auto t = (lo != order) ? this->fetch_add(0, order) : this->load(lo);
        while (carb_max(arg, t) != t)
            if (this->compare_exchange_weak(t, arg, order, lo))
                return t;
        return t;
    }
    value_type fetch_min(value_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        auto const lo = drop_release(order);
        // if `order` has release semantics, do fetch_add to ensure a read-modify-write operation (see paper p0493r5)
        auto t = (lo != order) ? this->fetch_add(0, order) : this->load(lo);
        while (carb_min(arg, t) != t)
            if (this->compare_exchange_weak(t, arg, order, lo))
                return t;
        return t;
    }
};

template <class T, bool IsConst = std::is_const_v<T>>
class atomic_ref_pointer_facade : public atomic_ref_base<T> // IsConst = true
{
    using Base = atomic_ref_base<T>;
    static_assert(std::is_pointer_v<T>);

public:
    using value_type = typename Base::value_type;
    using difference_type = std::ptrdiff_t;

    explicit atomic_ref_pointer_facade(T& ref) : Base(ref)
    {
    }
    atomic_ref_pointer_facade(const atomic_ref_pointer_facade& other) noexcept : Base(other)
    {
    }

    using Base::operator=;
};


template <class T>
class atomic_ref_pointer_facade<T, false> : public atomic_ref_pointer_facade<T, true> // IsConst = false
{
    using Base = atomic_ref_pointer_facade<T, true>;
    static_assert(std::is_pointer_v<T>);

public:
    using value_type = typename Base::value_type;
    using difference_type = typename Base::difference_type;

    explicit atomic_ref_pointer_facade(T& ref) : Base(ref)
    {
    }
    atomic_ref_pointer_facade(const atomic_ref_pointer_facade& other) noexcept : Base(other)
    {
    }

    using Base::operator=;

    value_type fetch_add(difference_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.fetch_add(arg, order);
    }
    value_type fetch_sub(difference_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.fetch_sub(arg, order);
    }
    value_type operator++() const noexcept
    {
        return this->m_ref.fetch_add(1) + 1;
    }
    value_type operator++(int) const noexcept
    {
        return this->m_ref.fetch_add(1);
    }
    value_type operator--() const noexcept
    {
        return this->m_ref.fetch_sub(1) - 1;
    }
    value_type operator--(int) const noexcept
    {
        return this->m_ref.fetch_sub(1);
    }
    value_type operator+=(difference_type arg) const noexcept
    {
        return this->m_ref.fetch_add(arg) + arg;
    }
    value_type operator-=(difference_type arg) const noexcept
    {
        return this->m_ref.fetch_sub(arg) - arg;
    }
};

template <class T, bool IsConst = std::is_const_v<T>>
class atomic_ref_numeric_facade : public atomic_ref_base<T> // IsConst = true
{
    using Base = atomic_ref_base<T>;
    static_assert(std::is_integral_v<T> || std::is_floating_point_v<T>);

public:
    using value_type = typename Base::value_type;
    using difference_type = typename Base::value_type;

    explicit atomic_ref_numeric_facade(T& ref) : Base(ref)
    {
    }
    atomic_ref_numeric_facade(const atomic_ref_numeric_facade& other) noexcept : Base(other)
    {
    }

    using Base::operator=;
};

template <class T>
class atomic_ref_numeric_facade<T, false> : public atomic_ref_numeric_facade<T, true> // IsConst = false
{
    using Base = atomic_ref_numeric_facade<T, true>;
    static_assert(std::is_integral_v<T> || std::is_floating_point_v<T>);

public:
    using value_type = typename Base::value_type;
    using difference_type = typename Base::difference_type;

    explicit atomic_ref_numeric_facade(T& ref) : Base(ref)
    {
    }
    atomic_ref_numeric_facade(const atomic_ref_numeric_facade& other) noexcept : Base(other)
    {
    }

    using Base::operator=;

    value_type fetch_add(difference_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.fetch_add(arg, order);
    }
    value_type fetch_sub(difference_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.fetch_sub(arg, order);
    }
    value_type operator+=(difference_type arg) const noexcept
    {
        return this->m_ref.fetch_add(arg) + arg;
    }
    value_type operator-=(difference_type arg) const noexcept
    {
        return this->m_ref.fetch_sub(arg) - arg;
    }
};

template <class T, bool IsConst = std::is_const_v<T>>
class atomic_ref_integer_facade : public atomic_ref_numeric_facade<T> // IsConst = true
{
    using Base = atomic_ref_numeric_facade<T>;
    static_assert(std::is_integral_v<T> && !std::is_same_v<T, bool>);

public:
    using value_type = typename Base::value_type;
    using difference_type = typename Base::difference_type;

    explicit atomic_ref_integer_facade(T& ref) : Base(ref)
    {
    }
    atomic_ref_integer_facade(const atomic_ref_integer_facade& other) noexcept : Base(other)
    {
    }

    using Base::operator=;
};

template <class T>
class atomic_ref_integer_facade<T, false> : public atomic_ref_integer_facade<T, true> // IsConst = false
{
    using Base = atomic_ref_integer_facade<T, true>;
    static_assert(std::is_integral_v<T> && !std::is_same_v<T, bool>);

public:
    using value_type = typename Base::value_type;
    using difference_type = typename Base::difference_type;

    explicit atomic_ref_integer_facade(T& ref) : Base(ref)
    {
    }
    atomic_ref_integer_facade(const atomic_ref_integer_facade& other) noexcept : Base(other)
    {
    }

    using Base::operator=;

    value_type fetch_and(value_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.fetch_and(arg, order);
    }
    value_type fetch_or(value_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.fetch_or(arg, order);
    }
    value_type fetch_xor(value_type arg, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return this->m_ref.fetch_xor(arg, order);
    }

    value_type operator++() const noexcept
    {
        return this->m_ref.fetch_add(T(1)) + T(1);
    }
    value_type operator++(int) const noexcept
    {
        return this->m_ref.fetch_add(T(1));
    }
    value_type operator--() const noexcept
    {
        return this->m_ref.fetch_sub(T(1)) - T(1);
    }
    value_type operator--(int) const noexcept
    {
        return this->m_ref.fetch_sub(T(1));
    }

    value_type operator&=(value_type arg) const noexcept
    {
        return this->m_ref.fetch_and(arg) & arg;
    }
    value_type operator|=(value_type arg) const noexcept
    {
        return this->m_ref.fetch_or(arg) | arg;
    }
    value_type operator^=(value_type arg) const noexcept
    {
        return this->m_ref.fetch_xor(arg) ^ arg;
    }
};

// non-bool integral or pointer types gain fetch_min and fetch_max through atomic_ref_add_minmax decorator type
template <class T>
using SelectAtomicRefBase = std::conditional_t<
    std::is_pointer_v<T>,
    atomic_ref_add_minmax<T, atomic_ref_pointer_facade<T>>,
    std::conditional_t<std::is_integral_v<T> && !std::is_same_v<std::remove_cv_t<T>, bool>,
                       atomic_ref_add_minmax<T, atomic_ref_integer_facade<T>>,
                       std::conditional_t<std::is_floating_point_v<T>, atomic_ref_numeric_facade<T>, atomic_ref_base<T>>>>;

// non-bool integral or pointer types gain fetch_min and fetch_max through atomic_add_minmax base type
template <class T>
using SelectAtomicBase = std::conditional_t<
    std::is_floating_point_v<T>,
    atomic_float_facade<T>,
    std::conditional_t<std::is_pointer_v<T> || (std::is_integral_v<T> && !std::is_same_v<std::remove_cv_t<T>, bool>),
                       atomic_add_minmax<T>,
                       std::atomic<T>>>;

#define CARB_ATOMIC_FLAG_INIT                                                                                          \
    {                                                                                                                  \
    }
} // namespace detail

template <class T>
class atomic : public detail::SelectAtomicBase<T>
{
    using Base = detail::SelectAtomicBase<T>;

public:
    using value_type = T;

    atomic() noexcept = default;
    constexpr atomic(T desired) noexcept : Base(desired)
    {
    }

    static constexpr bool is_always_lock_free = sizeof(T) == 1 || sizeof(T) == 2 || sizeof(T) == 4 || sizeof(T) == 8;

    using Base::operator=;
    using Base::operator T;

    CARB_PREVENT_COPY_AND_MOVE(atomic);

    // See https://en.cppreference.com/w/cpp/atomic/atomic/wait
    void wait(T old, std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        static_assert(is_always_lock_free, "Only supported for always-lock-free types");
        using I = thread::detail::to_integral_t<T>;
        for (;;)
        {
            if (carb::this_thread::spinTryWait([&] {
                    return thread::detail::reinterpret_as<I>(this->load(order)) != thread::detail::reinterpret_as<I>(old);
                }))
            {
                break;
            }
            thread::futex::wait(*this, old);
        }
    }
    void wait(T old, std::memory_order order = std::memory_order_seq_cst) const volatile noexcept
    {
        static_assert(is_always_lock_free, "Only supported for always-lock-free types");
        using I = thread::detail::to_integral_t<T>;
        for (;;)
        {
            if (carb::this_thread::spinTryWait([&] {
                    return thread::detail::reinterpret_as<I>(this->load(order)) != thread::detail::reinterpret_as<I>(old);
                }))
            {
                break;
            }
            thread::futex::wait(const_cast<atomic<T>&>(*this), old);
        }
    }
    // wait_for and wait_until are non-standard
    template <class Rep, class Period>
    bool wait_for(T old,
                  std::chrono::duration<Rep, Period> duration,
                  std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        // Since futex can spuriously wake up, calculate the end time so that we can handle the spurious wakeups without
        // shortening our wait time potentially significantly.
        return wait_until(old, cpp::detail::absTime<std::chrono::steady_clock>(duration), order);
    }
    template <class Rep, class Period>
    bool wait_for(T old,
                  std::chrono::duration<Rep, Period> duration,
                  std::memory_order order = std::memory_order_seq_cst) const volatile noexcept
    {
        // Since futex can spuriously wake up, calculate the end time so that we can handle the spurious wakeups without
        // shortening our wait time potentially significantly.
        return wait_until(old, cpp::detail::absTime<std::chrono::steady_clock>(duration), order);
    }
    template <class Clock, class Duration>
    bool wait_until(T old,
                    std::chrono::time_point<Clock, Duration> time_point,
                    std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        static_assert(is_always_lock_free, "Only supported for always-lock-free types");
        using I = thread::detail::to_integral_t<T>;
        for (;;)
        {
            if (carb::this_thread::spinTryWait([&] {
                    return thread::detail::reinterpret_as<I>(this->load(order)) != thread::detail::reinterpret_as<I>(old);
                }))
            {
                return true;
            }
            if (!thread::futex::wait_until(*this, old, time_point))
            {
                return false;
            }
        }
    }
    template <class Clock, class Duration>
    bool wait_until(T old,
                    std::chrono::time_point<Clock, Duration> time_point,
                    std::memory_order order = std::memory_order_seq_cst) const volatile noexcept
    {
        static_assert(is_always_lock_free, "Only supported for always-lock-free types");
        using I = thread::detail::to_integral_t<T>;
        for (;;)
        {
            if (carb::this_thread::spinTryWait([&] {
                    return thread::detail::reinterpret_as<I>(this->load(order)) != thread::detail::reinterpret_as<I>(old);
                }))
            {
                return true;
            }
            if (!thread::futex::wait_until(const_cast<atomic<T>&>(*this), old, time_point))
            {
                return false;
            }
        }
    }
    // See https://en.cppreference.com/w/cpp/atomic/atomic/notify_one
    void notify_one() noexcept
    {
        thread::futex::notify_one(*this);
    }
    void notify_one() volatile noexcept
    {
        thread::futex::notify_one(const_cast<atomic<T>&>(*this));
    }
    // See https://en.cppreference.com/w/cpp/atomic/atomic/notify_all
    void notify_all() noexcept
    {
        thread::futex::notify_all(*this);
    }
    void notify_all() volatile noexcept
    {
        thread::futex::notify_all(const_cast<atomic<T>&>(*this));
    }
};

template <class T>
class atomic_ref : public detail::SelectAtomicRefBase<T>
{
    using Base = detail::SelectAtomicRefBase<T>;

public:
    explicit atomic_ref(T& ref) : Base(ref)
    {
    }
    atomic_ref(const atomic_ref& other) noexcept : Base(other)
    {
    }
    using Base::operator=;
};

// Freestanding atomic_wait/atomic_notify implementations introduced in C++20
// See https://en.cppreference.com/w/cpp/atomic/atomic_wait
template <class T>
inline void atomic_wait(const atomic<T>* object, typename atomic<T>::value_type old) noexcept
{
    object->wait(old);
}
template <class T>
inline void atomic_wait_explicit(const atomic<T>* object, typename atomic<T>::value_type old, std::memory_order order) noexcept
{
    object->wait(old, order);
}
// See https://en.cppreference.com/w/cpp/atomic/atomic_notify_one
template <class T>
inline void atomic_notify_one(atomic<T>* object)
{
    object->notify_one();
}
// See https://en.cppreference.com/w/cpp/atomic/atomic_notify_all
template <class T>
inline void atomic_notify_all(atomic<T>* object)
{
    object->notify_all();
}

// freestanding fetch_min/fetch_max implementations introduced in C++26
// See https://en.cppreference.com/w/cpp/atomic/atomic_fetch_min
template <class T>
T atomic_fetch_min(volatile atomic<T>* obj, typename atomic<T>::value_type arg) noexcept
{
    return obj->fetch_min(arg);
}
template <class T>
T atomic_fetch_min(atomic<T>* obj, typename atomic<T>::value_type arg) noexcept
{
    return obj->fetch_min(arg);
}
template <class T>
T atomic_fetch_min_explicit(volatile atomic<T>* obj, typename atomic<T>::value_type arg, std::memory_order order) noexcept
{
    return obj->fetch_min(arg, order);
}
template <class T>
T atomic_fetch_min_explicit(atomic<T>* obj, typename atomic<T>::value_type arg, std::memory_order order) noexcept
{
    return obj->fetch_min(arg, order);
}
template <class T>
// See https://en.cppreference.com/w/cpp/atomic/atomic_fetch_max
T atomic_fetch_max(volatile atomic<T>* obj, typename atomic<T>::value_type arg) noexcept
{
    return obj->fetch_max(arg);
}
template <class T>
T atomic_fetch_max(atomic<T>* obj, typename atomic<T>::value_type arg) noexcept
{
    return obj->fetch_max(arg);
}
template <class T>
T atomic_fetch_max_explicit(volatile atomic<T>* obj, typename atomic<T>::value_type arg, std::memory_order order) noexcept
{
    return obj->fetch_max(arg, order);
}
template <class T>
T atomic_fetch_max_explicit(atomic<T>* obj, typename atomic<T>::value_type arg, std::memory_order order) noexcept
{
    return obj->fetch_max(arg, order);
}

struct atomic_flag
{
    using value_type = int32_t;

    CARB_CPP20_CONSTEXPR atomic_flag() noexcept : m_flag{}
    {
    }

    bool test_and_set(const std::memory_order order = std::memory_order_seq_cst) noexcept
    {
        return detail::AtomicOps<int32_t>::test_bit_and_set(m_flag, 0, order);
    }
    bool test_and_set(const std::memory_order order = std::memory_order_seq_cst) volatile noexcept
    {
        return const_cast<atomic_flag*>(this)->test_and_set(order);
    }

    void clear(std::memory_order order = std::memory_order_seq_cst) noexcept
    {
        m_flag.store(0, order);
    }
    void clear(std::memory_order order = std::memory_order_seq_cst) volatile noexcept
    {
        const_cast<atomic_flag*>(this)->clear(order);
    }

    // C++20 features
    [[nodiscard]] bool test(const std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return m_flag.load(order) != 0;
    }
    [[nodiscard]] bool test(const std::memory_order order = std::memory_order_seq_cst) const volatile noexcept
    {
        return const_cast<const atomic_flag*>(this)->test(order);
    }

    void wait(const bool expected, const std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        m_flag.wait(expected, order);
    }
    void wait(const bool expected, const std::memory_order order = std::memory_order_seq_cst) const volatile noexcept
    {
        const_cast<const atomic_flag*>(this)->wait(expected, order);
    }

    void notify_one() noexcept
    {
        m_flag.notify_one();
    }
    void notify_one() volatile noexcept
    {
        const_cast<atomic_flag*>(this)->notify_one();
    }

    void notify_all() noexcept
    {
        m_flag.notify_all();
    }
    void notify_all() volatile noexcept
    {
        const_cast<atomic_flag*>(this)->notify_all();
    }

    // Carbonite extensions to C++20 features
    template <class Rep, class Period>
    bool wait_for(const bool expected,
                  const std::chrono::duration<Rep, Period> dur,
                  const std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return m_flag.wait_for(expected, dur, order);
    }
    template <class Rep, class Period>
    bool wait_for(const bool expected,
                  const std::chrono::duration<Rep, Period> dur,
                  const std::memory_order order = std::memory_order_seq_cst) const volatile noexcept
    {
        return const_cast<const atomic_flag*>(this)->wait_for(expected, dur, order);
    }
    template <class Clock, class Duration>
    bool wait_until(const bool expected,
                    const std::chrono::time_point<Clock, Duration> tp,
                    const std::memory_order order = std::memory_order_seq_cst) const noexcept
    {
        return m_flag.wait_until(expected, tp, order);
    }
    template <class Clock, class Duration>
    bool wait_until(const bool expected,
                    const std::chrono::time_point<Clock, Duration> tp,
                    const std::memory_order order = std::memory_order_seq_cst) const volatile noexcept
    {
        return const_cast<const atomic_flag*>(this)->wait_until(expected, tp, order);
    }

    // Must be public because of CARB_ATOMIC_FLAG_INIT
    cpp::atomic<int32_t> m_flag;
};

using atomic_bool = atomic<bool>;
using atomic_char = atomic<char>;
using atomic_schar = atomic<signed char>;
using atomic_uchar = atomic<unsigned char>;
using atomic_short = atomic<short>;
using atomic_ushort = atomic<unsigned short>;
using atomic_int = atomic<int>;
using atomic_uint = atomic<unsigned int>;
using atomic_long = atomic<long>;
using atomic_ulong = atomic<unsigned long>;
using atomic_llong = atomic<long long>;
using atomic_ullong = atomic<unsigned long long>;
using atomic_char16_t = atomic<char16_t>;
using atomic_char32_t = atomic<char32_t>;
using atomic_wchar_t = atomic<wchar_t>;
using atomic_int8_t = atomic<int8_t>;
using atomic_uint8_t = atomic<uint8_t>;
using atomic_int16_t = atomic<int16_t>;
using atomic_uint16_t = atomic<uint16_t>;
using atomic_int32_t = atomic<int32_t>;
using atomic_uint32_t = atomic<uint32_t>;
using atomic_int64_t = atomic<int64_t>;
using atomic_uint64_t = atomic<uint64_t>;
using atomic_int_least8_t = atomic<int_least8_t>;
using atomic_uint_least8_t = atomic<uint_least8_t>;
using atomic_int_least16_t = atomic<int_least16_t>;
using atomic_uint_least16_t = atomic<uint_least16_t>;
using atomic_int_least32_t = atomic<int_least32_t>;
using atomic_uint_least32_t = atomic<uint_least32_t>;
using atomic_int_least64_t = atomic<int_least64_t>;
using atomic_uint_least64_t = atomic<uint_least64_t>;
using atomic_int_fast8_t = atomic<int_fast8_t>;
using atomic_uint_fast8_t = atomic<uint_fast8_t>;
using atomic_int_fast16_t = atomic<int_fast16_t>;
using atomic_uint_fast16_t = atomic<uint_fast16_t>;
using atomic_int_fast32_t = atomic<int_fast32_t>;
using atomic_uint_fast32_t = atomic<uint_fast32_t>;
using atomic_int_fast64_t = atomic<int_fast64_t>;
using atomic_uint_fast64_t = atomic<uint_fast64_t>;
using atomic_intptr_t = atomic<intptr_t>;
using atomic_uintptr_t = atomic<uintptr_t>;
using atomic_size_t = atomic<size_t>;
using atomic_ptrdiff_t = atomic<ptrdiff_t>;
using atomic_intmax_t = atomic<intmax_t>;
using atomic_uintmax_t = atomic<uintmax_t>;

} // namespace cpp
} // namespace carb
