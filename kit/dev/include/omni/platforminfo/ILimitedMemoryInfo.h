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
//! @brief Helper interface to retrieve memory info.
#pragma once

#include "../core/IObject.h"


namespace omni
{
/** Platform and operating system info namespace. */
namespace platforminfo
{

/** Forward declaration of the ILimitedMemoryInfo API object. */
class ILimitedMemoryInfo;

/** Interface to collect and retrieve information about memory installed in the system.  The
 *  values reported from this interface will reflect any memory limitations imposed on the
 *  system by an external source.  For example, the system memory could be limited in a container,
 *  a VM, or by an OS level per-user quota.
 *
 *  This interface has the same set of functions that the @ref omni::platforminfo::IMemoryInfo
 *  interface does.  The only difference is in its behavior - it will retrieve the memory values
 *  _available_ to the calling process under a resource limiting system such as Docker or a VM
 *  instead of the bare metal values.  If no limits are set on the container or VM, this will
 *  fall back to reporting the same bare metal values as @ref omni::platforminfo::IMemoryInfo
 *  instead.
 */
class ILimitedMemoryInfo_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.platforminfo.ILimitedMemoryInfo")>
{
protected:
    /** Retrieves the maximum RAM accessible by the calling user.
     *
     *  @returns The number of bytes of physical RAM installed in the system.  This value will
     *           not change during the lifetime of the calling process.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getTotalPhysicalMemory_abi() noexcept = 0;

    /** Retrieves the available physical memory in the system.
     *
     *  @returns The number of bytes of physical RAM that is currently available for use by the
     *           operating system.  Note that this is not a measure of how much memory is
     *           available to the calling process, but rather for the entire system.
     *
     *  @thread_safety This call is thread safe.  However, two consecutive or concurrent calls
     *                 are unlikely to return the same value.
     */
    virtual size_t getAvailablePhysicalMemory_abi() noexcept = 0;

    /** Retrieves the total page file space in the system.
     *
     *  @returns The number of bytes of page file space in the system.  The value will not
     *           change during the lifetime of the calling process.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getTotalPageFileMemory_abi() noexcept = 0;

    /** Retrieves the available page file space in the system.
     *
     *  @returns The number of bytes of page file space that is currently available for use
     *           by the operating system.
     *
     *  @thread_safety This call is thread safe.  However, two consecutive or concurrent calls
     *                 are unlikely to return the same value.
     */
    virtual size_t getAvailablePageFileMemory_abi() noexcept = 0;

    /** Retrieves the total memory usage for the calling process.
     *
     *  @returns The number of bytes of memory used by the calling process.  This will not
     *           necessarily be the amount of the process's virtual memory space that is
     *           currently in use, but rather the amount of memory that the OS currently
     *           has wired for this process (ie: the process's working set memory).  It is
     *           possible that the process could have a lot more memory allocated, just
     *           inactive as far as the OS is concerned.
     *
     *  @thread_safety This call is thread safe.  However, two consecutive calls are unlikely
     *                 to return the same value.
     */
    virtual size_t getProcessMemoryUsage_abi() noexcept = 0;

    /** Retrieves the peak memory usage of the calling process.
     *
     *  @returns The maximum number of bytes of memory used by the calling process.  This will
     *           not necessarily be the maximum amount of the process's virtual memory space that
     *           was ever allocated, but rather the maximum amount of memory that the OS ever had
     *           wired for the process (ie: the process's working set memory).  It is possible
     *           that the process could have had a lot more memory allocated, just inactive as
     *           far as the OS is concerned.
     */
    virtual size_t getProcessPeakMemoryUsage_abi() noexcept = 0;
};

} // namespace platforminfo
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "ILimitedMemoryInfo.gen.h"

/** @copydoc omni::platforminfo::ILimitedMemoryInfo_abi */
class omni::platforminfo::ILimitedMemoryInfo : public omni::core::Generated<omni::platforminfo::ILimitedMemoryInfo_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "ILimitedMemoryInfo.gen.h"
