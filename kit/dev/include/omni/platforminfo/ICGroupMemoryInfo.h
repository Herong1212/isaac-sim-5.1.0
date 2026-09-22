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
//! @brief Helper interface to retrieve cgroup memory info.
#pragma once

#include "../core/IObject.h"
#include "../../carb/cpp/Optional.h"


namespace omni
{
/** Platform and operating system info namespace. */
namespace platforminfo
{

/** Forward declaration of the ICGroupMemoryInfo API object. */
class ICGroupMemoryInfo;

/** @brief Interface to collect memory information directly from Linux's root control group.
 *
 *  Interface to collect and retrieve information about cgroup limited memory installed in the
 *  system.  The values reported from this interface will reflect any memory limitations imposed
 *  on the system by an external source.  For example, the system memory could be limited in a
 *  container, a VM, or by an OS level per-user quota.
 *
 *  This interface is intended to be used to directly retrieve the cgroup information about the
 *  system memory if set.  If a particular value is not set in the cgroup (ie: memory limit,
 *  swap limit, etc), the corresponding function will fail allowing the caller to fall back to
 *  another information source such as the bare metal values.
 *
 *  This interface is available on Windows for convenience, but all functions will simply fail
 *  when called.  This makes it easier to call into the interface without needing additional
 *  `nullptr` checks.
 *
 *  @note This interface supports cgroup versions 1 and 2 on Linux.
 */
class ICGroupMemoryInfo_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.platforminfo.ICGroupMemoryInfo")>
{
protected:
    /** Retrieves the maximum RAM accessible by the calling process.
     *
     *  @param[out] bytes   Receives the number of bytes of physical RAM installed in the system
     *                      and allowed for use by the calling process.  This value will not
     *                      change during the lifetime of the calling process and can be safely
     *                      cached.  Receives 0 if no memory limit is set.  This may not be
     *                      `nullptr`.
     *
     *  @returns `true` if a memory limit is set in the cgroup and that value is retrieved.
     *           Returns `false` if no memory limit is set in the cgroup.  In this case, the
     *           bare metal physical memory limit should be used instead.
     *
     *  @remarks This retrieves the maximum RAM that the calling process is allowed to access
     *           in a limited resource situation.  Depending on the cgroup version that is
     *           supported in the system, this value either comes from the file
     *           `/sys/fs/cgroup/memory.max` (v2) or `/sys/fs/cgroup/memory/memory.limit_in_bytes`
     *           (v1).
     *
     *  @thread_safety This call is thread safe.
     */
    virtual bool getTotalPhysicalMemory_abi(OMNI_ATTR("out") size_t& bytes) const noexcept = 0;

    /** Retrieves the available allowed physical memory in the system.
     *
     *  @param[out] bytes   Receives the number of bytes of physical memory that is currently
     *                      available and accessible for use by the operating system.  Note
     *                      that this is not a measure of how much memory is available to the
     *                      calling process, but rather for the entire system.  This value will
     *                      reflect the amount of memory available for the given cgroup memory
     *                      limit.  Receives 0 if no memory limit is set.  This may not be
     *                      `nullptr`.
     *
     *  @returns `true` if a memory limit is set and the available memory amount was retrieved
     *           successfully.  Returns `false` if no memory limit is set.
     *
     *  @remarks This retrieves the available RAM that the calling process is allowed to access
     *           in a limited resource situation.  Depending on the cgroup version that is
     *           supported in the system, this value either comes from the file
     *           `/sys/fs/cgroup/memory.current` (v2) or `/sys/fs/cgroup/memory/memory.usage_in_bytes`
     *           (v1).
     *
     *  @thread_safety This call is thread safe.  However, two consecutive or concurrent calls
     *                 are unlikely to return the same value.
     */
    virtual bool getAvailablePhysicalMemory_abi(OMNI_ATTR("out") size_t& bytes) const noexcept = 0;

    /** Retrieves the total accessible page file space in the system.
     *
     *  @param[out] bytes   Receives the number of bytes of page file space in the system.  The
     *                      value will not change during the lifetime of the calling process and
     *                      can be safely cached.  Receives 0 if no swap space limit is set in
     *                      the cgroup.  This may not be `nullptr`.
     *
     *  @returns `true` if a swap space limit has been set in the cgroup and is successfully
     *           retrieved.  Returns `false` if no swap space limit is set in the cgroup.
     *
     *  @remarks This retrieves the total accessible page file space in a limited system
     *           resource situation.  This value is only available on systems that support
     *           cgroup v2 from the file `/sys/fs/cgroup/memory.swap.max`.  Swap space
     *           limitations are not supported on cgroup v1 as a lone value.  It is only
     *           available as a combined swap plus memory value.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual bool getTotalPageFileMemory_abi(OMNI_ATTR("out") size_t& bytes) const noexcept = 0;

    /** Retrieves the available allowed page file space in the system.
     *
     *  @param[out] bytes   Receives the number of bytes of page file space that is currently
     *                      available for use by the operating system if a swap space limit
     *                      is set in the cgroup.  Receives 0 if no swap space limit is set
     *                      in the cgroup.  This may not be `nullptr`.
     *
     *  @returns `true` if a swap space limit is set and the available swap space memory amount
     *           was retrieved successfully.  Returns `false` if no swap space limit is set.
     *
     *  @remarks This retrieves the available page file space in a limited system resource
     *           situation.  Depending on the cgroup version that is supported in the system,
     *           this value either comes from the file `/sys/fs/cgroup/memory.swap.current`
     *           (v2) or the `swap` field of `/sys/fs/cgroup/memory/memory.stat`.
     *
     *  @thread_safety This call is thread safe.  However, two consecutive or concurrent calls
     *                 are unlikely to return the same value.
     */
    virtual bool getAvailablePageFileMemory_abi(OMNI_ATTR("out") size_t& bytes) const noexcept = 0;
};

} // namespace platforminfo
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "ICGroupMemoryInfo.gen.h"

/** @copydoc omni::platforminfo::ICGroupMemoryInfo_abi */
class omni::platforminfo::ICGroupMemoryInfo : public omni::core::Generated<omni::platforminfo::ICGroupMemoryInfo_abi>
{
public:
    /** Retrieves the maximum RAM accessible by the calling process.
     *
     *  @returns An optional value that indicates both whether the total physical memory byte
     *           count could be retrieved and the value itself.  If the return object contains
     *           a value, it will be the total number of bytes of physical memory allowed in
     *           the control group.  This is the total number of bytes of physical RAM that
     *           the calling process is allowed to use.  This count will not change during the
     *           lifetime of the calling process and can be safely cached.
     *
     *  @remarks This retrieves the maximum RAM that the calling process is allowed to access
     *           in a limited resource situation.  Depending on the cgroup version that is
     *           supported in the system, this value either comes from the file
     *           `/sys/fs/cgroup/memory.max` (v2) or `/sys/fs/cgroup/memory/memory.limit_in_bytes`
     *           (v1).
     *
     *  @thread_safety This call is thread safe.
     */
    inline carb::cpp::optional<size_t> getTotalPhysicalMemoryOpt() const noexcept
    {
        size_t bytes;
        if (getTotalPhysicalMemory_abi(bytes))
            return bytes;
        return {};
    }

    /** Retrieves the available allowed physical memory in the system.
     *
     *  @returns An optional value that indicates both whether the available physical memory byte
     *           count could be retrieved and the value itself.  If the return object contains
     *           a value, it will be the total number of bytes of available physical memory
     *           allowed in the control group.  This is the total number of bytes of available
     *           physical RAM that the calling process is allowed to use still.
     *
     *  @remarks This retrieves the available RAM that the calling process is allowed to access
     *           in a limited resource situation.  Depending on the cgroup version that is
     *           supported in the system, this value either comes from the file
     *           `/sys/fs/cgroup/memory.current` (v2) or `/sys/fs/cgroup/memory/memory.usage_in_bytes`
     *           (v1).
     *
     *  @thread_safety This call is thread safe.  However, two consecutive or concurrent calls
     *                 are unlikely to return the same value.
     */
    inline carb::cpp::optional<size_t> getAvailablePhysicalMemoryOpt() const noexcept
    {
        size_t bytes;
        if (getAvailablePhysicalMemory_abi(bytes))
            return bytes;
        return {};
    }

    /** Retrieves the total accessible page file space in the system.
     *
     *  @returns An optional value that indicates both whether the total page file memory byte
     *           count could be retrieved and the value itself.  If the return object contains a
     *           value, it will be the total number of bytes of page file memory available to the
     *           process in the control group.  If the control group value is present but the page
     *           file is disabled, this will contain 0.
     *
     *  @remarks This retrieves the total accessible page file space in a limited system
     *           resource situation.  This value is only available on systems that support
     *           cgroup v2 from the file `/sys/fs/cgroup/memory.swap.max`.  Swap space
     *           limitations are not supported on cgroup v1 as a lone value.  It is only
     *           available as a combined swap plus memory value.
     *
     *  @thread_safety This call is thread safe.
     */
    inline carb::cpp::optional<size_t> getTotalPageFileMemoryOpt() const noexcept
    {
        size_t bytes;
        if (getTotalPageFileMemory_abi(bytes))
            return bytes;
        return {};
    }

    /** Retrieves the available allowed page file space in the system.
     *
     *  @returns An optional value that indicates both whether the available page file memory byte
     *           count could be retrieved and the value itself.  If the return object contains a
     *           value, it will be the available number of bytes of page file memory available to
     *           the process in the control group.  If the control group value is present but the
     *           page file is disabled, this will contain 0.
     *
     *  @remarks This retrieves the available page file space in a limited system resource
     *           situation.  Depending on the cgroup version that is supported in the system,
     *           this value either comes from the file `/sys/fs/cgroup/memory.swap.current`
     *           (v2) or the `swap` field of `/sys/fs/cgroup/memory/memory.stat`.
     *
     *  @thread_safety This call is thread safe.  However, two consecutive or concurrent calls
     *                 are unlikely to return the same value.
     */
    inline carb::cpp::optional<size_t> getAvailablePageFileMemoryOpt() const noexcept
    {
        size_t bytes;
        if (getAvailablePageFileMemory_abi(bytes))
            return bytes;
        return {};
    }
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "ICGroupMemoryInfo.gen.h"
