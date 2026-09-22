// Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include "Defines.h"
#include "Intrinsics.h"

#include <cmath>
#include <cstdint>
#include <cstdlib>

namespace omni
{
namespace fabric
{

struct HashMapDefaultAllocator
{
    typedef void value_type;

    inline value_type* allocate(const size_t count)
    {
        return std::malloc(count);
    }

    void deallocate(value_type* const ptr, const size_t /*count*/) noexcept
    {
        std::free(ptr);
    }
};


// Enable using fibonacci hashing for indexing in the hash map
// this has better collision avoidance behaviors than multiplying by a prime, in exchange for a small perf cost.
// See for details:
// https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/
#define HASHMAP_FIBONACCI_HASHING IN_USE

// A hashmap implemented with the following decisions:
//
//   * Memory is allocated in a single contiguous buffer so that find operations make linear cache line fetches as much
//     as possible. This intends to make more easily predictable memory access patterns, and thus, easier hardware-level
//     prefetch decisions. Similarly, whole-map iteration benefits from the same cache-friendly access patterns.
//
//   * Find operations intentionally are coded without range checks on the main loop. This is a tradeoff of speed for
//     less error-detection in release builds. To help mitigate this, debug builds do track probe counts to validate
//     we don't exceed the possible length of the hashmap.
//
//   * No opinion codified on thread synchronization. It can be used safely if done carefully, but this is not a
//     guarantee of the implementation.
//
//   * No iterators provided. If some batch operation must occur, use the forEach() function provided, which should
//     suffice. The forEach() method should provide similar performance without the added risk of callers being able to
//     arbitrarily cache iterators outside the control of the HashMap, its routines, or even its lifetime.
//
//   * Deletes copy-constructor and copy-assignment for non-standard-layout mappings. This forces callers to implement
//     these routines explicitly, favoring the clarity of reading intent in explicit implementation over ambiguity over
//     compiler selection. Mappings that have standard-layout default to use a memcpy to copy data as fast as possible.
//
//   * Implements allocateEntry() method, rather than insert()/emplace() methods mimicing std::unordered_map API. This
//     does the minimum steps necessary to reserve address space for a key-value mapping, and provides the caller with
//     the reserved buffer memory address for them to do their own construction, assignment, or initialization routines.
//     This favors slightly more explicit coding patterns at the caller to force clarity of intent. In particular,
//     it make more obvious the choice of the caller between construction vs assignment, and copy vs move semantics. It
//     also offers greater flexibility without sacrificing performance.
//
//   * ~HashMap() and clear() operate different depending on if KeyT and ValueT are known to be
//     std::is_trivially_destructible. If they are, the fastest option is chosen: to deallocate the memory without
//     iteration or explicitly destruction per-entry. Otherwise, the implementation iterates to non-trivially destruct
//     each object in-place.

template <typename KeyT,
          typename ValueT,
          typename HashT = std::hash<KeyT>,
          typename KeyEqualsT = std::equal_to<KeyT>,
          typename AllocT = HashMapDefaultAllocator>
struct HashMap
{
    // I didn't experiment with this exhaustively, could be tuned better, probably
    // Note: rough testing seems to indicate that prime salting and fib hashing have slightly different
    // perf characteristics with the occupancy at high loads...make these separable for the moment for further tuning.
#if USING(HASHMAP_FIBONACCI_HASHING)
    static constexpr size_t LOAD_FACTOR_NUMERATOR = 3ull;
    static constexpr size_t LOAD_FACTOR_DENOMENATOR = 4ull;
#else
    static constexpr size_t LOAD_FACTOR_NUMERATOR = 3ull;
    static constexpr size_t LOAD_FACTOR_DENOMENATOR = 4ull;
#endif
    static constexpr size_t MIN_INIT_CAPACITY = 4ull;
    static_assert((MIN_INIT_CAPACITY & (MIN_INIT_CAPACITY - 1ull)) == 0, "MIN_INIT_CAPACITY must be a power of two!");

    enum EntryState : uint8_t
    {
        HASH_MAP_ENTRY_STATE_FREE = 0,
        HASH_MAP_ENTRY_STATE_OCCUPIED = 1,
        HASH_MAP_ENTRY_STATE_DELETED = 2,
    };

    struct EntryT
    {
        EntryState state;
        KeyT key;
        ValueT value;
    };

    static constexpr bool ENTRY_IS_TRIVIAL_TO_COPY = std::is_trivially_copyable<EntryT>::value;
    static constexpr bool ENTRY_IS_TRIVIAL_TO_SHUT = std::is_trivially_destructible<EntryT>::value;
    static constexpr bool ENTRY_IS_TRIVIAL_TO_MEMOP = ENTRY_IS_TRIVIAL_TO_SHUT && ENTRY_IS_TRIVIAL_TO_COPY;
    static constexpr bool DAMN_FAST = ENTRY_IS_TRIVIAL_TO_MEMOP;

    HashMap(const HashT& hasher = HashT(), const KeyEqualsT& keyEquals = KeyEqualsT(), const AllocT& alloc_ = AllocT());

    HashMap(const size_t user_capacity,
            const HashT& hasher = HashT(),
            const KeyEqualsT& keyEquals = KeyEqualsT(),
            const AllocT& alloc_ = AllocT());

    ~HashMap();

    HashMap(const HashMap& other);
    HashMap& operator=(const HashMap& other);

    HashMap(HashMap&& other) noexcept;
    HashMap& operator=(HashMap&& other) noexcept;

    void clear();
    void swap(HashMap& other) noexcept;

    const void* data() const;
    bool empty() const;
    size_t size() const;
    size_t capacity() const;
    size_t allocationCnt() const;

    void reserve(const size_t user_capacity);

    bool find(const KeyT& key, ValueT** outValue);
    bool find(const KeyT& key, const ValueT** outValue) const;
    bool exists(const KeyT& key) const;
    bool allocateEntry(KeyT&& key, ValueT** outValue);
    bool allocateEntry(const KeyT& key, ValueT** outValue);

    void setEntry(const KeyT& key, const ValueT& value);
    bool hasEntry(const KeyT& key, const ValueT& value) const;

    // Intended to be safe to call during forEach() as it does not invalidate iteration.
    bool freeEntry(const KeyT& key);
    void freeEntryByKeyAddress(const KeyT* const key);
    void freeEntryByValueAddress(const ValueT* const value);

    template <typename CallbackT>
    inline void forEach(CallbackT callback);

    template <typename CallbackT>
    inline void forEach(CallbackT callback) const;

    size_t totalCollisionLength() const;

    AllocT getAllocator() const noexcept;

private:
    static constexpr size_t allocationSize(const size_t capacity);
    static constexpr size_t loadThreshold(const size_t capacity);
    static constexpr size_t inverseLoadThreshold(const size_t capacity);
    static constexpr size_t capacityAdjustedForLoadThreshold(const size_t capacity);

    size_t hashInternal(const KeyT& key) const;

    void resizeIfNecessary(const size_t expectedOccupancy);
    void resize(const size_t user_capacity);

    void freeEntryInternal(EntryT* const entry);

    bool findExistingOrFirstAvailable(const KeyT& key, EntryT** outEntry);
    bool findExisting(const KeyT& key, EntryT** outEntry);
    bool findExisting(const KeyT& key, const EntryT** outEntry) const;

    void checkInvariants() const;

    void init();
    void init_with_final_capacity(size_t final_capacity, bool doInitEntries = true);
    void init_with_user_capacity(size_t user_capacity, bool doInitEntries = true);
    void init_from(const HashMap& other);
    void shut();

    struct EntryRange
    {
        EntryT* curPtr;
        EntryT* endPtr;
        size_t occupiedCnt;

        EntryRange()
        {
        }

        EntryRange(const HashMap& h)
            : curPtr(h.m_entries), endPtr(h.m_entries + h.m_capacity), occupiedCnt(h.m_occupied)
        {
            check();
        }

        void check() const
        {
            CARB_ASSERT(curPtr && curPtr <= endPtr);
            CARB_ASSERT(occupiedCnt == 0 || curPtr != endPtr);

#if CARB_DEBUG
            if (occupiedCnt != 0) // unallocated memory
            {
                size_t actuallyOccupied = 0;
                for (EntryT* cur = curPtr; cur != endPtr; ++cur)
                {
                    if (cur && cur->state == HASH_MAP_ENTRY_STATE_OCCUPIED)
                    {
                        ++actuallyOccupied;
                    }
                }

                CARB_ASSERT(occupiedCnt == actuallyOccupied);
            }
#endif
        }
    };

    void range_init(EntryRange& inOutRange);
    void range_shut(EntryRange& inOutRange);
    void range_reinit(EntryRange& inOutRange);
    void range_copy_from(EntryRange& inOutDstRange, EntryRange& inOutSrcRange);
    void range_init_from(EntryRange& inOutDstRange, EntryRange& inOutSrcRange);

    HashT m_hasher;
    KeyEqualsT m_keyEquals;
    AllocT m_alloc;
    size_t m_allocated;
    size_t m_allocationCnt;
    size_t m_occupied;
    size_t m_deleted;
    size_t m_capacity;
    size_t m_loadThreshold;
    size_t m_mask;
    uint32_t m_hashShiftAmount;
    EntryT* m_entries;
};


template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline constexpr size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::allocationSize(const size_t capacity)
{
    return capacity * sizeof(EntryT);
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline constexpr size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::loadThreshold(const size_t capacity)
{
    return (capacity * LOAD_FACTOR_NUMERATOR / LOAD_FACTOR_DENOMENATOR);
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline constexpr size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::inverseLoadThreshold(const size_t capacity)
{
    return (capacity * LOAD_FACTOR_DENOMENATOR / LOAD_FACTOR_NUMERATOR);
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline constexpr size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::capacityAdjustedForLoadThreshold(
    const size_t capacity)
{
    // reserves capacity to the nearest power of two that satisfies the load threshhold for the requested capacity

    size_t adjustedCapacity = 0;
    if (capacity && capacity >= loadThreshold(MIN_INIT_CAPACITY))
    {
        // +1 because we want capacity < loadThreshold(adjustedCapacity), not capacity <=
        // loadThreshold(adjustedCapacity)
        adjustedCapacity = 1ull << (64u - clz64(inverseLoadThreshold(capacity + 1) - 1ull));
    }
    else
    {
        adjustedCapacity = MIN_INIT_CAPACITY;
    }
    CARB_ASSERT(capacity < loadThreshold(adjustedCapacity));
    CARB_ASSERT((adjustedCapacity & (adjustedCapacity - 1ull)) == 0);
    return adjustedCapacity;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::checkInvariants() const
{
    CARB_ASSERT((m_capacity & (m_capacity - 1)) == 0);
    CARB_ASSERT((m_capacity && m_entries) || (!m_capacity && !m_entries));
    CARB_ASSERT((m_capacity && m_allocated) || (!m_capacity && !m_allocated));
    CARB_ASSERT(m_capacity <= m_allocated);
    CARB_ASSERT(!m_capacity || (m_allocationCnt > 0));
    CARB_ASSERT(!m_capacity || (m_occupied < m_capacity));
    CARB_ASSERT(!m_capacity || (m_occupied < m_loadThreshold));
    CARB_ASSERT(!m_capacity || (m_deleted < m_capacity));
    CARB_ASSERT(!m_capacity || (m_deleted < m_loadThreshold));
    CARB_ASSERT(!m_capacity || (m_occupied < m_capacity - m_deleted));
    CARB_ASSERT(!m_capacity || (m_occupied < m_loadThreshold - m_deleted));

#if CARB_ASSERT_ENABLED
    // this verification is viable only for non-trivial data
    if constexpr (!ENTRY_IS_TRIVIAL_TO_MEMOP)
    {
        if (m_capacity < 256)
        {
            size_t occupied_cnt = 0;
            size_t deleted_cnt = 0;
            for (size_t i = 0; i < m_capacity; i++)
            {
                const EntryState stt = m_entries[i].state;
                if (stt == HASH_MAP_ENTRY_STATE_OCCUPIED)
                    occupied_cnt++;
                else if (stt == HASH_MAP_ENTRY_STATE_DELETED)
                    deleted_cnt++;
            }
            CARB_ASSERT(occupied_cnt == m_occupied);
            CARB_UNUSED(occupied_cnt);
            CARB_UNUSED(deleted_cnt);
        }
    }
#endif
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::HashMap(const HashT& hasher,
                                                                 const KeyEqualsT& keyEquals,
                                                                 const AllocT& alloc_)
    : m_hasher(hasher), m_keyEquals(keyEquals), m_alloc(alloc_)
{
    init();
    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::HashMap(const size_t capacity,
                                                                 const HashT& hasher,
                                                                 const KeyEqualsT& keyEquals,
                                                                 const AllocT& alloc_)
    : m_hasher(hasher), m_keyEquals(keyEquals), m_alloc(alloc_)
{
    init_with_user_capacity(capacity);
    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::HashMap(const HashMap& other)
    : m_hasher(other.m_hasher), m_keyEquals(other.m_keyEquals), m_alloc(other.m_alloc)
{
    if (&other == this)
        return;

    other.checkInvariants();
    init_from(other);
    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::HashMap(HashMap&& other) noexcept
    : m_hasher(other.m_hasher), m_keyEquals(other.m_keyEquals), m_alloc(other.m_alloc)
{
    if (&other == this)
        return;

    other.checkInvariants();
    init();
    swap(other);
    other.checkInvariants();
    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::~HashMap()
{
    checkInvariants();
    shut();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>& HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::operator=(
    const HashMap& other)
{
    if (&other == this)
        return *this;

    checkInvariants();
    other.checkInvariants();

    const bool other_is_empty = (other.m_occupied == 0);
    const bool other_fits_in_alloc = (other.m_capacity <= m_allocated);

    if (other_is_empty)
    {
        clear();

        m_hasher = other.m_hasher;
        m_keyEquals = other.m_keyEquals;
    }
    else if (other_fits_in_alloc)
    {
        EntryRange src(other);
        EntryRange dst(*this);
        range_copy_from(dst, src);
        range_init_from(dst, src);
        range_reinit(dst);
        range_init(dst);

        m_hasher = other.m_hasher;
        m_keyEquals = other.m_keyEquals;
        m_loadThreshold = other.m_loadThreshold;
        m_mask = other.m_mask;
        m_hashShiftAmount = other.m_hashShiftAmount;
        m_capacity = other.m_capacity;
        m_occupied = other.m_occupied;
        m_deleted = other.m_deleted;
    }
    else
    {
        shut();

        const size_t alloc_cnt = m_allocationCnt;
        init_from(other);
        m_allocationCnt = alloc_cnt + 1;
    }

    checkInvariants();
    return *this;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>& HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::operator=(
    HashMap&& other) noexcept
{
    if (&other == this)
        return *this;

    checkInvariants();
    shut();
    init();
    swap(other);
    other.checkInvariants();
    checkInvariants();
    return *this;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::clear()
{
    checkInvariants();

    if (m_occupied)
    {
        EntryRange r(*this);
        range_reinit(r);
        range_init(r);
    }

    m_occupied = 0;
    m_deleted = 0;

    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::swap(HashMap& other) noexcept
{
    std::swap(m_hasher, other.m_hasher);
    std::swap(m_keyEquals, other.m_keyEquals);
    std::swap(m_alloc, other.m_alloc);
    std::swap(m_allocated, other.m_allocated);
    std::swap(m_allocationCnt, other.m_allocationCnt);
    std::swap(m_occupied, other.m_occupied);
    std::swap(m_deleted, other.m_deleted);
    std::swap(m_capacity, other.m_capacity);
    std::swap(m_loadThreshold, other.m_loadThreshold);
    std::swap(m_mask, other.m_mask);
    std::swap(m_hashShiftAmount, other.m_hashShiftAmount);
    std::swap(m_entries, other.m_entries);
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::init()
{
    m_capacity = 0;
    m_allocated = 0;
    m_allocationCnt = 0;
    m_loadThreshold = 0;
    m_mask = 0;
    m_hashShiftAmount = 0;
    m_occupied = 0;
    m_deleted = 0;
    m_entries = nullptr;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::init_with_final_capacity(size_t final_capacity,
                                                                                       bool doInitEntries)
{
    if (final_capacity == 0)
        return init();

    m_capacity = final_capacity;
    m_allocated = final_capacity;
    m_loadThreshold = loadThreshold(final_capacity);
    m_mask = final_capacity - 1ull;
    m_hashShiftAmount = 64 - uint32_t(std::log2(double(final_capacity)));
    m_occupied = 0;
    m_deleted = 0;
    m_allocationCnt = 1;

    const size_t bufSize = allocationSize(m_allocated);
    m_entries = (EntryT*)m_alloc.allocate(bufSize);

    if (doInitEntries)
    {
        EntryRange r(*this);
        range_init(r);
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::init_with_user_capacity(size_t user_capacity,
                                                                                      bool doInitEntries)
{
    const size_t adjusted_capacity = user_capacity ? capacityAdjustedForLoadThreshold(user_capacity) : 0;
    init_with_final_capacity(adjusted_capacity);
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::init_from(const HashMap& other)
{
    if (other.m_occupied == 0)
    {
        init();
    }
    else
    {
        init_with_final_capacity(other.m_capacity, false);

        EntryRange src(other);
        EntryRange dst(*this);
        range_init_from(dst, src);
        range_init(dst);

        m_occupied = other.m_occupied;
        m_deleted = other.m_deleted;
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::shut()
{
    if (m_occupied)
    {
        EntryRange r(*this);
        range_shut(r);
        m_occupied = 0;
    }

    if (m_entries)
    {
        const size_t bufSize = allocationSize(m_allocated);
        m_alloc.deallocate(m_entries, bufSize);
        m_entries = nullptr;
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::range_init(EntryRange& r)
{
    // init entries
    r.check();

    const size_t n = r.endPtr - r.curPtr;
    void* curPtr = r.curPtr; // -Wclass-memaccess on gcc11.4.0
    std::memset(curPtr, HASH_MAP_ENTRY_STATE_FREE, n * sizeof(EntryT));
    r.curPtr = r.endPtr;
    r.occupiedCnt = 0;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::range_shut(EntryRange& r)
{
    // shutdown occupied entries
    r.check();

    if constexpr (ENTRY_IS_TRIVIAL_TO_SHUT)
    {
        r.curPtr = r.endPtr;
        r.occupiedCnt = 0;
    }
    else
    {
        for (; r.curPtr < r.endPtr && r.occupiedCnt; r.curPtr++)
        {
            switch (r.curPtr->state)
            {
            case HASH_MAP_ENTRY_STATE_FREE:
            case HASH_MAP_ENTRY_STATE_DELETED:
                break;

            case HASH_MAP_ENTRY_STATE_OCCUPIED:
                r.curPtr->key.~KeyT();
                r.curPtr->value.~ValueT();
                r.occupiedCnt--;
                break;
            }
        }
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::range_reinit(EntryRange& r)
{
    // reinitialize entries, shutting down the occupied ones
    r.check();

    if constexpr (ENTRY_IS_TRIVIAL_TO_SHUT)
    {
        const size_t n = r.endPtr - r.curPtr;
        void* curPtr = r.curPtr; // -Wclass-memaccess on gcc11.4.0
        std::memset(curPtr, HASH_MAP_ENTRY_STATE_FREE, n * sizeof(EntryT));
        r.curPtr = r.endPtr;
        r.occupiedCnt = 0;
    }
    else
    {
        for (; r.curPtr < r.endPtr && r.occupiedCnt; r.curPtr++)
        {
            switch (r.curPtr->state)
            {
            case HASH_MAP_ENTRY_STATE_FREE:
            case HASH_MAP_ENTRY_STATE_DELETED:
                break;

            case HASH_MAP_ENTRY_STATE_OCCUPIED:
                r.curPtr->key.~KeyT();
                r.curPtr->value.~ValueT();
                r.occupiedCnt--;
                break;
            }
            r.curPtr->state = HASH_MAP_ENTRY_STATE_FREE;
        }
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::range_copy_from(EntryRange& dst, EntryRange& src)
{
    // copy entries, shutting down the previously occupied ones
    dst.check();
    src.check();

    if (src.occupiedCnt == 0 || dst.occupiedCnt == 0)
        return;

    const size_t dst_n = dst.endPtr - dst.curPtr;
    const size_t src_n = src.endPtr - src.curPtr;
    const size_t n = std::min(dst_n, src_n);
    const EntryT* dst_end = dst.curPtr + n;

    if constexpr (ENTRY_IS_TRIVIAL_TO_MEMOP)
    {
        const EntryT* src_end = src.curPtr + n;
        std::memcpy(dst.curPtr, src.curPtr, n * sizeof(EntryT));
        dst.curPtr = (EntryT*)dst_end;
        src.curPtr = (EntryT*)src_end;
        dst.occupiedCnt = (dst_end == dst.endPtr) ? 0 : dst.occupiedCnt;
        src.occupiedCnt = (src_end == src.endPtr) ? 0 : src.occupiedCnt;
    }
    else
    {
        for (; dst.curPtr < dst_end && src.occupiedCnt && dst.occupiedCnt; src.curPtr++, dst.curPtr++)
        {
            static_assert(HASH_MAP_ENTRY_STATE_OCCUPIED == 1);
            // Using bitwise operations and a switch to reduce instruction cache pressure - the branches/potential jump
            // table are closer together
            const unsigned dst_occupied = dst.curPtr->state & HASH_MAP_ENTRY_STATE_OCCUPIED;
            const unsigned src_occupied = src.curPtr->state & HASH_MAP_ENTRY_STATE_OCCUPIED;
            const unsigned occupiedBits = dst_occupied | (src_occupied << 1);
            switch (occupiedBits)
            {
            case 3: // src & dst are occupied
                dst.curPtr->value = src.curPtr->value;
                dst.curPtr->key = src.curPtr->key;
                src.occupiedCnt--;
                dst.occupiedCnt--;
                break;
            case 1: // dst only is occupied
                dst.curPtr->key.~KeyT();
                dst.curPtr->value.~ValueT();
                dst.occupiedCnt--;
                break;
            case 2: // src only is occupied
                new (&dst.curPtr->value) ValueT(src.curPtr->value);
                new (&dst.curPtr->key) KeyT(src.curPtr->key);
                src.occupiedCnt--;
                break;
            default:
                CARB_ASSERT(dst.curPtr->state != HASH_MAP_ENTRY_STATE_OCCUPIED);
                CARB_ASSERT(src.curPtr->state != HASH_MAP_ENTRY_STATE_OCCUPIED);
            }
            dst.curPtr->state = src.curPtr->state;
        }
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::range_init_from(EntryRange& dst, EntryRange& src)
{
    // init new entries by copying existing ones
    // the destination is expected to have a counter == 0 (no more occupied elements!)
    dst.check();
    src.check();

    if (src.occupiedCnt == 0 || dst.occupiedCnt != 0)
        return;

    const size_t dst_n = dst.endPtr - dst.curPtr;
    const size_t src_n = src.endPtr - src.curPtr;
    const size_t n = std::min(dst_n, src_n);
    const EntryT* dst_end = dst.curPtr + n;

    if constexpr (ENTRY_IS_TRIVIAL_TO_MEMOP)
    {
        const EntryT* src_end = src.curPtr + n;
        std::memcpy(dst.curPtr, src.curPtr, n * sizeof(EntryT));
        dst.curPtr = (EntryT*)dst_end;
        src.curPtr = (EntryT*)src_end;
        dst.occupiedCnt = (dst_end == dst.endPtr) ? 0 : dst.occupiedCnt;
        src.occupiedCnt = (src_end == src.endPtr) ? 0 : src.occupiedCnt;
    }
    else
    {
        for (; dst.curPtr < dst_end && src.occupiedCnt; src.curPtr++, dst.curPtr++)
        {
            switch (src.curPtr->state)
            {
            case HASH_MAP_ENTRY_STATE_FREE:
            case HASH_MAP_ENTRY_STATE_DELETED:
                break;

            case HASH_MAP_ENTRY_STATE_OCCUPIED:
                new (&dst.curPtr->value) ValueT(src.curPtr->value);
                new (&dst.curPtr->key) KeyT(src.curPtr->key);
                src.occupiedCnt--;
                break;
            }

            dst.curPtr->state = src.curPtr->state;
        }
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline const void* HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::data() const
{
    return m_entries;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::empty() const
{
    return m_occupied == 0;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::size() const
{
    return m_occupied;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::capacity() const
{
    return m_capacity;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::allocationCnt() const
{
    return m_allocationCnt;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::reserve(const size_t user_capacity)
{
    const size_t adjustedCapacity = capacityAdjustedForLoadThreshold(user_capacity);
    if (m_capacity < adjustedCapacity)
        resize(user_capacity);

    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::find(const KeyT& key, ValueT** outValue)
{
    EntryT* existing;
    if (findExisting(key, &existing))
    {
        *outValue = &existing->value;
        return true;
    }

    return false;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::find(const KeyT& key, const ValueT** outValue) const
{
    const EntryT* existing;
    if (findExisting(key, &existing))
    {
        *outValue = &existing->value;
        return true;
    }

    return false;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::exists(const KeyT& key) const
{
    const EntryT* existing;
    if (findExisting(key, &existing))
    {
        return true;
    }

    return false;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::allocateEntry(KeyT&& key, ValueT** outValue)
{
    // + 1 is slightly greedy in that it might resize early if the key exists, and this invocation would not have
    // allocated a new entry. However, the alternative is that we would either have to:
    //   a) call resizeIfNecessary again after the insert
    //   b) not resize after the insert and potentially leaving the HashMap in a state where m_occupied ==
    //   m_loadThreshhold
    //
    // (b) is exceptionally terrible because it means any subsequent copy-assignment or copy-construction would
    // double-allocate the m_entries buffer since we detect m_occupied >= m_loadThreshhold.
    //
    // The performance impact of doing +1 _should_ be minimal. We're not resizing constantly, just one allocation early.
    //

    checkInvariants();
    resizeIfNecessary(m_occupied + 1);
    checkInvariants();

    EntryT* availableEntry;
    const bool foundKey = findExistingOrFirstAvailable(key, &availableEntry);
    CARB_ASSERT(availableEntry);
    if (!foundKey)
    {
        new (&availableEntry->key) KeyT(std::move(key));
        CARB_ASSERT(availableEntry->state != HASH_MAP_ENTRY_STATE_OCCUPIED);
        if (availableEntry->state == HASH_MAP_ENTRY_STATE_DELETED)
        {
            CARB_ASSERT(m_deleted);
            --m_deleted;
        }
        availableEntry->state = HASH_MAP_ENTRY_STATE_OCCUPIED;
        *outValue = &availableEntry->value;
        CARB_ASSERT(m_occupied < m_capacity);
        CARB_ASSERT(m_occupied + 1 > m_occupied);
        ++m_occupied;

        checkInvariants();
        return true;
    }

    *outValue = &availableEntry->value;

    checkInvariants();
    return false;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::allocateEntry(const KeyT& key, ValueT** outValue)
{
    EntryT* availableEntry;

    // + 1 is slightly greedy in that it might resize early if the key exists, and this invocation would not have
    // allocated a new entry. However, the alternative is that we would either have to:
    //   a) call resizeIfNecessary again after the insert
    //   b) not resize after the insert and potentially leaving the HashMap in a state where m_occupied ==
    //   m_loadThreshhold
    //
    // (b) is exceptionally terrible because it means any subsequent copy-assignment or copy-construction would
    // double-allocate the m_entries buffer since we detect m_occupied >= m_loadThreshhold.
    //
    // The performance impact of doing +1 _should_ be minimal. We're not resizing constantly, just one allocation early.
    //
    resizeIfNecessary(m_occupied + 1);

    const bool foundKey = findExistingOrFirstAvailable(key, &availableEntry);
    CARB_ASSERT(availableEntry);
    if (!foundKey)
    {
        new (&availableEntry->key) KeyT(key);
        CARB_ASSERT(availableEntry->state != HASH_MAP_ENTRY_STATE_OCCUPIED);
        if (availableEntry->state == HASH_MAP_ENTRY_STATE_DELETED)
        {
            CARB_ASSERT(m_deleted);
            --m_deleted;
        }
        availableEntry->state = HASH_MAP_ENTRY_STATE_OCCUPIED;
        *outValue = &availableEntry->value;
        CARB_ASSERT(m_occupied < m_capacity);
        CARB_ASSERT(m_occupied + 1 > m_occupied);
        ++m_occupied;

        checkInvariants();
        return true;
    }

    *outValue = &availableEntry->value;

    checkInvariants();
    return false;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::setEntry(const KeyT& key, const ValueT& value)
{
    ValueT* pvalue;
    if (allocateEntry(key, &pvalue))
    {
        new (pvalue) ValueT(value);
    }
    else
    {
        CARB_ASSERT(pvalue);
        *pvalue = value;
    }
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::hasEntry(const KeyT& key, const ValueT& value) const
{
    const ValueT* pvalue;
    if (!find(key, &pvalue))
        return false;
    CARB_ASSERT(pvalue);
    return *pvalue == value;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::freeEntry(const KeyT& key)
{
    bool res = false;

    EntryT* existing;
    if (findExisting(key, &existing))
    {
        freeEntryInternal(existing);
        res = true;
    }

    checkInvariants();
    return res;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::freeEntryByKeyAddress(const KeyT* const key)
{
    static_assert(!std::is_polymorphic<EntryT>::value, "Unable to freeEntry by key address!");
    constexpr size_t OFFSET = offsetof(EntryT, key);
    EntryT* const entry = (EntryT*)(((uintptr_t)key) - OFFSET);
    freeEntryInternal(entry);
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::freeEntryByValueAddress(const ValueT* const value)
{
    static_assert(!std::is_polymorphic<EntryT>::value, "Unable to freeEntry by value address!");
    constexpr size_t OFFSET = offsetof(EntryT, value);
    EntryT* const entry = (EntryT*)(((uintptr_t)value) - OFFSET);
    freeEntryInternal(entry);
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::hashInternal(const KeyT& key) const
{
    size_t hash = m_hasher(key);

#define HASHMAP_DEFENSIVE_SALT IN_USE
#if USING(HASHMAP_DEFENSIVE_SALT)
    // Apply a defensive salt to the user-calculated hash value. It is unsafe to assume user-provided hashes are good.
    //
    // Kit historically had a problem where std::hash<PathC> caused terrible distributions inside of space-restricted
    // hashmaps. This was primarly because the hash values returned had zero entropy in the lower 8 bits. The higher
    // bits had excellent entropy, though. It is trivial to improve std::hash<PathC> by doing (oldHashValue >> 8).
    // In other words, tossing the bits with zero entropy. This will produce perfectly unique hash value output for
    // every PathC input. However, using this directly in a hash map is still not ideal because, while the hash function
    // has a guarantee on uniqueness, it does not necessarily lend to good distributions in a hash table. Two hash
    // values that are multiples of each other will naturally colliide in any space-restricted hashmap.
    // (Which, realistically, is all real hash maps since hardware memory is not infinite.) Applying a little salt on
    // top of the hash value fixes this distribution problem.
    //
    // This also provides general safety against poorly implemented user-provided hash functions that don't generate
    // unique or well distributed values.
    //
    // Known problematic data sets:
    // - PathC (interned SdfPaths)
    // - TokenC (interned TfTokens)
    //
    // Salt techniques tried:
    // - H3_XX64 (xxhash):
    //     - good distribution
    //     - too slow
    // - H3_XX64 (xxhash) with custom seeds:
    //     - no seed performed better than the xxhash default secret
    // - Custom H3_XX64 implementation specialized for aligned 64-bit keys:
    //     - mathematically identical distribution to H3_XX64
    //     - 2x faster performance than official implementation
    // - Multiply by a prime
    //     - best distribution so far
    //     - best speed so far (3x faster than custom H3_XX64)
    // - Fibonacci hashing
    //     - Has very good distribution with very few collisions
    //     - slightly slower than multiplying by a prime since it does additional shifts and xors
    //
    // TODO: A fun intern experiment would be to investigate our various omniverse hash functions for distribution and
    // speed. And also investigate alternative defensive salting techniques.

#    if USING(HASHMAP_FIBONACCI_HASHING)
    hash ^= hash >> m_hashShiftAmount; // shift down and xor to increase low bit entropy .
    hash = (11400714819323198485llu * hash) >> m_hashShiftAmount;
#    else
    hash = (hash * 48271ull) & m_mask; // prime hashing
#    endif
#else // #if USING( HASHMAP_DEFENSIVE_SALT )
    hash = hash & m_mask;
#endif // #if USING( HASHMAP_DEFENSIVE_SALT )
    CARB_ASSERT(hash < m_capacity);
    return hash;
#undef HASHMAP_DEFENSIVE_SALT
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::resizeIfNecessary(const size_t expectedOccupancy)
{
    checkInvariants();

    if (!m_entries)
    {
        resize(MIN_INIT_CAPACITY);
    }
    else
    {
        CARB_ASSERT(m_capacity);
        if (expectedOccupancy >= m_loadThreshold)
        {
            const size_t new_capacity = m_capacity * 2;
            CARB_ASSERT(new_capacity > m_capacity); // protect against overflow
            resize(new_capacity);
        }
        else if (expectedOccupancy >= m_loadThreshold - m_deleted)
        {
            resize(m_capacity); // rehashes table to clear DELETED entries
        }
    }

    CARB_ASSERT(m_allocated);
    CARB_ASSERT(m_entries);
    CARB_ASSERT(m_capacity);

    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::resize(const size_t new_user_capacity)
{
    checkInvariants();

    if (new_user_capacity == 0)
    {
        clear();
    }
    else
    {
        CARB_ASSERT(m_occupied < new_user_capacity); // cannot shrink!
        CARB_ASSERT(m_occupied <= capacityAdjustedForLoadThreshold(new_user_capacity));

        HashMap tmp(new_user_capacity, m_hasher, m_keyEquals, m_alloc);

        size_t index = 0;
        size_t visited = 0;
        for (; index < m_capacity && visited < m_occupied; ++index)
        {
            EntryT* const entry = &m_entries[index];
            if (entry->state == HASH_MAP_ENTRY_STATE_OCCUPIED)
            {
                ValueT* tmpV;
                tmp.allocateEntry(std::move(entry->key), &tmpV);
                new (tmpV) ValueT(std::move(entry->value));

                CARB_ASSERT(visited < m_occupied);
                ++visited;
            }
        }

        CARB_ASSERT(tmp.m_allocationCnt == 1);
        tmp.checkInvariants();
        tmp.m_allocationCnt += m_allocationCnt;

        swap(tmp);
    }

    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::freeEntryInternal(EntryT* const entry)
{
    CARB_ASSERT(entry);
    CARB_ASSERT(entry->state == HASH_MAP_ENTRY_STATE_OCCUPIED);

    CARB_ASSERT(m_entries <= entry);
    CARB_ASSERT(entry < m_entries + m_capacity);
    if (!(m_entries <= entry && entry < m_entries + m_capacity))
    {
        return;
    }

    if constexpr (!ENTRY_IS_TRIVIAL_TO_SHUT)
    {
        entry->key.~KeyT();
        entry->value.~ValueT();
    }

    entry->state = HASH_MAP_ENTRY_STATE_DELETED;
    CARB_ASSERT(m_occupied);
    CARB_ASSERT(m_occupied - 1 < m_occupied);
    --m_occupied;
    ++m_deleted;
    CARB_ASSERT(m_deleted);

    resizeIfNecessary(m_occupied);

    checkInvariants();
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
template <typename CallbackT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::forEach(CallbackT callback)
{

    size_t index = 0;
    size_t visited = 0;
    const size_t size_captured = m_occupied;
    for (; index < m_capacity && visited < size_captured; ++index)
    {
        if (m_entries[index].state == HASH_MAP_ENTRY_STATE_OCCUPIED)
        {
            callback(m_entries[index].key, m_entries[index].value);

            CARB_ASSERT(visited < size_captured);
            ++visited;
        }
    }
}


template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
template <typename CallbackT>
inline void HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::forEach(CallbackT callback) const
{
    size_t index = 0;
    size_t visited = 0;
    const size_t size_captured = m_occupied;
    for (; index < m_capacity && visited < size_captured; ++index)
    {
        if (m_entries[index].state == HASH_MAP_ENTRY_STATE_OCCUPIED)
        {
            callback(m_entries[index].key, m_entries[index].value);

            CARB_ASSERT(visited < size_captured);
            ++visited;
        }
    }
}


template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline size_t HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::totalCollisionLength() const
{
    size_t len = 0;

    if (m_entries)
    {
        size_t index = 0;
        size_t visited = 0;
        const size_t size_captured = m_occupied;
        for (; index < m_capacity && visited < size_captured; ++index)
        {
            const EntryT* const probe = &m_entries[index];
            if (probe->state == HASH_MAP_ENTRY_STATE_OCCUPIED)
            {
                const EntryT* const natural = &m_entries[hashInternal(probe->key)];
                len += (size_t)((natural <= probe) ? (probe - natural) : ((probe + m_capacity) - natural));

                CARB_ASSERT(visited < size_captured);
                ++visited;
            }
        }
    }

    return len;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline AllocT HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::getAllocator() const noexcept
{
    return m_alloc;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::findExistingOrFirstAvailable(const KeyT& key,
                                                                                           EntryT** outEntry)
{
    EntryT* probe;
    size_t probeIdx;
    size_t firstAvailable = SIZE_MAX;

#if USING(ASSERTS)
    size_t probes = 0;
#endif // #if USING( ASSERTS )
    probeIdx = hashInternal(key);

    CARB_ASSERT(m_entries);
    CARB_ASSERT(m_occupied < m_capacity); // otherwise we infinite loop
    while (1)
    {
        CARB_ASSERT(probeIdx < m_capacity);
        probe = &m_entries[probeIdx];

        if (probe->state == HASH_MAP_ENTRY_STATE_FREE)
        {
            if (firstAvailable != SIZE_MAX)
            {
                *outEntry = &m_entries[firstAvailable];
            }
            else
            {
                *outEntry = probe;
            }
            return false;
        }
        else if (probe->state == HASH_MAP_ENTRY_STATE_OCCUPIED)
        {
            if (m_keyEquals(probe->key, key))
            {
                *outEntry = probe;
                return true;
            }
        }
        else if (probe->state == HASH_MAP_ENTRY_STATE_DELETED)
        {
            if (firstAvailable == SIZE_MAX)
            {
                firstAvailable = probeIdx;
            }
        }

        probeIdx = (probeIdx + 1) & m_mask;
#if USING(ASSERTS)
        ++probes;
        CARB_ASSERT(probes < m_capacity);
#endif // #if USING( ASSERTS )
    }

    CARB_ASSERT(false && "unreachable code");
    return false;
}

template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::findExisting(const KeyT& key, EntryT** outEntry)
{
    if (!m_occupied)
    {
        return false;
    }

    EntryT* probe;
    size_t probeIdx;

#if USING(ASSERTS)
    size_t probes = 0;
#endif // #if USING( ASSERTS )
    probeIdx = hashInternal(key);

    CARB_ASSERT(m_occupied < m_capacity); // otherwise we infinite loop
    while (1)
    {
        CARB_ASSERT(probeIdx < m_capacity);
        probe = &m_entries[probeIdx];

        if (probe->state == HASH_MAP_ENTRY_STATE_FREE)
        {
            return false;
        }
        else if (probe->state == HASH_MAP_ENTRY_STATE_OCCUPIED)
        {
            if (m_keyEquals(probe->key, key))
            {
                *outEntry = probe;
                return true;
            }
        }
        else
        {
            // skip
            CARB_ASSERT(probe->state == HASH_MAP_ENTRY_STATE_DELETED);
        }

        probeIdx = (probeIdx + 1) & m_mask;
#if USING(ASSERTS)
        ++probes;
        CARB_ASSERT(probes < m_capacity);
#endif // #if USING( ASSERTS )
    }

    CARB_ASSERT(false && "unreachable code");
    return false;
}


template <typename KeyT, typename ValueT, typename HashT, typename KeyEqualsT, typename AllocT>
inline bool HashMap<KeyT, ValueT, HashT, KeyEqualsT, AllocT>::findExisting(const KeyT& key, const EntryT** outEntry) const
{
    return const_cast<HashMap*>(this)->findExisting(key, const_cast<EntryT**>(outEntry));
}


} // namespace fabric
} // namespace omni
