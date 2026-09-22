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
//! @brief Implementation detail for `LowLevelMutex`.
#pragma once

#include "../../Defines.h"
#include "../../cpp/Bit.h"
#include "../../cpp/detail/AtomicOps.h"
#include "../../clock/TscClock.h"
#include "../../detail/TSan.h"
#include "NativeFutex.h"

#include <atomic>

//! \cond DEV

#define CARBLOCAL_DEBUG 0
#define CARBLOCAL_WIN_USE_THREADID 1

namespace carb
{
namespace thread
{
namespace detail
{

inline int initCyclesPerPause() noexcept
{
    // TODO: Perhaps have this calculated someday?
    return 1;
}

inline int cyclesPerPause() noexcept
{
    static const int kCyclesPerPause = initCyclesPerPause();
    return kCyclesPerPause;
}

class Backoff
{
public:
    constexpr Backoff() noexcept = default;

    CARB_NOINLINE void backoff() noexcept
    {
        std::atomic_int dummy{ 0 };
        unsigned thisDelay = delay + unsigned(clock::detail::readTsc() & (delay - 1));
        const int kCyclesPerPause = detail::cyclesPerPause();
        for (int i = int(thisDelay) / kCyclesPerPause; i > 0; --i)
        {
            // Waste some time
            (void)dummy.load();
            (void)dummy.load();
            (void)dummy.load();
            CARB_HARDWARE_PAUSE();
        }
        if (delay < (kMaxDelay - 1))
        {
            delay <<= 1; // double it
            CARB_ASSERT(cpp::has_single_bit(delay)); // Always a power of two
        }
    }

private:
    constexpr static unsigned kInitialDelay = 64;
    constexpr static unsigned kMaxDelay = 8192;
    static_assert(cpp::has_single_bit(kInitialDelay), "Must be power of 2");

    unsigned delay = kInitialDelay;
};

class LowLevelLock
{
public:
    CARB_IF_NOT_TSAN(constexpr) LowLevelLock() noexcept
    {
        __tsan_mutex_create(this, __tsan_mutex_not_static);
    }
    ~LowLevelLock()
    {
        __tsan_mutex_destroy(this, __tsan_mutex_not_static);
    }

    void lock() noexcept
    {
        __tsan_mutex_pre_lock(this, 0);
        // If we successfully set the lock bit (was previously unset), we're locked
        CARB_LIKELY_IF(!cpp::detail::AtomicOps<uintptr_t>::test_bit_and_set(m_data, kLockBit, std::memory_order_seq_cst))
        {
            __tsan_mutex_post_lock(this, 0, 0);
            return;
        }

        lock_slow();
        __tsan_mutex_post_lock(this, 0, 0);
    }

    bool try_lock() noexcept
    {
        __tsan_mutex_pre_lock(this, __tsan_mutex_try_lock);
        // If we successfully set the lock bit (was previously unset), we're locked
        bool b = !cpp::detail::AtomicOps<uintptr_t>::test_bit_and_set(m_data, kLockBit, std::memory_order_seq_cst);
        __tsan_mutex_post_lock(this, b ? __tsan_mutex_try_lock : __tsan_mutex_try_lock_failed, 0);
        return b;
    }

    void unlock() noexcept
    {
        __tsan_mutex_pre_unlock(this, 0);
        uintptr_t old = m_data.fetch_sub(kLock, std::memory_order_seq_cst);

        CARB_ASSERT(old & kLock);
        CARB_ASSERT((old & kWaiting) || (old & kPtrMask) == 0);

        // If we have waiters and no one else is waking, try to set the Waking flag and if successful, wake.
        CARB_UNLIKELY_IF((old & (kWaiting | kWaking)) == kWaiting)
        {
            old -= kLock;
            auto newVal = old + kWaking;
            if (m_data.compare_exchange_strong(old, newVal, std::memory_order_acquire, std::memory_order_relaxed))
                wake(newVal);
        }

        __tsan_mutex_post_unlock(this, 0);
    }

    bool is_locked() const noexcept
    {
        return m_data.load(std::memory_order_acquire) & kLock;
    }

private:
    constexpr static int64_t kLockBit = 0;
    constexpr static intptr_t kLock = intptr_t(1) << kLockBit;
    constexpr static uintptr_t kWaiting = 0x2;
    constexpr static int64_t kWakingBit = 2;
    constexpr static uintptr_t kWaking = uintptr_t(1) << kWakingBit;
    constexpr static uintptr_t kPtrMask = uintptr_t(~0x7);

    constexpr static int kSpinCycles = 10200;

    struct WaitBlock
    {
        constexpr static unsigned kSpinningBit = 0;
        constexpr static unsigned kSpinning = 0x1;
        constexpr static unsigned kWakeup = 0x2;

        WaitBlock* next = nullptr;
        WaitBlock* last = nullptr; // pointer to the last item in the list, when optimized
        WaitBlock* prev = nullptr; // pointer to the previous item, when optimized
        std::atomic_uint32_t flags{ kSpinning };
#if CARB_PLATFORM_WINDOWS && CARBLOCAL_WIN_USE_THREADID
        thread::ThreadId threadId{ this_thread::getId() };
#endif
#if CARBLOCAL_DEBUG
        bool signaled = false;
        uintptr_t oldVal;
        uintptr_t newVal;
        LowLevelLock* lock;
#endif
    };
    static_assert(alignof(WaitBlock) > ~kPtrMask, "WaitBlock alignment too low for bit count");

    CARB_NOINLINE void lock_slow() noexcept
    {
        Backoff backoff;
        for (;;)
        {
            uintptr_t oldVal = m_data.load(std::memory_order_acquire);

            // If the lock is already held or there are waiters then we need to wait.
            if (!(oldVal & kLock))
            {
                if (m_data.compare_exchange_strong(oldVal, oldVal + kLock))
                    break;

                // Back-off if there is too much contention.
                backoff.backoff();
                continue;
            }

            WaitBlock waitBlock;

            bool optimize = false;

            uintptr_t newVal;
            if (oldVal & kWaiting)
            {
                // If there are already waiters, add ourself to the list (we become the new head), but we will need
                // optimize.
                waitBlock.last = nullptr;
                waitBlock.next = cpp::bit_cast<WaitBlock*>(oldVal & kPtrMask);
                newVal = cpp::bit_cast<uintptr_t>(&waitBlock) | (oldVal & ~kPtrMask) | kWaiting | kWaking | kLock;
                if (!(oldVal & kWaking))
                    optimize = true;
            }
            else
            {
                waitBlock.last = &waitBlock;
                newVal = cpp::bit_cast<uintptr_t>(&waitBlock) | kWaiting | kLock;
            }

#if CARBLOCAL_DEBUG
            waitBlock.oldVal = oldVal;
            waitBlock.newVal = newVal;
            waitBlock.lock = this;
#endif
            CARB_ASSERT(newVal & kWaiting);
            CARB_ASSERT(oldVal & kLock);
            CARB_ASSERT(newVal & kLock);

            if (!m_data.compare_exchange_strong(oldVal, newVal))
            {
                // Back off if there is contention.
                backoff.backoff();
                continue;
            }

            // Optimize the list if need be
            if (optimize)
                optimize_wait_list(newVal);

            // We will spin for a bit to see if we will get woken without the much more expensive kernel wait.
            const int kCyclesPerPause = detail::cyclesPerPause();
            for (int i = kSpinCycles / kCyclesPerPause; i > 0; --i)
            {
                if (!(waitBlock.flags.load(std::memory_order_acquire) & WaitBlock::kSpinning))
                {
#if CARBLOCAL_DEBUG
                    CARB_CHECK(waitBlock.signaled);
#endif
                    break;
                }
                CARB_HARDWARE_PAUSE();
            }

            // Atomically clear the Spinning flag, and if it was still set then we will wait in the kernel.
            if (cpp::detail::AtomicOps<uint32_t>::test_bit_and_reset(waitBlock.flags, WaitBlock::kSpinningBit))
            {
                do
                {
                    // Only the wakeup flag may be set
                    CARB_ASSERT((waitBlock.flags.load(std::memory_order_relaxed) & ~WaitBlock::kWakeup) == 0);
#if CARB_PLATFORM_WINDOWS && CARBLOCAL_WIN_USE_THREADID
                    thread::detail::threadId_wait(waitBlock.flags);
#else
                    detail::NativeFutex::wait(waitBlock.flags, 0);
#endif
                } while (!(waitBlock.flags.load(std::memory_order_acquire) & WaitBlock::kWakeup));
#if CARBLOCAL_DEBUG
                CARB_CHECK(waitBlock.signaled);
#endif
            }
            // loop and try again
        }
    }

    CARB_NOINLINE void wake(uintptr_t oldVal) noexcept
    {
        WaitBlock* waitBlock;

        for (;;)
        {
            // Both Waiting and Waking flags must be set
            CARB_ASSERT((oldVal & (kWaiting | kWaking)) == (kWaiting | kWaking));

            // No point waking if we're locked
            while (oldVal & kLock)
            {
                const auto newVal = oldVal - kWaking; // clear the waking flag
                CARB_ASSERT(!(newVal & kWaking));
                CARB_ASSERT(newVal & kLock);
                CARB_ASSERT(newVal & kWaiting);
                if (m_data.compare_exchange_strong(oldVal, newVal))
                    return;
                // oldVal was reloaded by the failed cmpxchg
            }

            WaitBlock* firstWaitBlock = waitBlock = cpp::bit_cast<WaitBlock*>(oldVal & kPtrMask);
            WaitBlock* prevWaitBlock;

            // If optimize was aborted then we need to do it here.
            for (;;)
            {
                if (auto nextWaitBlock = waitBlock->last)
                {
                    waitBlock = nextWaitBlock;
                    break;
                }

                prevWaitBlock = waitBlock;
                waitBlock = waitBlock->next;
                waitBlock->prev = prevWaitBlock;
            }

            if ((prevWaitBlock = waitBlock->prev) != nullptr)
            {
                // Pop the last waiter, but there are other waiters.
                firstWaitBlock->last = prevWaitBlock;

                waitBlock->prev = nullptr;

                CARB_ASSERT(firstWaitBlock != waitBlock);
                CARB_ASSERT(m_data.load(std::memory_order_relaxed) & kWaiting);

                cpp::detail::AtomicOps<uintptr_t>::test_bit_and_reset(m_data, kWakingBit, std::memory_order_release);
                break;
            }
            else
            {
                // Current waiter is the only waiter, so clear everything.
                CARB_ASSERT(!(oldVal & kLock));
                if (m_data.compare_exchange_strong(oldVal, 0))
                    break;
                // oldVal was reloaded by the failed cmpxchg
            }
        }

        __tsan_mutex_pre_signal(this, 0);
#if CARBLOCAL_DEBUG
        CARB_CHECK(!waitBlock->signaled);
        waitBlock->signaled = true;
#endif

#if CARB_PLATFORM_WINDOWS && CARBLOCAL_WIN_USE_THREADID
        // `waitBlock` may not be accessed once kWakeup is set as the waiting thread may destroy it, so read this here.
        auto threadId = waitBlock->threadId;
#endif

        // Simultaneously try to clear the spinning flag and set the wakeup flag.
        uint32_t prevFlags = waitBlock->flags.exchange(WaitBlock::kWakeup);
        CARB_ASSERT((prevFlags & ~WaitBlock::kSpinning) == 0);
        if (!(prevFlags & WaitBlock::kSpinning))
        {
            // If the Spinning flag was already cleared by the waiting thread we need to wake the thread.
            // If we cleared the Spinning flag, the thread will not wait.
#if CARB_PLATFORM_WINDOWS && CARBLOCAL_WIN_USE_THREADID
            thread::detail::threadId_wake(threadId);
#else
            detail::NativeFutex::notify_one(waitBlock->flags); // Note that this does not access waitBlock
#endif
        }
        __tsan_mutex_post_signal(this, 0);
    }

    void optimize_wait_list(uintptr_t oldVal) noexcept
    {
        // Optimization in this context finds the 'last' entry and writes it to the first entry (the one referenced in
        // the pointer bits of m_data) since we want to wake threads in reverse order (wake oldest waiter first). It
        // also assigns all of the 'prev' pointers that it encounters so that the list can be walked backwards.
        // Optimization is optional since wake() will essentially perform the same actions, but it makes sense to defer
        // the work to the thread that is about to wait rather than the thread that will be waking.
        for (;;)
        {
            // If not locked, wake the list rather than optimize
            if (!(oldVal & kLock))
            {
                wake(oldVal);
                break;
            }

            auto firstWaitBlock = cpp::bit_cast<WaitBlock*>(oldVal & kPtrMask);

            auto waitBlock = firstWaitBlock;
            for (;;)
            {
                if (auto nextWaitBlock = waitBlock->last)
                {
                    firstWaitBlock->last = nextWaitBlock;
                    break;
                }

                auto prevWaitBlock = waitBlock;
                waitBlock = waitBlock->next;
                waitBlock->prev = prevWaitBlock;
            }

            uintptr_t newVal = oldVal - kWaking;
            CARB_ASSERT(newVal & kLock);
            CARB_ASSERT(!(newVal & kWaking));
            if (m_data.compare_exchange_strong(oldVal, newVal))
                break;
            // oldVal was reloaded by failed cmpxchg, try again
        }
    }

    // This value has packed into it three control bits, plus an optional pointer to a list of WaitBlock objects.
    // bit 0: locked state (kLock above)
    // bit 1: waiting state (kWaiting above)
    // bit 2: waking state (kWaking above)
    // The remainder of the bits are used as the WaitBlock pointer, which may be 0s if nothing is waiting.
    std::atomic_uintptr_t m_data{ 0 };
};

} // namespace detail
} // namespace thread
} // namespace carb

//! \endcond

#undef CARBLOCAL_DEBUG
#undef CARBLOCAL_WIN_USE_THREADID
