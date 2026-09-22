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
//! @brief Defines the LocklessStack class.
#pragma once

#include "../Defines.h"
#include "../cpp/Atomic.h"
#include "../thread/Util.h"

#include <atomic>
#include <chrono>
#include <type_traits>
#include <utility>

#if CARB_POSIX
#    include <dlfcn.h>
#endif

namespace carb
{
namespace container
{

template <class T>
class LocklessStackLink;
template <class T, LocklessStackLink<T> T::*U>
class LocklessStack;

#ifndef DOXYGEN_BUILD
namespace detail
{
template <class T, LocklessStackLink<T> T::*U>
class LocklessStackHelpers;
template <class T, LocklessStackLink<T> T::*U>
class LocklessStackBase;
} // namespace detail
#endif

/**
 * Defines the link object. Each class contained in LocklessStack must have a member of type LocklessStackLink<T>. A
 * pointer to this member is required as the second parameter for LocklessStack.
 */
template <class T>
class LocklessStackLink
{
public:
    /**
     * Default constructor.
     */
    constexpr LocklessStackLink() = default;

private:
    CARB_VIZ LocklessStackLink<T>* m_next;

    friend T;
    template <class U, LocklessStackLink<U> U::*V>
    friend class detail::LocklessStackHelpers;
    template <class U, LocklessStackLink<U> U::*V>
    friend class detail::LocklessStackBase;
    template <class U, LocklessStackLink<U> U::*V>
    friend class LocklessStack;
};

#if !defined(DOXYGEN_BUILD)
namespace detail
{

template <class T, LocklessStackLink<T> T::*U>
class LocklessStackHelpers
{
public:
    // Access the LocklessStackLink member of `p`
    static LocklessStackLink<T>* link(T* p)
    {
        return std::addressof(p->*U);
    }

    // Converts a LocklessStackLink to the containing object
    static T* convert(LocklessStackLink<T>* p)
    {
        // We need to calculate the offset of our link member and calculate where T is.
        // Note that this doesn't work if T uses virtual inheritance
        size_t offset = (size_t) reinterpret_cast<char*>(&(((T*)0)->*U));
        return reinterpret_cast<T*>(reinterpret_cast<char*>(p) - offset);
    }
};

// Base implementations
template <class T, LocklessStackLink<T> T::*U>
class LocklessStackBase : protected LocklessStackHelpers<T, U>
{
    using Base = LocklessStackHelpers<T, U>;
    using Link = LocklessStackLink<T>;

public:
    bool _isEmpty() const
    {
        return !m_head.load(std::memory_order_acquire);
    }

    bool _push(T* first, T* last)
    {
        Link* old = m_head.load(std::memory_order_relaxed);
        do
        {
            // NOTE: if m_head has the lock bit set, the cmpxchg will fail. This is by design. Paradoxically this is
            // faster than testing and reloading.
            old = withoutLockBit(old);
            Base::link(last)->m_next = old;
        } while (!m_head.compare_exchange_weak(
            old, Base::link(first), std::memory_order_release, std::memory_order_relaxed));
        return old == nullptr;
    }

    T* _popOne()
    {
        this_thread::atomic_fence_seq_cst(); // force visibility
        Link* old = m_head.load(std::memory_order_relaxed);
        for (thread::AtomicBackoff<> backoff;; backoff.pause())
        {
            if (!old)
                return nullptr;

            // Try to lock. On average it is faster for our contention tests if we use AtomicBackoff and do not check
            // whether `old` has the lock bit set before attempting the cmpxchg.
            if (m_head.compare_exchange_weak(old, withLockBit(old), std::memory_order_relaxed, std::memory_order_relaxed) &&
                !hasLockBit(old))
                break;
        }

        // Now has exclusive access
        CARB_ASSERT(!hasLockBit(old->m_next));
        m_head.store(std::exchange(old->m_next, nullptr), std::memory_order_release);

        return Base::convert(old);
    }

    T* _popAll()
    {
        this_thread::atomic_fence_seq_cst(); // force visibility
        Link* old = m_head.load(std::memory_order_relaxed);
        for (thread::AtomicBackoff<> backoff;; backoff.pause())
        {
            if (!old)
                return nullptr;

            // Try to lock. On average it is faster for our contention tests if we use AtomicBackoff and do not check
            // whether `old` has the lock bit set before attempting the cmpxchg.
            if (m_head.compare_exchange_weak(old, withLockBit(old), std::memory_order_relaxed, std::memory_order_relaxed) &&
                !hasLockBit(old))
                break;
        }

        // Now has exclusive access
        m_head.store(nullptr, std::memory_order_release);

        return Base::convert(old);
    }

    void _wait()
    {
        auto p = m_head.load();
        while (!p)
        {
            m_head.wait(p);
            p = m_head.load();
        }
    }

    template <class Rep, class Period>
    bool _waitFor(const std::chrono::duration<Rep, Period>& dur)
    {
        return _waitUntil(cpp::detail::absTime<std::chrono::steady_clock>(dur));
    }

    template <class Clock, class Duration>
    bool _waitUntil(const std::chrono::time_point<Clock, Duration>& tp)
    {
        auto p = m_head.load();
        while (!p)
        {
            if (!m_head.wait_until(p, tp))
                return false;
            p = m_head.load();
        }
        return true;
    }

    void _notifyOne()
    {
        m_head.notify_one();
    }

    void _notifyAll()
    {
        m_head.notify_all();
    }

private:
    constexpr static uintptr_t kLock = 1;

    static bool hasLockBit(Link* in)
    {
        return !!(reinterpret_cast<uintptr_t>(in) & kLock);
    }

    static Link* withLockBit(Link* in)
    {
        return reinterpret_cast<Link*>(reinterpret_cast<uintptr_t>(in) | kLock);
    }

    static Link* withoutLockBit(Link* in)
    {
        return reinterpret_cast<Link*>(reinterpret_cast<uintptr_t>(in) & ~kLock);
    }

    cpp::atomic<Link*> m_head{ nullptr };
};
} // namespace detail
#endif

/**
 * @brief Implements a lockless stack: a LIFO container that is thread-safe yet requires no kernel involvement.
 *
 * LocklessStack is designed to be easy-to-use. For a class `Foo` that you want to be contained in a LocklessStack, it
 * must have a member of type LocklessStackLink<Foo>. This member is what the LocklessStack will use for tracking data.
 *
 * Pushing to LocklessStack is simply done through LocklessStack::push(), which is entirely thread-safe. LocklessStack
 * ensures last-in-first-out (LIFO) for each producer pushing to LocklessStack. Multiple producers may be pushing to
 * LocklessStack simultaneously, so their items can become mingled, but each producer's pushed items will be strongly
 * ordered.
 *
 * Popping is done through LocklessStack::pop(), which is also entirely thread-safe. Multiple threads may all attempt to
 * pop from the same LocklessStack simultaneously.
 *
 * Simple example:
 * ```cpp
 * class Foo
 * {
 * public:
 *     LocklessStackLink<Foo> m_link;
 * };
 *
 * LocklessStack<Foo, &Foo::m_link> stack;
 * stack.push(new Foo);
 * Foo* p = stack.pop();
 * delete p;
 * ```
 *
 * @thread_safety LocklessStack is entirely thread-safe except where declared otherwise. No allocation happens with a
 * LocklessStack; instead the caller is responsible for construction/destruction of contained objects.
 *
 * @tparam T The type to contain.
 * @tparam U A pointer-to-member of a LocklessStackLink member within T (see above example).
 */
template <class T, LocklessStackLink<T> T::*U>
class LocklessStack final : protected detail::LocklessStackBase<T, U>
{
    using Base = detail::LocklessStackBase<T, U>;

public:
    /**
     * Constructor.
     */
    constexpr LocklessStack() = default;

    /**
     * Destructor.
     *
     * Asserts that isEmpty() returns true.
     */
    ~LocklessStack()
    {
        // Ensure the stack is empty
        CARB_ASSERT(isEmpty());
    }

    /**
     * Indicates whether the stack is empty.
     *
     * @warning Another thread may have modified the LocklessStack before this function returns.
     *
     * @returns `true` if the stack appears empty; `false` if items appear to exist in the stack.
     */
    bool isEmpty() const
    {
        return Base::_isEmpty();
    }

    /**
     * Pushes an item onto the stack.
     *
     * @param p The item to push onto the stack.
     *
     * @return `true` if the stack was previously empty prior to push; `false` otherwise. Note that this is atomically
     * correct as opposed to checking isEmpty() before push().
     */
    bool push(T* p)
    {
        return Base::_push(p, p);
    }

    /**
     * Pushes a contiguous block of entries from [ @p begin, @p end) onto the stack.
     *
     * @note All of the entries are guaranteed to remain strongly ordered and will not be interspersed with entries from
     * other threads. @p begin will be popped from the stack first.
     *
     * @param begin An <a href="https://en.cppreference.com/w/cpp/named_req/InputIterator">InputIterator</a> of the
     * first item to push. `*begin` must resolve to a `T&`.
     * @param end An off-the-end InputIterator after the last item to push.
     * @returns `true` if the stack was empty prior to push; `false` otherwise. Note that this is atomically correct
     * as opposed to calling isEmpty() before push().
     */
#ifndef DOXYGEN_BUILD
    template <class InputItRef,
              std::enable_if_t<std::is_convertible<decltype(std::declval<InputItRef&>()++, *std::declval<InputItRef&>()), T&>::value,
                               bool> = false>
#else
    template <class InputItRef>
#endif
    bool push(InputItRef begin, InputItRef end)
    {
        if (begin == end)
        {
            return false;
        }

        // Walk the list and have them point to each other
        InputItRef last = begin;
        InputItRef iter = begin;
        for (iter++; iter != end; last = iter++)
        {
            Base::link(std::addressof(*last))->m_next = Base::link(std::addressof(*iter));
        }

        return Base::_push(std::addressof(*begin), std::addressof(*last));
    }

    /**
     * Pushes a block of pointers-to-entries from [ @p begin, @p end) onto the stack.
     *
     * @note All of the entries are guaranteed to remain strongly ordered and will not be interspersed with entries from
     * other threads. @p begin will be popped from the stack first.
     *
     * @param begin An <a href="https://en.cppreference.com/w/cpp/named_req/InputIterator">InputIterator</a> of the
     * first item to push. `*begin` must resolve to a `T*`.
     * @param end An off-the-end InputIterator after the last item to push.
     * @returns `true` if the stack was empty prior to push; `false` otherwise. Note that this is atomically correct
     * as opposed to calling isEmpty() before push().
     */
#ifndef DOXYGEN_BUILD
    template <class InputItPtr,
              std::enable_if_t<std::is_convertible<decltype(std::declval<InputItPtr&>()++, *std::declval<InputItPtr&>()), T*>::value,
                               bool> = true>
#else
    template <class InputItPtr>
#endif
    bool push(InputItPtr begin, InputItPtr end)
    {
        if (begin == end)
        {
            return false;
        }

        // Walk the list and have them point to each other
        InputItPtr last = begin;
        InputItPtr iter = begin;
        for (iter++; iter != end; last = iter++)
        {
            Base::link(*last)->m_next = Base::link(*iter);
        }

        return Base::_push(*begin, *last);
    }

    /**
     * Pops an item from the top of the stack if available.
     *
     * @return An item popped from the stack. If the stack was empty, then `nullptr` is returned.
     */
    T* pop()
    {
        return Base::_popOne();
    }

    /**
     * Empties the stack.
     *
     * @note To perform an action on each item as it is popped, use forEach() instead.
     */
    void popAll()
    {
        Base::_popAll();
    }

    /**
     * Pops all available items from the stack calling an invocable object on each.
     *
     * First, pops all available items from `*this` and then calls @p f on each.
     *
     * @note As the pop is the first thing that happens, any new entries that get pushed while the function is executing
     * will NOT be popped and will remain in the stack when this function returns.
     *
     * @param f An invocable object that accepts a `T*` parameter. Called for each item that was popped from the stack.
     */
    template <class Func>
    void forEach(Func&& f)
    {
        T* p = Base::_popAll();
        LocklessStackLink<T>* h = p ? Base::link(p) : nullptr;
        while (h)
        {
            p = Base::convert(h);
            h = h->m_next;
            f(p);
        }
    }

    /**
     * Pushes an item onto the stack and notifies a waiting listener.
     *
     * Equivalent to doing `auto b = push(p); notifyOne(); return b;`.
     *
     * @see push(), notifyOne()
     *
     * @param p The item to push.
     * @returns `true` if the stack was empty prior to push; `false` otherwise. Note that this is atomically correct
     * as opposed to calling isEmpty() before push().
     */
    bool pushNotify(T* p)
    {
        bool b = push(p);
        notifyOne();
        return b;
    }

    /**
     * Blocks the calling thread until an item is available and returns it.
     *
     * Requires the item to be pushed with pushNotify(), notifyOne() or notifyAll().
     *
     * @see pop(), wait()
     *
     * @returns The first item popped from the stack.
     */
    T* popWait()
    {
        T* p = pop();
        while (!p)
        {
            wait();
            p = pop();
        }
        return p;
    }

    /**
     * Blocks the calling thread until an item is available and returns it or a timeout elapses.
     *
     * Requires the item to be pushed with pushNotify(), notifyOne() or notifyAll().
     *
     * @see pop(), waitFor()
     *
     * @param dur The duration to wait for an item to become available.
     * @returns the first item removed from the stack or `nullptr` if the timeout period elapses.
     */
    template <class Rep, class Period>
    T* popWaitFor(const std::chrono::duration<Rep, Period>& dur)
    {
        return popWaitUntil(cpp::detail::absTime<std::chrono::steady_clock>(dur));
    }

    /**
     * Blocks the calling thread until an item is available and returns it or the clock reaches a time point.
     *
     * Requires the item to be pushed with pushNotify(), notifyOne() or notifyAll().
     *
     * @see pop(), waitUntil()
     *
     * @param tp The time to wait until for an item to become available.
     * @returns the first item removed from the stack or `nullptr` if the timeout period elapses.
     */
    template <class Clock, class Duration>
    T* popWaitUntil(const std::chrono::time_point<Clock, Duration>& tp)
    {
        T* p = pop();
        while (!p)
        {
            if (!waitUntil(tp))
            {
                return pop();
            }
            p = pop();
        }
        return p;
    }

    /**
     * Waits until the stack is non-empty.
     *
     * @note Requires notification that the stack is non-empty, such as from pushNotify(), notifyOne() or notifyAll().
     *
     * @note Though wait() returns, another thread may have popped the available item making the stack empty again. Use
     * popWait() if it is desired to ensure that the current thread can obtain an item.
     */
    void wait()
    {
        Base::_wait();
    }

    /**
     * Waits until the stack is non-empty or a specified duration has passed.
     *
     * @note Though waitFor() returns `true`, another thread may have popped the available item making the stack empty
     * again. Use popWaitFor() if it is desired to ensure that the current thread can obtain an item.
     *
     * @note Requires notification that the stack is non-empty, such as from pushNotify(), notifyOne() or notifyAll().
     *
     * @param dur The duration to wait for an item to become available.
     * @returns `true` if an item appears to be available; `false` if the timeout elapses.
     */
    template <class Rep, class Period>
    bool waitFor(const std::chrono::duration<Rep, Period>& dur)
    {
        return Base::_waitFor(dur);
    }

    /**
     * Waits until the stack is non-empty or a specific time is reached.
     *
     * @note Though waitUntil() returns `true`, another thread may have popped the available item making the stack empty
     * again. Use popWaitUntil() if it is desired to ensure that the current thread can obtain an item.
     *
     * @note Requires notification that the stack is non-empty, such as from pushNotify(), notifyOne() or notifyAll().
     *
     * @param tp The time to wait until for an item to become available.
     * @returns `true` if an item appears to be available; `false` if the time is reached.
     */
    template <class Clock, class Duration>
    bool waitUntil(const std::chrono::time_point<Clock, Duration>& tp)
    {
        return Base::_waitUntil(tp);
    }

    /**
     * Notifies a single waiting thread.
     *
     * Notifies a single thread waiting in wait(), waitFor(), waitUntil(), popWait(), popWaitFor(), or popWaitUntil() to
     * wake and check the stack.
     */
    void notifyOne()
    {
        Base::_notifyOne();
    }

    /**
     * Notifies all waiting threads.
     *
     * Notifies all threads waiting in wait(), waitFor(), waitUntil(), popWait(), popWaitFor(), or popWaitUntil() to
     * wake and check the stack.
     */
    void notifyAll()
    {
        Base::_notifyAll();
    }
};

} // namespace container
} // namespace carb
