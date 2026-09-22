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
//! @brief Helper interface to retrieve limited CPU info.
#pragma once

#include "ICpuInfo.h"


namespace omni
{
/** Platform and operating system info namespace. */
namespace platforminfo
{

/** Forward declaration of the API layer. */
class ILimitedCpuInfo;

/** Special value indicating that no CPU scheduling quota has been set.  In this case, all
 *  available CPU cores can schedule work at the maximum rate.  This can be returned by
 *  @ref omni::platforminfo::ILimitedCpuInfo::getCoreUsageQuota().
 */
constexpr int32_t kNoQuotaSet = -1;


/** Interface to collect information about the CPUs installed in the calling system.  This
 *  can provide some basic information about the CPU(s) and get access to features that are
 *  supported by them.  The values reported from this interface will reflect any CPU resource
 *  limitations imposed on the system by an external source.  For example, the available CPUs
 *  could be limited in a container, a VM, or by an OS level per-user quota.
 *
 *  This interface has mostly the same set of functions that the @ref omni::platforminfo::ICpuInfo
 *  interface does.  The only difference is in its behavior - it will retrieve the CPU info
 *  _available_ to the calling process under a resource limiting system such as Docker or a
 *  CM instead of the bare metal values.  If no limits are set on the container or VM, this
 *  will fall back to reporting the same bare metal values as @ref omni::platforminfo::ICpuInfo
 *  instead.
 *
 *  Some of the functions of @ref omni::platforminfo::ICpuInfo have been removed here since they
 *  do not make sense in a resource limiting situation.  Some new functions have also been added
 *  to retrieve more specific CPU core limiting information.
 *
 *  @note The CPU information will only be collected once on loading this plugin and cached
 *        for later retrieval.  If the CPU core allocation changes dynamically while the
 *        calling process is still running (and therefore the container is still running),
 *        this change will not be reflected in the returned values.
 */
class ILimitedCpuInfo_abi
    : public omni::core::Inherits<omni::core::IObject, OMNI_TYPE_ID("omni.platforminfo.ILimitedCpuInfo")>
{
protected:
    /** Retrieves the total number of CPU packages installed on the system.
     *
     *  @returns The total number of CPU packages installed in the system.  A CPU package
     *           is a single physical CPU chip that is connected to a physical socket on
     *           the motherboard.
     *
     *  @remarks A system may have multiple CPUs installed if the motherboard supports it.
     *           At least in the Intel (and compatible) case, there are some restrictions
     *           to doing this - all CPUs must be in the same family, share the same core
     *           count, feature set, and bus speed.  Outside of that, the CPUs do not need
     *           to be identical.  Note however that if the OS or container is limiting the
     *           number of available cores, the core count may not match in each package.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getCpuPackageCount_abi() noexcept = 0;

    /** Retrieves an estimate of the total number of physical cores across all CPUs in the system.
     *
     *  @returns An estimate of the total number of physical cores across all available CPUs in
     *           the system.  This includes the sum of all available physical cores on all CPU
     *           packages.  This will not be zero.
     *
     *  @note Because the available CPU cores may be limited in a container or at the OS level,
     *        it is possible that this may be an odd number.  It is also possible that the number
     *        of logical cores may not be an integer multiple of the number of physical cores.
     *        This is expected behavior since the CPU set may have asymmetrically limited the
     *        cores between packages.  It is most reliable to simply use the total number of
     *        logical cores to decide on things like worker thread counts or task load estimates.
     *
     *  @note Since any of the CPU's cores can be assigned to a container or control group, it is
     *        possible that fewer than all of the logical cores in a physical core could be
     *        assigned to the container.  This means that the physial core count can at best be
     *        an estimate.  This is typically just treated as one logical core per physical core
     *        in that case.  For this reason, the number of physical cores may be reported
     *        incorrectly, sometimes even to the point where more physical cores are reported
     *        than the bare metal hardware actually has.  Thus it is most accurate to retrieve
     *        and make decisions based on the logical core count, not the physical core count.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getTotalPhysicalCoreCount_abi() noexcept = 0;

    /** Retrieves the total number of logical cores across all CPUs in the system.
     *
     *  @returns The total number of logical cores across all CPUs in the system.  This includes
     *           the sum of all logical cores on all CPU packages.
     *
     *  @note Because the available CPU cores may be limited in a container or at the OS level,
     *        it is possible that this may be an odd number.  It is also possible that the number
     *        of logical cores may not be an integer multiple of the number of physical cores.
     *        This is expected behavior since the CPU set may have asymmetrically limited the
     *        cores between packages.  It is most reliable to simply use the total number of
     *        logical cores to decide on things like worker thread counts or task load estimates.
     *
     *  @note Also note that because of the way CPU cores can be assigned to VMs or containers,
     *        it may appear that there is only one logical core per physical core even when the
     *        underlying bare metal hardware supports multiple logical cores per physical core.
     *        There is unfortunately no way around this since it has been limited at the OS or
     *        VM level.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getTotalLogicalCoreCount_abi() noexcept = 0;

    /** Checks if a requested feature is supported by the CPU(s) in the system.
     *
     *  @returns `true` if the requested feature is supported.  Returns `false` otherwise.
     *
     *  @remarks See @ref omni::platforminfo::CpuFeature for more information on the features
     *           that can be queried.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual bool isFeatureSupported_abi(CpuFeature feature) noexcept = 0;

    /** Retrieves the friendly name of a CPU in the system.
     *
     *  @param[in] cpuIndex     The zero based index of the CPU package to retrieve the name
     *                          for.  This should be less than the return value of
     *                          @ref omni::platforminfo::ILimitedCpuInfo::getCpuPackageCount().
     *  @returns The friendly name of the requested CPU package.  This string should be suitable
     *           for display to the user.  This will contain a rough outline of the processor
     *           model and architecture.  It may or may not contain the clock speed.
     *
     *  @note This CPU pretty name string will still be retrieved from the CPU itself even if
     *        access to CPU cores has been limited.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual const char* getPrettyName_abi(size_t cpuIndex) noexcept = 0;

    /** Retrieves the identifier of a CPU in the system.
     *
     *  @param[in] cpuIndex     The zero based index of the CPU package to retrieve the identifier
     *                          for.  This should be less than the return value of
     *                          @ref omni::platforminfo::ILimitedCpuInfo::getCpuPackageCount().
     *  @returns The identifier string of the requested CPU package.  This string should be
     *           suitable for display to the user.  This will contain information about the
     *           processor family, vendor, and architecture.
     *
     *  @note This CPU identifier string will still be retrieved from the CPU itself even if
     *        access to CPU cores has been limited.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual const char* getIdentifier_abi(size_t cpuIndex) noexcept = 0;

    /** Retrieves the vendor string for a CPU package in the system.
     *
     *  @param[in] cpuIndex     The zero based index of the CPU package to retrieve the vendor
     *                          for.  This should be less than the return value of
     *                          @ref omni::platforminfo::ILimitedCpuInfo::getCpuPackageCount().
     *  @returns The name of the vendor as reported by the CPU itself.  This may be something
     *           along the lines of "GenuineIntel" or "AuthenticAMD" for x86_64 architectures,
     *           or the name of the CPU implementer for ARM architectures.
     *
     *  @note This CPU vendor string will still be retrieved from the CPU itself even if
     *        access to CPU cores has been limited.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual const char* getVendor_abi(size_t cpuIndex) noexcept = 0;

    /** Retrieves a bit mask for the processor cores in a CPU package in the system.
     *
     *  @param[in] cpuIndex     The zero based index of the CPU package to retrieve the identifier
     *                          for.  This should be less than the return value of
     *                          @ref omni::platforminfo::ILimitedCpuInfo::getCpuPackageCount().
     *  @returns A mask identifying which CPU cores the given CPU covers.  A set bit indicates
     *           a core that belongs to the given CPU.  A 0 bit indicates either a core from
     *           another package or a non-existent core.  This may also be 0 if more than 64
     *           cores are present in the system or they are out of range of a single 64-bit
     *           value.
     *
     *  @note The mask may be 0 if out of range of 64 bits.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual uint64_t getProcessorMask_abi(size_t cpuIndex) noexcept = 0;

    /** Retrieves the effective CPU usage quota.
     *
     *  @returns The effective CPU usage quota.  This is expressed as an estimate of how many
     *           cores the threads of the calling process can effectively be scheduled on.
     *           Note that this may be less than, equal to, or greater than the total logical
     *           core count available to the calling process.
     *
     *  @remarks The CPU usage quota is an estimate of how many cores a process can effectively
     *           use.  However, it does not mean that the process is restricted to only running
     *           on only a specific subset of cores.  Instead it means that the threads of the
     *           process will only be _scheduled_ to run for a portion of the total available
     *           time the CPU has.  On Linux, this is expressed as a ratio of available run
     *           time versus a scheduling period.  The scheduling period is 100000us by default
     *           and the run quota is expressed as the number of microseconds a given process
     *           is able to use out of that period.  For example, a quota of 25000us means that
     *           the process may effectively use 25% of a single core's processing time.  A
     *           value of 275000us means that the process may effectively use 275% of a single
     *           core's processing time (ie: it can effectively use 2.75 cores).  Note that
     *           providing a quota value less than the period (ie: the 25000us example) does
     *           not mean that _only_ one core may be used.  The host OS is still free to
     *           schedule the process' threads in parallel as needed, it just limits the
     *           number of time slices of the CPU's time that it can use over a given period.
     *
     *  @remarks The value returned here is the effective CPU usage quota rounded up or down
     *           to the nearest full core.  This can be used as an estimate of how many CPU
     *           cores the calling process effectively has access to.  Note that the given
     *           quota may still be larger than the total number of logical cores available
     *           to the process.  This can occur in cases where both a CPU quota and a CPU
     *           set are specified for a container.  In this case, the caller will need to
     *           clamp the value to the total number of logical cores as returned from
     *           @ref omni::platforminfo::ILimitedCpuInfo::getTotalLogicalCoreCount().
     *
     *  @thread_safety This call is thread safe.
     */
    virtual int32_t getCoreUsageQuota_abi() noexcept = 0;

    /** Retrieves the set of CPU cores available to the calling process.
     *
     *  @param[out] cores   Receives the list of core indices for all CPU cores available to
     *                      the calling process.  If no CPU set has been defined that limits
     *                      access to specific cores, this will simply return a list of all
     *                      core indices on the bare metal CPU.  This may not be `nullptr`.
     *                      This buffer should be large enough to hold as many core indices as
     *                      omni::platforminfo::ILimitedCpuInfo::getTotalLogicalCoreCount().
     *
     *  @param[in] maxCores The maximum number of CPU core indices that can fit in @p cores.
     *
     *  @returns `true` if the CPU core list is successfully returned.  Returns `false` if
     *           the @p cores buffer is too small to hold the full core indices list.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual bool getCoreSetList_abi(OMNI_ATTR("in, out, count=maxCores, not_null") int32_t* cores,
                                    size_t maxCores) noexcept = 0;

    /** Retrieves the physical CPU core count for a specific CPU package.
     *
     *  @param[in] cpuIndex     The CPU package to retrieve the physical core count for.  This
     *                          must be less than the value returned from
     *                          @ref omni::platforminfo::ILimitedCpuInfo::getCpuPackageCount().
     *  @returns The estimated number of physical CPU cores on the requested CPU package.  Note
     *           that this is only an estimate since logical cores may be assigned asymmetrically
     *           in a container or VM.  This is estimated using the bare metal physical-vs-logical
     *           core multiplier.  It is most accurate to only use the logical core count when
     *           making decisions based off of the CPU core count.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getPhysicalCoreCountForPackage_abi(size_t cpuIndex) noexcept = 0;

    /** Retrieves the logical CPU core count for a specific CPU package.
     *
     *  @param[in] cpuIndex     The CPU package to retrieve the logical core count for.  This
     *                          must be less than the value returned from
     *                          @ref omni::platforminfo::ILimitedCpuInfo::getCpuPackageCount().
     *  @returns The total number of logical CPU cores on the requested CPU package.  This will
     *           never be 0.  Any CPU packages that do not have cores assigned to them in the
     *           limited CPU resource case will be removed.
     *
     *  @thread_safety This call is thread safe.
     */
    virtual size_t getLogicalCoreCountForPackage_abi(size_t cpuIndex) noexcept = 0;
};

} // namespace platforminfo
} // namespace omni

#define OMNI_BIND_INCLUDE_INTERFACE_DECL
#include "ILimitedCpuInfo.gen.h"

/** @copydoc omni::platforminfo::ILimitedCpuInfo_abi */
class omni::platforminfo::ILimitedCpuInfo : public omni::core::Generated<omni::platforminfo::ILimitedCpuInfo_abi>
{
};

#define OMNI_BIND_INCLUDE_INTERFACE_IMPL
#include "ILimitedCpuInfo.gen.h"
