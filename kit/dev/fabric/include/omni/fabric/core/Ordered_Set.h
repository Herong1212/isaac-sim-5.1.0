// Copyright (c) 2019-2020, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once
#include <algorithm>
#include <functional>
#include <initializer_list>
#include <vector>

namespace omni
{
namespace fabric
{
template <class T, class Compare = std::less<T>>
struct set
{
    using value_type = T;

    std::vector<T> v;
    Compare cmp;
    using iterator = typename std::vector<T>::iterator;
    using const_iterator = typename std::vector<T>::const_iterator;
    iterator begin()
    {
        return v.begin();
    }
    iterator end()
    {
        return v.end();
    }
    const_iterator begin() const
    {
        return v.begin();
    }
    const_iterator end() const
    {
        return v.end();
    }
    set(const Compare& c = Compare()) : v(), cmp(c)
    {
    }
    template <class InputIterator>
    set(InputIterator first, InputIterator last, const Compare& c = Compare()) : v(), cmp(c)
    {
        insert(first, last);
    }

    set(std::initializer_list<T> _Ilist) : set(_Ilist.begin(), _Ilist.end())
    {
    }

    set(const size_t size, const Compare& c = Compare()) : v(size), cmp(c)
    {
    }

    void resize(size_t newSize)
    {
        v.resize(newSize);
    }
    void reserve(size_t newCapacity)
    {
        v.reserve(newCapacity);
    }

    void clear()
    {
        v.clear();
    }

    iterator insert(const T& t)
    {
        iterator i = std::lower_bound(begin(), end(), t, cmp);
        if (i == end() || cmp(t, *i))
            i = v.insert(i, t);
        return i;
    }

    iterator insert(T&& t)
    {
        iterator i = std::lower_bound(begin(), end(), t, cmp);
        if (i == end() || cmp(t, *i))
            i = v.insert(i, std::move(t));
        return i;
    }

    template <class _Iter>
    void insert(_Iter _First, _Iter _Last)
    { // insert [_First, _Last) one at a time
        for (; _First != _Last; ++_First)
        {
            insert(*_First);
        }
    }

    iterator insert(const_iterator hint, const value_type& value)
    {
        // Measurements show it is faster to ignore hint in this application
        return insert(value);
    }

    void insert(std::initializer_list<T> _Ilist)
    {
        insert(_Ilist.begin(), _Ilist.end());
    }

    size_t erase(const T& key)
    {
        iterator removeElement = find(key);
        if (removeElement != v.end())
        {
            v.erase(removeElement);
            return 1;
        }
        else
        {
            return 0;
        }
    }

    iterator erase(iterator iter)
    {
        return v.erase(iter);
    }

    iterator erase(iterator first, iterator last)
    {
        return v.erase(first, last);
    }

    const_iterator find(const T& t) const
    {
        const_iterator i = std::lower_bound(begin(), end(), t, cmp);
        return i == end() || cmp(t, *i) ? end() : i;
    }

    iterator find(const T& t)
    {
        iterator i = std::lower_bound(begin(), end(), t, cmp);
        return i == end() || cmp(t, *i) ? end() : i;
    }

    bool contains(const T& t) const
    {
        const_iterator i = std::lower_bound(begin(), end(), t, cmp);
        return i != end() && !cmp(t, *i);
    }

    bool operator==(const set<T>& other) const
    {
        return v == other.v;
    }

    bool operator!=(const set<T>& other) const
    {
        return v != other.v;
    }

    size_t size() const
    {
        return v.size();
    }

    bool empty() const
    {
        return v.empty();
    }

    T* data()
    {
        return v.data();
    }

    const T* data() const
    {
        return v.data();
    }
};

template <class T, class Compare = std::less<T>>
bool operator<(const set<T, Compare>& left, const set<T, Compare>& right)
{
    return left.v < right.v;
}

template <typename T>
fabric::set<T> nWayUnion(std::vector<omni::fabric::set<T>>& srcBuckets)
{
    omni::fabric::set<T> retval;

    // Calculate the maximum number of destination attributes
    // We could instead calculate it exactly by finding union of attribute names
    size_t maxDestAttrCount = 0;
    for (fabric::set<T>& srcBucket : srcBuckets)
    {
        maxDestAttrCount += srcBucket.size();
    }
    retval.reserve(maxDestAttrCount);

    auto currentDest = std::back_inserter(retval.v);

    size_t bucketCount = srcBuckets.size();

    // Initialize invariant that nonEmpty is the vector of buckets that have
    // non-zero attribute counts
    struct NonEmptySegment
    {
        // Invariant is current!=end
        typename std::vector<T>::iterator current;
        typename std::vector<T>::iterator end;
    };
    std::vector<NonEmptySegment> nonEmpty;
    nonEmpty.reserve(bucketCount);
    for (omni::fabric::set<T>& srcBucket : srcBuckets)
    {
        if (srcBucket.begin() != srcBucket.end())
        {
            nonEmpty.push_back({ srcBucket.begin(), srcBucket.end() });
        }
    }

    // Keep going until there's only 1 non-empty bucket
    // At that point we can just copy its attributes to the output
    while (1 < nonEmpty.size())
    {
        // Find all the buckets that have the minimum element
        // These are the ones whose iterators will get advanced

        // By the loop guard and the invariant, we know that nonEmpty[0] exists
        // and that nonEmpty[0].current!=nonEmpty[0].end.
        // So *nonEmpty[0].current is a safe dereference
        T minSoFar = *nonEmpty[0].current;
        for (size_t i = 1; i < nonEmpty.size(); i++)
        {
            minSoFar = std::min(*nonEmpty[i].current, minSoFar);
        }

        // Copy minimum element to the output
        *currentDest = minSoFar;
        ++(*currentDest);

        // Advance the iterators that pointed to the min
        for (size_t i = 0; i < nonEmpty.size(); i++)
        {
            if (*nonEmpty[i].current == minSoFar)
            {
                nonEmpty[i].current++;
                if (nonEmpty[i].current == nonEmpty[i].end)
                {
                    // this set is empty, remove it by overwriting with the last
                    nonEmpty[i] = nonEmpty[nonEmpty.size() - 1];
                    nonEmpty.pop_back();
                    i--; // make sure we still process the now overwritten one again
                }
            }
        }
    }

    // By the negation of the guard we know that nonEmpty has zero or one elements
    if (nonEmpty.size() == 1)
    {
        // If one bucket is left, copy its elements to the output
        std::copy(nonEmpty[0].current, nonEmpty[0].end, currentDest);
    }

    return retval;
}

} // namespace fabric
} // namespace omni
