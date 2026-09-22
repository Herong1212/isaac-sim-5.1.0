// Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include "Defines.h"

namespace omni
{
    template<typename T>
    struct CachedIPtr
    {
        CachedIPtr()
        {
            m_ptr = carb::getCachedInterface<T>();
            CARB_FAIL_UNLESS(m_ptr, "Interface not cached");
        }

        T* operator->() const
        {
            return m_ptr;
        }

        operator bool() const
        {
            return m_ptr != nullptr;
        }

        T* get()
        {
            return m_ptr;
        }

        T* m_ptr;
    };

    template<typename T>
    struct AcquiredIPtr
    {
        AcquiredIPtr()
        {
            m_ptr = carb::getFramework()->acquireInterface<T>();
            CARB_FAIL_UNLESS(m_ptr, "Interface not acquired");
        }

        T* operator->() const
        {
            return m_ptr;
        }

        operator bool() const
        {
            return m_ptr != nullptr;
        }

        T* get()
        {
            return m_ptr;
        }

        T* m_ptr;
    };

    template <typename T>
    struct TryAcquiredIPtr
    {
        TryAcquiredIPtr()
        {
            m_ptr = carb::getFramework()->tryAcquireInterface<T>();
        }

        T* operator->() const
        {
            return m_ptr;
        }

        operator bool() const
        {
            return m_ptr != nullptr;
        }

        T* get()
        {
            return m_ptr;
        }

        T* m_ptr;
    };
 }
