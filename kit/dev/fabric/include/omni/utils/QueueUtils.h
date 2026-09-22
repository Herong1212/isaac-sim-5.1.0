// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable : 4703)
#endif

#include <concurrentqueue/include_concurrentqueue.h>

#ifdef _MSC_VER
#pragma warning(pop)
#endif

#include <vector>
#include "SmallVector.h"

namespace omni
{

    template <typename T>
    static void dequeueElements(moodycamel::ConcurrentQueue<T>& queue, std::vector<T>& target, size_t maxElements = 0xffffffffffffffff, size_t startElement = 0)
    {
        const size_t sizeApprox = std::min(maxElements, queue.size_approx());
        target.resize(sizeApprox + startElement);

        auto it = target.begin() + startElement;
        size_t countInstances = sizeApprox;
        while (countInstances)
        {
            const size_t countDequeued = queue.try_dequeue_bulk(it, countInstances);
            countInstances -= countDequeued;
            it += countDequeued;
        }
    }

    template <typename T, std::size_t N>
    static void dequeueElements(moodycamel::ConcurrentQueue<T>& queue, SmallVector<T, N>& target, omni::SmallVectorBase::size_type maxElements = 0xffffffff, omni::SmallVectorBase::size_type startElement = 0)
    {
        using VectorSizeType = omni::SmallVectorBase::size_type;
        const VectorSizeType sizeApprox = VectorSizeType(std::min(size_t(maxElements), queue.size_approx()));
        target.resize(VectorSizeType(sizeApprox) + startElement);

        auto it = target.begin() + startElement;
        size_t countInstances = sizeApprox;
        while (countInstances)
        {
            const size_t countDequeued = queue.try_dequeue_bulk(it, countInstances);
            countInstances -= countDequeued;
            it += countDequeued;
        }
    }

} // namespace omni
