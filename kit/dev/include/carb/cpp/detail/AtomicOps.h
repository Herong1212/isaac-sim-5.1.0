// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief Implementation detail
#pragma once

#include "../../Defines.h"

#include <atomic>

//! \cond DEV

namespace carb
{
namespace cpp
{
namespace detail
{

template <class T, size_t S = sizeof(T)>
struct AtomicOps;

template <class T>
struct AtomicOps<T, 4>
{
    static_assert(sizeof(T) == 4, "Invalid assumption");
    static_assert(std::is_integral<T>::value, "Must be an integral type");
    using NativeType = T;
    using UnderlyingType = int32_t;
    using AtomicType = std::atomic<T>;

    static bool test_bit_and_set(AtomicType& val,
                                 const unsigned bit,
                                 const std::memory_order order = std::memory_order_seq_cst) noexcept;
    static bool test_bit_and_reset(AtomicType& val,
                                   const unsigned bit,
                                   const std::memory_order order = std::memory_order_seq_cst) noexcept;
};

template <class T>
struct AtomicOps<T, 8>
{
    static_assert(sizeof(T) == 8, "Invalid assumption");
    static_assert(std::is_integral<T>::value, "Must be an integral type");
    using NativeType = T;
    using UnderlyingType = int64_t;
    using AtomicType = std::atomic<T>;

    static bool test_bit_and_set(AtomicType& val,
                                 const unsigned bit,
                                 const std::memory_order order = std::memory_order_seq_cst) noexcept;
    static bool test_bit_and_reset(AtomicType& val,
                                   const unsigned bit,
                                   const std::memory_order order = std::memory_order_seq_cst) noexcept;
};

// x86-64 specializations to use bts/btr instructions
#if CARB_PLATFORM_WINDOWS && CARB_X86_64
extern "C" unsigned char _interlockedbittestandset(long volatile*, long);
#    pragma intrinsic(_interlockedbittestandset)
extern "C" unsigned char _interlockedbittestandset64(__int64 volatile*, __int64);
#    pragma intrinsic(_interlockedbittestandset64)
extern "C" unsigned char _interlockedbittestandreset(long volatile*, long);
#    pragma intrinsic(_interlockedbittestandreset)
extern "C" unsigned char _interlockedbittestandreset64(__int64 volatile*, __int64);
#    pragma intrinsic(_interlockedbittestandreset64)

template <class T>
bool AtomicOps<T, 4>::test_bit_and_set(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    return !!_interlockedbittestandset(reinterpret_cast<long*>(&val), bit);
}

template <class T>
bool AtomicOps<T, 4>::test_bit_and_reset(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    return !!_interlockedbittestandreset(reinterpret_cast<long*>(&val), bit);
}

template <class T>
bool AtomicOps<T, 8>::test_bit_and_set(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    return !!_interlockedbittestandset64(reinterpret_cast<__int64*>(&val), bit);
}

template <class T>
bool AtomicOps<T, 8>::test_bit_and_reset(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    return !!_interlockedbittestandreset64(reinterpret_cast<__int64*>(&val), bit);
}
#elif CARB_COMPILER_GNUC && CARB_X86_64 && !CARB_TSAN_ENABLED
template <class T>
bool AtomicOps<T, 4>::test_bit_and_set(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    bool out;
    __asm__ volatile("lock; btsl %2, %1; setc %0" : "=r"(out), "+m"(*(&val)) : "Ir"((bit)) : "cc");
    return out;
}

template <class T>
bool AtomicOps<T, 4>::test_bit_and_reset(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    bool out;
    __asm__ volatile("lock; btrl %2, %1; setc %0" : "=r"(out), "+m"(*(&val)) : "Ir"((bit)) : "cc");
    return out;
}

template <class T>
bool AtomicOps<T, 8>::test_bit_and_set(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    bool out;
    __asm__ volatile("lock; btsq %2, %1; setc %0" : "=r"(out), "+m"(*(&val)) : "Jr"((uint64_t)(bit)) : "cc");
    return out;
}

template <class T>
bool AtomicOps<T, 8>::test_bit_and_reset(AtomicType& val, const unsigned bit, const std::memory_order) noexcept
{
    // Effectively seq_cst
    bool out;
    __asm__ volatile("lock; btrq %2, %1; setc %0" : "=r"(out), "+m"(*(&val)) : "Jr"((uint64_t)(bit)) : "cc");
    return out;
}
#else // Fall back to slower existing atomics
template <class T>
bool AtomicOps<T, 4>::test_bit_and_set(AtomicType& val, const unsigned bit, const std::memory_order order) noexcept
{
    const NativeType mask = NativeType(1) << bit;
    return !!(val.fetch_or(mask, order) & mask);
}

template <class T>
bool AtomicOps<T, 4>::test_bit_and_reset(AtomicType& val, const unsigned bit, const std::memory_order order) noexcept
{
    const NativeType mask = NativeType(1) << bit;
    return !!(val.fetch_and(~mask, order) & mask);
}

template <class T>
bool AtomicOps<T, 8>::test_bit_and_set(AtomicType& val, const unsigned bit, const std::memory_order order) noexcept
{
    const NativeType mask = NativeType(1) << bit;
    return !!(val.fetch_or(mask, order) & mask);
}

template <class T>
bool AtomicOps<T, 8>::test_bit_and_reset(AtomicType& val, const unsigned bit, const std::memory_order order) noexcept
{
    const NativeType mask = NativeType(1) << bit;
    return !!(val.fetch_and(~mask, order) & mask);
}
#endif

} // namespace detail
} // namespace cpp
} // namespace carb

//! \endcond
