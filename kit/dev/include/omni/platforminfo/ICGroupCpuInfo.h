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
//! @brief Helper interface to retrieve cgroup CPU info.
#pragma once

#include "ILimitedCpuInfo.h" // for `kNoQuotaSet` constant.


namespace omni
{
/** Platform and operating system info namespace. */
namespace platforminfo
{

/** Forward declaration of the API layer. */
class ICGroupCpuInfo;


/** @brief Interface to collect CPU information directly from Linux's root level control group.
 *
 *  Interface to collect Linux control group ("cgroup") information about the CPU(s) installed
 *  in the calling system.  This can provide some basic information about the CPU core count,
 *  scheduling quotas, and active CPU sets.  The values reported from this interface will reflect
 *  any CPU resource limitations imposed on the system by an external source.  For example, the
 *  available CPUs could be limited in a container, a VM, or by an OS level per-user quota.
 *
 *  This interface is intended to be used to directly retrieve the cgroup information about the
 *  CPU if set.  If a particular value is not set (ie: logical core count, CPU set, scheduling
 *  quota), the corresponding function will fail allowing the caller to fall back to another
 *  information source such as the bare metal values.
 *
 *  This interface is available on Windows for convenience, but all functions will simply fail
 *  when called.  This makes it easier to call into the interface without needing additional
 *  `nullptr` checks.
 *
 *  @note The CPU information will only be collected once on loading this plugin and cached
 *        for later retrieval.  If the CPU core allocation changes dynamically while the
 *        calling process is still running (and therefore the container is still running),
 *        this change will not be reflected in the returned values.
 *
 *  @note This interface supports cgroup versions 1 and 2 on Linux.
 */
class ICGroupCpuInfo_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.platforminfo.ICGroupCpuInfo")>
{
protected:
    /** Retrieves the total number of logical cores in the active CPU set.
     *
     *  @returns The total number of logical cores in the active CPU set if defined.  This
     *           includes the sum of all available logical cores on all CPU packages.  Returns
     *           0 if no CPU set has been defined.  In this case, all CPU cores will be available
     *           to the calling process but scheduling time may be limited.
     *
     *  @remarks This retrieves the total number of logical cores in the active CPU set.
     *           Depending on the cgroup version that is supported in the system, this value
     *           can come from either one of the following files in this priority order:
     *             * `/sys/fs/cgroup/cpuset.cpus.effective` (v2)
     *             * `/sys/fs/cgroup/cpuset.cpus` (v2)
     *             * `/sys/fs/cgroup/cpuset/cpuset.effective_cpus` (v1)
     *             * `/sys/fs/cgroup/cpuset/cpuset.cpus` (v1)
     *
     *  @note Because the available CPU cores may be limited in a container or at the OS level,
     *        it is possible that this may be an odd number.  It is also possible that the number
     *        of logical cores may not be an integer multiple of the number of physical cores.
     *        This is expected behavior since the CPU set may have asymmetrically limited the
     *        cores between packages.  It is most reliable to simply use the total number of
     *        logical cores to decide on things like worker thread counts or task load estimates.
     *
     *  @note A CPU set may be defined in the cgroup even in a local bare metal situation on
     *        Linux.  In these cases, the CPU set is often the same as the bare metal CPU
     *        info.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getCpuSetLogicalCoreCount_abi() const noexcept = 0;

    /** Retrieves the effective CPU scheduling quota.
     *
     *  @returns The effective CPU scheduling quota.  This is expressed as an estimate of how many
     *           cores the threads of the calling process can effectively be scheduled on.  Note
     *           that this may be less than, equal to, or greater than the total logical core
     *           count available to the calling process.  Returns @ref omni::platforminfo::kNoQuotaSet
     *           if no CPU scheduling quota has been set.  Note that fractional number of cores
     *           may be returned here.  See remarks below for how to interpret these values.
     *
     *  @remarks The CPU scheduling quota is an estimate of how many cores a process can
     *           effectively use.  However, it does not mean that the process' threads are
     *           restricted to only running on only a specific subset of cores.  Instead it
     *           means that the threads of the process will only be _scheduled_ to run for a
     *           portion of the total available time the CPU has.  On Linux, this is expressed
     *           as a ratio of available run time versus a scheduling period.  The scheduling
     *           period is 100000us by default and the run quota is expressed as the number of
     *           microseconds a given process is able to use out of that period.  For example,
     *           a quota of 25000us means that the process may effectively use 25% of a single
     *           core's processing time.  A value of 275000us means that the process may
     *           effectively use 275% of a single core's processing time (ie: it can effectively
     *           use 2.75 cores).  Note that providing a quota value less than the period (ie:
     *           the 25000us example) does not mean that _only_ one core may be used.  The host
     *           OS is still free to schedule the process' threads in parallel as needed, it
     *           just limits the number of time slices of the CPU's time that it can use over
     *           a given period.
     *
     *  @remarks The value returned here is the effective CPU scheduling quota exactly as given
     *           in the root cgroup.  If a fractional CPU quota is given, that fractional value
     *           will be returned.  It is the caller's responsibility to round the value up or
     *           down to the nearest full core if it is to be treated as a core count.  This
     *           can be used as an estimate of how many CPU cores the calling process effectively
     *           has access to.  Note that the given quota may still be larger than the total
     *           number of logical cores available to the process.  This can occur in cases
     *           where both a CPU quota and a CPU set are specified for a container.  In this
     *           case, the caller will need to clamp the value to the total number of logical
     *           cores.
     *
     *  @remarks Depending on the cgroup version supported in the system, this value comes
     *           from the following files:
     *             * `/sys/fs/cgroup/cpu.max` (v2)
     *             * `/sys/fs/cgroup/cpu/cpu.cfs_quota_us` and `/sys/fs/cgroup/cpu/cpu.cfs_period_us`
     *               (v1)
     *
     *  @thread_safety This call is thread safe.
     */
    virtual float getCoreUsageQuota_abi() const noexcept = 0;

    /** Retrieves the set of CPU cores available to the calling process.
     *
     *  @param[out] cores   Receives the list of core indices for all CPU cores available to
     *                      the calling process.  If no CPU set has been defined that limits
     *                      access to specific cores, this will simply return 0.  This may
     *                      be `nullptr` if the list of core indices is not needed.  In this
     *                      case the total required size of the buffer will be returned if a
     *                      CPU set is defined.
     *
     *  @param[in] maxCores The maximum number of CPU core indices that can fit in @p cores.
     *                      This may be 0 to retrieve the required size of the buffer.
     *
     *  @returns The total number of CPU core indices written to the buffer @p cores if a
     *           CPU set has been defined in the cgroup and @p cores is non-nullptr.  If
     *           @p cores is `nullptr` the required size of the buffer in indices is returned.
     *           If the buffer is not large enough to hold the full CPU set indices, as many
     *           indices as will fit are written to the buffer and the required size of the
     *           buffer is returned.  If no CPU set has been defined, 0 is returned.
     *
     *  @remarks This retrieves the indices of the logical cores in the active CPU set.
     *           Depending on the cgroup version that is supported in the system, this value
     *           can come from either one of the following files in this priority order:
     *
     *             * `/sys/fs/cgroup/cpuset.cpus.effective` (v2)
     *             * `/sys/fs/cgroup/cpuset.cpus` (v2)
     *             * `/sys/fs/cgroup/cpuset/cpuset.effective_cpus` (v1)
     *             * `/sys/fs/cgroup/cpuset/cpuset.cpus` (v1)
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getCoreSetList_abi(OMNI_ATTR("in, out, count=maxCores, not_null") int32_t* cores,
                                      size_t maxCores) const noexcept = 0;
};

} // namespace platforminfo
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "ICGroupCpuInfo.gen.h"

/** @copydoc omni::platforminfo::ICGroupCpuInfo_abi */
class omni::platforminfo::ICGroupCpuInfo : public omni::core::Generated<omni::platforminfo::ICGroupCpuInfo_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "ICGroupCpuInfo.gen.h"
