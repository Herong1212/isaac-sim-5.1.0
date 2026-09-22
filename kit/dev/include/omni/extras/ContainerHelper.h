// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
/** @file
 *  @brief Helper functions for dealing with docker containers.  These functions will
 *         fail gracefully on Windows or Mac.
 */
#pragma once

#include "../../carb/Defines.h"

#if CARB_PLATFORM_LINUX
#    include <fcntl.h>
#    include <unistd.h>

#    include <string>
#    include <utility>
#    include <vector>
#endif


namespace omni
{
namespace extras
{

#if CARB_PLATFORM_LINUX || defined(DOXYGEN_BUILD)

#    ifndef DOXYGEN_SHOULD_SKIP_THIS
namespace detail
{

/** Reads a single line of text from a file.
 *
 *  @param[in] file     The path to the file to read from.  This may not be `nullptr`.
 *  @param[out] buffer  Receives the read text from the file.
 *  @param[in] len      The maximum number of characters that can fit into @p buffer including
 *                      the null terminator character.
 *  @returns `true` if the line is successfully read from the file.  Returns `false` if the file
 *           could not be found, opened, or read from for any reason.
 *
 *  @remarks This reads a single line of text from a file.  The read string will always be null
 *           terminated so that the data can be used with various string parsing functions.  Any
 *           newlines that are present in the file will be left on the read string.  This can
 *           technically be used to read binary data as well, but there isn't any way to reliably
 *           determine the length of the read data if it contains zeros.
 */
inline bool readLineFromFile(const char* file, char* buffer, size_t len) noexcept
{
    auto fd = ::open(file, O_RDONLY);
    if (fd == -1)
    {
        return false;
    }

    auto size = CARB_RETRY_EINTR(::read(fd, buffer, len - 1));
    ::close(fd);

    if (size <= 0)
    {
        return false;
    }

    buffer[size] = '\0';
    return true;
}

/** Reads a single integer value from the start of a file.
 *
 *  @param[in] file     The path to the file to read from.  This may not be `nullptr`.  This
 *                      file is expected to contain a single base 10 integer value.
 *  @returns The integer value that was parsed from the start of the file if found.  If the
 *           file does not contain an integer value, 0 will be returned.  If the file cannot
 *           be found, opened, or read from for any reason, -1 will be returned.
 */
inline int32_t readIntFromFile(const char* file) noexcept
{
    char buffer[64];

    if (!readLineFromFile(file, buffer, CARB_COUNTOF(buffer)))
    {
        return -1;
    }

    return std::atoi(buffer);
}

/** Descriptor of a CPU quota limiter.  This contains two values - a scheduling quota and a
 *  scheduling period, both values measured in microseconds.  The period is often 100000us
 *  and indicates the length of each scheduling time slice.  The quota value indicates how
 *  much CPU time of each scheduling slice can be allocated.  A quota value that matches the
 *  period value indicates that processes in the container may use 100% of one CPU core.
 *  Values smaller than the period effectively limit the number of cores processes in the
 *  container can be scheduled on.  Values larger than the period can be used to allow multiple
 *  cores to be used.
 */
struct CpuQuota
{
    /** The CPU scheduling quota that is allowed per scheduling period.  This is measured in
     *  microseconds and can be larger or smaller than the scheduling period value.  This will
     *  be set to -1 if no quota limiting CPU core usage has been set.
     */
    int32_t quota = -1;

    /** The CPU scheduling period.  This indicates the scheduling time slice and provides the
     *  time base that the CPU usage quota is defined around.  This value will be -1 if no
     *  scheduling period has been defined.
     */
    int32_t period = 100'000;
};

/** Parses a CPU quota pair from a file.
 *
 *  @param[in] file     The path to the file to read the CPU quota pair from.  This may not be
 *                      `nullptr`.  This file is expected to contain two values on the first
 *                      line where the first value is either "max" or an integer and the second
 *                      value is an integer.
 *  @returns A pair of integers indicating the CPU's usage quota and period.  The first value is
 *           the usage quota value or -1 if not quota limit has been specified.  The second value
 *           is the CPU scheduling period.  This is usually 100000.  If the CPU quota could not be
 *           parsed for any reason, a pair containing <-1, -1> will be returned instead.  If
 *           either value in the pair is negative or zero, the quota value should be considered
 *           invalid.
 *
 *  @remarks Parses a CPU usage quota file and extracts the scheduling quota and period values.
 *           These quota files are expected to be in the cgroups v2 format where both values
 *           are found in the same file.  In cgroups v1 each value has its own file so this
 *           parsing is not necessary.  The CPU usage quota files are expected to contain values
 *           similar to "275000 100000" where the first value is the usage scheduling quota in
 *           microseconds, and the second value is the CPU scheduling period in microseconds.
 *           The scheduling period defaults to 100000us.  When the usage quota value is larger
 *           than the scheduling period, it indicates that effectively multiple cores can be
 *           used by processes in the container.  However, even if this value is less than the
 *           scheduling period, that doesn't mean that parallel execution will be disallowed.
 *           multiple threads may still run on multiple cores simultaneously, however they will
 *           only be allowed to run on those multiple cores for a portion of each scheduling
 *           period.  These files may also contain values similar to "max 100000" to indicate
 *           that there is no limit on CPU usage and scheduling, but still provide a valid
 *           scheduling period.
 */
inline CpuQuota readCpuQuotaFromFile(const char* file) noexcept
{
    char buffer[64];
    int quota;
    int period;
    char* endp = nullptr;

    if (!readLineFromFile(file, buffer, CARB_COUNTOF(buffer)))
    {
        return { -1, -1 };
    }

    // attempt to parse two values from the line.  The first value may be 'max' or a number
    // between 0 and 100000.  The second number is often 100000 but could be different depending
    // on scheduler settings.  We expect this file to always be properly formatted.

    // set to use the maximum quota for all available CPU cores => fail.
    if (strncmp(buffer, "max ", 4) == 0)
    {
        return { -1, std::atoi(&buffer[4]) };
    }

    quota = (int)strtol(buffer, &endp, 10);
    period = std::atoi(endp);

    return { quota, period };
}

/** Reads a CPU set list and parses out the total core count (and optional cores list).
 *
 *  @param[in] buffer   The line of text to parse the cores list from.  This is expected to always
 *                      be properly formated.  The expected fomat is a comma separated list of
 *                      either core indices or core ranges.  For example, "0-1,3" includes cores
 *                      0, 1, and 3.  No whitespace is expected to be included in the string (but
 *                      will be parsed here anyway).  This may not be `nullptr` or an empty
 *                      string.
 *  @param[out] cores   Optionally receives a list of all core indices included in the CPU set.
 *                      If this value is not `nullptr`, this will receive a list of each core
 *                      index parsed from the CPU set list.  All ranges will be expanded to single
 *                      indices.
 *  @returns The total number of cores parsed out of the CPU set list.  This should never return
 *           0 if the CPU set string is properly formatted.
 */
inline int32_t getCpuSetCoreCount(const char* buffer, std::vector<int32_t>* cores = nullptr) noexcept
{
    std::string str = buffer;
    size_t pos = 0;
    size_t next;
    int32_t coreStart;
    int32_t coreEnd;
    int32_t total = 0;


    while (1)
    {
        std::string start;
        std::string end;

        next = str.find_first_of(",-", pos);

        // last item in the list (must be a single core) or a single core => parse and add it.
        if (next == std::string::npos || str[next] == ',')
        {
            size_t limit = (next == std::string::npos) ? str.length() : next;

            start = str.substr(pos, limit - pos);
            coreStart = std::atoi(start.c_str());
            total++;

            if (cores != nullptr)
            {
                cores->push_back(coreStart);
            }

            // done
            if (next == std::string::npos)
            {
                break;
            }
        }

        // found a core range => parse the start and end and add them.
        else if (str[next] == '-')
        {
            size_t posEnd = next + 1;

            start = str.substr(pos, next - pos);
            coreStart = std::atoi(start.c_str());

            next = str.find_first_of(",", posEnd);
            end = str.substr(posEnd, next - posEnd);
            coreEnd = std::atoi(end.c_str());

            // add the total core count.  Note that the ranges are always inclusive so we always
            // need to add 1 to the calculated range.
            total += coreEnd - coreStart + 1;

            // add all the cores to the list (inclusive on both ends of the range).
            if (cores != nullptr)
            {
                for (int32_t i = coreStart; i <= coreEnd; i++)
                {
                    cores->push_back(i);
                }
            }

            // nothing left in the source string => done.
            if (next == std::string::npos)
            {
                break;
            }
        }

        pos = next + 1;
    }

    return total;
}

/** Reads a CPU set file and parses out the total core count.
 *
 *  @param[in] file     The path to the file to read the CPU set list from.  This may not be
 *                      `nullptr`.  This is expected to always be properly formated.  The
 *                      expected fomat is a comma separated list of either core indices or
 *                      core ranges.  For example, "0-1,3" includes cores 0, 1, and 3.  No
 *                      whitespace is expected to be included in the string (but will be parsed
 *                      here anyway).  This may not be `nullptr` or an empty string.
 *  @param[out] buffer  Optionally receives the line of text parsed from the file.  This may be
 *                      `nullptr` if the read text is not required.  This buffer should be large
 *                      enough to potentially hold four characters per CPU core present in the
 *                      system.  In practice it will rarely require a buffer that size however.
 *  @param[in] len      The maximum number of characters including a null terminator character
 *                      that can fit in @p buffer.  This parameter is ignored if @p buffer is
 *                      `nullptr`.
 *  @returns The total number of cores parsed out of the CPU set list.  This should never return
 *           0 if the CPU set string is properly formatted.  Returns -1 if the file could not be
 *           found, opened, or read from for any reason.
 */
inline int readCpuSetCoreCountFromFile(const char* file, char* buffer = nullptr, size_t len = 0) noexcept
{
    char localBuffer[1024];

    if (buffer == nullptr || len == 0)
    {
        buffer = localBuffer;
        len = CARB_COUNTOF(localBuffer);
    }

    // read the first line from the file.  This will contain the CPU core list.  This list is
    // comma separated where each value may either be a single core index or a core index range.
    // For example, "0-1,3" would indicate that cores 0, 1, and 3 are available and "0-3,7,9"
    // would indicate that cores 0, 1, 2, 3, 7, and 9 are available.
    if (!readLineFromFile(file, buffer, len))
    {
        return -1;
    }

    // return the total number of cores included in the CPU set.
    return getCpuSetCoreCount(buffer);
}

inline bool isRunningInContainer() noexcept
{
    FILE* fp;

    // first (and easiest) check is to check whether the `/.dockerenv` file exists.  This file
    // is not necessarily always present though.
    if (access("/.dockerenv", F_OK) == 0)
    {
        return true;
    }

    // a more reliable but more expensive check is to verify the control group of `init`.  If
    // running under docker, all of the entries will have a path that starts with `/docker` or
    // `/lxc` instead of just `/`.
    // Kubernetes seems to use `:/kubepods.slice`.
    fp = fopen("/proc/1/cgroup", "r");

    if (fp != nullptr)
    {
        char line[256];

        while (fgets(line, CARB_COUNTOF(line), fp) != nullptr)
        {
            if (feof(fp) || ferror(fp))
                break;

            if (strstr(line, ":/docker") != nullptr || strstr(line, ":/lxc") != nullptr ||
                strstr(line, ":/kubepods") != nullptr)
            {
                return true;
            }
        }

        fclose(fp);
    }

    return false;
}

inline bool getCgroupCpuQuota(CpuQuota& quota)
{
    // attempt to read the CPU quota from cgroup v2 first.
    quota = readCpuQuotaFromFile("/sys/fs/cgroup/cpu.max");

    if (quota.quota > 0 && quota.period > 0)
    {
        return true;
    }

    // attempt to read the CPU quota from cgroup v1 next.
    quota.quota = detail::readIntFromFile("/sys/fs/cgroup/cpu/cpu.cfs_quota_us");
    quota.period = detail::readIntFromFile("/sys/fs/cgroup/cpu/cpu.cfs_period_us");

    if (quota.quota > 0 && quota.period > 0)
    {
        return true;
    }

    // CPU quota not available.
    return false;
}

inline int32_t getCgroupCpuQuota() noexcept
{
    CpuQuota quota;

    // attempt to read the CPU quota from cgroup v2 and cgroup v1.  This can affect how much
    // of the assigned cores scheduled time the processes in the container are effectively allowed
    // to make use of.
    if (getCgroupCpuQuota(quota))
    {
        return ::carb_max(1, (quota.quota + (quota.period / 2)) / quota.period);
    }

    return -1;
}

inline int getDockerCpuLimit() noexcept
{
    // See:
    // https://docs.docker.com/config/containers/resource_constraints/#cpu
    // https://engineering.squarespace.com/blog/2017/understanding-linux-container-scheduling
    // https://docs.kernel.org/admin-guide/cgroup-v1/cpusets.html
    // https://docs.kernel.org/admin-guide/cgroup-v2.html

    // ****** read the CPU core limit if defined ******
    // first attempt to read from the cgroup v2 and v1 CPU set lists to get the total core count.
    // We'll try the 'effective' CPU set list first.  If they doesn't exist or is empty, we'll fall
    // back to the main CPU set lists.  Note that the v1 and v2 cgroups will never simultaneously
    // exist in the container and that Docker will always respect the host system's cgroup version
    // regardless of the container's base image version.
    int32_t coreCount;

    // try to read the cgroup v2 effective CPU set.
    coreCount = detail::readCpuSetCoreCountFromFile("/sys/fs/cgroup/cpuset.cpus.effective");

    // fall back to the cgroup v2 main CPU set.
    if (coreCount < 0)
        coreCount = detail::readCpuSetCoreCountFromFile("/sys/fs/cgroup/cpuset.cpus");

    // fall back to the cgroup v1 effective CPU set.
    if (coreCount < 0)
        coreCount = detail::readCpuSetCoreCountFromFile("/sys/fs/cgroup/cpuset/cpuset.effective_cpus");

    // fall back to the cgroup v1 main CPU set.
    if (coreCount < 0)
        coreCount = detail::readCpuSetCoreCountFromFile("/sys/fs/cgroup/cpuset/cpuset.cpus");

    // ****** read the CPU usage quota if defined ******
    // next attempt to read the CPU quota from cgroup v2 and cgroup v1.  This can affect how much
    // of the assigned cores scheduled time the processes in the container are effectively allowed
    // to make use of.
    int32_t coreQuota = getCgroupCpuQuota();

    // ****** calculate the effective CPU core limit ******
    // a CPU set has been assigned and has limited the core count for the container => calculate
    //   the effective core count from the CPU set and the CPU quota.
    if (coreCount > 0)
    {
        // a CPU quota has been defined as well => caclulate the effective core count from both
        //   values.  Note that the CPU usage quota can oversubscribe the assigned core count.
        //   In that case we'd want to return the minimum of the CPU set core count and the
        //   effective count from the CPU quota.
        if (coreQuota > 0)
            return ::carb_min(coreQuota, coreCount);

        // no CPU usage quota defined => just return the CPU set core count.
        return coreCount;
    }

    // no CPU set core count defined => just return the effective core count from the CPU quota.
    else if (coreQuota > 0)
    {
        return coreQuota;
    }

    // no CPU usage limit.  This will effectively limit it to the host's bare metal CPU core
    // count.
    return -1;
}

} // namespace detail
#    endif


/** Attempts to read the current effective CPU usage quota for processes in a container.
 *
 *  @returns The effective number of logical cores that processes in the container will have
 *           access to if a limit has been imposed.  If no limit has been imposed when running
 *           the container, -1 will be returned.
 *
 *  @remarks This reads and calculates the effective CPU usage quota for processes in a container.
 *           If a limit has been imposed, the result is the number of logical cores that can be
 *           used.  Note that this does not actually guarantee that the processes will not be
 *           able to run on some cores, but rather that the CPU scheduler will only give a
 *           certain percentage of its time to processes in the container thereby effectively
 *           making their performance similar to running on a system with the returned number
 *           of cores.
 *
 *  @note This will still return a valid result outside of a container if a CPU usage limit has
 *        been imposed on the system.  By default, Linux systems allow unlimited CPU usage.
 */
inline int getDockerCpuLimit() noexcept
{
    static int s_coreCount = detail::getDockerCpuLimit();
    return s_coreCount;
}

/** Attempts to detect whether this process is running inside a container.
 *
 *  @returns `true` if this process is running inside a container.  Returns `false` otherwise.
 *
 *  @remarks This detects if the calling process is running inside a container.  This is done
 *           by checking for certain files or their contents that are known (and documented)
 *           to be modified by Docker.  Note that this currently only supports detecting Docker
 *           and LXC containers.
 */
inline bool isRunningInContainer()
{
    static bool s_inContainer = detail::isRunningInContainer();
    return s_inContainer;
}

#else

inline int getDockerCpuLimit() noexcept
{
    return -1;
}

inline bool isRunningInContainer() noexcept
{
    return false;
}

#endif

} // namespace extras
} // namespace omni
