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
//! @brief Futex implementation details.
#pragma once

#include "NativeFutex.h"
#include "LowLevelLock.h"
#include "../../cpp/Bit.h"
#include "../../detail/TSan.h"

#include <atomic>

#ifndef DOXYGEN_BUILD
#    if CARB_PLATFORM_WINDOWS
// Windows WaitOnAddress() supports 1, 2, 4 or 8 bytes, so it doesn't need to use ParkingLot. For testing ParkingLot
// or for specific modules this can be enabled though.
#        ifndef CARB_USE_PARKINGLOT
#            define CARB_USE_PARKINGLOT 0
#        endif
#    elif CARB_PLATFORM_LINUX
#        define CARB_USE_PARKINGLOT 1 // Linux and macOS only support 4 byte futex so they must use the ParkingLot
#    else
CARB_UNSUPPORTED_PLATFORM()
#    endif
#endif

#if CARB_USE_PARKINGLOT
#    include "ParkingLot.h"
#endif

//! \cond DEV
namespace carb
{
namespace thread
{
namespace detail
{

// Futex types that must use the ParkingLot
#if CARB_USE_PARKINGLOT
template <class T, size_t S = sizeof(T)>
using Futex = ParkingLotFutex<T, S>;
#elif CARB_PLATFORM_WINDOWS
// If Windows is not using the ParkingLot it can use the Windows-specific futex
template <class T, size_t S = sizeof(T)>
using Futex = WindowsFutex<T, S>;
#else
CARB_UNSUPPORTED_PLATFORM()
#endif

} // namespace detail
} // namespace thread
} // namespace carb
//! \endcond
