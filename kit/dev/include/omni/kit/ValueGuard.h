// Copyright (c) 2018-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#pragma once

#include <carb/Defines.h>

namespace omni
{
namespace kit
{

template <typename T, T inVal, T outVal>
class ValueGuard
{
public:
    explicit ValueGuard(T& val) : m_val(val)
    {
        CARB_ASSERT(m_val == outVal);
        m_val = inVal;
    }

    ~ValueGuard()
    {
        m_val = outVal;
    }

private:
    T& m_val;
};

using BoolGuard = ValueGuard<bool, true, false>;

}
}
