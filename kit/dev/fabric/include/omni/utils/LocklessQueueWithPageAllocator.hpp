// Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/container/LocklessQueue.h>
#include <omni/utils/PagedArenaAllocator.hpp>

namespace omni
{

/**
 LocklessQueueWithPageAllocator: 
 - Implements a lockless queue of entries allocated using a paged arena allocator
 */
template<typename DataType>
class LocklessQueueWithPageAllocator
{
public:
    static const uint32_t kDefaultPageSize = 16 * 1024;
    static const uint32_t kDefaultPageCount = 4;

    struct Entry
    {
        DataType data;
        carb::container::LocklessQueueLink<Entry> listlink;
    };

    LocklessQueueWithPageAllocator(uint32_t pageSize = kDefaultPageSize,
                                   uint32_t startPageCount = kDefaultPageCount)
    : m_pagedMemoryAllocator(pageSize, startPageCount)
    {}
    ~LocklessQueueWithPageAllocator()
    {
        clear();
    }

    bool queue(const DataType& data)
    {
        Entry* newEntry = reinterpret_cast<Entry*>(m_pagedMemoryAllocator.alloc(sizeof(Entry)));
        if (!newEntry)
        {
            return false;
        }
        newEntry->data = data;

        m_requestsQueue.push(newEntry);
        return true;
    }

    template <typename Callback>
    bool tryProcessOne(Callback callback)
    {
        if (Entry* entry = m_requestsQueue.popMC())
        {
            callback(entry->data);
            m_pagedMemoryAllocator.free(reinterpret_cast<uint8_t*>(entry));
            return true;
        }
        return false;
    }

    void clear()
    {
        m_requestsQueue.popAll();
    }

private:
    carb::container::LocklessQueue<Entry, &Entry::listlink> m_requestsQueue;
    omni::PagedArenaAllocator m_pagedMemoryAllocator;
};

} // namespace omni
