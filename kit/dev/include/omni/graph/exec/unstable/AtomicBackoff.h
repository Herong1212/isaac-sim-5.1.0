// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! @file AtomicBackoff.h
//!
//! @brief Defines @ref omni::graph::exec::unstable::AtomicBackoff.
#pragma once

#include <carb/Defines.h>

#if CARB_X86_64
#    include <immintrin.h>
#endif

#include <thread>

namespace omni
{
namespace graph
{
namespace exec
{
namespace unstable
{

//! Exponential backoff pattern for waiting with a cap number of pauses
//!
//! This class implements exponential backoff, where each call to pause will
//! cause busy waiting and increment the number of iterations for next pause call.
//! All of this is cap with a maximum limit of pause calls after which waiting
//! is considered long and switches to yield.
//!
//! This class is useful when we expect short waits and would like to prevent
//! yielding the compute resources for this short period of time.
//!
//! This object is not ABI-safe.
//!
//! @thread_safety Methods are not thread safe unless otherwise noted.
class AtomicBackoff
{
public:
    //! Default constructor
    constexpr AtomicBackoff() noexcept
    {
    }

    // No use in allowing copy and assignment operators for this class
    AtomicBackoff(const AtomicBackoff&) = delete;
    AtomicBackoff& operator=(const AtomicBackoff&) = delete;

    //! Pause execution for a short period of time.
    //!
    //! Use exponential backoff pattern and a upper wait cap to select between busy waiting and yielding.
    //!
    //! @thread_safety This method is not thread safe.
    void pause() noexcept
    {
        if (m_loopCount <= kLoopBeforeYield)
        {
            auto loop = m_loopCount;
            while (loop-- > 0)
            {
#if CARB_X86_64
                _mm_pause();
#elif CARB_AARCH64
                // based on TBB machine_pause and BOOST pause.hpp
                __asm__ __volatile__("yield" ::: "memory");
#endif
            }

            m_loopCount *= 2;
        }
        else
        {
            std::this_thread::yield();
        }
    }

    //! Clear wait counter.
    //!
    //! @thread_safety This method is not thread safe.
    void reset() noexcept
    {
        m_loopCount = 1;
    }

private:
    //! Upper cap for busy waiting. Pass this count the pause call will always yield until reset method is called.
    //!
    //! The number must be power of two and is approximately equal to number of pause instructions it would take
    //! to do a context switch.
    enum : int
    {
        kLoopBeforeYield = 16
    };

    //! Next number of busy loop iterations. Incremented exponentially and cap at kLoopBeforeYield
    int m_loopCount{ 1 };
};

} // namespace unstable
} // namespace exec
} // namespace graph
} // namespace omni
