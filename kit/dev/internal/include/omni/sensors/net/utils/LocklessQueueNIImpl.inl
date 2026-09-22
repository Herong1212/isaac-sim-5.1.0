// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#pragma once

#include <omni/sensors/net/utils/LocklessQueueNI.h>

#include <chrono>

namespace omni::sensors::net::utils
{

// LocklessQueueNI

template <typename T>
LocklessQueueNI<T>::~LocklessQueueNI()
{
    consume([](T&) {}); // destroy every element in the queue (i.e., queue is not empty)
    m_store.forEach([](Element* p) { ::operator delete(p); }); // free memory in store
}

template <typename T>
template <typename... Args>
void LocklessQueueNI<T>::emplace(Args&&... args)
{
    Element* p = m_store.pop();

    if (nullptr == p)
        p = new Element{ std::forward<Args>(args)... };
    else
        new (p) Element{ std::forward<Args>(args)... };

    m_queue.pushNotify(p);
}

template <typename T>
carb::cpp::optional<T> LocklessQueueNI<T>::tryPop(bool sc)
{
    carb::cpp::optional<T> ret;

    auto p = sc ? m_queue.popSC() : m_queue.popMC();

    if (nullptr != p)
    {
        ret = p->value;

        p->~Element();
        m_store.push(p);
    }

    return ret;
}

template <typename T>
template <typename Clock, typename Duration>
carb::cpp::optional<T> LocklessQueueNI<T>::tryPopUntil(const std::chrono::time_point<Clock, Duration>& timepoint, bool sc)
{
    carb::cpp::optional<T> ret;

    auto p = sc ? m_queue.popSCWaitUntil(timepoint) : m_queue.popMCWaitUntil(timepoint);

    if (nullptr != p)
    {
        ret = p->value;

        p->~Element();
        m_store.push(p);
    }

    return ret;
}

template <typename T>
template <typename Rep, typename Period>
carb::cpp::optional<T> LocklessQueueNI<T>::tryPopFor(const std::chrono::duration<Rep, Period>& duration, bool sc)
{
    return tryPopUntil(std::chrono::steady_clock::now() + duration, sc);
}

template <typename T>
template <typename F>
void LocklessQueueNI<T>::consume(F&& f)
{
    m_queue.forEach(
        [&](Element* p)
        {
            f(p->value);

            p->~Element();
            m_store.push(p);
        });
}

// LocklessQueueNI::Element

template <typename T>
template <typename... Args>
LocklessQueueNI<T>::Element::Element(Args&&... args) : value{ std::forward<Args>(args)... }
{
}

} // namespace omni::sensors::net::utils
