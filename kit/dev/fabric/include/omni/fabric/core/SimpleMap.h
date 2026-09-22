// Copyright (c) 2019-2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "SimpleVector.h"

namespace omni
{
namespace fabric
{

//
// Implementation of a simple hashmap
//
// !! You are not encourage to use this hashmap container
// !! except if you know what you are doing and you accept
// !! any changes in the future.
// !! This code is designed Fabric internal core hashing
// !! where critical performances are expected. This code
// !! is not user friendly.
// !! Please do not modify it.
//
// Purpose of this implementation is to be very fast.
//
// To achive this goal, the implementation is limited to the following:
// - minimum service with minimal amount of code
// - no automatic resizing, no copy, minimal error management
// - a single type for the key and the value
// - supported types are integers, floating points and pointers
// - the key value (0) is reserved and cannot be used
// - no deletion supported, the container is always growing
// - no user custom indexing function but a small choice of predefined ones (see SimpleMapIndexing)

enum struct SimpleMapIndexing
{
    None = 0,
    Knuth,
    KnuthU,
    Fibo,
    Shift8,
    Unpack8,
    Path = Shift8, // Recommended on PathC
    Token = Knuth, // Recommended on TokenC
    CAddr = Knuth, // Recommended on Fabric CacheAddr
    RandomU64 = Knuth, // Recommended on random 64-bits values
    Default = Knuth
};

template <typename T>
constexpr bool SimpleMapSupportedType =
    !(std::is_same<T, bool>::value) &&
    (std::is_integral<T>::value || std::is_floating_point<T>::value || std::is_pointer<T>::value) && (sizeof(T) <= 8);

template <typename T, SimpleMapIndexing I = SimpleMapIndexing::Default>
struct SimpleMap
{
    struct Entry
    {
        T key;
        T value;
    };

    using type_t = T;
    using entry_t = Entry;
    using value_generator_t = T (*)(void* ud);
    static constexpr T kReservedKey = 0;
    //  static constexpr T kReservedKey = std::numeric_limits<T>::max();
    static constexpr SimpleMapIndexing indexing = I;
    static_assert(SimpleMapSupportedType<T>);

    void clear(); // clear the elements
    void reserve(size_t n); // reserve n elements (recommended to double the capacity to reduce collisions)
    void reserveAtLeast(size_t n); // reserve IF the capacity is less than the given amount
    Entry* data() const;
    size_t capacity() const;
    size_t size() const;
    bool empty() const;
    size_t growCounter() const;
    size_t probeCounter() const;
    float efficiency() const;
    size_t index(const T key) const;

    bool has(const T key) const;
    bool has(const T key, const T value) const;
    const Entry* find(const T key) const;
    size_t slot(const Entry* ent) const;
    Entry* slot(size_t index) const;

    Entry* allocate(const T key, T*& pvalue); // allocate an entry
    Entry* allocate_grow(const T key, T*& pvalue); // allocate an entry and increase the capacity x2 if necessary

    T store(const T key, const T value); // store an entry if not existing

    void set(const T key, const T value); // set an entry and override the current value if existing
    void set(const SimpleMap& other); // set entries from an other map

    void concurrent_set(const T key, const T value); // atomically set an entry and override the current value if
                                                     // existing
    T concurrent_store(const T key, const T value); // atomically store an entry if not existing
    T concurrent_store(const T key, value_generator_t gen, void* ud);

    template <typename VisitorT>
    void for_each(VisitorT visitor);
    template <typename VisitorT>
    void for_each(VisitorT visitor) const;

protected:
    SimpleVector<Entry> entries;
    size_t usedCnt = 0;
    size_t probedCnt = 0;
    size_t grewCnt = 0;
    size_t m = 0;
};


template <typename T, SimpleMapIndexing I>
inline size_t SimpleMap<T, I>::index(const T key) const
{
    CARB_ASSERT(m);
    CARB_ASSERT(key != kReservedKey);

    size_t idx;
    switch (I)
    {
    case SimpleMapIndexing::None:
        idx = key & m;
        break;
    case SimpleMapIndexing::Knuth:
        idx = key * 0x9e3779b97f4a7c13;
        idx = (idx ^ (idx >> 32)) & m;
        break;
    case SimpleMapIndexing::KnuthU:
        static_assert(sizeof(key) == 8);
        idx = interleave8_mem((uint64_t*)&key);
        idx = idx * 0x9e3779b97f4a7c13;
        idx = (idx ^ (idx >> 32)) & m;
        break;
    case SimpleMapIndexing::Fibo:
        // Fibonacci hash
        // https://probablydance.com/2018/06/16/fibonacci-hashing-the-optimization-that-the-world-forgot-or-a-better-alternative-to-integer-modulo/
        idx = (((key ^ (key >> 6)) * 11400714819323198485llu) >> 6) & m;
        break;
    case SimpleMapIndexing::Shift8:
        idx = (key >> 8) & m;
        break;
    case SimpleMapIndexing::Unpack8:
        static_assert(sizeof(key) == 8);
        idx = interleave8_mem((uint64_t*)&key) & m;
        break;
    }

    CARB_ASSERT(idx < entries.size());
    return idx;
}

template <typename T, SimpleMapIndexing I>
inline size_t SimpleMap<T, I>::slot(const Entry* ent) const
{
    CARB_ASSERT(ent);
    const Entry* p0 = entries.data();
    const Entry* p1 = p0 + entries.size();
    const bool belongs_to = (ent >= p0 && ent < p1);
    CARB_ASSERT(belongs_to);
    return belongs_to ? ent - p0 : 0;
}

template <typename T, SimpleMapIndexing I>
inline typename SimpleMap<T, I>::Entry* SimpleMap<T, I>::slot(size_t index) const
{
    CARB_ASSERT(index < entries.size());
    return entries.at(index);
}

template <typename T, SimpleMapIndexing I>
inline void SimpleMap<T, I>::clear()
{
    if (usedCnt > 0)
    {
        CARB_ASSERT(entries.empty() == false);
        const size_t occupancy_thr_hi = entries.size() * 10 / 100;
        const size_t occupancy_thr_lo = entries.size() * 5 / 100;

        if (usedCnt > occupancy_thr_hi)
        {
            std::memset(entries.data(), kReservedKey, entries.size() * sizeof(Entry));
        }
        else if (usedCnt > occupancy_thr_lo)
        {
            Entry* p = entries.data();
            const Entry* pend = p + entries.size();
            while (p < pend)
                p++->key = kReservedKey;
        }
        else
        {
            size_t n = usedCnt;
            Entry* p = entries.data();
            for (; n; p++)
            {
                if (p->key != kReservedKey)
                {
                    p->key = kReservedKey;
                    n--;
                }
            }
        }

        usedCnt = probedCnt = 0;
    }
}

template <typename T, SimpleMapIndexing I>
inline typename SimpleMap<T, I>::Entry* SimpleMap<T, I>::data() const
{
    return entries.data();
}

template <typename T, SimpleMapIndexing I>
inline void SimpleMap<T, I>::reserve(size_t n)
{
    CARB_ASSERT(n > 0);
    if (usedCnt == 0)
    {
        size_t c = 1;
        while (c < n)
            c <<= 1;
        ;
        m = c - 1;
        entries.reset(c);
        Entry* p = entries.data();
        const Entry* pe = p + c;
        while (p < pe)
            p++->key = kReservedKey;
        usedCnt = probedCnt = 0;
        grewCnt++;
    }
    else
    {
        SimpleMap<T, I> m;
        m.reserve(n);
        m.set(*this);
        const size_t gc = grewCnt;
        *this = std::move(m);
        grewCnt = gc + 1;
    }
}

template <typename T, SimpleMapIndexing I>
inline void SimpleMap<T, I>::reserveAtLeast(size_t n)
{
    CARB_ASSERT(n > 0);
    if (capacity() < n)
        reserve(n);
}

template <typename T, SimpleMapIndexing I>
inline size_t SimpleMap<T, I>::capacity() const
{
    return entries.size();
}

template <typename T, SimpleMapIndexing I>
inline size_t SimpleMap<T, I>::size() const
{
    return usedCnt;
}

template <typename T, SimpleMapIndexing I>
inline bool SimpleMap<T, I>::empty() const
{
    return usedCnt == 0;
}

template <typename T, SimpleMapIndexing I>
inline size_t SimpleMap<T, I>::growCounter() const
{
    return grewCnt;
}

template <typename T, SimpleMapIndexing I>
inline size_t SimpleMap<T, I>::probeCounter() const
{
    return probedCnt;
}

template <typename T, SimpleMapIndexing I>
inline float SimpleMap<T, I>::efficiency() const
{
    return double(probedCnt) / double(usedCnt);
}

template <typename T, SimpleMapIndexing I>
inline bool SimpleMap<T, I>::has(const T key) const
{
    const Entry* ent = find(key);
    return ent && ent->key == key;
}

template <typename T, SimpleMapIndexing I>
inline bool SimpleMap<T, I>::has(const T key, const T value) const
{
    const Entry* ent = find(key);
    return ent && ent->key == key && ent->value == value;
}

template <typename T, SimpleMapIndexing I>
inline const typename SimpleMap<T, I>::Entry* SimpleMap<T, I>::find(const T key) const
{
    if (usedCnt == 0)
        return nullptr;

    const Entry* e0 = entries.data();
    const size_t i0 = index(key);
    size_t i = i0;

loop:
    const Entry* e = e0 + i;
    if (e->key == kReservedKey)
        return nullptr;
    else if (e->key == key)
        return e;
    else if ((i = (i + 1) & m) != i0)
        goto loop;
    return nullptr;
}

template <typename T, SimpleMapIndexing I>
inline typename SimpleMap<T, I>::Entry* SimpleMap<T, I>::allocate(const T key, T*& pvalue)
{
    CARB_ASSERT(capacity() > 0);

    const size_t i0 = index(key);
    Entry* e0 = entries.data();
    size_t i = i0;
    size_t d = 1;

loop:
    Entry* e = e0 + i;
    if (e->key == kReservedKey)
        return e->key = key, pvalue = (T*)&e->value, probedCnt += d, usedCnt++, e;
    else if (e->key == key)
        return pvalue = (T*)&e->value, probedCnt += d, nullptr;
    else if (++d, (i = (i + 1) & m) != i0)
        goto loop;

    CARB_FATAL_UNLESS(false, "undersized map!");
    return nullptr;
}

template <typename T, SimpleMapIndexing I>
inline typename SimpleMap<T, I>::Entry* SimpleMap<T, I>::allocate_grow(const T key, T*& pvalue)
{
    const size_t sz = size();
    const size_t cp = capacity();
    if (cp < 256 || sz > cp / 2)
    {
        const size_t nsz = std::max(cp * 2ull, 4096ull);
        reserveAtLeast(nsz);
    }

    return allocate(key, pvalue);
}

template <typename T, SimpleMapIndexing I>
inline T SimpleMap<T, I>::store(const T key, const T value)
{
    T* pvalue = nullptr;
    if (allocate(key, pvalue))
        *pvalue = value;
    return *pvalue;
}

template <typename T, SimpleMapIndexing I>
inline void SimpleMap<T, I>::set(const T key, const T value)
{
    T* pvalue = nullptr;
    allocate(key, pvalue);
    *pvalue = value;
}

template <typename T, SimpleMapIndexing I>
inline void SimpleMap<T, I>::set(const SimpleMap& other)
{
    size_t n = other.usedCnt;
    const Entry* p = other.entries.data();
    for (; n; p++)
    {
        if (p->key != kReservedKey)
        {
            set(p->key, p->value);
            n--;
        }
    }
}

template <typename T, SimpleMapIndexing I>
inline void SimpleMap<T, I>::concurrent_set(const T key, const T value)
{
    const size_t i0 = index(key);
    Entry* e0 = entries.data();
    size_t i = i0;
    size_t d = 1;

loop:
    Entry* e = e0 + i;
    if (e->key == kReservedKey)
    {
        if (lock_xchg_kvp(&e->key, &e->value, kReservedKey, key, value) == kReservedKey)
        {
            lock_add(&probedCnt, d);
            lock_inc(&usedCnt);
            return;
        }
        else
        {
            goto loop;
        }
    }
    else if (e->key == key)
    {
        e->value = value;
        lock_add(&probedCnt, d);
        return;
    }
    else if (++d, (i = (i + 1) & m) != i0)
    {
        goto loop;
    }

    CARB_FATAL_UNLESS(false, "undersized map!");
}

template <typename T, SimpleMapIndexing I>
inline T SimpleMap<T, I>::concurrent_store(const T key, const T value)
{
    const size_t i0 = index(key);
    Entry* e0 = entries.data();
    size_t i = i0;
    size_t d = 1;

loop:
    Entry* e = e0 + i;
    if (e->key == kReservedKey)
    {
        if (lock_xchg_kvp(&e->key, &e->value, kReservedKey, key, value) == kReservedKey)
        {
            lock_add(&probedCnt, d);
            lock_inc(&usedCnt);
            return value;
        }
        else
        {
            goto loop;
        }
    }
    else if (e->key == key)
    {
        lock_add(&probedCnt, d);
        return e->value;
    }
    else if (++d, (i = (i + 1) & m) != i0)
    {
        goto loop;
    }

    CARB_FATAL_UNLESS(false, "undersized map!");
    return 0;
}

template <typename T, SimpleMapIndexing I>
inline T SimpleMap<T, I>::concurrent_store(const T key, value_generator_t gen, void* ud)
{
    const size_t i0 = index(key);
    Entry* e0 = entries.data();
    size_t i = i0;
    size_t d = 1;

loop:
    Entry* e = e0 + i;
    if (e->key == kReservedKey)
    {
        if (lock_xchg_kvp(&e->key, &e->value, kReservedKey, key, gen, ud) == kReservedKey)
        {
            lock_add(&probedCnt, d);
            lock_inc(&usedCnt);
            return e->value;
        }
        else
        {
            goto loop;
        }
    }
    else if (e->key == key)
    {
        lock_add(&probedCnt, d);
        return e->value;
    }
    else if (++d, (i = (i + 1) & m) != i0)
    {
        goto loop;
    }

    CARB_FATAL_UNLESS(false, "undersized map!");
    return 0;
}

template <typename T, SimpleMapIndexing I>
template <typename VisitorT>
void SimpleMap<T, I>::for_each(VisitorT visitor)
{
    const Entry* p = entries.data();
    size_t n = usedCnt;
    for (; n; p++)
    {
        if (p->key != kReservedKey)
        {
            visitor(*p);
            n--;
        }
    }
}

template <typename T, SimpleMapIndexing I>
template <typename VisitorT>
void SimpleMap<T, I>::for_each(VisitorT visitor) const
{
    const Entry* p = entries.data();
    size_t n = usedCnt;
    for (; n; p++)
    {
        if (p->key != kReservedKey)
        {
            visitor(*p);
            n--;
        }
    }
}

} // namespace fabric
} // namespace omni
