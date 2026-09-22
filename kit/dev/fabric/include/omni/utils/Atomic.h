// Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <atomic>
#include <carb/cpp/Atomic.h>

namespace omni
{

// helper for atomic max
template <typename T>
inline T fetch_max(std::atomic<T>& value, T newValue)
{
    T previousValue = value.load();
    while (previousValue < newValue)
        if (value.compare_exchange_strong(previousValue, newValue))
            break;
    return previousValue;
}

template <typename T>
inline T fetch_min(std::atomic<T>& value, T newValue)
{
    T previousValue = value.load();
    while (previousValue > newValue)
        if (value.compare_exchange_strong(previousValue, newValue))
            break;
    return previousValue;
}

template <typename T>
inline T fetch_max(carb::cpp::atomic_ref<T> value, T newValue)
{
    T previousValue = value.load();
    while (previousValue < newValue)
        if (value.compare_exchange_strong(previousValue, newValue))
            break;
    return previousValue;
}

template <typename T>
inline T fetch_min(carb::cpp::atomic_ref<T> value, T newValue)
{
    T previousValue = value.load();
    while (previousValue > newValue)
        if (value.compare_exchange_strong(previousValue, newValue))
            break;
    return previousValue;
}


template<typename T>
carb::cpp::atomic_ref<std::remove_volatile_t<T>> makeAtomic(T& value)
{
    return carb::cpp::atomic_ref<std::remove_volatile_t<T>>((std::remove_volatile_t<T>&)value);
}

template<bool useAtomicAccess, typename CallbackT>
void modifyAtomicValue(uint64_t& val, CallbackT cb)
{
    if (useAtomicAccess)
    {
        uint64_t oldVal = val;
        uint64_t newData;
        do
        {
            newData = cb(oldVal);
        } while (!makeAtomic(val).compare_exchange_strong(oldVal, newData));
    }
    else
    {
        val = cb(val);
    }
}

} // namespace omni
