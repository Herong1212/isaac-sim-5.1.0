// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "Atomic.h"
#include "Defines.h"
#include <mutex>

namespace omni
{

// ReservedVector - a std::vector replacement that allocates virtual memory upfront and only commits necessary pages on resize
//                  pages are always committed densely up to the size of the vector
//                  pages are only uncommitted in a specific garbageCollect call
//                  as the vector never relocates, this allows using this vector in a lock-less way while it is only growing (committing new pages triggers a lock)
//                  resizeMaxAtomic and grow() can be used from n threads at the same time and the integrity of the vector memory is guaranteed (aka. memory up to the size of the current request has been committed and new elements have been constructed)

// !!!! the methods of this base class are defined in ReservedVector.inl, to avoid the need for including platform specific memory management functions
// this file needs to be included once in each link unit !!!

namespace detail
{
    struct ReservedVectorBase
    {
        void* m_data = nullptr;
        size_t m_capacity = 0;
        size_t m_pageSize = 0;
        std::atomic<size_t> m_committedPages{ 0 };
        size_t m_maxPages = 0;
        size_t m_sizePerElem = 0;
        size_t m_pageGrowth = 1;
        std::mutex m_mutex;

        ReservedVectorBase(size_t capacity, size_t sizePerElem, size_t pageGrowth);
        ~ReservedVectorBase();

        void* reserve(size_t capacity);
        void free();

        size_t capacity() const { return m_capacity; }
        size_t committed() const { return m_committedPages * m_pageSize / m_sizePerElem; }

        // commits new pages necessary to store size number of elements - this function is thread safe
        void commit(size_t size);

        // uncommits pages that are no longer necessary - this function itself is thread safe, but uncommitting pages makes all other operations on this vector unsafe
        // particularly committing and uncommitting pages cannot be performed in a concurrent way
        void decommit(size_t size);
    };
}

template<class T>
class ReservedVector
{
public:
    CARB_PREVENT_COPY_AND_MOVE(ReservedVector);

    // initialize the vector with a given capacity and a page grows step
    // pageGrowth determines the granularity at which physical memory is allocated, this can be useful to balance memory overhead and mapping frequency/overhead
    ReservedVector(size_t capacity = 0, size_t pageGrowth = 1)
        : m_base(capacity, sizeof(T), pageGrowth)
    {
        m_garbageCollectFrame = ((size_t)this >> 8) % C_GARBAGE_COLLECT_FRAMES; // pseudo random number for garbage collection
        m_elems = (T*)m_base.m_data;
    }

    size_t capacity() const { return m_base.capacity(); }
    size_t size() const { return m_size; }

    // number of committed elements
    size_t committed() const { return m_base.committed(); }

    void clear()
    {
        resize(0, {});
    }

    // decommits all memory and resizes the vector to 0
    // this function is not threadsafe
    void free()
    {
        m_base.decommit(0);
        m_size = 0;
        m_resizedSize = 0;
    }

    void reserve(size_t capacity)
    {
        CARB_FAIL_UNLESS(!m_doNotRelocate || (m_base.capacity() == 0), "Should not reserve after initial reservation as this will break the assumptions that memory is never relocated");
        m_elems = (T*)m_base.reserve(capacity);
    }

    // grows the vector by increment elements, returns the old value before atomically incrementing the size
    // does not initialize the new element
    // this function is thread safe
    size_t growNoInit(size_t increment)
    {
        size_t oldSize = m_size.fetch_add(increment);
        m_base.commit(oldSize + increment);
        return oldSize;
    }

    // grows the vector by increment elements, returns the old value before atomically incrementing the size
    // this function is thread safe
    size_t grow(size_t increment, const T& newValue = {})
    {
        size_t oldSize = growNoInit(increment);
        for (size_t i = 0; i < increment; i++)
        {
            new (&m_elems[oldSize + i])T(newValue);
        }
        return oldSize;
    }

    // grows the vector to a new maximum size using atomics (it never shrinks)
    // commits memory if necessary
    // fills the elements between oldsize and size with newValue
    // this function is thread safe
    size_t resizeMaxAtomic(size_t size, const T& newValue)
    {
        if (CARB_UNLIKELY(size > m_base.capacity()))
        {
            reserve(size);
        }

        size_t oldSize = fetch_max(m_size, size);
        if (size > oldSize)
        {
            m_base.commit(size);
            for (size_t i = oldSize; i < size; i++)
            {
                new (&m_elems[i])T(newValue);
            }
            waitUntilResized(oldSize);
            fetch_max(m_resizedSize, size);
        }
        else
        {
            waitUntilResized(size);
        }
        CARB_ASSERT(size * sizeof(T) <= m_base.m_committedPages * m_base.m_pageSize);
        return oldSize;
    }

    // grows the vector to a new maximum size using atomics (it never shrinks)
    // commits memory if necessary
    // new elements are not constructed, so this should not be used with non pod
    // this function is thread safe
    size_t resizeMaxAtomic(size_t size)
    {
        static_assert(std::is_trivial<T>::value, "Use resizeMaxAtomic with newValue to construct non-pod types");
        if (CARB_UNLIKELY(size > m_base.capacity()))
        {
            reserve(size);
        }

        size_t oldSize = fetch_max(m_size, size);
        if (size > oldSize)
        {
            m_base.commit(size);

            waitUntilResized(oldSize);
            fetch_max(m_resizedSize, size);
        }
        else
        {
            waitUntilResized(size);
        }
        return oldSize;
    }

    // resizes the vector to a new size, reserves and commits memory
    // this function is not thread safe
    // fills the elements between oldsize and size with newValue
    size_t resize(size_t size, const T& newValue)
    {
        if (CARB_UNLIKELY(size > m_base.capacity()))
        {
            reserve(size);
        }

        size_t oldSize = m_size;
        m_size = size;;
        if (size > oldSize)
        {
            m_base.commit(size);
            for (size_t i = oldSize; i < size; i++)
            {
                new (&m_elems[i])T(newValue);
            }
        }
        else if (size < oldSize)
        {
            for (size_t i = size; i < oldSize - 1; i++)
            {
                m_elems[i].~T();
            }
        }
        m_resizedSize.store(m_size);
        return oldSize;
    }

    // resizes the vector to a new size, reserves and commits memory, this is not thread safe
    size_t resize(size_t size)
    {
        static_assert(std::is_trivial<T>::value, "Use resize with newValue to construct non-pod types");
        if (CARB_UNLIKELY(size > m_base.capacity()))
        {
            reserve(size);
        }

        size_t oldSize = m_size;
        m_size = size;
        if (size > oldSize)
        {
            m_base.commit(size);
            for (size_t i = oldSize; i < size; i++)
            {
                new (&m_elems[i])T;
            }
        }
        else if (size < oldSize)
        {
            for (size_t i = size; i < oldSize - 1; i++)
            {
                m_elems[i].~T();
            }
        }
        m_resizedSize.store(m_size);
        return oldSize;
    }

    void push_back(const T& elem)
    {
        m_elems[grow(1)] = elem;
    }

    void push_back(T&& elem)
    {
        m_elems[grow(1)] = std::move(elem);
    }

    // triggers garbage collection (decommitting unused pages) every n frames
    void garbageCollect(size_t garbageCollectFrames = C_GARBAGE_COLLECT_FRAMES)
    {
        m_garbageCollectFrame++;
        if (m_garbageCollectFrame > garbageCollectFrames)
        {
            m_base.decommit(m_size.load());
            m_garbageCollectFrame = 0;
        }
    }

    void shrink_to_fit()
    {
        garbageCollect(0);
    }

    bool empty() const
    {
        return size() == 0;
    }

    const T& operator[](size_t index) const { return m_elems[index]; }
    T& operator[](size_t index) { return m_elems[index]; }
    const T* data() const { return m_elems; }
    T* data() { return m_elems; }

    // controls whether the memory storing this buffer should be potentially relocate or not
    void setDoNotRelocate(bool doNotRelocate) { m_doNotRelocate = doNotRelocate; }


    // iterators for range based loops
    struct ReservedVectorIterator
    {
        ReservedVector<T>& array;
        size_t idx;

        ReservedVectorIterator(ReservedVector<T>& array_, size_t startIndex)
            : array(array_)
            , idx(startIndex)
        {
        }

        ReservedVectorIterator(ReservedVector<T>& array_)
            : array(array_)
            , idx(array.size())
        {
        }

        bool operator!=(const ReservedVectorIterator& other) const { CARB_ASSERT(&other.array == &this->array); return idx != other.idx; }
        T& operator*() { return array[idx]; }
        const T& operator*() const { return array[idx]; }

        ReservedVectorIterator& operator++()
        {
            idx++;
            return *this;
        }
    };

    struct ReservedVectorConstIterator
    {
        const ReservedVector<T>& array;
        size_t idx;

        ReservedVectorConstIterator(const ReservedVector<T>& array_, size_t startIndex)
            : array(array_)
            , idx(startIndex)
        {
        }

        ReservedVectorConstIterator(const ReservedVector<T>& array_)
            : array(array_)
            , idx(array.size())
        {
        }

        bool operator!=(const ReservedVectorConstIterator& other) const { CARB_ASSERT(&other.array == &this->array); return idx != other.idx; }
        const T& operator*() const { return array[idx]; }

        ReservedVectorConstIterator& operator++()
        {
            idx++;
            return *this;
        }
    };

    inline ReservedVectorIterator begin() { return { *this, 0 }; }
    inline ReservedVectorIterator end() { return { *this }; }

    inline ReservedVectorConstIterator begin() const { return { *this, 0 }; }
    inline ReservedVectorConstIterator end() const { return { *this }; }
private:
    detail::ReservedVectorBase m_base;
    T* m_elems = nullptr;
    std::atomic<size_t> m_size{ 0 };
    std::atomic<size_t> m_resizedSize{ 0 };
    size_t m_garbageCollectFrame = 0;
    // whether this buffer can relocate (which only happens on reserve)
    bool m_doNotRelocate = true;

    // standard number of frames for garbage collection (aka uncommit) happens
    static const size_t C_GARBAGE_COLLECT_FRAMES = 128;
    // wait until we can be sure that the resize to a certain minimum size has finished on another thread
    void waitUntilResized(size_t size)
    {
        while (m_resizedSize.load() < size);
    }
};

} // namespace omni
