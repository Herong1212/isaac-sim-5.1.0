// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "ReservedVector.h"
#include <carb/Framework.h>
#include <carb/logging/Log.h>
#include <carb/tasking/TaskingUtils.h>

#ifdef _WIN32
    #include <Windows.h>
    #undef min
    #undef max
#else
    #include <unistd.h>
    #include <sys/mman.h>
    #include <cstring>
#endif
#include <atomic>

namespace omni
{

namespace detail
{

ReservedVectorBase::ReservedVectorBase(size_t capacity, size_t sizePerElem, size_t pageGrowth)
    : m_capacity(capacity)
    , m_sizePerElem(sizePerElem)
    , m_pageGrowth(std::max(pageGrowth, size_t(1)))
{
#ifdef _WIN32
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    m_pageSize = sysInfo.dwAllocationGranularity;
#else
    m_pageSize = getpagesize();
#endif

    if (capacity > 0)
    {
        reserve(capacity);
    }
}

ReservedVectorBase::~ReservedVectorBase()
{
    free();
}

void* ReservedVectorBase::reserve(size_t capacity)
{
    free();
    m_capacity = capacity;
    m_maxPages = (m_capacity * m_sizePerElem + m_pageSize - 1) / m_pageSize;

#ifdef _WIN32
    m_data = VirtualAlloc(nullptr, m_maxPages * m_pageSize, MEM_RESERVE, PAGE_READWRITE);
#else
    m_data = mmap(nullptr, m_maxPages * m_pageSize, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
#endif
    return m_data;
}

void ReservedVectorBase::free()
{
    if (m_data != nullptr)
    {
        decommit(0);
#ifdef _WIN32
        VirtualFree(m_data, 0, MEM_RELEASE);
#else
        munmap(m_data, m_maxPages * m_pageSize);
#endif
    }

    m_capacity = 0;
    m_data = nullptr;
    m_maxPages = 0;
    m_committedPages.store(0);
}

void ReservedVectorBase::commit(size_t size)
{
    CARB_ASSERT(size <= m_capacity); // cannot resize more than original capacity
    size_t needsPageCount = std::min(m_maxPages, (size * m_sizePerElem + m_pageSize - 1) / m_pageSize);

    // early out before the lock if we don't need to commit pages, this assumes that committing and uncommitting pages is not performed in a concurrent way
    if (needsPageCount <= m_committedPages.load())
        return;

    CARB_PROFILE_ZONE(1, "ReservedVector commit");
    std::lock_guard<std::mutex> lock(m_mutex);
    size_t currentCommitted = m_committedPages.load();
    // check again after taking the lock if another thread already committed enough
    if (needsPageCount > currentCommitted)
    {
        needsPageCount = std::min(m_maxPages, CARB_ALIGN(needsPageCount, m_pageGrowth));
#ifdef _WIN32
        VirtualAlloc((unsigned char*)m_data + currentCommitted * m_pageSize, m_pageSize * (needsPageCount - currentCommitted), MEM_COMMIT, PAGE_READWRITE);
#else
        mprotect((unsigned char*)m_data + currentCommitted * m_pageSize, m_pageSize * (needsPageCount - currentCommitted), PROT_READ | PROT_WRITE);
#endif
        m_committedPages.store(needsPageCount);
    }
}

void ReservedVectorBase::decommit(size_t size)
{
    size_t needsPageCount = (size * m_sizePerElem + m_pageSize - 1) / m_pageSize;
    if (needsPageCount < m_committedPages.load())
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        size_t neededOffset = needsPageCount * m_pageSize;
        size_t currentOffset = m_committedPages.load() * m_pageSize;
        if (m_data != nullptr)
        {
#ifdef _WIN32
            VirtualFree((unsigned char*)m_data + neededOffset, currentOffset - neededOffset, MEM_DECOMMIT);
#else
            mprotect((unsigned char*)m_data + neededOffset, currentOffset - neededOffset, PROT_NONE);
            madvise((unsigned char*)m_data + neededOffset, currentOffset - neededOffset, MADV_DONTNEED);
#endif
        }
        m_committedPages.store(needsPageCount);
    }
}

}

} // namespace omni
