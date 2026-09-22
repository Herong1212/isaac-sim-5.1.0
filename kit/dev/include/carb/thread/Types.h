// SPDX-FileCopyrightText: Copyright (c) 2019-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Carbonite thread types.
#pragma once

#include "../process/Types.h"

#include <vector>

namespace carb::thread
{

/** The type for a process ID. */
using ProcessId = process::ProcessId;

/** The type for a thread ID. */
using ThreadId = uint32_t;

/**
 * Each entry in the vector is a bitmask for a set of CPUs.
 *
 * On Windows each entry corresponds to a Processor Group.
 *
 * On Linux the entries are contiguous, like cpu_set_t.
 */
using CpuMaskVector = std::vector<uint64_t>;

#if CARB_PLATFORM_WINDOWS
static_assert(sizeof(ThreadId) >= sizeof(DWORD), "ThreadId type is too small");
#elif CARB_POSIX
static_assert(sizeof(ThreadId) >= sizeof(pid_t), "ThreadId type is too small");
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

/** The printf format macro to print a thread ID. */
#define OMNI_PRItid PRIu32

/** The printf format macro to print a thread ID in hexadecimal. */
#define OMNI_PRIxtid PRIx32

#if CARB_PLATFORM_WINDOWS
//! The definition of a NativeHandleType. On Windows this is a `HANDLE` and on Linux it is a `pthread_t`.
using NativeHandleType = HANDLE;
#elif CARB_POSIX
//! The definition of a NativeHandleType. On Windows this is a `HANDLE` and on Linux it is a `pthread_t`.
using NativeHandleType = pthread_t;

#else
CARB_UNSUPPORTED_PLATFORM();
#endif

} // namespace carb::thread
