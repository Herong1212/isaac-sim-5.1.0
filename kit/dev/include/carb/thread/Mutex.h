// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//!
//! @brief Carbonite mutex and recursive_mutex implementation.
#pragma once

#include "Futex.h"
#include "Util.h"

#include <type_traits>

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#endif

namespace carb
{
namespace thread
{

#ifndef DOXYGEN_SHOULD_SKIP_THIS
namespace detail
{
#    if CARB_PLATFORM_WINDOWS
template <bool Recursive>
class BaseMutex
{
public:
    constexpr static bool kRecursive = Recursive;

    CARB_PREVENT_COPY_AND_MOVE(BaseMutex);

    constexpr BaseMutex() noexcept = default;
    ~BaseMutex()
    {
        CARB_FATAL_UNLESS(m_count == 0, "Mutex destroyed while busy");
    }

    void lock()
    {
        uint32_t const tid = this_thread::getId();
        if (try_recurse(tid, std::bool_constant<kRecursive>()))
            return;

        m_lll.lock();
        m_owner = tid;
        m_count = 1;
    }
    bool try_lock()
    {
        uint32_t const tid = this_thread::getId();
        if (try_recurse(tid, std::bool_constant<kRecursive>()))
            return true;

        if (m_lll.try_lock())
        {
            m_owner = tid;
            m_count = 1;
            return true;
        }
        return false;
    }
    void unlock()
    {
        uint32_t tid = this_thread::getId();
        CARB_FATAL_UNLESS(m_owner == tid, "Not owner");
        if (--m_count == 0)
        {
            m_owner = kInvalidOwner;
            m_lll.unlock();
        }
    }
    bool is_current_thread_owner() const noexcept
    {
        // We don't need this to be an atomic op because one of the following must be true during this call:
        // - m_owner is equal to this_thread::getId() and cannot change
        // - m_owner is not equal and cannot become equal to this_thread::getId()
        return m_owner == this_thread::getId();
    }

private:
    bool try_recurse(ThreadId who, std::true_type) // recursive
    {
        if (who == m_owner)
        {
            // Already inside the lock
            ++m_count;
            return true;
        }
        return false;
    }
    bool try_recurse(ThreadId who, std::false_type) // non-recursive
    {
        CARB_FATAL_UNLESS(who != m_owner, "Attempted recursion on non-recursive mutex");
        return false;
    }

    constexpr static ThreadId kInvalidOwner = ThreadId{};

    LowLevelLock m_lll;
    ThreadId m_owner{ kInvalidOwner };
    int m_count{ 0 };
};

#    else
template <bool Recursive>
class BaseMutex;

// BaseMutex (non-recursive)
template <>
class BaseMutex<false>
{
public:
    constexpr static bool kRecursive = false;

    CARB_IF_NOT_TSAN(constexpr) BaseMutex() noexcept
    {
    }

    ~BaseMutex()
    {
        CARB_FATAL_UNLESS(m_owner == kInvalidOwner, "Mutex destroyed while busy");
    }

    void lock()
    {
        auto self = pthread_self();
        CARB_FATAL_UNLESS(m_owner != self, "Attempted recursive lock on non-recursive mutex");
        m_lll.lock();
        // Now inside the lock
        m_owner = self;
    }

    bool try_lock()
    {
        auto self = pthread_self();
        CARB_FATAL_UNLESS(m_owner != self, "Attempted recursive lock on non-recursive mutex");
        if (m_lll.try_lock())
        {
            // Now inside the lock
            m_owner = self;
            return true;
        }
        return false;
    }

    void unlock()
    {
        CARB_FATAL_UNLESS(m_owner == pthread_self(), "unlock() called by non-owning thread");
        m_owner = kInvalidOwner;
        m_lll.unlock();
    }

    bool is_current_thread_owner() const noexcept
    {
        // We don't need this to be an atomic op because one of the following must be true during this call:
        // - m_owner is equal to pthread_self() and cannot change
        // - m_owner is not equal and cannot become equal to pthread_self()
        return m_owner == pthread_self();
    }

private:
    constexpr static pthread_t kInvalidOwner = pthread_t();

    LowLevelLock m_lll;
    // this_thread::getId() is incredibly slow because it makes a syscall; use pthread_self() instead.
    // TSan complains about a data race here, but see is_current_thread_owner() for why it's not actually an issue.
    carb::AtomicIfTSan<pthread_t> m_owner = kInvalidOwner;
};

// BaseMutex (recursive)
template <>
class BaseMutex<true>
{
public:
    constexpr static bool kRecursive = true;

    CARB_IF_NOT_TSAN(constexpr) BaseMutex() noexcept = default;

    ~BaseMutex()
    {
        CARB_FATAL_UNLESS(m_owner == kInvalidOwner, "Mutex destroyed while busy");
    }

    void lock()
    {
        auto self = pthread_self();
        if (self == m_owner)
        {
            CARB_FATAL_UNLESS(m_depth != kMaxDepth, "Recursion overflow");
            ++m_depth;
            // Keep tsan updated wrt recursion
            __tsan_mutex_pre_lock(this, 0);
            __tsan_mutex_post_lock(this, 0, 0);
            return;
        }
        m_lll.lock();
        // Now inside the lock
        m_owner = self;
        CARB_ASSERT(m_depth == 0);
        m_depth = 1;
    }

    bool try_lock()
    {
        auto self = pthread_self();
        if (self == m_owner)
        {
            CARB_FATAL_UNLESS(m_depth != kMaxDepth, "Recursion overflow");
            ++m_depth;
            // Keep tsan updated wrt recursion
            __tsan_mutex_pre_lock(this, 0);
            __tsan_mutex_post_lock(this, 0, 0);
            return true;
        }

        if (m_lll.try_lock())
        {
            // Now inside the lock
            m_owner = self;
            CARB_ASSERT(m_depth == 0);
            m_depth = 1;
            return true;
        }
        return false;
    }

    void unlock()
    {
        CARB_FATAL_UNLESS(m_owner == pthread_self(), "unlock() called by non-owning thread");
        CARB_ASSERT(m_depth > 0);
        if (--m_depth == 0)
        {
            m_owner = kInvalidOwner;
            m_lll.unlock();
        }
        else
        {
            // Keep tsan updated wrt recursion
            __tsan_mutex_pre_unlock(this, 0);
            __tsan_mutex_post_unlock(this, 0);
        }
    }

    bool is_current_thread_owner() const noexcept
    {
        // We don't need this to be an atomic op because one of the following must be true during this call:
        // - m_owner is equal to pthread_self() and cannot change
        // - m_owner is not equal and cannot become equal to pthread_self()
        return m_owner == pthread_self();
    }

private:
    constexpr static pthread_t kInvalidOwner = pthread_t();
    constexpr static size_t kMaxDepth = size_t(INT_MAX); // For tsan since we can only pass an int for depth

    LowLevelLock m_lll;
    // this_thread::getId() is incredibly slow because it makes a syscall; use pthread_self() instead.
    // TSan complains about a data race here, but see is_current_thread_owner for why it's not an issue.
    carb::AtomicIfTSan<pthread_t> m_owner = kInvalidOwner;
    size_t m_depth = 0;
};
#    endif
} // namespace detail
#endif

/**
 * A Carbonite implementation of [std::mutex](https://en.cppreference.com/w/cpp/thread/mutex).
 *
 * @note Windows: `std::mutex` uses `SRWLOCK` for Win 7+, `CONDITION_VARIABLE` for Vista and the massive
 * `CRITICAL_SECTION` for pre-Vista. Due to this, the `std::mutex` class is about 80 bytes. Since Carbonite supports
 * Windows 10 and later, `SRWLOCK` is used exclusively. This implementation is 16 bytes. This version that uses
 * `SRWLOCK` is significantly faster on Windows than the portable implementation used for the linux version.
 *
 * @note Linux: `sizeof(std::mutex)` is 40 bytes on GLIBC 2.27, which is based on the size of `pthread_mutex_t`. The
 * Carbonite implementation of mutex is 16 bytes and at least as performant as `std::mutex` in the contended case.
 */
class mutex : protected detail::BaseMutex<false>
{
    using Base = detail::BaseMutex<false>;

public:
    /**
     * Constructor.
     *
     * @note Unlike `std::mutex`, this implementation can be declared `constexpr`.
     */
    CARB_IF_NOT_TSAN(constexpr) mutex() noexcept = default;

    /**
     * Destructor.
     * @warning `std::terminate()` is called if mutex is locked by a thread.
     */
    ~mutex() = default;

    /**
     * Locks the mutex, blocking until it becomes available.
     * @warning `std::terminate()` is called if the calling thread already has the mutex locked. Use recursive_mutex if
     * recursive locking is desired.
     * The calling thread must call unlock() at a later time to release the lock.
     */
    void lock()
    {
        Base::lock();
    }

    /**
     * Attempts to immediately lock the mutex.
     * @warning `std::terminate()` is called if the calling thread already has the mutex locked. Use recursive_mutex if
     * recursive locking is desired.
     * @returns `true` if the mutex was available and the lock was taken by the calling thread (unlock() must be called
     * from the calling thread at a later time to release the lock); `false` if the mutex could not be locked by the
     * calling thread.
     */
    bool try_lock()
    {
        return Base::try_lock();
    }

    /**
     * Unlocks the mutex.
     * @warning `std::terminate()` is called if the calling thread does not own the mutex.
     */
    void unlock()
    {
        Base::unlock();
    }

    /**
     * Checks if the current thread owns the mutex.
     * @note This is a non-standard Carbonite extension.
     * @returns `true` if the current thread owns the mutex; `false` otherwise.
     */
    bool is_current_thread_owner() const noexcept
    {
        return Base::is_current_thread_owner();
    }
};

/**
 * A Carbonite implementation of [std::recursive_mutex](https://en.cppreference.com/w/cpp/thread/recursive_mutex).
 *
 * @note Windows: `std::recursive_mutex` uses `SRWLOCK` for Win 7+, `CONDITION_VARIABLE` for Vista and the massive
 * `CRITICAL_SECTION` for pre-Vista. Due to this, the `std::recursive_mutex` class is about 80 bytes. Since Carbonite
 * supports Windows 10 and later, `SRWLOCK` is used exclusively. This implementation is 16 bytes. This version that uses
 * `SRWLOCK` is significantly faster on Windows than the portable implementation used for the linux version.
 *
 * @note Linux: `sizeof(std::recursive_mutex)` is 40 bytes on GLIBC 2.27, which is based on the size of
 * `pthread_mutex_t`. The Carbonite implementation of recursive_mutex is 24 bytes and at least as performant as
 * `std::recursive_mutex` in the contended case.
 */
class recursive_mutex : protected detail::BaseMutex<true>
{
    using Base = detail::BaseMutex<true>;

public:
    /**
     * Constructor.
     *
     * @note Unlike `std::recursive_mutex`, this implementation can be declared `constexpr`.
     */
    CARB_IF_NOT_TSAN(constexpr) recursive_mutex() noexcept = default;

    /**
     * Destructor.
     * @warning `std::terminate()` is called if recursive_mutex is locked by a thread.
     */
    ~recursive_mutex() = default;

    /**
     * Locks the recursive_mutex, blocking until it becomes available.
     *
     * The calling thread must call unlock() at a later time to release the lock. There must be symmetrical calls to
     * unlock() for each call to lock() or successful call to try_lock().
     */
    void lock()
    {
        Base::lock();
    }

    /**
     * Attempts to immediately lock the recursive_mutex.
     * @returns `true` if the recursive_mutex was available and the lock was taken by the calling thread (unlock() must
     * be called from the calling thread at a later time to release the lock); `false` if the recursive_mutex could not
     * be locked by the calling thread. If the lock was already held by the calling thread, `true` is always returned.
     */
    bool try_lock()
    {
        return Base::try_lock();
    }

    /**
     * Unlocks the recursive_mutex.
     * @warning `std::terminate()` is called if the calling thread does not own the recursive_mutex.
     */
    void unlock()
    {
        Base::unlock();
    }

    /**
     * Checks if the current thread owns the mutex.
     * @note This is a non-standard Carbonite extension.
     * @returns `true` if the current thread owns the mutex; `false` otherwise.
     */
    bool is_current_thread_owner() const noexcept
    {
        return Base::is_current_thread_owner();
    }
};

} // namespace thread
} // namespace carb
