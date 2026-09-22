// SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

//! \file
//! \brief carb.tasking Parallel Sort algorithm
#pragma once
#include "TaskingUtils.h"
#include "ITasking.h"
#include "TaskingTypes.h"
#include "../cpp/Bit.h"
#include <algorithm>
#include <iterator>

namespace carb
{
namespace tasking
{

#pragma push_macro("min")
#undef min

//! \cond DEV
namespace detail
{

template <class T>
using IsRandomAccess =
    ::std::is_convertible<typename ::std::iterator_traits<T>::iterator_category, ::std::random_access_iterator_tag>;

template <class T>
constexpr bool IsRandomAccess_v = IsRandomAccess<T>::value;

template <typename RandomAccessIterator, typename Compare>
struct Sorter
{
    Sorter(carb::tasking::ITasking& tasking,
           RandomAccessIterator first,
           RandomAccessIterator last,
           const Compare& compare,
           size_t spawnThreshold = 512)
        : tasking(tasking), base(first), len(last - first), compare(compare), spawnThreshold(spawnThreshold)
    {
    }
    ~Sorter()
    {
        taskGroup.wait();
    }

    void operator()()
    {
        sort(0, len, getRecursiveDepth(len));
    }

private:
    // Unless you pick the perfect median, it is always possible to pick a poor median, to prevent O(n^2) behavior
    // in this case we terminate our system if it is worse than 2 times log n depth.
    size_t getRecursiveDepth(size_t n)
    {
        // This is ~log_2(n) * 2.
        return static_cast<size_t>(carb::cpp::bit_width(n) * 2);
    }

    // Finds the median of 3 values.
    inline size_t median3(size_t a, size_t b, size_t c) const
    {
        bool comp_b_a = compare(base[b], base[a]);
        return (comp_b_a != compare(base[c], base[a])) ? a : (comp_b_a != compare(base[b], base[c])) ? b : c;
    }

    // https://people.seas.harvard.edu/~cs125/fall16/lec4.pdf
    // For a justification why doing a small set of medians and then a larger one gives a good pseudo median value.
    // This is also known as Tukey's Ninther in the literature.
    inline size_t pseudoMedian9(size_t start, size_t n) const
    {
        size_t stepSize = n / 8;
        return median3(median3(start + 0, start + stepSize, start + 2 * stepSize),
                       median3(start + 3 * stepSize, start + 4 * stepSize, start + 5 * stepSize),
                       median3(start + 6 * stepSize, start + 7 * stepSize, start + n - 1));
    }

    inline void swapAt(size_t a, size_t b)
    {
        using ::std::swap;
        swap(base[a], base[b]);
    }

    // This is simpler and faster than std::rotate, as we don't care about order preservation.
    inline void rotate(size_t l, size_t h, size_t rotateLen)
    {
        for (; rotateLen; rotateLen--)
            swapAt(l++, h++);
    }

    struct SubSort
    {
        SubSort(Sorter* sorter, size_t l, size_t h, size_t rotateLen, size_t start, size_t n, size_t depthRemaining)
            : sorter(sorter), l(l), h(h), rotateLen(rotateLen), start(start), n(n), depthRemaining(depthRemaining)
        {
        }

        void operator()() const
        {
            sorter->rotate(l, h, rotateLen);
            if (n > 0)
                sorter->sort(start, n, depthRemaining);
        }

        Sorter* sorter;
        size_t l;
        size_t h;
        size_t rotateLen;
        size_t start;
        size_t n;
        size_t depthRemaining;
    };
    template <typename Fn>
    void addTask(Fn&& fn)
    {
        tasking.addTask(Priority::eDefault, { taskGroup }, ::std::forward<Fn>(fn));
    }

    inline void sort(size_t start, size_t n, size_t depthRemaining)
    {
        // If there is a small amount of data, use the std algorithm which is likely highly tuned for the serial case.
        if (depthRemaining == 0 || n < spawnThreshold)
        {
            ::std::sort(base + start, base + start + n, compare);
            return;
        }
        size_t pivot = pseudoMedian9(start, n);
        // Place the pivot on the left, so we do not have to move it again.
        swapAt(pivot, start);

        size_t a = start + 1, b = start + 1;
        size_t c = start + n - 1, d = start + n - 1;

        // Three way partition.
        // See: Engineering a Sort Function by Bentley et all.
        const auto& v = base[start];
        for (;;)
        {
            while (b <= c && !compare(v, base[b]))
            {
                if (!compare(base[b], v))
                    swapAt(a++, b);
                b++;
            }
            while (b <= c && !compare(base[c], v))
            {
                if (!compare(v, base[c]))
                    swapAt(d--, c);
                c--;
            }
            if (b > c)
                break;
            swapAt(b++, c--);
        }

        // At this point:
        //   base[start...a] == V
        //   base[a..b] < V
        //   base[c..d] > V
        //   base[d..start+n] == V
        //
        // The rotation step will convert this so the == are in the middle of the array.
        //
        // Since the rotation step is independent it can be ran on the other thread, but it must be ran before the rest
        // of the sorting can occur. A full std::rotate could be ran after, but it is slower.

        size_t rotateLeftCount = ::std::min(a - start, b - a);
        size_t rotateRightCount = ::std::min(d - c, start + n - 1 - d);

        size_t lenLeft = b - a;
        size_t lenRight = d - c;

        auto doLeft = SubSort(this, start, b - rotateLeftCount, rotateLeftCount, start, lenLeft, depthRemaining - 1);
        auto doRight = SubSort(this, b, start + n - rotateRightCount, rotateRightCount, start + n - lenRight, lenRight,
                               depthRemaining - 1);

        // We judge just rotating things to be half the cost.
        size_t costLeft = rotateLeftCount / 2 + lenLeft;
        size_t costRight = rotateRightCount / 2 + lenRight;
        if (costLeft > spawnThreshold && costRight > spawnThreshold)
        {
            // Only spawn, if both are larger than the threshold, the idea is if one partition is small, just do it.
            // Spawn the smaller partition, the idea is the overhead of the spawning is ideally absorbed by that.
            if (costLeft < costRight)
            {
                addTask(doLeft);
                doRight();
            }
            else
            {
                addTask(doRight);
                doLeft();
            }
        }
        else
        {
            doLeft();
            doRight();
        }
    }

    carb::tasking::ITasking& tasking;
    carb::tasking::TaskGroup taskGroup;

    RandomAccessIterator base;
    size_t len;
    const Compare& compare;
    size_t spawnThreshold;
};

} // namespace detail
  //! \endcond

/**
 * Performs a parallel sort on the given data.
 *
 * @warning This sorting algorithm is not stable.
 *
 * @param tasking the ITasking interface to use.
 * @param first an iterator to the first element to sort.
 * @param last an iterator to the last element to sort.
 * @param comp the Functor to use to compare two elements.
 */
template <typename RandomAccessIterator, typename Compare>
inline ::std::enable_if_t<detail::IsRandomAccess_v<RandomAccessIterator>> parallelSort(ITasking* tasking,
                                                                                       RandomAccessIterator first,
                                                                                       RandomAccessIterator last,
                                                                                       const Compare& comp)
{
    detail::Sorter<RandomAccessIterator, Compare>(*tasking, first, last, comp)();
}

/**
 * Performs a parallel sort on the given data.
 *
 * @warning This sorting algorithm is not stable.
 *
 * @param tasking the ITasking interface to use.
 * @param first an iterator to the first element to sort.
 * @param last an iterator to the last element to sort.
 */
template <typename RandomAccessIterator>
inline ::std::enable_if_t<detail::IsRandomAccess_v<RandomAccessIterator>> parallelSort(ITasking* tasking,
                                                                                       RandomAccessIterator first,
                                                                                       RandomAccessIterator last)
{
    parallelSort(tasking, first, last, ::std::less<typename std::iterator_traits<RandomAccessIterator>::value_type>());
}

#pragma pop_macro("min")

} // namespace tasking
} // namespace carb
