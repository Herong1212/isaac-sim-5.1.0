// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file
//! @brief Futex implementation details.
#pragma once

#include "NativeFutex.h"
#include "LowLevelLock.h"

#include <atomic>
#include <chrono>
#include <cstddef>
#include <memory>
#include <mutex>
#include <utility>

//! \cond DEV
namespace carb
{
namespace thread
{
namespace detail
{

// NOTE: We cannot use thread ID wakeup on Windows while LowLevelLock is used (and it also uses thread ID wakeup) as
// this will lead to hard-to-debug hangs (See OVCC-1662)
#define CARBLOCAL_WIN_USE_THREADID 0

struct ParkingLot
{
    struct WaitEntry
    {
        enum Bits : uint32_t
        {
            kNoBits = 0,
            kNotifyBit = 1,
            kWaitBit = 2,
        };

        const void* addr;
        WaitEntry* next{ nullptr };
        WaitEntry* prev{ nullptr };
        uint32_t changeId{ 0 };
        NativeFutex::AtomicType wakeup{ kNoBits };
#if CARB_PLATFORM_WINDOWS && CARBLOCAL_WIN_USE_THREADID
        ThreadId threadId{ this_thread::getId() };
#endif
    };

    class WakeCache
    {
    public:
        constexpr static size_t kWakeCacheSize = 128;

        WakeCache() noexcept = default;

        ~WakeCache()
        {
            wakeAll();
        }

#if CARB_PLATFORM_WINDOWS && CARBLOCAL_WIN_USE_THREADID
        using Entry = ThreadId;

        static Entry fromWaitEntry(WaitEntry& we) noexcept
        {
            return we.threadId;
        }

        static void doWake(Entry val) noexcept
        {
            threadId_wake(val);
        }

        static void doWait(WaitEntry& we) noexcept
        {
            threadId_wait(we.wakeup);
        }

        template <class Duration>
        static bool doWaitFor(WaitEntry& we, Duration duration)
        {
            return threadId_wait_for(we.wakeup, duration);
        }

        template <class TimePoint>
        static bool doWaitUntil(WaitEntry& we, TimePoint timePoint)
        {
            return threadId_wait_until(we.wakeup, timePoint);
        }
#else
        using Entry = NativeFutex::AtomicType*;

        static Entry fromWaitEntry(WaitEntry& we) noexcept
        {
            return &we.wakeup;
        }

        static void doWake(Entry val) noexcept
        {
            NativeFutex::notify_one(*val);
        }

        static void doWait(WaitEntry& we) noexcept
        {
            NativeFutex::wait(we.wakeup, WaitEntry::kNoBits);
        }

        template <class Duration>
        static bool doWaitFor(WaitEntry& we, Duration duration)
        {
            return NativeFutex::wait_for(we.wakeup, WaitEntry::kNoBits, duration);
        }

        template <class TimePoint>
        static bool doWaitUntil(WaitEntry& we, TimePoint timePoint)
        {
            return NativeFutex::wait_until(we.wakeup, WaitEntry::kNoBits, timePoint);
        }
#endif

        [[nodiscard]] bool add(WaitEntry& we) noexcept
        {
            CARB_ASSERT(m_end < pastTheEnd());
            *(m_end++) = fromWaitEntry(we);
            return m_end != pastTheEnd();
        }

        void wakeAll() noexcept
        {
            for (Entry* p = &m_entries[0]; p != m_end; ++p)
                doWake(*p);
            m_end = &m_entries[0];
        }

    private:
        const Entry* pastTheEnd() const noexcept
        {
            return &m_entries[kWakeCacheSize];
        }

        Entry m_entries[kWakeCacheSize];
        Entry* m_end = &m_entries[0];
    };

    class WaitBucket
    {
        LowLevelLock m_lock;
        // m_head intentionally has data races, which TSan flags. Use an atomic to work around TSan.
        carb::AtomicIfTSan<WaitEntry*> m_head{ nullptr };
        WaitEntry* m_tail{ nullptr };
        std::atomic_uint32_t m_changeTracker{ 0 };

        static_assert(std::atomic<WaitEntry*>::is_always_lock_free, "requires lock-free atomics");

        void assertLockState() const noexcept
        {
            CARB_ASSERT(m_lock.is_locked());
        }

    public:
        CARB_IF_NOT_TSAN(constexpr) WaitBucket() noexcept = default;

        [[nodiscard]] std::unique_lock<LowLevelLock> lock() noexcept
        {
            return std::unique_lock<LowLevelLock>(m_lock);
        }

        void incChangeTracker() noexcept
        {
            assertLockState(); // under lock
            m_changeTracker.store(m_changeTracker.load(std::memory_order_relaxed) + 1, std::memory_order_relaxed);
        }

        bool appearsEmpty() const noexcept
        {
            // fence-fence synchronization with wait functions, forces visibility
            this_thread::atomic_fence_seq_cst();
#if CARB_TSAN_ENABLED
            return m_head == nullptr;
#else
            // cpp::atomic_ref() is dependent on this file, so we can't use it.
            return cpp::bit_cast<const std::atomic<WaitEntry*>*>(&m_head)->load(std::memory_order_relaxed) == nullptr;
#endif
        }

        std::atomic_uint32_t& changeTracker() noexcept
        {
            return m_changeTracker;
        }

        WaitEntry* head() noexcept
        {
            assertLockState();
            return m_head;
        }

        void append(WaitEntry* e) noexcept
        {
            assertLockState();
            e->prev = std::exchange(m_tail, e);
            e->next = nullptr;
            if (e->prev)
            {
                e->prev->next = e;
            }
            else
            {
                CARB_ASSERT(m_head == nullptr);
                m_head = e;
            }
        }

        void remove(WaitEntry* e) noexcept
        {
            assertLockState();
            if (e->next)
            {
                e->next->prev = e->prev;
            }
            else
            {
                CARB_ASSERT(m_tail == e);
                m_tail = e->prev;
            }
            if (e->prev)
            {
                e->prev->next = e->next;
            }
            else
            {
                CARB_ASSERT(m_head == e);
                m_head = e->next;
            }
        }

        constexpr static size_t kNumWaitBuckets = 2048; // Must be a power of two
        static_assert(carb::cpp::has_single_bit(kNumWaitBuckets), "Invalid assumption");

        static inline WaitBucket& bucket(const void* addr) noexcept
        {
            static WaitBucket waitBuckets[kNumWaitBuckets];

#if 1
            // FNV-1a hash is fast with really good distribution
            // In "futex buckets" test, about ~70% on Windows and ~80% on Linux
            auto hash = carb::hashBuffer(&addr, sizeof(addr));
            return waitBuckets[hash & (kNumWaitBuckets - 1)];
#else
            // Simple bitshift method
            // In "futex buckets" test:
            //  >> 4 bits: ~71% on Windows, ~72% on Linux
            //  >> 5 bits: ~42% on Windows, ~71% on Linux
            return waitBuckets[(size_t(addr) >> 4) & (kNumWaitBuckets - 1)];
#endif
        }
    };

    template <typename T>
    static void wait(const std::atomic<T>& val, T compare) noexcept
    {
        WaitEntry entry{ std::addressof(val) };

        using I = to_integral_t<T>;

        // Check before waiting
        if (reinterpret_as<I>(val.load(std::memory_order_acquire)) != reinterpret_as<I>(compare))
        {
            return;
        }

        WaitBucket& b = WaitBucket::bucket(std::addressof(val));
        {
            auto lock = b.lock();

            // Check inside the lock to reduce spurious wakeups
            if (CARB_UNLIKELY(reinterpret_as<I>(val.load(std::memory_order_relaxed)) != reinterpret_as<I>(compare)))
            {
                return;
            }

            entry.changeId = b.changeTracker().load(std::memory_order_relaxed);

            b.append(&entry);
        }

        // Do the wait if everything is consistent
        NativeFutex::Type v = WaitEntry::kNoBits;
        if (CARB_LIKELY(reinterpret_as<I>(val.load(std::memory_order_acquire)) == reinterpret_as<I>(compare) &&
                        b.changeTracker().load(std::memory_order_relaxed) == entry.changeId))
        {
            ///////////////////////////////////////////////////////////////////
            // Do the wait
            WakeCache::doWait(entry);
            ///////////////////////////////////////////////////////////////////

            // Full fence to force visibility on entry.wakeup, which can be a relaxed load
            this_thread::atomic_fence_seq_cst();
            // TSAN doesn't understand the barrier, so notify it of the acquire
            __tsan_acquire(&entry.wakeup);
            v = entry.wakeup.load(std::memory_order_relaxed);

            // See if already removed without a wait bit
            if (CARB_LIKELY(v == WaitEntry::kNotifyBit))
                return;
        }

        // May not have been removed
        if (!(v & WaitEntry::kNotifyBit))
        {
            // Need to remove
            auto lock = b.lock();
            // Check again under the lock (relaxed because we're under the lock)
            v = entry.wakeup.load(std::memory_order_relaxed);
            if (CARB_LIKELY(v == WaitEntry::kNoBits))
            {
                b.remove(&entry);
                return;
            }
        }

        // Spin briefly while the wait bit is set, though this should be rare
        if (CARB_UNLIKELY(v & WaitEntry::kWaitBit))
            this_thread::spinWait([&] { return !(entry.wakeup.load(std::memory_order_acquire) & WaitEntry::kWaitBit); });
    }

    template <typename T, typename Rep, typename Period>
    static bool wait_for(const std::atomic<T>& val, T compare, const std::chrono::duration<Rep, Period>& duration)
    {
        WaitEntry entry{ std::addressof(val) };

        using I = to_integral_t<T>;

        // Check before waiting
        if (reinterpret_as<I>(val.load(std::memory_order_acquire)) != reinterpret_as<I>(compare))
        {
            return true;
        }

        WaitBucket& b = WaitBucket::bucket(std::addressof(val));
        {
            auto lock = b.lock();

            // Check inside the lock to reduce spurious wakeups
            if (CARB_UNLIKELY(reinterpret_as<I>(val.load(std::memory_order_relaxed)) != reinterpret_as<I>(compare)))
            {
                return true;
            }

            entry.changeId = b.changeTracker().load(std::memory_order_relaxed);
            b.append(&entry);
        }

        // Do the wait if everything is consistent
        bool wasNotified = true;
        NativeFutex::Type v = WaitEntry::kNoBits;
        if (CARB_LIKELY(reinterpret_as<I>(val.load(std::memory_order_acquire)) == reinterpret_as<I>(compare) &&
                        b.changeTracker().load(std::memory_order_relaxed) == entry.changeId))
        {
            ///////////////////////////////////////////////////////////////////
            // Do the wait
            wasNotified = WakeCache::doWaitFor(entry, duration);
            ///////////////////////////////////////////////////////////////////

            if (wasNotified) // specifically woken
            {
                // Full fence to force visibility on entry.wakeup, which can be a relaxed load
                this_thread::atomic_fence_seq_cst();
                // TSAN doesn't understand the barrier, so notify it of the acquire
                __tsan_acquire(&entry.wakeup);
                v = entry.wakeup.load(std::memory_order_relaxed);

                // See if already removed without a wait bit
                if (CARB_LIKELY(v == WaitEntry::kNotifyBit))
                    return true;
            }
        }

        // May not have been removed.
        if (!(v & WaitEntry::kNotifyBit))
        {
            // Need to remove
            auto lock = b.lock();
            // Check again under the lock (relaxed because we're under the lock)
            v = entry.wakeup.load(std::memory_order_relaxed);
            if (CARB_LIKELY(v == WaitEntry::kNoBits))
            {
                b.remove(&entry);
                return wasNotified;
            }
            else
            {
                // Already removed, so treat it as a notification rather than a timeout.
                wasNotified = true;
            }
        }

        // Spin briefly while the wait bit is set, though this should be rare
        if (CARB_UNLIKELY(v & WaitEntry::kWaitBit))
            this_thread::spinWait([&] { return !(entry.wakeup.load(std::memory_order_acquire) & WaitEntry::kWaitBit); });

        return wasNotified;
    }

    template <typename T, typename FromClock, typename Duration>
    static bool wait_until(const std::atomic<T>& val, T compare, const std::chrono::time_point<FromClock, Duration>& until)
    {
        WaitEntry entry{ std::addressof(val) };

        using I = to_integral_t<T>;

        // Check before waiting
        if (reinterpret_as<I>(val.load(std::memory_order_acquire)) != reinterpret_as<I>(compare))
        {
            return true;
        }

        // Convert to a steady clock
        auto when = cpp::detail::convertToClock<std::chrono::steady_clock>(until);

        WaitBucket& b = WaitBucket::bucket(std::addressof(val));
        {
            auto lock = b.lock();

            // Check inside the lock to reduce spurious wakeups
            if (CARB_UNLIKELY(reinterpret_as<I>(val.load(std::memory_order_relaxed)) != reinterpret_as<I>(compare)))
            {
                return true;
            }

            entry.changeId = b.changeTracker().load(std::memory_order_relaxed);
            b.append(&entry);
        }

        // Do the wait if everything is consistent
        bool wasNotified = true;
        NativeFutex::Type v = WaitEntry::kNoBits;
        if (CARB_LIKELY(reinterpret_as<I>(val.load(std::memory_order_acquire)) == reinterpret_as<I>(compare) &&
                        b.changeTracker().load(std::memory_order_relaxed) == entry.changeId))
        {
            ///////////////////////////////////////////////////////////////////
            // Do the wait
            wasNotified = WakeCache::doWaitUntil(entry, when);
            ///////////////////////////////////////////////////////////////////

            if (wasNotified)
            {
                // Full fence to force visibility on entry.wakeup, which can be a relaxed load
                this_thread::atomic_fence_seq_cst();
                // TSAN doesn't understand the barrier, so notify it of the acquire
                __tsan_acquire(&entry.wakeup);
                v = entry.wakeup.load(std::memory_order_relaxed);

                // See if already removed without a wait bit
                if (CARB_LIKELY(v == WaitEntry::kNotifyBit))
                    return true;
            }
        }

        // May not have been removed.
        if (!(v & WaitEntry::kNotifyBit))
        {
            // Need to remove
            auto lock = b.lock();
            // Check again under the lock (relaxed because we're under the lock)
            v = entry.wakeup.load(std::memory_order_relaxed);
            if (CARB_LIKELY(v == WaitEntry::kNoBits))
            {
                b.remove(&entry);
                return wasNotified;
            }
            else
            {
                // Already removed, so treat it as a notification rather than a timeout.
                wasNotified = true;
            }
        }

        // Spin briefly while the wait bit is set, though this should be rare
        if (CARB_UNLIKELY(v & WaitEntry::kWaitBit))
            this_thread::spinWait([&] { return !(entry.wakeup.load(std::memory_order_acquire) & WaitEntry::kWaitBit); });

        return wasNotified;
    }

    static void notify_one(void* addr) noexcept
    {
        WaitBucket& b = WaitBucket::bucket(addr);

        // Read empty state with full fence to avoid locking
        if (b.appearsEmpty())
            return;

        auto lock = b.lock();
        b.incChangeTracker();
        for (WaitEntry* e = b.head(); e; e = e->next)
        {
            if (e->addr == addr)
            {
                // Remove before setting the wakeup flag
                b.remove(e);

                // `e` may be destroyed after we unlock, so record the value that we need here.
                auto val = WakeCache::fromWaitEntry(*e);

                // release semantics despite being under the lock because we want `val` read before store.
                // No access to `e` allowed after this store.
                e->wakeup.store(WaitEntry::kNotifyBit, std::memory_order_release);
                // TSAN needs to be manually informed of the release
                __tsan_release(&e->wakeup);

                // Unlock and issue the wake
                lock.unlock();

                WakeCache::doWake(val);

                return;
            }
        }
    }

private:
    static CARB_NOINLINE void notify_n_slow(
        std::unique_lock<LowLevelLock> lock, void* addr, size_t n, WaitBucket& b, WaitEntry* e, WakeCache& wakeCache) noexcept
    {
        // We are waking a lot of things and the wakeCache is completely full. Now we need to start building a list
        WaitEntry *wake = nullptr, *end = nullptr;

        for (WaitEntry* next; e; e = next)
        {
            next = e->next;
            if (e->addr == addr)
            {
                b.remove(e);
                e->next = nullptr;
                // Don't bother with prev pointers
                if (end)
                    end->next = e;
                else
                    wake = e;
                end = e;

                // Relaxed because we're under the lock.
                // Need to set the wait bit since we're still reading/writing to the WaitEntry
                e->wakeup.store(WaitEntry::kWaitBit | WaitEntry::kNotifyBit, std::memory_order_relaxed);

                if (!--n)
                    break;
            }
        }

        lock.unlock();

        // Wake the entire cache since we know it's full
        wakeCache.wakeAll();

        for (WaitEntry* next; wake; wake = next)
        {
            next = wake->next;

            auto val = WakeCache::fromWaitEntry(*wake);

            // Clear the wait bit so that only the wake bit is set. No accesses to `wake` are allowed after this since
            // the waiting thread is free to destroy it. Release to synchronize-with spin-waiting on the wait bit.
            wake->wakeup.store(WaitEntry::kNotifyBit, std::memory_order_release);
            // TSAN needs to be manually informed of the release
            __tsan_release(&wake->wakeup);

            WakeCache::doWake(val);
        }
    }

    static CARB_NOINLINE void notify_all_slow(
        std::unique_lock<LowLevelLock> lock, void* addr, WaitBucket& b, WaitEntry* e, WakeCache& wakeCache) noexcept
    {
        // We are waking a lot of things and the wakeCache is completely full. Now we need to start building a list
        WaitEntry *wake = nullptr, *end = nullptr;

        for (WaitEntry* next; e; e = next)
        {
            next = e->next;
            if (e->addr == addr)
            {
                b.remove(e);
                e->next = nullptr;
                // Don't bother with prev pointers
                if (end)
                    end->next = e;
                else
                    wake = e;
                end = e;

                // Relaxed because we're under the lock.
                // Need to set the wait bit since we're still reading/writing to the WaitEntry
                e->wakeup.store(WaitEntry::kWaitBit | WaitEntry::kNotifyBit, std::memory_order_relaxed);
            }
        }

        lock.unlock();

        // Wake the entire cache since we know it's full
        wakeCache.wakeAll();

        for (WaitEntry* next; wake; wake = next)
        {
            next = wake->next;
            auto val = WakeCache::fromWaitEntry(*wake);

            // Clear the wait bit so that only the wake bit is set. No accesses to `wake` are allowed after this since
            // the waiting thread is free to destroy it. Release to synchronize-with spin-waiting on the wait bit.
            wake->wakeup.store(WaitEntry::kNotifyBit, std::memory_order_release);
            // TSAN needs to be manually informed of the release
            __tsan_release(&wake->wakeup);

            WakeCache::doWake(val);
        }
    }

public:
    static void notify_n(void* addr, size_t n) noexcept
    {
        if (CARB_UNLIKELY(n == 0))
        {
            return;
        }

        WaitBucket& b = WaitBucket::bucket(addr);

        // Read empty state with full fence to avoid locking
        if (b.appearsEmpty())
            return;

        // It is much faster overall to not set kWaitBit and force the woken threads to wait until we're clear of their
        // WaitEntry, so keep a local cache of addresses to wake here that don't require a WaitEntry.
        // Note that we do retain a pointer to the std::atomic_uint32_t *contained in* the WaitEntry and tell the
        // underlying OS system to wake by that address, but this is safe as it does not read that memory. The address
        // is used as a lookup to find any waiters that registered with that address. If the memory was quickly reused
        // for a different wait operation, this will cause a spurious wakeup which is allowed, but this should be
        // exceedingly rare.
        // Must be constructed before the lock is taken
        WakeCache wakeCache;

        auto lock = b.lock();
        b.incChangeTracker();
        for (WaitEntry *next, *e = b.head(); e; e = next)
        {
            next = e->next;
            if (e->addr == addr)
            {
                b.remove(e);
                bool nowFull = wakeCache.add(*e);

                // release semantics despite being under the lock because we want add() complete before store.
                // No access to `e` allowed after this store.
                e->wakeup.store(WaitEntry::kNotifyBit, std::memory_order_release);
                // TSAN needs to be manually informed of the release
                __tsan_release(&e->wakeup);

                if (!--n)
                    break;

                if (CARB_UNLIKELY(nowFull))
                {
                    // Cache is full => transition to a list for the rest
                    notify_n_slow(std::move(lock), addr, n, b, next, wakeCache);
                    return;
                }
            }
        }

        // Lock is unlocked (important this happens first), and then wakeCache destructs and issues all of its wakes
    }

    static void notify_all(void* addr) noexcept
    {
        WaitBucket& b = WaitBucket::bucket(addr);

        // Read empty state with full fence to avoid locking
        if (b.appearsEmpty())
            return;

        // It is much faster overall to not set kWaitBit and force the woken threads to wait until we're clear of their
        // WaitEntry, so keep a local cache of addresses to wake here that don't require a WaitEntry.
        // Note that we do retain a pointer to the std::atomic_uint32_t *contained in* the WaitEntry and tell the
        // underlying OS system to wake by that address, but this is safe as it does not read that memory. The address
        // is used as a lookup to find any waiters that registered with that address. If the memory was quickly reused
        // for a different wait operation, this will cause a spurious wakeup which is allowed, but this should be
        // exceedingly rare.
        // Must be constructed before the lock is taken
        WakeCache wakeCache;

        auto lock = b.lock();
        b.incChangeTracker();
        for (WaitEntry *next, *e = b.head(); e; e = next)
        {
            next = e->next;
            if (e->addr == addr)
            {
                b.remove(e);
                bool nowFull = wakeCache.add(*e);

                // release semantics despite being under the lock because we want add() complete before store.
                // No access to `e` allowed after this store.
                e->wakeup.store(WaitEntry::kNotifyBit, std::memory_order_release);
                // TSAN needs to be manually informed of the release
                __tsan_release(&e->wakeup);

                if (CARB_UNLIKELY(nowFull))
                {
                    // Full => transition to a list for the rest of the items
                    notify_all_slow(std::move(lock), addr, b, next, wakeCache);
                    return;
                }
            }
        }

        // Lock is unlocked (important this happens first), and then wakeCache destructs and issues all of its wakes
    }

}; // struct ParkingLot

template <class T, size_t S = sizeof(T)>
class ParkingLotFutex
{
    static_assert(S == 1 || S == 2 || S == 4 || S == 8, "Unsupported size");

public:
    using AtomicType = typename std::atomic<T>;
    using Type = T;
    static void wait(const AtomicType& val, T compare) noexcept
    {
        ParkingLot::wait(val, compare);
    }
    template <class Rep, class Period>
    static bool wait_for(const AtomicType& val, T compare, std::chrono::duration<Rep, Period> duration)
    {
        return ParkingLot::wait_for(val, compare, duration);
    }
    template <class Clock, class Duration>
    static bool wait_until(const AtomicType& val, T compare, std::chrono::time_point<Clock, Duration> time_point)
    {
        return ParkingLot::wait_until(val, compare, time_point);
    }
    static void notify_one(AtomicType& val) noexcept
    {
        ParkingLot::notify_one(std::addressof(val));
    }
    static void notify_n(AtomicType& val, size_t count) noexcept
    {
        ParkingLot::notify_n(std::addressof(val), count);
    }
    static void notify_all(AtomicType& val) noexcept
    {
        ParkingLot::notify_all(std::addressof(val));
    }
};

#undef CARBLOCAL_WIN_USE_THREADID

} // namespace detail
} // namespace thread
} // namespace carb
//! \endcond
