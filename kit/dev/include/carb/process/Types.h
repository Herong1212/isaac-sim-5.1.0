// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
//! @brief Carbonite process types.
#pragma once

#include "../Defines.h"

#if CARB_PLATFORM_WINDOWS
#    include "../CarbWindows.h"
#elif CARB_POSIX
#    include <sys/types.h>
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

//! Namespace for Carbonite process utilities.
namespace carb::process
{

/** The type for a process ID. */
using ProcessId = uint32_t;

#if CARB_PLATFORM_WINDOWS
static_assert(sizeof(ProcessId) >= sizeof(DWORD), "ProcessId type is too small");
#elif CARB_POSIX
static_assert(sizeof(ProcessId) >= sizeof(pid_t), "ProcessId type is too small");
#else
CARB_UNSUPPORTED_PLATFORM();
#endif

/** The printf format macro to print a process ID. */
#define OMNI_PRIpid PRIu32

/** The printf format macro to print a process ID in hexadecimal. */
#define OMNI_PRIxpid PRIx32

} // namespace carb::process
