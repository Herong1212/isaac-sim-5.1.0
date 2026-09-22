// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/thread/Spinlock.h>
#include <carb/container/IntrusiveList.h>

#include <mutex>

namespace omni
{

/**
 PagedArenaAllocator: A simple arena like allocator which allocs it's memory in pages
 - based on fixed sized pages that only track the amount allocated/freed and allow fast out of order frees
 - can only reuse a page once all allocations are freed from it
 - has the overhead of an allocation header stored before each allocation
 */
class PagedArenaAllocator
{
    struct Page;

public:
    PagedArenaAllocator(size_t pageSize, uint32_t preallocatedPages)
	: m_pageSize(pageSize)
    {
        for (uint32_t i = 0; i < preallocatedPages; ++i)
        {
            Page* newPage = new Page(m_pageSize);
            m_freePages.push_back(*newPage);
        }
        allocPage();
    }
    ~PagedArenaAllocator()
    {
        std::unique_lock lock(m_lock);
        deleteAllPages(m_inUsePages);
        deleteAllPages(m_freePages);
    }

    static const uint32_t kAllocMarker = 0xa110c8;
    struct AllocHeader
    {
        uint32_t marker;
        uint32_t size;
        Page* page;
    };

    uint8_t* alloc(size_t size)
    {
        size_t sizeToAlloc = size + sizeof(AllocHeader);
        CARB_FATAL_UNLESS(sizeToAlloc <= m_pageSize, "Can only make allocations <= of page size (%zu)", m_pageSize);

        std::unique_lock lock(m_lock);

        Page* currentPage = &m_inUsePages.front();
        size_t newUsedSize = currentPage->usedSize + sizeToAlloc;
        if (newUsedSize >= m_pageSize)
            currentPage = allocPage(currentPage);

        uint8_t* memory = currentPage->memory + currentPage->usedSize;
        currentPage->usedSize += sizeToAlloc;

        AllocHeader* header = reinterpret_cast<AllocHeader*>(memory);
        header->marker = kAllocMarker;
        header->page = currentPage;
        header->size = uint32_t(sizeToAlloc);

        uint8_t* allocedMem = memory + sizeof(AllocHeader);

        return allocedMem;
    }

    void free(uint8_t* memory)
    {
        AllocHeader* header = reinterpret_cast<AllocHeader*>(memory - sizeof(AllocHeader));
        CARB_FATAL_UNLESS(header->marker == kAllocMarker, "PagedArenaAllocator: Invalid allocation header!");
        freeFromPage(header->page, header->size);
    }

    size_t getAllocatedPageCount() const
    {
        std::unique_lock lock(m_lock);
        return m_inUsePages.size();
    }
    size_t getFreePageCount() const
    {
        std::unique_lock lock(m_lock);
        return m_freePages.size();
    }

    void releaseFreePages()
    {
        std::unique_lock lock(m_lock);
        deleteAllPages(m_freePages);
    }

private:
    struct Page
    {
        Page(size_t pageSize)
        {
            memory = new uint8_t[pageSize];
        }
        ~Page()
        {
            delete[] memory;
        }
        void reset()
        {
            freedSize = 0;
            usedSize = 0;
        }
        bool isInUse() const
        {
            return (freedSize < usedSize);
        }

        uint8_t* memory = nullptr;
        size_t usedSize = 0;
        size_t freedSize = 0;
        carb::container::IntrusiveListLink<Page> listlink;
    };

    Page* allocPage(Page* currentPage = nullptr)
    {
        Page* newPage = (m_freePages.size() > 0) ? &m_freePages.pop_back() : new Page(m_pageSize);
        m_inUsePages.push_front(*newPage);
        return newPage;
    }

    void freePage(Page& entry)
    {
        CARB_FATAL_UNLESS(&entry != &m_inUsePages.front(), "Cannot free the current top page!");
        m_inUsePages.remove(entry);
        entry.reset();
        m_freePages.push_back(entry);
    }

    typedef carb::container::IntrusiveList<Page, &Page::listlink> PageEntryList;
    void deleteAllPages(PageEntryList& pageEntryList)
    {
        while (!pageEntryList.empty())
        {
            Page* entry = &pageEntryList.pop_back();
            delete entry;
        }
    }

    void freeFromPage(Page* page, uint32_t allocedSize)
    {
        std::unique_lock lock(m_lock);

        page->freedSize += allocedSize;
        if (page->freedSize == page->usedSize)
        {
            if (page == &m_inUsePages.front())
                page->reset();
            else
                freePage(*page);
        }
        CARB_FATAL_UNLESS(page->freedSize <= page->usedSize, "PagedArenaAllocator: Memory free underflow");
    }

    size_t m_pageSize = 0;
    using LockType = carb::thread::Spinlock;
    mutable LockType m_lock;
    PageEntryList m_inUsePages;
    PageEntryList m_freePages;
};

} // namespace omni
