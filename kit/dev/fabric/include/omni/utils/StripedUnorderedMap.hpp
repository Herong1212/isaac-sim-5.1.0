// Copyright (c) 2020-2023, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
//! @file
//!
//! @brief A Concurrent Unordered Map using a Stripe of Unordered Maps.
#pragma once

#include <carb/thread/Mutex.h>

#include <unordered_map>

/**
 * A stripe of unordered maps.
 *
 * This concept of the striped unordered map can be found in The Art of
 * Multiprocessor programming. We adjust it a bit for simplicity, notably we use
 * a fixed number of locks rather than a ratio of locks. Notably if we were to
 * take the route outlined in TAOMP, we would have to replace the
 * std::unordered_map, which is a much more complicated task. By used a fixed N,
 * we can simply choose a N that is likely to avoid contention.
 *
 * In the long run the TAOMP also shows a fully lockless solution, however again
 * this an even more difficult implemenation.
 *
 * TODO: This class should support both acquireAccess for read/write operations and
 * acquireSharedAccess for read only operations. If read only operations are
 * needed acquireSharedAccess is prefered because it will allow many threads to
 * access the same stripe at the same time for read.
 *
 * @note In general pick a stripe count that is a prime number. See Algorithms
 * Forth Edition by Sedgewick et all for more information.
 */
template <typename Key,
          typename Value,
          size_t StripeCount,
          typename Device = carb::thread::mutex,
          typename Hasher = std::hash<Key>,
          typename EqualTo = std::equal_to<Key>,
          typename Allocator = std::allocator<std::pair<const Key, Value>>>
class StripedUnorderedMap
{
    CARB_PREVENT_COPY_AND_MOVE(StripedUnorderedMap);

public:
    //! Default constructor.
    StripedUnorderedMap() = default;

    //! The underling unordered_map each stripe own.
    using map_type = std::unordered_map<Key, Value, Hasher, EqualTo, Allocator>;

    /**
     * @brief Clears all entries in the Map.
     *
     * WARNING: This function is not thread safe.
     */
    void clearUnsafe()
    {
        for (auto& stripe : m_stripes)
        {
            stripe.map.clear();
        }
    }

    /**
     * A RAII class providing exclusive access to the unordered map.
     */
    struct ScopedAccess
    {
        CARB_PREVENT_COPY(ScopedAccess);
        friend class StripedUnorderedMap;

    public:
        /** Default constructor. */
        ScopedAccess() = default;

        /** Destructor releases the lock. */
        ~ScopedAccess()
        {
            if (m_parent)
            {
                m_parent->unlockStripe(m_stripe);
            }
        }
        /** Move constructor */
        ScopedAccess(ScopedAccess&& other)
        {
            m_parent = other.m_parent;
            m_stripe = other.m_stripe;
            other.m_parent = nullptr;
            other.m_stripe = 0;
        }
        /** Move assignment */
        ScopedAccess& operator=(ScopedAccess&& other)
        {
            m_parent = other.m_parent;
            m_stripe = other.m_stripe;
            other.m_parent = nullptr;
            other.m_stripe = 0;
            return *this;
        }

        /**
         * Access the unordered map on this stripe via dereference.
         */
        map_type& operator*()
        {
            return *m_parent->getMap(m_stripe);
        }

        /**
         * Access the unordered map on this stripe via pointer.
         */
        map_type* operator->()
        {
            return m_parent->getMap(m_stripe);
        }

    private:
        ScopedAccess(StripedUnorderedMap& parent, size_t stripe) : m_parent(&parent), m_stripe(stripe)
        {
            m_parent->lockStripe(m_stripe);
        }

        StripedUnorderedMap* m_parent = nullptr;
        size_t m_stripe = 0;
    };

    /**
     * Acquires exclusive access.
     *
     * @note Only one thread can have exclusive access at a time.
     *
     * @param key The key to access.
     * @returns a RAII object that holds the exclusive access to the unordered
     * map.
     */
    ScopedAccess acquireAccess(const Key& key)
    {
        return ScopedAccess(*this, keyToStripe(key));
    }

    template <class Fn>
    void forEach(Fn&& fn)
    {
        for (size_t i = 0; i < StripeCount; i++)
        {
            auto& stripe = m_stripes[i];
            stripe.lock();
            for (auto& item : stripe.map)
            {
                fn(item);
            }
            stripe.unlock();
        }
    }

private:
    void lockStripe(size_t stripe)
    {
        m_stripes[stripe].mutex.lock();
    }
    void unlockStripe(size_t stripe)
    {
        m_stripes[stripe].mutex.unlock();
    }
    map_type* getMap(size_t stripe)
    {
        return &m_stripes[stripe].map;
    }
    const map_type* getMap(size_t stripe) const
    {
        return &m_stripes[stripe].map;
    }

    size_t keyToStripe(const Key& key)
    {
        // We need to rehash the hash, as there is a possibility of our hash falling
        // into the same buckets as the primary hash used by std::unordered_map.

        // https://en.wikipedia.org/wiki/Hash_function#Fibonacci_hashing
        // See also: The Art of Computer Programming by Knuth
        // Using Pari/GP
        // ? 2^64/((1 + sqrt(5)) / 2)
        // %1 = 11400714819323198485.951610587621806950
        return ((m_hasher(key) * 11400714819323198485ULL) >> 48) % StripeCount;
    }

    struct Stripe
    {
        map_type map;
        mutable Device mutex;
    };

    Stripe m_stripes[StripeCount];
    Hasher m_hasher;
};
