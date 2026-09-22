// SPDX-FileCopyrightText: Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include <carb/container/LocklessQueue.h>
#include <carb/container/LocklessStack.h>
#include <carb/cpp/Optional.h>

namespace omni::sensors::net::utils
{

/**
 * Non-intrusive lockless queue
 */
template <typename T>
class LocklessQueueNI
{
public:
    LocklessQueueNI() = default;

    ~LocklessQueueNI();

    CARB_PREVENT_COPY_AND_MOVE(LocklessQueueNI);

    /**
     * Emplace an element
     *
     * @param args arguments to be forwarded to the constructor of T
     *
     */
    template <typename... Args>
    void emplace(Args&&... args);

    /**
     * Try popping an element
     *
     * @param singleConsumer popping/consuming from 1 thread
     * @return optional with value if there is something to pop, and carb::cpp::nullopt otherwise
     *
     */
    carb::cpp::optional<T> tryPop(bool singleConsumer = true);

    /**
     * Try popping an element until a point in time
     *
     * @param timepoint time point to wait until
     * @param singleConsumer popping/consuming from 1 thread
     * @return optional with value if there is something to pop, and carb::cpp::nullopt otherwise
     *
     */
    template <typename Clock, typename Duration>
    carb::cpp::optional<T> tryPopUntil(const std::chrono::time_point<Clock, Duration>& timepoint,
                                       bool singleConsumer = true);

    /**
     * Try popping an element for a duration of time
     *
     * @param duration duration to wait for
     * @param singleConsumer popping/consuming from 1 thread
     * @return optional with value if there is something to pop, and carb::cpp::nullopt otherwise
     *
     */
    template <typename Rep, typename Period>
    carb::cpp::optional<T> tryPopFor(const std::chrono::duration<Rep, Period>& duration, bool singleConsumer = true);


    /**
     * Consume all elements in the queue, while applying function f to every element
     *
     * @param f function-like object to apply to every element before it's destroyed
     *
     * @note the following signatures are valid (replace T with the template argument):
     * 1. void(T)
     * 2. void(T&)
     * 3. void(const T&)
     *
     * example:
     * @code{.cpp}
     *
     * struct S;
     *
     * LocklessQueueNI<S> lq;
     *
     * lq.consume([](const S& s){ ... });
     *
     * @endcode
     */
    template <typename F>
    void consume(F&& f);


    /**
     * Get the underlying queue object for more advanced operations
     *
     * @return reference to carb::container::LocklessQueue
     */
    auto& getQueue()
    {
        return m_queue;
    }


private:
    struct Element
    {
        template <typename... Args>
        Element(Args&&... args);

        T value;

        union
        {
            carb::container::LocklessQueueLink<Element> queueLink;
            carb::container::LocklessStackLink<Element> stackLink;
        };
    };

    carb::container::LocklessQueue<Element, &Element::queueLink> m_queue;
    carb::container::LocklessStack<Element, &Element::stackLink> m_store;
};

} // namespace omni::sensors::net::utils

#include <omni/sensors/net/utils/LocklessQueueNIImpl.inl>
